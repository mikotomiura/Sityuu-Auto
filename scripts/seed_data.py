"""テストデータ投入スクリプト。

sample_clients.json からサンプル相談者データをDBに投入する。

Usage:
    python scripts/seed_data.py
    python scripts/seed_data.py --db-path data/fortune.sqlite3
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path

# プロジェクトルートをsys.pathに追加
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DB_PATH  # noqa: E402
from src.db_service.database import create_connection, initialize_database  # noqa: E402
from src.db_service.repositories.client_repo import ClientRepository  # noqa: E402
from src.utils.exceptions import DatabaseError  # noqa: E402
from src.utils.logger import setup_logging  # noqa: E402

FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"
SAMPLE_CLIENTS_FILE = FIXTURES_DIR / "sample_clients.json"


def load_sample_clients(file_path: Path) -> list[dict[str, str | None]]:
    """サンプル相談者データをJSONファイルから読み込む。

    Args:
        file_path: JSONファイルのパス。

    Returns:
        相談者データの辞書リスト。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
    """
    data = json.loads(file_path.read_text(encoding="utf-8"))
    return data["clients"]


def seed_clients(db_path: Path, clients_data: list[dict[str, str | None]]) -> int:
    """相談者データをDBに投入する。

    Args:
        db_path: DBファイルのパス。
        clients_data: 相談者データの辞書リスト。

    Returns:
        投入した件数。
    """
    conn = create_connection(db_path)
    try:
        initialize_database(conn)
        repo = ClientRepository(conn)
        count = 0

        for client in clients_data:
            birth_date = date.fromisoformat(str(client["birth_date"]))
            repo.save(
                name=str(client["name"]),
                birth_date=birth_date,
                birth_time=client.get("birth_time"),
                gender=client.get("gender"),
                notes=client.get("notes"),
            )
            count += 1

        return count
    finally:
        conn.close()


def main() -> None:
    """シードデータ投入のエントリーポイント。"""
    parser = argparse.ArgumentParser(description="サンプル相談者データをDBに投入")
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help=f"DBファイルのパス（デフォルト: {DB_PATH}）",
    )
    parser.add_argument(
        "--data-file",
        type=Path,
        default=SAMPLE_CLIENTS_FILE,
        help=f"サンプルデータファイル（デフォルト: {SAMPLE_CLIENTS_FILE}）",
    )
    args = parser.parse_args()

    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("シードデータ投入を開始: %s", args.db_path)

    try:
        clients_data = load_sample_clients(args.data_file)
        count = seed_clients(args.db_path, clients_data)
        logger.info("シードデータ投入完了: %d 件の相談者を登録しました", count)
    except FileNotFoundError:
        logger.error("データファイルが見つかりません: %s", args.data_file)
        sys.exit(1)
    except (DatabaseError, ValueError, KeyError) as e:
        logger.error("シードデータ投入に失敗しました: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
