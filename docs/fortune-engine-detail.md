# 命式計算エンジン 詳細設計書

`src/fortune_engine/` — プロジェクトのコアモジュール

---

## 1. 設計概要

### 1.1 目的

生年月日（+ 出生時間）から以下を算出する：

1. **四柱推命の命式**（年柱・月柱・日柱・時柱の干支）
2. **算命学の陽占データ**（十大主星5つ + 十二大従星3つ + 天中殺）
3. **五行バランス**（木火土金水の分布）

### 1.2 核心的な設計判断

**`lunar_python` のEightCharクラスが既に通変星（十神）と十二運を算出可能。**
四柱推命の通変星と算命学の十大主星は同一の算出ロジック（日干と他干の五行関係）に基づいている。
よって、`lunar_python` の出力を算命学の用語体系にマッピングすることで、算出ロジックの自作を最小限にできる。

| 四柱推命の用語 | 算命学の用語 | lunar_python のAPI |
|--------------|------------|-------------------|
| 通変星（十神） | 十大主星 | `eightChar.getXxxShiShenGan()` |
| 十二運 | 十二大従星 | `Lunar` の十二長生から算出 |
| 空亡 | 天中殺 | `eightChar.getDayXunKong()` |

---

## 2. モジュール構成

```
src/fortune_engine/
├── __init__.py           # 公開API（calculate_fortune を export）
├── calculator.py         # 【主要】四柱推命の命式算出（lunar_python 利用）
├── sanmei.py             # 【主要】算命学データ算出（通変星→十大主星マッピング）
├── models.py             # Pydantic データモデル定義
├── constants.py          # 全定数テーブル（干支・五行・星の対応表）
└── formatter.py          # 命式データのテキスト/表フォーマッタ
```

---

## 3. データモデル（models.py）

```python
"""命式計算エンジンのデータモデル定義。"""

from enum import StrEnum  # Python 3.11+: str, Enum → StrEnum（ruff UP042）
from pydantic import BaseModel, Field


# ============================================================
# 基本 Enum
# ============================================================

class FiveElement(StrEnum):
    """五行。"""
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


class YinYang(StrEnum):
    """陰陽。"""
    YANG = "陽"
    YIN = "陰"


class TenStem(StrEnum):
    """十干。"""
    KINOE = "甲"    # 木の陽
    KINOTO = "乙"   # 木の陰
    HINOE = "丙"    # 火の陽
    HINOTO = "丁"   # 火の陰
    TSUCHINOE = "戊" # 土の陽
    TSUCHINOTO = "己" # 土の陰
    KANOE = "庚"    # 金の陽
    KANOTO = "辛"   # 金の陰
    MIZUNOE = "壬"  # 水の陽
    MIZUNOTO = "癸" # 水の陰


class TwelveBranch(StrEnum):
    """十二支。"""
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
    INOSHISHI = "亥"  # ruff E741 回避: I → INOSHISHI


class JudaiShusei(StrEnum):
    """十大主星（算命学）。"""
    KANSAKU = "貫索星"   # 守備本能・陽（= 比肩）
    SEKIMON = "石門星"   # 守備本能・陰（= 劫財）
    HOUKAKU = "鳳閣星"   # 伝達本能・陽（= 食神）
    CHOSHO = "調舒星"    # 伝達本能・陰（= 傷官）
    ROKUZON = "禄存星"   # 引力本能・陽（= 偏財）
    SHIROKU = "司禄星"   # 引力本能・陰（= 正財）
    SHAKI = "車騎星"     # 攻撃本能・陽（= 偏官）
    KENGYUU = "牽牛星"   # 攻撃本能・陰（= 正官）
    RYUUKOU = "龍高星"   # 習得本能・陽（= 偏印）
    GYOKUDOU = "玉堂星"  # 習得本能・陰（= 印綬）


class JuniDaiJusei(StrEnum):
    """十二大従星（算命学）。"""
    TENPOU = "天報星"     # 胎（= 胎）  エネルギー3
    TENIN = "天印星"      # 養（= 養）  エネルギー6
    TENKI = "天貴星"      # 長生（= 長生）エネルギー9
    TENKOU = "天恍星"     # 沐浴（= 沐浴）エネルギー7
    TENNAN = "天南星"     # 冠帯（= 冠帯）エネルギー8
    TENROKU = "天禄星"    # 建禄（= 建禄）エネルギー11
    TENSHOU = "天将星"    # 帝旺（= 帝旺）エネルギー12
    TENDOU = "天堂星"     # 衰（= 衰）  エネルギー10
    TENKOSEI = "天胡星"   # 病（= 病）  エネルギー5  ※旧名 TENKO → 天庫星と区別
    TENGOKU = "天極星"    # 死（= 死）  エネルギー2
    TENKUSEI = "天庫星"   # 墓（= 墓）  エネルギー4  ※旧名 TENKO2 → 天胡星と区別
    TENCHI = "天馳星"     # 絶（= 絶）  エネルギー1


class TenchusatsuGroup(StrEnum):
    """天中殺グループ（6種類）。"""
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
    """四柱の1柱（年柱・月柱・日柱・時柱）。"""
    stem: str = Field(description="天干（甲〜癸）")
    branch: str = Field(description="地支（子〜亥）")
    stem_element: FiveElement = Field(description="天干の五行")
    branch_element: FiveElement = Field(description="地支の五行")
    yinyang: YinYang = Field(description="陰陽")
    ganshi: str = Field(description="干支（例: '甲子'）")
    nayin: str = Field(description="納音（例: '海中金'）")


class NatalChart(BaseModel):
    """四柱推命の命式（陰占）。"""
    year_pillar: Pillar = Field(description="年柱")
    month_pillar: Pillar = Field(description="月柱")
    day_pillar: Pillar = Field(description="日柱")
    hour_pillar: Pillar | None = Field(default=None, description="時柱（出生時間不明時None）")
    day_stem: str = Field(description="日干（命式の中心）")
    day_stem_element: FiveElement = Field(description="日干の五行")
    five_elements_balance: dict[FiveElement, int] = Field(description="五行バランス")
    xun_kong: str = Field(description="旬空（空亡）— 日柱基準")


class HumanStarChart(BaseModel):
    """算命学の人体星図（陽占）。"""
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
    """算命学の総合データ。"""
    human_star_chart: HumanStarChart = Field(description="人体星図")
    tenchusatsu: TenchusatsuGroup = Field(description="天中殺グループ")
    total_energy: int = Field(description="十二大従星のエネルギー合計（3〜36）")


class FortuneResult(BaseModel):
    """命式算出の最終結果（UI層に返すデータ）。"""
    natal_chart: NatalChart = Field(description="四柱推命の命式")
    sanmei_data: SanmeiData = Field(description="算命学データ")
```

---

## 4. 定数テーブル（constants.py）

### 4.1 十干→五行・陰陽マッピング

```python
STEM_TO_ELEMENT: dict[str, FiveElement] = {
    "甲": FiveElement.WOOD,  "乙": FiveElement.WOOD,
    "丙": FiveElement.FIRE,  "丁": FiveElement.FIRE,
    "戊": FiveElement.EARTH, "己": FiveElement.EARTH,
    "庚": FiveElement.METAL, "辛": FiveElement.METAL,
    "壬": FiveElement.WATER, "癸": FiveElement.WATER,
}

STEM_TO_YINYANG: dict[str, YinYang] = {
    "甲": YinYang.YANG, "乙": YinYang.YIN,
    "丙": YinYang.YANG, "丁": YinYang.YIN,
    "戊": YinYang.YANG, "己": YinYang.YIN,
    "庚": YinYang.YANG, "辛": YinYang.YIN,
    "壬": YinYang.YANG, "癸": YinYang.YIN,
}
```

### 4.2 十二支→五行マッピング

```python
BRANCH_TO_ELEMENT: dict[str, FiveElement] = {
    "子": FiveElement.WATER,
    "丑": FiveElement.EARTH,
    "寅": FiveElement.WOOD,
    "卯": FiveElement.WOOD,
    "辰": FiveElement.EARTH,
    "巳": FiveElement.FIRE,
    "午": FiveElement.FIRE,
    "未": FiveElement.EARTH,
    "申": FiveElement.METAL,
    "酉": FiveElement.METAL,
    "戌": FiveElement.EARTH,
    "亥": FiveElement.WATER,
}
```

### 4.3 通変星（十神）→ 十大主星マッピング（核心テーブル）

**四柱推命の通変星と算命学の十大主星は1対1で対応する。**
`lunar_python` の `getXxxShiShenGan()` が返す通変星をこのテーブルで変換する。

```python
TSUHENSEI_TO_JUDAI: dict[str, JudaiShusei] = {
    "比肩": JudaiShusei.KANSAKU,    # 貫索星（守備・陽）
    "劫財": JudaiShusei.SEKIMON,    # 石門星（守備・陰）
    "食神": JudaiShusei.HOUKAKU,    # 鳳閣星（伝達・陽）
    "傷官": JudaiShusei.CHOSHO,     # 調舒星（伝達・陰）
    "偏財": JudaiShusei.ROKUZON,    # 禄存星（引力・陽）
    "正財": JudaiShusei.SHIROKU,    # 司禄星（引力・陰）
    "偏官": JudaiShusei.SHAKI,      # 車騎星（攻撃・陽）
    "正官": JudaiShusei.KENGYUU,    # 牽牛星（攻撃・陰）
    "偏印": JudaiShusei.RYUUKOU,    # 龍高星（習得・陽）
    "印綬": JudaiShusei.GYOKUDOU,   # 玉堂星（習得・陰）
}
```

### 4.4 十大主星表（日干 × 相手干 → 十大主星）

`lunar_python` の通変星変換が利用できない場合の**フォールバック用テーブル**。
行 = 日干、列 = 相手干、値 = 十大主星。

```python
JUDAI_TABLE: dict[str, dict[str, str]] = {
    #        甲        乙        丙        丁        戊        己        庚        辛        壬        癸
    "甲": {"甲":"貫索星","乙":"石門星","丙":"鳳閣星","丁":"調舒星","戊":"禄存星","己":"司禄星","庚":"車騎星","辛":"牽牛星","壬":"龍高星","癸":"玉堂星"},
    "乙": {"乙":"貫索星","甲":"石門星","丁":"鳳閣星","丙":"調舒星","己":"禄存星","戊":"司禄星","辛":"車騎星","庚":"牽牛星","癸":"龍高星","壬":"玉堂星"},
    "丙": {"丙":"貫索星","丁":"石門星","戊":"鳳閣星","己":"調舒星","庚":"禄存星","辛":"司禄星","壬":"車騎星","癸":"牽牛星","甲":"龍高星","乙":"玉堂星"},
    "丁": {"丁":"貫索星","丙":"石門星","己":"鳳閣星","戊":"調舒星","辛":"禄存星","庚":"司禄星","癸":"車騎星","壬":"牽牛星","乙":"龍高星","甲":"玉堂星"},
    "戊": {"戊":"貫索星","己":"石門星","庚":"鳳閣星","辛":"調舒星","壬":"禄存星","癸":"司禄星","甲":"車騎星","乙":"牽牛星","丙":"龍高星","丁":"玉堂星"},
    "己": {"己":"貫索星","戊":"石門星","辛":"鳳閣星","庚":"調舒星","癸":"禄存星","壬":"司禄星","乙":"車騎星","甲":"牽牛星","丁":"龍高星","丙":"玉堂星"},
    "庚": {"庚":"貫索星","辛":"石門星","壬":"鳳閣星","癸":"調舒星","甲":"禄存星","乙":"司禄星","丙":"車騎星","丁":"牽牛星","戊":"龍高星","己":"玉堂星"},
    "辛": {"辛":"貫索星","庚":"石門星","癸":"鳳閣星","壬":"調舒星","乙":"禄存星","甲":"司禄星","丁":"車騎星","丙":"牽牛星","己":"龍高星","戊":"玉堂星"},
    "壬": {"壬":"貫索星","癸":"石門星","甲":"鳳閣星","乙":"調舒星","丙":"禄存星","丁":"司禄星","戊":"車騎星","己":"牽牛星","庚":"龍高星","辛":"玉堂星"},
    "癸": {"癸":"貫索星","壬":"石門星","乙":"鳳閣星","甲":"調舒星","丁":"禄存星","丙":"司禄星","己":"車騎星","戊":"牽牛星","辛":"龍高星","庚":"玉堂星"},
}
```

### 4.5 十二運→十二大従星マッピング

```python
JUNIUNSEI_TO_JUNIDAI: dict[str, JuniDaiJusei] = {
    "胎":  JuniDaiJusei.TENPOU,    # 天報星 エネルギー3
    "養":  JuniDaiJusei.TENIN,     # 天印星 エネルギー6
    "長生": JuniDaiJusei.TENKI,     # 天貴星 エネルギー9
    "沐浴": JuniDaiJusei.TENKOU,    # 天恍星 エネルギー7
    "冠帯": JuniDaiJusei.TENNAN,    # 天南星 エネルギー8
    "臨官": JuniDaiJusei.TENROKU,   # 天禄星 エネルギー11（建禄）
    "帝旺": JuniDaiJusei.TENSHOU,   # 天将星 エネルギー12
    "衰":  JuniDaiJusei.TENDOU,    # 天堂星 エネルギー10
    "病":  JuniDaiJusei.TENKOSEI,   # 天胡星 エネルギー5
    "死":  JuniDaiJusei.TENGOKU,   # 天極星 エネルギー2
    "墓":  JuniDaiJusei.TENKUSEI,  # 天庫星 エネルギー4
    "絶":  JuniDaiJusei.TENCHI,    # 天馳星 エネルギー1
}

JUNIDAI_ENERGY: dict[JuniDaiJusei, int] = {
    JuniDaiJusei.TENPOU: 3,
    JuniDaiJusei.TENIN: 6,
    JuniDaiJusei.TENKI: 9,
    JuniDaiJusei.TENKOU: 7,
    JuniDaiJusei.TENNAN: 8,
    JuniDaiJusei.TENROKU: 11,
    JuniDaiJusei.TENSHOU: 12,
    JuniDaiJusei.TENDOU: 10,
    JuniDaiJusei.TENKOSEI: 5,
    JuniDaiJusei.TENGOKU: 2,
    JuniDaiJusei.TENKUSEI: 4,
    JuniDaiJusei.TENCHI: 1,
}
```

### 4.6 天中殺（空亡）マッピング

`lunar_python` の `getDayXunKong()` が返す2文字の地支を天中殺グループに変換。

```python
XUNKONG_TO_TENCHUSATSU: dict[str, TenchusatsuGroup] = {
    "子丑": TenchusatsuGroup.NE_USHI,
    "寅卯": TenchusatsuGroup.TORA_U,
    "辰巳": TenchusatsuGroup.TATSU_MI,
    "午未": TenchusatsuGroup.UMA_HITSUJI,
    "申酉": TenchusatsuGroup.SARU_TORI,
    "戌亥": TenchusatsuGroup.INU_I,
}
```

### 4.7 干合テーブル（伴星算出用）

干合とは特定の天干同士のペアリング。伴星 = 日干 ×「年干と干合する干」で算出。

```python
KANGO_PAIR: dict[str, str] = {
    "甲": "己", "己": "甲",  # 甲己干合（土化）
    "乙": "庚", "庚": "乙",  # 乙庚干合（金化）
    "丙": "辛", "辛": "丙",  # 丙辛干合（水化）
    "丁": "壬", "壬": "丁",  # 丁壬干合（木化）
    "戊": "癸", "癸": "戊",  # 戊癸干合（火化）
}
```

### 4.8 蔵干テーブル（十二支→内蔵する天干）

人体星図の南方星（日干×日支蔵干）、東方星（日干×月支蔵干）、西方星（日干×年支蔵干）の算出に使用。
**蔵干の「本気」（最も影響力の強い干）を使用する。**

```python
ZOUKAN_HONKI: dict[str, str] = {
    "子": "癸",
    "丑": "己",
    "寅": "甲",
    "卯": "乙",
    "辰": "戊",
    "巳": "丙",
    "午": "丁",
    "未": "己",
    "申": "庚",
    "酉": "辛",
    "戌": "戊",
    "亥": "壬",
}
```

---

## 5. 算出フロー（calculator.py + sanmei.py）

### 5.1 全体フロー

```
入力: birth_date, birth_time
  │
  ▼
[Step 1] lunar_python で四柱推命データ取得
  │  Solar.fromYmd() → Lunar → EightChar
  │  → 年柱/月柱/日柱/時柱の干支
  │  → 五行・納音
  │  → 通変星（十神）
  │  → 空亡（旬空）
  │
  ▼
[Step 2] NatalChart（命式）を構築
  │  各柱 → Pillar オブジェクト
  │  五行バランスを集計
  │
  ▼
[Step 3] 算命学データを算出（sanmei.py）
  │
  ├─ [3a] 十大主星の算出（人体星図5箇所 + 伴星）
  │   ├─ 中央: 日干 × 月干 → JUDAI_TABLE で変換
  │   ├─ 北方: 日干 × 年干 → JUDAI_TABLE で変換
  │   ├─ 南方: 日干 × 日支蔵干（本気）→ JUDAI_TABLE
  │   ├─ 東方: 日干 × 月支蔵干（本気）→ JUDAI_TABLE
  │   ├─ 西方: 日干 × 年支蔵干（本気）→ JUDAI_TABLE
  │   └─ 伴星: 日干 × KANGO_PAIR[年干] → JUDAI_TABLE
  │
  ├─ [3b] 十二大従星の算出（3箇所）
  │   ├─ 北方（左肩）: 日干 × 年支 → 十二運テーブル
  │   ├─ 南方（左足）: 日干 × 日支 → 十二運テーブル
  │   └─ 西方（右足）: 日干 × 月支 → 十二運テーブル
  │
  ├─ [3c] 天中殺の算出
  │   └─ eightChar.getDayXunKong() → XUNKONG_TO_TENCHUSATSU
  │
  └─ [3d] エネルギー合計の算出
      └─ 3つの十二大従星のエネルギー値を合計
  │
  ▼
[Step 4] FortuneResult として統合して返却
```

### 5.2 calculator.py の処理詳細

```python
def calculate_natal_chart(birth_date: date, birth_time: time | None = None) -> NatalChart:
    """四柱推命の命式を算出する。"""

    # 1. Solar オブジェクトを生成
    if birth_time:
        solar = Solar.fromYmdHms(
            birth_date.year, birth_date.month, birth_date.day,
            birth_time.hour, birth_time.minute, 0
        )
    else:
        solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)

    # 2. Lunar（太陰暦）に変換
    lunar = solar.getLunar()

    # 3. EightChar（八字）を取得
    eight_char = lunar.getEightChar()

    # 4. 各柱を構築
    year_pillar = _build_pillar(eight_char.getYearGan(), eight_char.getYearZhi(), eight_char.getYear())
    month_pillar = _build_pillar(eight_char.getMonthGan(), eight_char.getMonthZhi(), eight_char.getMonth())
    day_pillar = _build_pillar(eight_char.getDayGan(), eight_char.getDayZhi(), eight_char.getDay())

    hour_pillar = None
    if birth_time:
        hour_pillar = _build_pillar(eight_char.getTimeGan(), eight_char.getTimeZhi(), eight_char.getTime())

    # 5. 日干
    day_stem = eight_char.getDayGan()

    # 6. 五行バランス集計
    pillars = [year_pillar, month_pillar, day_pillar]
    if hour_pillar:
        pillars.append(hour_pillar)
    balance = _count_five_elements(pillars)

    # 7. 旬空（空亡）
    xun_kong = eight_char.getDayXunKong()

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
```

### 5.3 sanmei.py の処理詳細

```python
def calculate_sanmei_data(natal_chart: NatalChart) -> SanmeiData:
    """命式から算命学データを算出する。"""

    day_stem = natal_chart.day_stem
    year_stem = natal_chart.year_pillar.stem
    month_stem = natal_chart.month_pillar.stem
    year_branch = natal_chart.year_pillar.branch
    month_branch = natal_chart.month_pillar.branch
    day_branch = natal_chart.day_pillar.branch

    # --- 十大主星（人体星図5箇所 + 伴星）---
    center = _lookup_judai(day_stem, month_stem)          # 中央（胸）
    north = _lookup_judai(day_stem, year_stem)             # 北方（頭）
    south = _lookup_judai(day_stem, ZOUKAN_HONKI[day_branch])   # 南方（腹）
    east = _lookup_judai(day_stem, ZOUKAN_HONKI[month_branch])  # 東方（左手）
    west = _lookup_judai(day_stem, ZOUKAN_HONKI[year_branch])   # 西方（右手）

    # 伴星: 年干と干合する干を求め、日干との関係から算出
    kango_stem = KANGO_PAIR[year_stem]
    companion = _lookup_judai(day_stem, kango_stem)

    # --- 十二大従星（3箇所）---
    north_twelve = _lookup_junidai(day_stem, year_branch)   # 北方（左肩）
    south_twelve = _lookup_junidai(day_stem, day_branch)    # 南方（左足）
    west_twelve = _lookup_junidai(day_stem, month_branch)   # 西方（右足）

    # --- 天中殺 ---
    tenchusatsu = XUNKONG_TO_TENCHUSATSU[natal_chart.xun_kong]

    # --- エネルギー ---
    total_energy = sum(
        JUNIDAI_ENERGY[s]
        for s in [north_twelve, south_twelve, west_twelve]
    )

    human_chart = HumanStarChart(
        center_star=center, north_star=north, south_star=south,
        east_star=east, west_star=west, companion_star=companion,
        north_twelve=north_twelve, south_twelve=south_twelve, west_twelve=west_twelve,
    )

    return SanmeiData(
        human_star_chart=human_chart,
        tenchusatsu=tenchusatsu,
        total_energy=total_energy,
    )


def _lookup_judai(day_stem: str, target_stem: str) -> JudaiShusei:
    """日干と対象干から十大主星を引く。"""
    star_name = JUDAI_TABLE[day_stem][target_stem]
    return JudaiShusei(star_name)


def _lookup_junidai(day_stem: str, branch: str) -> JuniDaiJusei:
    """日干と地支から十二大従星を引く。

    十二運（長生表）を使用。日干の五行と陰陽に基づき、
    地支に対応する十二運を求め、十二大従星に変換する。
    """
    # lunar_python の十二長生表を利用するか、
    # 独自のTWELVE_PHASES_TABLE を参照する
    phase = TWELVE_PHASES_TABLE[day_stem][branch]
    return JUNIUNSEI_TO_JUNIDAI[phase]
```

---

## 6. 十二運テーブル（TWELVE_PHASES_TABLE）

日干（行）× 地支（列）→ 十二運。十二大従星算出の核心テーブル。

```python
TWELVE_PHASES_TABLE: dict[str, dict[str, str]] = {
    #     子     丑     寅     卯     辰     巳     午     未     申     酉     戌     亥
    "甲": {"子":"沐浴","丑":"冠帯","寅":"臨官","卯":"帝旺","辰":"衰",  "巳":"病",  "午":"死",  "未":"墓",  "申":"絶",  "酉":"胎",  "戌":"養",  "亥":"長生"},
    "乙": {"子":"病",  "丑":"衰",  "寅":"帝旺","卯":"臨官","辰":"冠帯","巳":"沐浴","午":"長生","未":"養",  "申":"胎",  "酉":"絶",  "戌":"墓",  "亥":"死"},
    "丙": {"子":"胎",  "丑":"養",  "寅":"長生","卯":"沐浴","辰":"冠帯","巳":"臨官","午":"帝旺","未":"衰",  "申":"病",  "酉":"死",  "戌":"墓",  "亥":"絶"},
    "丁": {"子":"絶",  "丑":"墓",  "寅":"死",  "卯":"病",  "辰":"衰",  "巳":"帝旺","午":"臨官","未":"冠帯","申":"沐浴","酉":"長生","戌":"養",  "亥":"胎"},
    "戊": {"子":"胎",  "丑":"養",  "寅":"長生","卯":"沐浴","辰":"冠帯","巳":"臨官","午":"帝旺","未":"衰",  "申":"病",  "酉":"死",  "戌":"墓",  "亥":"絶"},
    "己": {"子":"絶",  "丑":"墓",  "寅":"死",  "卯":"病",  "辰":"衰",  "巳":"帝旺","午":"臨官","未":"冠帯","申":"沐浴","酉":"長生","戌":"養",  "亥":"胎"},
    "庚": {"子":"死",  "丑":"墓",  "寅":"絶",  "卯":"胎",  "辰":"養",  "巳":"長生","午":"沐浴","未":"冠帯","申":"臨官","酉":"帝旺","戌":"衰",  "亥":"病"},
    "辛": {"子":"長生","丑":"養",  "寅":"胎",  "卯":"絶",  "辰":"墓",  "巳":"死",  "午":"病",  "未":"衰",  "申":"帝旺","酉":"臨官","戌":"冠帯","亥":"沐浴"},
    "壬": {"子":"帝旺","丑":"衰",  "寅":"病",  "卯":"死",  "辰":"墓",  "巳":"絶",  "午":"胎",  "未":"養",  "申":"長生","酉":"沐浴","戌":"冠帯","亥":"臨官"},
    "癸": {"子":"臨官","丑":"冠帯","寅":"沐浴","卯":"長生","辰":"養",  "巳":"胎",  "午":"絶",  "未":"墓",  "申":"死",  "酉":"病",  "戌":"衰",  "亥":"帝旺"},
}
```

---

## 7. formatter.py（出力フォーマッタ）

AIプロンプトに埋め込む命式テキストと、UI表示用のフォーマットを提供する。

### 7.1 AI プロンプト用フォーマット

```python
def format_for_ai_prompt(result: FortuneResult) -> str:
    """FortuneResult をAIプロンプトに埋め込むテキストに変換する。"""

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

    lines.extend([
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
    ])

    return "\n".join(lines)
```

---

## 8. テスト戦略

### 8.1 既知の命式での検証

**実在する生年月日で算出結果を既知の命式ソフトと照合する。**

テストケース例:
- 1985年12月15日生まれ → 算命学Stockの無料命式と照合
- 1990年5月15日 10:30生まれ → 年柱・月柱・日柱・時柱を検証
- 2000年1月1日生まれ（出生時間不明）→ 時柱が None であること

### 8.2 テストファイル

```
tests/
├── unit/
│   ├── test_calculator.py     # calculate_natal_chart の正常系・異常系
│   ├── test_sanmei.py         # calculate_sanmei_data の正常系・テーブル照合
│   ├── test_constants.py      # 定数テーブルの整合性（全10干×10干 = 100組が定義されているか等）
│   └── test_formatter.py      # フォーマッタの出力内容
├── integration/
│   └── test_fortune_flow.py   # calculate_fortune の入力→出力フルフロー
└── fixtures/
    └── expected_natal_charts.json  # 既知の命式データ（検証用）
```

### 8.3 定数テーブルの整合性テスト

```python
def test_judai_table_has_all_100_combinations():
    """十大主星表が10干×10干=100組すべてを網羅していること。"""
    stems = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    for day in stems:
        assert day in JUDAI_TABLE
        for target in stems:
            assert target in JUDAI_TABLE[day]

def test_twelve_phases_table_has_all_120_combinations():
    """十二運テーブルが10干×12支=120組すべてを網羅していること。"""
    stems = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
    branches = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]
    for stem in stems:
        assert stem in TWELVE_PHASES_TABLE
        for branch in branches:
            assert branch in TWELVE_PHASES_TABLE[stem]
```

---

## 9. 公開API（__init__.py）

```python
"""命式計算エンジン。

Usage:
    from fortune_engine import calculate_fortune
    result = calculate_fortune(birth_date=date(1990, 5, 15), birth_time=time(10, 30))
"""

from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.sanmei import calculate_sanmei_data
from fortune_engine.formatter import format_for_ai_prompt
from fortune_engine.models import FortuneResult


def calculate_fortune(
    birth_date: "date",
    birth_time: "time | None" = None,
) -> FortuneResult:
    """命式を算出する統合関数（UI層から呼び出すエントリーポイント）。"""
    natal_chart = calculate_natal_chart(birth_date, birth_time)
    sanmei_data = calculate_sanmei_data(natal_chart)
    return FortuneResult(natal_chart=natal_chart, sanmei_data=sanmei_data)
```

---

## 10. 実装優先順位

| # | タスク | 依存 | 見積 |
|---|--------|------|------|
| 1 | `models.py` — 全データモデル定義 | なし | 小 |
| 2 | `constants.py` — 全定数テーブル | models.py | 中 |
| 3 | `calculator.py` — lunar_python連携 | models, constants | 中 |
| 4 | テスト: calculator の正常系 | calculator | 小 |
| 5 | `sanmei.py` — 算命学算出 | models, constants, calculator | 中 |
| 6 | テスト: sanmei の正常系 + テーブル照合 | sanmei | 中 |
| 7 | `formatter.py` — 出力フォーマッタ | models | 小 |
| 8 | `__init__.py` — 公開API | 全モジュール | 小 |
| 9 | テスト: フルフロー統合テスト | 全モジュール | 中 |
