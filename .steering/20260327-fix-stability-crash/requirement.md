# 要件定義: アプリ安定性・クラッシュ修正
- 日付: 2026-03-27

## 症状
- 処理が途中で止まる、画面がクラッシュする
- 複数アクセスにシステムが耐えられない
- PM2が3日間で31回リスタート

## 根本原因
1. SQLiteに `busy_timeout` が未設定 → 複数スレッドが同時に書き込むと即座に "database is locked" で失敗
2. `@st.cache_resource` で単一のDB接続を全ユーザーセッション間で共有 → スレッド間でのSQLite接続競合

## 期待される修正後の動作
- 複数ユーザーが同時にアクセスしてもクラッシュしない
- DB書き込みの競合時は待機して再試行する
- 各ユーザーセッションが独立したDB接続を使用する

## 対象スコープ
- src/db_service/database.py（busy_timeout追加）
- src/db_init.py（スレッドローカル接続管理に変更）
- src/ai_service/client.py（Geminiフォールバックのsleep削除）
