# Streamlit 開発 — 実装例とベストプラクティス

## ページファイルの実装例

```python
"""鑑定ページ — 相談者情報の入力から鑑定結果の表示まで。"""

import streamlit as st

from components.input_form import render_client_input_form
from components.natal_chart_display import render_natal_chart
from components.reading_result import render_reading_result
from config import (
    SESSION_KEY_AI_RESPONSE,
    SESSION_KEY_CHART_RESULT,
    SESSION_KEY_CLIENT_CURRENT,
)
from fortune_engine.calculator import calculate_natal_chart
from ai_service.client import create_client


def _initialize_state() -> None:
    """session_state の初期化。ページ読み込み時に1回実行。"""
    if SESSION_KEY_CLIENT_CURRENT not in st.session_state:
        st.session_state[SESSION_KEY_CLIENT_CURRENT] = None
    if SESSION_KEY_CHART_RESULT not in st.session_state:
        st.session_state[SESSION_KEY_CHART_RESULT] = None
    if SESSION_KEY_AI_RESPONSE not in st.session_state:
        st.session_state[SESSION_KEY_AI_RESPONSE] = None


def main() -> None:
    """鑑定ページのメイン処理。"""
    _initialize_state()

    st.title("鑑定")

    # Step 1: 入力フォーム
    client_data = render_client_input_form()

    if client_data is None:
        return

    # Step 2: 命式算出
    with st.spinner("命式を算出中..."):
        chart = calculate_natal_chart(
            birth_date=client_data.birth_date,
            birth_time=client_data.birth_time,
        )
        st.session_state[SESSION_KEY_CHART_RESULT] = chart

    # Step 3: 命式表示
    render_natal_chart(chart)

    # Step 4: AI鑑定テキスト生成
    if st.button("AI鑑定を開始"):
        with st.spinner("AIが鑑定テキストを生成中...（最大30秒）"):
            llm = create_client(st.session_state.get("api_provider", "anthropic"))
            # ... AI呼び出し処理
            pass

    # Step 5: 結果表示
    if st.session_state[SESSION_KEY_AI_RESPONSE]:
        render_reading_result(
            chart=chart,
            ai_response=st.session_state[SESSION_KEY_AI_RESPONSE],
        )


main()
```

---

## コンポーネントの実装例

```python
"""相談者情報入力フォームコンポーネント。"""

from dataclasses import dataclass
from datetime import date, time

import streamlit as st


@dataclass
class ClientInputData:
    """フォームから取得した入力データ。"""
    name: str
    birth_date: date
    birth_time: time | None
    concern: str


def render_client_input_form() -> ClientInputData | None:
    """相談者情報の入力フォームを表示し、送信された場合にデータを返す。

    Returns:
        フォーム送信時: ClientInputData
        未送信時: None
    """
    with st.form("client_input_form"):
        name = st.text_input(
            "お名前（仮名可）",
            max_chars=50,
            placeholder="例: 山田太郎",
        )

        birth_date = st.date_input(
            "生年月日",
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )

        birth_time_unknown = st.checkbox("出生時間不明")
        birth_time_input = st.time_input(
            "出生時間",
            disabled=birth_time_unknown,
        )

        concern = st.text_area(
            "現在の主な悩み",
            max_chars=2000,
            height=150,
            placeholder="相談したい内容を入力してください（10文字以上）",
        )

        submitted = st.form_submit_button("鑑定開始")

    if not submitted:
        return None

    # バリデーション
    if len(name.strip()) < 1:
        st.warning("お名前を入力してください。")
        return None

    if len(concern.strip()) < 10:
        st.warning("悩みは10文字以上入力してください。")
        return None

    return ClientInputData(
        name=name.strip(),
        birth_date=birth_date,
        birth_time=None if birth_time_unknown else birth_time_input,
        concern=concern.strip(),
    )
```

---

## 設定定数の実装例（config.py）

```python
"""アプリケーション設定。"""

# --- session_state キー ---
SESSION_KEY_CLIENT_CURRENT = "current_client"
SESSION_KEY_CHART_RESULT = "natal_chart"
SESSION_KEY_AI_RESPONSE = "ai_response"
SESSION_KEY_API_PROVIDER = "api_provider"
SESSION_KEY_API_MODEL = "api_model"

# --- アプリケーション設定 ---
APP_TITLE = "占い・メンタリング支援システム"
APP_ICON = "🔮"
DB_PATH = "data/fortune.db"

# --- API設定 ---
DEFAULT_API_PROVIDER = "anthropic"
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
API_TIMEOUT_SECONDS = 30
API_MAX_TOKENS = 2000
API_TEMPERATURE = 0.7
```

---

## キャッシュの使用例

```python
import streamlit as st
from datetime import date, time

from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.models import NatalChart


# Good: 同じ引数に対する再計算を防ぐ
@st.cache_data
def cached_calculate_chart(birth_date: date, birth_time: time | None) -> NatalChart:
    """命式算出結果をキャッシュする。"""
    return calculate_natal_chart(birth_date, birth_time)


# Good: DB接続をシングルトンとして管理
@st.cache_resource
def get_db_connection():
    """DBコネクションを取得（アプリ起動中1回のみ生成）。"""
    from db_service.database import create_connection
    return create_connection()
```

---

## アンチパターン（避けるべき実装）

```python
# Bad: ページファイルにビジネスロジックを直接記述
# → fortune_engine/ に切り出すこと
def page():
    birth_date = st.date_input("生年月日")
    if st.button("算出"):
        solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
        lunar = solar.getLunar()
        eight_char = lunar.getEightChar()
        # ... 長いロジックがページに直書きされている

# Bad: session_state キーのハードコード
# → config.py に定数として定義すること
st.session_state["chart"] = chart  # キーが散在し管理困難

# Bad: エラーハンドリングなしのAPI呼び出し
# → try/except で適切にハンドリングすること
response = openai.chat.completions.create(...)  # タイムアウトもエラーも未処理
```
