# タスクリスト: SQLiteトランザクション蓄積問題の根本修正
- 日付: 2026-03-30
- ステータス: 完了

## タスク
- [x] 根本原因の特定
- [x] 構造化ノートの作成
- [x] `database.py`: autocommit移行 + `begin_transaction()` 追加
- [x] `auth_session_repo.py`: 明示的トランザクション対応
- [x] `password_reset_repo.py`: 明示的トランザクション対応
- [x] `user_repo.py`: 明示的トランザクション対応
- [x] `invitation_repo.py`: commit削除
- [x] `client_repo.py`: commit削除
- [x] `session_repo.py`: commit削除
- [x] `prompt_template_repo.py`: 明示的トランザクション対応
- [x] `db_init.py`: autocommit対応
- [x] `auth.py`: suppress(DatabaseError) 除去
- [x] `05_admin.py`: suppress(DatabaseError) 除去
- [x] テスト実行 (404 passed, 0 failed)
- [x] コードレビュー

## 完了条件
- [x] テスト通過
- [x] DB操作のカスケード障害が発生しないことの確認
