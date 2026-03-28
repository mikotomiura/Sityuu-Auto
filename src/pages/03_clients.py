"""相談者管理ページ — 相談者の一覧表示・検索・詳細閲覧・情報編集。

Note:
    認証は app.py の require_login() に加え、ページ冒頭の
    require_page_auth() で二重チェックする（防御深度）。
"""

import html
import logging
from datetime import date, datetime

import streamlit as st

from config import (
    CONCERN_PREVIEW_LENGTH,
    SESSION_KEY_CLIENTS_EDIT_SUCCESS,
    SESSION_KEY_CLIENTS_SEARCH_QUERY,
    SESSION_KEY_CLIENTS_SELECTED,
)
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository
from utils.auth import require_page_auth
from utils.exceptions import DatabaseError
from utils.privacy import inject_autocomplete_off

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
        autocomplete="one-time-code",
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
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">\U0001f465</div>'
            '<div class="empty-state-text">'
            "相談者がまだ登録されていません。<br>"
            "鑑定ページから鑑定を行うと自動登録されます。"
            "</div></div>",
            unsafe_allow_html=True,
        )
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
                badge_class = "status-badge-ai" if session_count > 0 else "status-badge-basic"
                badge_text = f"{session_count}回鑑定" if session_count > 0 else "未鑑定"
                # SECURITY: client.name はDB由来の自由入力。XSS防止のためエスケープ必須。
                safe_name = html.escape(client.name)
                st.markdown(
                    f'**{safe_name}** <span class="status-badge {badge_class}">{badge_text}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(f"生年月日: {client.birth_date} | 登録日: {client.created_at[:10]}")

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
    st.caption(f"登録日: {client.created_at[:10]} | 更新日: {client.updated_at[:10]}")

    # --- 更新成功メッセージ（rerun後に表示） ---
    if st.session_state.pop(SESSION_KEY_CLIENTS_EDIT_SUCCESS, False):
        st.success("相談者情報を更新しました。")

    # --- 相談者情報の編集 ---
    st.markdown("---")
    st.markdown("#### 相談者情報の編集")
    st.caption("※ 生年月日・出生時間を変更しても、過去の鑑定結果の命式は更新されません。")

    current_name = client.name
    current_kana = client.name_kana or ""
    current_birth_date = date.fromisoformat(client.birth_date)
    current_birth_time = client.birth_time
    current_gender = client.gender
    current_notes = client.notes or ""

    with st.form("client_edit_form"):
        # 名前・フリガナ
        col_name, col_kana = st.columns(2)
        new_name = col_name.text_input(
            "名前",
            value=current_name,
            max_chars=50,
            placeholder="例: 山田 太郎",
            autocomplete="one-time-code",
        )
        new_kana = col_kana.text_input(
            "フリガナ",
            value=current_kana,
            max_chars=50,
            placeholder="例: ヤマダ タロウ",
            autocomplete="one-time-code",
        )

        # 生年月日・出生時間・性別
        col_bd, col_bt, col_gender = st.columns(3)

        new_birth_date = col_bd.date_input(
            "生年月日",
            value=current_birth_date,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )

        # 出生時間: checkbox + time_input（form内なので常に両方表示）
        has_birth_time = current_birth_time is not None
        use_birth_time = col_bt.checkbox("出生時間あり", value=has_birth_time)
        default_time = (
            datetime.strptime(current_birth_time, "%H:%M").time()
            if current_birth_time
            else datetime.strptime("12:00", "%H:%M").time()
        )
        new_birth_time_val = col_bt.time_input(
            "出生時間", value=default_time, disabled=not use_birth_time
        )
        new_birth_time: str | None = (
            new_birth_time_val.strftime("%H:%M") if use_birth_time else None
        )

        # 性別
        gender_options = ["未回答", "男性", "女性"]
        current_gender_index = (
            gender_options.index(current_gender) if current_gender in gender_options else 0
        )
        new_gender_display = col_gender.selectbox(
            "性別",
            options=gender_options,
            index=current_gender_index,
        )
        new_gender: str | None = new_gender_display if new_gender_display != "未回答" else None

        # メモ
        new_notes = st.text_area(
            "メモ（自由記述）",
            value=current_notes,
            height=120,
            placeholder="相談者に関するメモを入力...",
        )

        submitted = st.form_submit_button("変更を保存", use_container_width=True)

    if submitted:
        # 変更検出
        name_changed = new_name.strip() != current_name
        kana_changed = new_kana.strip() != current_kana
        birth_date_changed = new_birth_date != current_birth_date
        birth_time_changed = new_birth_time != current_birth_time
        gender_changed = new_gender != current_gender
        notes_changed = new_notes != current_notes

        has_changes = any(
            [
                name_changed,
                kana_changed,
                birth_date_changed,
                birth_time_changed,
                gender_changed,
                notes_changed,
            ]
        )

        if not has_changes:
            st.info("変更はありません。")
        elif not new_name.strip():
            st.warning("名前は必須です。")
        else:
            try:
                update_kwargs: dict[str, object] = {}
                if name_changed:
                    update_kwargs["name"] = new_name.strip()
                if kana_changed:
                    update_kwargs["name_kana"] = new_kana.strip() or None
                if birth_date_changed:
                    update_kwargs["birth_date"] = new_birth_date
                if birth_time_changed:
                    update_kwargs["birth_time"] = new_birth_time
                if gender_changed:
                    update_kwargs["gender"] = new_gender
                if notes_changed:
                    update_kwargs["notes"] = new_notes
                client_repo.update(client_id=client_id, **update_kwargs)
                st.session_state[SESSION_KEY_CLIENTS_EDIT_SUCCESS] = True
                st.rerun()
            except DatabaseError as e:
                logger.error("相談者情報の更新に失敗: %s", e)
                st.error("更新に失敗しました。")

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
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">\U0001f4cb</div>'
            '<div class="empty-state-text">鑑定履歴がありません。</div>'
            "</div>",
            unsafe_allow_html=True,
        )
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
    require_page_auth()
    _initialize_state()
    inject_autocomplete_off()

    st.title("相談者管理")
    st.markdown(
        '<p class="page-description">'
        "相談者の基本情報の閲覧・編集と、鑑定履歴のサマリを確認できます"
        "</p>",
        unsafe_allow_html=True,
    )

    conn = get_db_connection()
    client_repo = ClientRepository(conn)
    session_repo = SessionRepository(conn)

    # --- ビュー切り替え ---
    if st.session_state[SESSION_KEY_CLIENTS_SELECTED] is not None:
        _render_detail_view(client_repo, session_repo)
    else:
        _render_list_view(client_repo, session_repo)


main()
