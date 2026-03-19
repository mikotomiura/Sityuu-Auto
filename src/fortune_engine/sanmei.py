"""算命学データ算出モジュール。

命式（NatalChart）から十大主星・十二大従星・天中殺・エネルギーを算出し、
SanmeiData オブジェクトとして返す。
設計は docs/fortune-engine-detail.md「5.3 sanmei.py の処理詳細」に完全準拠する。
"""

from __future__ import annotations

import logging

from fortune_engine.constants import (
    JUDAI_TABLE,
    JUNIDAI_ENERGY,
    JUNIUNSEI_TO_JUNIDAI,
    KANGO_PAIR,
    TWELVE_PHASES_TABLE,
    XUNKONG_TO_TENCHUSATSU,
    ZOUKAN_HONKI,
)
from fortune_engine.models import (
    HumanStarChart,
    JudaiShusei,
    JuniDaiJusei,
    NatalChart,
    SanmeiData,
)
from utils.exceptions import FortuneCalculationError

logger = logging.getLogger(__name__)


def calculate_sanmei_data(natal_chart: NatalChart) -> SanmeiData:
    """命式から算命学データを算出する。

    四柱推命の命式（NatalChart）を入力として、算命学の人体星図（十大主星5箇所
    + 伴星 + 十二大従星3箇所）、天中殺グループ、エネルギー合計を算出する。

    Args:
        natal_chart: 四柱推命の命式。

    Returns:
        算出された算命学データ（SanmeiData）。

    Raises:
        FortuneCalculationError: 算命学データの算出に失敗した場合。
    """
    logger.info("算命学データの算出を開始します")

    try:
        day_stem = natal_chart.day_stem
        year_stem = natal_chart.year_pillar.stem
        month_stem = natal_chart.month_pillar.stem
        year_branch = natal_chart.year_pillar.branch
        month_branch = natal_chart.month_pillar.branch
        day_branch = natal_chart.day_pillar.branch

        # --- 十大主星（人体星図5箇所 + 伴星）---
        center = _lookup_judai(day_stem, month_stem)  # 中央（胸）
        north = _lookup_judai(day_stem, year_stem)  # 北方（頭）
        south = _lookup_judai(day_stem, ZOUKAN_HONKI[day_branch])  # 南方（腹）
        east = _lookup_judai(day_stem, ZOUKAN_HONKI[month_branch])  # 東方（左手）
        west = _lookup_judai(day_stem, ZOUKAN_HONKI[year_branch])  # 西方（右手）

        # 伴星: 年干と干合する干を求め、日干との関係から算出
        kango_stem = KANGO_PAIR[year_stem]
        companion = _lookup_judai(day_stem, kango_stem)

        # --- 十二大従星（3箇所）---
        north_twelve = _lookup_junidai(day_stem, year_branch)  # 北方（左肩）
        south_twelve = _lookup_junidai(day_stem, day_branch)  # 南方（左足）
        west_twelve = _lookup_junidai(day_stem, month_branch)  # 西方（右足）

        # --- 天中殺 ---
        tenchusatsu = XUNKONG_TO_TENCHUSATSU[natal_chart.xun_kong]

        # --- エネルギー ---
        total_energy = sum(
            JUNIDAI_ENERGY[s] for s in [north_twelve, south_twelve, west_twelve]
        )

        human_chart = HumanStarChart(
            center_star=center,
            north_star=north,
            south_star=south,
            east_star=east,
            west_star=west,
            companion_star=companion,
            north_twelve=north_twelve,
            south_twelve=south_twelve,
            west_twelve=west_twelve,
        )

    except FortuneCalculationError:
        raise
    except (KeyError, ValueError, TypeError, AttributeError) as exc:
        logger.error(
            "算命学データ算出中にエラーが発生しました: %s", type(exc).__name__
        )
        msg = "算命学データの算出に失敗しました"
        raise FortuneCalculationError(msg) from exc

    logger.info("算命学データの算出が完了しました")

    return SanmeiData(
        human_star_chart=human_chart,
        tenchusatsu=tenchusatsu,
        total_energy=total_energy,
    )


def _lookup_judai(day_stem: str, target_stem: str) -> JudaiShusei:
    """日干と対象干から十大主星を引く。

    JUDAI_TABLE（日干×相手干→十大主星名）を参照し、
    対応する JudaiShusei 列挙値を返す。

    Args:
        day_stem: 日干（甲〜癸）。
        target_stem: 対象干（甲〜癸）。

    Returns:
        対応する十大主星。
    """
    star_name = JUDAI_TABLE[day_stem][target_stem]
    return JudaiShusei(star_name)


def _lookup_junidai(day_stem: str, branch: str) -> JuniDaiJusei:
    """日干と地支から十二大従星を引く。

    TWELVE_PHASES_TABLE で十二運を求め、JUNIUNSEI_TO_JUNIDAI で
    十二大従星に変換する2段階ルックアップ。

    Args:
        day_stem: 日干（甲〜癸）。
        branch: 地支（子〜亥）。

    Returns:
        対応する十二大従星。
    """
    phase = TWELVE_PHASES_TABLE[day_stem][branch]
    return JUNIUNSEI_TO_JUNIDAI[phase]
