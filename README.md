# Sityuu-Auto — 占い・メンタリング支援ローカルシステム

出品者（メンター）が自身のPC上で相談者の生年月日を入力し、**四柱推命・算命学の命式を瞬時に算出**、AIが鑑定レポートや傾聴のヒントを生成するローカルファーストのデスクトップアプリケーションです。

## 主な機能

| 機能 | 説明 |
|------|------|
| 命式自動算出 | 生年月日から四柱推命の命式（年柱・月柱・日柱・時柱）を瞬時に算出 |
| 算命学データ | 十大主星・十二大従星・天中殺・エネルギー値を自動計算し人体星図を生成 |
| AI鑑定レポート | 命式と悩みから5セクション構成の詳細な鑑定レポートをAIが生成 |
| 傾聴ヒント | メンター向けの傾聴ガイド・声掛けフレーズをAIが提案 |
| タブ表示 | 命式・人体星図・AI鑑定・傾聴ヒントをタブで切り替えて閲覧 |

### AI鑑定レポートの構成

1. **命式の総合評価** — 日干の特徴、五行バランスの解釈、人体星図の分析
2. **強みと課題** — 最大の強み、潜在的才能、注意すべき課題（テーブル形式）
3. **悩みに対する占術的解釈** — 命式と悩みの関連分析、乗り越えのヒント
4. **具体的なアドバイス** — 命式の根拠を明示した5項目
5. **メンター向け傾聴ガイド** — 響きやすい言葉の傾向、声掛けフレーズ

## 技術スタック

| カテゴリ | 技術 |
|----------|------|
| 言語 | Python 3.11+ |
| UI | Streamlit |
| 命式計算 | lunar_python |
| データベース | SQLite |
| AI連携 | Google Gemini API / OpenAI API / Anthropic API |
| データモデル | Pydantic v2 |

## セットアップ

### 前提条件

- Python 3.11 以上
- pip（最新版推奨）
- Git
- LLM APIキー（Gemini / OpenAI / Anthropic のいずれか）

### インストール

```bash
# 1. リポジトリのクローン
git clone https://github.com/mikotomiura/Sityuu-Auto.git
cd Sityuu-Auto

# 2. 仮想環境の作成・有効化
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows

# 3. 依存パッケージのインストール（開発用含む）
pip install -e ".[dev]"

# 4. 環境変数の設定
cp .env.example .env
# .env を編集し、APIキーを設定
```

### APIキーの設定

`.env` ファイルを編集して、使用するプロバイダーのAPIキーを設定してください。

```env
# いずれか1つのAPIキーがあれば動作します
GEMINI_API_KEY=your-gemini-api-key       # Google AI Studio で取得（無料枠あり）
OPENAI_API_KEY=sk-your-key-here          # OpenAI
ANTHROPIC_API_KEY=sk-ant-your-key-here   # Anthropic

# 使用するプロバイダー（gemini / openai / anthropic）
DEFAULT_API_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.5-flash
```

> Gemini API は無料枠があるため、MVP検証に最適です。
> [Google AI Studio](https://aistudio.google.com/) でAPIキーを取得できます。

### 起動

```bash
# データベースの初期化
python scripts/init_db.py

# アプリケーションの起動
streamlit run src/app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

### 初回ログイン

アプリを初めて起動すると、管理者アカウントがランダムパスワードで自動生成されます。
**ターミナルに表示されるパスワードを控えてください。**

```
==================================================
  初期管理者アカウント
  ユーザー名: admin
  パスワード: aB3kLm9xQr7z   ← ランダム生成される
  ※ 初回ログイン後に必ず変更してください
==================================================
```

1. 表示されたユーザー名・パスワードでログイン
2. **設定 → アカウント設定** タブでパスワードを変更

### ユーザーアカウントの発行

顧客用アカウントはCLIスクリプトで発行します。

```bash
# ランダムパスワードで発行（推奨）
python scripts/create_user.py <ユーザー名>

# パスワードを指定する場合
python scripts/create_user.py <ユーザー名> --password <パスワード>

# 管理者権限で発行
python scripts/create_user.py <ユーザー名> --role admin
```

実行するとユーザー名とパスワードがターミナルに表示されます。
この情報を顧客に伝え、顧客自身がログイン後に以下を行えます：

- **パスワードの変更**（設定 → アカウント設定）
- **自身のAPIキーの登録**（BYOK — 設定 → アカウント設定）

> ユーザーが個人のAPIキーを登録すると、そのキーがシステムの `.env` キーより優先して使用されます。

## 使い方

1. **相談者情報を入力** — 名前（仮名可）、生年月日、出生時間、悩みを入力
2. **命式を算出** — 「命式を算出して鑑定を開始」ボタンで命式を自動算出
3. **AI鑑定レポートを生成** — 「AI鑑定レポートを生成」ボタンで詳細な分析を取得
4. **結果をタブで確認** — 命式・人体星図・AI鑑定・傾聴ヒントを切り替えて閲覧

## プロジェクト構成

```
src/
├── app.py                    # Streamlit エントリーポイント
├── config.py                 # アプリケーション設定
├── pages/
│   └── 01_reading.py         # 鑑定ページ
├── components/               # 再利用可能UIコンポーネント
│   ├── input_form.py         # 入力フォーム
│   ├── natal_chart_display.py # 命式表表示
│   └── reading_result.py     # 鑑定結果表示
├── fortune_engine/           # 命式計算エンジン
│   ├── calculator.py         # 四柱推命の命式算出
│   ├── sanmei.py             # 算命学データ算出
│   ├── models.py             # データモデル（Pydantic）
│   ├── constants.py          # 定数（干支・五行・星の対応表）
│   └── formatter.py          # 命式データのフォーマッタ
├── ai_service/               # AI連携層
│   ├── client.py             # LLM APIクライアント（Gemini/OpenAI/Anthropic）
│   ├── prompt_builder.py     # プロンプト構築
│   └── templates/            # プロンプトテンプレート
└── db_service/               # DB層
    ├── database.py           # DB接続・初期化
    └── repositories/         # リポジトリパターン
```

## 開発

### テスト・リント

```bash
# テスト実行
pytest tests/ -v

# リント
ruff check src/ tests/

# 型チェック
mypy src/

# フォーマット
ruff format src/ tests/
```

### コミット規約

[Conventional Commits](https://www.conventionalcommits.org/) に従います。

```
feat(scope): 新機能の説明
fix(scope): バグ修正の説明
refactor(scope): リファクタリングの説明
```

## セキュリティ

- **認証**: bcryptによるパスワードハッシュ化、ログイン失敗時の漸増遅延（ブルートフォース対策）
- **APIキー**: `.env` ファイルで管理（Git管理外）。ユーザー個別キーはDBに保存
- **個人情報**: ローカルSQLiteにのみ保存、クラウドに送信しない
- **ログ**: 個人情報（名前・生年月日・悩み・パスワード）はログに出力しない

## ライセンス

Private — All rights reserved.
