"""管理者ページ — ユーザー管理・招待リンク管理。"""

import logging
from datetime import datetime

import streamlit as st

from config import (
    INVITATION_DEFAULT_EXPIRY_HOURS,
    INVITATION_TOKEN_QUERY_PARAM,
    SESSION_KEY_AUTH_ROLE,
)
from db_init import get_db_connection
from db_service.repositories.invitation_repo import InvitationRepository
from db_service.repositories.user_repo import UserRepository
from utils.auth import get_current_user_id
from utils.exceptions import DatabaseError

logger = logging.getLogger(__name__)


def _require_admin() -> bool:
    """管理者ロールを確認する。

    非管理者の場合はエラー表示と st.stop() でページ実行を停止する。

    Returns:
        管理者なら True。非管理者の場合はエラー表示して False。
    """
    role = st.session_state.get(SESSION_KEY_AUTH_ROLE)
    if role != "admin":
        st.error("このページは管理者のみアクセスできます。")
        st.stop()
        return False  # st.stop() で到達しないが型安全のため保持
    return True


def _render_user_management(user_repo: UserRepository) -> None:
    """ユーザー管理セクションを表示する。

    Args:
        user_repo: UserRepository インスタンス。
    """
    st.header("ユーザー管理")

    try:
        users = user_repo.find_all()
    except DatabaseError:
        st.error("ユーザー一覧の取得に失敗しました。")
        return

    if not users:
        st.info("登録されたユーザーはいません。")
        return

    current_user_id = get_current_user_id()

    st.caption(f"登録ユーザー数: {len(users)}")

    for user in users:
        is_self = user.id == current_user_id
        role_badge = " (admin)" if user.role == "admin" else ""
        self_badge = " — あなた" if is_self else ""

        with st.expander(f"{user.username}{role_badge}{self_badge}", expanded=False):
            col1, col2, col3 = st.columns(3)
            col1.text(f"ロール: {user.role}")
            col2.text(f"作成日: {user.created_at[:10]}")
            col3.text(f"更新日: {user.updated_at[:10]}")

            if user.api_keys_json:
                st.caption("APIキー: 登録済み")
            else:
                st.caption("APIキー: 未登録")

            # 自分自身は削除不可
            if is_self:
                st.button(
                    "削除",
                    key=f"del_user_{user.id}",
                    disabled=True,
                    help="自分自身は削除できません",
                    use_container_width=True,
                )
            else:
                if st.button(
                    f"{user.username} を削除",
                    key=f"del_user_{user.id}",
                    type="secondary",
                    use_container_width=True,
                ):
                    st.session_state[f"_confirm_del_{user.id}"] = True
                    st.rerun()

                if st.session_state.get(f"_confirm_del_{user.id}"):
                    st.warning(f"本当に {user.username} を削除しますか？この操作は取り消せません。")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button(
                            "削除する",
                            key=f"confirm_del_{user.id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            try:
                                user_repo.delete(user.id)
                                st.session_state.pop(f"_confirm_del_{user.id}", None)
                                st.success(f"{user.username} を削除しました。")
                                st.rerun()
                            except DatabaseError:
                                st.error("ユーザーの削除に失敗しました。")
                    with col_no:
                        if st.button(
                            "キャンセル",
                            key=f"cancel_del_{user.id}",
                            use_container_width=True,
                        ):
                            st.session_state.pop(f"_confirm_del_{user.id}", None)
                            st.rerun()


def _render_invitation_management(invitation_repo: InvitationRepository) -> None:
    """招待リンク管理セクションを表示する。

    Args:
        invitation_repo: InvitationRepository インスタンス。
    """
    st.header("招待リンク管理")

    # --- 招待リンク生成 ---
    st.subheader("新しい招待リンクを生成")

    expiry_hours = st.number_input(
        "有効期限（時間）",
        min_value=1,
        max_value=720,
        value=INVITATION_DEFAULT_EXPIRY_HOURS,
        step=24,
        help="招待リンクの有効期限を時間単位で指定します。",
    )

    if st.button("招待リンクを生成", type="primary", use_container_width=True):
        admin_user_id = get_current_user_id()
        if not admin_user_id:
            st.error("ログインが必要です。")
            return

        try:
            token = invitation_repo.create(
                created_by=admin_user_id,
                expiry_hours=int(expiry_hours),
            )
            # 現在のURLのベースを取得してリンクを構築
            base_url = st.context.headers.get("Origin", "http://localhost:8501")
            invite_url = f"{base_url}/?{INVITATION_TOKEN_QUERY_PARAM}={token}"
            st.success("招待リンクを生成しました。")
            st.code(invite_url, language=None)
            st.caption("このURLを登録希望者に共有してください。")
        except DatabaseError:
            st.error("招待リンクの生成に失敗しました。")

    st.markdown("---")

    # --- 招待リンク一覧 ---
    st.subheader("招待リンク一覧")

    try:
        invitations = invitation_repo.find_all()
    except DatabaseError:
        st.error("招待リンクの取得に失敗しました。")
        return

    if not invitations:
        st.info("招待リンクはまだ生成されていません。")
        return

    for inv in invitations:
        now = datetime.now()
        expires_at = datetime.fromisoformat(inv.expires_at)
        is_used = inv.used_by is not None
        is_expired = now > expires_at

        if is_used:
            status = "使用済み"
            icon = "\u2705"
        elif is_expired:
            status = "期限切れ"
            icon = "\u274c"
        else:
            status = "有効"
            icon = "\U0001f7e2"

        with st.expander(f"{icon} {inv.token[:12]}... — {status}", expanded=False):
            col1, col2 = st.columns(2)
            col1.text(f"ステータス: {status}")
            col2.text(f"作成日: {inv.created_at[:10]}")

            col3, col4 = st.columns(2)
            col3.text(f"有効期限: {inv.expires_at[:16]}")
            if inv.used_at:
                col4.text(f"使用日: {inv.used_at[:10]}")

            if not is_used and not is_expired:
                base_url = st.context.headers.get("Origin", "http://localhost:8501")
                invite_url = f"{base_url}/?token={inv.token}"
                st.code(invite_url, language=None)

            if st.button("削除", key=f"del_inv_{inv.id}", use_container_width=True):
                try:
                    invitation_repo.delete(inv.id)
                    st.success("招待リンクを削除しました。")
                    st.rerun()
                except DatabaseError:
                    st.error("招待リンクの削除に失敗しました。")


def main() -> None:
    """管理者ページのメイン処理。"""
    if not _require_admin():
        return

    st.title("管理者ページ")
    st.markdown(
        '<p class="page-description">ユーザーアカウントと招待リンクの管理を行います</p>',
        unsafe_allow_html=True,
    )

    conn = get_db_connection()
    user_repo = UserRepository(conn)
    invitation_repo = InvitationRepository(conn)

    tab_users, tab_invitations = st.tabs(["ユーザー管理", "招待リンク管理"])

    with tab_users:
        _render_user_management(user_repo)

    with tab_invitations:
        _render_invitation_management(invitation_repo)


main()
