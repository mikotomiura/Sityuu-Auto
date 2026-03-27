# Sityuu-Auto — 占い・メンタリング支援システム

出品者（メンター）が相談者の生年月日を入力し、**四柱推命・算命学の命式を瞬時に算出**、AIが鑑定レポートや傾聴のヒントを生成するアプリケーションです。マルチユーザー認証・個別APIキー管理（BYOK）に対応しています。

## 主な機能

| 機能 | 説明 |
|------|------|
| 命式自動算出 | 生年月日から四柱推命の命式（年柱・月柱・日柱・時柱）を瞬時に算出 |
| 算命学データ | 十大主星・十二大従星・天中殺・エネルギー値を自動計算し人体星図を生成 |
| AI鑑定レポート | 命式と悩みから5セクション構成の詳細な鑑定レポートをAIが生成 |
| 傾聴ヒント | メンター向けの傾聴ガイド・声掛けフレーズをAIが提案 |
| 鑑定履歴 | 過去の鑑定結果を一覧表示・検索・詳細閲覧 |
| 相談者管理 | 相談者の基本情報を登録・編集・一覧表示 |
| PDFエクスポート | 鑑定結果をPDF形式でダウンロード |
| プロンプトテンプレート管理 | AIへ送信するシステムプロンプトを編集・切替可能 |
| ユーザー認証 | bcryptパスワードハッシュ、ログイン画面、セッション管理 |
| 招待リンクによるユーザー登録 | 管理者が生成したワンタイムURL（有効期限付き）からWebでアカウント登録 |
| 管理者ページ | ユーザー一覧・削除、招待リンク生成・管理（adminロール限定） |
| 個別APIキー管理（BYOK） | ユーザーごとにAPIキーを登録。ユーザーキー→システムキーの自動フォールバック |
| PII匿名化 | LLM API送信前に相談者の名前・フリガナを匿名化（デフォルトON、設定で切替可能） |
| プレミアムUIテーマ | ミッドナイトブルー・ゴールドアクセントの神秘的なカスタムCSS |

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
| 認証 | bcrypt |
| PDF出力 | reportlab |

## セットアップ

### 前提条件

- Python 3.11 以上
- pip（最新版推奨）
- Git
- LLM APIキー（Gemini / OpenAI / Anthropic のいずれか。BYOKによるUI登録も可）

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
# .env を編集し、APIキーを設定（BYOKを使う場合は空でもOK）
```

### APIキーの設定

APIキーは以下の **2つの方法** で設定できます。

**方法1: `.env` ファイル（システム共通キー）**

```env
# いずれか1つのAPIキーがあれば動作します
GEMINI_API_KEY=your-gemini-api-key       # Google AI Studio で取得（無料枠あり）
OPENAI_API_KEY=sk-your-key-here          # OpenAI
ANTHROPIC_API_KEY=sk-ant-your-key-here   # Anthropic

# 使用するプロバイダー（gemini / openai / anthropic）
DEFAULT_API_PROVIDER=gemini
DEFAULT_MODEL=gemini-2.5-flash
```

**方法2: BYOK（ユーザー個別キー登録）**

ログイン後、**設定 → アカウント設定** タブで各プロバイダーのAPIキーを登録できます。
ユーザー個別キーが登録されている場合、`.env` のシステムキーより優先して使用されます。

> Gemini API は無料枠があるため、MVP検証に最適です。
> [Google AI Studio](https://aistudio.google.com/) でAPIキーを取得できます。

### 起動

```bash
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

ユーザーアカウントは **招待リンク（推奨）** または CLIスクリプト で発行できます。

**方法1: 招待リンク（Web UI から発行・推奨）**

1. 管理者アカウントでログイン
2. サイドバーの **「管理」** ページへ移動
3. **「招待リンク管理」** タブで **「招待リンクを生成」** をクリック
4. 表示されたURL（例: `http://host:8501/?token=abc123...`）を登録希望者に共有
5. 登録希望者がURLにアクセスすると、ユーザー名・パスワード設定フォームが表示される
6. 登録完了後、ログイン画面からログイン可能

> 招待リンクはワンタイム（1回使用で無効化）で、有効期限（デフォルト72時間）を設定できます。

**方法2: CLIスクリプト**

```bash
# ランダムパスワードで発行（推奨）
python scripts/create_user.py <ユーザー名>

# パスワードを指定する場合
python scripts/create_user.py <ユーザー名> --password <パスワード>

# 管理者権限で発行
python scripts/create_user.py <ユーザー名> --role admin
```

実行するとユーザー名とパスワードがターミナルに表示されます。

**登録後、ユーザー自身が行えること：**

- **パスワードの変更**（設定 → アカウント設定）
- **自身のAPIキーの登録**（BYOK — 設定 → アカウント設定）

### 管理者ページ

adminロールのユーザーには、サイドバーに **「管理」** ページが表示されます。

| タブ | 機能 |
|------|------|
| ユーザー管理 | 登録ユーザーの一覧表示・削除（自分自身は削除不可） |
| 招待リンク管理 | 招待リンクの生成・一覧・ステータス確認・削除 |

## 使い方

1. **ログイン** — ユーザー名・パスワードでログイン
2. **相談者情報を入力** — 名前（仮名可）、生年月日、出生時間、悩みを入力
3. **命式を算出** — 「命式を算出して鑑定を開始」ボタンで命式を自動算出
4. **AI鑑定レポートを生成** — 「AI鑑定レポートを生成」ボタンで詳細な分析を取得
5. **結果をタブで確認** — 命式・人体星図・AI鑑定・傾聴ヒントを切り替えて閲覧

## プロジェクト構成

```
src/
├── app.py                    # Streamlit エントリーポイント（認証ゲート含む）
├── config.py                 # アプリケーション設定・セッションキー定義
├── db_init.py                # DB接続キャッシュ・初期データ投入
├── pages/
│   ├── 00_dashboard.py       # ダッシュボードページ（統計・概要表示）
│   ├── 01_reading.py         # 鑑定ページ（入力→算出→AI生成→表示）
│   ├── 02_history.py         # 鑑定履歴ページ（一覧・検索・詳細）
│   ├── 03_clients.py         # 相談者管理ページ（CRUD）
│   ├── 04_settings.py        # 設定ページ（API・プライバシー・テンプレート・アカウント）
│   └── 05_admin.py           # 管理者ページ（ユーザー管理・招待リンク）
├── components/               # 再利用可能UIコンポーネント
│   ├── input_form.py         # 入力フォーム
│   ├── natal_chart_display.py # 命式表表示
│   ├── reading_result.py     # 鑑定結果表示
│   ├── history_table.py      # 履歴テーブル
│   ├── pdf_export.py         # PDFエクスポート
│   └── theme.py              # プレミアムUIテーマ（カスタムCSS）
├── fortune_engine/           # 命式計算エンジン（ロジック層）
│   ├── calculator.py         # 四柱推命の命式算出
│   ├── sanmei.py             # 算命学データ算出
│   ├── models.py             # データモデル（Pydantic）
│   ├── constants.py          # 定数（干支・五行・星の対応表）
│   └── formatter.py          # 命式データのフォーマッタ
├── ai_service/               # AI連携層
│   ├── client.py             # LLM APIクライアント（Gemini/OpenAI/Anthropic）
│   ├── prompt_builder.py     # プロンプト構築
│   ├── pii_sanitizer.py      # PII匿名化（API送信前の名前・フリガナ置換）
│   ├── models.py             # AI応答データモデル
│   └── templates/            # プロンプトテンプレート（Markdown）
├── db_service/               # DB層
│   ├── database.py           # DB接続・マイグレーション実行
│   ├── models.py             # DBレコード定義（dataclass）
│   ├── repositories/         # リポジトリパターン
│   │   ├── client_repo.py    # 相談者リポジトリ
│   │   ├── session_repo.py   # 鑑定セッションリポジトリ
│   │   ├── prompt_template_repo.py # テンプレートリポジトリ
│   │   ├── user_repo.py      # ユーザーリポジトリ（認証・BYOK）
│   │   ├── invitation_repo.py # 招待トークンリポジトリ
│   │   └── auth_session_repo.py # 認証セッションリポジトリ
│   └── migrations/           # SQLマイグレーション
└── utils/                    # 共通ユーティリティ
    ├── auth.py               # 認証（ログイン・セッション管理）
    ├── exceptions.py         # カスタム例外
    ├── logger.py             # ロギング設定
    ├── validators.py         # バリデーション
    ├── text_utils.py         # テキスト処理
    └── privacy.py            # ブラウザ向けプライバシー制御（autocomplete無効化CSS）

scripts/
├── init_db.py                # DB初期化スクリプト
├── create_user.py            # ユーザーアカウント発行スクリプト
└── seed_data.py              # テストデータ投入スクリプト

tests/
├── unit/                     # ユニットテスト（306件）
├── fixtures/                 # テスト用フィクスチャ
└── integration/              # 統合テスト
```

## 開発

### テスト・リント

```bash
# テスト実行
pytest tests/ -v

# カバレッジ付き
pytest --cov=src --cov-report=html

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
- **招待トークン**: `secrets.token_urlsafe(32)` で生成（256ビット相当）。ワンタイム・有効期限付き
- **管理者ページ保護**: ナビゲーション制御＋ページ内ロールチェック＋`st.stop()` による二重防御
- **APIキー**: `.env` ファイルで管理（Git管理外）。ユーザー個別キーはDBに保存
- **個人情報**: ローカルSQLiteにのみ保存、クラウドに送信しない
- **PII匿名化**: LLM API送信前に名前・フリガナを「相談者様」に置換（デフォルトON）。設定ページで切替可能
- **ログ**: 個人情報（名前・生年月日・悩み・パスワード）はログに出力しない
- **SQLインジェクション対策**: 全クエリでパラメータバインディングを使用
- **DBファイル権限**: macOS/Linuxでは所有者のみ読み書き可（0o600）

## ライセンス

Private — All rights reserved.
