"""AuthSessionRepository のユニットテスト。"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from db_service.database import initialize_database
from db_service.repositories.auth_session_repo import AuthSessionRepository
from db_service.repositories.user_repo import UserRepository
from utils.exceptions import DatabaseError


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


@pytest.fixture()
def auth_repo(db_conn: sqlite3.Connection) -> AuthSessionRepository:
    """テスト用 AuthSessionRepository を返す。"""
    return AuthSessionRepository(db_conn)


@pytest.fixture()
def sample_user_id(user_repo: UserRepository) -> str:
    """テスト用ユーザーを作成しIDを返す。"""
    return user_repo.create("testuser", "password123")


class TestCreate:
    """セッショントークン作成のテスト。"""

    def test_create_returns_token_string(
        self, auth_repo: AuthSessionRepository, sample_user_id: str
    ) -> None:
        """作成が文字列トークンを返すこと。"""
        token = auth_repo.create(sample_user_id)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_stores_session_in_db(
        self,
        auth_repo: AuthSessionRepository,
        db_conn: sqlite3.Connection,
        sample_user_id: str,
    ) -> None:
        """作成後にDBにセッションが保存されていること。"""
        token = auth_repo.create(sample_user_id)
        row = db_conn.execute(
            "SELECT * FROM auth_sessions WHERE token = ?", (token,)
        ).fetchone()
        assert row is not None
        assert row["user_id"] == sample_user_id

    def test_create_replaces_existing_session(
        self, auth_repo: AuthSessionRepository, db_conn: sqlite3.Connection, sample_user_id: str
    ) -> None:
        """同一ユーザーで再作成すると旧トークンが削除されること。"""
        token1 = auth_repo.create(sample_user_id)
        token2 = auth_repo.create(sample_user_id)

        assert token1 != token2

        # 旧トークンは存在しない
        row_old = db_conn.execute(
            "SELECT * FROM auth_sessions WHERE token = ?", (token1,)
        ).fetchone()
        assert row_old is None

        # 新トークンのみ存在
        row_new = db_conn.execute(
            "SELECT * FROM auth_sessions WHERE token = ?", (token2,)
        ).fetchone()
        assert row_new is not None

    def test_create_sets_expiry_in_future(
        self, auth_repo: AuthSessionRepository, db_conn: sqlite3.Connection, sample_user_id: str
    ) -> None:
        """作成されたセッションの有効期限が未来であること。"""
        token = auth_repo.create(sample_user_id)
        row = db_conn.execute(
            "SELECT expires_at FROM auth_sessions WHERE token = ?", (token,)
        ).fetchone()
        expires_at = datetime.fromisoformat(row["expires_at"])
        assert expires_at > datetime.now()

    def test_create_db_error_raises_database_error(
        self, sample_user_id: str
    ) -> None:
        """DB障害時にDatabaseErrorが発生すること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        # auth_sessions テーブルを作成しない → sqlite3.Error
        repo = AuthSessionRepository(conn)
        with pytest.raises(DatabaseError):
            repo.create(sample_user_id)


class TestValidateToken:
    """トークン検証のテスト。"""

    def test_validate_valid_token_returns_user_record(
        self, auth_repo: AuthSessionRepository, sample_user_id: str
    ) -> None:
        """有効なトークンでUserRecordが返ること。"""
        token = auth_repo.create(sample_user_id)
        user = auth_repo.validate_token(token)
        assert user is not None
        assert user.id == sample_user_id
        assert user.username == "testuser"

    def test_validate_expired_token_returns_none(
        self,
        auth_repo: AuthSessionRepository,
        db_conn: sqlite3.Connection,
        sample_user_id: str,
    ) -> None:
        """期限切れトークンでNoneが返ること。"""
        token = auth_repo.create(sample_user_id)

        # 有効期限を過去に更新
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        db_conn.execute(
            "UPDATE auth_sessions SET expires_at = ? WHERE token = ?",
            (past, token),
        )
        db_conn.commit()

        user = auth_repo.validate_token(token)
        assert user is None

    def test_validate_nonexistent_token_returns_none(
        self, auth_repo: AuthSessionRepository
    ) -> None:
        """存在しないトークンでNoneが返ること。"""
        user = auth_repo.validate_token("nonexistent_token_value")
        assert user is None

    def test_validate_token_returns_user_with_display_name(
        self,
        auth_repo: AuthSessionRepository,
        user_repo: UserRepository,
        sample_user_id: str,
    ) -> None:
        """display_nameが設定されたユーザーの情報が正しく返ること。"""
        user_repo.update_display_name(sample_user_id, "テスト表示名")
        token = auth_repo.create(sample_user_id)
        user = auth_repo.validate_token(token)
        assert user is not None
        assert user.display_name == "テスト表示名"

    def test_validate_db_error_raises_database_error(self) -> None:
        """DB障害時にDatabaseErrorが発生すること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        repo = AuthSessionRepository(conn)
        with pytest.raises(DatabaseError):
            repo.validate_token("any_token")


class TestRevoke:
    """トークン無効化のテスト。"""

    def test_revoke_existing_token_returns_true(
        self, auth_repo: AuthSessionRepository, sample_user_id: str
    ) -> None:
        """存在するトークンの無効化がTrueを返すこと。"""
        token = auth_repo.create(sample_user_id)
        result = auth_repo.revoke(token)
        assert result is True

    def test_revoke_removes_token_from_db(
        self,
        auth_repo: AuthSessionRepository,
        db_conn: sqlite3.Connection,
        sample_user_id: str,
    ) -> None:
        """無効化後にDBからトークンが削除されること。"""
        token = auth_repo.create(sample_user_id)
        auth_repo.revoke(token)
        row = db_conn.execute(
            "SELECT * FROM auth_sessions WHERE token = ?", (token,)
        ).fetchone()
        assert row is None

    def test_revoke_nonexistent_token_returns_false(
        self, auth_repo: AuthSessionRepository
    ) -> None:
        """存在しないトークンの無効化がFalseを返すこと。"""
        result = auth_repo.revoke("nonexistent_token")
        assert result is False

    def test_revoke_db_error_raises_database_error(self) -> None:
        """DB障害時にDatabaseErrorが発生すること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        repo = AuthSessionRepository(conn)
        with pytest.raises(DatabaseError):
            repo.revoke("any_token")


class TestRevokeUser:
    """ユーザー全セッション無効化のテスト。"""

    def test_revoke_user_deletes_all_sessions(
        self,
        auth_repo: AuthSessionRepository,
        db_conn: sqlite3.Connection,
        sample_user_id: str,
    ) -> None:
        """ユーザーの全セッションが削除されること。"""
        # create は旧セッションを削除するので、直接INSERTで複数作成
        for i in range(3):
            db_conn.execute(
                """INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (
                    f"id-{i}",
                    sample_user_id,
                    f"token-{i}",
                    (datetime.now() + timedelta(hours=24)).isoformat(),
                    datetime.now().isoformat(),
                ),
            )
        db_conn.commit()

        count = auth_repo.revoke_user(sample_user_id)
        assert count == 3

        row = db_conn.execute(
            "SELECT COUNT(*) as cnt FROM auth_sessions WHERE user_id = ?",
            (sample_user_id,),
        ).fetchone()
        assert row["cnt"] == 0

    def test_revoke_user_with_no_sessions_returns_zero(
        self, auth_repo: AuthSessionRepository, sample_user_id: str
    ) -> None:
        """セッションがないユーザーで0が返ること。"""
        count = auth_repo.revoke_user(sample_user_id)
        assert count == 0

    def test_revoke_user_db_error_raises_database_error(self) -> None:
        """DB障害時にDatabaseErrorが発生すること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        repo = AuthSessionRepository(conn)
        with pytest.raises(DatabaseError):
            repo.revoke_user("any_user_id")


class TestCleanupExpired:
    """期限切れセッション一括削除のテスト。"""

    def test_cleanup_deletes_only_expired_sessions(
        self,
        auth_repo: AuthSessionRepository,
        db_conn: sqlite3.Connection,
        sample_user_id: str,
    ) -> None:
        """期限切れのみ削除し、有効セッションは残ること。"""
        past = (datetime.now() - timedelta(hours=1)).isoformat()
        future = (datetime.now() + timedelta(hours=24)).isoformat()
        now = datetime.now().isoformat()

        # 期限切れセッション2件
        for i in range(2):
            db_conn.execute(
                """INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)""",
                (f"expired-{i}", sample_user_id, f"expired-token-{i}", past, now),
            )
        # 有効セッション1件
        db_conn.execute(
            """INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at)
            VALUES (?, ?, ?, ?, ?)""",
            ("valid-1", sample_user_id, "valid-token-1", future, now),
        )
        db_conn.commit()

        count = auth_repo.cleanup_expired()
        assert count == 2

        # 有効セッションが残っている
        row = db_conn.execute(
            "SELECT COUNT(*) as cnt FROM auth_sessions WHERE user_id = ?",
            (sample_user_id,),
        ).fetchone()
        assert row["cnt"] == 1

    def test_cleanup_with_no_expired_returns_zero(
        self, auth_repo: AuthSessionRepository
    ) -> None:
        """期限切れがない場合に0が返ること。"""
        count = auth_repo.cleanup_expired()
        assert count == 0

    def test_cleanup_db_error_raises_database_error(self) -> None:
        """DB障害時にDatabaseErrorが発生すること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        repo = AuthSessionRepository(conn)
        with pytest.raises(DatabaseError):
            repo.cleanup_expired()
