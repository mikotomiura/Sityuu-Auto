# 技術設計書（architecture.md）

## 1. アーキテクチャ概要

### 1.1 設計思想

- **ローカルファースト:** すべてのデータと処理をローカルPC上で完結させる
- **レイヤードアーキテクチャ:** UI層・ロジック層・AI連携層・DB層の4層構造
- **シングルユーザー:** 同時利用者は1名。認証機構は不要
- **外部依存最小化:** 外部通信は LLM API のみ

### 1.2 技術スタック

| レイヤー | 技術 | バージョン | 目的 |
|----------|------|-----------|------|
| フロントエンド/バックエンド | Streamlit | 1.38+ | Web UI構築（ローカルサーバー） |
| 命式計算 | lunar_python | 1.3+ | 太陰暦変換・干支算出・四柱推命計算 |
| AI文章生成 | OpenAI API / Anthropic API | — | 鑑定テキスト・傾聴ヒントの生成 |
| データベース | SQLite3 | Python標準 | ローカルデータ永続化 |
| 環境変数管理 | python-dotenv | 1.0+ | APIキー等の秘匿情報管理 |
| データバリデーション | Pydantic | 2.0+ | 入出力データの型安全性担保 |
| テスト | pytest | 8.0+ | ユニットテスト・統合テスト |

### 1.3 アーキテクチャ図

```
┌─────────────────────────────────────────────────┐
│                    ブラウザ                        │
│              (localhost:8501)                      │
└─────────────────┬───────────────────────────────┘
                  │ HTTP (ローカルのみ)
┌─────────────────▼───────────────────────────────┐
│              UI層 (Streamlit)                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐  │
│  │入力フォーム│ │結果表示   │ │履歴・管理画面    │  │
│  └────┬─────┘ └────▲─────┘ └────▲──────────────┘  │
└───────┼────────────┼────────────┼────────────────┘
        │            │            │
┌───────▼────────────┴────────────┴────────────────┐
│            ロジック層 (fortune_engine)             │
│  ┌──────────────┐  ┌──────────────────────────┐  │
│  │命式算出モジュール│  │算命学算出モジュール         │  │
│  │(lunar_python) │  │(独自ロジック)              │  │
│  └──────┬───────┘  └──────────┬───────────────┘  │
│         │                     │                   │
│  ┌──────▼─────────────────────▼───────────────┐  │
│  │       NatalChart (命式データオブジェクト)       │  │
│  └──────────────────┬─────────────────────────┘  │
└─────────────────────┼────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼───────┐ ┌──▼──────────┐ ┌▼──────────────┐
│ AI連携層       │ │             │ │ DB層           │
│ (ai_service)  │ │             │ │ (db_service)   │
│ ┌───────────┐ │ │             │ │ ┌────────────┐ │
│ │Prompt     │ │ │             │ │ │SQLite      │ │
│ │Builder    │ │ │             │ │ │Repository  │ │
│ └─────┬─────┘ │ │             │ │ └──────┬─────┘ │
│       │       │ │             │ │        │       │
│ ┌─────▼─────┐ │ │             │ │ ┌──────▼─────┐ │
│ │API Client │ │ │             │ │ │fortune.db  │ │
│ │(OpenAI/   │ │ │             │ │ │(SQLiteファイル)│ │
│ │Anthropic) │ │ │             │ │ └────────────┘ │
│ └─────┬─────┘ │ │             │ └────────────────┘
│       │       │ │             │
└───────┼───────┘ │             │
        │ HTTPS   │             │
┌───────▼───────┐ │             │
│ 外部LLM API   │ │             │
│ (クラウド)     │ │             │
└───────────────┘ │             │
                  │             │
```

---

## 2. レイヤー詳細設計

### 2.1 UI層（Streamlit）

**責務:** ユーザーインターフェースの提供。入力受付と結果表示。

**設計方針:**
- Streamlit のマルチページ機能を使用（`pages/` ディレクトリ）
- `st.session_state` でページ間の状態を管理
- コンポーネントは再利用可能な関数として `components/` に切り出す

**ページ構成:**

| ファイル | ページ | 機能 |
|----------|--------|------|
| `app.py` | メイン | エントリーポイント・ナビゲーション |
| `pages/01_reading.py` | 鑑定 | 入力フォーム → 命式算出 → AI鑑定 → 結果表示 |
| `pages/02_history.py` | 履歴 | 鑑定履歴一覧・詳細表示 |
| `pages/03_clients.py` | 相談者管理 | 相談者の登録・編集・一覧 |
| `pages/04_settings.py` | 設定 | API設定・プロンプトテンプレート管理 |

**状態管理:**
```python
# session_state で管理するキー
st.session_state.current_client: Client | None        # 現在の相談者
st.session_state.natal_chart: NatalChart | None        # 算出済み命式
st.session_state.ai_response: AIResponse | None        # AI生成テキスト
st.session_state.api_provider: Literal["openai", "anthropic"]  # APIプロバイダー
```

---

### 2.2 ロジック層（fortune_engine）

**責務:** 命式の算出と算命学データの計算。ビジネスロジックの中核。

**モジュール構成:**

```
fortune_engine/
├── __init__.py
├── calculator.py        # 四柱推命の命式算出（lunar_python利用）
├── sanmei.py            # 算命学の星・天中殺算出（独自ロジック）
├── models.py            # データモデル定義（Pydantic）
├── constants.py         # 定数定義（十干・十二支・五行・星の対応表）
└── formatter.py         # 命式データの文字列フォーマット
```

**データモデル（Pydantic）:**

```python
from pydantic import BaseModel
from datetime import date, time
from enum import Enum

class FiveElement(str, Enum):
    WOOD = "木"
    FIRE = "火"
    EARTH = "土"
    METAL = "金"
    WATER = "水"

class Pillar(BaseModel):
    """四柱の1柱を表す"""
    stem: str           # 天干（甲〜癸）
    branch: str         # 地支（子〜亥）
    element: FiveElement  # 五行属性

class NatalChart(BaseModel):
    """四柱推命の命式"""
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar | None  # 出生時間不明の場合はNone
    day_stem: str               # 日干（最重要）
    five_elements_balance: dict[FiveElement, int]

class SanmeiData(BaseModel):
    """算命学データ"""
    center_star: str              # 中心星（十大主星）
    north_star: str               # 北方星
    south_star: str               # 南方星
    east_star: str                # 東方星
    west_star: str                # 西方星
    tenchusatsu: str              # 天中殺（例: "戌亥"）
    twelve_stars: list[str]       # 十二大従星のリスト
```

---

### 2.3 AI連携層（ai_service）

**責務:** LLM API との通信、プロンプト構築、レスポンス解析。

**モジュール構成:**

```
ai_service/
├── __init__.py
├── client.py            # APIクライアント（OpenAI/Anthropic切替）
├── prompt_builder.py    # プロンプト構築
├── templates/           # プロンプトテンプレート（Markdown）
│   ├── reading_base.md  # 鑑定テキスト生成用
│   └── listening_hint.md # 傾聴ヒント生成用
└── models.py            # AI応答のデータモデル
```

**APIクライアント設計（Strategy パターン）:**

```python
from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass

class OpenAIClient(LLMClient):
    """OpenAI API クライアント"""
    pass

class AnthropicClient(LLMClient):
    """Anthropic API クライアント"""
    pass

def create_client(provider: str) -> LLMClient:
    """ファクトリ関数"""
    if provider == "openai":
        return OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient()
    raise ValueError(f"Unknown provider: {provider}")
```

---

### 2.4 DB層（db_service）

**責務:** SQLite を用いたデータの永続化と検索。

**モジュール構成:**

```
db_service/
├── __init__.py
├── database.py          # DB接続・初期化
├── repositories/
│   ├── __init__.py
│   ├── client_repo.py   # 相談者リポジトリ
│   └── session_repo.py  # セッション（鑑定履歴）リポジトリ
├── models.py            # DBモデル定義
└── migrations/          # スキーママイグレーション
    └── 001_initial.sql
```

**テーブル設計:**

```sql
-- 相談者テーブル
CREATE TABLE clients (
    id TEXT PRIMARY KEY,           -- UUID
    name TEXT NOT NULL,            -- 名前（仮名可）
    birth_date TEXT NOT NULL,      -- 生年月日（ISO 8601）
    birth_time TEXT,               -- 出生時間（HH:MM or NULL）
    gender TEXT,                   -- 性別
    notes TEXT,                    -- メモ
    created_at TEXT NOT NULL,      -- 作成日時
    updated_at TEXT NOT NULL       -- 更新日時
);

-- 鑑定セッションテーブル
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,           -- UUID
    client_id TEXT NOT NULL,       -- 相談者ID
    concern TEXT NOT NULL,         -- 悩みテキスト
    natal_chart_json TEXT NOT NULL, -- 命式データ（JSON）
    sanmei_data_json TEXT,         -- 算命学データ（JSON）
    ai_reading_text TEXT,          -- AI鑑定テキスト
    ai_listening_hints TEXT,       -- 傾聴ヒント
    mentor_notes TEXT,             -- 出品者メモ
    api_provider TEXT,             -- 使用APIプロバイダー
    api_model TEXT,                -- 使用モデル
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- プロンプトテンプレートテーブル
CREATE TABLE prompt_templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    system_prompt TEXT NOT NULL,
    description TEXT,
    is_default INTEGER DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 3. エラーハンドリング戦略

| レイヤー | エラーケース | 対応 |
|----------|------------|------|
| UI層 | 入力バリデーションエラー | Streamlit の `st.error()` で即座にフィードバック |
| ロジック層 | 無効な日付・算出不能 | `FortuneCalculationError` を送出し、UI層で捕捉して表示 |
| AI連携層 | API接続エラー | 1回リトライ → 失敗時はエラー表示。オフライン時は命式のみ表示 |
| AI連携層 | APIキー未設定 | 設定画面への導線を表示 |
| AI連携層 | レート制限 | 待機時間を表示し、ユーザーにリトライを促す |
| DB層 | DB ファイル破損 | バックアップからの復元手順を表示 |

**カスタム例外クラス:**

```python
class FortuneAppError(Exception):
    """アプリケーション基底例外"""
    pass

class FortuneCalculationError(FortuneAppError):
    """命式算出エラー"""
    pass

class AIServiceError(FortuneAppError):
    """AI連携エラー"""
    pass

class DatabaseError(FortuneAppError):
    """DB操作エラー"""
    pass
```

---

## 4. セキュリティ設計

### 4.1 APIキー管理

- `.env` ファイルにAPIキーを格納（`.gitignore` に登録必須）
- `python-dotenv` で読み込み
- アプリ起動時にAPIキーの存在チェック

```
# .env
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
DEFAULT_API_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

### 4.2 個人情報保護

- 個人情報はSQLiteファイル内にのみ保存（クラウド非送信）
- LLM API への送信時、名前は仮名/イニシャルに置換するオプションを提供
- ログ出力時に個人情報をマスキング
- OS のディスク暗号化（BitLocker/FileVault）の有効化を推奨

### 4.3 データバックアップ

- SQLite ファイル（`fortune.db`）の手動コピーで対応
- 将来的に自動バックアップ機能を追加（日次でファイルコピー）

---

## 5. パフォーマンス目標

| 処理 | 目標時間 |
|------|----------|
| 命式算出 | < 1秒 |
| 算命学データ算出 | < 1秒 |
| AI鑑定テキスト生成 | < 30秒 |
| 鑑定履歴検索 | < 1秒 |
| アプリ起動 | < 5秒 |

---

## 6. 将来拡張

| 項目 | 概要 | 優先度 |
|------|------|--------|
| Ollama連携 | ローカルLLMでの完全オフライン稼働 | 中 |
| デスクトップアプリ化 | stlite/electron-builderでのパッケージング | 低 |
| レポートPDF出力 | 鑑定結果をPDFとして出力 | 中 |
| 複数テンプレート | 相談内容に応じたプロンプト切替 | 中 |
