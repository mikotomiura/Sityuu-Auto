# Sityuu-Auto-占い・メンタリング支援ローカルシステム-

出品者（メンター）が自身のPC上で相談者の生年月日を入力し、四柱推命・算命学の命式を瞬時に算出、AIが鑑定テキストのベースや傾聴のヒントを出力するローカルファーストのデスクトップアプリケーション。

- ローカルPC（Windows / macOS）で動作
- 外部通信は LLM API 呼び出しのみ
- データは SQLite でローカル保存

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| 言語 | Python 3.11+ |
| UI | Streamlit |
| 命式計算 | lunar_python |
| データベース | SQLite |
| AI連携 | OpenAI API / Anthropic API |
| データモデル | Pydantic |

## セットアップ

### 前提条件

- Python 3.11 以上
- pip（最新版推奨）
- Git

### 手順

```bash
# 1. リポジトリのクローン
git clone https://github.com/mikotomiura/AI-paper-Canvas_demo.git
cd AI-paper-Canvas_demo

# 2. 仮想環境の作成・有効化
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. 依存パッケージのインストール（開発用含む）
pip install -e ".[dev]"

# 4. 環境変数の設定
cp .env.example .env
# .env を編集し、APIキーを設定

# 5. データベースの初期化
python scripts/init_db.py

# 6. アプリケーションの起動
streamlit run src/app.py
```

### 動作確認

```bash
# テスト実行
pytest tests/ -v

# リント
ruff check src/ tests/

# 型チェック
mypy src/

# フォーマット確認
ruff format --check src/ tests/
```
