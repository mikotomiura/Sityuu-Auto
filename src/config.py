"""アプリケーション定数・設定値の定義。"""

from pathlib import Path

# --- session_state キー ---
SESSION_KEY_CLIENT_CURRENT = "current_client"
SESSION_KEY_CLIENT_NAME = "client_name"
SESSION_KEY_CLIENT_NAME_KANA = "client_name_kana"
SESSION_KEY_CLIENT_BIRTH_DATE = "client_birth_date"
SESSION_KEY_CLIENT_BIRTH_TIME = "client_birth_time"
SESSION_KEY_CLIENT_GENDER = "client_gender"
SESSION_KEY_CHART_RESULT = "natal_chart"
SESSION_KEY_AI_RESPONSE = "ai_response"
SESSION_KEY_FORTUNE_RESULT = "fortune_result"
SESSION_KEY_LISTENING_HINTS = "listening_hints"
SESSION_KEY_CONCERN = "concern"
SESSION_KEY_API_PROVIDER = "api_provider"
SESSION_KEY_API_MODEL = "api_model"

# --- 履歴ページ用 ---
SESSION_KEY_HISTORY_SELECTED_SESSION = "history_selected_session"
SESSION_KEY_HISTORY_SEARCH_QUERY = "history_search_query"

# --- 相談者管理ページ用 ---
SESSION_KEY_CLIENTS_SELECTED = "clients_selected_client"
SESSION_KEY_CLIENTS_SEARCH_QUERY = "clients_search_query"

# --- テンプレート管理用 ---
SESSION_KEY_SELECTED_TEMPLATE = "selected_template_id"
SESSION_KEY_TEMPLATE_EDIT_ID = "template_edit_id"

# --- アプリケーション設定 ---
APP_TITLE = "Sityuu-Auto-占い・メンタリング支援システム-"
APP_ICON = "\U0001f52e"
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "fortune.sqlite3"

# --- API設定 ---
DEFAULT_API_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash"
API_TIMEOUT_SECONDS = 30
API_MAX_TOKENS = 2000
API_TEMPERATURE = 0.7

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
