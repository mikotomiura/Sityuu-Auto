"""招待トークンリポジトリ — 招待リンクの生成・検証・管理。"""

import logging
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta

from db_service.models import InvitationTokenRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)

DEFAULT_EXPIRY_HOURS = 72


def _row_to_invitation_record(row: sqlite3.Row) -> InvitationTokenRecord:
    """sqlite3.Row を InvitationTokenRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された InvitationTokenRecord。
    """
    return InvitationTokenRecord(
        id=row["id"],
        token=row["token"],
        created_by=row["created_by"],
        used_by=row["used_by"],
        expires_at=row["expires_at"],
        used_at=row["used_at"],
        created_at=row["created_at"],
    )


class InvitationRepository:
    """招待トークンのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        created_by: str,
        expiry_hours: int = DEFAULT_EXPIRY_HOURS,
    ) -> str:
        """招待トークンを新規作成する。

        Args:
            created_by: トークンを生成する管理者のユーザーID。
            expiry_hours: 有効期限（時間単位）。

        Returns:
            生成されたトークン文字列。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        token_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(32)
        now = datetime.now()
        expires_at = now + timedelta(hours=expiry_hours)

        try:
            self._conn.execute(
                """
                INSERT INTO invitation_tokens
                    (id, token, created_by, used_by, expires_at, used_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token_id,
                    token,
                    created_by,
                    None,
                    expires_at.isoformat(),
                    None,
                    now.isoformat(),
                ),
            )
        except sqlite3.Error as e:
            logger.error("招待トークン作成失敗: %s", e)
            raise DatabaseError("招待トークンの作成に失敗しました") from e

        logger.info("招待トークンを作成: token_id=%s, created_by=%s", token_id, created_by)
        return token

    def find_by_token(self, token: str) -> InvitationTokenRecord | None:
        """トークン文字列で招待を検索する。

        Args:
            token: トークン文字列。

        Returns:
            見つかった場合は InvitationTokenRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM invitation_tokens WHERE token = ?",
                (token,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("招待トークン検索失敗: %s", e)
            raise DatabaseError("招待トークンの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_invitation_record(row)

    def validate_token(self, token: str) -> InvitationTokenRecord | None:
        """トークンが有効（未使用かつ期限内）かを検証する。

        Args:
            token: トークン文字列。

        Returns:
            有効な場合は InvitationTokenRecord、無効の場合は None。
        """
        record = self.find_by_token(token)
        if record is None:
            return None

        # 使用済みチェック
        if record.used_by is not None:
            return None

        # 有効期限チェック
        expires_at = datetime.fromisoformat(record.expires_at)
        if datetime.now() > expires_at:
            return None

        return record

    def use_token(self, token: str, user_id: str) -> bool:
        """トークンを使用済みにマークする。

        Args:
            token: トークン文字列。
            user_id: トークンを使用して登録したユーザーのID。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                """UPDATE invitation_tokens
                   SET used_by = ?, used_at = ?
                   WHERE token = ? AND used_by IS NULL""",
                (user_id, now, token),
            )
        except sqlite3.Error as e:
            logger.error("招待トークン使用済み更新失敗: %s", e)
            raise DatabaseError("招待トークンの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("招待トークンを使用済みに: token=%s..., user_id=%s", token[:8], user_id)
        return updated

    def find_all(self) -> list[InvitationTokenRecord]:
        """全招待トークンを作成日時の降順で取得する。

        Returns:
            InvitationTokenRecord のリスト。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute("SELECT * FROM invitation_tokens ORDER BY created_at DESC")
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error("招待トークン一覧取得失敗: %s", e)
            raise DatabaseError("招待トークンの一覧取得に失敗しました") from e

        return [_row_to_invitation_record(row) for row in rows]

    def delete(self, invitation_id: str) -> bool:
        """招待トークンを削除する。

        Args:
            invitation_id: 招待トークンのUUID。

        Returns:
            削除成功なら True。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM invitation_tokens WHERE id = ?",
                (invitation_id,),
            )
        except sqlite3.Error as e:
            logger.error("招待トークン削除失敗: %s", e)
            raise DatabaseError("招待トークンの削除に失敗しました") from e

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("招待トークンを削除: id=%s", invitation_id)
        return deleted
