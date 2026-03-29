"""Streamlit用DB接続の初期化・キャッシュ。

DB層（db_service）にStreamlit依存を持ち込まないための薄いラッパー。
UI層のページファイルからimportして使用する。

各Streamlitセッション（スレッド）に独立したDB接続を提供し、
SQLiteの同時アクセスによるロック競合を軽減する。
"""

import logging
import sqlite3
import threading

import streamlit as st

from config import DB_PATH
from db_service.database import create_connection, initialize_database
from db_service.repositories.prompt_template_repo import PromptTemplateRepository
from db_service.repositories.user_repo import UserRepository, generate_random_password

logger = logging.getLogger(__name__)

_thread_local = threading.local()


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

    initial_password = generate_random_password()

    logger.info("初期管理者アカウントを登録します")
    repo.create(username="admin", password=initial_password, role="admin")
    logger.info("初期管理者アカウント登録完了。初回ログイン後にパスワードを変更してください。")

    # コンソールに初期パスワードを表示（ログではなく標準出力に1度だけ）
    print("=" * 50)  # noqa: T201
    print("  初期管理者アカウント")  # noqa: T201
    print("  ユーザー名: admin")  # noqa: T201
    print(f"  パスワード: {initial_password}")  # noqa: T201
    print("  ※ 初回ログイン後に必ず変更してください")  # noqa: T201
    print("=" * 50)  # noqa: T201


@st.cache_resource
def _initialize_db() -> bool:
    """DB初期化を1度だけ実行する（マイグレーション・初期データ投入）。

    Note:
        初期化専用コネクションを使用する。initialize_database() 内の
        executescript() は暗黙の COMMIT を発行するため、このコネクションを
        通常のリクエスト処理に再利用してはならない。

    Returns:
        初期化完了なら True。
    """
    conn = create_connection(DB_PATH)
    try:
        initialize_database(conn)
        _seed_default_templates(conn)
        _seed_default_admin(conn)
    finally:
        conn.close()
    return True


def get_db_connection() -> sqlite3.Connection:
    """スレッドローカルなDB接続を取得する。

    各Streamlitセッション（スレッド）に独立したDB接続を提供する。
    同一スレッド内では接続を再利用し、異なるスレッドでは別々の接続を使用する。
    これによりSQLiteの同時アクセスによるロック競合を軽減する。

    初回呼び出し時にマイグレーションと初期データ投入を実行する（1度のみ）。

    Returns:
        スレッドローカルなSQLiteコネクション。

    Raises:
        DatabaseError: DB接続またはマイグレーションに失敗した場合。
    """
    _initialize_db()

    conn = getattr(_thread_local, "conn", None)
    if conn is not None:
        try:
            conn.execute("SELECT 1")
            # autocommit モードでも明示的 BEGIN が rollback されずに残る可能性がある
            # （ページ処理中の例外で begin_transaction の ROLLBACK に到達しなかったケース）
            if conn.in_transaction:
                logger.warning("未コミットトランザクションを検出、ロールバックします")
                conn.execute("ROLLBACK")
            return conn
        except sqlite3.Error as e:
            logger.warning("DB接続の検証またはロールバックに失敗: %s", e)
            conn = None

    conn = create_connection(DB_PATH)
    _thread_local.conn = conn
    return conn
