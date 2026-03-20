"""プロンプトテンプレートリポジトリ。"""

import logging
import sqlite3
import uuid
from datetime import datetime

from db_service.models import PromptTemplateRecord
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _row_to_template_record(row: sqlite3.Row) -> PromptTemplateRecord:
    """sqlite3.Row を PromptTemplateRecord に変換する。"""
    return PromptTemplateRecord(
        id=row["id"],
        name=row["name"],
        system_prompt=row["system_prompt"],
        description=row["description"],
        is_default=row["is_default"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class PromptTemplateRepository:
    """プロンプトテンプレートのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(
        self,
        name: str,
        system_prompt: str,
        description: str | None = None,
        is_default: bool = False,
    ) -> str:
        """テンプレートを新規保存する。

        Args:
            name: テンプレート名（ユニーク）。
            system_prompt: システムプロンプト本文。
            description: テンプレートの説明。
            is_default: デフォルトテンプレートに設定するかどうか。

        Returns:
            生成された UUID（文字列）。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        try:
            if is_default:
                self._clear_default()

            self._conn.execute(
                """
                INSERT INTO prompt_templates
                    (id, name, system_prompt, description, is_default, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (template_id, name, system_prompt, description, int(is_default), now, now),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            logger.error("テンプレート名が重複しています: %s", e)
            raise DatabaseError(f"テンプレート名「{name}」は既に使用されています") from e
        except sqlite3.Error as e:
            logger.error("テンプレートの保存に失敗: %s", e)
            raise DatabaseError("テンプレートの保存に失敗しました") from e

        logger.info("テンプレートを保存: template_id=%s", template_id)
        return template_id

    def find_by_id(self, template_id: str) -> PromptTemplateRecord | None:
        """IDでテンプレートを検索する。

        Args:
            template_id: テンプレートの UUID。

        Returns:
            見つかった場合は PromptTemplateRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM prompt_templates WHERE id = ?",
                (template_id,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("テンプレートの検索に失敗: %s", e)
            raise DatabaseError("テンプレートの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_template_record(row)

    def find_all(self) -> list[PromptTemplateRecord]:
        """全テンプレートを取得する（デフォルト優先、名前順）。

        Returns:
            PromptTemplateRecord のリスト。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM prompt_templates ORDER BY is_default DESC, name ASC"
            )
            return [_row_to_template_record(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error("テンプレート一覧の取得に失敗: %s", e)
            raise DatabaseError("テンプレート一覧の取得に失敗しました") from e

    def find_default(self) -> PromptTemplateRecord | None:
        """デフォルトテンプレートを取得する。

        Returns:
            デフォルトテンプレート。未設定の場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM prompt_templates WHERE is_default = 1 LIMIT 1"
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("デフォルトテンプレートの検索に失敗: %s", e)
            raise DatabaseError("デフォルトテンプレートの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_template_record(row)

    def update(
        self,
        template_id: str,
        name: str | None = None,
        system_prompt: str | None = None,
        description: str | None = None,
    ) -> bool:
        """テンプレートを更新する。

        Args:
            template_id: テンプレートの UUID。
            name: 更新するテンプレート名。
            system_prompt: 更新するシステムプロンプト。
            description: 更新する説明。

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
        if system_prompt is not None:
            updates.append("system_prompt = ?")
            params.append(system_prompt)
        if description is not None:
            updates.append("description = ?")
            params.append(description)

        if not updates:
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(template_id)

        try:
            sql = f"UPDATE prompt_templates SET {', '.join(updates)} WHERE id = ?"
            cursor = self._conn.execute(sql, params)
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            logger.error("テンプレート名が重複しています: %s", e)
            raise DatabaseError("指定したテンプレート名は既に使用されています") from e
        except sqlite3.Error as e:
            logger.error("テンプレートの更新に失敗: %s", e)
            raise DatabaseError("テンプレートの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("テンプレートを更新: template_id=%s", template_id)
        return updated

    def set_default(self, template_id: str) -> bool:
        """指定テンプレートをデフォルトに設定する。

        既存のデフォルト設定を解除してから、指定テンプレートをデフォルトに設定する。

        Args:
            template_id: デフォルトに設定するテンプレートの UUID。

        Returns:
            設定成功なら True。

        Raises:
            DatabaseError: 設定に失敗した場合。
        """
        try:
            self._clear_default()
            cursor = self._conn.execute(
                "UPDATE prompt_templates SET is_default = 1, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), template_id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("デフォルトテンプレートの設定に失敗: %s", e)
            raise DatabaseError("デフォルトテンプレートの設定に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("デフォルトテンプレートを設定: template_id=%s", template_id)
        return updated

    def delete(self, template_id: str) -> bool:
        """テンプレートを削除する。

        Args:
            template_id: 削除するテンプレートの UUID。

        Returns:
            削除成功なら True。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "DELETE FROM prompt_templates WHERE id = ?",
                (template_id,),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("テンプレートの削除に失敗: %s", e)
            raise DatabaseError("テンプレートの削除に失敗しました") from e

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("テンプレートを削除: template_id=%s", template_id)
        return deleted

    def count(self) -> int:
        """テンプレート数を取得する。

        Returns:
            テンプレートの件数。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute("SELECT COUNT(*) FROM prompt_templates")
            row = cursor.fetchone()
            return row[0] if row else 0
        except sqlite3.Error as e:
            logger.error("テンプレート数の取得に失敗: %s", e)
            raise DatabaseError("テンプレート数の取得に失敗しました") from e

    def _clear_default(self) -> None:
        """全テンプレートのデフォルトフラグを解除する。"""
        self._conn.execute(
            "UPDATE prompt_templates SET is_default = 0 WHERE is_default = 1"
        )
