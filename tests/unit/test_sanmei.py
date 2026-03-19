"""算命学データ算出（sanmei.py）のユニットテスト。

calculate_sanmei_data 関数の正常系・異常系テストを行う。
テストデータは Phase 2 照合済みの既知命式（1990-05-15 10:30）を使用する。
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from fortune_engine.constants import (
    JUDAI_TABLE,
    JUNIDAI_ENERGY,
    KANGO_PAIR,
)
from fortune_engine.models import (
    JudaiShusei,
    NatalChart,
    SanmeiData,
    TenchusatsuGroup,
)
from fortune_engine.sanmei import calculate_sanmei_data
from utils.exceptions import FortuneCalculationError


class TestCalculateSanmeiData:
    """calculate_sanmei_data の正常系テスト。"""

    def test_calculate_sanmei_returns_sanmei_data(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """SanmeiData が正しく返ること。"""
        result = calculate_sanmei_data(sample_natal_chart)

        assert isinstance(result, SanmeiData)
        assert result.human_star_chart is not None
        assert result.tenchusatsu is not None
        assert result.total_energy > 0

    def test_center_star_is_day_stem_x_month_stem(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """中央星が日干×月干の JUDAI_TABLE ルックアップと一致すること。"""
        result = calculate_sanmei_data(sample_natal_chart)

        day_stem = sample_natal_chart.day_stem
        month_stem = sample_natal_chart.month_pillar.stem
        expected = JudaiShusei(JUDAI_TABLE[day_stem][month_stem])

        assert result.human_star_chart.center_star == expected

    def test_north_star_is_day_stem_x_year_stem(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """北方星が日干×年干のルックアップと一致すること。"""
        result = calculate_sanmei_data(sample_natal_chart)

        day_stem = sample_natal_chart.day_stem
        year_stem = sample_natal_chart.year_pillar.stem
        expected = JudaiShusei(JUDAI_TABLE[day_stem][year_stem])

        assert result.human_star_chart.north_star == expected

    def test_tenchusatsu_is_valid_group(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """天中殺が6グループのいずれかであること。"""
        result = calculate_sanmei_data(sample_natal_chart)

        assert result.tenchusatsu in list(TenchusatsuGroup)

    def test_total_energy_in_valid_range(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """エネルギー合計が3（最小: 1+1+1）〜36（最大: 12+12+12）の範囲内。"""
        result = calculate_sanmei_data(sample_natal_chart)

        assert 3 <= result.total_energy <= 36

    def test_total_energy_equals_sum_of_three_twelve_stars(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """エネルギー合計が3つの十二大従星のエネルギー値の合計と一致。"""
        result = calculate_sanmei_data(sample_natal_chart)

        chart = result.human_star_chart
        expected_energy = sum(
            JUNIDAI_ENERGY[s]
            for s in [chart.north_twelve, chart.south_twelve, chart.west_twelve]
        )

        assert result.total_energy == expected_energy

    def test_companion_star_uses_kango_pair(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """伴星が KANGO_PAIR[年干] を使って正しく算出されていること。"""
        result = calculate_sanmei_data(sample_natal_chart)

        day_stem = sample_natal_chart.day_stem
        year_stem = sample_natal_chart.year_pillar.stem
        kango_stem = KANGO_PAIR[year_stem]
        expected = JudaiShusei(JUDAI_TABLE[day_stem][kango_stem])

        assert result.human_star_chart.companion_star == expected


class TestCalculateSanmeiDataError:
    """calculate_sanmei_data の異常系テスト。"""

    def test_raises_fortune_calculation_error_on_key_error(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """KeyError が FortuneCalculationError にラップされること。"""
        with (
            patch.dict(
                "fortune_engine.sanmei.ZOUKAN_HONKI",
                clear=True,
            ),
            pytest.raises(FortuneCalculationError, match="算命学データの算出に失敗しました"),
        ):
            calculate_sanmei_data(sample_natal_chart)

    def test_reraises_fortune_calculation_error_as_is(
        self,
        sample_natal_chart: NatalChart,
    ) -> None:
        """FortuneCalculationError はそのまま再raiseされること。"""
        with (
            patch(
                "fortune_engine.sanmei.XUNKONG_TO_TENCHUSATSU",
                new={"dummy": TenchusatsuGroup.NE_USHI},
            ),
            pytest.raises(FortuneCalculationError),
        ):
            calculate_sanmei_data(sample_natal_chart)
