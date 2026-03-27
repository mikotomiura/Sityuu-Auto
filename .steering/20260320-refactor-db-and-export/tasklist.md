# タスクリスト: DB拡張子統一・AI鑑定レポートMDエクスポート
- 日付: 2026-03-20
- ステータス: 完了

## タスク
- [x] 影響範囲分析（impact-analyzer）
- [x] 既存テスト実行（test-runner）ベースライン確認 — 95/95 pass
- [x] config.py: DB_PATH を Path 型 + `.sqlite3` に変更
- [x] database.py: DB_PATH 削除、config からインポート、旧DB自動移行
- [x] db_init.py: import 整理
- [x] scripts/init_db.py: デフォルトパスを config.DB_PATH から取得
- [x] components/reading_result.py: MDエクスポート機能追加 + 型修正
- [x] pages/01_reading.py: エクスポート用の相談者名渡し + エラーメッセージ改善
- [x] ドキュメント更新（architecture.md, repository-structure.md, .gitignore）
- [x] テスト実行（test-runner）全テスト通過確認 — 95/95 pass
- [x] コードレビュー（code-reviewer）— 重大指摘2件を修正済み
- [x] ruff format / ruff check — 変更ファイルはクリーン

## 完了条件
- [x] テスト通過（95/95 ベースライン維持）
- [x] ruff check 通過（変更ファイル）
- [x] レビュー済み（重大指摘修正済み）
