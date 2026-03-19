"""DB初期化スクリプト。

コマンドラインから実行してSQLiteデータベースを初期化する。

Usage:
    python scripts/init_db.py
    python scripts/init_db.py --db-path data/fortune.db
"""

import argparse
import logging
import sys
from pathlib import Path

# プロジェクトルートをsys.pathに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.db_service.database import create_connection, initialize_database
from src.utils.exceptions import DatabaseError


def main() -> None:
    """DB初期化のエントリーポイント。"""
    parser = argparse.ArgumentParser(description="占い・メンタリング支援システムのDB初期化")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path("data/fortune.db"),
        help="DBファイルのパス（デフォルト: data/fortune.db）",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger = logging.getLogger(__name__)
    logger.info("DB初期化を開始: %s", args.db_path)

    try:
        conn = create_connection(args.db_path)
        try:
            initialize_database(conn)
            logger.info("DB初期化が正常に完了しました: %s", args.db_path)
        finally:
            conn.close()
    except DatabaseError as e:
        logger.error("DB初期化に失敗しました: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
