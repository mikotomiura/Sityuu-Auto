"""ダッシュボードページ — ログイン後のトップページ。

利用状況の概要と最近の鑑定履歴を表示し、主要機能へのクイックアクセスを提供する。
"""

import logging

import streamlit as st

from config import (
    DEFAULT_API_PROVIDER,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_AUTH_DISPLAY_NAME,
    SESSION_KEY_AUTH_USERNAME,
)
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository
from db_service.repositories.user_repo import UserRepository
from utils.auth import get_current_user_id, require_page_auth
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
        client_count = client_repo.count()
    except DatabaseError:
        client_count = 0

    try:
        session_count = session_repo.count()
    except DatabaseError:
        session_count = 0

    # APIキー状態を確認
    provider = st.session_state.get(SESSION_KEY_API_PROVIDER, DEFAULT_API_PROVIDER)
    user_id = get_current_user_id()
    api_status = "未設定"
    if user_id:
        try:
            conn = get_db_connection()
            user_repo = UserRepository(conn)
            user_key = user_repo.get_api_key(user_id, provider)
            if user_key:
                api_status = "設定済み"
        except DatabaseError:
            pass

    col1, col2, col3 = st.columns(3)
    col1.metric("相談者数", f"{client_count} 名")
    col2.metric("鑑定回数", f"{session_count} 回")
    col3.metric("APIキー", api_status)


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

    for item in recent:
        s = item.session
        with st.container(border=True):
            col_name, col_date = st.columns([3, 1])
            with col_name:
                concern_preview = s.concern[:40] + "…" if len(s.concern) > 40 else s.concern
                st.markdown(f"**{item.client_name}** — {concern_preview}")
            with col_date:
                st.caption(s.created_at[:10])


def _render_quick_actions() -> None:
    """クイックアクションセクションを表示する。"""
    st.subheader("クイックアクション")

    st.page_link("pages/01_reading.py", label="✨ 新しい鑑定を開始", use_container_width=True)
    st.page_link("pages/02_history.py", label="📋 鑑定履歴を見る", use_container_width=True)
    st.page_link("pages/03_clients.py", label="👥 相談者を管理", use_container_width=True)
    st.page_link("pages/04_settings.py", label="⚙️ 設定", use_container_width=True)


def main() -> None:
    """ダッシュボードページのメイン処理。"""
    require_page_auth()
    st.title("ダッシュボード")
    st.markdown(
        '<p class="page-description">利用状況の概要と最近の鑑定履歴を確認できます</p>',
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
