"""アプリケーション定数・設定値の定義。"""

from pathlib import Path

# --- session_state キー ---
SESSION_KEY_CLIENT_CURRENT = "current_client"
SESSION_KEY_CLIENT_NAME = "client_name"
SESSION_KEY_CLIENT_NAME_KANA = "client_name_kana"
SESSION_KEY_CLIENT_BIRTH_DATE = "client_birth_date"
SESSION_KEY_CLIENT_BIRTH_TIME = "client_birth_time"
SESSION_KEY_CLIENT_GENDER = "client_gender"
SESSION_KEY_AI_RESPONSE = "ai_response"
SESSION_KEY_FORTUNE_RESULT = "fortune_result"
SESSION_KEY_LISTENING_HINTS = "listening_hints"
SESSION_KEY_SESSION_SAVED = "session_saved"
SESSION_KEY_CONCERN = "concern"
SESSION_KEY_API_PROVIDER = "api_provider"
SESSION_KEY_API_MODEL = "api_model"

# --- 履歴ページ用 ---
SESSION_KEY_HISTORY_SELECTED_SESSION = "history_selected_session"
SESSION_KEY_HISTORY_SEARCH_QUERY = "history_search_query"

# --- 相談者管理ページ用 ---
SESSION_KEY_CLIENTS_SELECTED = "clients_selected_client"
SESSION_KEY_CLIENTS_SEARCH_QUERY = "clients_search_query"
SESSION_KEY_CLIENTS_EDIT_SUCCESS = "client_edit_success"

# --- 認証・ユーザー管理用 ---
SESSION_KEY_AUTH_USER_ID = "auth_user_id"
SESSION_KEY_AUTH_USERNAME = "auth_username"
SESSION_KEY_AUTH_ROLE = "auth_role"
SESSION_KEY_AUTH_DISPLAY_NAME = "auth_display_name"
SESSION_KEY_AUTH_FAIL_COUNT = "auth_fail_count"

# --- パスワードポリシー ---
PASSWORD_MIN_LENGTH = 8

# --- セッション永続化 ---
SESSION_TOKEN_QUERY_PARAM = "_session"
SESSION_TOKEN_EXPIRY_HOURS = 168  # 7日間
SESSION_TOKEN_LENGTH = 32

# --- 招待トークン ---
INVITATION_TOKEN_QUERY_PARAM = "token"
INVITATION_DEFAULT_EXPIRY_HOURS = 72

# --- パスワードリセットトークン ---
RESET_TOKEN_QUERY_PARAM = "reset_token"
RESET_TOKEN_DEFAULT_EXPIRY_HOURS = 24

# --- SMTP（セルフリセット用メール送信） ---
SMTP_HOST_ENV = "SMTP_HOST"
SMTP_PORT_ENV = "SMTP_PORT"
SMTP_USER_ENV = "SMTP_USER"
SMTP_PASSWORD_ENV = "SMTP_PASSWORD"
SMTP_FROM_ENV = "SMTP_FROM"
SMTP_DEFAULT_PORT = 587

# --- プライバシー設定用 ---
SESSION_KEY_PII_ANONYMIZE = "pii_anonymize"

# --- テンプレート管理用 ---
SESSION_KEY_SELECTED_TEMPLATE = "selected_template_id"
SESSION_KEY_TEMPLATE_EDIT_ID = "template_edit_id"
SESSION_KEY_FORM_VERSION = "form_version"

# --- アプリケーション設定 ---
APP_TITLE = "Sityuu-Auto-占い・メンタリング支援システム-"
APP_ICON = "\U0001f52e"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "fortune.sqlite3"

# --- API設定 ---
DEFAULT_API_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash"
API_TIMEOUT_SECONDS = 60
API_MAX_TOKENS = 8192  # 鑑定レポート（5セクション・日本語）の完全出力に必要
API_TEMPERATURE = 0.7
API_MAX_RETRIES = 2
API_RETRY_BASE_WAIT = 1.0

# --- UI表示設定 ---
CONCERN_PREVIEW_LENGTH = 40

# --- プロバイダー別デフォルトモデル ---
PROVIDER_DEFAULT_MODELS: dict[str, str] = {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
}

SUPPORTED_PROVIDERS: list[str] = ["gemini", "openai", "anthropic"]

# --- プロバイダー別APIキー環境変数名 ---
API_KEY_ENV_MAP: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

# --- Gemini フォールバックモデルリスト ---
# 利用可不可が変動するため、順番に試行する
GEMINI_FALLBACK_MODELS: list[str] = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
]
