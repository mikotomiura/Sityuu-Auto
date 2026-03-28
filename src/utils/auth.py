"""認証ユーティリティ — ログイン状態の管理とUI表示。

Streamlit の st.session_state を使用してログイン状態を管理する。
未ログイン時はログインフォームを表示し、st.stop() でページ遷移を阻止する。
"""

import logging
import time
import uuid

import streamlit as st

from config import (
    INVITATION_TOKEN_QUERY_PARAM,
    PASSWORD_MIN_LENGTH,
    SESSION_KEY_API_MODEL,
    SESSION_KEY_API_PROVIDER,
    SESSION_KEY_AUTH_DISPLAY_NAME,
    SESSION_KEY_AUTH_FAIL_COUNT,
    SESSION_KEY_AUTH_ROLE,
    SESSION_KEY_AUTH_USER_ID,
    SESSION_KEY_AUTH_USERNAME,
    SESSION_TOKEN_QUERY_PARAM,
)
from db_service.models import UserRecord
from db_service.repositories.auth_session_repo import AuthSessionRepository
from db_service.repositories.invitation_repo import InvitationRepository
from db_service.repositories.user_repo import UserRepository
from utils.exceptions import AuthenticationError, DatabaseError
from utils.privacy import inject_autocomplete_off

logger = logging.getLogger(__name__)


def is_logged_in() -> bool:
    """ログイン済みかどうかを判定する。

    Returns:
        ログイン済みなら True。
    """
    return bool(st.session_state.get(SESSION_KEY_AUTH_USER_ID))


def get_current_user_id() -> str | None:
    """現在のログインユーザーIDを取得する。

    Returns:
        ユーザーID文字列。未ログインの場合は None。
    """
    return st.session_state.get(SESSION_KEY_AUTH_USER_ID)


def get_current_display_name() -> str | None:
    """現在のログインユーザーの表示名を取得する。

    Returns:
        表示名。未ログインの場合は None。
    """
    return st.session_state.get(
        SESSION_KEY_AUTH_DISPLAY_NAME,
        st.session_state.get(SESSION_KEY_AUTH_USERNAME),
    )


def get_current_username() -> str | None:
    """現在のログインユーザー名を取得する。

    Returns:
        ユーザー名。未ログインの場合は None。
    """
    return st.session_state.get(SESSION_KEY_AUTH_USERNAME)


def logout(auth_session_repo: AuthSessionRepository | None = None) -> None:
    """ログアウト処理（セッションから認証情報とAPI設定を削除）。

    Args:
        auth_session_repo: セッションリポジトリ。指定時はDBトークンも無効化する。
    """
    # DBセッショントークンを無効化
    session_token = st.query_params.get(SESSION_TOKEN_QUERY_PARAM)
    if session_token and auth_session_repo is not None:
        try:
            auth_session_repo.revoke(session_token)
        except DatabaseError:
            logger.warning("セッショントークン無効化に失敗")

    # URLからセッションパラメータを削除
    if SESSION_TOKEN_QUERY_PARAM in st.query_params:
        del st.query_params[SESSION_TOKEN_QUERY_PARAM]

    # session_stateをクリア
    for key in (
        SESSION_KEY_AUTH_USER_ID,
        SESSION_KEY_AUTH_USERNAME,
        SESSION_KEY_AUTH_ROLE,
        SESSION_KEY_AUTH_DISPLAY_NAME,
        SESSION_KEY_AUTH_FAIL_COUNT,
        SESSION_KEY_API_PROVIDER,
        SESSION_KEY_API_MODEL,
    ):
        st.session_state.pop(key, None)


def _restore_session_from_user(user: UserRecord) -> None:
    """UserRecord から session_state を復元する。

    Args:
        user: ユーザーレコード。
    """
    st.session_state[SESSION_KEY_AUTH_USER_ID] = user.id
    st.session_state[SESSION_KEY_AUTH_USERNAME] = user.username
    st.session_state[SESSION_KEY_AUTH_ROLE] = user.role
    st.session_state[SESSION_KEY_AUTH_DISPLAY_NAME] = (
        user.display_name or user.username
    )
    if user.preferred_provider:
        st.session_state[SESSION_KEY_API_PROVIDER] = user.preferred_provider
    if user.preferred_model:
        st.session_state[SESSION_KEY_API_MODEL] = user.preferred_model


def _try_restore_from_token(
    auth_session_repo: AuthSessionRepository,
) -> bool:
    """クエリパラメータのセッショントークンからログイン状態を復元する。

    復元成功時はトークンをURLに保持し、session_state揮発時の再復元に備える。
    復元失敗時（期限切れ等）は無効なトークンをURLから削除する。

    Note:
        Referer漏洩は app.py の ``<meta name="referrer" content="no-referrer">``
        で防止済み。トークンをURLに残してもセキュリティリスクは限定的。

    Args:
        auth_session_repo: セッションリポジトリ。

    Returns:
        復元成功なら True。
    """
    token = st.query_params.get(SESSION_TOKEN_QUERY_PARAM)
    if not token:
        return False

    try:
        user = auth_session_repo.validate_token(token)
    except DatabaseError:
        logger.warning("セッショントークン検証中にDBエラー")
        return False

    if user is None:
        # 無効なトークンをURLから削除
        del st.query_params[SESSION_TOKEN_QUERY_PARAM]
        return False

    _restore_session_from_user(user)
    # トークンはURLに保持（session_state揮発時の再復元用）
    logger.info("セッショントークンからログイン復元: username=%s", user.username)
    return True


def _login(
    user_repo: UserRepository,
    username: str,
    password: str,
    auth_session_repo: AuthSessionRepository | None = None,
) -> bool:
    """ログイン処理を実行する。

    Args:
        user_repo: UserRepository インスタンス。
        username: ユーザー名。
        password: 平文パスワード。
        auth_session_repo: セッションリポジトリ。指定時は永続トークンを生成する。

    Returns:
        ログイン成功なら True。
    """
    try:
        user = user_repo.authenticate(username, password)
        _restore_session_from_user(user)
        st.session_state.pop(SESSION_KEY_AUTH_FAIL_COUNT, None)

        # セッショントークンを生成してURLに埋め込む
        if auth_session_repo is not None:
            try:
                token = auth_session_repo.create(user.id)
                st.query_params[SESSION_TOKEN_QUERY_PARAM] = token
                auth_session_repo.cleanup_expired()
            except DatabaseError:
                logger.warning("セッショントークン生成に失敗（ログインは継続）")

        logger.info("ログイン成功: username=%s", username)
        return True
    except AuthenticationError:
        logger.warning("ログイン失敗: username=%s", username)
        # ブルートフォース対策: 失敗回数に応じた遅延
        fails = st.session_state.get(SESSION_KEY_AUTH_FAIL_COUNT, 0) + 1
        st.session_state[SESSION_KEY_AUTH_FAIL_COUNT] = fails
        delay = min(fails * 1.0, 5.0)  # 最大5秒
        time.sleep(delay)
        return False


def render_login_form(
    user_repo: UserRepository,
    auth_session_repo: AuthSessionRepository | None = None,
) -> None:
    """ログインフォームを画面中央に表示する。

    ログイン成功時は st.rerun() でページを再読み込みする。

    Args:
        user_repo: UserRepository インスタンス。
        auth_session_repo: セッションリポジトリ（トークン生成用）。
    """
    inject_autocomplete_off()

    # サイドバーを視覚的に非表示にする
    # Note: display:none はStreamlitの内部サイドバー状態を破壊するため、
    #       visibility + 幅縮小で非表示化しつつDOM状態を保持する
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 中央寄せのレイアウト
    _col_left, col_center, _col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            '<div class="login-card">'
            '<div class="login-logo">\U0001f52e</div>'
            '<div class="login-title">Sityuu-Auto</div>'
            '<div class="login-divider"></div>'
            '<div class="login-subtitle">四柱推命・算命学 AI鑑定支援ツール</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        # フォームキーにUUIDを含め、ブラウザが過去入力と紐付けるのを防ぐ
        if "_login_form_id" not in st.session_state:
            st.session_state["_login_form_id"] = uuid.uuid4().hex[:8]
        form_id = st.session_state["_login_form_id"]

        with st.form(f"login_form_{form_id}"):
            username = st.text_input(
                "ユーザー名",
                placeholder="username",
                key=f"login_user_{form_id}",
                autocomplete="one-time-code",
            )
            password = st.text_input(
                "パスワード",
                type="password",
                placeholder="password",
                key=f"login_pass_{form_id}",
                autocomplete="new-password",
            )
            submitted = st.form_submit_button("ログイン", type="primary", use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("ユーザー名とパスワードを入力してください。")
                else:
                    try:
                        success = _login(user_repo, username, password, auth_session_repo)
                        if success:
                            st.rerun()
                        else:
                            st.error("ユーザー名またはパスワードが正しくありません。")
                    except DatabaseError:
                        st.error("認証処理中にエラーが発生しました。")


def _render_registration_form(
    user_repo: UserRepository,
    invitation_repo: InvitationRepository,
    token: str,
) -> None:
    """招待トークンによるセルフ登録フォームを表示する。

    Args:
        user_repo: UserRepository インスタンス。
        invitation_repo: InvitationRepository インスタンス。
        token: 招待トークン文字列。
    """
    inject_autocomplete_off()

    # サイドバーを非表示（登録フォーム）
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # トークン検証
    invitation = invitation_repo.validate_token(token)
    if invitation is None:
        _col_left, col_center, _col_right = st.columns([1, 2, 1])
        with col_center:
            st.error("この招待リンクは無効です（期限切れまたは使用済み）。")
            st.info("管理者に新しい招待リンクの発行を依頼してください。")
            if st.button("ログイン画面へ", use_container_width=True):
                st.query_params.clear()
                st.rerun()
        return

    _col_left, col_center, _col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown(
            '<div class="login-card">'
            '<div class="login-logo">\U0001f52e</div>'
            '<div class="login-title">Sityuu-Auto</div>'
            '<div class="login-divider"></div>'
            '<div class="login-subtitle">アカウント登録</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        if "_reg_form_id" not in st.session_state:
            st.session_state["_reg_form_id"] = uuid.uuid4().hex[:8]
        form_id = st.session_state["_reg_form_id"]

        with st.form(f"register_form_{form_id}"):
            username = st.text_input(
                "ユーザー名",
                placeholder="任意のユーザー名を入力",
                key=f"reg_user_{form_id}",
                autocomplete="one-time-code",
            )
            password = st.text_input(
                "パスワード",
                type="password",
                placeholder=f"{PASSWORD_MIN_LENGTH}文字以上",
                key=f"reg_pass_{form_id}",
                autocomplete="new-password",
            )
            confirm_password = st.text_input(
                "パスワード（確認）",
                type="password",
                placeholder="もう一度入力",
                key=f"reg_confirm_{form_id}",
                autocomplete="new-password",
            )
            submitted = st.form_submit_button(
                "アカウントを作成", type="primary", use_container_width=True
            )

            if submitted:
                if not username or not password or not confirm_password:
                    st.error("すべてのフィールドを入力してください。")
                elif len(username.strip()) < 2:
                    st.error("ユーザー名は2文字以上で入力してください。")
                elif len(password) < PASSWORD_MIN_LENGTH:
                    st.error(f"パスワードは{PASSWORD_MIN_LENGTH}文字以上で設定してください。")
                elif password != confirm_password:
                    st.error("パスワードが一致しません。")
                else:
                    try:
                        user_id = user_repo.create(
                            username=username.strip(),
                            password=password,
                            role="user",
                        )
                        if not invitation_repo.use_token(token, user_id):
                            # トークン使用済みマークに失敗 → ユーザーをロールバック
                            user_repo.delete(user_id)
                            st.error("この招待リンクは既に使用されています。")
                        else:
                            st.success("アカウントを作成しました。ログインしてください。")
                            st.query_params.clear()
                            logger.info("招待トークンによるユーザー登録: username=%s", username)
                            st.rerun()
                    except DatabaseError as e:
                        error_msg = str(e)
                        if "既に使用されています" in error_msg:
                            st.error("このユーザー名は既に使用されています。")
                        else:
                            st.error("アカウントの作成に失敗しました。")

        if st.button("ログイン画面へ戻る", use_container_width=True):
            st.query_params.clear()
            st.rerun()


def require_page_auth() -> None:
    """ページ単位の認証チェック（防御深度）。

    app.py の require_login() に加え、各ページが独自に認証状態を検証する。
    未ログイン時はセッション切れの案内を表示し、st.stop() でページ描画を阻止する。

    URLにセッショントークンが残っている場合はページリロードで復元可能なため、
    リロードボタンを表示してユーザーを誘導する。
    """
    if is_logged_in():
        return

    has_token = bool(st.query_params.get(SESSION_TOKEN_QUERY_PARAM))

    if has_token:
        # トークンがURLにある場合、リロードすればapp.pyのrequire_login()で復元される
        st.warning("セッションの接続が切れました。ページを再読み込みしてください。")
        if st.button("ページを再読み込み", type="primary", use_container_width=True):
            st.rerun()
    else:
        st.warning("セッションの有効期限が切れました。再度ログインしてください。")
        st.page_link("app.py", label="ログイン画面へ", icon="\U0001f513", use_container_width=True)

    st.stop()


def require_login(
    user_repo: UserRepository,
    invitation_repo: InvitationRepository | None = None,
    auth_session_repo: AuthSessionRepository | None = None,
) -> None:
    """ログインを必須にする。未ログイン時はフォームを表示して st.stop()。

    セッショントークンがクエリパラメータに含まれている場合は自動復元を試みる。
    招待トークンがクエリパラメータに含まれている場合は登録フォームを表示する。
    app.py のページ設定後に呼び出す。

    Args:
        user_repo: UserRepository インスタンス。
        invitation_repo: InvitationRepository インスタンス（招待登録用）。
        auth_session_repo: セッションリポジトリ（トークン復元用）。
    """
    if is_logged_in():
        return

    # セッショントークンからの復元を試みる
    if auth_session_repo is not None and _try_restore_from_token(auth_session_repo):
        # rerun で session_state が復元された状態をページに反映する
        st.rerun()
        return

    # 招待トークンによる登録フロー
    token = st.query_params.get(INVITATION_TOKEN_QUERY_PARAM)
    if token and invitation_repo is not None:
        _render_registration_form(user_repo, invitation_repo, token)
        st.stop()

    render_login_form(user_repo, auth_session_repo)
    st.stop()
