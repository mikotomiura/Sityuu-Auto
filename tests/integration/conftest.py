"""統合テスト共通フィクスチャ。"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator

import pytest

from db_service.database import initialize_database
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository


@pytest.fixture()
def db_conn() -> Generator[sqlite3.Connection, None, None]:
    """インメモリSQLiteコネクションを作成し、マイグレーションを実行する。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    initialize_database(conn)
    yield conn
    conn.close()


@pytest.fixture()
def client_repo(db_conn: sqlite3.Connection) -> ClientRepository:
    """ClientRepository フィクスチャ。"""
    return ClientRepository(db_conn)


@pytest.fixture()
def session_repo(db_conn: sqlite3.Connection) -> SessionRepository:
    """SessionRepository フィクスチャ。"""
    return SessionRepository(db_conn)
