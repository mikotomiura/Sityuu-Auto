"""require_page_auth のユニットテスト。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from config import SESSION_KEY_AUTH_USER_ID, SESSION_TOKEN_QUERY_PARAM
from utils.auth import require_page_auth


class _StopException(Exception):
    """st.stop() の代替例外。"""


@pytest.fixture(autouse=True)
def _mock_streamlit():
    """Streamlit の session_state / query_params とUI関数をモックする。"""
    with (
        patch("utils.auth.st") as mock_st,
    ):
        mock_st.session_state = {}
        mock_st.query_params = {}
        mock_st.stop = MagicMock(side_effect=_StopException)
        mock_st.error = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.button = MagicMock(return_value=False)
        mock_st.page_link = MagicMock()
        yield mock_st


class TestRequirePageAuth:
    """require_page_auth のテスト。"""

    def test_logged_in_passes(self, _mock_streamlit: MagicMock) -> None:
        """ログイン済みの場合は何もせずに返る。"""
        _mock_streamlit.session_state[SESSION_KEY_AUTH_USER_ID] = "user-123"
        require_page_auth()
        _mock_streamlit.warning.assert_not_called()
        _mock_streamlit.stop.assert_not_called()

    def test_not_logged_in_no_token_shows_expiry_message(self, _mock_streamlit: MagicMock) -> None:
        """未ログイン・トークンなしの場合は期限切れメッセージを表示して停止。"""
        with pytest.raises(_StopException):
            require_page_auth()
        _mock_streamlit.warning.assert_called_once_with(
            "セッションの有効期限が切れました。再度ログインしてください。"
        )
        _mock_streamlit.page_link.assert_called_once()
        _mock_streamlit.stop.assert_called_once()

    def test_not_logged_in_with_token_shows_reload_message(
        self, _mock_streamlit: MagicMock
    ) -> None:
        """未ログイン・トークンありの場合はリロード案内を表示して停止。"""
        _mock_streamlit.query_params[SESSION_TOKEN_QUERY_PARAM] = "some-token"
        with pytest.raises(_StopException):
            require_page_auth()
        _mock_streamlit.warning.assert_called_once_with(
            "セッションの接続が切れました。ページを再読み込みしてください。"
        )
        _mock_streamlit.button.assert_called_once()
        _mock_streamlit.stop.assert_called_once()

    def test_empty_user_id_stops(self, _mock_streamlit: MagicMock) -> None:
        """空文字列のuser_idは未ログイン扱い。"""
        _mock_streamlit.session_state[SESSION_KEY_AUTH_USER_ID] = ""
        with pytest.raises(_StopException):
            require_page_auth()
        _mock_streamlit.warning.assert_called_once()
