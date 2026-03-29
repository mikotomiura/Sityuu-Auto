# 設計メモ: SQLiteトランザクション蓄積問題の根本修正
- 日付: 2026-03-30

## 実装アプローチ
`isolation_level=None` (autocommit) へ移行し、トランザクション蓄積を構造的に不可能にする。

### 変更の要点
1. `create_connection()` で `isolation_level=None` を指定
2. 単一DMLのリポジトリメソッドから `self._conn.commit()` を削除（autocommitで不要）
3. 複数DMLが必要な操作には `begin_transaction()` コンテキストマネージャーを使用
4. `contextlib.suppress(DatabaseError)` を明示的 try/except に置換

### autocommit モードの動作
- 単一DML: `execute("INSERT ...")` → 即座にコミット。`commit()` は no-op
- 明示的トランザクション: `BEGIN IMMEDIATE` → 複数DML → `COMMIT` / `ROLLBACK`
- `BEGIN IMMEDIATE` は書き込みロックを即座に取得し、競合を早期検知

### 影響を受けるメソッド（明示的トランザクションが必要）
| リポジトリ | メソッド | 理由 |
|---|---|---|
| `AuthSessionRepository` | `create()` | DELETE + INSERT |
| `PasswordResetRepository` | `create()` | DELETE + INSERT |
| `UserRepository` | `delete()` | 複数テーブルの DELETE |
| `PromptTemplateRepository` | `save()` | `_clear_default()` + INSERT |
| `PromptTemplateRepository` | `set_default()` | `_clear_default()` + UPDATE |

## 代替案
- **案B: 全エラーハンドラにrollback追加**: 侵襲度は低いが、将来の新コード追加時にrollback忘れが再発するリスク
- **案C: commit()をtry/finallyでラップ**: 部分的な対策であり根本解決にならない

## 影響範囲
- DB層全体（全リポジトリ）
- 認証フロー（auth.py）
- 管理者ページ（05_admin.py）
- DB初期化（db_init.py）
