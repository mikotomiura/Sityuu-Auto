# 要件定義: ユーザー削除失敗の修正
- 日付: 2026-03-27

## 症状
管理者ページのユーザー管理でユーザーを削除しようとすると失敗する。

## 根本原因
`PRAGMA foreign_keys=ON` が有効な状態で、以下のテーブルが users.id を外部キーで参照している:
- `invitation_tokens.created_by` → users(id)
- `invitation_tokens.used_by` → users(id)
- `auth_sessions.user_id` → users(id)

ユーザーに関連する招待リンクやセッションが存在すると、外部キー制約違反 (sqlite3.IntegrityError) が発生する。

## 期待される修正後の動作
- ユーザー削除時に、関連する auth_sessions と invitation_tokens のレコードを先に削除（またはNULL化）する
- 削除が正常に完了し、管理者に成功メッセージが表示される

## 対象スコープ
- src/db_service/repositories/user_repo.py（delete メソッドの修正）
