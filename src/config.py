"""アプリケーション設定"""

# --- session_state キー ---
SESSION_KEY_CLIENT_CURRENT = "current_client"
SESSION_KEY_CHART_RESULT = "natal_chart"
SESSION_KEY_AI_RESPONSE = "ai_response"
SESSION_KEY_FORTUNE_RESULT = "fortune_result"
SESSION_KEY_API_PROVIDER = "api_provider"
SESSION_KEY_API_MODEL = "api_model"

# --- アプリケーション設定 ---
APP_TITLE = "Sityuu-Auto-占い・メンタリング支援システム-"
APP_ICON = "\U0001f52e"
DB_PATH = "data/fortune.db"

# --- API設定 ---
DEFAULT_API_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash"
API_TIMEOUT_SECONDS = 30
API_MAX_TOKENS = 2000
API_TEMPERATURE = 0.7

# --- Gemini フォールバックモデルリスト ---
# 利用可不可が変動するため、順番に試行する
GEMINI_FALLBACK_MODELS: list[str] = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
]
