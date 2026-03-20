"""Streamlit用DB接続の初期化・キャッシュ。

DB層（db_service）にStreamlit依存を持ち込まないための薄いラッパー。
UI層のページファイルからimportして使用する。
"""

import logging
import sqlite3

import streamlit as st

from config import DB_PATH
from db_service.database import create_connection, initialize_database
from db_service.repositories.prompt_template_repo import PromptTemplateRepository

logger = logging.getLogger(__name__)


def _seed_default_templates(conn: sqlite3.Connection) -> None:
    """初期テンプレートをDBに登録する。

    テンプレートが1件も登録されていない場合のみ、
    デフォルトのシステムプロンプトをDBに保存する。

    Args:
        conn: SQLite コネクション。
    """
    repo = PromptTemplateRepository(conn)

    if repo.count() > 0:
        return

    logger.info("初期プロンプトテンプレートを登録します")

    # 鑑定レポート用デフォルトテンプレート
    reading_system = (
        "あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した鑑定師です。"
        "以下のユーザーメッセージに含まれる命式データと悩みをもとに、"
        "鑑定テキストのベースを作成してください。"
    )
    repo.save(
        name="標準鑑定テンプレート",
        system_prompt=reading_system,
        description=(
            "デフォルトの鑑定レポート生成用テンプレート。"
            "命式の総合評価・強みと課題・悩みへの解釈・アドバイス・傾聴ガイドの5セクション構成。"
        ),
        is_default=True,
    )

    # 傾聴ヒント特化テンプレート
    listening_system = (
        "あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した"
        "メンタリングの専門家です。"
        "以下のユーザーメッセージに含まれる命式データと悩みをもとに、"
        "傾聴のヒントを作成してください。"
    )
    repo.save(
        name="傾聴ヒント特化テンプレート",
        system_prompt=listening_system,
        description=(
            "メンター向けの傾聴ヒント生成に特化したテンプレート。"
            "相談者の特性に合った聴き方・声掛け・注意点を出力。"
        ),
        is_default=False,
    )

    logger.info("初期テンプレート登録完了（2件）")


@st.cache_resource
def get_db_connection() -> sqlite3.Connection:
    """DB接続を取得する（Streamlitセッション間で共有）。

    初回呼び出し時にDB接続を作成し、マイグレーションを実行する。
    テンプレートが未登録の場合は初期テンプレートを登録する。
    以降の呼び出しではキャッシュされた接続を返す。

    Returns:
        初期化済みのSQLiteコネクション。

    Raises:
        DatabaseError: DB接続またはマイグレーションに失敗した場合。
    """
    conn = create_connection(DB_PATH)
    initialize_database(conn)
    _seed_default_templates(conn)
    return conn
