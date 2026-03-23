"""UserRepository のユニットテスト。"""

import json
import sqlite3

import pytest

from db_service.database import initialize_database
from db_service.repositories.user_repo import (
    UserRepository,
    hash_password,
    verify_password,
)
from utils.exceptions import AuthenticationError, DatabaseError


@pytest.fixture()
def db_conn() -> sqlite3.Connection:
    """インメモリDBのコネクションを返す。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    initialize_database(conn)
    return conn


@pytest.fixture()
def user_repo(db_conn: sqlite3.Connection) -> UserRepository:
    """テスト用 UserRepository を返す。"""
    return UserRepository(db_conn)


class TestHashPassword:
    """パスワードハッシュのユーティリティ関数テスト。"""

    def test_hash_and_verify_password(self) -> None:
        """ハッシュ化と照合が正常に動作すること。"""
        pw = "test_password_123"
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed) is True

    def test_verify_wrong_password(self) -> None:
        """異なるパスワードで照合失敗すること。"""
        hashed = hash_password("correct_password")
        assert verify_password("wrong_password", hashed) is False


class TestUserRepositoryCreate:
    """ユーザー作成のテスト。"""

    def test_create_user_returns_uuid(self, user_repo: UserRepository) -> None:
        """ユーザー作成がUUIDを返すこと。"""
        user_id = user_repo.create("testuser", "password123")
        assert isinstance(user_id, str)
        assert len(user_id) == 36  # UUID format

    def test_create_duplicate_username_raises_error(self, user_repo: UserRepository) -> None:
        """重複ユーザー名でDatabaseErrorが発生すること。"""
        user_repo.create("testuser", "password123")
        with pytest.raises(DatabaseError, match="既に使用されています"):
            user_repo.create("testuser", "other_password")

    def test_create_user_with_admin_role(self, user_repo: UserRepository) -> None:
        """adminロールでユーザーを作成できること。"""
        user_id = user_repo.create("admin_user", "password123", role="admin")
        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.role == "admin"


class TestUserRepositoryAuthenticate:
    """認証のテスト。"""

    def test_authenticate_success(self, user_repo: UserRepository) -> None:
        """正しい認証情報でUserRecordが返ること。"""
        user_repo.create("testuser", "password123")
        user = user_repo.authenticate("testuser", "password123")
        assert user.username == "testuser"

    def test_authenticate_wrong_password(self, user_repo: UserRepository) -> None:
        """パスワード不一致でAuthenticationErrorが発生すること。"""
        user_repo.create("testuser", "password123")
        with pytest.raises(AuthenticationError):
            user_repo.authenticate("testuser", "wrong_password")

    def test_authenticate_nonexistent_user(self, user_repo: UserRepository) -> None:
        """存在しないユーザーでAuthenticationErrorが発生すること。"""
        with pytest.raises(AuthenticationError):
            user_repo.authenticate("nonexistent", "password123")


class TestUserRepositoryFind:
    """ユーザー検索のテスト。"""

    def test_find_by_id(self, user_repo: UserRepository) -> None:
        """IDでユーザーを検索できること。"""
        user_id = user_repo.create("testuser", "password123")
        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.username == "testuser"

    def test_find_by_id_not_found(self, user_repo: UserRepository) -> None:
        """存在しないIDでNoneが返ること。"""
        assert user_repo.find_by_id("nonexistent-id") is None

    def test_find_by_username(self, user_repo: UserRepository) -> None:
        """ユーザー名でユーザーを検索できること。"""
        user_repo.create("testuser", "password123")
        user = user_repo.find_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_find_by_username_not_found(self, user_repo: UserRepository) -> None:
        """存在しないユーザー名でNoneが返ること。"""
        assert user_repo.find_by_username("nonexistent") is None


class TestUserRepositoryUpdatePassword:
    """パスワード更新のテスト。"""

    def test_update_password(self, user_repo: UserRepository) -> None:
        """パスワードを更新し、新パスワードで認証できること。"""
        user_id = user_repo.create("testuser", "old_password")
        result = user_repo.update_password(user_id, "new_password")
        assert result is True

        # 新パスワードで認証
        user = user_repo.authenticate("testuser", "new_password")
        assert user.username == "testuser"

        # 旧パスワードで認証失敗
        with pytest.raises(AuthenticationError):
            user_repo.authenticate("testuser", "old_password")


class TestUserRepositoryApiKeys:
    """APIキー管理のテスト。"""

    def test_get_api_key_when_none(self, user_repo: UserRepository) -> None:
        """APIキー未登録時にNoneが返ること。"""
        user_id = user_repo.create("testuser", "password123")
        assert user_repo.get_api_key(user_id, "gemini") is None

    def test_update_and_get_api_key(self, user_repo: UserRepository) -> None:
        """APIキーを保存・取得できること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_api_key(user_id, "gemini", "test-gemini-key")

        key = user_repo.get_api_key(user_id, "gemini")
        assert key == "test-gemini-key"

    def test_update_multiple_provider_keys(self, user_repo: UserRepository) -> None:
        """複数プロバイダーのキーを独立して管理できること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_api_key(user_id, "gemini", "gemini-key")
        user_repo.update_api_key(user_id, "openai", "openai-key")

        assert user_repo.get_api_key(user_id, "gemini") == "gemini-key"
        assert user_repo.get_api_key(user_id, "openai") == "openai-key"
        assert user_repo.get_api_key(user_id, "anthropic") is None

    def test_delete_api_key_with_empty_string(self, user_repo: UserRepository) -> None:
        """空文字列でAPIキーを削除できること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_api_key(user_id, "gemini", "test-key")
        user_repo.update_api_key(user_id, "gemini", "")

        assert user_repo.get_api_key(user_id, "gemini") is None

    def test_get_api_key_for_nonexistent_user(self, user_repo: UserRepository) -> None:
        """存在しないユーザーIDでNoneが返ること。"""
        assert user_repo.get_api_key("nonexistent-id", "gemini") is None


class TestUserRepositoryPreferences:
    """ユーザー設定（プロバイダー・モデル）永続化のテスト。"""

    def test_preferences_initially_none(self, user_repo: UserRepository) -> None:
        """新規ユーザーの設定がNoneであること。"""
        user_id = user_repo.create("testuser", "password123")
        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.preferred_provider is None
        assert user.preferred_model is None

    def test_update_preferences(self, user_repo: UserRepository) -> None:
        """設定を保存・取得できること。"""
        user_id = user_repo.create("testuser", "password123")
        result = user_repo.update_preferences(user_id, "openai", "gpt-4o")
        assert result is True

        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.preferred_provider == "openai"
        assert user.preferred_model == "gpt-4o"

    def test_update_preferences_partial(self, user_repo: UserRepository) -> None:
        """プロバイダーのみ更新できること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_preferences(user_id, "gemini", None)

        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.preferred_provider == "gemini"
        assert user.preferred_model is None

    def test_preferences_persist_across_reads(self, user_repo: UserRepository) -> None:
        """保存した設定が再取得時も維持されること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_preferences(user_id, "anthropic", "claude-sonnet-4-20250514")

        # 再度取得
        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.preferred_provider == "anthropic"
        assert user.preferred_model == "claude-sonnet-4-20250514"

    def test_update_preferences_nonexistent_user(self, user_repo: UserRepository) -> None:
        """存在しないユーザーでFalseが返ること。"""
        result = user_repo.update_preferences("nonexistent-id", "gemini", "model")
        assert result is False


class TestUserRepositoryCount:
    """ユーザー数取得のテスト。"""

    def test_count_empty(self, user_repo: UserRepository) -> None:
        """ユーザーなしで0が返ること。"""
        assert user_repo.count() == 0

    def test_count_after_create(self, user_repo: UserRepository) -> None:
        """ユーザー作成後にカウントが増えること。"""
        user_repo.create("user1", "pw1")
        user_repo.create("user2", "pw2")
        assert user_repo.count() == 2
