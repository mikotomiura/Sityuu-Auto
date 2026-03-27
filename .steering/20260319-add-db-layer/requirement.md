# 要件定義: DB層の基盤実装
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
DB層（db_service）の基盤を実装し、SQLiteによるデータ永続化の土台を構築する。

## 受け入れ条件
- [ ] `src/db_service/database.py` — DB接続・初期化関数が動作する
- [ ] `src/db_service/migrations/001_initial.sql` — architecture.md 準拠のテーブルが作成される
- [ ] `src/db_service/models.py` — ClientRecord, SessionRecord データクラスが定義されている
- [ ] `scripts/init_db.py` — コマンドラインから実行してDBが正しく作成される
- [ ] SQLインジェクション対策（パラメータバインディング）が適用されている
- [ ] 型ヒント・docstring が規約に準拠している

## 対象スコープ
- `src/db_service/database.py`
- `src/db_service/models.py`
- `src/db_service/migrations/001_initial.sql`
- `scripts/init_db.py`

## スコープ外
- リポジトリ層（client_repo.py, session_repo.py）の実装
- UI層との統合
- テストコードの作成（別タスク）
