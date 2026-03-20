"""ロギング設定モジュール。

アプリケーション全体の統一的なロギング設定を提供する。
個人情報マスキングフィルタにより、ログへの個人情報漏洩を防止する。

Usage::

    from utils.logger import setup_logging

    # アプリ起動時に1度だけ呼び出す
    setup_logging()

    # 各モジュールでは従来通り
    import logging
    logger = logging.getLogger(__name__)
"""

import logging
import re
from pathlib import Path

# --- 定数 ---
DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = logging.INFO
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_FILE_NAME = "app.log"
MAX_LOG_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 3

# 個人情報パターン（生年月日・メールアドレス）
_setup_done = False

_DATE_PATTERN = re.compile(r"\b(19|20)\d{2}[-/](0[1-9]|1[0-2])[-/](0[1-9]|[12]\d|3[01])\b")
_EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


class PrivacyFilter(logging.Filter):
    """個人情報マスキングフィルタ。

    ログメッセージ内の生年月日パターンやメールアドレスを
    マスク文字列に置換する。
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """ログレコードの個人情報をマスキングする。

        ``record.args`` を展開した最終メッセージに対してマスキングを行い、
        展開済みテキストを ``record.msg`` に設定、``record.args`` を空にする。

        Args:
            record: ログレコード。

        Returns:
            常に True（レコードは破棄しない）。
        """
        message = record.getMessage()
        message = _DATE_PATTERN.sub("****-**-**", message)
        message = _EMAIL_PATTERN.sub("***@***.***", message)
        record.msg = message
        record.args = None
        return True


def setup_logging(
    level: int = DEFAULT_LOG_LEVEL,
    log_to_file: bool = False,
    log_dir: Path = LOG_DIR,
) -> None:
    """アプリケーション全体のロギングを設定する。

    ルートロガーに統一フォーマットのハンドラを追加する。
    個人情報マスキングフィルタを自動的に適用する。

    Args:
        level: ログレベル（デフォルト: INFO）。
        log_to_file: True の場合、ファイルへのログ出力も有効化する。
        log_dir: ログファイルの出力先ディレクトリ。
    """
    global _setup_done  # noqa: PLW0603
    if _setup_done:
        return
    _setup_done = True

    root_logger = logging.getLogger()

    root_logger.setLevel(level)
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, datefmt=DEFAULT_DATE_FORMAT)
    privacy_filter = PrivacyFilter()

    # コンソールハンドラ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(privacy_filter)
    root_logger.addHandler(console_handler)

    # ファイルハンドラ（オプション）
    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / LOG_FILE_NAME

        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=MAX_LOG_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        file_handler.addFilter(privacy_filter)
        root_logger.addHandler(file_handler)
