"""命式計算エンジンのデータモデル定義。

四柱推命・算命学で使用するEnum型およびPydanticモデルを定義する。
用語はdocs/glossary.mdの英語表記に準拠する。
設計はdocs/fortune-engine-detail.md「3. データモデル（models.py）」に完全準拠する。
"""

from enum import StrEnum

from pydantic import BaseModel, Field

# ============================================================
# 基本 Enum
# ============================================================


class FiveElement(StrEnum):
    """五行（GoGyo）。木・火・土・金・水の5つの元素。"""

    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


class YinYang(StrEnum):
    """陰陽。十干の陰陽属性を表す。"""

    YANG = "陽"
    YIN = "陰"


class TenStem(StrEnum):
    """十干（Jikkan）。五行×陰陽で構成される10種の天干。"""

    KINOE = "甲"  # 木の陽
    KINOTO = "乙"  # 木の陰
    HINOE = "丙"  # 火の陽
    HINOTO = "丁"  # 火の陰
    TSUCHINOE = "戊"  # 土の陽
    TSUCHINOTO = "己"  # 土の陰
    KANOE = "庚"  # 金の陽
    KANOTO = "辛"  # 金の陰
    MIZUNOE = "壬"  # 水の陽
    MIZUNOTO = "癸"  # 水の陰


class TwelveBranch(StrEnum):
    """十二支（Junishi）。12種の地支。"""

    NE = "子"
    USHI = "丑"
    TORA = "寅"
    U = "卯"
    TATSU = "辰"
    MI = "巳"
    UMA = "午"
    HITSUJI = "未"
    SARU = "申"
    TORI = "酉"
    INU = "戌"
    INOSHISHI = "亥"  # 設計書では I だが ruff E741 回避のため INOSHISHI


class JudaiShusei(StrEnum):
    """十大主星（JudaiShusei）。算命学の星体系。

    各星は四柱推命の通変星（十神）と1対1で対応する。
    """

    KANSAKU = "貫索星"  # 守備本能・陽（= 比肩）
    SEKIMON = "石門星"  # 守備本能・陰（= 劫財）
    HOUKAKU = "鳳閣星"  # 伝達本能・陽（= 食神）
    CHOSHO = "調舒星"  # 伝達本能・陰（= 傷官）
    ROKUZON = "禄存星"  # 引力本能・陽（= 偏財）
    SHIROKU = "司禄星"  # 引力本能・陰（= 正財）
    SHAKI = "車騎星"  # 攻撃本能・陽（= 偏官）
    KENGYUU = "牽牛星"  # 攻撃本能・陰（= 正官）
    RYUUKOU = "龍高星"  # 習得本能・陽（= 偏印）
    GYOKUDOU = "玉堂星"  # 習得本能・陰（= 印綬）


class JuniDaiJusei(StrEnum):
    """十二大従星（JuniDaiJusei）。エネルギーの強弱を表す12種の星。

    各星は四柱推命の十二運と1対1で対応する。
    """

    TENPOU = "天報星"  # 胎  エネルギー3
    TENIN = "天印星"  # 養  エネルギー6
    TENKI = "天貴星"  # 長生 エネルギー9
    TENKOU = "天恍星"  # 沐浴 エネルギー7
    TENNAN = "天南星"  # 冠帯 エネルギー8
    TENROKU = "天禄星"  # 建禄 エネルギー11
    TENSHOU = "天将星"  # 帝旺 エネルギー12
    TENDOU = "天堂星"  # 衰  エネルギー10
    TENKOSEI = "天胡星"  # 病  エネルギー5
    TENGOKU = "天極星"  # 死  エネルギー2
    TENKUSEI = "天庫星"  # 墓  エネルギー4
    TENCHI = "天馳星"  # 絶  エネルギー1


class TenchusatsuGroup(StrEnum):
    """天中殺（Tenchusatsu）グループ。六十干支から決定される空亡の6種類。"""

    NE_USHI = "子丑天中殺"
    TORA_U = "寅卯天中殺"
    TATSU_MI = "辰巳天中殺"
    UMA_HITSUJI = "午未天中殺"
    SARU_TORI = "申酉天中殺"
    INU_I = "戌亥天中殺"


# ============================================================
# 構造化データモデル
# ============================================================


class Pillar(BaseModel):
    """四柱の1柱（年柱・月柱・日柱・時柱）。

    Attributes:
        stem: 天干（甲〜癸）。
        branch: 地支（子〜亥）。
        stem_element: 天干の五行。
        branch_element: 地支の五行。
        yinyang: 陰陽。
        ganshi: 干支文字列（例: '甲子'）。
        nayin: 納音（例: '海中金'）。
    """

    stem: str = Field(description="天干（甲〜癸）")
    branch: str = Field(description="地支（子〜亥）")
    stem_element: FiveElement = Field(description="天干の五行")
    branch_element: FiveElement = Field(description="地支の五行")
    yinyang: YinYang = Field(description="陰陽")
    ganshi: str = Field(description="干支（例: '甲子'）")
    nayin: str = Field(description="納音（例: '海中金'）")


class NatalChart(BaseModel):
    """四柱推命の命式（陰占）。

    生年月日・出生時間から算出される年柱・月柱・日柱・時柱で構成される。
    日干（day_stem）が命式の中心であり、最も重要な要素となる。

    Attributes:
        year_pillar: 年柱。
        month_pillar: 月柱。
        day_pillar: 日柱。
        hour_pillar: 時柱（出生時間不明時None）。
        day_stem: 日干（命式の中心）。
        day_stem_element: 日干の五行。
        five_elements_balance: 五行バランス。
        xun_kong: 旬空（空亡）— 日柱基準。
    """

    year_pillar: Pillar = Field(description="年柱")
    month_pillar: Pillar = Field(description="月柱")
    day_pillar: Pillar = Field(description="日柱")
    hour_pillar: Pillar | None = Field(default=None, description="時柱（出生時間不明時None）")
    day_stem: str = Field(description="日干（命式の中心）")
    day_stem_element: FiveElement = Field(description="日干の五行")
    five_elements_balance: dict[FiveElement, int] = Field(description="五行バランス")
    xun_kong: str = Field(description="旬空（空亡）— 日柱基準")


class HumanStarChart(BaseModel):
    """算命学の人体星図（陽占）。

    十大主星5箇所 + 伴星 + 十二大従星3箇所で構成される。

    Attributes:
        center_star: 中央の十大主星（胸）= 日干×月干。
        north_star: 北方の十大主星（頭）= 日干×年干。
        south_star: 南方の十大主星（腹）= 日干×日支蔵干。
        east_star: 東方の十大主星（左手）= 日干×月支蔵干。
        west_star: 西方の十大主星（右手）= 日干×年支蔵干。
        companion_star: 伴星 = 日干×年干と干合する干。
        north_twelve: 北方（左肩）の十二大従星 = 日干×年支。
        south_twelve: 南方（左足）の十二大従星 = 日干×日支。
        west_twelve: 西方（右足）の十二大従星 = 日干×月支。
    """

    center_star: JudaiShusei = Field(description="中央の十大主星（胸）= 日干×月干")
    north_star: JudaiShusei = Field(description="北方の十大主星（頭）= 日干×年干")
    south_star: JudaiShusei = Field(description="南方の十大主星（腹）= 日干×日支蔵干")
    east_star: JudaiShusei = Field(description="東方の十大主星（左手）= 日干×月支蔵干")
    west_star: JudaiShusei = Field(description="西方の十大主星（右手）= 日干×年支蔵干")
    companion_star: JudaiShusei = Field(description="伴星 = 日干×年干と干合する干")

    north_twelve: JuniDaiJusei = Field(description="北方（左肩）の十二大従星 = 日干×年支")
    south_twelve: JuniDaiJusei = Field(description="南方（左足）の十二大従星 = 日干×日支")
    west_twelve: JuniDaiJusei = Field(description="西方（右足）の十二大従星 = 日干×月支")


class SanmeiData(BaseModel):
    """算命学の総合データ。

    Attributes:
        human_star_chart: 人体星図。
        tenchusatsu: 天中殺グループ。
        total_energy: 十二大従星のエネルギー合計（3〜36）。
    """

    human_star_chart: HumanStarChart = Field(description="人体星図")
    tenchusatsu: TenchusatsuGroup = Field(description="天中殺グループ")
    total_energy: int = Field(description="十二大従星のエネルギー合計（3〜36）")


class FortuneResult(BaseModel):
    """命式算出の最終結果（UI層に返すデータ）。

    四柱推命の命式と算命学データを統合し、
    AI鑑定テキスト生成への入力データとなる。

    Attributes:
        natal_chart: 四柱推命の命式。
        sanmei_data: 算命学データ。
    """

    natal_chart: NatalChart = Field(description="四柱推命の命式")
    sanmei_data: SanmeiData = Field(description="算命学データ")
