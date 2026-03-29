# タスクリスト: アカウント間データ分離バグ修正
- 日付: 2026-03-29
- ステータス: 完了

## タスク
- [x] DBマイグレーション作成（clients, sessions に user_id 追加）
- [x] models.py に user_id フィールド追加
- [x] client_repo.py の全メソッドに user_id フィルタ追加
- [x] session_repo.py の全メソッドに user_id フィルタ追加
- [x] 01_reading.py: 保存時に user_id を渡す
- [x] 00_dashboard.py: クエリに user_id を渡す
- [x] 02_history.py: クエリに user_id を渡す
- [x] 03_clients.py: クエリに user_id を渡す
- [x] 既存テストの更新 + データ分離テスト追加
- [x] 回帰テスト実行（404件全パス）
- [x] コードレビュー + 指摘事項修正

## 完了条件
- [x] テスト通過
- [x] レビュー済み
