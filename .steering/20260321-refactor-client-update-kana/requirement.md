# 要件定義: client_repo.update に name_kana を追加
- 日付: 2026-03-21
- 関連Issue/PR: advice.md の改善提案

## 目的
client_repo.py の update メソッドに name_kana パラメータを追加し、
相談者管理ページ（03_clients.py）でフリガナの編集を可能にする。

## 受け入れ条件
- [ ] update メソッドで name_kana を更新できる
- [ ] 03_clients.py の詳細画面でフリガナ編集UIが表示される
- [ ] 既存テスト全通過 + 新規テスト追加
- [ ] ruff format / check クリア

## 対象スコープ
- src/db_service/repositories/client_repo.py
- src/pages/03_clients.py
- tests/integration/test_db_operations.py

## スコープ外
- gender, birth_date, birth_time の update 対応（今回は name_kana のみ）
