"""鑑定セッションリポジトリ。"""

import logging
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime

from db_service.models import SessionRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _row_to_session_record(row: sqlite3.Row) -> SessionRecord:
    """sqlite3.Row を SessionRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された SessionRecord。
    """
    return SessionRecord(
        id=row["id"],
        client_id=row["client_id"],
        concern=row["concern"],
        natal_chart_json=row["natal_chart_json"],
        sanmei_data_json=row["sanmei_data_json"],
        ai_reading_text=row["ai_reading_text"],
        ai_listening_hints=row["ai_listening_hints"],
        mentor_notes=row["mentor_notes"],
        api_provider=row["api_provider"],
        api_model=row["api_model"],
        user_id=row["user_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


@dataclass(frozen=True)
class SessionWithClientName:
    """セッションレコードに相談者名を付加したデータ。

    履歴一覧表示用に、sessions と clients を JOIN した結果を表現する。

    Attributes:
        session: セッションレコード。
        client_name: 相談者の名前。
    """

    session: SessionRecord
    client_name: str


def _row_to_session_with_client_name(row: sqlite3.Row) -> SessionWithClientName:
    """JOIN結果のRowをSessionWithClientNameに変換する。"""
    return SessionWithClientName(
        session=_row_to_session_record(row),
        client_name=row["client_name"],
    )


class SessionRepository:
    """鑑定セッションデータのCRUD操作を提供する。

    Note:
        update / delete メソッドは今後の機能要件（F-010 鑑定履歴詳細、
        mentor_notes の追記等）に応じて追加予定。
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(
        self,
        client_id: str,
        concern: str,
        natal_chart_json: str,
        sanmei_data_json: str | None = None,
        ai_reading_text: str | None = None,
        ai_listening_hints: str | None = None,
        mentor_notes: str | None = None,
        api_provider: str | None = None,
        api_model: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """鑑定セッションを新規保存する。

        Args:
            client_id: 相談者の UUID。
            concern: 相談者の悩みテキスト（個人情報に準じる扱い）。
            natal_chart_json: 命式データ（JSON 文字列）。
            sanmei_data_json: 算命学データ（JSON 文字列）。
            ai_reading_text: AI 鑑定テキスト。
            ai_listening_hints: 傾聴ヒントテキスト。
            mentor_notes: 出品者メモ。
            api_provider: 使用した API プロバイダー名。
            api_model: 使用したモデル名。
            user_id: データ所有者のユーザーID。

        Returns:
            生成された UUID（文字列）。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        try:
            self._conn.execute(
                """
                INSERT INTO sessions
                    (id, client_id, concern, natal_chart_json, sanmei_data_json,
                     ai_reading_text, ai_listening_hints, mentor_notes,
                     api_provider, api_model, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    client_id,
                    concern,
                    natal_chart_json,
                    sanmei_data_json,
                    ai_reading_text,
                    ai_listening_hints,
                    mentor_notes,
                    api_provider,
                    api_model,
                    user_id,
                    now,
                    now,
                ),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("セッションの保存に失敗: %s", e)
            raise DatabaseError("セッションの保存に失敗しました") from e

        logger.info("セッションを保存: session_id=%s, client_id=%s", session_id, client_id)
        return session_id

    def find_by_id(self, session_id: str, user_id: str = "") -> SessionRecord | None:
        """IDでセッションを検索する。

        Args:
            session_id: セッションの UUID。
            user_id: データ所有者のユーザーID。

        Returns:
            見つかった場合は SessionRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM sessions WHERE id = ? AND user_id = ?",
                (session_id, user_id),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("セッションの検索に失敗: %s", e)
            raise DatabaseError("セッションの検索に失敗しました") from e

        if row is None:
            return None

        return _row_to_session_record(row)

    def find_by_client_id(
        self, client_id: str, user_id: str = "", limit: int = 50, offset: int = 0
    ) -> list[SessionRecord]:
        """相談者IDでセッションを検索する。

        Args:
            client_id: 相談者の UUID。
            user_id: データ所有者のユーザーID。
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            SessionRecord のリスト（作成日時の降順）。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM sessions WHERE client_id = ? AND user_id = ?"
                " ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (client_id, user_id, limit, offset),
            )
            return [_row_to_session_record(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("セッションの検索に失敗: %s", e)
            raise DatabaseError("セッションの検索に失敗しました") from e

    def find_all(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> list[SessionRecord]:
        """指定ユーザーのセッションを取得する（ページネーション付き）。

        Args:
            user_id: データ所有者のユーザーID。
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            SessionRecord のリスト（作成日時の降順）。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM sessions WHERE user_id = ?"
                " ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (user_id, limit, offset),
            )
            return [_row_to_session_record(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("セッション一覧の取得に失敗: %s", e)
            raise DatabaseError("セッション一覧の取得に失敗しました") from e

    def count(self, user_id: str) -> int:
        """指定ユーザーのセッション数を取得する。

        Args:
            user_id: データ所有者のユーザーID。

        Returns:
            セッション数。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT COUNT(*) as cnt FROM sessions WHERE user_id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            return row["cnt"] if row else 0
        except sqlite3.Error as e:
            logger.error("セッション数の取得に失敗: %s", e)
            raise DatabaseError("セッション数の取得に失敗しました") from e

    def find_all_with_client_name(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SessionWithClientName]:
        """指定ユーザーのセッションを相談者名付きで取得する。

        sessions と clients を JOIN し、相談者名を含めた一覧を返す。

        Args:
            user_id: データ所有者のユーザーID。
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            SessionWithClientName のリスト（作成日時の降順）。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                """
                SELECT s.*, c.name AS client_name
                FROM sessions s
                JOIN clients c ON s.client_id = c.id
                WHERE s.user_id = ? AND c.user_id = ?
                ORDER BY s.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (user_id, user_id, limit, offset),
            )
            return [_row_to_session_with_client_name(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("セッション一覧（相談者名付き）の取得に失敗: %s", e)
            raise DatabaseError("セッション一覧の取得に失敗しました") from e

    def search_by_client_name(
        self,
        query: str,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[SessionWithClientName]:
        """相談者名でセッションを検索する。

        sessions と clients を JOIN し、名前の部分一致で検索する。

        Args:
            query: 検索文字列（相談者名の部分一致）。
            user_id: データ所有者のユーザーID。
            limit: 取得件数上限。
            offset: オフセット。

        Returns:
            SessionWithClientName のリスト（作成日時の降順）。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                """
                SELECT s.*, c.name AS client_name
                FROM sessions s
                JOIN clients c ON s.client_id = c.id
                WHERE s.user_id = ? AND c.user_id = ? AND c.name LIKE ?
                ORDER BY s.created_at DESC
                LIMIT ? OFFSET ?
                """,
                (user_id, user_id, f"%{query}%", limit, offset),
            )
            return [_row_to_session_with_client_name(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("セッション検索に失敗: %s", e)
            raise DatabaseError("セッションの検索に失敗しました") from e
