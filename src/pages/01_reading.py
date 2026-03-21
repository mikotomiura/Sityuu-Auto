"""鑑定ページ — 相談者情報の入力から鑑定結果の表示まで。"""

import logging
import os

import streamlit as st
from dotenv import load_dotenv

from ai_service.client import LLMClient, create_client
from ai_service.prompt_builder import build_listening_hint_prompt, build_reading_prompt
from components.input_form import render_client_input_form
from components.natal_chart_display import render_natal_chart
from components.reading_result import render_reading_result
from config import (
    API_KEY_ENV_MAP,
    API_TIMEOUT_SECONDS,
    DEFAULT_API_PROVIDER,
    DEFAULT_MODEL,
    GEMINI_FALLBACK_MODELS,
    SESSION_KEY_AI_RESPONSE,
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_CLIENT_BIRTH_DATE,
    SESSION_KEY_CLIENT_BIRTH_TIME,
    SESSION_KEY_CLIENT_GENDER,
    SESSION_KEY_CLIENT_NAME,
    SESSION_KEY_CLIENT_NAME_KANA,
    SESSION_KEY_CONCERN,
    SESSION_KEY_FORM_VERSION,
    SESSION_KEY_FORTUNE_RESULT,
    SESSION_KEY_LISTENING_HINTS,
    SESSION_KEY_SELECTED_TEMPLATE,
)
from db_init import get_db_connection
from db_service.repositories.client_repo import ClientRepository
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.session_repo import SessionRepository
from fortune_engine import calculate_fortune, format_for_ai_prompt
from fortune_engine.models import FortuneResult
from utils.exceptions import (
    AIServiceConfigError,
    AIServiceError,
    DatabaseError,
    FortuneCalculationError,
)

load_dotenv()

logger = logging.getLogger(__name__)


# クリア対象の鑑定セッションキー（SESSION_KEY_FORM_VERSION は含まない: インクリメントで管理）
_READING_STATE_KEYS = (
    SESSION_KEY_FORTUNE_RESULT,
    SESSION_KEY_AI_RESPONSE,
    SESSION_KEY_LISTENING_HINTS,
    SESSION_KEY_CONCERN,
    SESSION_KEY_CLIENT_NAME,
    SESSION_KEY_CLIENT_NAME_KANA,
    SESSION_KEY_CLIENT_BIRTH_DATE,
    SESSION_KEY_CLIENT_BIRTH_TIME,
    SESSION_KEY_CLIENT_GENDER,
)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    for key in _READING_STATE_KEYS:
        if key not in st.session_state:
            st.session_state[key] = None


def _clear_reading_state() -> None:
    """鑑定に関するセッション状態をすべてリセットする。

    カスタムキーの値を None にリセットし、フォームバージョンを
    インクリメントすることで Streamlit ウィジェットの内部状態も
    強制的にリセットする。
    """
    for key in _READING_STATE_KEYS:
        st.session_state[key] = None
    # フォームバージョンをインクリメントしてウィジェットを再生成
    st.session_state[SESSION_KEY_FORM_VERSION] = (
        st.session_state.get(SESSION_KEY_FORM_VERSION, 0) + 1
    )


def _get_api_key(provider: str) -> str | None:
    """環境変数からAPIキーを取得する。

    Args:
        provider: APIプロバイダー名。

    Returns:
        APIキー文字列。未設定の場合はNone。
    """
    env_var = API_KEY_ENV_MAP.get(provider)
    if env_var:
        return os.environ.get(env_var)
    return None


def _create_llm_client(provider: str, api_key: str, model: str) -> LLMClient:
    """LLMクライアントを生成する。

    Args:
        provider: APIプロバイダー名。
        api_key: APIキー文字列。
        model: 使用するモデル名。

    Returns:
        設定済みの LLMClient インスタンス。
    """
    return create_client(
        provider=provider,
        api_key=api_key,
        model=model,
        timeout=API_TIMEOUT_SECONDS,
        fallback_models=GEMINI_FALLBACK_MODELS if provider == "gemini" else None,
    )


def _save_session_to_db(
    result: FortuneResult,
    ai_text: str | None,
    listening_hints: str | None,
) -> None:
    """鑑定結果をDBに保存する。

    相談者をclientsテーブルに、セッションをsessionsテーブルに保存する。

    Args:
        result: 命式算出結果。
        ai_text: AI鑑定テキスト。
        listening_hints: 傾聴ヒントテキスト。
    """
    client_name: str | None = st.session_state.get(SESSION_KEY_CLIENT_NAME)
    client_name_kana: str | None = st.session_state.get(SESSION_KEY_CLIENT_NAME_KANA)
    birth_date_val = st.session_state.get(SESSION_KEY_CLIENT_BIRTH_DATE)
    birth_time_val: str | None = st.session_state.get(SESSION_KEY_CLIENT_BIRTH_TIME)
    gender_val: str | None = st.session_state.get(SESSION_KEY_CLIENT_GENDER)
    concern: str | None = st.session_state.get(SESSION_KEY_CONCERN)

    if not client_name or not birth_date_val or not concern:
        st.error("保存に必要な情報が不足しています。フォームから再度入力してください。")
        return

    try:
        conn = get_db_connection()
        client_repo = ClientRepository(conn)
        session_repo = SessionRepository(conn)

        # 相談者を保存
        client_id = client_repo.save(
            name=client_name,
            birth_date=birth_date_val,
            birth_time=birth_time_val,
            gender=gender_val,
            name_kana=client_name_kana,
        )

        # セッションを保存
        session_repo.save(
            client_id=client_id,
            concern=concern,
            natal_chart_json=result.natal_chart.model_dump_json(),
            sanmei_data_json=result.sanmei_data.model_dump_json(),
            ai_reading_text=ai_text,
            ai_listening_hints=listening_hints,
            api_provider=st.session_state.get(SESSION_KEY_API_PROVIDER, DEFAULT_API_PROVIDER),
            api_model=st.session_state.get(SESSION_KEY_API_MODEL, DEFAULT_MODEL),
        )

        st.success("鑑定結果を保存しました。")
        logger.info("鑑定結果を保存: client_id=%s", client_id)

    except DatabaseError as e:
        logger.error("鑑定結果の保存に失敗: %s", e)
        st.error("保存に失敗しました。しばらくしてから再度お試しください。")


def main() -> None:
    """鑑定ページのメイン処理。"""
    _initialize_state()

    st.title("鑑定")

    # --- 前回の鑑定結果が残っている場合: フォームを非表示にし結果のみ表示 ---
    prev_result = st.session_state.get(SESSION_KEY_FORTUNE_RESULT)
    if prev_result is not None:
        prev_name = st.session_state.get(SESSION_KEY_CLIENT_NAME, "")
        col_info, col_btn = st.columns([3, 1])
        with col_info:
            st.info(f"鑑定結果を表示中: **{prev_name}** さん")
        with col_btn:
            if st.button(
                "新規鑑定を開始", key="new_reading_top", type="primary", use_container_width=True
            ):
                _clear_reading_state()
                st.rerun()
    else:
        # --- Step 1: 入力フォーム（鑑定結果がない場合のみ表示） ---
        client_data = render_client_input_form()

        if client_data is not None:
            # --- Step 2: 命式算出 ---
            try:
                with st.spinner("命式を算出中..."):
                    result = calculate_fortune(
                        birth_date=client_data.birth_date,
                        birth_time=client_data.birth_time,
                    )
                    st.session_state[SESSION_KEY_FORTUNE_RESULT] = result
                    st.session_state[SESSION_KEY_CONCERN] = client_data.concern
                    st.session_state[SESSION_KEY_CLIENT_NAME] = client_data.name
                    st.session_state[SESSION_KEY_CLIENT_NAME_KANA] = client_data.name_kana
                    st.session_state[SESSION_KEY_CLIENT_BIRTH_DATE] = client_data.birth_date
                    st.session_state[SESSION_KEY_CLIENT_BIRTH_TIME] = (
                        client_data.birth_time.strftime("%H:%M") if client_data.birth_time else None
                    )
                    st.session_state[SESSION_KEY_CLIENT_GENDER] = client_data.gender
                    # 新しい鑑定ではAI結果をリセット
                    st.session_state[SESSION_KEY_AI_RESPONSE] = None
                    st.session_state[SESSION_KEY_LISTENING_HINTS] = None
                # 結果表示モードに切り替え（フォームを非表示にする）
                st.rerun()
            except FortuneCalculationError:
                st.error("命式の算出に失敗しました。入力値を確認してください。")
                return

    # --- 算出済み結果の取得 ---
    result: FortuneResult | None = st.session_state[SESSION_KEY_FORTUNE_RESULT]
    if result is None:
        return

    concern: str | None = st.session_state[SESSION_KEY_CONCERN]

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
    provider = st.session_state.get(SESSION_KEY_API_PROVIDER, DEFAULT_API_PROVIDER)
    model = st.session_state.get(SESSION_KEY_API_MODEL, DEFAULT_MODEL)
    api_key = _get_api_key(provider)

    if not api_key:
        st.info(
            "AI鑑定を利用するには `.env` ファイルにAPIキーを設定してください。\n\n"
            f"現在のプロバイダー: `{provider}`"
        )
        # APIなしでも命式結果は表示
        render_reading_result(result=result)
        return

    # --- テンプレート選択 ---
    conn = get_db_connection()
    template_repo = PromptTemplateRepository(conn)
    try:
        templates = template_repo.find_all()
    except DatabaseError:
        templates = []

    custom_system_prompt: str | None = None
    if templates:
        # デフォルトテンプレートのインデックスを検索
        default_idx = 0
        selected_id = st.session_state.get(SESSION_KEY_SELECTED_TEMPLATE)
        for i, t in enumerate(templates):
            if selected_id and t.id == selected_id:
                default_idx = i
                break
            if not selected_id and t.is_default:
                default_idx = i
                break

        selected_template = st.selectbox(
            "プロンプトテンプレート",
            options=templates,
            index=default_idx,
            format_func=lambda t: f"{t.name} (デフォルト)" if t.is_default else t.name,
            help="AI鑑定レポート生成に使用するシステムプロンプトを選択します。",
        )
        if selected_template:
            st.session_state[SESSION_KEY_SELECTED_TEMPLATE] = selected_template.id
            custom_system_prompt = selected_template.system_prompt

    if st.button("AI鑑定レポートを生成", type="primary", use_container_width=True):
        if not concern:
            st.error("悩みテキストが見つかりません。フォームから再度入力してください。")
            return

        prompt_text = format_for_ai_prompt(result)
        llm = _create_llm_client(provider, api_key, model)
        client_name = st.session_state.get(SESSION_KEY_CLIENT_NAME, "")
        client_name_kana = st.session_state.get(SESSION_KEY_CLIENT_NAME_KANA, "")

        # --- 鑑定レポート生成 ---
        try:
            with st.spinner("AIが鑑定レポートを生成中..."):
                system_prompt, user_prompt = build_reading_prompt(
                    natal_chart_text=prompt_text,
                    concern=concern,
                    name=client_name or "",
                    name_kana=client_name_kana or "",
                    custom_system_prompt=custom_system_prompt,
                )
                ai_text = llm.generate(system_prompt, user_prompt)
                st.session_state[SESSION_KEY_AI_RESPONSE] = ai_text
        except AIServiceConfigError:
            st.error("API設定に問題があります。`.env` ファイルのAPIキーを確認してください。")
            return
        except AIServiceError as e:
            logger.error("AI鑑定レポートの生成に失敗: %s", e)
            st.error("AI鑑定レポートの生成に失敗しました。しばらくしてから再度お試しください。")
            return

        # --- 傾聴ヒント生成 ---
        try:
            with st.spinner("傾聴ヒントを生成中..."):
                sys_prompt, usr_prompt = build_listening_hint_prompt(
                    natal_chart_text=prompt_text,
                    concern=concern,
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
            client_name=st.session_state.get(SESSION_KEY_CLIENT_NAME),
        )

        # --- 保存ボタン・新規鑑定ボタン ---
        st.markdown("---")
        col_save, col_new = st.columns(2)
        with col_save:
            if st.button("鑑定結果を保存", use_container_width=True):
                _save_session_to_db(result, ai_response, hints_response)
        with col_new:
            if st.button(
                "新規鑑定を開始",
                key="new_reading_bottom",
                use_container_width=True,
            ):
                _clear_reading_state()
                st.rerun()


main()
