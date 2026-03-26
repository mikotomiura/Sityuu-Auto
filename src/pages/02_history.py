"""鑑定履歴ページ — 過去の鑑定セッションの一覧・詳細閲覧。

Note:
    本ページは app.py 経由でのみアクセスされる前提。
    認証は app.py の require_login() で実施済み。
"""

import json
import logging
from datetime import datetime

import streamlit as st
from pydantic import ValidationError

from components.history_table import render_history_table
from components.pdf_export import build_fallback_pdf
from components.reading_result import render_reading_result
from config import (
    SESSION_KEY_HISTORY_SEARCH_QUERY,
    SESSION_KEY_HISTORY_SELECTED_SESSION,
)
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository
from fortune_engine.models import FortuneResult, NatalChart, SanmeiData
from utils.exceptions import DatabaseError, PDFExportError
from utils.privacy import inject_autocomplete_off

logger = logging.getLogger(__name__)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_HISTORY_SELECTED_SESSION not in st.session_state:
        st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION] = None
    if SESSION_KEY_HISTORY_SEARCH_QUERY not in st.session_state:
        st.session_state[SESSION_KEY_HISTORY_SEARCH_QUERY] = ""


def _render_list_view(session_repo: SessionRepository) -> None:
    """一覧ビューを表示する。

    検索フィルタと鑑定履歴一覧テーブルを表示し、
    セッションが選択されたら詳細ビューに切り替える。

    Args:
        session_repo: セッションリポジトリ。
    """
    # --- 検索フィルタ ---
    search_query = st.text_input(
        "相談者名で検索",
        value=st.session_state[SESSION_KEY_HISTORY_SEARCH_QUERY],
        placeholder="名前を入力...",
        key="history_search_input",
        autocomplete="off",
    )
    st.session_state[SESSION_KEY_HISTORY_SEARCH_QUERY] = search_query

    # --- データ取得（ページネーション付き） ---
    try:
        if search_query.strip():
            sessions = session_repo.search_by_client_name(search_query.strip(), limit=50)
        else:
            sessions = session_repo.find_all_with_client_name(limit=50)
    except DatabaseError as e:
        logger.error("履歴の取得に失敗: %s", e)
        st.error("履歴の取得に失敗しました。")
        return

    # --- 件数表示 ---
    st.caption(f"{len(sessions)} 件の鑑定履歴")

    # --- 一覧テーブル ---
    selected_id = render_history_table(sessions)

    if selected_id:
        st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION] = selected_id
        st.rerun()


def _render_detail_view(session_repo: SessionRepository) -> None:
    """詳細ビューを表示する。

    選択されたセッションの鑑定結果（命式・AIレポート・傾聴ヒント）を
    表示し、MDエクスポートを提供する。

    Args:
        session_repo: セッションリポジトリ。
    """
    session_id: str = st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION]

    # --- 戻るボタン ---
    if st.button("< 一覧に戻る"):
        st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION] = None
        st.rerun()

    # --- セッションデータ取得 ---
    try:
        session = session_repo.find_by_id(session_id)
    except DatabaseError as e:
        logger.error("セッション詳細の取得に失敗: %s", e)
        st.error("セッション詳細の取得に失敗しました。")
        return

    if session is None:
        st.error("指定された鑑定セッションが見つかりません。")
        st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION] = None
        return

    # --- 相談者名の取得 ---
    try:
        conn = get_db_connection()
        client_repo = ClientRepository(conn)
        client = client_repo.find_by_id(session.client_id)
        client_name = client.name if client else "不明"
    except DatabaseError:
        client_name = "不明"

    # --- ヘッダー情報 ---
    created_date = session.created_at[:10] if session.created_at else "不明"
    st.subheader(f"{client_name} の鑑定 — {created_date}")

    with st.expander("相談内容", expanded=False):
        st.text(session.concern)

    if session.api_provider:
        st.caption(f"使用モデル: {session.api_provider} / {session.api_model or '不明'}")

    # --- 命式データの復元と表示 ---
    try:
        natal_chart = NatalChart.model_validate_json(session.natal_chart_json)
        sanmei_data = (
            SanmeiData.model_validate_json(session.sanmei_data_json)
            if session.sanmei_data_json
            else None
        )
    except (ValidationError, json.JSONDecodeError):
        logger.warning("命式データの復元に失敗: session_id=%s", session_id)
        st.warning("命式データの復元に失敗しました。AI鑑定テキストのみ表示します。")
        natal_chart = None
        sanmei_data = None

    if natal_chart and sanmei_data:
        fortune_result = FortuneResult(
            natal_chart=natal_chart,
            sanmei_data=sanmei_data,
        )
        st.markdown("---")
        render_reading_result(
            result=fortune_result,
            ai_text=session.ai_reading_text,
            listening_hints=session.ai_listening_hints,
            client_name=client_name,
        )
    else:
        # 命式復元に失敗した場合でもAIテキストは表示する
        if session.ai_reading_text:
            st.markdown("---")
            st.markdown("### AI鑑定レポート")
            st.markdown(session.ai_reading_text)
        if session.ai_listening_hints:
            st.markdown("---")
            st.markdown("### 傾聴のヒント")
            st.markdown(session.ai_listening_hints)

        # 命式なしでもエクスポートを提供
        if session.ai_reading_text:
            md_content = _build_fallback_markdown(
                client_name=client_name,
                ai_text=session.ai_reading_text,
                listening_hints=session.ai_listening_hints,
            )
            col_md, col_pdf = st.columns(2)
            with col_md:
                st.download_button(
                    label="Markdownで保存",
                    data=md_content,
                    file_name=f"鑑定レポート_{client_name}_{created_date}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            with col_pdf:
                try:
                    pdf_data = build_fallback_pdf(
                        client_name=client_name,
                        ai_text=session.ai_reading_text,
                        listening_hints=session.ai_listening_hints,
                    )
                    st.download_button(
                        label="PDFで保存",
                        data=pdf_data,
                        file_name=f"鑑定レポート_{client_name}_{created_date}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except PDFExportError:
                    logger.exception("PDF生成に失敗しました")
                    st.error("PDF生成に失敗しました。")


def _build_fallback_markdown(
    client_name: str,
    ai_text: str,
    listening_hints: str | None = None,
) -> str:
    """命式データなしの簡易Markdownレポートを生成する。

    Args:
        client_name: 相談者名。
        ai_text: AI鑑定テキスト。
        listening_hints: 傾聴ヒントテキスト。

    Returns:
        Markdown形式のレポート文字列。
    """
    today = datetime.now().strftime("%Y-%m-%d")
    sections = [
        f"# 鑑定レポート: {client_name}",
        f"- 鑑定日: {today}",
        "",
        "---",
        "",
        "## AI鑑定レポート",
        "",
        ai_text,
    ]

    if listening_hints:
        sections.extend(
            [
                "",
                "---",
                "",
                "## 傾聴のヒント（メンター向け）",
                "",
                listening_hints,
            ]
        )

    sections.extend(["", "---", f"*Generated by Sityuu-Auto on {today}*", ""])
    return "\n".join(sections)


def main() -> None:
    """鑑定履歴ページのメイン処理。"""
    _initialize_state()
    inject_autocomplete_off()

    st.title("鑑定履歴")
    st.markdown(
        '<p class="page-description">'
        "過去の鑑定セッションを検索・閲覧し、レポートをエクスポートできます"
        "</p>",
        unsafe_allow_html=True,
    )

    conn = get_db_connection()
    session_repo = SessionRepository(conn)

    # --- ビュー切り替え ---
    if st.session_state[SESSION_KEY_HISTORY_SELECTED_SESSION] is not None:
        _render_detail_view(session_repo)
    else:
        _render_list_view(session_repo)


main()
