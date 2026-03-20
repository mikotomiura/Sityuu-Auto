"""ロギング設定のユニットテスト。"""

import logging

import pytest

import utils.logger as logger_module
from utils.logger import PrivacyFilter, setup_logging


class TestPrivacyFilter:
    """PrivacyFilter のテスト。"""

    @pytest.fixture()
    def privacy_filter(self) -> PrivacyFilter:
        """PrivacyFilter インスタンスを生成する。"""
        return PrivacyFilter()

    def test_mask_birth_date_hyphen(self, privacy_filter: PrivacyFilter) -> None:
        """ハイフン区切りの生年月日がマスキングされること。"""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="生年月日: 1990-05-15 のデータ", args=(), exc_info=None,
        )
        privacy_filter.filter(record)
        assert "1990-05-15" not in record.msg
        assert "****-**-**" in record.msg

    def test_mask_birth_date_slash(self, privacy_filter: PrivacyFilter) -> None:
        """スラッシュ区切りの生年月日がマスキングされること。"""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="生年月日: 1990/05/15 のデータ", args=(), exc_info=None,
        )
        privacy_filter.filter(record)
        assert "1990/05/15" not in record.msg
        assert "****-**-**" in record.msg

    def test_mask_email(self, privacy_filter: PrivacyFilter) -> None:
        """メールアドレスがマスキングされること。"""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="連絡先: user@example.com に送信", args=(), exc_info=None,
        )
        privacy_filter.filter(record)
        assert "user@example.com" not in record.msg
        assert "***@***.***" in record.msg

    def test_no_mask_for_safe_message(self, privacy_filter: PrivacyFilter) -> None:
        """個人情報を含まないメッセージは変更されないこと。"""
        original_msg = "命式算出を開始: client_id=abc-123"
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg=original_msg, args=(), exc_info=None,
        )
        privacy_filter.filter(record)
        assert record.msg == original_msg

    def test_mask_date_in_args(self, privacy_filter: PrivacyFilter) -> None:
        """record.args に渡された生年月日がマスキングされること。"""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="生年月日: %s", args=("1990-05-15",), exc_info=None,
        )
        privacy_filter.filter(record)
        assert "1990-05-15" not in record.msg
        assert "****-**-**" in record.msg
        assert record.args is None

    def test_filter_always_returns_true(self, privacy_filter: PrivacyFilter) -> None:
        """filter は常に True を返すこと（レコードを破棄しない）。"""
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="テスト", args=(), exc_info=None,
        )
        assert privacy_filter.filter(record) is True


def _get_app_handlers(root: logging.Logger) -> list[logging.Handler]:
    """pytest の LogCaptureHandler を除いたハンドラ一覧を返す。"""
    return [
        h for h in root.handlers
        if type(h).__name__ != "LogCaptureHandler"
    ]


class TestSetupLogging:
    """setup_logging のテスト。"""

    @pytest.fixture(autouse=True)
    def _reset_root_logger(self) -> None:
        """各テスト前にアプリ追加ハンドラを除去し setup_done をリセットする。"""
        root = logging.getLogger()
        original_level = root.level
        logger_module._setup_done = False
        # アプリが追加したハンドラだけ除去（pytest のハンドラは残す）
        for h in _get_app_handlers(root):
            root.removeHandler(h)
        yield
        for h in _get_app_handlers(root):
            root.removeHandler(h)
        root.setLevel(original_level)
        logger_module._setup_done = False

    def test_adds_console_handler(self) -> None:
        """コンソールハンドラが追加されること。"""
        setup_logging()
        root = logging.getLogger()
        app_handlers = _get_app_handlers(root)
        assert len(app_handlers) == 1
        assert isinstance(app_handlers[0], logging.StreamHandler)

    def test_skips_if_already_configured(self) -> None:
        """2回呼んでも重複追加しないこと。"""
        setup_logging()
        setup_logging()  # 2回目
        root = logging.getLogger()
        app_handlers = _get_app_handlers(root)
        assert len(app_handlers) == 1

    def test_sets_log_level(self) -> None:
        """指定したログレベルが設定されること。"""
        setup_logging(level=logging.DEBUG)
        root = logging.getLogger()
        assert root.level == logging.DEBUG

    def test_file_handler_with_log_to_file(self, tmp_path: "object") -> None:
        """log_to_file=True でファイルハンドラが追加されること。"""
        from pathlib import Path

        log_dir = Path(str(tmp_path)) / "logs"
        setup_logging(log_to_file=True, log_dir=log_dir)
        root = logging.getLogger()
        app_handlers = _get_app_handlers(root)
        assert len(app_handlers) == 2  # console + file

    def test_privacy_filter_applied(self) -> None:
        """PrivacyFilter がハンドラに適用されていること。"""
        setup_logging()
        root = logging.getLogger()
        app_handlers = _get_app_handlers(root)
        assert len(app_handlers) >= 1
        filter_types = [type(f) for f in app_handlers[0].filters]
        assert PrivacyFilter in filter_types
