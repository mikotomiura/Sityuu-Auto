"""database モジュールのユニットテスト。"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from db_service.database import (
    _migrate_old_db_file,
    create_connection,
    initialize_database,
)
from utils.exceptions import DatabaseError


class TestCreateConnection:
    """create_connection のテスト。"""

    def test_create_connection_returns_connection(self, tmp_path: Path) -> None:
        """正常なパスで Connection が返ること。"""
        db_path = tmp_path / "test.sqlite3"
        conn = create_connection(db_path)
        try:
            assert isinstance(conn, sqlite3.Connection)
        finally:
            conn.close()

    def test_create_connection_enables_wal_mode(self, tmp_path: Path) -> None:
        """WALモードが有効化されていること。"""
        db_path = tmp_path / "test.sqlite3"
        conn = create_connection(db_path)
        try:
            cursor = conn.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            assert mode == "wal"
        finally:
            conn.close()

    def test_create_connection_enables_foreign_keys(self, tmp_path: Path) -> None:
        """外部キー制約が有効化されていること。"""
        db_path = tmp_path / "test.sqlite3"
        conn = create_connection(db_path)
        try:
            cursor = conn.execute("PRAGMA foreign_keys")
            fk = cursor.fetchone()[0]
            assert fk == 1
        finally:
            conn.close()

    def test_create_connection_creates_parent_directory(self, tmp_path: Path) -> None:
        """親ディレクトリが自動作成されること。"""
        db_path = tmp_path / "subdir" / "nested" / "test.sqlite3"
        assert not db_path.parent.exists()

        conn = create_connection(db_path)
        try:
            assert db_path.parent.exists()
        finally:
            conn.close()

    def test_create_connection_sets_row_factory(self, tmp_path: Path) -> None:
        """row_factory が sqlite3.Row に設定されていること。"""
        db_path = tmp_path / "test.sqlite3"
        conn = create_connection(db_path)
        try:
            assert conn.row_factory is sqlite3.Row
        finally:
            conn.close()

    def test_create_connection_raises_database_error_on_failure(self) -> None:
        """不正パスで DatabaseError が発生すること。"""
        with (
            patch("db_service.database.sqlite3.connect", side_effect=sqlite3.Error("mock error")),
            pytest.raises(DatabaseError, match="DB接続に失敗しました"),
        ):
            create_connection(Path("/tmp/test_db_err.sqlite3"))


class TestMigrateOldDbFile:
    """_migrate_old_db_file のテスト。"""

    def test_renames_old_db_file(self, tmp_path: Path) -> None:
        """旧 .db ファイルが .sqlite3 にリネームされること。"""
        old_file = tmp_path / "fortune.db"
        old_file.write_text("dummy")
        new_path = tmp_path / "fortune.sqlite3"

        _migrate_old_db_file(new_path)

        assert new_path.exists()
        assert not old_file.exists()

    def test_does_not_rename_when_new_file_exists(self, tmp_path: Path) -> None:
        """新ファイルが既に存在する場合はリネームしないこと。"""
        old_file = tmp_path / "fortune.db"
        old_file.write_text("old data")
        new_file = tmp_path / "fortune.sqlite3"
        new_file.write_text("new data")

        _migrate_old_db_file(new_file)

        assert new_file.read_text() == "new data"
        assert old_file.exists()

    def test_does_not_rename_when_old_file_missing(self, tmp_path: Path) -> None:
        """旧ファイルが存在しない場合は何もしないこと。"""
        new_path = tmp_path / "fortune.sqlite3"
        _migrate_old_db_file(new_path)
        assert not new_path.exists()

    def test_skips_non_sqlite3_suffix(self, tmp_path: Path) -> None:
        """拡張子が .sqlite3 でない場合は何もしないこと。"""
        db_path = tmp_path / "fortune.txt"
        _migrate_old_db_file(db_path)

    def test_renames_wal_and_shm_files(self, tmp_path: Path) -> None:
        """WAL/SHMファイルも同時にリネームされること。"""
        old_file = tmp_path / "fortune.db"
        old_file.write_text("dummy")
        wal_file = tmp_path / "fortune.db-wal"
        wal_file.write_text("wal data")
        shm_file = tmp_path / "fortune.db-shm"
        shm_file.write_text("shm data")

        new_path = tmp_path / "fortune.sqlite3"
        _migrate_old_db_file(new_path)

        assert new_path.exists()
        assert not wal_file.exists()
        assert not shm_file.exists()


class TestInitializeDatabase:
    """initialize_database のテスト。"""

    def test_initialize_creates_tables(self) -> None:
        """マイグレーション実行後にテーブルが作成されること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        initialize_database(conn)

        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        assert "clients" in tables
        assert "sessions" in tables
        conn.close()

    def test_initialize_is_idempotent(self) -> None:
        """複数回実行しても安全であること。"""
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        initialize_database(conn)
        initialize_database(conn)  # 2回目もエラーにならない
        conn.close()

    def test_initialize_raises_database_error_on_sql_failure(self) -> None:
        """SQL実行エラーで DatabaseError が発生すること。"""
        conn = MagicMock()
        conn.executescript.side_effect = sqlite3.Error("mock SQL error")

        with pytest.raises(DatabaseError, match="マイグレーション失敗"):
            initialize_database(conn)
