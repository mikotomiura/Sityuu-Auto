"""Streamlit エントリーポイント。

アプリケーションのページ設定とサイドバーナビゲーションを構成する。
認証ゲートにより、未ログイン時はログインフォームのみ表示する。
起動コマンド: streamlit run src/app.py
"""

import streamlit as st
from dotenv import load_dotenv

from components.theme import inject_custom_theme
from config import APP_ICON, APP_TITLE, SESSION_KEY_AUTH_ROLE
from db_init import get_db_connection
from db_service.repositories.auth_session_repo import AuthSessionRepository
from db_service.repositories.invitation_repo import InvitationRepository
from db_service.repositories.user_repo import UserRepository
from utils.auth import get_current_display_name, logout, require_login
from utils.logger import setup_logging

load_dotenv()
setup_logging()

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_theme()

# --- 認証ゲート ---
conn = get_db_connection()
user_repo = UserRepository(conn)
invitation_repo = InvitationRepository(conn)
auth_session_repo = AuthSessionRepository(conn)
require_login(user_repo, invitation_repo, auth_session_repo)

# --- 認証済み: サイドバー表示を保証 ---
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: block !important;
        visibility: visible !important;
    }
    [data-testid="stHeader"] {
        display: block !important;
        visibility: visible !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- サイドバーとナビゲーション ---
st.sidebar.markdown(
    '<div class="sidebar-brand"><div class="sidebar-brand-icon">\U0001f52e</div></div>',
    unsafe_allow_html=True,
)
st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
st.sidebar.caption("四柱推命・算命学 AI鑑定支援ツール")
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

# ログインユーザー情報とログアウト
display_name = get_current_display_name()
st.sidebar.markdown(f"**ログイン中:** {display_name}")
if st.sidebar.button("ログアウト", use_container_width=True):
    logout(auth_session_repo)
    st.rerun()

st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown(
    "**使い方**\n1. 相談者の情報を入力\n2. 命式を自動算出\n3. AI鑑定で分析レポート生成"
)
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

reading_page = st.Page("pages/01_reading.py", title="鑑定", icon="\u2728")
history_page = st.Page("pages/02_history.py", title="鑑定履歴", icon="\U0001f4cb")
clients_page = st.Page("pages/03_clients.py", title="相談者管理", icon="\U0001f465")
settings_page = st.Page("pages/04_settings.py", title="設定", icon="\u2699\ufe0f")

pages: list[st.Page] = [reading_page, history_page, clients_page, settings_page]

# 管理者ロールの場合のみ管理者ページを追加
if st.session_state.get(SESSION_KEY_AUTH_ROLE) == "admin":
    admin_page = st.Page("pages/05_admin.py", title="管理", icon="\U0001f6e0\ufe0f")
    pages.append(admin_page)

pg = st.navigation(pages)
pg.run()
