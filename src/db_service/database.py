"""データベース接続と初期化。"""

import logging
import os
import re
import sqlite3
from pathlib import Path

from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "fortune.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
_MIGRATION_FILENAME_PATTERN = re.compile(r"^\d{3}_[\w]+\.sql$")


def create_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """SQLite DBへの接続を作成する。

    親ディレクトリが存在しない場合は自動作成する。
    WALモードと外部キー制約を有効化する。

    Args:
        db_path: DBファイルのパス。

    Returns:
        SQLite コネクション。

    Raises:
        DatabaseError: DB接続に失敗した場合。
    """
    try:
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(db_path), check_same_thread=False)

        # 個人情報を含むDBファイルのパーミッションを所有者のみに制限
        if db_path.exists() and os.name != "nt":
            db_path.chmod(0o600)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

        logger.info("DB接続を作成: %s", db_path)
        return conn
    except sqlite3.Error as e:
        raise DatabaseError(f"DB接続に失敗しました: {e}") from e


def initialize_database(conn: sqlite3.Connection) -> None:
    """マイグレーションを実行してDBを初期化する。

    ``migrations/`` ディレクトリ内のSQLファイルをファイル名順に実行する。
    各マイグレーションは冪等（IF NOT EXISTS）であるため、
    繰り返し実行しても安全。

    Args:
        conn: SQLite コネクション。

    Raises:
        DatabaseError: マイグレーション実行に失敗した場合。
    """
    migration_files = sorted(
        f for f in MIGRATIONS_DIR.glob("*.sql")
        if _MIGRATION_FILENAME_PATTERN.match(f.name)
    )

    if not migration_files:
        logger.warning("マイグレーションファイルが見つかりません: %s", MIGRATIONS_DIR)
        return

    for migration_file in migration_files:
        logger.info("マイグレーション実行: %s", migration_file.name)
        try:
            sql = migration_file.read_text(encoding="utf-8")
            conn.executescript(sql)
        except sqlite3.Error as e:
            raise DatabaseError(
                f"マイグレーション失敗 ({migration_file.name}): {e}"
            ) from e

    conn.commit()
    logger.info("DB初期化完了")
