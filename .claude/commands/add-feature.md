# /add-feature — 新機能追加ワークフロー

新機能を追加する際の完全なワークフロー。設計理解→既存パターン調査→実装→テスト→ドキュメント更新の順に実行する。

---

## 1. プロジェクト理解

以下のドキュメントを順番に読み、プロジェクトの全体像を理解する：

1. `CLAUDE.md` を読む — プロジェクト概要と作業ルールを確認
2. `docs/glossary.md` を読む — 用語の定義を確認（命名に使用）
3. `docs/functional-design.md` を読む — 既存の機能一覧と今回追加する機能の位置づけを確認
4. `docs/architecture.md` を読む — レイヤー構造（UI→ロジック→AI連携→DB）を確認
5. `docs/repository-structure.md` を読む — ファイルの配置先を確認

## 2. 構造化ノートの作成

`.steering/[YYYYMMDD]-[タスク名]/` ディレクトリを作成し、以下のファイルを初期化：

- `requirement.md` — 今回の機能の要件（目的、受け入れ条件、スコープ）を記述
- `design.md` — 空のテンプレートを配置（Step 3 で記入）
- `tasklist.md` — 空のテンプレートを配置（Step 3 で記入）

## 3. 既存パターンの調査

追加する機能に最も近い既存の実装を調査する：

1. `Grep` で類似の機能・パターンを検索
2. 既存のコンポーネント構造を確認（`src/components/`）
3. データモデルの定義を確認（`src/fortune_engine/models.py`, `src/db_service/models.py`）
4. 調査結果を `.steering/[今回]/design.md` に記録

## 4. 設計

1. 変更が必要なファイルを特定し、`design.md` に記載
2. 新規ファイルが必要な場合、配置先を `repository-structure.md` に照らして決定
3. データモデルの変更が必要な場合、Pydantic モデルの設計を先に行う
4. **サブエージェント `impact-analyzer` を起動** し、影響範囲を確認
5. タスクを `tasklist.md` にチェックリスト形式で記載

## 5. 実装

`tasklist.md` のタスクを上から順に実行する。実装時の原則：

1. **データモデルから実装**する（`models.py`）
2. **ロジック層**を実装する（`fortune_engine/` or `ai_service/` or `db_service/`）
3. **UIコンポーネント**を実装する（`components/`）
4. **ページ**に組み込む（`pages/`）

各ファイルの実装時：
- `docs/development-guidelines.md` の規約に従う
- 型ヒントを必ず付与する
- docstring を Google スタイルで記述する
- `glossary.md` の用語で命名する

## 6. テストの作成と実行

1. 新機能に対するユニットテストを `tests/unit/` に作成
2. 必要に応じて統合テストを `tests/integration/` に作成
3. テスト命名は `test_[対象]_[条件/期待結果]` パターンに従う
4. **サブエージェント `test-runner` を起動** してテストを実行
5. **サブエージェント `test-analyzer` を起動** して結果を分析

## 7. レビューと検証

1. **サブエージェント `code-reviewer` を起動** してコードレビューを実施
2. **サブエージェント `security-checker` を起動** してセキュリティチェックを実施
3. レビュー指摘事項を修正

## 8. ドキュメント更新

1. `docs/functional-design.md` — 機能一覧に新機能を追加
2. `docs/architecture.md` — アーキテクチャに変更がある場合は更新
3. `docs/repository-structure.md` — 新規ファイルがある場合は更新
4. `.steering/[今回]/tasklist.md` — すべてのタスクを完了に更新

## 9. コミット

Conventional Commits に従いコミットする：

```bash
git add .
git commit -m "feat(<scope>): <変更内容の要約>"
```
