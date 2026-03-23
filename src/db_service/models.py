"""DB層のデータモデル定義。

SQLite から取得したレコードを表現するデータクラスを提供する。
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientRecord:
    """相談者テーブルのレコード。

    Attributes:
        id: UUID 文字列。
        name: 相談者の名前（仮名可）。
        name_kana: フリガナ（カタカナ）。未設定の場合は None。
        birth_date: 生年月日（ISO 8601 形式）。
        birth_time: 出生時間（HH:MM形式）。不明の場合は None。
        gender: 性別。
        notes: メモ。
        created_at: 作成日時（ISO 8601 形式）。
        updated_at: 更新日時（ISO 8601 形式）。
    """

    id: str
    name: str
    name_kana: str | None
    birth_date: str
    birth_time: str | None
    gender: str | None
    notes: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class SessionRecord:
    """鑑定セッションテーブルのレコード。

    Attributes:
        id: UUID 文字列。
        client_id: 相談者の UUID。
        concern: 相談者の悩みテキスト。
        natal_chart_json: 命式データ（JSON 文字列）。
        sanmei_data_json: 算命学データ（JSON 文字列）。
        ai_reading_text: AI 鑑定テキスト。
        ai_listening_hints: 傾聴ヒントテキスト。
        mentor_notes: 出品者メモ。
        api_provider: 使用した API プロバイダー名。
        api_model: 使用したモデル名。
        created_at: 作成日時（ISO 8601 形式）。
        updated_at: 更新日時（ISO 8601 形式）。
    """

    id: str
    client_id: str
    concern: str
    natal_chart_json: str
    sanmei_data_json: str | None
    ai_reading_text: str | None
    ai_listening_hints: str | None
    mentor_notes: str | None
    api_provider: str | None
    api_model: str | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class UserRecord:
    """ユーザーテーブルのレコード。

    Attributes:
        id: UUID 文字列。
        username: ユーザー名（ユニーク）。
        password_hash: bcrypt ハッシュ化されたパスワード。
        api_keys_json: プロバイダー別APIキーのJSON文字列。
        preferred_provider: 優先APIプロバイダー。
        preferred_model: 優先モデル名。
        role: ユーザーロール（"admin" または "user"）。
        created_at: 作成日時（ISO 8601 形式）。
        updated_at: 更新日時（ISO 8601 形式）。
    """

    id: str
    username: str
    password_hash: str
    api_keys_json: str | None
    preferred_provider: str | None
    preferred_model: str | None
    role: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class PromptTemplateRecord:
    """プロンプトテンプレートテーブルのレコード。

    Attributes:
        id: UUID 文字列。
        name: テンプレート名（ユニーク）。
        system_prompt: システムプロンプト本文。
        description: テンプレートの説明。
        is_default: デフォルトテンプレートかどうか。
        created_at: 作成日時（ISO 8601 形式）。
        updated_at: 更新日時（ISO 8601 形式）。
    """

    id: str
    name: str
    system_prompt: str
    description: str | None
    is_default: bool
    created_at: str
    updated_at: str
