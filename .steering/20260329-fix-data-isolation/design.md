# 設計メモ: アカウント間データ分離バグ修正
- 日付: 2026-03-29

## 実装アプローチ
- clients, sessions テーブルに user_id TEXT カラムを NULL許容で追加
- 既存データは NULL のまま（管理者がアプリ上で確認して必要なら手動割当）
- リポジトリの全メソッドに user_id パラメータを追加し、WHERE句でフィルタ
- ページ層で get_current_user_id() を取得して全リポジトリ呼び出しに渡す

## 変更内容
1. マイグレーション 009: ALTER TABLE + INDEX 追加
2. models.py: ClientRecord, SessionRecord に user_id フィールド追加
3. client_repo.py: save, find_all, find_by_id, count, search_by_name, count_sessions_by_client, update に user_id フィルタ追加
4. session_repo.py: save, find_all, find_by_id, find_by_client_id, count, find_all_with_client_name, search_by_client_name に user_id フィルタ追加
5. ページ層 (00, 01, 02, 03): user_id を渡す
6. テスト更新

## 既存データの扱い
- user_id = NULL の既存レコードは、user_id フィルタ付きクエリでは返されない
- 管理者が管理画面から既存データの所有者を割り当てる運用を想定
- 将来的に管理者が全データ閲覧できる機能を別途追加可能

## 影響範囲
- src/db_service/ (models, repositories)
- src/pages/ (00, 01, 02, 03)
- tests/integration/, tests/unit/
