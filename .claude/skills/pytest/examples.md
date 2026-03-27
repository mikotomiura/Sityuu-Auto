# テスト開発 — 実装例とベストプラクティス

## conftest.py（全テスト共通フィクスチャ）

```python
"""テスト共通フィクスチャ。"""

from datetime import date, time

import pytest

from fortune_engine.models import (
    ClientInput,
    FiveElement,
    NatalChart,
    Pillar,
)


@pytest.fixture
def sample_client_input() -> ClientInput:
    """テスト用の相談者入力データ。"""
    return ClientInput(
        name="テスト太郎",
        birth_date=date(1990, 5, 15),
        birth_time=time(10, 30),
        concern="仕事の方向性について悩んでいます。転職すべきか現職で頑張るべきか。",
    )


@pytest.fixture
def sample_client_input_no_time() -> ClientInput:
    """出生時間不明の相談者入力データ。"""
    return ClientInput(
        name="テスト花子",
        birth_date=date(1985, 12, 1),
        birth_time=None,
        concern="人間関係の悩みです。周囲との関係をどう改善すればよいか知りたい。",
    )


@pytest.fixture
def sample_natal_chart() -> NatalChart:
    """テスト用の命式データ。"""
    return NatalChart(
        year_pillar=Pillar(stem="庚", branch="午", element=FiveElement.METAL),
        month_pillar=Pillar(stem="辛", branch="巳", element=FiveElement.METAL),
        day_pillar=Pillar(stem="甲", branch="子", element=FiveElement.WOOD),
        hour_pillar=Pillar(stem="丙", branch="寅", element=FiveElement.FIRE),
        day_stem="甲",
        five_elements_balance={
            FiveElement.WOOD: 2,
            FiveElement.FIRE: 1,
            FiveElement.EARTH: 0,
            FiveElement.METAL: 2,
            FiveElement.WATER: 1,
        },
    )
```

---

## ユニットテストの実装例

### 命式算出のテスト

```python
"""命式算出のユニットテスト。"""

from datetime import date, time

import pytest

from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.models import NatalChart
from utils.exceptions import FortuneCalculationError


class TestCalculateNatalChart:
    """calculate_natal_chart 関数のテスト。"""

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
        assert result.hour_pillar is not None

    def test_calculate_without_birth_time_has_no_hour_pillar(self) -> None:
        """出生時間なしの場合、hour_pillar が None であること。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=None,
        )

        assert result.hour_pillar is None

    def test_calculate_with_boundary_date_earliest(self) -> None:
        """最古の対応日付（1900-01-01）で算出できること。"""
        result = calculate_natal_chart(birth_date=date(1900, 1, 1))

        assert isinstance(result, NatalChart)

    def test_calculate_with_today_date(self) -> None:
        """今日の日付で算出できること。"""
        result = calculate_natal_chart(birth_date=date.today())

        assert isinstance(result, NatalChart)

    def test_five_elements_balance_sums_correctly(self) -> None:
        """五行バランスの合計が柱の数と一致すること。"""
        result = calculate_natal_chart(
            birth_date=date(1990, 5, 15),
            birth_time=time(10, 30),
        )

        total = sum(result.five_elements_balance.values())
        expected = 4  # year + month + day + hour
        assert total == expected
```

---

### バリデーションのテスト

```python
"""バリデーション関数のユニットテスト。"""

from datetime import date

import pytest
from pydantic import ValidationError

from fortune_engine.models import ClientInput


class TestClientInputValidation:
    """ClientInput のバリデーションテスト。"""

    def test_valid_input_creates_successfully(self) -> None:
        """有効な入力で ClientInput が生成されること。"""
        client = ClientInput(
            name="テスト太郎",
            birth_date=date(1990, 5, 15),
            concern="仕事について悩んでいます。どうすればよいか教えてください。",
        )

        assert client.name == "テスト太郎"

    def test_empty_name_raises_validation_error(self) -> None:
        """空の名前で ValidationError が発生すること。"""
        with pytest.raises(ValidationError):
            ClientInput(
                name="",
                birth_date=date(1990, 5, 15),
                concern="仕事について悩んでいます。どうすればよいか教えてください。",
            )

    def test_short_concern_raises_validation_error(self) -> None:
        """10文字未満の悩みで ValidationError が発生すること。"""
        with pytest.raises(ValidationError):
            ClientInput(
                name="テスト",
                birth_date=date(1990, 5, 15),
                concern="短い悩み",
            )

    def test_future_birth_date_raises_validation_error(self) -> None:
        """未来の生年月日で ValidationError が発生すること。"""
        with pytest.raises(ValidationError):
            ClientInput(
                name="テスト",
                birth_date=date(2099, 1, 1),
                concern="仕事について悩んでいます。どうすればよいか教えてください。",
            )
```

---

## AI連携層のモックテスト例

```python
"""プロンプトビルダーのユニットテスト。"""

from unittest.mock import AsyncMock, patch

import pytest

from ai_service.prompt_builder import build_reading_prompt
from fortune_engine.models import NatalChart


class TestBuildReadingPrompt:
    """build_reading_prompt のテスト。"""

    def test_prompt_contains_day_stem(
        self, sample_natal_chart: NatalChart
    ) -> None:
        """プロンプトに日干が含まれること。"""
        prompt = build_reading_prompt(
            natal_chart=sample_natal_chart,
            concern="仕事の方向性について悩んでいます。",
        )

        assert sample_natal_chart.day_stem in prompt

    def test_prompt_contains_concern_text(
        self, sample_natal_chart: NatalChart
    ) -> None:
        """プロンプトに悩みテキストが含まれること。"""
        concern = "仕事の方向性について悩んでいます。"
        prompt = build_reading_prompt(
            natal_chart=sample_natal_chart,
            concern=concern,
        )

        assert concern in prompt
```

---

## 統合テストの実装例

```python
"""DB操作の統合テスト。"""

import sqlite3
from datetime import date

import pytest

from db_service.database import initialize_database
from db_service.repositories.client_repo import ClientRepository


@pytest.fixture
def db_connection():
    """テスト用インメモリDBコネクション。"""
    conn = sqlite3.connect(":memory:")
    initialize_database(conn)
    yield conn
    conn.close()


@pytest.fixture
def client_repo(db_connection: sqlite3.Connection) -> ClientRepository:
    """テスト用クライアントリポジトリ。"""
    return ClientRepository(db_connection)


class TestClientRepository:
    """ClientRepository の統合テスト。"""

    def test_save_and_find_client(self, client_repo: ClientRepository) -> None:
        """相談者を保存して検索できること。"""
        client_id = client_repo.save(
            name="テスト太郎",
            birth_date=date(1990, 5, 15),
        )

        found = client_repo.find_by_id(client_id)

        assert found is not None
        assert found.name == "テスト太郎"

    def test_find_nonexistent_client_returns_none(
        self, client_repo: ClientRepository
    ) -> None:
        """存在しないIDで None が返ること。"""
        found = client_repo.find_by_id("nonexistent-id")

        assert found is None
```
