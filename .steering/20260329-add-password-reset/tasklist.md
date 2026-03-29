# タスクリスト: パスワードリセット機能

- 日付: 2026-03-29
- ステータス: 進行中

## タスク

- [x] config.py にリセットトークン定数を追加
- [x] models.py に PasswordResetTokenRecord を追加
- [x] 007_add_password_reset_tokens.sql マイグレーション作成
- [x] password_reset_repo.py リポジトリ実装
- [x] auth.py にリセットフォーム表示・処理を追加
- [x] 05_admin.py にリセットリンク発行UIを追加
- [x] app.py に PasswordResetRepository を追加
- [x] user_repo.py の delete でリセットトークンも削除
- [x] ユニットテスト作成・実行（17テスト全通過、全386テスト通過）
- [x] コードレビュー・セキュリティチェック
- [x] ドキュメント更新（functional-design.md, repository-structure.md, architecture.md）

## 完了条件

- [x] テスト通過（386件全通過）
- [x] レビュー済み
