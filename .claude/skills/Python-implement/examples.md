# Python 開発 — 実装例とベストプラクティス

## Pydantic モデルの定義例

```python
"""命式関連のデータモデル定義。"""

from datetime import date, time
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class FiveElement(str, Enum):
    """五行。"""
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"


class Pillar(BaseModel):
    """四柱の1柱。天干・地支・五行属性を持つ。"""

    stem: str = Field(description="天干（甲〜癸）")
    branch: str = Field(description="地支（子〜亥）")
    element: FiveElement = Field(description="五行属性")

    @field_validator("stem")
    @classmethod
    def validate_stem(cls, v: str) -> str:
        """天干が有効な値であることを検証する。"""
        valid_stems = {"甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"}
        if v not in valid_stems:
            raise ValueError(f"無効な天干: {v}")
        return v


class NatalChart(BaseModel):
    """四柱推命の命式。"""

    year_pillar: Pillar = Field(description="年柱")
    month_pillar: Pillar = Field(description="月柱")
    day_pillar: Pillar = Field(description="日柱")
    hour_pillar: Pillar | None = Field(
        default=None,
        description="時柱（出生時間不明の場合はNone）",
    )
    day_stem: str = Field(description="日干（命式の中心）")
    five_elements_balance: dict[FiveElement, int] = Field(
        description="五行のバランス（各要素の出現数）",
    )


class ClientInput(BaseModel):
    """相談者入力データ。"""

    name: str = Field(min_length=1, max_length=50, description="名前（仮名可）")
    birth_date: date = Field(description="生年月日")
    birth_time: time | None = Field(default=None, description="出生時間")
    concern: str = Field(min_length=10, max_length=2000, description="悩み")

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: date) -> date:
        """生年月日が有効な範囲であることを検証する。"""
        if v > date.today():
            raise ValueError("未来の日付は指定できません")
        if v < date(1900, 1, 1):
            raise ValueError("1900年以前の日付は対応していません")
        return v
```

---

## 関数の実装例（型ヒント・docstring 付き）

```python
"""命式算出モジュール。lunar_python を使用して四柱推命の命式を算出する。"""

import logging
from datetime import date, time

from lunar_python import Solar

from fortune_engine.constants import STEM_TO_ELEMENT
from fortune_engine.models import FiveElement, NatalChart, Pillar
from utils.exceptions import FortuneCalculationError

logger = logging.getLogger(__name__)


def calculate_natal_chart(
    birth_date: date,
    birth_time: time | None = None,
) -> NatalChart:
    """生年月日から四柱推命の命式を算出する。

    lunar_python を使用して太陰暦変換・干支算出を行い、
    NatalChart オブジェクトとして返す。

    Args:
        birth_date: 相談者の生年月日。
        birth_time: 出生時間。不明の場合はNone。

    Returns:
        算出された命式データ。

    Raises:
        FortuneCalculationError: 日付が範囲外など、算出不能な場合。
    """
    logger.info("命式算出を開始")

    try:
        solar = Solar.fromYmd(birth_date.year, birth_date.month, birth_date.day)
        lunar = solar.getLunar()
        eight_char = lunar.getEightChar()
    except Exception as e:
        logger.error("lunar_python での変換に失敗: %s", e)
        raise FortuneCalculationError(f"命式の算出に失敗しました: {e}") from e

    year_pillar = _create_pillar(
        stem=eight_char.getYearGan(),
        branch=eight_char.getYearZhi(),
    )
    month_pillar = _create_pillar(
        stem=eight_char.getMonthGan(),
        branch=eight_char.getMonthZhi(),
    )
    day_pillar = _create_pillar(
        stem=eight_char.getDayGan(),
        branch=eight_char.getDayZhi(),
    )

    hour_pillar = None
    if birth_time is not None:
        hour_pillar = _create_pillar(
            stem=eight_char.getTimeGan(),
            branch=eight_char.getTimeZhi(),
        )

    day_stem = day_pillar.stem
    balance = _calculate_five_elements_balance(
        [year_pillar, month_pillar, day_pillar, hour_pillar]
    )

    logger.info("命式算出完了: 日干=%s", day_stem)

    return NatalChart(
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_stem=day_stem,
        five_elements_balance=balance,
    )


def _create_pillar(stem: str, branch: str) -> Pillar:
    """天干と地支から Pillar オブジェクトを生成する。"""
    element = STEM_TO_ELEMENT.get(stem, FiveElement.EARTH)
    return Pillar(stem=stem, branch=branch, element=element)


def _calculate_five_elements_balance(
    pillars: list[Pillar | None],
) -> dict[FiveElement, int]:
    """柱のリストから五行のバランスを算出する。"""
    balance: dict[FiveElement, int] = {e: 0 for e in FiveElement}
    for pillar in pillars:
        if pillar is not None:
            balance[pillar.element] += 1
    return balance
```

---

## カスタム例外の定義例

```python
"""カスタム例外定義。"""


class FortuneAppError(Exception):
    """アプリケーション基底例外。すべてのカスタム例外はこれを継承する。"""
    pass


class FortuneCalculationError(FortuneAppError):
    """命式算出時のエラー。無効な日付や算出不能な入力に対して送出する。"""
    pass


class AIServiceError(FortuneAppError):
    """AI連携時のエラー。API接続失敗、タイムアウト等に対して送出する。"""
    pass


class AIServiceConfigError(AIServiceError):
    """AI設定エラー。APIキー未設定等に対して送出する。"""
    pass


class DatabaseError(FortuneAppError):
    """データベース操作時のエラー。"""
    pass
```

---

## ログ出力の例

```python
import logging

logger = logging.getLogger(__name__)

# Good: 個人情報を含めず、IDで識別
logger.info("命式算出を開始: client_id=%s", client_id)
logger.info("AI鑑定テキスト生成完了: session_id=%s, tokens=%d", session_id, token_count)
logger.warning("API呼び出しリトライ: provider=%s, attempt=%d", provider, attempt)
logger.error("DB保存に失敗: session_id=%s, error=%s", session_id, str(e))

# Bad: 個人情報がログに含まれる（絶対に避ける）
logger.info("命式算出: %s さん, 生年月日: %s", name, birth_date)
logger.info("悩み: %s", concern_text)
```
