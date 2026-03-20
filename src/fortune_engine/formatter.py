"""命式データのテキスト/表フォーマッタ。

AIプロンプトに埋め込む命式テキストと、UI表示用のフォーマットを提供する。
設計はdocs/fortune-engine-detail.md「7. formatter.py」に準拠する。
"""

import unicodedata
from typing import Any

from fortune_engine.constants import JUNIDAI_ENERGY
from fortune_engine.models import (
    FortuneResult,
    HumanStarChart,
    Pillar,
)


def format_for_ai_prompt(result: FortuneResult) -> str:
    """FortuneResultをAIプロンプトに埋め込むテキストに変換する。

    四柱推命命式 + 算命学人体星図 + 天中殺 + エネルギーを含む
    整形テキストを返す。設計書7.1のフォーマットに完全準拠。

    Args:
        result: 命式算出の最終結果。

    Returns:
        AIプロンプトに埋め込むための整形テキスト。
    """
    nc = result.natal_chart
    sd = result.sanmei_data
    hsc = sd.human_star_chart

    lines = [
        "【四柱推命 命式】",
        f"  日干: {nc.day_stem}（{nc.day_stem_element.value}）",
        f"  年柱: {nc.year_pillar.ganshi}",
        f"  月柱: {nc.month_pillar.ganshi}",
        f"  日柱: {nc.day_pillar.ganshi}",
    ]
    if nc.hour_pillar:
        lines.append(f"  時柱: {nc.hour_pillar.ganshi}")
    else:
        lines.append("  時柱: 不明")

    balance_str = " ".join(f"{e.value}:{c}" for e, c in nc.five_elements_balance.items())
    lines.append(f"  五行バランス: {balance_str}")

    lines.extend(
        [
            "",
            "【算命学 人体星図】",
            f"  中央（胸）: {hsc.center_star.value}",
            f"  北方（頭）: {hsc.north_star.value}  / {hsc.north_twelve.value}",
            f"  南方（腹）: {hsc.south_star.value}  / {hsc.south_twelve.value}",
            f"  東方（左手）: {hsc.east_star.value}",
            f"  西方（右手）: {hsc.west_star.value}  / {hsc.west_twelve.value}",
            f"  伴星: {hsc.companion_star.value}",
            f"  天中殺: {sd.tenchusatsu.value}",
            f"  エネルギー合計: {sd.total_energy}",
        ]
    )

    return "\n".join(lines)


def format_for_display(result: FortuneResult) -> dict[str, Any]:
    """FortuneResultをUI表示用の辞書データに変換する。

    Streamlitのst.table()等で直接使えるデータ構造を返す。

    Args:
        result: 命式算出の最終結果。

    Returns:
        以下のキーを持つ辞書:
            - pillars: 四柱の一覧（list[dict]）。各要素は柱名・干支・天干・地支・五行・陰陽を含む。
            - human_star_chart: 人体星図の辞書（位置→星名）。
            - tenchusatsu: 天中殺グループ名。
            - total_energy: エネルギー合計値。
            - five_elements_balance: 五行バランス（dict[str, int]）。
    """
    nc = result.natal_chart
    sd = result.sanmei_data
    hsc = sd.human_star_chart

    pillars: list[dict[str, str]] = []
    pillar_entries: list[tuple[str, Pillar]] = [
        ("年柱", nc.year_pillar),
        ("月柱", nc.month_pillar),
        ("日柱", nc.day_pillar),
    ]
    if nc.hour_pillar:
        pillar_entries.append(("時柱", nc.hour_pillar))

    for name, pillar in pillar_entries:
        pillars.append(
            {
                "柱": name,
                "干支": pillar.ganshi,
                "天干": pillar.stem,
                "地支": pillar.branch,
                "五行（天干）": pillar.stem_element.value,
                "五行（地支）": pillar.branch_element.value,
                "陰陽": pillar.yinyang.value,
                "納音": pillar.nayin,
            }
        )

    human_star_chart: dict[str, str] = {
        "中央（胸）": hsc.center_star.value,
        "北方（頭）": hsc.north_star.value,
        "南方（腹）": hsc.south_star.value,
        "東方（左手）": hsc.east_star.value,
        "西方（右手）": hsc.west_star.value,
        "伴星": hsc.companion_star.value,
        "北方（左肩）従星": f"{hsc.north_twelve.value}（{JUNIDAI_ENERGY[hsc.north_twelve]}）",
        "南方（左足）従星": f"{hsc.south_twelve.value}（{JUNIDAI_ENERGY[hsc.south_twelve]}）",
        "西方（右足）従星": f"{hsc.west_twelve.value}（{JUNIDAI_ENERGY[hsc.west_twelve]}）",
    }

    five_elements_balance: dict[str, int] = {
        e.value: c for e, c in nc.five_elements_balance.items()
    }

    return {
        "pillars": pillars,
        "human_star_chart": human_star_chart,
        "tenchusatsu": sd.tenchusatsu.value,
        "total_energy": sd.total_energy,
        "five_elements_balance": five_elements_balance,
    }


def format_human_star_chart_grid(chart: HumanStarChart) -> str:
    """人体星図をテキストのグリッド形式で表現する。

    算命学の人体星図を視覚的に分かりやすい2次元グリッドとして整形する。
    十大主星5箇所と十二大従星3箇所を人体配置に対応させて表示する。

    Args:
        chart: 算命学の人体星図データ。

    Returns:
        以下のレイアウトで整形されたテキスト::

                     [北方: 龍高星]
                          [天貴星]
            [東方: 車騎星]  [中央: 貫索星]  [西方: 禄存星]
                          [南方: 鳳閣星]
            [天恍星]                      [天禄星]
    """
    north = f"[北方: {chart.north_star.value}]"
    north_tw = f"[{chart.north_twelve.value}]"
    east = f"[東方: {chart.east_star.value}]"
    center = f"[中央: {chart.center_star.value}]"
    west = f"[西方: {chart.west_star.value}]"
    south = f"[南方: {chart.south_star.value}]"
    south_tw = f"[{chart.south_twelve.value}]"
    west_tw = f"[{chart.west_twelve.value}]"

    # 各列の幅を計算して整列する
    east_width = max(_display_width(east), _display_width(south_tw))
    center_width = max(
        _display_width(north),
        _display_width(north_tw),
        _display_width(center),
        _display_width(south),
    )

    def _pad_center(text: str, width: int) -> str:
        """テキストを指定幅で中央寄せする（全角文字対応）。"""
        text_w = _display_width(text)
        if text_w >= width:
            return text
        left = (width - text_w) // 2
        right = width - text_w - left
        return " " * left + text + " " * right

    def _pad_right(text: str, width: int) -> str:
        """テキストを指定幅で左寄せ・右パディングする（全角文字対応）。"""
        text_w = _display_width(text)
        if text_w >= width:
            return text
        return text + " " * (width - text_w)

    # 行1: 北方（十大主星）— 中央列に配置
    row1 = " " * east_width + "  " + _pad_center(north, center_width)
    # 行2: 北方（十二大従星）— 中央列に配置
    row2 = " " * east_width + "  " + _pad_center(north_tw, center_width)
    # 行3: 東方 / 中央 / 西方
    row3 = _pad_right(east, east_width) + "  " + _pad_center(center, center_width) + "  " + west
    # 行4: 南方（十大主星）— 中央列に配置
    row4 = " " * east_width + "  " + _pad_center(south, center_width)
    # 行5: 南方従星（左） / 西方従星（右）
    row5 = _pad_right(south_tw, east_width) + "  " + " " * center_width + "  " + west_tw

    return "\n".join(line.rstrip() for line in [row1, row2, row3, row4, row5])


def _display_width(text: str) -> int:
    """テキストの表示幅を算出する（全角=2, 半角=1）。

    Args:
        text: 表示幅を算出するテキスト。

    Returns:
        表示幅（半角換算）。
    """
    width = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        if eaw in ("F", "W"):
            width += 2
        else:
            width += 1
    return width
