"""定数テーブルの整合性テスト。

constants.py に定義された全定数テーブルが、
設計書（fortune-engine-detail.md）の仕様を満たしていることを検証する。
"""

from fortune_engine.constants import (
    BRANCH_TO_ELEMENT,
    JUDAI_TABLE,
    JUNIDAI_ENERGY,
    JUNIUNSEI_TO_JUNIDAI,
    KANGO_PAIR,
    STEM_TO_ELEMENT,
    STEM_TO_YINYANG,
    TWELVE_PHASES_TABLE,
    XUNKONG_TO_TENCHUSATSU,
    ZOUKAN_HONKI,
)
from fortune_engine.models import JudaiShusei, JuniDaiJusei, TenchusatsuGroup

STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


class TestJudaiTable:
    """JUDAI_TABLE（日干×相手干→十大主星）の整合性テスト。"""

    def test_judai_table_has_all_100_combinations(self) -> None:
        """十大主星表が10干×10干=100組すべてを網羅していること。"""
        for day in STEMS:
            assert day in JUDAI_TABLE, f"日干 '{day}' が JUDAI_TABLE に存在しない"
            for target in STEMS:
                assert target in JUDAI_TABLE[day], f"JUDAI_TABLE['{day}']['{target}'] が存在しない"

    def test_judai_table_values_are_valid_judai_names(self) -> None:
        """JUDAI_TABLE の全値が十大主星の有効な名前であること。"""
        valid_names = {star.value for star in JudaiShusei}
        for day in STEMS:
            for target in STEMS:
                value = JUDAI_TABLE[day][target]
                assert value in valid_names, (
                    f"JUDAI_TABLE['{day}']['{target}'] = '{value}' は有効な十大主星名ではない"
                )


class TestTwelvePhasesTable:
    """TWELVE_PHASES_TABLE（日干×地支→十二運）の整合性テスト。"""

    def test_twelve_phases_table_has_all_120_combinations(self) -> None:
        """十二運テーブルが10干×12支=120組すべてを網羅していること。"""
        for stem in STEMS:
            assert stem in TWELVE_PHASES_TABLE, f"日干 '{stem}' が TWELVE_PHASES_TABLE に存在しない"
            for branch in BRANCHES:
                assert branch in TWELVE_PHASES_TABLE[stem], (
                    f"TWELVE_PHASES_TABLE['{stem}']['{branch}'] が存在しない"
                )

    def test_twelve_phases_table_values_are_valid_phases(self) -> None:
        """十二運テーブルの全値がJUNIUNSEI_TO_JUNIDAIのキーに含まれること。"""
        valid_phases = set(JUNIUNSEI_TO_JUNIDAI.keys())
        for stem in STEMS:
            for branch in BRANCHES:
                value = TWELVE_PHASES_TABLE[stem][branch]
                assert value in valid_phases, (
                    f"TWELVE_PHASES_TABLE['{stem}']['{branch}'] = '{value}' は"
                    f"有効な十二運名ではない"
                )


class TestStemMappings:
    """十干関連テーブルの整合性テスト。"""

    def test_stem_to_element_covers_all_stems(self) -> None:
        """STEM_TO_ELEMENT が十干10種すべてをカバーしていること。"""
        for stem in STEMS:
            assert stem in STEM_TO_ELEMENT, f"十干 '{stem}' が STEM_TO_ELEMENT に存在しない"

    def test_stem_to_yinyang_covers_all_stems(self) -> None:
        """STEM_TO_YINYANG が十干10種すべてをカバーしていること。"""
        for stem in STEMS:
            assert stem in STEM_TO_YINYANG, f"十干 '{stem}' が STEM_TO_YINYANG に存在しない"


class TestBranchMappings:
    """十二支関連テーブルの整合性テスト。"""

    def test_branch_to_element_covers_all_branches(self) -> None:
        """BRANCH_TO_ELEMENT が十二支12種すべてをカバーしていること。"""
        for branch in BRANCHES:
            assert branch in BRANCH_TO_ELEMENT, (
                f"十二支 '{branch}' が BRANCH_TO_ELEMENT に存在しない"
            )

    def test_zoukan_honki_covers_all_branches(self) -> None:
        """ZOUKAN_HONKI が十二支12種すべてをカバーしていること。"""
        for branch in BRANCHES:
            assert branch in ZOUKAN_HONKI, f"十二支 '{branch}' が ZOUKAN_HONKI に存在しない"

    def test_zoukan_honki_values_are_valid_stems(self) -> None:
        """ZOUKAN_HONKI の全値が有効な十干であること。"""
        for branch in BRANCHES:
            value = ZOUKAN_HONKI[branch]
            assert value in STEMS, f"ZOUKAN_HONKI['{branch}'] = '{value}' は有効な十干ではない"


class TestTenchusatsu:
    """天中殺関連テーブルの整合性テスト。"""

    def test_xunkong_to_tenchusatsu_covers_all_groups(self) -> None:
        """XUNKONG_TO_TENCHUSATSU が天中殺6グループすべてをカバーしていること。"""
        all_groups = {group for group in TenchusatsuGroup}
        mapped_groups = set(XUNKONG_TO_TENCHUSATSU.values())
        assert all_groups == mapped_groups, (
            f"未カバーの天中殺グループ: {all_groups - mapped_groups}"
        )


class TestKangoPair:
    """干合テーブルの整合性テスト。"""

    def test_kango_pair_is_symmetric(self) -> None:
        """干合テーブルが対称であること（AのペアがBなら、BのペアがA）。"""
        for stem_a, stem_b in KANGO_PAIR.items():
            assert stem_b in KANGO_PAIR, (
                f"KANGO_PAIR['{stem_a}'] = '{stem_b}' だが'{stem_b}' が KANGO_PAIR に存在しない"
            )
            assert KANGO_PAIR[stem_b] == stem_a, (
                f"KANGO_PAIR['{stem_a}'] = '{stem_b}' だが"
                f"KANGO_PAIR['{stem_b}'] = '{KANGO_PAIR[stem_b]}'（非対称）"
            )

    def test_kango_pair_covers_all_stems(self) -> None:
        """干合テーブルが十干10種すべてをカバーしていること。"""
        for stem in STEMS:
            assert stem in KANGO_PAIR, f"十干 '{stem}' が KANGO_PAIR に存在しない"


class TestJuniDaiEnergy:
    """十二大従星エネルギーテーブルの整合性テスト。"""

    def test_junidai_energy_values_are_in_range(self) -> None:
        """エネルギー値が1〜12の範囲内であること。"""
        for star, energy in JUNIDAI_ENERGY.items():
            assert 1 <= energy <= 12, f"JUNIDAI_ENERGY[{star.value}] = {energy} は範囲外（1〜12）"

    def test_junidai_energy_covers_all_stars(self) -> None:
        """JUNIDAI_ENERGY が十二大従星12種すべてをカバーしていること。"""
        all_stars = {star for star in JuniDaiJusei}
        mapped_stars = set(JUNIDAI_ENERGY.keys())
        assert all_stars == mapped_stars, f"未カバーの十二大従星: {all_stars - mapped_stars}"

    def test_junidai_energy_values_are_unique(self) -> None:
        """エネルギー値が全て一意であること（1〜12の各値が1回ずつ）。"""
        values = list(JUNIDAI_ENERGY.values())
        assert sorted(values) == list(range(1, 13)), (
            f"エネルギー値が1〜12の完全な集合ではない: {sorted(values)}"
        )
