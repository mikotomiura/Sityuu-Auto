# リポジトリ構造定義書（repository-structure.md）

## リポジトリURL

https://github.com/mikotomiura/AI-paper-Canvas_demo.git

---

## ディレクトリ構造

```
fortune-mentoring-system/
│
├── CLAUDE.md                          # Claude Code 設定・作業ガイド
├── README.md                          # プロジェクト概要・セットアップ手順
├── pyproject.toml                     # プロジェクト設定・依存関係定義
├── .env.example                       # 環境変数テンプレート
├── .gitignore                         # Git除外設定
│
├── docs/                              # 📖 設計ドキュメント
│   ├── functional-design.md           #   機能設計書
│   ├── architecture.md                #   技術設計書
│   ├── repository-structure.md        #   リポジトリ構造定義書（本ファイル）
│   ├── development-guidelines.md      #   開発ガイドライン
│   └── glossary.md                    #   ユビキタス言語定義
│
├── .steering/                         # 📝 構造化ノート（作業記録）
│   └── [YYYYMMDD]-[タスク名]/
│       ├── requirement.md             #   要件定義
│       ├── design.md                  #   設計メモ
│       ├── tasklist.md                #   タスクリスト
│       ├── blockers.md                #   ブロッカー記録（オプション）
│       └── decisions.md               #   意思決定記録（オプション）
│
├── .claude/                           # 🤖 Claude Code 拡張設定
│   ├── agents/                        #   サブエージェント定義
│   │   ├── code-reviewer.md
│   │   ├── test-analyzer.md
│   │   ├── security-checker.md
│   │   ├── impact-analyzer.md
│   │   ├── dependency-checker.md
│   │   ├── file-finder.md
│   │   ├── test-runner.md
│   │   ├── build-executor.md
│   │   └── log-analyzer.md
│   ├── commands/                      #   スラッシュコマンド
│   │   ├── add-feature.md
│   │   ├── fix-bug.md
│   │   ├── refactor.md
│   │   ├── review.md
│   │   ├── test.md
│   │   └── setup.md
│   └── skills/                        #   スキル定義
│       ├── streamlit-standards/
│       │   ├── SKILL.md
│       │   └── examples.md
│       ├── python-standards/
│       │   ├── SKILL.md
│       │   └── examples.md
│       ├── test-standards/
│       │   ├── SKILL.md
│       │   └── examples.md
│       ├── api-integration/
│       │   ├── SKILL.md
│       │   └── examples.md
│       └── sqlite-standards/
│           ├── SKILL.md
│           └── examples.md
│
├── src/                               # 🔧 アプリケーションソースコード
│   ├── __init__.py
│   ├── app.py                         #   Streamlit エントリーポイント
│   ├── config.py                      #   アプリケーション設定
│   │
│   ├── pages/                         #   Streamlit マルチページ
│   │   ├── 01_reading.py              #     鑑定ページ
│   │   ├── 02_history.py              #     鑑定履歴ページ
│   │   ├── 03_clients.py              #     相談者管理ページ
│   │   ├── 04_settings.py             #     設定ページ
│   │   └── 05_admin.py               #     管理者ページ（招待リンク・ユーザー管理）
│   │
│   ├── components/                    #   再利用可能UIコンポーネント
│   │   ├── __init__.py
│   │   ├── input_form.py              #     相談者情報入力フォーム
│   │   ├── natal_chart_display.py     #     命式表表示
│   │   ├── reading_result.py          #     鑑定結果表示
│   │   ├── history_table.py           #     履歴テーブル
│   │   ├── pdf_export.py             #     PDFエクスポート
│   │   └── theme.py                  #     プレミアムUIテーマ（カスタムCSS注入）
│   │
│   ├── fortune_engine/                #   命式計算エンジン（ロジック層）
│   │   ├── __init__.py
│   │   ├── calculator.py              #     四柱推命の命式算出
│   │   ├── sanmei.py                  #     算命学データ算出
│   │   ├── models.py                  #     データモデル（Pydantic）
│   │   ├── constants.py               #     定数（干支・五行・星の対応表）
│   │   └── formatter.py               #     命式データのフォーマッタ
│   │
│   ├── ai_service/                    #   AI連携層
│   │   ├── __init__.py
│   │   ├── client.py                  #     LLM APIクライアント
│   │   ├── prompt_builder.py          #     プロンプト構築
│   │   ├── pii_sanitizer.py           #     PII匿名化（API送信前の名前・フリガナ置換）
│   │   ├── models.py                  #     AI応答データモデル
│   │   └── templates/                 #     プロンプトテンプレート
│   │       ├── reading_base.md        #       鑑定テキスト生成用
│   │       └── listening_hint.md      #       傾聴ヒント生成用
│   │
│   ├── db_service/                    #   DB層
│   │   ├── __init__.py
│   │   ├── database.py                #     DB接続・初期化
│   │   ├── models.py                  #     DBモデル定義
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── client_repo.py         #     相談者リポジトリ
│   │   │   ├── session_repo.py        #     セッションリポジトリ
│   │   │   ├── prompt_template_repo.py #    プロンプトテンプレートリポジトリ
│   │   │   ├── user_repo.py           #     ユーザーリポジトリ（認証・BYOK）
│   │   │   ├── invitation_repo.py     #     招待トークンリポジトリ
│   │   │   └─��� password_reset_repo.py #    パスワードリセットトークンリポ��トリ
│   │   └── migrations/
│   │       ├── 001_initial.sql        #     初期スキーマ
│   │       ├── 003_add_users.sql      #     ユーザー管理テーブル
│   │       ├── 004_add_invitation_tokens.sql #  招待トークンテーブル
│   │       ├── 007_add_password_reset_tokens.sql # パスワードリセットトークンテーブル
│   │       └── 008_add_email_to_users.sql #      ユーザーテーブルにメール列追加
│   │
│   └── utils/                         #   共通ユーティリティ
│       ├── __init__.py
│       ├── auth.py                    #     認証ユーティリティ（ログイン・セッション管理・セルフリセット）
│       ├── email_sender.py            #     メール送信ユーティリティ（SMTP経由リセットリンク送信）
│       ├── exceptions.py              #     カスタム例外定義
│       ├── logger.py                  #     ロギング設定
│       └── validators.py              #     バリデーション関数
│
├── tests/                             # 🧪 テスト
│   ├── __init__.py
│   ├── conftest.py                    #   テスト共通フィクスチャ
│   ├── unit/                          #   ユニットテスト
│   │   ├── __init__.py
│   │   ├── test_calculator.py
│   │   ├── test_sanmei.py
│   │   ├── test_prompt_builder.py
│   │   ├── test_prompt_template_repo.py
│   │   ├── test_pdf_export.py
│   │   ├── test_validators.py
│   │   ├── test_ai_models.py
│   │   └── test_logger.py
│   ├── integration/                   #   統合テスト
│   │   ├── __init__.py
│   │   ├── test_fortune_flow.py
│   │   ├── test_db_operations.py
│   │   └── test_history_queries.py
│   └── fixtures/                      #   テストデータ
│       ├── sample_clients.json
│       └── expected_natal_charts.json
│
├── data/                              # 💾 ローカルデータ（.gitignore対象）
│   └── fortune.sqlite3                     #   SQLiteデータベースファイル
│
└── scripts/                           # 🔨 ユーティリティスクリプト
    ├── init_db.py                     #   DB初期化スクリプト
    ├── create_user.py                 #   ユーザーアカウント発行スクリプト
    └── seed_data.py                   #   テストデータ投入スクリプト
```

---

## 配置ルール

### ファイル配置の原則

| ルール | 説明 |
|--------|------|
| ソースコードは `src/` 配下 | アプリケーションコードはすべて `src/` 内に配置 |
| テストは `tests/` 配下 | テストコードは `tests/` 内に、`src/` のディレクトリ構造をミラー |
| 設計ドキュメントは `docs/` 配下 | 永続的な設計ドキュメントはすべて `docs/` に配置 |
| 作業記録は `.steering/` 配下 | セッション単位の作業記録はすべて `.steering/` に配置 |
| Claude 設定は `.claude/` 配下 | サブエージェント・コマンド・スキルは `.claude/` に配置 |
| データファイルは `data/` 配下 | SQLite DB等の永続データは `data/` に配置（Git管理外） |

### 新規ファイル作成時のチェックリスト

- [ ] 適切なディレクトリに配置しているか
- [ ] `__init__.py` が必要な場合、作成しているか
- [ ] テストファイルを同時に作成しているか
- [ ] 型ヒントを付与しているか
- [ ] docstring を記述しているか

---

## .gitignore に含めるべきファイル

```gitignore
# 環境変数
.env

# ローカルデータ
data/fortune.sqlite3
data/*.db

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# 作業記録（プロジェクトに応じて含めるか判断）
# .steering/
```

---

## パッケージ管理

本プロジェクトでは `pyproject.toml` でパッケージと依存関係を管理する。

```toml
[project]
name = "fortune-mentoring-system"
version = "0.1.0"
description = "占い・メンタリング支援ローカルシステム"
requires-python = ">=3.11"
dependencies = [
    "streamlit>=1.38",
    "lunar-python>=1.3",
    "openai>=1.0",
    "anthropic>=0.30",
    "python-dotenv>=1.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.5",
    "mypy>=1.10",
]
```
