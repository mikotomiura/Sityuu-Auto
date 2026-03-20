"""Streamlit用DB接続の初期化・キャッシュ。

DB層（db_service）にStreamlit依存を持ち込まないための薄いラッパー。
UI層のページファイルからimportして使用する。
"""

import sqlite3

import streamlit as st

from config import DB_PATH
from db_service.database import create_connection, initialize_database


@st.cache_resource
def get_db_connection() -> sqlite3.Connection:
    """DB接続を取得する（Streamlitセッション間で共有）。

    初回呼び出し時にDB接続を作成し、マイグレーションを実行する。
    以降の呼び出しではキャッシュされた接続を返す。

    Returns:
        初期化済みのSQLiteコネクション。

    Raises:
        DatabaseError: DB接続またはマイグレーションに失敗した場合。
    """
    conn = create_connection(DB_PATH)
    initialize_database(conn)
    return conn
