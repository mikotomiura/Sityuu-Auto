"""プロンプト構築モジュール。

テンプレートファイルを読み込み、命式データと悩みテキストを埋め込んで
(system_prompt, user_prompt) のタプルを生成する。
"""

import logging
from pathlib import Path
from string import Template

logger = logging.getLogger(__name__)

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def _load_template(filename: str) -> str:
    """テンプレートファイルを読み込む。

    Args:
        filename: テンプレートファイル名。

    Returns:
        テンプレート文字列。

    Raises:
        FileNotFoundError: テンプレートファイルが存在しない場合。
    """
    path = _TEMPLATES_DIR / filename
    return path.read_text(encoding="utf-8")


def build_reading_prompt(
    natal_chart_text: str,
    concern: str,
    custom_system_prompt: str | None = None,
) -> tuple[str, str]:
    """鑑定テキスト生成用のプロンプトを構築する。

    Args:
        natal_chart_text: AIプロンプト用に整形された命式テキスト。
        concern: 相談者の悩みテキスト。
        custom_system_prompt: DBから取得したカスタムシステムプロンプト。
            指定された場合はデフォルトのシステムプロンプトを置き換える。

    Returns:
        (system_prompt, user_prompt) のタプル。
        system_prompt にはロール定義・指示・出力フォーマットを含む。
        user_prompt には命式データと悩みを含む。
    """
    template_text = _load_template("reading_base.md")
    template = Template(template_text)

    if custom_system_prompt is not None:
        system_prompt = custom_system_prompt
    else:
        system_prompt = (
            "あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した鑑定師です。"
            "以下のユーザーメッセージに含まれる命式データと悩みをもとに、"
            "鑑定テキストのベースを作成してください。"
        )

    user_prompt = template.substitute(
        natal_chart_text=natal_chart_text,
        concern_text=concern,
    )

    return system_prompt, user_prompt


def build_listening_hint_prompt(
    natal_chart_text: str,
    concern: str,
    custom_system_prompt: str | None = None,
) -> tuple[str, str]:
    """傾聴ヒント生成用のプロンプトを構築する。

    Args:
        natal_chart_text: AIプロンプト用に整形された命式テキスト。
        concern: 相談者の悩みテキスト。
        custom_system_prompt: DBから取得したカスタムシステムプロンプト。
            指定された場合はデフォルトのシステムプロンプトを置き換える。

    Returns:
        (system_prompt, user_prompt) のタプル。
        system_prompt にはロール定義を含む。
        user_prompt には命式データと悩みを含む。
    """
    template_text = _load_template("listening_hint.md")
    template = Template(template_text)

    if custom_system_prompt is not None:
        system_prompt = custom_system_prompt
    else:
        system_prompt = (
            "あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した"
            "メンタリングの専門家です。"
            "以下のユーザーメッセージに含まれる命式データと悩みをもとに、"
            "傾聴のヒントを作成してください。"
        )

    user_prompt = template.substitute(
        natal_chart_text=natal_chart_text,
        concern_text=concern,
    )

    return system_prompt, user_prompt
