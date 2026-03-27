# 要件定義: リポジトリ層の実装
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
DB層のリポジトリパターンを実装し、相談者・セッションのCRUD操作を提供する。

## 受け入れ条件
- [ ] `src/db_service/repositories/client_repo.py` — ClientRepository の CRUD が動作する
- [ ] `src/db_service/repositories/session_repo.py` — SessionRepository の CRUD が動作する
- [ ] すべての SQL でパラメータバインディングを使用している
- [ ] `tests/integration/test_db_operations.py` — 正常系・異常系テストが全パスする
- [ ] 型ヒント・docstring が規約に準拠している

## 対象スコープ
- `src/db_service/repositories/client_repo.py`
- `src/db_service/repositories/session_repo.py`
- `src/db_service/repositories/__init__.py`
- `tests/integration/test_db_operations.py`

## スコープ外
- UI層との統合
- プロンプトテンプレートのリポジトリ
