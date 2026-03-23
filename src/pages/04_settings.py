"""設定ページ — API設定・プロンプトテンプレート管理・アカウント設定。"""

import json
import logging
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
    SESSION_KEY_TEMPLATE_EDIT_ID,
    SUPPORTED_PROVIDERS,
)
from db_init import get_db_connection
from db_service.models import PromptTemplateRecord
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.user_repo import UserRepository, verify_password
from utils.auth import get_current_user_id
from utils.exceptions import DatabaseError

load_dotenv()

logger = logging.getLogger(__name__)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_API_PROVIDER not in st.session_state:
        st.session_state[SESSION_KEY_API_PROVIDER] = DEFAULT_API_PROVIDER
    if SESSION_KEY_API_MODEL not in st.session_state:
        st.session_state[SESSION_KEY_API_MODEL] = DEFAULT_MODEL
    if SESSION_KEY_TEMPLATE_EDIT_ID not in st.session_state:
        st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = None


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


def _save_user_preferences(provider: str, model: str) -> None:
    """ユーザーのAPI設定をDBに永続化する。

    Args:
        provider: APIプロバイダー名。
        model: モデル名。
    """
    user_id = get_current_user_id()
    if not user_id:
        return
    try:
        conn = get_db_connection()
        user_repo = UserRepository(conn)
        user_repo.update_preferences(user_id, provider, model)
    except DatabaseError:
        logger.warning("ユーザー設定のDB永続化に失敗: user_id=%s", user_id)


def _render_api_settings() -> None:
    """API設定セクションを表示する。"""
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

    # プロバイダー変更時にモデルをデフォルトにリセット＆DBに永続化
    if selected_provider != current_provider:
        new_model = PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
        st.session_state[SESSION_KEY_API_PROVIDER] = selected_provider
        st.session_state[SESSION_KEY_API_MODEL] = new_model
        _save_user_preferences(selected_provider, new_model)
        st.rerun()

    # --- APIキーステータス（ユーザーBYOK + システム） ---
    user_id = get_current_user_id()
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_key = user_repo.get_api_key(user_id, selected_provider) if user_id else None
    has_system_key = _check_api_key(selected_provider)

    if user_key:
        st.success(f"個人APIキーが登録済みです（{selected_provider}）。")
    elif has_system_key:
        st.info(f"システムAPIキーを使用します（{selected_provider}）。")
    else:
        env_var = API_KEY_ENV_MAP.get(selected_provider, "")
        st.warning(
            f"APIキーが未設定です。「アカウント設定」タブで個人キーを登録するか、"
            f"`.env` ファイルに `{env_var}` を設定してください。"
        )

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
        _save_user_preferences(selected_provider, model_input)

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
    key_source = "個人キー" if user_key else ("システム" if has_system_key else "未設定")
    col3.metric("APIキー", key_source)


def _render_account_settings() -> None:
    """アカウント設定セクション（パスワード変更・APIキー管理）を表示する。"""
    user_id = get_current_user_id()
    if not user_id:
        st.error("ログインが必要です。")
        return

    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user = user_repo.find_by_id(user_id)
    if not user:
        st.error("ユーザー情報の取得に失敗しました。")
        return

    # --- パスワード変更 ---
    st.header("パスワードの変更")
    with st.form("change_password_form"):
        current_pw = st.text_input("現在のパスワード", type="password")
        new_pw = st.text_input("新しいパスワード", type="password")
        confirm_pw = st.text_input("新しいパスワード（確認）", type="password")
        pw_submitted = st.form_submit_button("パスワードを変更", use_container_width=True)

        if pw_submitted:
            if not current_pw or not new_pw or not confirm_pw:
                st.error("すべてのフィールドを入力してください。")
            elif not verify_password(current_pw, user.password_hash):
                st.error("現在のパスワードが正しくありません。")
            elif new_pw != confirm_pw:
                st.error("新しいパスワードが一致しません。")
            elif len(new_pw) < 8:
                st.error("パスワードは8文字以上で設定してください。")
            else:
                try:
                    user_repo.update_password(user_id, new_pw)
                    st.success("パスワードを変更しました。")
                except DatabaseError:
                    st.error("パスワードの変更に失敗しました。")

    st.markdown("---")

    # --- APIキー管理（BYOK） ---
    st.header("APIキーの管理（BYOK）")
    st.caption(
        "各プロバイダーのAPIキーを登録すると、システムのAPIキーよりも優先して使用されます。"
        "空欄にして保存するとキーを削除できます。"
    )

    # 現在登録されているキーを取得
    current_keys: dict[str, str] = {}
    if user.api_keys_json:
        try:
            current_keys = json.loads(user.api_keys_json)
        except (json.JSONDecodeError, TypeError):
            current_keys = {}

    provider_labels: dict[str, str] = {
        "gemini": "Google Gemini",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
    }

    for provider in SUPPORTED_PROVIDERS:
        label = provider_labels.get(provider, provider)
        current_value = current_keys.get(provider, "")
        # マスク表示
        display_value = f"****{current_value[-4:]}" if current_value else ""

        with st.form(f"api_key_form_{provider}"):
            st.subheader(label)
            if current_value:
                st.caption(f"登録済み: {display_value}")
            else:
                has_system = _check_api_key(provider)
                if has_system:
                    st.caption("個人キー未登録（システムキーを使用中）")
                else:
                    st.caption("未登録")

            new_key = st.text_input(
                f"{label} APIキー",
                type="password",
                placeholder="新しいAPIキーを入力（空欄で削除）",
                key=f"api_key_input_{provider}",
            )
            key_submitted = st.form_submit_button("保存", use_container_width=True)

            if key_submitted:
                try:
                    user_repo.update_api_key(user_id, provider, new_key)
                    if new_key:
                        st.success(f"{label} のAPIキーを更新しました。")
                    else:
                        st.success(f"{label} のAPIキーを削除しました。")
                    st.rerun()
                except DatabaseError:
                    st.error("APIキーの更新に失敗しました。")


def _render_template_list(repo: PromptTemplateRepository) -> None:
    """テンプレート一覧と操作UIを表示する。

    Args:
        repo: プロンプトテンプレートリポジトリ。
    """
    st.header("プロンプトテンプレート管理")
    st.caption("AI鑑定レポート生成時に使用するシステムプロンプトを管理します。")

    try:
        templates = repo.find_all()
    except DatabaseError:
        st.error("テンプレートの取得に失敗しました。")
        return

    # --- 新規作成フォーム ---
    with st.expander("新しいテンプレートを作成", expanded=False):
        _render_create_form(repo)

    if not templates:
        st.info("テンプレートがまだ登録されていません。")
        return

    # --- テンプレート一覧 ---
    for tmpl in templates:
        default_badge = " (デフォルト)" if tmpl.is_default else ""
        with st.expander(f"{tmpl.name}{default_badge}", expanded=False):
            if tmpl.description:
                st.caption(tmpl.description)

            # 編集モードの判定
            is_editing = st.session_state.get(SESSION_KEY_TEMPLATE_EDIT_ID) == tmpl.id

            if is_editing:
                _render_edit_form(repo, tmpl)
            else:
                st.text_area(
                    "システムプロンプト",
                    value=tmpl.system_prompt,
                    height=150,
                    disabled=True,
                    key=f"view_{tmpl.id}",
                )

                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("編集", key=f"edit_{tmpl.id}", use_container_width=True):
                        st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = tmpl.id
                        st.rerun()
                with col2:
                    if not tmpl.is_default and st.button(
                        "デフォルトに設定",
                        key=f"default_{tmpl.id}",
                        use_container_width=True,
                    ):
                        try:
                            repo.set_default(tmpl.id)
                            st.success(f"「{tmpl.name}」をデフォルトに設定しました。")
                            st.rerun()
                        except DatabaseError:
                            st.error("操作に失敗しました。")
                with col3:
                    if tmpl.is_default:
                        st.button(
                            "削除",
                            key=f"delete_{tmpl.id}",
                            type="secondary",
                            use_container_width=True,
                            disabled=True,
                            help="デフォルトテンプレートは削除できません",
                        )
                    elif st.button(
                        "削除",
                        key=f"delete_{tmpl.id}",
                        type="secondary",
                        use_container_width=True,
                    ):
                        try:
                            repo.delete(tmpl.id)
                            st.success(f"「{tmpl.name}」を削除しました。")
                            st.rerun()
                        except DatabaseError as e:
                            st.error(str(e))

                st.caption(f"作成日: {tmpl.created_at[:10]} / 更新日: {tmpl.updated_at[:10]}")


def _render_create_form(repo: PromptTemplateRepository) -> None:
    """テンプレート新規作成フォームを表示する。

    Args:
        repo: プロンプトテンプレートリポジトリ。
    """
    with st.form("create_template_form"):
        name = st.text_input("テンプレート名", placeholder="例: 恋愛相談向けテンプレート")
        description = st.text_input("説明（任意）", placeholder="このテンプレートの用途")
        system_prompt = st.text_area(
            "システムプロンプト",
            height=200,
            placeholder="あなたは熟練のカウンセラーであり...",
            help="AI に送信されるシステムプロンプトを入力してください。",
        )
        is_default = st.checkbox("デフォルトテンプレートに設定")

        submitted = st.form_submit_button("作成", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("テンプレート名を入力してください。")
            elif not system_prompt.strip():
                st.error("システムプロンプトを入力してください。")
            else:
                try:
                    repo.save(
                        name=name.strip(),
                        system_prompt=system_prompt.strip(),
                        description=description.strip() or None,
                        is_default=is_default,
                    )
                    st.success(f"テンプレート「{name}」を作成しました。")
                    st.rerun()
                except DatabaseError as e:
                    st.error(str(e))


def _render_edit_form(
    repo: PromptTemplateRepository,
    tmpl: PromptTemplateRecord,
) -> None:
    """テンプレート編集フォームを表示する。

    Args:
        repo: プロンプトテンプレートリポジトリ。
        tmpl: 編集対象のテンプレートレコード。
    """
    with st.form(f"edit_form_{tmpl.id}"):
        name = st.text_input("テンプレート名", value=tmpl.name)
        description = st.text_input("説明", value=tmpl.description or "")
        system_prompt = st.text_area(
            "システムプロンプト",
            value=tmpl.system_prompt,
            height=200,
        )

        col_save, col_cancel = st.columns(2)
        with col_save:
            save_clicked = st.form_submit_button("保存", use_container_width=True)
        with col_cancel:
            cancel_clicked = st.form_submit_button("キャンセル", use_container_width=True)

        if save_clicked:
            if not name.strip():
                st.error("テンプレート名を入力してください。")
            elif not system_prompt.strip():
                st.error("システムプロンプトを入力してください。")
            else:
                try:
                    repo.update(
                        template_id=tmpl.id,
                        name=name.strip(),
                        system_prompt=system_prompt.strip(),
                        description=description.strip() or None,
                    )
                    st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = None
                    st.success("テンプレートを更新しました。")
                    st.rerun()
                except DatabaseError as e:
                    st.error(str(e))

        if cancel_clicked:
            st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = None
            st.rerun()


def main() -> None:
    """設定ページのメイン処理。"""
    _initialize_state()

    st.title("設定")

    tab_api, tab_template, tab_account = st.tabs(
        ["API設定", "プロンプトテンプレート", "アカウント設定"]
    )

    with tab_api:
        _render_api_settings()

    with tab_template:
        conn = get_db_connection()
        repo = PromptTemplateRepository(conn)
        _render_template_list(repo)

    with tab_account:
        _render_account_settings()


main()
