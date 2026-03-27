# 設計メモ: client_repo.update に name_kana を追加
- 日付: 2026-03-21

## 実装アプローチ
既存の動的 SQL パターン（updates リスト + params バインディング）に
name_kana を追加する。後方互換性を保つためデフォルト引数 None とする。

## 変更内容
1. client_repo.py: update() に name_kana: str | None = None を追加
2. 03_clients.py: 詳細画面にフリガナ編集フィールドを追加
3. test_db_operations.py: name_kana 更新テストを追加

## 影響範囲
- update() の既存呼び出し元（03_clients.py のメモ保存）は影響なし（デフォルト引数）
