"""require_page_auth のユニットテスト。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from config import SESSION_KEY_AUTH_USER_ID
from utils.auth import require_page_auth


class _StopException(Exception):
    """st.stop() の代替例外。"""


@pytest.fixture(autouse=True)
def _mock_streamlit():
    """Streamlit の session_state と stop/error をモックする。"""
    with (
        patch("utils.auth.st") as mock_st,
    ):
        mock_st.session_state = {}
        mock_st.stop = MagicMock(side_effect=_StopException)
        mock_st.error = MagicMock()
        yield mock_st


class TestRequirePageAuth:
    """require_page_auth のテスト。"""

    def test_logged_in_passes(self, _mock_streamlit: MagicMock) -> None:
        """ログイン済みの場合は何もせずに返る。"""
        _mock_streamlit.session_state[SESSION_KEY_AUTH_USER_ID] = "user-123"
        require_page_auth()
        _mock_streamlit.error.assert_not_called()
        _mock_streamlit.stop.assert_not_called()

    def test_not_logged_in_stops(self, _mock_streamlit: MagicMock) -> None:
        """未ログインの場合はエラー表示して停止する。"""
        with pytest.raises(_StopException):
            require_page_auth()
        _mock_streamlit.error.assert_called_once_with("ログインが必要です。")
        _mock_streamlit.stop.assert_called_once()

    def test_empty_user_id_stops(self, _mock_streamlit: MagicMock) -> None:
        """空文字列のuser_idは未ログイン扱い。"""
        _mock_streamlit.session_state[SESSION_KEY_AUTH_USER_ID] = ""
        with pytest.raises(_StopException):
            require_page_auth()
        _mock_streamlit.error.assert_called_once()
