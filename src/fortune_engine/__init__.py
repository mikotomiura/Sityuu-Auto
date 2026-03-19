"""命式計算エンジン。

四柱推命・算命学の命式算出とフォーマットを提供する公開API。

Usage:
    from fortune_engine import calculate_fortune, format_for_ai_prompt
    result = calculate_fortune(birth_date=date(1990, 5, 15), birth_time=time(10, 30))
    prompt_text = format_for_ai_prompt(result)
"""

from __future__ import annotations

from datetime import date, time

from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.formatter import (
    format_for_ai_prompt,
    format_for_display,
    format_human_star_chart_grid,
)
from fortune_engine.models import FortuneResult, HumanStarChart
from fortune_engine.sanmei import calculate_sanmei_data
from utils.exceptions import FortuneCalculationError

__all__ = [
    "FortuneCalculationError",
    "FortuneResult",
    "HumanStarChart",
    "calculate_fortune",
    "format_for_ai_prompt",
    "format_for_display",
    "format_human_star_chart_grid",
]


def calculate_fortune(
    birth_date: date,
    birth_time: time | None = None,
) -> FortuneResult:
    """命式を算出する統合関数（UI層から呼び出すエントリーポイント）。

    生年月日（+ 出生時間）から四柱推命の命式と算命学データを算出し、
    FortuneResult として返す。

    Args:
        birth_date: 相談者の生年月日。
        birth_time: 出生時間。不明の場合はNone。

    Returns:
        四柱推命の命式と算命学データを統合した結果。

    Raises:
        FortuneCalculationError: 命式の算出に失敗した場合。
    """
    natal_chart = calculate_natal_chart(birth_date, birth_time)
    sanmei_data = calculate_sanmei_data(natal_chart)
    return FortuneResult(natal_chart=natal_chart, sanmei_data=sanmei_data)
