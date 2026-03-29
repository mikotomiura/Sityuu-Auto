"""リポジトリの sqlite3.Error → DatabaseError 変換パスのユニットテスト。"""

from __future__ import annotations

import sqlite3
from unittest.mock import MagicMock

import pytest

from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.session_repo import SessionRepository
from utils.exceptions import DatabaseError


def _make_error_conn() -> MagicMock:
    """execute が sqlite3.Error を送出するモックコネクションを返す。"""
    conn = MagicMock(spec=sqlite3.Connection)
    conn.execute.side_effect = sqlite3.Error("mock error")
    return conn


class TestClientRepositoryErrorPaths:
    """ClientRepository の sqlite3.Error 変換テスト。"""

    def test_save_raises_database_error(self) -> None:
        """save で sqlite3.Error が DatabaseError にラップされること。"""
        from datetime import date

        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.save(name="テスト", birth_date=date(1990, 1, 1), user_id="u1")

    def test_find_by_id_raises_database_error(self) -> None:
        """find_by_id で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_by_id("some-uuid")

    def test_find_all_raises_database_error(self) -> None:
        """find_all で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_all(user_id="u1")

    def test_search_by_name_raises_database_error(self) -> None:
        """search_by_name で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.search_by_name("山田", user_id="u1")

    def test_update_raises_database_error(self) -> None:
        """update で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.update("some-uuid", name="新名前")

    def test_count_raises_database_error(self) -> None:
        """count で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.count(user_id="u1")

    def test_count_sessions_by_client_raises_database_error(self) -> None:
        """count_sessions_by_client で sqlite3.Error が DatabaseError にラップされること。"""
        repo = ClientRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.count_sessions_by_client(user_id="u1")


class TestSessionRepositoryErrorPaths:
    """SessionRepository の sqlite3.Error 変換テスト。"""

    def test_save_raises_database_error(self) -> None:
        """save で sqlite3.Error が DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.save(
                client_id="client-uuid",
                concern="テスト",
                natal_chart_json="{}",
                user_id="u1",
            )

    def test_find_by_id_raises_database_error(self) -> None:
        """find_by_id で sqlite3.Error が DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_by_id("some-uuid")

    def test_find_by_client_id_raises_database_error(self) -> None:
        """find_by_client_id で sqlite3.Error が DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_by_client_id("client-uuid", user_id="u1")

    def test_find_all_raises_database_error(self) -> None:
        """find_all で sqlite3.Error が DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_all(user_id="u1")

    def test_count_raises_database_error(self) -> None:
        """count で sqlite3.Error が DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.count(user_id="u1")

    def test_find_all_with_client_name_raises_database_error(self) -> None:
        """find_all_with_client_name で DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_all_with_client_name(user_id="u1")

    def test_search_by_client_name_raises_database_error(self) -> None:
        """search_by_client_name で DatabaseError にラップされること。"""
        repo = SessionRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.search_by_client_name("山田", user_id="u1")


class TestPromptTemplateRepositoryErrorPaths:
    """PromptTemplateRepository の sqlite3.Error 変換テスト。"""

    def test_save_raises_database_error(self) -> None:
        """save で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.save(name="テンプレート", system_prompt="プロンプト")

    def test_find_by_id_raises_database_error(self) -> None:
        """find_by_id で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_by_id("some-uuid")

    def test_find_all_raises_database_error(self) -> None:
        """find_all で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_all()

    def test_find_default_raises_database_error(self) -> None:
        """find_default で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.find_default()

    def test_update_raises_database_error(self) -> None:
        """update で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.update(template_id="some-uuid", name="新名前")

    def test_set_default_raises_database_error(self) -> None:
        """set_default で sqlite3.Error が DatabaseError にラップされること。"""
        conn = _make_error_conn()
        repo = PromptTemplateRepository(conn)
        with pytest.raises(DatabaseError):
            repo.set_default("some-uuid")

    def test_delete_raises_database_error(self) -> None:
        """delete で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.delete("some-uuid")

    def test_count_raises_database_error(self) -> None:
        """count で sqlite3.Error が DatabaseError にラップされること。"""
        repo = PromptTemplateRepository(_make_error_conn())
        with pytest.raises(DatabaseError):
            repo.count()
