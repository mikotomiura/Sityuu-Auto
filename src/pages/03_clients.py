"""相談者管理ページ — 相談者の一覧表示・検索・詳細閲覧・メモ編集。"""

import logging

import streamlit as st

from config import (
    CONCERN_PREVIEW_LENGTH,
    SESSION_KEY_CLIENTS_SEARCH_QUERY,
    SESSION_KEY_CLIENTS_SELECTED,
)
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_CLIENTS_SELECTED not in st.session_state:
        st.session_state[SESSION_KEY_CLIENTS_SELECTED] = None
    if SESSION_KEY_CLIENTS_SEARCH_QUERY not in st.session_state:
        st.session_state[SESSION_KEY_CLIENTS_SEARCH_QUERY] = ""


def _render_list_view(
    client_repo: ClientRepository,
    session_repo: SessionRepository,
) -> None:
    """一覧ビューを表示する。

    相談者の検索フィルタと一覧カードを表示し、
    選択された相談者の詳細ビューに遷移する。

    Args:
        client_repo: 相談者リポジトリ。
        session_repo: セッションリポジトリ。
    """
    # --- 検索フィルタ ---
    search_query = st.text_input(
        "相談者名で検索",
        value=st.session_state[SESSION_KEY_CLIENTS_SEARCH_QUERY],
        placeholder="名前を入力...",
        key="clients_search_input",
    )
    st.session_state[SESSION_KEY_CLIENTS_SEARCH_QUERY] = search_query

    # --- データ取得 ---
    try:
        if search_query.strip():
            clients = client_repo.search_by_name(search_query.strip())
        else:
            clients = client_repo.find_all()
    except DatabaseError as e:
        logger.error("相談者一覧の取得に失敗: %s", e)
        st.error("相談者情報の取得に失敗しました。")
        return

    st.caption(f"{len(clients)} 名の相談者")

    if not clients:
        st.info("相談者がまだ登録されていません。鑑定ページから鑑定を行うと自動登録されます。")
        return

    # セッション数を一括取得（N+1問題の回避）
    try:
        session_counts = client_repo.count_sessions_by_client()
    except DatabaseError:
        session_counts = {}

    # --- 相談者カード ---
    for client in clients:
        session_count = session_counts.get(client.id, 0)

        with st.container(border=True):
            col_info, col_action = st.columns([4, 1])

            with col_info:
                st.write(f"**{client.name}**")
                st.caption(
                    f"生年月日: {client.birth_date}"
                    f" | 鑑定回数: {session_count}回"
                    f" | 登録日: {client.created_at[:10]}"
                )

            with col_action:
                if st.button("詳細", key=f"client_{client.id}", use_container_width=True):
                    st.session_state[SESSION_KEY_CLIENTS_SELECTED] = client.id
                    st.rerun()


def _render_detail_view(
    client_repo: ClientRepository,
    session_repo: SessionRepository,
) -> None:
    """詳細ビューを表示する。

    選択された相談者の基本情報、メモ編集、鑑定履歴サマリを表示する。

    Args:
        client_repo: 相談者リポジトリ。
        session_repo: セッションリポジトリ。
    """
    client_id: str = st.session_state[SESSION_KEY_CLIENTS_SELECTED]

    # --- 戻るボタン ---
    if st.button("< 一覧に戻る"):
        st.session_state[SESSION_KEY_CLIENTS_SELECTED] = None
        st.rerun()

    # --- 相談者データ取得 ---
    try:
        client = client_repo.find_by_id(client_id)
    except DatabaseError as e:
        logger.error("相談者の取得に失敗: %s", e)
        st.error("相談者情報の取得に失敗しました。")
        return

    if client is None:
        st.error("指定された相談者が見つかりません。")
        st.session_state[SESSION_KEY_CLIENTS_SELECTED] = None
        return

    st.subheader(client.name)

    # --- 基本情報 ---
    col1, col2, col3 = st.columns(3)
    col1.metric("生年月日", client.birth_date)
    col2.metric("出生時間", client.birth_time or "不明")
    col3.metric("性別", client.gender or "未回答")

    st.caption(f"登録日: {client.created_at[:10]} | 更新日: {client.updated_at[:10]}")

    # --- メモ編集 ---
    st.markdown("---")
    st.markdown("#### メモ")

    current_notes = client.notes or ""
    new_notes = st.text_area(
        "メモ（自由記述）",
        value=current_notes,
        height=120,
        placeholder="相談者に関するメモを入力...",
        label_visibility="collapsed",
    )

    if st.button("メモを保存", use_container_width=True):
        if new_notes != current_notes:
            try:
                client_repo.update(client_id=client_id, notes=new_notes)
                st.success("メモを保存しました。")
                st.rerun()
            except DatabaseError as e:
                logger.error("メモの保存に失敗: %s", e)
                st.error("メモの保存に失敗しました。")
        else:
            st.info("変更はありません。")

    # --- 鑑定履歴サマリ ---
    st.markdown("---")
    st.markdown("#### 鑑定履歴")

    try:
        sessions = session_repo.find_by_client_id(client_id)
    except DatabaseError as e:
        logger.error("鑑定履歴の取得に失敗: %s", e)
        st.error("鑑定履歴の取得に失敗しました。")
        return

    if not sessions:
        st.info("鑑定履歴がありません。")
        return

    st.caption(f"{len(sessions)} 件の鑑定")

    for s in sessions:
        concern_preview = (
            s.concern[:CONCERN_PREVIEW_LENGTH] + "..."
            if len(s.concern) > CONCERN_PREVIEW_LENGTH
            else s.concern
        )
        created_date = s.created_at[:10] if s.created_at else "不明"
        has_ai = "AI鑑定あり" if s.ai_reading_text else "命式のみ"

        with st.container(border=True):
            st.write(f"**{created_date}** — {has_ai}")
            st.caption(concern_preview)


def main() -> None:
    """相談者管理ページのメイン処理。"""
    _initialize_state()

    st.title("相談者管理")

    conn = get_db_connection()
    client_repo = ClientRepository(conn)
    session_repo = SessionRepository(conn)

    # --- ビュー切り替え ---
    if st.session_state[SESSION_KEY_CLIENTS_SELECTED] is not None:
        _render_detail_view(client_repo, session_repo)
    else:
        _render_list_view(client_repo, session_repo)


main()
