"""相談者リポジトリ。"""

import logging
import sqlite3
import uuid
from datetime import date, datetime
from enum import Enum, auto

from db_service.models import ClientRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class _Unset(Enum):
    """update() で『変更しない』を表すセンチネル値。"""

    TOKEN = auto()


UNSET = _Unset.TOKEN
"""update() のデフォルト値。この値のままなら該当カラムを更新しない。"""


def _row_to_client_record(row: sqlite3.Row) -> ClientRecord:
    """sqlite3.Row を ClientRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された ClientRecord。
    """
    return ClientRecord(
        id=row["id"],
        name=row["name"],
        name_kana=row["name_kana"],
        birth_date=row["birth_date"],
        birth_time=row["birth_time"],
        gender=row["gender"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


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
        name_kana: str | None = None,
        notes: str | None = None,
    ) -> str:
        """相談者を新規保存する。

        Args:
            name: 名前（仮名可）。
            birth_date: 生年月日。
            birth_time: 出生時間（HH:MM形式）。不明の場合は None。
            gender: 性別。
            name_kana: フリガナ（カタカナ）。
            notes: メモ。

        Returns:
            生成された UUID（文字列）。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        client_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        try:
            self._conn.execute(
                """
                INSERT INTO clients
                    (id, name, name_kana, birth_date, birth_time,
                     gender, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client_id,
                    name,
                    name_kana,
                    birth_date.isoformat(),
                    birth_time,
                    gender,
                    notes,
                    now,
                    now,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("相談者の保存に失敗: %s", e)
            raise DatabaseError("相談者の保存に失敗しました") from e

        logger.info("相談者を保存: client_id=%s", client_id)
        return client_id

    def find_by_id(self, client_id: str) -> ClientRecord | None:
        """IDで相談者を検索する。

        Args:
            client_id: 相談者の UUID。

        Returns:
            見つかった場合は ClientRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM clients WHERE id = ?",
                (client_id,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("相談者の検索に失敗: %s", e)
            raise DatabaseError("相談者の検索に失敗しました") from e

        if row is None:
            return None

        return _row_to_client_record(row)

    def find_all(self, limit: int = 50, offset: int = 0) -> list[ClientRecord]:
        """全相談者を取得する（ページネーション付き）。

        Args:
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            ClientRecord のリスト。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM clients ORDER BY updated_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            return [_row_to_client_record(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("相談者一覧の取得に失敗: %s", e)
            raise DatabaseError("相談者一覧の取得に失敗しました") from e

    def count_sessions_by_client(self) -> dict[str, int]:
        """全相談者のセッション数を一括取得する。

        Returns:
            相談者IDをキー、セッション件数を値とする辞書。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT client_id, COUNT(*) as cnt FROM sessions GROUP BY client_id"
            )
            return {row["client_id"]: row["cnt"] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logger.error("セッション数の取得に失敗: %s", e)
            raise DatabaseError("セッション数の取得に失敗しました") from e

    def search_by_name(self, query: str) -> list[ClientRecord]:
        """名前で相談者を検索する。

        Args:
            query: 検索文字列（部分一致）。

        Returns:
            マッチした ClientRecord のリスト。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM clients WHERE name LIKE ? OR name_kana LIKE ? ORDER BY name",
                (f"%{query}%", f"%{query}%"),
            )
            return [_row_to_client_record(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("相談者の名前検索に失敗: %s", e)
            raise DatabaseError("相談者の名前検索に失敗しました") from e

    def update(
        self,
        client_id: str,
        name: str | None = None,
        name_kana: str | None = None,
        notes: str | None = None,
        birth_date: date | None = None,
        birth_time: str | None | _Unset = UNSET,
        gender: str | None | _Unset = UNSET,
    ) -> bool:
        """相談者情報を更新する。

        Args:
            client_id: 相談者の UUID。
            name: 更新する名前（None の場合は変更しない）。
            name_kana: 更新するフリガナ（None の場合は変更しない）。
            notes: 更新するメモ（None の場合は変更しない）。
            birth_date: 更新する生年月日（None の場合は変更しない）。
            birth_time: 更新する出生時間。UNSET で変更しない、None で未設定に戻す。
            gender: 更新する性別。UNSET で変更しない、None で未設定に戻す。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        # updates にはハードコードされたカラム名リテラルのみが追加される。
        # ユーザー入力値はすべて params 経由でバインディングされるため安全。
        updates: list[str] = []
        params: list[str | None] = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if name_kana is not None:
            updates.append("name_kana = ?")
            params.append(name_kana)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        if birth_date is not None:
            updates.append("birth_date = ?")
            params.append(birth_date.isoformat())
        if not isinstance(birth_time, _Unset):
            updates.append("birth_time = ?")
            params.append(birth_time)
        if not isinstance(gender, _Unset):
            updates.append("gender = ?")
            params.append(gender)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(client_id)

        try:
            sql = f"UPDATE clients SET {', '.join(updates)} WHERE id = ?"
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("相談者の更新に失敗: %s", e)
            raise DatabaseError("相談者の更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("相談者を更新: client_id=%s", client_id)
        return updated
