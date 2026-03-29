"""UserRepository のユニットテスト。"""

import sqlite3

import pytest

from db_service.database import initialize_database
from db_service.repositories.user_repo import (
    UserRepository,
    generate_random_password,
    hash_password,
    verify_password,
)
from utils.exceptions import AuthenticationError, DatabaseError, ValidationError


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
        with pytest.raises(DatabaseError, match="既に使用されて"):
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


class TestGenerateRandomPassword:
    """パスワード生成関数のテスト。"""

    def test_default_length(self) -> None:
        """デフォルト12文字のパスワードが生成されること。"""
        pw = generate_random_password()
        assert len(pw) == 12

    def test_custom_length(self) -> None:
        """指定した長さのパスワードが生成されること。"""
        pw = generate_random_password(20)
        assert len(pw) == 20

    def test_alphanum_only(self) -> None:
        """英数字のみで構成されること。"""
        pw = generate_random_password(100)
        assert pw.isalnum()

    def test_randomness(self) -> None:
        """2回の生成で異なる値が返ること。"""
        pw1 = generate_random_password()
        pw2 = generate_random_password()
        assert pw1 != pw2


class TestUserRepositoryDelete:
    """ユーザー削除のテスト。"""

    def test_delete_user(self, user_repo: UserRepository) -> None:
        """ユーザーを削除できること。"""
        user_id = user_repo.create("testuser", "password123")
        result = user_repo.delete(user_id)
        assert result is True
        assert user_repo.find_by_id(user_id) is None

    def test_delete_nonexistent_user(self, user_repo: UserRepository) -> None:
        """存在しないユーザーIDでFalseが返ること。"""
        result = user_repo.delete("nonexistent-id")
        assert result is False

    def test_delete_user_with_auth_sessions(
        self, db_conn: sqlite3.Connection, user_repo: UserRepository
    ) -> None:
        """認証セッションがあるユーザーを削除できること。"""
        user_id = user_repo.create("testuser", "password123")
        # 認証セッションを作成
        db_conn.execute(
            "INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("sess-1", user_id, "token-abc", "2099-01-01T00:00:00", "2026-01-01T00:00:00"),
        )
        db_conn.commit()

        result = user_repo.delete(user_id)
        assert result is True
        assert user_repo.find_by_id(user_id) is None

    def test_delete_user_with_invitation_tokens_created(
        self, db_conn: sqlite3.Connection, user_repo: UserRepository
    ) -> None:
        """招待リンクを作成したユーザーを削除できること。"""
        user_id = user_repo.create("admin1", "password123", role="admin")
        # 招待トークンを作成
        db_conn.execute(
            "INSERT INTO invitation_tokens (id, token, created_by, expires_at, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            ("inv-1", "tok-123", user_id, "2099-01-01T00:00:00", "2026-01-01T00:00:00"),
        )
        db_conn.commit()

        result = user_repo.delete(user_id)
        assert result is True
        assert user_repo.find_by_id(user_id) is None

    def test_delete_user_with_invitation_used_by(
        self, db_conn: sqlite3.Connection, user_repo: UserRepository
    ) -> None:
        """招待リンクを使用したユーザーを削除できること。"""
        admin_id = user_repo.create("admin1", "password123", role="admin")
        user_id = user_repo.create("invited_user", "password123")
        # 招待トークン（adminが作成、user_idが使用）
        db_conn.execute(
            "INSERT INTO invitation_tokens "
            "(id, token, created_by, used_by, expires_at, used_at, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                "inv-1",
                "tok-123",
                admin_id,
                user_id,
                "2099-01-01T00:00:00",
                "2026-01-01T00:00:00",
                "2026-01-01T00:00:00",
            ),
        )
        db_conn.commit()

        result = user_repo.delete(user_id)
        assert result is True
        assert user_repo.find_by_id(user_id) is None
        # 招待トークンのused_byがNULLになっていること
        row = db_conn.execute(
            "SELECT used_by FROM invitation_tokens WHERE id = ?", ("inv-1",)
        ).fetchone()
        assert row["used_by"] is None

    def test_delete_user_count_decreases(self, user_repo: UserRepository) -> None:
        """削除後にカウントが減ること。"""
        user_repo.create("user1", "pw1")
        user_id = user_repo.create("user2", "pw2")
        assert user_repo.count() == 2
        user_repo.delete(user_id)
        assert user_repo.count() == 1


class TestUserRepositoryEdgeCases:
    """エッジケースのテスト。"""

    def test_update_password_returns_false_for_nonexistent_user(
        self, user_repo: UserRepository
    ) -> None:
        """存在しないユーザーIDでFalseが返ること。"""
        result = user_repo.update_password("nonexistent-id", "newpassword")
        assert result is False

    def test_update_api_key_returns_false_for_nonexistent_user(
        self, user_repo: UserRepository
    ) -> None:
        """存在しないユーザーIDでFalseが返ること。"""
        result = user_repo.update_api_key("nonexistent-id", "gemini", "test-key")
        assert result is False

    def test_get_api_key_with_malformed_json_returns_none(
        self, db_conn: sqlite3.Connection, user_repo: UserRepository
    ) -> None:
        """壊れたJSONがDBにある場合にNoneが返ること。"""
        user_id = user_repo.create("testuser", "password123")
        # 直接DBに壊れたJSONを書き込む
        db_conn.execute(
            "UPDATE users SET api_keys_json = ? WHERE id = ?",
            ("{broken json", user_id),
        )
        db_conn.commit()
        assert user_repo.get_api_key(user_id, "gemini") is None

    def test_update_api_key_with_whitespace_only_deletes_key(
        self, user_repo: UserRepository
    ) -> None:
        """空白のみのAPIキーが保存されず削除されること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_api_key(user_id, "gemini", "real-key")
        user_repo.update_api_key(user_id, "gemini", "   ")
        assert user_repo.get_api_key(user_id, "gemini") is None

    def test_create_user_with_sql_injection_attempt(self, user_repo: UserRepository) -> None:
        """SQLインジェクション的な入力がパラメータバインディングで無害化されること。"""
        malicious = "'; DROP TABLE users; --"
        user_repo.create(malicious, "password123")
        user = user_repo.find_by_username(malicious)
        assert user is not None
        assert user.username == malicious
        # usersテーブルが存在し続けることを確認
        assert user_repo.count() >= 1


class TestUserRepositoryUpdateDisplayName:
    """表示名更新のテスト。"""

    def test_update_display_name_success(self, user_repo: UserRepository) -> None:
        """表示名を正常に更新できること。"""
        user_id = user_repo.create("testuser", "password123")
        result = user_repo.update_display_name(user_id, "テスト表示名")
        assert result is True

        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.display_name == "テスト表示名"

    def test_update_display_name_strips_whitespace(self, user_repo: UserRepository) -> None:
        """前後の空白がトリムされること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.update_display_name(user_id, "  表示名  ")

        user = user_repo.find_by_id(user_id)
        assert user is not None
        assert user.display_name == "表示名"

    def test_update_display_name_50_chars_succeeds(self, user_repo: UserRepository) -> None:
        """ちょうど50文字の表示名が成功すること。"""
        user_id = user_repo.create("testuser", "password123")
        name_50 = "あ" * 50
        result = user_repo.update_display_name(user_id, name_50)
        assert result is True

    def test_update_display_name_51_chars_raises_validation_error(
        self, user_repo: UserRepository
    ) -> None:
        """51文字の表示名でValidationErrorが発生すること。"""
        user_id = user_repo.create("testuser", "password123")
        name_51 = "あ" * 51
        with pytest.raises(ValidationError, match="50文字以内"):
            user_repo.update_display_name(user_id, name_51)

    def test_update_display_name_nonexistent_user_returns_false(
        self, user_repo: UserRepository
    ) -> None:
        """存在しないユーザーIDでFalseが返ること。"""
        result = user_repo.update_display_name("nonexistent-id", "名前")
        assert result is False

    def test_update_display_name_updates_timestamp(self, user_repo: UserRepository) -> None:
        """更新時にupdated_atが変更されること。"""
        user_id = user_repo.create("testuser", "password123")
        user_before = user_repo.find_by_id(user_id)

        user_repo.update_display_name(user_id, "新しい名前")
        user_after = user_repo.find_by_id(user_id)

        assert user_before is not None
        assert user_after is not None
        assert user_after.updated_at >= user_before.updated_at


class TestUserRepositoryFindAll:
    """全ユーザー取得のテスト。"""

    def test_find_all_empty(self, user_repo: UserRepository) -> None:
        """ユーザーなしで空リストが返ること。"""
        users = user_repo.find_all()
        assert users == []

    def test_find_all_returns_all_users(self, user_repo: UserRepository) -> None:
        """作成したユーザーが全件返ること。"""
        user_repo.create("user1", "pw1")
        user_repo.create("user2", "pw2")
        user_repo.create("user3", "pw3")
        users = user_repo.find_all()
        assert len(users) == 3

    def test_find_all_ordered_by_created_at_desc(
        self, db_conn: sqlite3.Connection, user_repo: UserRepository
    ) -> None:
        """created_at降順でソートされること。"""
        user_repo.create("first", "pw1")
        user_repo.create("second", "pw2")
        user_repo.create("third", "pw3")
        # タイムスタンプを明示的に設定してソート順を保証
        users = user_repo.find_all()
        db_conn.execute(
            "UPDATE users SET created_at = ? WHERE username = ?",
            ("2026-01-01T00:00:00", "first"),
        )
        db_conn.execute(
            "UPDATE users SET created_at = ? WHERE username = ?",
            ("2026-01-02T00:00:00", "second"),
        )
        db_conn.execute(
            "UPDATE users SET created_at = ? WHERE username = ?",
            ("2026-01-03T00:00:00", "third"),
        )
        db_conn.commit()
        users = user_repo.find_all()
        # 最新のユーザーが先頭
        assert users[0].username == "third"
        assert users[-1].username == "first"
