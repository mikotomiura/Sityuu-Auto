"""password_reset_repo モジュールのユニットテスト。

PasswordResetRepository のCRUD操作（create, validate_token, use_token,
find_all, delete, cleanup_expired）をテストする。
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pytest

from db_service.models import PasswordResetTokenRecord
from db_service.repositories.password_reset_repo import PasswordResetRepository


@pytest.fixture()
def conn() -> sqlite3.Connection:
    """テスト用インメモリDB接続を作成する。"""
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=OFF")
    connection.executescript(
        """
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            api_keys_json TEXT,
            preferred_provider TEXT,
            preferred_model TEXT,
            role TEXT NOT NULL DEFAULT 'user',
            display_name TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE password_reset_tokens (
            id TEXT PRIMARY KEY,
            token TEXT NOT NULL UNIQUE,
            user_id TEXT NOT NULL,
            created_by TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            created_at TEXT NOT NULL
        );
        INSERT INTO users
            (id, username, password_hash, role, created_at, updated_at)
        VALUES
            ('user-001', 'testuser', '$2b$12$dummy', 'user',
             '2026-01-01T00:00:00', '2026-01-01T00:00:00');
        INSERT INTO users
            (id, username, password_hash, role, created_at, updated_at)
        VALUES
            ('admin-001', 'admin', '$2b$12$dummy', 'admin',
             '2026-01-01T00:00:00', '2026-01-01T00:00:00');
        """
    )
    return connection


@pytest.fixture()
def repo(conn: sqlite3.Connection) -> PasswordResetRepository:
    """テスト用リポジトリを作成する。"""
    return PasswordResetRepository(conn)


class TestCreate:
    """create メソッドのテスト。"""

    def test_create_returns_token_string(self, repo: PasswordResetRepository) -> None:
        """トークン文字列が返されること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_stores_record(
        self, repo: PasswordResetRepository, conn: sqlite3.Connection
    ) -> None:
        """DBにレコードが保存されること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        row = conn.execute(
            "SELECT * FROM password_reset_tokens WHERE token = ?", (token,)
        ).fetchone()
        assert row is not None
        assert row["user_id"] == "user-001"
        assert row["created_by"] == "admin-001"
        assert row["used_at"] is None

    def test_create_invalidates_previous_unused_token(self, repo: PasswordResetRepository) -> None:
        """同一ユーザーの未使用トークンが新規作成時に削除されること。"""
        token1 = repo.create(user_id="user-001", created_by="admin-001")
        token2 = repo.create(user_id="user-001", created_by="admin-001")
        assert token1 != token2
        # 古いトークンは無効化されている
        assert repo.find_by_token(token1) is None
        assert repo.find_by_token(token2) is not None

    def test_create_with_custom_expiry(self, repo: PasswordResetRepository) -> None:
        """カスタム有効期限が設定されること。"""
        token = repo.create(user_id="user-001", created_by="admin-001", expiry_hours=1)
        record = repo.find_by_token(token)
        assert record is not None
        expires_at = datetime.fromisoformat(record.expires_at)
        now = datetime.now()
        # 1時間以内に期限が設定されている
        assert expires_at - now < timedelta(hours=1, minutes=1)


class TestValidateToken:
    """validate_token メソッドのテスト。"""

    def test_validate_valid_token(self, repo: PasswordResetRepository) -> None:
        """有効なトークンが検証を通過すること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        record = repo.validate_token(token)
        assert record is not None
        assert record.user_id == "user-001"

    def test_validate_nonexistent_token(self, repo: PasswordResetRepository) -> None:
        """存在しないトークンは None が返ること。"""
        assert repo.validate_token("nonexistent") is None

    def test_validate_used_token(self, repo: PasswordResetRepository) -> None:
        """使用済みトークンは None が返ること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        repo.use_token(token)
        assert repo.validate_token(token) is None

    def test_validate_expired_token(
        self, repo: PasswordResetRepository, conn: sqlite3.Connection
    ) -> None:
        """期限切れトークンは None が返ること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        # 期限を過去に変更
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        conn.execute(
            "UPDATE password_reset_tokens SET expires_at = ? WHERE token = ?",
            (past, token),
        )
        conn.commit()
        assert repo.validate_token(token) is None


class TestUseToken:
    """use_token メソッドのテスト。"""

    def test_use_token_marks_as_used(self, repo: PasswordResetRepository) -> None:
        """トークンが使用済みにマークされること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        assert repo.use_token(token) is True
        record = repo.find_by_token(token)
        assert record is not None
        assert record.used_at is not None

    def test_use_token_already_used(self, repo: PasswordResetRepository) -> None:
        """既に使用済みのトークンは False が返ること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        repo.use_token(token)
        assert repo.use_token(token) is False

    def test_use_nonexistent_token(self, repo: PasswordResetRepository) -> None:
        """存在しないトークンは False が返ること。"""
        assert repo.use_token("nonexistent") is False


class TestFindAll:
    """find_all メソッドのテスト。"""

    def test_find_all_empty(self, repo: PasswordResetRepository) -> None:
        """レコードがない場合は空リストが返ること。"""
        assert repo.find_all() == []

    def test_find_all_returns_records(self, repo: PasswordResetRepository) -> None:
        """レコードがリストで返ること。"""
        repo.create(user_id="user-001", created_by="admin-001")
        results = repo.find_all()
        assert len(results) == 1
        assert isinstance(results[0], PasswordResetTokenRecord)


class TestDelete:
    """delete メソッドのテスト。"""

    def test_delete_existing(self, repo: PasswordResetRepository) -> None:
        """存在するレコードが削除されること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        record = repo.find_by_token(token)
        assert record is not None
        assert repo.delete(record.id) is True
        assert repo.find_by_token(token) is None

    def test_delete_nonexistent(self, repo: PasswordResetRepository) -> None:
        """存在しないIDの場合は False が返ること。"""
        assert repo.delete("nonexistent-id") is False


class TestCleanupExpired:
    """cleanup_expired メソッドのテスト。"""

    def test_cleanup_removes_expired(
        self, repo: PasswordResetRepository, conn: sqlite3.Connection
    ) -> None:
        """期限切れトークンが削除されること。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        # 期限を過去に変更
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        conn.execute(
            "UPDATE password_reset_tokens SET expires_at = ? WHERE token = ?",
            (past, token),
        )
        conn.commit()
        count = repo.cleanup_expired()
        assert count == 1
        assert repo.find_by_token(token) is None

    def test_cleanup_keeps_valid(self, repo: PasswordResetRepository) -> None:
        """有効なトークンは削除されないこと。"""
        token = repo.create(user_id="user-001", created_by="admin-001")
        count = repo.cleanup_expired()
        assert count == 0
        assert repo.find_by_token(token) is not None
