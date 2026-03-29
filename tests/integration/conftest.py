"""統合テスト共通フィクスチャ。"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator

import pytest

from db_service.database import initialize_database
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.session_repo import SessionRepository


TEST_USER_ID = "test-user-00000000-0000-0000-0000-000000000001"
"""テスト用のユーザーID。"""

OTHER_USER_ID = "test-user-00000000-0000-0000-0000-000000000002"
"""データ分離テスト用の別ユーザーID。"""


@pytest.fixture()
def db_conn() -> Generator[sqlite3.Connection, None, None]:
    """インメモリSQLiteコネクションを作成し、マイグレーションを実行する。"""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    initialize_database(conn)

    # テスト用ユーザーを事前作成（外部キー制約を満たすため）
    import uuid
    from datetime import datetime

    now = datetime.now().isoformat()
    for uid in (TEST_USER_ID, OTHER_USER_ID):
        conn.execute(
            "INSERT OR IGNORE INTO users (id, username, password_hash, role, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (uid, f"test-{uuid.uuid4().hex[:8]}", "dummy-hash", "user", now, now),
        )
    conn.commit()

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
