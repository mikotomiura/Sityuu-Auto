"""Streamlit エントリーポイント。

アプリケーションのページ設定とサイドバーナビゲーションを構成する。
起動コマンド: streamlit run src/app.py
"""

import streamlit as st

from config import APP_ICON, APP_TITLE

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
st.sidebar.caption("四柱推命・算命学 AI鑑定支援ツール")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**使い方**\n1. 相談者の情報を入力\n2. 命式を自動算出\n3. AI鑑定で分析レポート生成"
)
st.sidebar.markdown("---")

reading_page = st.Page("pages/01_reading.py", title="鑑定", icon="\u2728")
history_page = st.Page("pages/02_history.py", title="鑑定履歴", icon="\U0001f4cb")
clients_page = st.Page("pages/03_clients.py", title="相談者管理", icon="\U0001f465")
settings_page = st.Page("pages/04_settings.py", title="設定", icon="\u2699\ufe0f")

pg = st.navigation([reading_page, history_page, clients_page, settings_page])
pg.run()
