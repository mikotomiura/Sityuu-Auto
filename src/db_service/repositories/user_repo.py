"""ユーザーリポジトリ — 認証・BYOK APIキー管理。"""

import json
import logging
import secrets
import sqlite3
import string
import uuid
from datetime import datetime

import bcrypt

from db_service.models import UserRecord
from utils.exceptions import AuthenticationError, DatabaseError, ValidationError

logger = logging.getLogger(__name__)


def _row_to_user_record(row: sqlite3.Row) -> UserRecord:
    """sqlite3.Row を UserRecord に変換する。

    Args:
        row: SQLiteの行データ。

    Returns:
        変換された UserRecord。
    """
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


def generate_random_password(length: int = 12) -> str:
    """ランダムパスワードを生成する。

    Args:
        length: パスワード文字数。

    Returns:
        英数字で構成されたランダムパスワード文字列。
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def hash_password(password: str) -> str:
    """パスワードを bcrypt でハッシュ化する。

    Args:
        password: 平文パスワード。

    Returns:
        bcrypt ハッシュ文字列。
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """パスワードとハッシュを照合する。

    Args:
        password: 平文パスワード。
        password_hash: bcrypt ハッシュ文字列。

    Returns:
        一致する場合は True。
    """
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


class UserRepository:
    """ユーザーデータのCRUD操作を提供する。"""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def create(
        self,
        username: str,
        password: str,
        role: str = "user",
    ) -> str:
        """ユーザーを新規作成する。

        Args:
            username: ユーザー名（ユニーク）。
            password: 平文パスワード（ハッシュ化して保存）。
            role: ロール（"admin" または "user"）。

        Returns:
            生成された UUID（文字列）。

        Raises:
            DatabaseError: 保存に失敗した場合。
        """
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        pw_hash = hash_password(password)

        try:
            self._conn.execute(
                """
                INSERT INTO users
                    (id, username, password_hash, api_keys_json,
                     preferred_provider, preferred_model, role, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, username, pw_hash, None, None, None, role, now, now),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            logger.error("ユーザー作成失敗（重複）: %s", e)
            raise DatabaseError("ユーザー名が既に使用されています") from e
        except sqlite3.Error as e:
            logger.error("ユーザー作成失敗: %s", e)
            raise DatabaseError("ユーザーの作成に失敗しました") from e

        logger.info("ユーザーを作成: user_id=%s", user_id)
        return user_id

    def authenticate(self, username: str, password: str) -> UserRecord:
        """ユーザー名とパスワードで認証する。

        Args:
            username: ユーザー名。
            password: 平文パスワード。

        Returns:
            認証成功時の UserRecord。

        Raises:
            AuthenticationError: 認証失敗時。
            DatabaseError: DB検索に失敗した場合。
        """
        user = self.find_by_username(username)
        if user is None:
            raise AuthenticationError("ユーザー名またはパスワードが正しくありません")

        if not verify_password(password, user.password_hash):
            raise AuthenticationError("ユーザー名またはパスワードが正しくありません")

        return user

    def find_by_id(self, user_id: str) -> UserRecord | None:
        """IDでユーザーを検索する。

        Args:
            user_id: ユーザーの UUID。

        Returns:
            見つかった場合は UserRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("ユーザー検索失敗: %s", e)
            raise DatabaseError("ユーザーの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_user_record(row)

    def find_by_username(self, username: str) -> UserRecord | None:
        """ユーザー名でユーザーを検索する。

        Args:
            username: ユーザー名。

        Returns:
            見つかった場合は UserRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("ユーザー名検索失敗: %s", e)
            raise DatabaseError("ユーザーの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_user_record(row)

    def find_by_email(self, email: str) -> UserRecord | None:
        """メールアドレスでユーザーを検索する。

        Args:
            email: メールアドレス。

        Returns:
            見つかった場合は UserRecord、見つからない場合は None。

        Raises:
            DatabaseError: 検索に失敗した場合。
        """
        try:
            cursor = self._conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email.strip().lower(),),
            )
            row = cursor.fetchone()
        except sqlite3.Error as e:
            logger.error("メールアドレス検索失敗: %s", e)
            raise DatabaseError("ユーザーの検索に失敗しました") from e

        if row is None:
            return None
        return _row_to_user_record(row)

    def update_email(self, user_id: str, email: str | None) -> bool:
        """メールアドレスを更新する。

        Args:
            user_id: ユーザーの UUID。
            email: メールアドレス。None または空文字で削除。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        normalized = email.strip().lower() if email and email.strip() else None
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                "UPDATE users SET email = ?, updated_at = ? WHERE id = ?",
                (normalized, now, user_id),
            )
            self._conn.commit()
        except sqlite3.IntegrityError as e:
            logger.error("メールアドレス更新失敗（重複）: %s", e)
            raise DatabaseError("このメールアドレスは既に登録されています") from e
        except sqlite3.Error as e:
            logger.error("メールアドレス更新失敗: %s", e)
            raise DatabaseError("メールアドレスの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("メールアドレスを更新: user_id=%s", user_id)
        return updated

    def update_password(self, user_id: str, new_password: str) -> bool:
        """パスワードを更新する。

        Args:
            user_id: ユーザーの UUID。
            new_password: 新しい平文パスワード。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        pw_hash = hash_password(new_password)
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (pw_hash, now, user_id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("パスワード更新失敗: %s", e)
            raise DatabaseError("パスワードの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("パスワードを更新: user_id=%s", user_id)
        return updated

    def update_display_name(self, user_id: str, display_name: str) -> bool:
        """表示名を更新する。

        Args:
            user_id: ユーザーの UUID。
            display_name: 新しい表示名（50文字以内）。

        Returns:
            更新成功なら True。

        Raises:
            ValidationError: 表示名が50文字を超える場合。
            DatabaseError: 更新に失敗した場合。
        """
        if len(display_name.strip()) > 50:
            raise ValidationError("表示名は50文字以内で入力してください")
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                "UPDATE users SET display_name = ?, updated_at = ? WHERE id = ?",
                (display_name.strip(), now, user_id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("表示名更新失敗: %s", e)
            raise DatabaseError("表示名の更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("表示名を更新: user_id=%s", user_id)
        return updated

    def get_api_key(self, user_id: str, provider: str) -> str | None:
        """指定プロバイダーのAPIキーを取得する。

        Args:
            user_id: ユーザーの UUID。
            provider: APIプロバイダー名（"gemini", "openai", "anthropic"）。

        Returns:
            APIキー文字列。未登録の場合は None。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        user = self.find_by_id(user_id)
        if user is None or not user.api_keys_json:
            return None

        try:
            keys: dict[str, str] = json.loads(user.api_keys_json)
        except (json.JSONDecodeError, TypeError):
            return None

        return keys.get(provider)

    def update_api_key(self, user_id: str, provider: str, api_key: str) -> bool:
        """指定プロバイダーのAPIキーを保存・更新する。

        Args:
            user_id: ユーザーの UUID。
            provider: APIプロバイダー名。
            api_key: APIキー文字列。空文字の場合はキーを削除する。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        user = self.find_by_id(user_id)
        if user is None:
            return False

        # 既存のキーをパース
        keys: dict[str, str] = {}
        if user.api_keys_json:
            try:
                keys = json.loads(user.api_keys_json)
            except (json.JSONDecodeError, TypeError):
                keys = {}

        # キーの追加・更新・削除
        stripped_key = api_key.strip()
        if stripped_key:
            keys[provider] = stripped_key
        else:
            keys.pop(provider, None)

        keys_json = json.dumps(keys) if keys else None
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                "UPDATE users SET api_keys_json = ?, updated_at = ? WHERE id = ?",
                (keys_json, now, user_id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("APIキー更新失敗: %s", e)
            raise DatabaseError("APIキーの更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("APIキーを更新: user_id=%s, provider=%s", user_id, provider)
        return updated

    def update_preferences(
        self,
        user_id: str,
        preferred_provider: str | None = None,
        preferred_model: str | None = None,
    ) -> bool:
        """ユーザーのAPI設定（プロバイダー・モデル）を保存する。

        Args:
            user_id: ユーザーの UUID。
            preferred_provider: 優先APIプロバイダー名。
            preferred_model: 優先モデル名。

        Returns:
            更新成功なら True。

        Raises:
            DatabaseError: 更新に失敗した場合。
        """
        now = datetime.now().isoformat()

        try:
            cursor = self._conn.execute(
                """UPDATE users
                   SET preferred_provider = ?, preferred_model = ?, updated_at = ?
                   WHERE id = ?""",
                (preferred_provider, preferred_model, now, user_id),
            )
            self._conn.commit()
        except sqlite3.Error as e:
            logger.error("ユーザー設定の更新失敗: %s", e)
            raise DatabaseError("ユーザー設定の更新に失敗しました") from e

        updated = cursor.rowcount > 0
        if updated:
            logger.info("ユーザー設定を更新: user_id=%s", user_id)
        return updated

    def find_all(self) -> list[UserRecord]:
        """全ユーザーを作成日時の降順で取得する。

        Returns:
            UserRecord のリスト。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute("SELECT * FROM users ORDER BY created_at DESC")
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            logger.error("ユーザー一覧取得失敗: %s", e)
            raise DatabaseError("ユーザー一覧の取得に失敗しました") from e

        return [_row_to_user_record(row) for row in rows]

    def delete(self, user_id: str) -> bool:
        """ユーザーを削除する。

        関連する認証セッションと招待トークンの参照を先に削除・解除してから
        ユーザー本体を削除する。

        Args:
            user_id: 削除するユーザーのUUID。

        Returns:
            削除成功なら True。

        Raises:
            DatabaseError: 削除に失敗した場合。
        """
        try:
            # トランザクション内で関連レコードを削除してからユーザーを削除
            with self._conn:
                self._conn.execute(
                    "DELETE FROM auth_sessions WHERE user_id = ?",
                    (user_id,),
                )
                self._conn.execute(
                    "DELETE FROM password_reset_tokens WHERE user_id = ? OR created_by = ?",
                    (user_id, user_id),
                )
                self._conn.execute(
                    "DELETE FROM invitation_tokens WHERE created_by = ?",
                    (user_id,),
                )
                self._conn.execute(
                    "UPDATE invitation_tokens SET used_by = NULL WHERE used_by = ?",
                    (user_id,),
                )
                cursor = self._conn.execute(
                    "DELETE FROM users WHERE id = ?",
                    (user_id,),
                )
        except sqlite3.Error as e:
            logger.error("ユーザー削除失敗: %s", e)
            raise DatabaseError("ユーザーの削除に失敗しました") from e

        deleted = cursor.rowcount > 0
        if deleted:
            logger.info("ユーザーを削除: user_id=%s", user_id)
        return deleted

    def count(self) -> int:
        """ユーザー数を取得する。

        Returns:
            ユーザー数。

        Raises:
            DatabaseError: 取得に失敗した場合。
        """
        try:
            cursor = self._conn.execute("SELECT COUNT(*) as cnt FROM users")
            row = cursor.fetchone()
            return row["cnt"] if row else 0
        except sqlite3.Error as e:
            logger.error("ユーザー数の取得に失敗: %s", e)
            raise DatabaseError("ユーザー数の取得に失敗しました") from e
