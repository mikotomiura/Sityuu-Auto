# SQLite 開発 — 実装例とベストプラクティス

## DB接続・初期化の実装例

```python
"""データベース接続と初期化。"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = Path("data/fortune.db")
MIGRATIONS_DIR = Path("src/db_service/migrations")


def create_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """SQLite DBへの接続を作成する。

    Args:
        db_path: DBファイルのパス。

    Returns:
        SQLite コネクション。
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # カラム名でアクセス可能にする
    conn.execute("PRAGMA journal_mode=WAL")  # 書き込みパフォーマンス向上
    conn.execute("PRAGMA foreign_keys=ON")   # 外部キー制約を有効化

    logger.info("DB接続を作成: %s", db_path)
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    """マイグレーションを実行してDBを初期化する。

    Args:
        conn: SQLite コネクション。
    """
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    for migration_file in migration_files:
        logger.info("マイグレーション実行: %s", migration_file.name)
        sql = migration_file.read_text(encoding="utf-8")
        conn.executescript(sql)

    conn.commit()
    logger.info("DB初期化完了")
```

---

## マイグレーションファイルの例（001_initial.sql）

```sql
-- 001_initial.sql: 初期スキーマ作成

-- 相談者テーブル
CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    birth_time TEXT,
    gender TEXT,
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 鑑定セッションテーブル
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    client_id TEXT NOT NULL,
    concern TEXT NOT NULL,
    natal_chart_json TEXT NOT NULL,
    sanmei_data_json TEXT,
    ai_reading_text TEXT,
    ai_listening_hints TEXT,
    mentor_notes TEXT,
    api_provider TEXT,
    api_model TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- プロンプトテンプレートテーブル
CREATE TABLE IF NOT EXISTS prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    system_prompt TEXT NOT NULL,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_sessions_client_id ON sessions(client_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name);
```

---

## リポジトリの実装例

```python
"""相談者リポジトリ。"""

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import date, datetime

logger = logging.getLogger(__name__)


@dataclass
class ClientRecord:
    """DB から取得した相談者レコード。"""
    id: str
    name: str
    birth_date: str
    birth_time: str | None
    gender: str | None
    notes: str | None
    created_at: str
    updated_at: str


class ClientRepository:
    """相談者データのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(
        self,
        name: str,
        birth_date: date,
        birth_time: str | None = None,
        gender: str | None = None,
        notes: str | None = None,
    ) -> str:
        """相談者を新規保存する。

        Args:
            name: 名前（仮名可）。
            birth_date: 生年月日。
            birth_time: 出生時間（HH:MM形式）。不明の場合はNone。
            gender: 性別。
            notes: メモ。

        Returns:
            生成されたUUID（文字列）。
        """
        client_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # Good: パラメータバインディングを使用
        self._conn.execute(
            """
            INSERT INTO clients (id, name, birth_date, birth_time, gender, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, name, birth_date.isoformat(), birth_time, gender, notes, now, now),
        )
        self._conn.commit()

        logger.info("相談者を保存: client_id=%s", client_id)
        return client_id

    def find_by_id(self, client_id: str) -> ClientRecord | None:
        """IDで相談者を検索する。

        Args:
            client_id: 相談者のUUID。

        Returns:
            見つかった場合は ClientRecord、見つからない場合は None。
        """
        # Good: パラメータバインディング
        cursor = self._conn.execute(
            "SELECT * FROM clients WHERE id = ?",
            (client_id,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return ClientRecord(
            id=row["id"],
            name=row["name"],
            birth_date=row["birth_date"],
            birth_time=row["birth_time"],
            gender=row["gender"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def find_all(self, limit: int = 50, offset: int = 0) -> list[ClientRecord]:
        """全相談者を取得する（ページネーション付き）。

        Args:
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            ClientRecord のリスト。
        """
        cursor = self._conn.execute(
            "SELECT * FROM clients ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = cursor.fetchall()

        return [
            ClientRecord(
                id=row["id"],
                name=row["name"],
                birth_date=row["birth_date"],
                birth_time=row["birth_time"],
                gender=row["gender"],
                notes=row["notes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def search_by_name(self, query: str) -> list[ClientRecord]:
        """名前で相談者を検索する。

        Args:
            query: 検索文字列（部分一致）。

        Returns:
            マッチした ClientRecord のリスト。
        """
        # Good: LIKE 検索でもパラメータバインディングを使用
        cursor = self._conn.execute(
            "SELECT * FROM clients WHERE name LIKE ? ORDER BY name",
            (f"%{query}%",),
        )
        rows = cursor.fetchall()

        return [
            ClientRecord(
                id=row["id"],
                name=row["name"],
                birth_date=row["birth_date"],
                birth_time=row["birth_time"],
                gender=row["gender"],
                notes=row["notes"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )
            for row in rows
        ]

    def update(
        self,
        client_id: str,
        name: str | None = None,
        notes: str | None = None,
    ) -> bool:
        """相談者情報を更新する。

        Args:
            client_id: 相談者のUUID。
            name: 更新する名前（Noneの場合は変更しない）。
            notes: 更新するメモ（Noneの場合は変更しない）。

        Returns:
            更新成功なら True。
        """
        updates: list[str] = []
        params: list[str] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(client_id)

        sql = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"
        cursor = self._conn.execute(sql, params)
        self._conn.commit()

        updated = cursor.rowcount > 0
        if updated:
            logger.info("相談者を更新: client_id=%s", client_id)
        return updated
```

---

## アンチパターン（避けるべき実装）

```python
# Bad: SQLインジェクション脆弱性
cursor.execute(f"SELECT * FROM clients WHERE name = '{user_input}'")

# Bad: コネクションの未クローズ
conn = sqlite3.connect("data/fortune.db")
cursor = conn.execute("SELECT * FROM clients")
# conn.close() がない

# Bad: 外部キー制約を有効化していない
conn = sqlite3.connect("data/fortune.db")
# PRAGMA foreign_keys=ON を忘れている

# Bad: トランザクション管理の不備
conn.execute("INSERT INTO clients VALUES (...)")
conn.execute("INSERT INTO sessions VALUES (...)")
# commit() がないため、クラッシュ時にデータ不整合
```
