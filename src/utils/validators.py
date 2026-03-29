"""入力バリデーション関数。

相談者情報やAPI設定の入力値を検証する共通関数を提供する。
各関数は検証に失敗した場合、エラーメッセージ文字列を返す。
成功時は None を返す。
"""

import re
from datetime import date

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --- 定数 ---
CLIENT_NAME_MIN_LENGTH = 1
CLIENT_NAME_MAX_LENGTH = 50
CONCERN_MIN_LENGTH = 10
CONCERN_MAX_LENGTH = 2000
BIRTH_DATE_MIN = date(1900, 1, 1)


def validate_client_name(name: str) -> str | None:
    """相談者名を検証する。

    Args:
        name: 相談者の名前。

    Returns:
        検証エラー時はエラーメッセージ。成功時は None。
    """
    stripped = name.strip()
    if len(stripped) < CLIENT_NAME_MIN_LENGTH:
        return "お名前を入力してください。"
    if len(stripped) > CLIENT_NAME_MAX_LENGTH:
        return f"お名前は{CLIENT_NAME_MAX_LENGTH}文字以内で入力してください。"
    return None


def validate_birth_date(birth_date: date | None) -> str | None:
    """生年月日を検証する。

    Args:
        birth_date: 相談者の生年月日。未入力の場合は None。

    Returns:
        検証エラー時はエラーメッセージ。成功時は None。
    """
    if birth_date is None:
        return "生年月日を入力してください。"
    if birth_date < BIRTH_DATE_MIN:
        return f"生年月日は{BIRTH_DATE_MIN.isoformat()}以降を指定してください。"
    if birth_date > date.today():
        return "未来の日付は指定できません。"
    return None


def validate_concern(concern: str) -> str | None:
    """悩みテキストを検証する。

    Args:
        concern: 相談者の悩みテキスト。

    Returns:
        検証エラー時はエラーメッセージ。成功時は None。
    """
    stripped = concern.strip()
    if len(stripped) < CONCERN_MIN_LENGTH:
        return f"悩みは{CONCERN_MIN_LENGTH}文字以上入力してください。"
    if len(stripped) > CONCERN_MAX_LENGTH:
        return f"悩みは{CONCERN_MAX_LENGTH}文字以内で入力してください。"
    return None


def validate_api_key(api_key: str | None, provider: str) -> str | None:
    """APIキーを検証する。

    フォーマットの基本的なチェックのみ行う。実際の認証確認は行わない。

    Args:
        api_key: APIキー文字列。
        provider: APIプロバイダー名。

    Returns:
        検証エラー時はエラーメッセージ。成功時は None。
    """
    if not api_key or not api_key.strip():
        return f"{provider} のAPIキーが設定されていません。"

    stripped = api_key.strip()

    # プロバイダー別プレフィックスチェック
    prefix_map: dict[str, str] = {
        "openai": "sk-",
        "anthropic": "sk-ant-",
    }

    expected_prefix = prefix_map.get(provider)
    if expected_prefix and not stripped.startswith(expected_prefix):
        return f"{provider} のAPIキーの形式が正しくありません。"

    return None


def is_valid_email(email: str) -> bool:
    """メールアドレスの形式が有効かを判定する。

    Args:
        email: メールアドレス文字列。

    Returns:
        有効な形式なら True。
    """
    return bool(_EMAIL_PATTERN.match(email.strip()))
