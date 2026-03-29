# 要件定義: SQLiteトランザクション蓄積問題の根本修正
- 日付: 2026-03-30
- 関連Issue/PR: advice.md (バグ報告 #1-#4)

## 目的
advice.mdに記載された4つのバグの根本原因であるSQLiteトランザクション蓄積問題を解決する。

## バグ報告
1. リロードでログイン画面に遷移する
2. アカウント設定のメールアドレス保存が失敗する
3. 鑑定結果の保存が失敗する（「保存に失敗しました」+「再保存を実行しろ」）
4. 招待リンク・パスワードリセットリンクの削除が失敗する

## 根本原因
Python sqlite3 の `isolation_level=""` (デフォルト) による暗黙トランザクション管理が原因。

1. `commit()` 失敗時にトランザクションが開いたまま残る（WALライターロックも保持）
2. `contextlib.suppress(DatabaseError)` がエラーをロールバックせずに飲み込む
3. 同一リクエスト内の後続DB操作が全てカスケード失敗する

具体的なフロー:
- `refresh_expiry()` の commit 失敗 → suppress で握り潰し → トランザクション開放されず
- 後続の `client_repo.save()`, `session_repo.save()` が同じ汚染接続で失敗

## 受け入れ条件
- [ ] `isolation_level=None` (autocommit) への移行
- [ ] 複数DML操作を持つメソッドの明示的トランザクション化
- [ ] `contextlib.suppress(DatabaseError)` の除去
- [ ] 既存テストの通過
- [ ] DB整合性の維持

## 対象スコープ
- `src/db_service/database.py`
- `src/db_service/repositories/*.py` (全リポジトリ)
- `src/db_init.py`
- `src/utils/auth.py`
- `src/pages/05_admin.py`

## スコープ外
- UI層のロジック変更
- 新規テストの追加（回帰テストのみ）
