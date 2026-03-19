"""四柱推命の命式算出モジュール。

lunar_python を利用して生年月日から四柱（年柱・月柱・日柱・時柱）を算出し、
NatalChart オブジェクトとして返す。
設計は docs/fortune-engine-detail.md「5.2 calculator.py の処理詳細」に完全準拠する。
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import date, time

from lunar_python import Solar
from lunar_python.util import LunarUtil

from fortune_engine.constants import (
    BRANCH_TO_ELEMENT,
    STEM_TO_ELEMENT,
    STEM_TO_YINYANG,
)
from fortune_engine.models import FiveElement, NatalChart, Pillar
from utils.exceptions import FortuneCalculationError

logger = logging.getLogger(__name__)


def calculate_natal_chart(
    birth_date: date,
    birth_time: time | None = None,
) -> NatalChart:
    """四柱推命の命式を算出する。

    Args:
        birth_date: 生年月日。lunar_python の対応範囲（西暦1〜9999年）内であること。
        birth_time: 出生時間。不明の場合は None。

    Returns:
        算出された命式（NatalChart）。

    Raises:
        FortuneCalculationError: 命式算出に失敗した場合（日付範囲外を含む）。
    """
    logger.info("命式算出を開始します")

    if birth_date.year < 1 or birth_date.year > 9999:
        msg = "対応範囲外の年が指定されました"
        raise FortuneCalculationError(msg)

    try:
        # 1. Solar オブジェクトを生成
        if birth_time:
            solar = Solar.fromYmdHms(
                birth_date.year,
                birth_date.month,
                birth_date.day,
                birth_time.hour,
                birth_time.minute,
                0,
            )
        else:
            solar = Solar.fromYmd(
                birth_date.year,
                birth_date.month,
                birth_date.day,
            )

        # 2. Lunar（太陰暦）に変換
        lunar = solar.getLunar()

        # 3. EightChar（八字）を取得
        eight_char = lunar.getEightChar()

        # 4. 各柱を構築
        year_pillar = _build_pillar(
            eight_char.getYearGan(),
            eight_char.getYearZhi(),
            eight_char.getYear(),
        )
        month_pillar = _build_pillar(
            eight_char.getMonthGan(),
            eight_char.getMonthZhi(),
            eight_char.getMonth(),
        )
        day_pillar = _build_pillar(
            eight_char.getDayGan(),
            eight_char.getDayZhi(),
            eight_char.getDay(),
        )

        hour_pillar = None
        if birth_time:
            hour_pillar = _build_pillar(
                eight_char.getTimeGan(),
                eight_char.getTimeZhi(),
                eight_char.getTime(),
            )

        # 5. 日干
        day_stem = eight_char.getDayGan()

        # 6. 五行バランス集計
        pillars = [year_pillar, month_pillar, day_pillar]
        if hour_pillar:
            pillars.append(hour_pillar)
        balance = _count_five_elements(pillars)

        # 7. 旬空（空亡）
        # 四柱推命では「旬空（xun_kong）」、算命学では「天中殺（tenchusatsu）」と呼ぶ。
        # ここでは lunar_python の API 名に合わせて xun_kong を使用する。
        # 算命学の天中殺グループへの変換は sanmei.py で行う。
        xun_kong = eight_char.getDayXunKong()

    except FortuneCalculationError:
        raise
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        logger.error("命式算出中にエラーが発生しました: %s", type(exc).__name__)
        msg = "命式の算出に失敗しました"
        raise FortuneCalculationError(msg) from exc

    logger.info("命式算出が完了しました")

    return NatalChart(
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_stem=day_stem,
        day_stem_element=STEM_TO_ELEMENT[day_stem],
        five_elements_balance=balance,
        xun_kong=xun_kong,
    )


def _build_pillar(stem: str, branch: str, ganshi: str) -> Pillar:
    """天干・地支から Pillar オブジェクトを構築する。

    Args:
        stem: 天干の文字列（例: "甲"）。
        branch: 地支の文字列（例: "子"）。
        ganshi: 干支の文字列（例: "甲子"）。

    Returns:
        構築された Pillar オブジェクト。

    Raises:
        KeyError: 未定義の天干・地支が渡された場合。
    """
    nayin: str = LunarUtil.NAYIN.get(ganshi, "")

    return Pillar(
        stem=stem,
        branch=branch,
        stem_element=STEM_TO_ELEMENT[stem],
        branch_element=BRANCH_TO_ELEMENT[branch],
        yinyang=STEM_TO_YINYANG[stem],
        ganshi=ganshi,
        nayin=nayin,
    )


def _count_five_elements(pillars: list[Pillar]) -> dict[FiveElement, int]:
    """柱のリストから天干の五行をカウントする。

    設計書の仕様に基づき、天干（stem_element）のみを集計対象とする。
    地支の五行は含めない。

    Args:
        pillars: 柱のリスト（年柱・月柱・日柱、時柱がある場合は4つ）。

    Returns:
        五行ごとの天干出現回数。全五行を含む（カウント0の要素も含む）。
    """
    counter: Counter[FiveElement] = Counter()
    for pillar in pillars:
        counter[pillar.stem_element] += 1

    return {element: counter[element] for element in FiveElement}
