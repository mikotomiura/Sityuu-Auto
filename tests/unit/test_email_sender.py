"""utils/email_sender モジュールのユニットテスト。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from utils.email_sender import is_smtp_configured, send_password_reset_email


class TestIsSmtpConfigured:
    """is_smtp_configured のテスト。"""

    def test_returns_true_when_configured(self) -> None:
        """SMTP_HOSTとSMTP_FROMが設定されている場合にTrueを返すこと。"""
        with patch.dict(
            "os.environ",
            {"SMTP_HOST": "smtp.example.com", "SMTP_FROM": "noreply@example.com"},
        ):
            assert is_smtp_configured() is True

    def test_returns_false_when_host_missing(self) -> None:
        """SMTP_HOSTが未設定の場合にFalseを返すこと。"""
        with patch.dict("os.environ", {"SMTP_FROM": "noreply@example.com"}, clear=True):
            assert is_smtp_configured() is False

    def test_returns_false_when_from_missing(self) -> None:
        """SMTP_FROMが未設定の場合にFalseを返すこと。"""
        with patch.dict("os.environ", {"SMTP_HOST": "smtp.example.com"}, clear=True):
            assert is_smtp_configured() is False

    def test_returns_false_when_both_missing(self) -> None:
        """両方未設定の場合にFalseを返すこと。"""
        with patch.dict("os.environ", {}, clear=True):
            assert is_smtp_configured() is False


class TestSendPasswordResetEmail:
    """send_password_reset_email のテスト。"""

    def test_returns_false_when_smtp_not_configured(self) -> None:
        """SMTP未設定の場合にFalseを返すこと。"""
        with patch.dict("os.environ", {}, clear=True):
            result = send_password_reset_email(
                to_email="test@example.com",
                reset_url="http://localhost:8501/?reset_token=abc",
                username="testuser",
            )
            assert result is False

    @patch("utils.email_sender.smtplib.SMTP")
    def test_sends_email_successfully(self, mock_smtp_class: MagicMock) -> None:
        """メールが正常に送信されること。"""
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "user",
            "SMTP_PASSWORD": "pass",
            "SMTP_FROM": "noreply@example.com",
        }
        with patch.dict("os.environ", env):
            result = send_password_reset_email(
                to_email="test@example.com",
                reset_url="http://localhost:8501/?reset_token=abc",
                username="testuser",
            )
            assert result is True
            mock_server.sendmail.assert_called_once()

    @patch("utils.email_sender.smtplib.SMTP")
    def test_returns_false_on_smtp_error(self, mock_smtp_class: MagicMock) -> None:
        """SMTP送信エラー時にFalseを返すこと。"""
        import smtplib

        mock_smtp_class.side_effect = smtplib.SMTPException("Connection failed")

        env = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_FROM": "noreply@example.com",
        }
        with patch.dict("os.environ", env):
            result = send_password_reset_email(
                to_email="test@example.com",
                reset_url="http://localhost:8501/?reset_token=abc",
                username="testuser",
            )
            assert result is False
