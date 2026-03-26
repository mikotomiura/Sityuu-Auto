"""プロンプト構築モジュール。

テンプレートファイルを読み込み、命式データと悩みテキストを埋め込んで
(system_prompt, user_prompt) のタプルを生成する。
"""

import logging
from pathlib import Path
from string import Template

from ai_service.pii_sanitizer import sanitize_for_prompt

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
    name: str = "",
    name_kana: str = "",
    custom_system_prompt: str | None = None,
    anonymize: bool = True,
) -> tuple[str, str]:
    """鑑定テキスト生成用のプロンプトを構築する。

    Args:
        natal_chart_text: AIプロンプト用に整形された命式テキスト。
        concern: 相談者の悩みテキスト。
        name: 相談者の名前。ハイブリッド鑑定（名前×命式）に使用。
        name_kana: 相談者のフリガナ。音韻鑑定に使用。
        custom_system_prompt: DBから取得したカスタムシステムプロンプト。
            指定された場合はデフォルトのシステムプロンプトを置き換える。
        anonymize: Trueの場合、名前・フリガナを匿名化してからAPIに送信する。

    Returns:
        (system_prompt, user_prompt) のタプル。
        system_prompt にはロール定義・指示・出力フォーマットを含む。
        user_prompt には命式データ・名前・悩みを含む。
    """
    template_text = _load_template("reading_base.md")
    template = Template(template_text)

    if anonymize:
        name, name_kana = sanitize_for_prompt(name, name_kana)

    if custom_system_prompt is not None:
        system_prompt = custom_system_prompt
    else:
        system_prompt = (
            "あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した鑑定師です。"
            "また、漢字の持つ意味や音の響き（言霊）を読み解く総合鑑定師でもあります。"
            "以下のユーザーメッセージに含まれる命式データ・名前・悩みをもとに、"
            "鑑定テキストのベースを作成してください。"
            "画数に基づく姓名判断は行わないでください。"
        )

    user_prompt = template.substitute(
        natal_chart_text=natal_chart_text,
        concern_text=concern,
        name=name or "（未入力）",
        name_kana=name_kana or "（未入力）",
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
