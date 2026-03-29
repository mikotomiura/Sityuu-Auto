"""設定ページ — API設定・プロンプトテンプレート管理・アカウント設定。"""

import html
import json
import logging
import os

import streamlit as st

from config import (
    API_KEY_ENV_MAP,
    DEFAULT_API_PROVIDER,
    DEFAULT_MODEL,
    GEMINI_FALLBACK_MODELS,
    PASSWORD_MIN_LENGTH,
    PROVIDER_DEFAULT_MODELS,
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_AUTH_DISPLAY_NAME,
    SESSION_KEY_PII_ANONYMIZE,
    SESSION_KEY_TEMPLATE_EDIT_ID,
    SUPPORTED_PROVIDERS,
)
from db_init import get_db_connection
from db_service.models import PromptTemplateRecord
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.user_repo import UserRepository, verify_password
from utils.auth import get_current_user_id, require_page_auth
from utils.exceptions import DatabaseError, ValidationError
from utils.privacy import inject_autocomplete_off
from utils.validators import is_valid_email

logger = logging.getLogger(__name__)

_PW_CHANGE_FAIL_KEY = "_pw_change_fail_count"
_PW_CHANGE_MAX_ATTEMPTS = 5

# --- 成功メッセージの永続化キー ---
_SUCCESS_MSG_KEY = "_settings_success_msg"

# --- プロバイダー表示名 ---
_PROVIDER_LABELS: dict[str, str] = {
    "gemini": "Google Gemini",
    "openai": "OpenAI",
    "anthropic": "Anthropic",
}


def _show_deferred_success() -> None:
    """session_state に保存された成功メッセージを表示し、クリアする。

    st.rerun() 前に設定された成功メッセージを、
    rerun 後の描画で確実に表示するためのヘルパー。
    """
    msg = st.session_state.pop(_SUCCESS_MSG_KEY, None)
    if msg:
        st.success(msg)


def _initialize_state() -> None:
    """session_state のキーが未初期化の場合にデフォルト値を設定する。"""
    if SESSION_KEY_API_PROVIDER not in st.session_state:
        st.session_state[SESSION_KEY_API_PROVIDER] = DEFAULT_API_PROVIDER
    if SESSION_KEY_API_MODEL not in st.session_state:
        st.session_state[SESSION_KEY_API_MODEL] = DEFAULT_MODEL
    if SESSION_KEY_PII_ANONYMIZE not in st.session_state:
        st.session_state[SESSION_KEY_PII_ANONYMIZE] = True
    if SESSION_KEY_TEMPLATE_EDIT_ID not in st.session_state:
        st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = None


def _check_system_api_key(provider: str) -> bool:
    """指定プロバイダーのシステムAPIキー（.env）が設定されているか確認する。

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
    _show_deferred_success()
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
        format_func=lambda x: _PROVIDER_LABELS.get(x, x),
    )

    # プロバイダー変更時にモデルをデフォルトにリセット＆DBに永続化
    if selected_provider != current_provider:
        new_model = PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
        st.session_state[SESSION_KEY_API_PROVIDER] = selected_provider
        st.session_state[SESSION_KEY_API_MODEL] = new_model
        _save_user_preferences(selected_provider, new_model)
        st.rerun()

    # --- APIキーステータス ---
    user_id = get_current_user_id()
    conn = get_db_connection()
    user_repo = UserRepository(conn)
    user_key = user_repo.get_api_key(user_id, selected_provider) if user_id else None

    if user_key:
        st.success(f"APIキーが登録済みです（{selected_provider}）。")
    else:
        st.warning("APIキーが未設定です。下部の「APIキーの管理」から登録してください。")

    # --- モデル設定 ---
    default_model = PROVIDER_DEFAULT_MODELS.get(selected_provider, "")
    model_input = st.text_input(
        "モデル名",
        value=current_model,
        placeholder=default_model,
        help=f"デフォルト: {default_model}",
        autocomplete="one-time-code",
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

    provider_label = _PROVIDER_LABELS.get(selected_provider, selected_provider)
    model_display = model_input or default_model
    key_source = "✅ 設定済み" if user_key else "⚠️ 未設定"

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**プロバイダー**<br>`{provider_label}`", unsafe_allow_html=True)
    col2.markdown(f"**モデル**<br>`{html.escape(model_display)}`", unsafe_allow_html=True)
    col3.markdown(f"**APIキー**<br>{key_source}", unsafe_allow_html=True)

    # --- APIキー管理（BYOK） ---
    st.markdown("---")
    st.header("APIキーの管理（BYOK）")
    st.caption(
        "各プロバイダーのAPIキーを登録すると、システムのAPIキーよりも優先して使用されます。"
        "空欄にして保存するとキーを削除できます。"
    )

    # 現在登録されているキーを取得
    current_keys: dict[str, str] = {}
    if user_id:
        user = user_repo.find_by_id(user_id)
        if user and user.api_keys_json:
            try:
                current_keys = json.loads(user.api_keys_json)
            except (json.JSONDecodeError, TypeError):
                current_keys = {}

    for provider in SUPPORTED_PROVIDERS:
        label = _PROVIDER_LABELS.get(provider, provider)
        current_value = current_keys.get(provider, "")
        display_value = f"****{current_value[-4:]}" if current_value else ""

        with st.form(f"api_key_form_{provider}"):
            st.subheader(label)
            if current_value:
                st.caption(f"登録済み: {display_value}")
            else:
                st.caption("未登録")

            new_key = st.text_input(
                f"{label} APIキー",
                type="password",
                placeholder="新しいAPIキーを入力（空欄で削除）",
                key=f"api_key_input_{provider}",
                autocomplete="one-time-code",
            )
            key_submitted = st.form_submit_button("保存", use_container_width=True)

            if key_submitted and user_id:
                try:
                    user_repo.update_api_key(user_id, provider, new_key)
                    if new_key:
                        st.session_state[_SUCCESS_MSG_KEY] = (
                            f"{label} のAPIキーを更新しました。"
                        )
                    else:
                        st.session_state[_SUCCESS_MSG_KEY] = (
                            f"{label} のAPIキーを削除しました。"
                        )
                    st.rerun()
                except DatabaseError:
                    st.error("APIキーの更新に失敗しました。")


def _render_account_settings() -> None:
    """アカウント設定セクション（アカウント情報・表示名変更・パスワード変更）を表示する。"""
    _show_deferred_success()
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

    # --- アカウント情報 ---
    st.header("アカウント情報")
    st.text_input("アカウントID（変更不可）", value=user.username, disabled=True)
    st.caption("ログイン時に使用するIDです。変更はできません。")

    # --- 表示名の変更 ---
    st.markdown("---")
    st.header("表示名の変更")
    st.caption("サイドバーや画面上に表示される名前を変更できます。")

    current_display = user.display_name or user.username
    with st.form("change_display_name_form"):
        new_display_name = st.text_input(
            "表示名",
            value=current_display,
            max_chars=50,
            placeholder="画面上に表示する名前",
            autocomplete="one-time-code",
        )
        display_submitted = st.form_submit_button("表示名を変更", use_container_width=True)

        if display_submitted:
            stripped_name = new_display_name.strip()
            if not stripped_name:
                st.error("表示名を入力してください。")
            elif stripped_name == current_display:
                st.info("表示名に変更はありません。")
            else:
                try:
                    result = user_repo.update_display_name(user_id, stripped_name)
                    if result:
                        st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] = stripped_name
                        st.session_state[_SUCCESS_MSG_KEY] = (
                            f"表示名を「{stripped_name}」に変更しました。"
                        )
                        st.rerun()
                    else:
                        st.error("表示名の変更に失敗しました。")
                except ValidationError as e:
                    st.warning(str(e))
                except DatabaseError:
                    st.error("表示名の変更に失敗しました。")

    # --- メールアドレス設定 ---
    st.markdown("---")
    st.header("メールアドレス")
    st.caption(
        "メールアドレスを登録すると、パスワードを忘れた場合にログイン画面から"
        "セルフサービスでパスワードを再設定できます。"
    )

    current_email = user.email or ""
    with st.form("change_email_form"):
        new_email = st.text_input(
            "メールアドレス",
            value=current_email,
            placeholder="example@mail.com",
            autocomplete="email",
        )
        email_submitted = st.form_submit_button("メールアドレスを保存", use_container_width=True)

        if email_submitted:
            stripped_email = new_email.strip()
            if stripped_email == current_email:
                st.info("メールアドレスに変更はありません。")
            elif stripped_email and not is_valid_email(stripped_email):
                st.error("有効なメールアドレスを入力してください。")
            else:
                try:
                    user_repo.update_email(user_id, stripped_email or None)
                    if stripped_email:
                        st.session_state[_SUCCESS_MSG_KEY] = (
                            f"メールアドレスを「{stripped_email}」に更新しました。"
                        )
                    else:
                        st.session_state[_SUCCESS_MSG_KEY] = "メールアドレスを削除しました。"
                    st.rerun()
                except DatabaseError as e:
                    error_msg = str(e)
                    if "既に登録" in error_msg:
                        st.error("このメールアドレスは既に他のユーザーに登録されています。")
                    else:
                        st.error("メールアドレスの更新に失敗しました。")

    # --- パスワード変更 ---
    st.markdown("---")
    st.header("パスワードの変更")

    pw_fails = st.session_state.get(_PW_CHANGE_FAIL_KEY, 0)
    pw_locked = pw_fails >= _PW_CHANGE_MAX_ATTEMPTS

    if pw_locked:
        st.error(
            f"パスワード変更の試行回数が上限（{_PW_CHANGE_MAX_ATTEMPTS}回）に達しました。"
            "再度試すにはログインし直してください。"
        )

    with st.form("change_password_form"):
        current_pw = st.text_input(
            "現在のパスワード",
            type="password",
            disabled=pw_locked,
            autocomplete="one-time-code",
        )
        new_pw = st.text_input(
            "新しいパスワード",
            type="password",
            disabled=pw_locked,
            autocomplete="new-password",
        )
        confirm_pw = st.text_input(
            "新しいパスワード（確認）",
            type="password",
            disabled=pw_locked,
            autocomplete="new-password",
        )
        pw_submitted = st.form_submit_button(
            "パスワードを変更", use_container_width=True, disabled=pw_locked
        )

        if pw_submitted and not pw_locked:
            if not current_pw or not new_pw or not confirm_pw:
                st.error("すべてのフィールドを入力してください。")
            elif not verify_password(current_pw, user.password_hash):
                st.session_state[_PW_CHANGE_FAIL_KEY] = pw_fails + 1
                st.error("現在のパスワードが正しくありません。")
            elif new_pw != confirm_pw:
                st.error("新しいパスワードが一致しません。")
            elif len(new_pw) < PASSWORD_MIN_LENGTH:
                st.error(f"パスワードは{PASSWORD_MIN_LENGTH}文字以上で設定してください。")
            else:
                try:
                    result = user_repo.update_password(user_id, new_pw)
                    if result:
                        st.session_state.pop(_PW_CHANGE_FAIL_KEY, None)
                        st.success("パスワードを変更しました。")
                    else:
                        st.error("パスワードの変更に失敗しました。")
                except DatabaseError:
                    st.error("パスワードの変更に失敗しました。")


def _render_privacy_settings() -> None:
    """プライバシー設定セクションを表示する。"""
    st.header("個人情報保護（PII匿名化）")
    st.caption(
        "AI鑑定レポート生成時に、相談者の名前・フリガナを匿名化してからLLM APIに送信します。"
        "命式データと悩みテキストはAIの鑑定に必要なためそのまま送信されます。"
    )

    current_value = st.session_state.get(SESSION_KEY_PII_ANONYMIZE, True)
    anonymize = st.toggle(
        "名前・フリガナを匿名化してAPI送信",
        value=current_value,
        help=(
            "ONの場合: 名前は「相談者様」に、フリガナは省略されてAPIに送信されます。"
            "名前を使ったハイブリッド鑑定（漢字の意味・音韻分析）はスキップされます。\n\n"
            "OFFの場合: 名前・フリガナがそのままAPIに送信され、"
            "漢字の意味や音韻を含む詳細な鑑定が可能になります。"
        ),
    )
    st.session_state[SESSION_KEY_PII_ANONYMIZE] = anonymize

    if anonymize:
        st.info(
            "匿名化が有効です。名前は「相談者様」に置換されてAPIに送信されます。"
            "名前×命式のハイブリッド鑑定（漢字の意味・音韻分析）はスキップされます。"
        )
    else:
        st.warning(
            "匿名化が無効です。相談者の名前・フリガナがそのままLLM APIに送信されます。"
            "名前を使った詳細な鑑定が利用できますが、個人情報が外部に送信される点にご注意ください。"
        )


def _render_template_list(repo: PromptTemplateRepository) -> None:
    """テンプレート一覧と操作UIを表示する。

    Args:
        repo: プロンプトテンプレートリポジトリ。
    """
    _show_deferred_success()
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
                            st.session_state[_SUCCESS_MSG_KEY] = (
                                f"「{tmpl.name}」をデフォルトに設定しました。"
                            )
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
                            st.session_state[_SUCCESS_MSG_KEY] = (
                                f"「{tmpl.name}」を削除しました。"
                            )
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
        name = st.text_input(
            "テンプレート名",
            placeholder="例: 恋愛相談向けテンプレート",
            autocomplete="one-time-code",
        )
        description = st.text_input(
            "説明（任意）",
            placeholder="このテンプレートの用途",
            autocomplete="one-time-code",
        )
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
                    st.session_state[_SUCCESS_MSG_KEY] = (
                        f"テンプレート「{name}」を作成しました。"
                    )
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
        name = st.text_input(
            "テンプレート名",
            value=tmpl.name,
            autocomplete="one-time-code",
        )
        description = st.text_input(
            "説明",
            value=tmpl.description or "",
            autocomplete="one-time-code",
        )
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
                    st.session_state[_SUCCESS_MSG_KEY] = "テンプレートを更新しました。"
                    st.rerun()
                except DatabaseError as e:
                    st.error(str(e))

        if cancel_clicked:
            st.session_state[SESSION_KEY_TEMPLATE_EDIT_ID] = None
            st.rerun()


def main() -> None:
    """設定ページのメイン処理。"""
    require_page_auth()
    _initialize_state()
    inject_autocomplete_off()

    st.title("設定")
    st.markdown(
        '<p class="page-description">'
        "APIキー・プロンプトテンプレート・アカウントの管理を行います"
        "</p>",
        unsafe_allow_html=True,
    )

    tab_api, tab_privacy, tab_template, tab_account = st.tabs(
        ["API設定", "プライバシー", "プロンプトテンプレート", "アカウント設定"]
    )

    with tab_api:
        _render_api_settings()

    with tab_privacy:
        _render_privacy_settings()

    with tab_template:
        conn = get_db_connection()
        repo = PromptTemplateRepository(conn)
        _render_template_list(repo)

    with tab_account:
        _render_account_settings()


main()
