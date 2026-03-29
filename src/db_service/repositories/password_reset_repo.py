"""パスワードリセットトークンリポジトリ — リセットリンクの生成・検証・管理。"""

import logging
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta

from config import RESET_TOKEN_DEFAULT_EXPIRY_HOURS
from db_service.models import PasswordResetTokenRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _row_to_reset_record(row: sqlite3.Row) -> PasswordResetTokenRecord:
    """sqlite3.Row を PasswordResetTokenRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された PasswordResetTokenRecord。
    """
    return PasswordResetTokenRecord(
        id=row["id"],
        token=row["token"],
        user_id=row["user_id"],
        created_by=row["created_by"],
        expires_at=row["expires_at"],
        used_at=row["used_at"],
        created_at=row["created_at"],
    )


class PasswordResetRepository:
    """パスワードリセットトークンのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        user_id: str,
        created_by: str,
        expiry_hours: int = RESET_TOKEN_DEFAULT_EXPIRY_HOURS,
    ) -> str:
        """パスワードリセットトークンを新規作成する。

        同一ユーザーの未使用トークンは無効化（削除）してから新規生成する。

        Args:
            user_id: リセット対象のユーザーID。
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
            # 同一ユーザーの未使用トークンを削除（1ユーザー1トークンに制限）
            self._conn.execute(
                "DELETE FROM password_reset_tokens WHERE user_id = ? AND used_at IS NULL",
                (user_id,),
            )
            self._conn.execute(
                """
                INSERT INTO password_reset_tokens
                    (id, token, user_id, created_by, expires_at, used_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    token_id,
                    token,
                    user_id,
                    created_by,
                    expires_at.isoformat(),
                    None,
                    now.isoformat(),
                ),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("パスワードリセットトークン作成失敗: %s", e)
            raise DatabaseError("パスワードリセットトークンの作成に失敗しました") from e

        logger.info(
            "パスワードリセットトークンを作成: token_id=%s, user_id=%s",
            token_id,
            user_id,
        )
        return token

    def find_by_token(self, token: str) -> PasswordResetTokenRecord | None:
        """トークン文字列でリセットトークンを検索する。

        Args:
            token: トークン文字列。

        Returns:
            見つかった場合は PasswordResetTokenRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM password_reset_tokens WHERE token = ?",
                (token,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("パスワードリセットトークン検索失敗: %s", e)
            raise DatabaseError("パスワードリセットトークンの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_reset_record(row)

    def validate_token(self, token: str) -> PasswordResetTokenRecord | None:
        """トークンが有効（未使用かつ期限内）かを検証する。

        Args:
            token: トークン文字列。

        Returns:
            有効な場合は PasswordResetTokenRecord、無効の場合は None。
        """
        record = self.find_by_token(token)
        if record is None:
            return None

        # 使用済みチェック
        if record.used_at is not None:
            return None

        # 有効期限チェック
        expires_at = datetime.fromisoformat(record.expires_at)
        if datetime.now() > expires_at:
            return None

        return record

    def use_token(self, token: str) -> bool:
        """トークンを使用済みにマークする。

        Args:
            token: トークン文字列。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                """UPDATE password_reset_tokens
                   SET used_at = ?
                   WHERE token = ? AND used_at IS NULL""",
                (now, token),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("パスワードリセットトークン使用済み更新失敗: %s", e)
            raise DatabaseError("パスワードリセットトークンの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("パスワードリセットトークンを使用済みに: token=%s...", token[:8])
        return updated

    def find_all(self) -> list[PasswordResetTokenRecord]:
        """全パスワードリセットトークンを作成日時の降順で取得する。

        Returns:
            PasswordResetTokenRecord のリスト。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM password_reset_tokens ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error("パスワードリセットトークン一覧取得失敗: %s", e)
            raise DatabaseError("パスワードリセットトークンの一覧取得に失敗しました") from e

        return [_row_to_reset_record(row) for row in rows]

    def delete(self, reset_id: str) -> bool:
        """パスワードリセットトークンを削除する。

        Args:
            reset_id: リセットトークンのUUID。

        Returns:
            削除成功なら True。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM password_reset_tokens WHERE id = ?",
                (reset_id,),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("パスワードリセットトークン削除失敗: %s", e)
            raise DatabaseError("パスワードリセットトークンの削除に失敗しました") from e

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("パスワードリセットトークンを削除: id=%s", reset_id)
        return deleted

    def cleanup_expired(self) -> int:
        """期限切れのリセットトークンを一括削除する。

        Returns:
            削除されたレコード数。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                "DELETE FROM password_reset_tokens WHERE expires_at < ?",
                (now,),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("期限切れリセットトークン削除失敗: %s", e)
            raise DatabaseError("期限切れトークンの削除に失敗しました") from e

        count = cursor.rowcount
        if count > 0:
            logger.info("期限切れリセットトークンを削除: %d件", count)
        return count
