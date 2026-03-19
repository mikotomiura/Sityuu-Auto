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
)

st.sidebar.title(f"{APP_ICON} {APP_TITLE}")
st.sidebar.markdown("---")

reading_page = st.Page("pages/01_reading.py", title="鑑定", icon="\u2728")

pg = st.navigation([reading_page])
pg.run()
