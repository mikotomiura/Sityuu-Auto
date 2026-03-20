"""テスト共通フィクスチャ。"""

from __future__ import annotations

import pytest

from fortune_engine.models import (
    FiveElement,
    FortuneResult,
    HumanStarChart,
    JudaiShusei,
    JuniDaiJusei,
    NatalChart,
    Pillar,
    SanmeiData,
    TenchusatsuGroup,
    YinYang,
)


@pytest.fixture()
def sample_natal_chart() -> NatalChart:
    """Phase 2 照合済み既知データ（1990-05-15 10:30）から構築した NatalChart。

    命式:
        年柱: 庚午  月柱: 辛巳  日柱: 庚辰  時柱: 辛巳
        日干: 庚    旬空: 申酉
    """
    return NatalChart(
        year_pillar=Pillar(
            stem="庚",
            branch="午",
            stem_element=FiveElement.METAL,
            branch_element=FiveElement.FIRE,
            yinyang=YinYang.YANG,
            ganshi="庚午",
            nayin="路傍土",
        ),
        month_pillar=Pillar(
            stem="辛",
            branch="巳",
            stem_element=FiveElement.METAL,
            branch_element=FiveElement.FIRE,
            yinyang=YinYang.YIN,
            ganshi="辛巳",
            nayin="白蝋金",
        ),
        day_pillar=Pillar(
            stem="庚",
            branch="辰",
            stem_element=FiveElement.METAL,
            branch_element=FiveElement.EARTH,
            yinyang=YinYang.YANG,
            ganshi="庚辰",
            nayin="白蝋金",
        ),
        hour_pillar=Pillar(
            stem="辛",
            branch="巳",
            stem_element=FiveElement.METAL,
            branch_element=FiveElement.FIRE,
            yinyang=YinYang.YIN,
            ganshi="辛巳",
            nayin="白蝋金",
        ),
        day_stem="庚",
        day_stem_element=FiveElement.METAL,
        five_elements_balance={
            FiveElement.WOOD: 0,
            FiveElement.FIRE: 0,
            FiveElement.EARTH: 0,
            FiveElement.METAL: 4,
            FiveElement.WATER: 0,
        },
        xun_kong="申酉",
    )


@pytest.fixture()
def sample_sanmei_data() -> SanmeiData:
    """テスト用の算命学データ。"""
    return SanmeiData(
        human_star_chart=HumanStarChart(
            center_star=JudaiShusei.KANSAKU,
            north_star=JudaiShusei.KANSAKU,
            south_star=JudaiShusei.SHIROKU,
            east_star=JudaiShusei.SHAKI,
            west_star=JudaiShusei.HOUKAKU,
            companion_star=JudaiShusei.SEKIMON,
            north_twelve=JuniDaiJusei.TENPOU,
            south_twelve=JuniDaiJusei.TENROKU,
            west_twelve=JuniDaiJusei.TENSHOU,
        ),
        tenchusatsu=TenchusatsuGroup.SARU_TORI,
        total_energy=26,
    )


@pytest.fixture()
def sample_fortune_result(
    sample_natal_chart: NatalChart,
    sample_sanmei_data: SanmeiData,
) -> FortuneResult:
    """テスト用の命式算出結果。"""
    return FortuneResult(
        natal_chart=sample_natal_chart,
        sanmei_data=sample_sanmei_data,
    )
