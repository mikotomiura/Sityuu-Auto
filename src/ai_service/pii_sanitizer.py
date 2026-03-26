"""PII匿名化モジュール。

LLM API送信前に相談者の個人情報（名前・フリガナ）を
プレースホルダに置換し、外部サービスへの個人情報流出を防止する。
"""

import logging

logger = logging.getLogger(__name__)

_ANONYMIZED_NAME = "相談者様"
_ANONYMIZED_NAME_KANA = ""


def sanitize_name(name: str) -> str:
    """相談者の名前を匿名化プレースホルダに置換する。

    Args:
        name: 相談者の名前。空文字の場合はそのまま返す。

    Returns:
        匿名化されたプレースホルダ文字列。
        空文字が渡された場合は空文字を返す。
    """
    if not name:
        return name
    return _ANONYMIZED_NAME


def sanitize_name_kana(name_kana: str) -> str:
    """相談者のフリガナを匿名化（空文字に置換）する。

    匿名化時はフリガナを削除し、音韻鑑定をスキップさせる。

    Args:
        name_kana: 相談者のフリガナ。空文字の場合はそのまま返す。

    Returns:
        空文字。元が空文字の場合も空文字を返す。
    """
    if not name_kana:
        return name_kana
    return _ANONYMIZED_NAME_KANA


def sanitize_for_prompt(
    name: str,
    name_kana: str,
) -> tuple[str, str]:
    """プロンプト送信用に名前・フリガナをまとめて匿名化する。

    Args:
        name: 相談者の名前。
        name_kana: 相談者のフリガナ。

    Returns:
        (匿名化された名前, 匿名化されたフリガナ) のタプル。
    """
    logger.debug("PII匿名化を適用")
    return sanitize_name(name), sanitize_name_kana(name_kana)
