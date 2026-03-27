# 開発ガイドライン（development-guidelines.md）

## 1. コーディング規約

### 1.1 Python バージョン

- **Python 3.11 以上**を使用する
- 3.11 以降の構文（`match` 文、`Self` 型など）は積極的に利用してよい

### 1.2 型ヒント

すべての関数・メソッドに型ヒントを付与すること。

```python
# Good
def calculate_natal_chart(birth_date: date, birth_time: time | None = None) -> NatalChart:
    ...

# Bad
def calculate_natal_chart(birth_date, birth_time=None):
    ...
```

コレクション型は `list`, `dict`, `tuple` のビルトイン型を使用する（`typing.List` 等は使わない）。

```python
# Good
def get_clients(limit: int = 10) -> list[Client]:
    ...

# Bad（typing.Listは不要）
from typing import List
def get_clients(limit: int = 10) -> List[Client]:
    ...
```

### 1.3 命名規則

| 対象 | スタイル | 例 |
|------|----------|-----|
| モジュール | snake_case | `fortune_engine.py` |
| クラス | PascalCase | `NatalChart`, `LLMClient` |
| 関数・メソッド | snake_case | `calculate_natal_chart()` |
| 変数 | snake_case | `day_stem`, `birth_date` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT`, `DEFAULT_MODEL` |
| プライベート | 先頭アンダースコア | `_parse_response()` |
| Enum メンバー | UPPER_SNAKE_CASE | `FiveElement.WOOD` |

命名は `docs/glossary.md` のユビキタス言語に準拠すること。

### 1.4 docstring

Google スタイルの docstring を使用する。

```python
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
```

### 1.5 import 順序

```python
# 1. 標準ライブラリ
import os
from datetime import date, time
from pathlib import Path

# 2. サードパーティ
import streamlit as st
from pydantic import BaseModel

# 3. ローカルモジュール
from fortune_engine.calculator import calculate_natal_chart
from fortune_engine.models import NatalChart
```

---

## 2. ツールチェーン

### 2.1 フォーマッター / リンター

`ruff` を使用する。

```bash
# フォーマット
ruff format src/ tests/

# リント
ruff check src/ tests/

# リント（自動修正）
ruff check --fix src/ tests/
```

**ruff 設定（pyproject.toml）:**

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM", "RUF"]

[tool.ruff.format]
quote-style = "double"
```

### 2.2 型チェック

`mypy` を使用する。

```bash
mypy src/
```

**mypy 設定（pyproject.toml）:**

```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
```

### 2.3 テスト

`pytest` を使用する。

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定テスト実行
pytest tests/unit/test_calculator.py -v
```

---

## 3. Git 運用

### 3.1 コミットメッセージ

**Conventional Commits** に従う。

```
<type>(<scope>): <description>

<body>（任意）

<footer>（任意）
```

**type 一覧:**

| type | 用途 |
|------|------|
| `feat` | 新機能追加 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更 |
| `style` | コードの意味に影響しない変更（フォーマット等） |
| `refactor` | バグ修正でも機能追加でもないコード変更 |
| `test` | テストの追加・修正 |
| `chore` | ビルドプロセスや補助ツールの変更 |

**例:**

```
feat(fortune-engine): 四柱推命の命式算出機能を実装

lunar_pythonを使用して年柱・月柱・日柱・時柱の算出を行う。
出生時間が不明な場合は時柱をNoneとして扱う。
```

### 3.2 ブランチ戦略

```
main                      # 安定版（リリース可能な状態を保つ）
├── develop               # 開発統合ブランチ
│   ├── feat/xxx          # 機能開発ブランチ
│   ├── fix/xxx           # バグ修正ブランチ
│   └── refactor/xxx      # リファクタリングブランチ
```

---

## 4. エラーハンドリング

### 4.1 例外の使い方

- カスタム例外を使用する（`src/utils/exceptions.py` で定義）
- `Exception` を直接 `raise` しない
- `except Exception` で広範囲に捕捉しない（具体的な例外型を指定する）

```python
# Good
try:
    chart = calculate_natal_chart(birth_date)
except FortuneCalculationError as e:
    st.error(f"命式の算出に失敗しました: {e}")

# Bad
try:
    chart = calculate_natal_chart(birth_date)
except Exception:
    st.error("エラーが発生しました")
```

### 4.2 ログ出力

- `logging` モジュールを使用する（`print` デバッグ禁止）
- **個人情報をログに出力しない**（生年月日、名前、悩みテキスト）

```python
import logging

logger = logging.getLogger(__name__)

# Good
logger.info("命式算出を開始: client_id=%s", client_id)

# Bad（個人情報がログに含まれる）
logger.info("命式算出: %s, 生年月日: %s", client_name, birth_date)
```

---

## 5. テスト戦略

### 5.1 テストの種類

| 種類 | 場所 | 対象 | 実行頻度 |
|------|------|------|----------|
| ユニットテスト | `tests/unit/` | 個々の関数・クラス | コミット毎 |
| 統合テスト | `tests/integration/` | モジュール間の連携 | PR毎 |

### 5.2 テスト命名

```python
def test_calculate_natal_chart_with_valid_date():
    """正常な日付で命式が算出されること。"""
    ...

def test_calculate_natal_chart_raises_error_for_future_date():
    """未来の日付ではFortuneCalculationErrorが発生すること。"""
    ...
```

パターン: `test_[対象]_[条件/期待結果]`

### 5.3 カバレッジ目標

- ロジック層（`fortune_engine/`）: **90% 以上**
- DB層（`db_service/`）: **80% 以上**
- AI連携層（`ai_service/`）: **70% 以上**（外部API依存部分はモック）
- UI層: カバレッジ目標なし（手動テストで代替）

---

## 6. Streamlit 固有のガイドライン

### 6.1 状態管理

- `st.session_state` を唯一の状態管理手段とする
- 状態キーは定数として `config.py` に定義する
- ページ遷移時に状態が失われないよう注意する

```python
# config.py
SESSION_KEY_CLIENT = "current_client"
SESSION_KEY_CHART = "natal_chart"
SESSION_KEY_AI_RESPONSE = "ai_response"
```

### 6.2 コンポーネント分離

- UIロジックは `components/` に関数として切り出す
- ページファイル（`pages/`）はコンポーネントの組み合わせに専念する
- ビジネスロジックをページファイルに書かない

### 6.3 パフォーマンス

- `@st.cache_data` で計算結果をキャッシュする
- `@st.cache_resource` でDBコネクション等のリソースをキャッシュする
- 重い処理には `st.spinner()` でローディング表示を行う

---

## 7. セキュリティチェックリスト

### コードレビュー時の確認事項

- [ ] APIキーがハードコードされていないか
- [ ] 個人情報がログに出力されていないか
- [ ] `.env` が `.gitignore` に含まれているか
- [ ] SQLインジェクション対策（パラメータバインディング）がされているか
- [ ] エラーメッセージに内部情報が含まれていないか
