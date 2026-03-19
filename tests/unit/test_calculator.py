"""命式算出（calculator.py）のユニットテスト。

calculate_natal_chart 関数の正常系・境界値・異常系をテストする。
テスト設計は .claude/skills/test-standards/examples.md の命式算出テスト例に準拠する。
"""

from __future__ import annotations

import functools
import json
from datetime import date, time
from pathlib import Path
from unittest.mock import patch

import pytest

from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.constants import BRANCH_TO_ELEMENT, STEM_TO_ELEMENT
from fortune_engine.models import FiveElement, NatalChart
from utils.exceptions import FortuneCalculationError

FIXTURES_DIR: Path = Path(__file__).resolve().parent.parent / "fixtures"

VALID_STEMS: set[str] = set(STEM_TO_ELEMENT.keys())
VALID_BRANCHES: set[str] = set(BRANCH_TO_ELEMENT.keys())
VALID_XUN_KONG: set[str] = {"子丑", "寅卯", "辰巳", "午未", "申酉", "戌亥"}


class TestCalculateNatalChartNormal:
    """calculate_natal_chart 正常系テスト。"""

    def test_calculate_with_valid_date_returns_natal_chart(self) -> None:
        """正常な日付で NatalChart が返ること。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        assert isinstance(result, NatalChart)
        assert result.day_stem is not None
        assert result.year_pillar is not None
        assert result.month_pillar is not None
        assert result.day_pillar is not None

    def test_calculate_with_birth_time_has_hour_pillar(self) -> None:
        """出生時間ありの場合、hour_pillar が設定されていること。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        assert result.hour_pillar is not None
        assert result.hour_pillar.stem in VALID_STEMS
        assert result.hour_pillar.branch in VALID_BRANCHES

    def test_calculate_without_birth_time_has_no_hour_pillar(self) -> None:
        """出生時間なしの場合、hour_pillar が None であること。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=None,
        )

        assert result.hour_pillar is None

    def test_day_stem_is_valid_stem(self) -> None:
        """day_stem が十干のいずれかであること。"""
        result = calculate_natal_chart(birth_date=date(1990, 5, 15))

        assert result.day_stem in VALID_STEMS

    def test_five_elements_balance_sum_equals_pillar_count(self) -> None:
        """五行バランスの合計値が柱の数（4）と一致すること（出生時間あり）。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        total = sum(result.five_elements_balance.values())
        assert total == 4

    def test_five_elements_balance_sum_equals_three_without_hour(self) -> None:
        """五行バランスの合計値が柱の数（3）と一致すること（出生時間なし）。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=None,
        )

        total = sum(result.five_elements_balance.values())
        assert total == 3

    def test_five_elements_balance_contains_all_elements(self) -> None:
        """五行バランスに全五行が含まれること。"""
        result = calculate_natal_chart(birth_date=date(1990, 5, 15))

        for element in FiveElement:
            assert element in result.five_elements_balance

    def test_xun_kong_is_valid_two_char_branch(self) -> None:
        """xun_kong が2文字の地支の組み合わせであること。"""
        result = calculate_natal_chart(birth_date=date(1990, 5, 15))

        assert result.xun_kong in VALID_XUN_KONG

    def test_pillar_has_nayin(self) -> None:
        """柱に納音が設定されていること。"""
        result = calculate_natal_chart(birth_date=date(1990, 5, 15))

        assert result.year_pillar.nayin != ""
        assert result.day_pillar.nayin != ""


class TestCalculateNatalChartBoundary:
    """calculate_natal_chart 境界値テスト。"""

    def test_calculate_with_earliest_date(self) -> None:
        """最古の対応日付（1900-01-01）で算出できること。"""
        result = calculate_natal_chart(birth_date=date(1900, 1, 1))

        assert isinstance(result, NatalChart)
        assert result.day_stem in VALID_STEMS

    def test_calculate_with_today_date(self) -> None:
        """今日の日付で算出できること。"""
        result = calculate_natal_chart(birth_date=date.today())

        assert isinstance(result, NatalChart)
        assert result.day_stem in VALID_STEMS


class TestCalculateNatalChartError:
    """calculate_natal_chart 異常系テスト。"""

    def test_calculate_raises_error_for_invalid_date(self) -> None:
        """lunar_python が処理できない入力で FortuneCalculationError が発生すること。"""
        with (
            patch(
                "fortune_engine.calculator.Solar.fromYmd",
                side_effect=ValueError("invalid date"),
            ),
            pytest.raises(FortuneCalculationError),
        ):
            calculate_natal_chart(birth_date=date(1990, 5, 15))

    def test_calculate_raises_error_when_lunar_conversion_fails(self) -> None:
        """Lunar 変換失敗時に FortuneCalculationError が発生すること。"""
        with (
            patch(
                "fortune_engine.calculator.Solar.fromYmd",
            ) as mock_solar,
            pytest.raises(FortuneCalculationError),
        ):
            mock_solar.return_value.getLunar.side_effect = AttributeError("conversion failed")
            calculate_natal_chart(birth_date=date(1990, 5, 15))


@functools.cache
def _load_fixture_data() -> dict[str, dict[str, str | None]]:
    """フィクスチャJSONを読み込み、case_id → expected のマップを返す。

    Raises:
        FileNotFoundError: フィクスチャファイルが見つからない場合。
        ValueError: JSONの解析に失敗した場合。
    """
    path = FIXTURES_DIR / "expected_natal_charts.json"
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        msg = f"フィクスチャファイルが見つかりません: {path}"
        raise FileNotFoundError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"フィクスチャJSONの解析に失敗しました: {path}"
        raise ValueError(msg) from exc
    return {case["id"]: case["expected"] for case in data["test_cases"]}


def _load_expected(case_id: str) -> dict[str, str | None]:
    """テストフィクスチャから指定ケースの期待値を読み込む。

    Args:
        case_id: テストケースID（例: "1985-12-15"）。

    Returns:
        期待値の辞書。

    Raises:
        ValueError: 指定IDのテストケースが見つからない場合。
    """
    fixtures = _load_fixture_data()
    if case_id not in fixtures:
        msg = f"テストケース '{case_id}' が見つかりません"
        raise ValueError(msg)
    return fixtures[case_id]


class TestKnownNatalCharts:
    """既知の命式データとの照合テスト。

    tests/fixtures/expected_natal_charts.json の期待値と算出結果を照合する。
    """

    def test_known_chart_1985_12_15(self) -> None:
        """1985年12月15日（出生時間なし）の年柱・月柱・日柱が期待値と一致すること。"""
        expected = _load_expected("1985-12-15")
        result = calculate_natal_chart(birth_date=date(1985, 12, 15), birth_time=None)

        assert result.day_stem == expected["day_stem"]
        assert result.year_pillar.ganshi == expected["year_pillar_ganshi"]
        assert result.month_pillar.ganshi == expected["month_pillar_ganshi"]
        assert result.day_pillar.ganshi == expected["day_pillar_ganshi"]
        assert result.hour_pillar is None
        assert result.xun_kong == expected["xun_kong"]

    def test_known_chart_1990_05_15(self) -> None:
        """1990年5月15日 10:30 の全4柱が期待値と一致すること。"""
        expected = _load_expected("1990-05-15")
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        assert result.day_stem == expected["day_stem"]
        assert result.year_pillar.ganshi == expected["year_pillar_ganshi"]
        assert result.month_pillar.ganshi == expected["month_pillar_ganshi"]
        assert result.day_pillar.ganshi == expected["day_pillar_ganshi"]
        assert result.hour_pillar is not None
        assert result.hour_pillar.ganshi == expected["hour_pillar_ganshi"]
        assert result.xun_kong == expected["xun_kong"]

    def test_known_chart_2000_01_01(self) -> None:
        """2000年1月1日 0:00 の全4柱が期待値と一致すること。"""
        expected = _load_expected("2000-01-01")
        result = calculate_natal_chart(
            birth_date=date(2000, 1, 1),
            birth_time=time(0, 0),
        )

        assert result.day_stem == expected["day_stem"]
        assert result.year_pillar.ganshi == expected["year_pillar_ganshi"]
        assert result.month_pillar.ganshi == expected["month_pillar_ganshi"]
        assert result.day_pillar.ganshi == expected["day_pillar_ganshi"]
        assert result.hour_pillar is not None
        assert result.hour_pillar.ganshi == expected["hour_pillar_ganshi"]
        assert result.xun_kong == expected["xun_kong"]
