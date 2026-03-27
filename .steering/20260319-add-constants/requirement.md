# 要件定義: constants.py の実装
- 日付: 2026-03-19
- 関連Issue/PR: なし

## 目的
docs/fortune-engine-detail.md セクション4・6に定義された全定数テーブルを実装する。

## 受け入れ条件
- [ ] 11個の定数テーブルがすべて定義されている
- [ ] 設計書の値を正確に転記している
- [ ] 型は models.py の Enum を使用している
- [ ] ruff check / mypy がエラーなし

## 対象スコープ
- src/fortune_engine/constants.py（新規作成）

## スコープ外
- calculator.py / sanmei.py（次タスク）
- テスト（別タスクで作成）
