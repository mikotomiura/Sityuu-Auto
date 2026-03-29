"""データベース接続と初期化。"""

import logging
import os
import re
import sqlite3
from pathlib import Path

from config import DB_PATH
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
_MIGRATION_FILENAME_PATTERN = re.compile(r"^\d{3}_[\w]+\.sql$")

# SQLite ロック待ち時間（秒）— マルチスレッド環境での書き込み競合に対応
_DB_LOCK_TIMEOUT_SECONDS = 30

# 旧拡張子 .db → .sqlite3 への移行マッピング
_OLD_DB_EXTENSION = ".db"


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

        # 旧拡張子(.db)のファイルが存在し、新ファイルが未作成の場合は自動リネーム
        _migrate_old_db_file(db_path)

        conn = sqlite3.connect(
            str(db_path),
            check_same_thread=False,
            timeout=_DB_LOCK_TIMEOUT_SECONDS,
        )

        # 個人情報を含むDBファイルのパーミッションを所有者のみに制限
        if db_path.exists() and os.name != "nt":
            db_path.chmod(0o600)
        conn.row_factory = sqlite3.Row

        # WALモードを有効化（並行読み取り + 単一書き込みを高速化）
        result = conn.execute("PRAGMA journal_mode=WAL").fetchone()
        if not result:
            logger.warning("PRAGMA journal_mode=WAL の結果を取得できませんでした")
        elif result[0] != "wal":
            logger.warning("WALモード設定失敗: 現在のモード=%s", result[0])

        conn.execute("PRAGMA foreign_keys=ON")
        # busy_timeout: SQLiteエンジンレベルのロック待機（Pythonのtimeoutと二重防御）
        conn.execute("PRAGMA busy_timeout=%d" % (_DB_LOCK_TIMEOUT_SECONDS * 1000))

        logger.info("DB接続を作成: %s", db_path)
        return conn
    except sqlite3.Error as e:
        raise DatabaseError(f"DB接続に失敗しました: {e}") from e


def _migrate_old_db_file(db_path: Path) -> None:
    """旧拡張子(.db)のDBファイルを新拡張子(.sqlite3)にリネームする。

    新ファイルが存在しない場合のみリネームを行う。
    旧ファイルに付随するWAL/SHMファイルも同時にリネームする。

    Args:
        db_path: 新しい拡張子のDBファイルパス。
    """
    if db_path.suffix != ".sqlite3":
        return

    old_path = db_path.with_suffix(_OLD_DB_EXTENSION)
    if not old_path.exists() or db_path.exists():
        return

    logger.info("旧DBファイルを移行: %s → %s", old_path.name, db_path.name)
    old_path.rename(db_path)

    # WAL/SHMファイルも移行
    for ext in (".db-wal", ".db-shm"):
        old_aux = old_path.parent / (old_path.stem + ext)
        if old_aux.exists():
            new_aux = db_path.parent / (db_path.stem + ext.replace(".db", ".sqlite3"))
            old_aux.rename(new_aux)


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
        f for f in MIGRATIONS_DIR.glob("*.sql") if _MIGRATION_FILENAME_PATTERN.match(f.name)
    )

    if not migration_files:
        logger.warning("マイグレーションファイルが見つかりません: %s", MIGRATIONS_DIR)
        return

    for migration_file in migration_files:
        logger.info("マイグレーション実行: %s", migration_file.name)
        try:
            sql = migration_file.read_text(encoding="utf-8")
            conn.executescript(sql)
        except sqlite3.OperationalError as e:
            # ALTER TABLE での「duplicate column」エラーは冪等実行として許容する
            if "duplicate column name" in str(e):
                logger.info("カラム既存のためスキップ: %s (%s)", migration_file.name, e)
            else:
                raise DatabaseError(f"マイグレーション失敗 ({migration_file.name}): {e}") from e
        except sqlite3.Error as e:
            raise DatabaseError(f"マイグレーション失敗 ({migration_file.name}): {e}") from e

    conn.commit()
    logger.info("DB初期化完了")
