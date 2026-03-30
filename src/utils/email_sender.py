"""メール送信ユーティリティ — パスワードリセットリンクのメール配信。

SMTP設定が.envに存在する場合のみメール送信が有効になる。
未設定時はセルフリセット機能を無効化する。
"""

import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import (
    SMTP_DEFAULT_PORT,
    SMTP_FROM_ENV,
    SMTP_HOST_ENV,
    SMTP_PASSWORD_ENV,
    SMTP_PORT_ENV,
    SMTP_USER_ENV,
)

logger = logging.getLogger(__name__)


def is_smtp_configured() -> bool:
    """SMTP設定が有効かどうかを判定する。

    Returns:
        SMTP_HOSTとSMTP_FROMが設定されている場合にTrue。
    """
    return bool(os.environ.get(SMTP_HOST_ENV)) and bool(os.environ.get(SMTP_FROM_ENV))


def send_password_reset_email(to_email: str, reset_url: str, username: str) -> bool:
    """パスワードリセットリンクをメールで送信する。

    Args:
        to_email: 送信先メールアドレス。
        reset_url: リセットリンクURL。
        username: 対象ユーザーのユーザー名（メール本文に表示）。

    Returns:
        送信成功なら True。送信失敗時は False を返しログに記録する。
    """
    subject = "【Sityuu-Auto】パスワード再設定のご案内"
    body_text = (
        f"{username} 様\n\n"
        "パスワードの再設定リクエストを受け付けました。\n"
        "以下のリンクから新しいパスワードを設定してください。\n\n"
        f"  {reset_url}\n\n"
        "このリンクの有効期限は24時間です。\n"
        "心当たりがない場合は、このメールを無視してください。\n\n"
        "---\n"
        "Sityuu-Auto — 占い・メンタリング支援システム\n"
    )

    return _send_email(to_email, subject, body_text, log_label="パスワードリセットメール")


def send_account_deleted_email(to_email: str, username: str) -> bool:
    """アカウント削除通知メールを送信する。

    管理者によるアカウント削除時に、ユーザーのメールアドレスに通知する。

    Args:
        to_email: 送信先メールアドレス。
        username: 削除されたユーザーのユーザー名（メール本文に表示）。

    Returns:
        送信成功なら True。
    """
    subject = "【Sityuu-Auto】アカウント削除のお知らせ"
    body_text = (
        f"{username} 様\n\n"
        "管理者により、あなたのアカウントが削除されました。\n\n"
        "今後、このアカウントでのログインはできなくなります。\n\n"
        "ご不明な点がございましたら、以下の問い合わせフォームよりご連絡ください。\n"
        "https://docs.google.com/forms/d/1nB63bWYSztx_hrHolJpbE2Y6xKGVTjjxDpiDZ4ZmTTc/viewform\n\n"
        "---\n"
        "Sityuu-Auto — 占い・メンタリング支援システム\n"
    )

    return _send_email(to_email, subject, body_text, log_label="アカウント削除通知メール")


def _send_email(to_email: str, subject: str, body_text: str, log_label: str) -> bool:
    """��通メール送信処理。

    Args:
        to_email: 送信先メールアドレス。
        subject: メール件名。
        body_text: メール本文（プレーンテキスト）。
        log_label: ログ出力用のラベル。

    Returns:
        送信成功なら True。送信失敗時は False を返しログに記録する。
    """
    host = os.environ.get(SMTP_HOST_ENV, "")
    port = int(os.environ.get(SMTP_PORT_ENV, str(SMTP_DEFAULT_PORT)))
    user = os.environ.get(SMTP_USER_ENV, "")
    password = os.environ.get(SMTP_PASSWORD_ENV, "")
    from_addr = os.environ.get(SMTP_FROM_ENV, "")

    if not host or not from_addr:
        logger.error("SMTP設定が不完全です")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    try:
        with smtplib.SMTP(host, port, timeout=10) as server:
            server.ehlo()
            if port != 25:
                server.starttls()
                server.ehlo()
            if user and password:
                server.login(user, password)
            server.sendmail(from_addr, [to_email], msg.as_string())
        # SECURITY: メールアドレスをマスクしてログ出力（個人情報保護）
        masked = to_email[:2] + "***@***"
        logger.info("%sを送信: to=%s", log_label, masked)
        return True
    except (smtplib.SMTPException, OSError) as e:
        logger.error("%s送信失敗: %s", log_label, e)
        return False
