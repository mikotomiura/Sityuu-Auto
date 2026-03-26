"""ダッシュボードページ — ログイン後のトップページ。

利用状況の概要と最近の鑑定履歴を表示し、主要機能へのクイックアクセスを提供する。
"""

import logging

import streamlit as st

from config import SESSION_KEY_AUTH_DISPLAY_NAME, SESSION_KEY_AUTH_USERNAME
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _render_welcome_section() -> None:
    """ウェルカムメッセージを表示する。"""
    display_name = st.session_state.get(
        SESSION_KEY_AUTH_DISPLAY_NAME,
        st.session_state.get(SESSION_KEY_AUTH_USERNAME, ""),
    )
    st.markdown(
        f'<h2 style="margin-bottom:0.2em;">ようこそ、{display_name} さん</h2>',
        unsafe_allow_html=True,
    )
    st.caption("四柱推命・算命学 AI鑑定支援ツール")
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)


def _render_stats(
    client_repo: ClientRepository,
    session_repo: SessionRepository,
) -> None:
    """統計カードを表示する。

    Args:
        client_repo: 相談者リポジトリ。
        session_repo: セッションリポジトリ。
    """
    try:
        clients = client_repo.find_all(limit=9999)
        client_count = len(clients)
    except DatabaseError:
        client_count = 0

    try:
        sessions = session_repo.find_all(limit=9999)
        session_count = len(sessions)
    except DatabaseError:
        session_count = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("相談者数", f"{client_count} 名")
    col2.metric("鑑定回数", f"{session_count} 回")
    col3.metric("ステータス", "稼働中")


def _render_recent_sessions(session_repo: SessionRepository) -> None:
    """最近の鑑定履歴を表示する。

    Args:
        session_repo: セッションリポジトリ。
    """
    st.subheader("最近の鑑定")

    try:
        recent = session_repo.find_all_with_client_name(limit=5)
    except DatabaseError:
        st.warning("鑑定履歴の取得に失敗しました。")
        return

    if not recent:
        st.markdown(
            '<div class="empty-state">'
            '<div class="empty-state-icon">🔮</div>'
            '<div class="empty-state-text">'
            "まだ鑑定履歴がありません。<br>"
            "サイドバーの「鑑定」から最初の鑑定を始めましょう。"
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    for session in recent:
        with st.container(border=True):
            col_name, col_date = st.columns([3, 1])
            with col_name:
                concern_preview = (
                    session.concern[:40] + "…" if len(session.concern) > 40 else session.concern
                )
                st.markdown(f"**{session.client_name}** — {concern_preview}")
            with col_date:
                st.caption(session.created_at[:10])


def _render_quick_actions() -> None:
    """クイックアクションセクションを表示する。"""
    st.subheader("クイックアクション")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/01_reading.py", label="新しい鑑定を開始", icon="✨")
    with col2:
        st.page_link("pages/02_history.py", label="鑑定履歴を見る", icon="📋")
    with col3:
        st.page_link("pages/03_clients.py", label="相談者を管理", icon="👥")


def main() -> None:
    """ダッシュボードページのメイン処理。"""
    st.title("ダッシュボード")
    st.markdown(
        '<p class="page-description">'
        "利用状況の概要と最近の鑑定履歴を確認できます"
        "</p>",
        unsafe_allow_html=True,
    )

    _render_welcome_section()

    conn = get_db_connection()
    client_repo = ClientRepository(conn)
    session_repo = SessionRepository(conn)

    _render_stats(client_repo, session_repo)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        _render_recent_sessions(session_repo)

    with col_right:
        _render_quick_actions()


main()
