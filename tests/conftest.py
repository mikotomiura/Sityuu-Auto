"""テスト共通フィクスチャ。"""

from __future__ import annotations

import pytest

from fortune_engine.models import (
    FiveElement,
    NatalChart,
    Pillar,
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
