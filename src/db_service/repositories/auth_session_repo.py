"""認証セッションリポジトリ — セッショントークンの生成・検証・削除。

ブラウザリロード時にログイン状態を復元するためのトークンを管理する。
"""

import logging
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta

from config import SESSION_TOKEN_EXPIRY_HOURS, SESSION_TOKEN_LENGTH
from db_service.models import AuthSessionRecord, UserRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _row_to_auth_session_record(row: sqlite3.Row) -> AuthSessionRecord:
    """sqlite3.Row を AuthSessionRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された AuthSessionRecord。
    """
    return AuthSessionRecord(
        id=row["id"],
        user_id=row["user_id"],
        token=row["token"],
        expires_at=row["expires_at"],
        created_at=row["created_at"],
    )


class AuthSessionRepository:
    """認証セッショントークンのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(self, user_id: str) -> str:
        """セッショントークンを新規作成する。

        同一ユーザーの既存トークンは削除してから新規作成する。

        Args:
            user_id: ユーザーID。

        Returns:
            生成されたトークン文字列。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        session_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(SESSION_TOKEN_LENGTH)
        now = datetime.now()
        expires_at = now + timedelta(hours=SESSION_TOKEN_EXPIRY_HOURS)

        try:
            # 同一ユーザーの既存セッションを削除（1ユーザー1セッション）
            self._conn.execute(
                "DELETE FROM auth_sessions WHERE user_id = ?",
                (user_id,),
            )
            self._conn.execute(
                """
                INSERT INTO auth_sessions (id, user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    user_id,
                    token,
                    expires_at.isoformat(),
                    now.isoformat(),
                ),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("セッショントークン作成失敗: %s", e)
            raise DatabaseError("セッショントークンの作成に失敗しました") from e

        logger.info("セッショントークンを作成: user_id=%s", user_id)
        return token

    def validate_token(self, token: str) -> UserRecord | None:
        """トークンが有効（期限内）かを検証し、対応するユーザー情報を返す。

        Args:
            token: セッショントークン文字列。

        Returns:
            有効な場合は UserRecord、無効の場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                """
                SELECT u.* FROM auth_sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.token = ? AND s.expires_at > ?
                """,
                (token, datetime.now().isoformat()),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("セッショントークン検証失敗: %s", e)
            raise DatabaseError("セッショントークンの検証に失敗しました") from e

        if row is None:
            return None

        return UserRecord(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            api_keys_json=row["api_keys_json"],
            preferred_provider=row["preferred_provider"],
            preferred_model=row["preferred_model"],
            role=row["role"],
            display_name=row["display_name"] if "display_name" in row.keys() else None,  # noqa: SIM118, SIM401
            email=row["email"] if "email" in row.keys() else None,  # noqa: SIM118, SIM401
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def revoke(self, token: str) -> bool:
        """セッショントークンを無効化する。

        Args:
            token: セッショントークン文字列。

        Returns:
            削除成功なら True。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM auth_sessions WHERE token = ?",
                (token,),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("セッショントークン削除失敗: %s", e)
            raise DatabaseError("セッショントークンの削除に失敗しました") from e

        return cursor.rowcount > 0

    def revoke_user(self, user_id: str) -> int:
        """ユーザーの全セッションを無効化する。

        Args:
            user_id: ユーザーID。

        Returns:
            削除された件数。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM auth_sessions WHERE user_id = ?",
                (user_id,),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("ユーザーセッション全削除失敗: %s", e)
            raise DatabaseError("セッションの削除に失敗しました") from e

        return cursor.rowcount

    def cleanup_expired(self) -> int:
        """期限切れセッションを一括削除する。

        Returns:
            削除された件数。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM auth_sessions WHERE expires_at <= ?",
                (datetime.now().isoformat(),),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("期限切れセッション削除失敗: %s", e)
            raise DatabaseError("期限切れセッションの削除に失敗しました") from e

        count = cursor.rowcount
        if count > 0:
            logger.info("期限切れセッションを%d件削除", count)
        return count
