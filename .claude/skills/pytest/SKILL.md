---
name: test-standards
description: pytest を使用したテスト戦略と品質基準。テストの種類、命名規則、フィクスチャ設計、モック戦略、カバレッジ目標を定義する。テストコードの新規作成・修正時に参照すべき。
allowed-tools: Read, Write, Bash, Grep, Glob
---

# テスト開発規約

## テストの種類と配置

### ユニットテスト（tests/unit/）

- 個々の関数・クラスを独立してテストする
- 外部依存（DB、API）はすべてモックする
- 実行速度が速いこと（1テスト1秒以内）

### 統合テスト（tests/integration/）

- モジュール間の連携をテストする
- DB はテスト用 SQLite（インメモリ or テンポラリファイル）を使用
- API はモックサーバーを使用

## テスト命名規則

```
test_[テスト対象]_[条件や期待結果]
```

- テスト対象: 関数名やクラス名
- 条件: `with_valid_date`, `when_api_key_missing`
- 期待結果: `returns_natal_chart`, `raises_error`

## フィクスチャ設計

### conftest.py の階層

- `tests/conftest.py`: 全テスト共通のフィクスチャ
- `tests/unit/conftest.py`: ユニットテスト固有のフィクスチャ
- `tests/integration/conftest.py`: 統合テスト固有のフィクスチャ

### フィクスチャ命名

- `sample_[オブジェクト名]`: テストデータ（例: `sample_client_input`）
- `mock_[対象名]`: モックオブジェクト（例: `mock_llm_client`）
- `db_[説明]`: DB関連フィクスチャ（例: `db_session`）

## モック戦略

### AI連携層のモック

- LLM API は常にモックする（テストでAPIを呼ばない）
- レスポンスフィクスチャを `tests/fixtures/` に JSON で定義

### DB層のモック

- ユニットテスト: リポジトリをモック
- 統合テスト: インメモリ SQLite を使用

## カバレッジ目標

| モジュール | 目標 |
|-----------|------|
| `fortune_engine/` | 90% 以上 |
| `db_service/` | 80% 以上 |
| `ai_service/` | 70% 以上 |
| `utils/` | 80% 以上 |

## テストで確認すべきケース

### 正常系

- 有効な入力に対して正しい結果が返ること
- 境界値（最小値・最大値）で正常に動作すること

### 異常系

- 無効な入力に対して適切な例外が発生すること
- None / 空文字 / 空リストでクラッシュしないこと
- API接続エラー時にリトライ・フォールバックが動作すること

## 詳細情報

- 実装例は `examples.md` を参照
