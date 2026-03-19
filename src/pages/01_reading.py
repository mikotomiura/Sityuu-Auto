"""鑑定ページ — 相談者情報の入力から鑑定結果の表示まで。"""

import logging
import os

import streamlit as st
from dotenv import load_dotenv

from ai_service.client import create_client
from ai_service.prompt_builder import build_reading_prompt
from components.input_form import render_client_input_form
from components.natal_chart_display import render_natal_chart
from components.reading_result import render_reading_result
from config import (
    API_TIMEOUT_SECONDS,
    DEFAULT_API_PROVIDER,
    DEFAULT_MODEL,
    GEMINI_FALLBACK_MODELS,
    SESSION_KEY_AI_RESPONSE,
    SESSION_KEY_FORTUNE_RESULT,
)
from fortune_engine import calculate_fortune, format_for_ai_prompt
from fortune_engine.models import FortuneResult
from utils.exceptions import AIServiceConfigError, AIServiceError, FortuneCalculationError

load_dotenv()

logger = logging.getLogger(__name__)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_FORTUNE_RESULT not in st.session_state:
        st.session_state[SESSION_KEY_FORTUNE_RESULT] = None
    if SESSION_KEY_AI_RESPONSE not in st.session_state:
        st.session_state[SESSION_KEY_AI_RESPONSE] = None


def _get_api_key(provider: str) -> str | None:
    """環境変数からAPIキーを取得する。

    Args:
        provider: APIプロバイダー名。

    Returns:
        APIキー文字列。未設定の場合はNone。
    """
    if provider == "openai":
        return os.environ.get("OPENAI_API_KEY")
    if provider == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY")
    if provider == "gemini":
        return os.environ.get("GEMINI_API_KEY")
    return None


def main() -> None:
    """鑑定ページのメイン処理。"""
    _initialize_state()

    st.title("鑑定")
    st.markdown("相談者の情報を入力し、命式を算出します。")

    # --- Step 1: 入力フォーム ---
    client_data = render_client_input_form()

    if client_data is None:
        # 算出済みの結果があれば表示を維持
        result: FortuneResult | None = st.session_state[SESSION_KEY_FORTUNE_RESULT]
        if result is not None:
            render_reading_result(
                result=result,
                ai_text=st.session_state[SESSION_KEY_AI_RESPONSE],
            )
        return

    # --- Step 2: 命式算出 ---
    try:
        with st.spinner("命式を算出中..."):
            result = calculate_fortune(
                birth_date=client_data.birth_date,
                birth_time=client_data.birth_time,
            )
            st.session_state[SESSION_KEY_FORTUNE_RESULT] = result
    except FortuneCalculationError as e:
        st.error(f"命式の算出に失敗しました: {e}")
        return

    # --- Step 3: 命式表を表示 ---
    render_natal_chart(result)

    st.markdown("---")

    # --- Step 4: AI鑑定テキスト生成 ---
    provider = DEFAULT_API_PROVIDER
    api_key = _get_api_key(provider)

    if api_key:
        if st.button("AI鑑定を開始", type="primary"):
            try:
                with st.spinner("AIが鑑定テキストを生成中...（最大30秒）"):
                    prompt_text = format_for_ai_prompt(result)
                    system_prompt, user_prompt = build_reading_prompt(
                        natal_chart_text=prompt_text,
                        concern=client_data.concern,
                    )

                    llm = create_client(
                        provider=provider,
                        api_key=api_key,
                        model=DEFAULT_MODEL,
                        timeout=API_TIMEOUT_SECONDS,
                        fallback_models=GEMINI_FALLBACK_MODELS
                        if provider == "gemini"
                        else None,
                    )
                    ai_text = llm.generate(system_prompt, user_prompt)
                    st.session_state[SESSION_KEY_AI_RESPONSE] = ai_text
            except AIServiceConfigError:
                st.error(
                    "API設定に問題があります。`.env` ファイルのAPIキーを確認してください。"
                )
            except AIServiceError as e:
                st.error(f"AI鑑定テキストの生成に失敗しました: {e}")
    else:
        st.info(
            "AI鑑定を利用するには `.env` ファイルにAPIキーを設定してください。\n\n"
            f"現在のプロバイダー: `{provider}`"
        )

    # --- Step 5: 鑑定結果の統合表示 ---
    ai_response: str | None = st.session_state[SESSION_KEY_AI_RESPONSE]
    if ai_response:
        st.markdown("---")
        render_reading_result(result=result, ai_text=ai_response)

    # --- Step 6: 保存ボタン ---
    st.markdown("---")
    if st.button("鑑定結果を保存"):
        st.success("鑑定結果を保存しました。（DB保存は今後実装予定）")


main()
