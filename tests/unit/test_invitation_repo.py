"""InvitationRepository のユニットテスト。"""

import sqlite3
from datetime import datetime, timedelta

import pytest

from db_service.database import initialize_database
from db_service.repositories.invitation_repo import InvitationRepository
from db_service.repositories.user_repo import UserRepository


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
def invitation_repo(db_conn: sqlite3.Connection) -> InvitationRepository:
    """テスト用 InvitationRepository を返す。"""
    return InvitationRepository(db_conn)


@pytest.fixture()
def admin_user_id(user_repo: UserRepository) -> str:
    """テスト用管理者ユーザーのIDを返す。"""
    return user_repo.create("admin", "admin_password", role="admin")


class TestInvitationCreate:
    """招待トークン作成のテスト。"""

    def test_create_returns_token_string(
        self, invitation_repo: InvitationRepository, admin_user_id: str
    ) -> None:
        """トークン作成が文字列を返すこと。"""
        token = invitation_repo.create(admin_user_id)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_create_tokens_are_unique(
        self, invitation_repo: InvitationRepository, admin_user_id: str
    ) -> None:
        """異なるトークンが生成されること。"""
        token1 = invitation_repo.create(admin_user_id)
        token2 = invitation_repo.create(admin_user_id)
        assert token1 != token2


class TestInvitationFindByToken:
    """トークン検索のテスト。"""

    def test_find_by_token(self, invitation_repo: InvitationRepository, admin_user_id: str) -> None:
        """トークンで招待を検索できること。"""
        token = invitation_repo.create(admin_user_id)
        record = invitation_repo.find_by_token(token)
        assert record is not None
        assert record.token == token
        assert record.created_by == admin_user_id
        assert record.used_by is None

    def test_find_by_token_not_found(self, invitation_repo: InvitationRepository) -> None:
        """存在しないトークンでNoneが返ること。"""
        assert invitation_repo.find_by_token("nonexistent-token") is None


class TestInvitationValidateToken:
    """トークン検証のテスト。"""

    def test_validate_valid_token(
        self, invitation_repo: InvitationRepository, admin_user_id: str
    ) -> None:
        """有効なトークンが検証に通ること。"""
        token = invitation_repo.create(admin_user_id)
        record = invitation_repo.validate_token(token)
        assert record is not None

    def test_validate_used_token_returns_none(
        self,
        invitation_repo: InvitationRepository,
        user_repo: UserRepository,
        admin_user_id: str,
    ) -> None:
        """使用済みトークンが検証に失敗すること。"""
        token = invitation_repo.create(admin_user_id)
        new_user_id = user_repo.create("newuser", "password123")
        invitation_repo.use_token(token, new_user_id)

        assert invitation_repo.validate_token(token) is None

    def test_validate_expired_token_returns_none(
        self,
        invitation_repo: InvitationRepository,
        admin_user_id: str,
        db_conn: sqlite3.Connection,
    ) -> None:
        """有効期限切れトークンが検証に失敗すること。"""
        token = invitation_repo.create(admin_user_id, expiry_hours=1)

        # DBの有効期限を過去に書き換え
        past = (datetime.now() - timedelta(hours=2)).isoformat()
        db_conn.execute(
            "UPDATE invitation_tokens SET expires_at = ? WHERE token = ?",
            (past, token),
        )
        db_conn.commit()

        assert invitation_repo.validate_token(token) is None

    def test_validate_nonexistent_token_returns_none(
        self, invitation_repo: InvitationRepository
    ) -> None:
        """存在しないトークンが検証に失敗すること。"""
        assert invitation_repo.validate_token("nonexistent") is None


class TestInvitationUseToken:
    """トークン使用のテスト。"""

    def test_use_token_success(
        self,
        invitation_repo: InvitationRepository,
        user_repo: UserRepository,
        admin_user_id: str,
    ) -> None:
        """トークンを使用済みにマークできること。"""
        token = invitation_repo.create(admin_user_id)
        new_user_id = user_repo.create("newuser", "password123")

        result = invitation_repo.use_token(token, new_user_id)
        assert result is True

        record = invitation_repo.find_by_token(token)
        assert record is not None
        assert record.used_by == new_user_id
        assert record.used_at is not None

    def test_use_token_already_used(
        self,
        invitation_repo: InvitationRepository,
        user_repo: UserRepository,
        admin_user_id: str,
    ) -> None:
        """使用済みトークンの再使用がFalseを返すこと。"""
        token = invitation_repo.create(admin_user_id)
        user1_id = user_repo.create("user1", "password123")
        user2_id = user_repo.create("user2", "password456")

        invitation_repo.use_token(token, user1_id)
        result = invitation_repo.use_token(token, user2_id)
        assert result is False

    def test_use_nonexistent_token(self, invitation_repo: InvitationRepository) -> None:
        """存在しないトークンの使用がFalseを返すこと。"""
        result = invitation_repo.use_token("nonexistent", "some-user-id")
        assert result is False


class TestInvitationFindAll:
    """全件取得のテスト。"""

    def test_find_all_empty(self, invitation_repo: InvitationRepository) -> None:
        """トークンなしで空リストが返ること。"""
        assert invitation_repo.find_all() == []

    def test_find_all_returns_all(
        self, invitation_repo: InvitationRepository, admin_user_id: str
    ) -> None:
        """全トークンがリストで返ること。"""
        invitation_repo.create(admin_user_id)
        invitation_repo.create(admin_user_id)
        invitation_repo.create(admin_user_id)

        results = invitation_repo.find_all()
        assert len(results) == 3


class TestInvitationDelete:
    """トークン削除のテスト。"""

    def test_delete_success(
        self, invitation_repo: InvitationRepository, admin_user_id: str
    ) -> None:
        """トークンを削除できること。"""
        token = invitation_repo.create(admin_user_id)
        record = invitation_repo.find_by_token(token)
        assert record is not None

        result = invitation_repo.delete(record.id)
        assert result is True
        assert invitation_repo.find_by_token(token) is None

    def test_delete_nonexistent(self, invitation_repo: InvitationRepository) -> None:
        """存在しないIDの削除がFalseを返ること。"""
        result = invitation_repo.delete("nonexistent-id")
        assert result is False


class TestUserRepositoryFindAll:
    """UserRepository.find_all のテスト。"""

    def test_find_all_empty(self, user_repo: UserRepository) -> None:
        """ユーザーなしで空リストが返ること。"""
        assert user_repo.find_all() == []

    def test_find_all_returns_all(self, user_repo: UserRepository) -> None:
        """全ユーザーがリストで返ること。"""
        user_repo.create("user1", "pw1")
        user_repo.create("user2", "pw2")
        results = user_repo.find_all()
        assert len(results) == 2

    def test_find_all_ordered_by_created_at_desc(self, user_repo: UserRepository) -> None:
        """作成日時の降順でソートされていること。"""
        user_repo.create("first", "pw1")
        user_repo.create("second", "pw2")
        results = user_repo.find_all()
        assert results[0].username == "second"
        assert results[1].username == "first"


class TestUserRepositoryDelete:
    """UserRepository.delete のテスト。"""

    def test_delete_user(self, user_repo: UserRepository) -> None:
        """ユーザーを削除できること。"""
        user_id = user_repo.create("testuser", "password123")
        result = user_repo.delete(user_id)
        assert result is True
        assert user_repo.find_by_id(user_id) is None

    def test_delete_nonexistent_user(self, user_repo: UserRepository) -> None:
        """存在しないユーザーの削除がFalseを返ること。"""
        result = user_repo.delete("nonexistent-id")
        assert result is False

    def test_delete_reduces_count(self, user_repo: UserRepository) -> None:
        """ユーザー削除後にカウントが減少すること。"""
        user_id = user_repo.create("testuser", "password123")
        user_repo.create("other_user", "password456")
        assert user_repo.count() == 2

        user_repo.delete(user_id)
        assert user_repo.count() == 1
