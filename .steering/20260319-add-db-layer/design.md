# 設計メモ: DB層の基盤実装
- 日付: 2026-03-19

## 実装アプローチ
- SQLite skills (`examples.md`) のDB接続パターンを踏襲
- `config.py` の `DB_PATH` を参照してDB配置先を統一
- マイグレーションは `MIGRATIONS_DIR` のSQLファイルをソート順に実行
- データクラスは `dataclass` で定義（DB層のレコード表現、Pydantic は fortune_engine 側）

## 変更内容
1. `src/db_service/migrations/001_initial.sql` — clients, sessions, prompt_templates テーブル + インデックス
2. `src/db_service/models.py` — ClientRecord, SessionRecord データクラス
3. `src/db_service/database.py` — create_connection(), initialize_database()
4. `scripts/init_db.py` — DB初期化エントリーポイント

## 代替案
- Pydantic BaseModel でDB層モデルも定義 → 過剰。DB層は dataclass で軽量に保つ
- alembic によるマイグレーション管理 → ローカルファーストの小規模アプリには過剰

## 影響範囲
- `src/db_service/__init__.py` の公開APIに追加
- `data/` ディレクトリにDBファイルが生成される
