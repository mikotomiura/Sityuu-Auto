---
name: sqlite-standards
description: SQLite データベース設計と操作の規約。テーブル設計、リポジトリパターン、マイグレーション、セキュリティ（SQLインジェクション対策）、バックアップ方針を定義する。DB層（db_service/）のコードを新規作成・修正する際に参照すべき。
allowed-tools: Read, Write, Bash, Grep, Glob
---

# SQLite 開発規約

## テーブル設計のルール

### 命名規則

- テーブル名: `snake_case`（複数形）— `clients`, `sessions`
- カラム名: `snake_case` — `birth_date`, `created_at`
- 外部キー: `[参照テーブル単数形]_id` — `client_id`

### 必須カラム

すべてのテーブルに以下のカラムを含める：

- `id TEXT PRIMARY KEY` — UUID を使用
- `created_at TEXT NOT NULL` — ISO 8601 形式
- `updated_at TEXT NOT NULL` — ISO 8601 形式

### データ型

SQLite はデータ型が柔軟だが、以下の型を統一して使用する：

| 用途 | SQLite 型 | Python 型 | 備考 |
|------|----------|----------|------|
| ID | TEXT | str | UUID 文字列 |
| 文字列 | TEXT | str | |
| 日付 | TEXT | str | ISO 8601 形式（YYYY-MM-DD） |
| 日時 | TEXT | str | ISO 8601 形式（YYYY-MM-DDTHH:MM:SS） |
| 時刻 | TEXT | str | HH:MM 形式 |
| 数値 | INTEGER | int | |
| 真偽値 | INTEGER | int | 0 = False, 1 = True |
| JSON | TEXT | str | JSON 文字列として格納 |

## リポジトリパターン

### リポジトリの責務

- DB操作を抽象化し、ロジック層に対してドメインオブジェクトで入出力する
- SQL文はリポジトリ内部に閉じ込める
- 1テーブル = 1リポジトリを基本とする

### メソッド命名

- `save(...)` — 新規作成（INSERT）
- `update(...)` — 更新（UPDATE）
- `find_by_id(id)` — ID で1件取得
- `find_all(...)` — 条件付き全件取得
- `delete(id)` — 削除（DELETE）
- `search(...)` — 検索

## SQLインジェクション対策

### 必須ルール: パラメータバインディング

すべてのSQL実行でパラメータバインディング（`?` プレースホルダ）を使用すること。

```python
# Good
cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))

# Bad（SQLインジェクションの脆弱性）
cursor.execute(f"SELECT * FROM clients WHERE id = '{client_id}'")
```

## マイグレーション

### マイグレーションファイル

- `src/db_service/migrations/` に連番で配置
- ファイル名: `[番号]_[説明].sql` — `001_initial.sql`
- 各ファイルは冪等であること（`IF NOT EXISTS` を使用）

### マイグレーション実行

- アプリ起動時に自動実行
- 適用済みマイグレーションを管理テーブルで追跡

## バックアップ

- SQLite ファイル（`data/fortune.db`）のコピーで対応
- 将来的に日次自動バックアップを実装

## 詳細情報

- 実装例は `examples.md` を参照
