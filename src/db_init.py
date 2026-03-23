"""Streamlit用DB接続の初期化・キャッシュ。

DB層（db_service）にStreamlit依存を持ち込まないための薄いラッパー。
UI層のページファイルからimportして使用する。
"""

import logging
import secrets
import sqlite3
import string

import streamlit as st

from config import DB_PATH
from db_service.database import create_connection, initialize_database
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.user_repo import UserRepository

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


def _generate_initial_password(length: int = 12) -> str:
    """初期管理者用のランダムパスワードを生成する。

    Args:
        length: パスワード文字数。

    Returns:
        ランダムパスワード文字列。
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _seed_default_admin(conn: sqlite3.Connection) -> None:
    """初期管理者アカウントを登録する。

    ユーザーが1件も登録されていない場合のみ、
    ランダムパスワードで管理者アカウントを作成し、
    初期パスワードをコンソールに1度だけ表示する。

    Args:
        conn: SQLite コネクション。
    """
    repo = UserRepository(conn)

    if repo.count() > 0:
        return

    initial_password = _generate_initial_password()

    logger.info("初期管理者アカウントを登録します")
    repo.create(username="admin", password=initial_password, role="admin")
    logger.info("初期管理者アカウント登録完了。初回ログイン後にパスワードを変更してください。")

    # コンソールに初期パスワードを表示（ログではなく標準出力に1度だけ）
    print("=" * 50)  # noqa: T201
    print("  初期管理者アカウント")  # noqa: T201
    print(f"  ユーザー名: admin")  # noqa: T201
    print(f"  パスワード: {initial_password}")  # noqa: T201
    print("  ※ 初回ログイン後に必ず変更してください")  # noqa: T201
    print("=" * 50)  # noqa: T201


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
    _seed_default_admin(conn)
    return conn
