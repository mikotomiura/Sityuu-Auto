"""鑑定ページ — 相談者情報の入力から鑑定結果の表示まで。"""

import logging
import os

import streamlit as st
from dotenv import load_dotenv

from ai_service.client import create_client
from ai_service.prompt_builder import build_listening_hint_prompt, build_reading_prompt
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
    SESSION_KEY_LISTENING_HINTS,
)
from fortune_engine import calculate_fortune, format_for_ai_prompt
from fortune_engine.models import FortuneResult
from utils.exceptions import AIServiceConfigError, AIServiceError, FortuneCalculationError

load_dotenv()

logger = logging.getLogger(__name__)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    for key in (SESSION_KEY_FORTUNE_RESULT, SESSION_KEY_AI_RESPONSE, SESSION_KEY_LISTENING_HINTS):
        if key not in st.session_state:
            st.session_state[key] = None


def _get_api_key(provider: str) -> str | None:
    """環境変数からAPIキーを取得する。

    Args:
        provider: APIプロバイダー名。

    Returns:
        APIキー文字列。未設定の場合はNone。
    """
    key_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    env_var = key_map.get(provider)
    if env_var:
        return os.environ.get(env_var)
    return None


def _create_llm_client(provider: str, api_key: str):
    """LLMクライアントを生成する。"""
    return create_client(
        provider=provider,
        api_key=api_key,
        model=DEFAULT_MODEL,
        timeout=API_TIMEOUT_SECONDS,
        fallback_models=GEMINI_FALLBACK_MODELS if provider == "gemini" else None,
    )


def main() -> None:
    """鑑定ページのメイン処理。"""
    _initialize_state()

    st.title("鑑定")

    # --- Step 1: 入力フォーム ---
    client_data = render_client_input_form()

    if client_data is None:
        # 算出済みの結果があれば表示を維持
        result: FortuneResult | None = st.session_state[SESSION_KEY_FORTUNE_RESULT]
        if result is not None:
            render_reading_result(
                result=result,
                ai_text=st.session_state[SESSION_KEY_AI_RESPONSE],
                listening_hints=st.session_state[SESSION_KEY_LISTENING_HINTS],
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
            # 新しい鑑定ではAI結果をリセット
            st.session_state[SESSION_KEY_AI_RESPONSE] = None
            st.session_state[SESSION_KEY_LISTENING_HINTS] = None
    except FortuneCalculationError as e:
        st.error(f"命式の算出に失敗しました: {e}")
        return

    st.success(
        f"命式を算出しました "
        f"（日干: {result.natal_chart.day_stem} / "
        f"天中殺: {result.sanmei_data.tenchusatsu.value}）"
    )

    # --- Step 3: 命式表を表示（プレビュー） ---
    with st.expander("命式プレビュー", expanded=True):
        render_natal_chart(result)

    st.markdown("---")

    # --- Step 4: AI鑑定テキスト生成 ---
    provider = DEFAULT_API_PROVIDER
    api_key = _get_api_key(provider)

    if not api_key:
        st.info(
            "AI鑑定を利用するには `.env` ファイルにAPIキーを設定してください。\n\n"
            f"現在のプロバイダー: `{provider}`"
        )
        # APIなしでも命式結果は表示
        render_reading_result(result=result)
        return

    if st.button("AI鑑定レポートを生成", type="primary", use_container_width=True):
        prompt_text = format_for_ai_prompt(result)
        llm = _create_llm_client(provider, api_key)

        # --- 鑑定レポート生成 ---
        try:
            with st.spinner("AIが鑑定レポートを生成中..."):
                system_prompt, user_prompt = build_reading_prompt(
                    natal_chart_text=prompt_text,
                    concern=client_data.concern,
                )
                ai_text = llm.generate(system_prompt, user_prompt)
                st.session_state[SESSION_KEY_AI_RESPONSE] = ai_text
        except AIServiceConfigError:
            st.error("API設定に問題があります。`.env` ファイルのAPIキーを確認してください。")
            return
        except AIServiceError as e:
            st.error(f"AI鑑定レポートの生成に失敗しました: {e}")
            return

        # --- 傾聴ヒント生成 ---
        try:
            with st.spinner("傾聴ヒントを生成中..."):
                sys_prompt, usr_prompt = build_listening_hint_prompt(
                    natal_chart_text=prompt_text,
                    concern=client_data.concern,
                )
                hints = llm.generate(sys_prompt, usr_prompt)
                st.session_state[SESSION_KEY_LISTENING_HINTS] = hints
        except AIServiceError:
            # 傾聴ヒントはオプショナル — 失敗しても鑑定結果は表示する
            logger.warning("傾聴ヒントの生成に失敗しました")

    # --- Step 5: 鑑定結果の統合表示 ---
    ai_response: str | None = st.session_state[SESSION_KEY_AI_RESPONSE]
    hints_response: str | None = st.session_state[SESSION_KEY_LISTENING_HINTS]

    if ai_response:
        st.markdown("---")
        render_reading_result(
            result=result,
            ai_text=ai_response,
            listening_hints=hints_response,
        )

        # --- 保存ボタン ---
        st.markdown("---")
        if st.button("鑑定結果を保存", use_container_width=True):
            st.success("鑑定結果を保存しました。（DB保存は今後実装予定）")


main()
