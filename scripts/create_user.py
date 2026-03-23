"""ユーザーアカウント発行スクリプト。

コマンドラインからユーザーアカウントを作成する。
初期パスワードはランダム生成され、標準出力に表示される。

Usage:
    python scripts/create_user.py <username>
    python scripts/create_user.py <username> --role admin
    python scripts/create_user.py <username> --password mypassword
    python scripts/create_user.py <username> --db-path data/fortune.sqlite3

Note:
    --password オプションを使用するとシェル履歴にパスワードが残ります。
    セキュリティ上、ランダム生成（--password 未指定）を推奨します。
"""

import argparse
import logging
import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_PATH, PASSWORD_MIN_LENGTH  # noqa: E402
from src.db_service.database import create_connection, initialize_database  # noqa: E402
from src.db_service.repositories.user_repo import (  # noqa: E402
    UserRepository,
    generate_random_password,
)
from src.utils.exceptions import DatabaseError  # noqa: E402


def main() -> None:
    """ユーザー作成のエントリーポイント。"""
    parser = argparse.ArgumentParser(
        description="占い・メンタリング支援システムのユーザーアカウント発行"
    )
    parser.add_argument("username", help="作成するユーザー名")
    parser.add_argument(
        "--role",
        choices=["admin", "user"],
        default="user",
        help="ユーザーロール（デフォルト: user）",
    )
    parser.add_argument(
        "--password",
        default=None,
        help="初期パスワード（未指定でランダム生成）",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help=f"DBファイルのパス（デフォルト: {DB_PATH}）",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger = logging.getLogger(__name__)

    password = args.password or generate_random_password()

    if len(password) < PASSWORD_MIN_LENGTH:
        logger.error("パスワードは%d文字以上で指定してください。", PASSWORD_MIN_LENGTH)
        sys.exit(1)

    try:
        conn = create_connection(args.db_path)
        try:
            initialize_database(conn)
            repo = UserRepository(conn)
            user_id = repo.create(
                username=args.username,
                password=password,
                role=args.role,
            )
            logger.info("ユーザーを作成しました: user_id=%s", user_id)
        finally:
            conn.close()
    except DatabaseError as e:
        logger.error("ユーザー作成に失敗しました: %s", e)
        sys.exit(1)

    # 標準出力に認証情報を表示
    print()  # noqa: T201
    print("=" * 50)  # noqa: T201
    print("  ユーザーアカウントが作成されました")  # noqa: T201
    print("=" * 50)  # noqa: T201
    print(f"  ユーザー名: {args.username}")  # noqa: T201
    print(f"  パスワード: {password}")  # noqa: T201
    print(f"  ロール:     {args.role}")  # noqa: T201
    print("=" * 50)  # noqa: T201
    print()  # noqa: T201
    print("  ※ 初回ログイン後にパスワードを変更してください。")  # noqa: T201


if __name__ == "__main__":
    main()
