"""命式算出フルフロー統合テスト。

calculate_fortune → format_for_ai_prompt / format_for_display の
一連のパイプラインが正しく動作することを検証する。
"""

from __future__ import annotations

from datetime import date, time

from fortune_engine import (
    calculate_fortune,
    format_for_ai_prompt,
    format_for_display,
    format_human_star_chart_grid,
)
from fortune_engine.models import (
    FortuneResult,
    JudaiShusei,
    JuniDaiJusei,
)


class TestFullFortuneCalculationFlow:
    """calculate_fortune のフルフロー検証。"""

    def test_full_fortune_calculation_flow(self) -> None:
        """calculate_fortune が FortuneResult を返し、全フィールドが設定されていること。"""
        result = calculate_fortune(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        assert isinstance(result, FortuneResult)
        assert result.natal_chart is not None
        assert result.sanmei_data is not None

        # 人体星図の十大主星5箇所 + 伴星がすべて設定されていること
        hsc = result.sanmei_data.human_star_chart
        assert isinstance(hsc.center_star, JudaiShusei)
        assert isinstance(hsc.north_star, JudaiShusei)
        assert isinstance(hsc.south_star, JudaiShusei)
        assert isinstance(hsc.east_star, JudaiShusei)
        assert isinstance(hsc.west_star, JudaiShusei)
        assert isinstance(hsc.companion_star, JudaiShusei)

        # 十二大従星3箇所がすべて設定されていること
        assert isinstance(hsc.north_twelve, JuniDaiJusei)
        assert isinstance(hsc.south_twelve, JuniDaiJusei)
        assert isinstance(hsc.west_twelve, JuniDaiJusei)


class TestFormatForAiPrompt:
    """format_for_ai_prompt の統合検証。"""

    def test_fortune_result_can_be_formatted_for_ai(self) -> None:
        """format_for_ai_prompt が空でない文字列を返し、主要キーワードが含まれること。"""
        result = calculate_fortune(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        text = format_for_ai_prompt(result)

        assert isinstance(text, str)
        assert len(text) > 0
        assert "日干" in text
        assert "天中殺" in text
        assert "四柱推命" in text
        assert "算命学" in text
        assert "エネルギー合計" in text


class TestFormatForDisplay:
    """format_for_display の統合検証。"""

    def test_fortune_result_can_be_formatted_for_display(self) -> None:
        """format_for_display が必要なキーを持つ辞書を返すこと。"""
        result = calculate_fortune(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        display = format_for_display(result)

        assert isinstance(display, dict)
        assert "pillars" in display
        assert "human_star_chart" in display
        assert "tenchusatsu" in display
        assert "total_energy" in display
        assert "five_elements_balance" in display

        # pillars が list[dict] であること
        assert isinstance(display["pillars"], list)
        assert len(display["pillars"]) >= 3


class TestFortuneWithoutBirthTime:
    """出生時間なしのフロー検証。"""

    def test_fortune_without_birth_time(self) -> None:
        """出生時間なしでもエラーなく算出でき、hour_pillar が None であること。"""
        result = calculate_fortune(
            birth_date=date(1985, 12, 15),
            birth_time=None,
        )

        assert isinstance(result, FortuneResult)
        assert result.natal_chart.hour_pillar is None

        # フォーマッタも問題なく動作すること
        text = format_for_ai_prompt(result)
        assert "時柱: 不明" in text

        display = format_for_display(result)
        assert len(display["pillars"]) == 3  # 年柱・月柱・日柱のみ

        grid = format_human_star_chart_grid(result.sanmei_data.human_star_chart)
        assert len(grid) > 0


class TestMultipleDatesProduceDifferentResults:
    """異なる生年月日での算出結果の差異検証。"""

    def test_multiple_different_dates_produce_different_results(self) -> None:
        """異なる生年月日で異なる命式が算出されること。"""
        result_a = calculate_fortune(birth_date=date(1990, 5, 15))
        result_b = calculate_fortune(birth_date=date(2000, 1, 1))

        # 日柱の干支が異なること（同じ日付でない限り異なる）
        assert result_a.natal_chart.day_pillar.ganshi != result_b.natal_chart.day_pillar.ganshi
