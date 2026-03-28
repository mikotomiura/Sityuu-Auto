"""utils/auth モジュールのユニットテスト。

認証コアロジック（_login, logout, _try_restore_from_token, _restore_session_from_user,
is_logged_in, get_current_user_id, get_current_display_name, get_current_username,
require_login）をテストする。
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from config import (
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_AUTH_DISPLAY_NAME,
    SESSION_KEY_AUTH_FAIL_COUNT,
    SESSION_KEY_AUTH_ROLE,
    SESSION_KEY_AUTH_USER_ID,
    SESSION_KEY_AUTH_USERNAME,
    SESSION_TOKEN_QUERY_PARAM,
)
from db_service.models import UserRecord
from utils.exceptions import AuthenticationError, DatabaseError


class _StopException(Exception):
    """st.stop() の代替例外。"""


class _RerunException(Exception):
    """st.rerun() の代替例外。"""


def _make_user(
    *,
    user_id: str = "user-001",
    username: str = "testuser",
    role: str = "user",
    display_name: str | None = "テストユーザー",
    preferred_provider: str | None = None,
    preferred_model: str | None = None,
) -> UserRecord:
    """テスト用 UserRecord を生成する。"""
    return UserRecord(
        id=user_id,
        username=username,
        password_hash="$2b$12$dummy",
        api_keys_json=None,
        preferred_provider=preferred_provider,
        preferred_model=preferred_model,
        role=role,
        display_name=display_name,
        created_at="2026-01-01T00:00:00",
        updated_at="2026-01-01T00:00:00",
    )


@pytest.fixture()
def mock_st():
    """Streamlit をモックし、session_state / query_params / stop / rerun を提供する。"""
    with patch("utils.auth.st") as m:
        m.session_state = {}
        m.query_params = {}
        m.stop = MagicMock(side_effect=_StopException)
        m.rerun = MagicMock(side_effect=_RerunException)
        m.error = MagicMock()
        m.warning = MagicMock()
        m.markdown = MagicMock()
        m.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        m.form = MagicMock()
        m.text_input = MagicMock(return_value="")
        m.form_submit_button = MagicMock(return_value=False)
        yield m


# ---------------------------------------------------------------------------
# is_logged_in / get_current_user_id / get_current_username / get_current_display_name
# ---------------------------------------------------------------------------
class TestSessionHelpers:
    """セッション状態ヘルパー関数のテスト。"""

    def test_is_logged_in_true(self, mock_st: MagicMock) -> None:
        """ユーザーIDがあればTrue。"""
        mock_st.session_state[SESSION_KEY_AUTH_USER_ID] = "u-1"
        from utils.auth import is_logged_in

        assert is_logged_in() is True

    def test_is_logged_in_false(self, mock_st: MagicMock) -> None:
        """ユーザーIDがなければFalse。"""
        from utils.auth import is_logged_in

        assert is_logged_in() is False

    def test_get_current_user_id(self, mock_st: MagicMock) -> None:
        """session_stateからユーザーIDを取得。"""
        mock_st.session_state[SESSION_KEY_AUTH_USER_ID] = "u-1"
        from utils.auth import get_current_user_id

        assert get_current_user_id() == "u-1"

    def test_get_current_user_id_none(self, mock_st: MagicMock) -> None:
        """未ログインならNone。"""
        from utils.auth import get_current_user_id

        assert get_current_user_id() is None

    def test_get_current_username(self, mock_st: MagicMock) -> None:
        """session_stateからユーザー名を取得。"""
        mock_st.session_state[SESSION_KEY_AUTH_USERNAME] = "admin"
        from utils.auth import get_current_username

        assert get_current_username() == "admin"

    def test_get_current_display_name_with_display(self, mock_st: MagicMock) -> None:
        """display_nameが設定されていればそれを返す。"""
        mock_st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] = "表示名"
        mock_st.session_state[SESSION_KEY_AUTH_USERNAME] = "user"
        from utils.auth import get_current_display_name

        assert get_current_display_name() == "表示名"

    def test_get_current_display_name_fallback(self, mock_st: MagicMock) -> None:
        """display_nameがなければusernameをフォールバック。"""
        mock_st.session_state[SESSION_KEY_AUTH_USERNAME] = "user"
        from utils.auth import get_current_display_name

        assert get_current_display_name() == "user"


# ---------------------------------------------------------------------------
# _restore_session_from_user
# ---------------------------------------------------------------------------
class TestRestoreSessionFromUser:
    """_restore_session_from_user のテスト。"""

    def test_basic_restore(self, mock_st: MagicMock) -> None:
        """基本フィールドが復元される。"""
        user = _make_user()
        from utils.auth import _restore_session_from_user

        _restore_session_from_user(user)
        assert mock_st.session_state[SESSION_KEY_AUTH_USER_ID] == "user-001"
        assert mock_st.session_state[SESSION_KEY_AUTH_USERNAME] == "testuser"
        assert mock_st.session_state[SESSION_KEY_AUTH_ROLE] == "user"
        assert mock_st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] == "テストユーザー"

    def test_restore_with_preferences(self, mock_st: MagicMock) -> None:
        """APIプロバイダー・モデル設定が復元される。"""
        user = _make_user(preferred_provider="openai", preferred_model="gpt-4o")
        from utils.auth import _restore_session_from_user

        _restore_session_from_user(user)
        assert mock_st.session_state[SESSION_KEY_API_PROVIDER] == "openai"
        assert mock_st.session_state[SESSION_KEY_API_MODEL] == "gpt-4o"

    def test_restore_without_preferences(self, mock_st: MagicMock) -> None:
        """API設定がNoneの場合はsession_stateに書き込まない。"""
        user = _make_user(preferred_provider=None, preferred_model=None)
        from utils.auth import _restore_session_from_user

        _restore_session_from_user(user)
        assert SESSION_KEY_API_PROVIDER not in mock_st.session_state
        assert SESSION_KEY_API_MODEL not in mock_st.session_state

    def test_restore_display_name_fallback(self, mock_st: MagicMock) -> None:
        """display_nameがNoneならusernameがセットされる。"""
        user = _make_user(display_name=None)
        from utils.auth import _restore_session_from_user

        _restore_session_from_user(user)
        assert mock_st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] == "testuser"


# ---------------------------------------------------------------------------
# logout
# ---------------------------------------------------------------------------
class TestLogout:
    """logout のテスト。"""

    def test_clears_session_state(self, mock_st: MagicMock) -> None:
        """session_stateから認証・API設定キーがクリアされる。"""
        mock_st.session_state[SESSION_KEY_AUTH_USER_ID] = "u-1"
        mock_st.session_state[SESSION_KEY_AUTH_USERNAME] = "user"
        mock_st.session_state[SESSION_KEY_AUTH_ROLE] = "admin"
        mock_st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] = "name"
        mock_st.session_state[SESSION_KEY_API_PROVIDER] = "openai"
        mock_st.session_state[SESSION_KEY_API_MODEL] = "gpt-4o"
        from utils.auth import logout

        logout()
        assert SESSION_KEY_AUTH_USER_ID not in mock_st.session_state
        assert SESSION_KEY_AUTH_USERNAME not in mock_st.session_state
        assert SESSION_KEY_AUTH_ROLE not in mock_st.session_state
        assert SESSION_KEY_API_PROVIDER not in mock_st.session_state

    def test_revokes_db_token(self, mock_st: MagicMock) -> None:
        """auth_session_repo指定時にDBトークンが無効化される。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "tok-abc"
        repo = MagicMock()
        from utils.auth import logout

        logout(auth_session_repo=repo)
        repo.revoke.assert_called_once_with("tok-abc")
        assert SESSION_TOKEN_QUERY_PARAM not in mock_st.query_params

    def test_revoke_db_error_ignored(self, mock_st: MagicMock) -> None:
        """DB無効化失敗でもログアウトは継続する。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "tok-abc"
        repo = MagicMock()
        repo.revoke.side_effect = DatabaseError("DB error")
        from utils.auth import logout

        logout(auth_session_repo=repo)
        # session_stateはクリアされていること
        assert SESSION_KEY_AUTH_USER_ID not in mock_st.session_state

    def test_no_token_no_repo(self, mock_st: MagicMock) -> None:
        """トークンなし・repo未指定でもエラーなくクリアされる。"""
        mock_st.session_state[SESSION_KEY_AUTH_USER_ID] = "u-1"
        from utils.auth import logout

        logout()
        assert SESSION_KEY_AUTH_USER_ID not in mock_st.session_state


# ---------------------------------------------------------------------------
# _try_restore_from_token
# ---------------------------------------------------------------------------
class TestTryRestoreFromToken:
    """_try_restore_from_token のテスト。"""

    def test_no_token_returns_false(self, mock_st: MagicMock) -> None:
        """URLにトークンがなければFalse。"""
        repo = MagicMock()
        from utils.auth import _try_restore_from_token

        assert _try_restore_from_token(repo) is False
        repo.validate_token.assert_not_called()

    def test_valid_token_restores_and_keeps_url(self, mock_st: MagicMock) -> None:
        """有効なトークンでセッション復元��URLからトークン削除。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "valid-token"
        user = _make_user()
        repo = MagicMock()
        repo.validate_token.return_value = user
        from utils.auth import _try_restore_from_token

        result = _try_restore_from_token(repo)
        assert result is True
        assert mock_st.session_state[SESSION_KEY_AUTH_USER_ID] == "user-001"
        assert mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] == "valid-token"

    def test_invalid_token_removes_url(self, mock_st: MagicMock) -> None:
        """無効なトークンではFalse＆URLからトークン削除。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "expired-token"
        repo = MagicMock()
        repo.validate_token.return_value = None
        from utils.auth import _try_restore_from_token

        result = _try_restore_from_token(repo)
        assert result is False
        assert SESSION_TOKEN_QUERY_PARAM not in mock_st.query_params

    def test_db_error_returns_false(self, mock_st: MagicMock) -> None:
        """DB検証エラー時はFalse（セッション未復元）。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "some-token"
        repo = MagicMock()
        repo.validate_token.side_effect = DatabaseError("connection lost")
        from utils.auth import _try_restore_from_token

        result = _try_restore_from_token(repo)
        assert result is False
        assert SESSION_KEY_AUTH_USER_ID not in mock_st.session_state


# ---------------------------------------------------------------------------
# _login
# ---------------------------------------------------------------------------
class TestLogin:
    """_login のテスト。"""

    def test_success(self, mock_st: MagicMock) -> None:
        """認証成功でTrueを返しsession_stateが復元される。"""
        user = _make_user()
        user_repo = MagicMock()
        user_repo.authenticate.return_value = user
        from utils.auth import _login

        result = _login(user_repo, "testuser", "password123")
        assert result is True
        assert mock_st.session_state[SESSION_KEY_AUTH_USER_ID] == "user-001"

    def test_success_creates_session_token(self, mock_st: MagicMock) -> None:
        """auth_session_repo指定時にトークンが生成されURLに埋め込まれる。"""
        user = _make_user()
        user_repo = MagicMock()
        user_repo.authenticate.return_value = user
        session_repo = MagicMock()
        session_repo.create.return_value = "new-token-xyz"
        from utils.auth import _login

        result = _login(user_repo, "testuser", "pw", auth_session_repo=session_repo)
        assert result is True
        session_repo.create.assert_called_once_with("user-001")
        assert mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] == "new-token-xyz"
        session_repo.cleanup_expired.assert_called_once()

    def test_success_token_creation_failure_continues(self, mock_st: MagicMock) -> None:
        """トークン生成失敗でもログイン自体は成功する。"""
        user = _make_user()
        user_repo = MagicMock()
        user_repo.authenticate.return_value = user
        session_repo = MagicMock()
        session_repo.create.side_effect = DatabaseError("DB error")
        from utils.auth import _login

        result = _login(user_repo, "testuser", "pw", auth_session_repo=session_repo)
        assert result is True

    @patch("utils.auth.time.sleep")
    def test_failure_returns_false(self, mock_sleep: MagicMock, mock_st: MagicMock) -> None:
        """認証失敗でFalseを返し失敗カウントが増加する。"""
        user_repo = MagicMock()
        user_repo.authenticate.side_effect = AuthenticationError("bad password")
        from utils.auth import _login

        result = _login(user_repo, "testuser", "wrong")
        assert result is False
        assert mock_st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] == 1
        mock_sleep.assert_called_once_with(1.0)

    @patch("utils.auth.time.sleep")
    def test_failure_delay_increases(self, mock_sleep: MagicMock, mock_st: MagicMock) -> None:
        """連続失敗で遅延が増加する（最大5秒）。"""
        mock_st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] = 4
        user_repo = MagicMock()
        user_repo.authenticate.side_effect = AuthenticationError("bad")
        from utils.auth import _login

        _login(user_repo, "testuser", "wrong")
        assert mock_st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] == 5
        mock_sleep.assert_called_once_with(5.0)

    @patch("utils.auth.time.sleep")
    def test_failure_delay_capped_at_5(self, mock_sleep: MagicMock, mock_st: MagicMock) -> None:
        """失敗回数が5を超えても遅延は5秒で頭打ち。"""
        mock_st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] = 10
        user_repo = MagicMock()
        user_repo.authenticate.side_effect = AuthenticationError("bad")
        from utils.auth import _login

        _login(user_repo, "testuser", "wrong")
        mock_sleep.assert_called_once_with(5.0)

    def test_success_clears_fail_count(self, mock_st: MagicMock) -> None:
        """ログイン成功で失敗カウントがクリアされる。"""
        mock_st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] = 3
        user = _make_user()
        user_repo = MagicMock()
        user_repo.authenticate.return_value = user
        from utils.auth import _login

        _login(user_repo, "testuser", "correct")
        assert SESSION_KEY_AUTH_FAIL_COUNT not in mock_st.session_state


# ---------------------------------------------------------------------------
# require_login
# ---------------------------------------------------------------------------
class TestRequireLogin:
    """require_login のテスト。"""

    def test_already_logged_in_returns(self, mock_st: MagicMock) -> None:
        """ログイン済みなら即座にreturn。"""
        mock_st.session_state[SESSION_KEY_AUTH_USER_ID] = "u-1"
        user_repo = MagicMock()
        from utils.auth import require_login

        require_login(user_repo)
        mock_st.stop.assert_not_called()

    def test_token_restore_triggers_rerun(self, mock_st: MagicMock) -> None:
        """トークン復元成功時にst.rerun()が呼ばれる。"""
        mock_st.query_params[SESSION_TOKEN_QUERY_PARAM] = "valid"
        user = _make_user()
        user_repo = MagicMock()
        session_repo = MagicMock()
        session_repo.validate_token.return_value = user
        from utils.auth import require_login

        with pytest.raises(_RerunException):
            require_login(user_repo, auth_session_repo=session_repo)

    def test_no_auth_shows_login_form_and_stops(self, mock_st: MagicMock) -> None:
        """未ログイン・トークンなしでログインフォーム表示後にst.stop()。"""
        user_repo = MagicMock()
        from utils.auth import require_login

        with pytest.raises(_StopException):
            require_login(user_repo)
        mock_st.stop.assert_called()

    def test_invitation_token_shows_registration_and_stops(self, mock_st: MagicMock) -> None:
        """招待トークンありで登録フォーム表示後にst.stop()。"""
        mock_st.query_params["token"] = "invite-abc"
        mock_st.button.return_value = False
        user_repo = MagicMock()
        invitation_repo = MagicMock()
        invitation_repo.validate_token.return_value = MagicMock()
        from utils.auth import require_login

        with pytest.raises(_StopException):
            require_login(user_repo, invitation_repo=invitation_repo)
        mock_st.stop.assert_called()
