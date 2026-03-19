# /setup — 開発環境セットアップワークフロー

開発環境を初期構築する際のワークフロー。依存関係→設定→DB初期化→動作確認の順に実行する。

---

## 1. 前提条件の確認

以下がインストールされていることを確認：

- Python 3.11 以上
- pip（最新版推奨）
- Git

```bash
python --version   # 3.11 以上であること
pip --version
git --version
```

## 2. リポジトリのクローン

```bash
git clone https://github.com/mikotomiura/AI-paper-Canvas_demo.git
cd AI-paper-Canvas_demo
```

## 3. 仮想環境の作成

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

## 4. 依存パッケージのインストール

```bash
# 本番 + 開発依存をインストール
pip install -e ".[dev]"
```

**サブエージェント `dependency-checker` を起動** し、依存関係の問題がないか確認。

## 5. 環境変数の設定

```bash
# テンプレートからコピー
cp .env.example .env
```

`.env` ファイルを編集し、APIキーを設定：

```
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
DEFAULT_API_PROVIDER=anthropic
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

**注意:** `.env` が `.gitignore` に含まれていることを確認する。

## 6. データベースの初期化

```bash
python scripts/init_db.py
```

- `data/` ディレクトリが作成されること
- `data/fortune.db` が生成されること
- テーブル（clients, sessions, prompt_templates）が作成されること

## 7. 動作確認

### 7.1 テストの実行

```bash
pytest tests/ -v
```

全テストが通過することを確認する。

### 7.2 アプリケーションの起動

```bash
streamlit run src/app.py
```

- ブラウザで `http://localhost:8501` が開くこと
- メインページが表示されること
- ナビゲーションが機能すること

### 7.3 静的解析

```bash
# リント
ruff check src/ tests/

# 型チェック
mypy src/

# フォーマット確認
ruff format --check src/ tests/
```

**サブエージェント `build-executor` を起動** し、ビルド確認を実行。

## 8. 設計ドキュメントの確認

以下のドキュメントに一通り目を通し、プロジェクトの理解を深める：

1. `CLAUDE.md`
2. `docs/glossary.md`
3. `docs/functional-design.md`
4. `docs/architecture.md`
5. `docs/repository-structure.md`
6. `docs/development-guidelines.md`

## 9. セットアップ完了チェックリスト

- [ ] Python 3.11+ がインストールされている
- [ ] 仮想環境が作成・有効化されている
- [ ] 依存パッケージがインストールされている
- [ ] `.env` ファイルが設定されている
- [ ] `.env` が `.gitignore` に含まれている
- [ ] データベースが初期化されている
- [ ] テストが全件通過する
- [ ] アプリケーションが起動する
- [ ] リント・型チェックがエラーなし
