# 要件定義: アカウント間データ分離バグ修正
- 日付: 2026-03-29
- 関連Issue/PR: なし（ユーザー報告）

## 目的
あるアカウントで作成した鑑定結果・相談者データが他のアカウントからも閲覧できてしまう重大なセキュリティバグを修正する。

## 症状
- ユーザーAが鑑定を実行すると、ユーザーBのダッシュボード・履歴・相談者一覧にもデータが表示される
- 全ユーザーが全データにアクセス可能な状態

## 根本原因
- `clients` テーブルと `sessions` テーブルに `user_id` カラムが存在しない
- リポジトリの全クエリにユーザーフィルタがない
- ページ層がデータ保存時に `user_id` を渡していない

## 受け入れ条件
- [ ] clients, sessions テーブルに user_id カラムが追加されている
- [ ] 全クエリが user_id でフィルタされている
- [ ] データ保存時に current_user_id が記録される
- [ ] 既存データに対するマイグレーションが安全に行われる
- [ ] 全テストがパスする

## 対象スコープ
- src/db_service/migrations/ (新規マイグレーション)
- src/db_service/models.py
- src/db_service/repositories/client_repo.py
- src/db_service/repositories/session_repo.py
- src/pages/00_dashboard.py, 01_reading.py, 02_history.py, 03_clients.py
- tests/

## スコープ外
- 管理者による全データ閲覧機能（将来対応）
