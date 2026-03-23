"""認証ユーティリティ — ログイン状態の管理とUI表示。

Streamlit の st.session_state を使用してログイン状態を管理する。
未ログイン時はログインフォームを表示し、st.stop() でページ遷移を阻止する。
"""

import logging
import time

import streamlit as st

from config import (
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_AUTH_FAIL_COUNT,
    SESSION_KEY_AUTH_ROLE,
    SESSION_KEY_AUTH_USER_ID,
    SESSION_KEY_AUTH_USERNAME,
)
from db_service.repositories.user_repo import UserRepository
from utils.exceptions import AuthenticationError, DatabaseError

logger = logging.getLogger(__name__)


def is_logged_in() -> bool:
    """ログイン済みかどうかを判定する。

    Returns:
        ログイン済みなら True。
    """
    return bool(st.session_state.get(SESSION_KEY_AUTH_USER_ID))


def get_current_user_id() -> str | None:
    """現在のログインユーザーIDを取得する。

    Returns:
        ユーザーID文字列。未ログインの場合は None。
    """
    return st.session_state.get(SESSION_KEY_AUTH_USER_ID)


def get_current_username() -> str | None:
    """現在のログインユーザー名を取得する。

    Returns:
        ユーザー名。未ログインの場合は None。
    """
    return st.session_state.get(SESSION_KEY_AUTH_USERNAME)


def logout() -> None:
    """ログアウト処理（セッションから認証情報とAPI設定を削除）。"""
    for key in (
        SESSION_KEY_AUTH_USER_ID,
        SESSION_KEY_AUTH_USERNAME,
        SESSION_KEY_AUTH_ROLE,
        SESSION_KEY_AUTH_FAIL_COUNT,
        SESSION_KEY_API_PROVIDER,
        SESSION_KEY_API_MODEL,
    ):
        st.session_state.pop(key, None)


def _login(user_repo: UserRepository, username: str, password: str) -> bool:
    """ログイン処理を実行する。

    Args:
        user_repo: UserRepository インスタンス。
        username: ユーザー名。
        password: 平文パスワード。

    Returns:
        ログイン成功なら True。
    """
    try:
        user = user_repo.authenticate(username, password)
        st.session_state[SESSION_KEY_AUTH_USER_ID] = user.id
        st.session_state[SESSION_KEY_AUTH_USERNAME] = user.username
        st.session_state[SESSION_KEY_AUTH_ROLE] = user.role
        # ユーザーの保存済みAPI設定を復元
        if user.preferred_provider:
            st.session_state[SESSION_KEY_API_PROVIDER] = user.preferred_provider
        if user.preferred_model:
            st.session_state[SESSION_KEY_API_MODEL] = user.preferred_model
        st.session_state.pop(SESSION_KEY_AUTH_FAIL_COUNT, None)
        logger.info("ログイン成功: username=%s", username)
        return True
    except AuthenticationError:
        logger.warning("ログイン失敗: username=%s", username)
        # ブルートフォース対策: 失敗回数に応じた遅延
        fails = st.session_state.get(SESSION_KEY_AUTH_FAIL_COUNT, 0) + 1
        st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] = fails
        delay = min(fails * 1.0, 5.0)  # 最大5秒
        time.sleep(delay)
        return False


def render_login_form(user_repo: UserRepository) -> None:
    """ログインフォームを画面中央に表示する。

    ログイン成功時は st.rerun() でページを再読み込みする。

    Args:
        user_repo: UserRepository インスタンス。
    """
    # サイドバーを視覚的に非表示にする
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="stSidebarCollapsedControl"] { display: none; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 中央寄せのレイアウト
    _col_left, col_center, _col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            "<h1 style='text-align: center; margin-bottom: 0.5em;'>"
            "\U0001f52e Sityuu-Auto</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align: center; opacity: 0.7; margin-bottom: 2em;'>"
            "四柱推命・算命学 AI鑑定支援ツール</p>",
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("ユーザー名", placeholder="username")
            password = st.text_input("パスワード", type="password", placeholder="password")
            submitted = st.form_submit_button("ログイン", type="primary", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("ユーザー名とパスワードを入力してください。")
                else:
                    try:
                        success = _login(user_repo, username, password)
                        if success:
                            st.rerun()
                        else:
                            st.error("ユーザー名またはパスワードが正しくありません。")
                    except DatabaseError:
                        st.error("認証処理中にエラーが発生しました。")


def require_login(user_repo: UserRepository) -> None:
    """ログインを必須にする。未ログイン時はフォームを表示して st.stop()。

    app.py のページ設定後に呼び出す。

    Args:
        user_repo: UserRepository インスタンス。
    """
    if is_logged_in():
        return

    render_login_form(user_repo)
    st.stop()
