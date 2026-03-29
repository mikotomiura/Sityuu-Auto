# 設計メモ: SQLite "database is locked" 根本解決
- 日付: 2026-03-30

## 根本原因の詳細分析

Streamlitはマルチスレッドで動作し、各ユーザーセッションが独立スレッドで処理される。
各スレッドはthread-localなDB接続を持つが、以下の問題がある:

1. **busy_timeout不足**: デフォルト5秒のタイムアウトでは、同時書き込み時にロック待ちが間に合わない
2. **未コミットトランザクション残留**: ページ処理中にStreamlitが例外を投げた場合、
   `execute()` 後の `commit()` に到達しない。スレッドが再利用されると、
   前のリクエストの未コミットトランザクションがロックを保持し続ける

## 修正アプローチ

### 1. 接続タイムアウト増加（database.py）
- `sqlite3.connect(timeout=30)` で30秒のロック待ちを設定
- `PRAGMA busy_timeout=30000` も同値に設定

### 2. 未コミットトランザクションの検出・ロールバック（db_init.py）
- `get_db_connection()` でコネクション再利用時に `conn.in_transaction` をチェック
- 未コミットトランザクションが検出された場合は `rollback()` してロックを解放

### 3. WALモード検証ログ（database.py）
- `PRAGMA journal_mode=WAL` の戻り値をチェックし、WAL以外の場合は警告ログ

## 変更対象ファイル
- `src/db_service/database.py` — 接続タイムアウト・WAL検証
- `src/db_init.py` — 未コミットトランザクション検出
