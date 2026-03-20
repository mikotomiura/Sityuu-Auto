"""設定ページ — APIプロバイダーとモデルの設定。"""

import os

import streamlit as st
from dotenv import load_dotenv

from config import (
    API_KEY_ENV_MAP,
    DEFAULT_API_PROVIDER,
    DEFAULT_MODEL,
    GEMINI_FALLBACK_MODELS,
    PROVIDER_DEFAULT_MODELS,
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SUPPORTED_PROVIDERS,
)

load_dotenv()


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_API_PROVIDER not in st.session_state:
        st.session_state[SESSION_KEY_API_PROVIDER] = DEFAULT_API_PROVIDER
    if SESSION_KEY_API_MODEL not in st.session_state:
        st.session_state[SESSION_KEY_API_MODEL] = DEFAULT_MODEL


def _check_api_key(provider: str) -> bool:
    """指定プロバイダーのAPIキーが環境変数に設定されているか確認する。

    Args:
        provider: APIプロバイダー名。

    Returns:
        APIキーが設定されている場合はTrue。
    """
    env_var = API_KEY_ENV_MAP.get(provider)
    if not env_var:
        return False
    return bool(os.environ.get(env_var))


def main() -> None:
    """設定ページのメイン処理。"""
    _initialize_state()

    st.title("設定")

    # === API プロバイダー設定 ===
    st.header("API設定")

    current_provider: str = st.session_state[SESSION_KEY_API_PROVIDER]
    current_model: str = st.session_state[SESSION_KEY_API_MODEL]

    # --- プロバイダー選択 ---
    provider_index = (
        SUPPORTED_PROVIDERS.index(current_provider)
        if current_provider in SUPPORTED_PROVIDERS
        else 0
    )
    selected_provider = st.selectbox(
        "APIプロバイダー",
        options=SUPPORTED_PROVIDERS,
        index=provider_index,
        format_func=lambda x: {
            "gemini": "Google Gemini",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
        }.get(x, x),
    )

    # プロバイダー変更時にモデルをデフォルトにリセット
    if selected_provider != current_provider:
        st.session_state[SESSION_KEY_API_PROVIDER] = selected_provider
        st.session_state[SESSION_KEY_API_MODEL] = PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
        st.rerun()

    # --- APIキーステータス ---
    has_key = _check_api_key(selected_provider)
    if has_key:
        st.success(f"{selected_provider} のAPIキーが設定されています。")
    else:
        env_var = API_KEY_ENV_MAP.get(selected_provider, "")
        st.warning(f"APIキーが未設定です。`.env` ファイルに `{env_var}` を設定してください。")

    # --- モデル設定 ---
    default_model = PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
    model_input = st.text_input(
        "モデル名",
        value=current_model,
        placeholder=default_model,
        help=f"デフォルト: {default_model}",
    )

    if model_input != current_model:
        st.session_state[SESSION_KEY_API_MODEL] = model_input

    # --- Gemini フォールバック情報 ---
    if selected_provider == "gemini":
        with st.expander("Gemini フォールバックモデル", expanded=False):
            st.caption("利用不可の場合、以下のモデルを順番に試行します:")
            for i, model in enumerate(GEMINI_FALLBACK_MODELS, 1):
                st.text(f"  {i}. {model}")

    # --- 現在の設定サマリ ---
    st.markdown("---")
    st.subheader("現在の設定")

    col1, col2, col3 = st.columns(3)
    col1.metric("プロバイダー", selected_provider)
    col2.metric("モデル", model_input or default_model)
    col3.metric("APIキー", "設定済み" if has_key else "未設定")

    st.caption(
        "APIキーは `.env` ファイルで管理されます。"
        "セキュリティ上、UI上での入力には対応していません。"
    )


main()
