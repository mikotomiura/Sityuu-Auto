# 要件定義: __init__.py 公開API + 統合テスト

- 日付: 2026-03-19

## 目的

fortune_engine の公開API（__init__.py）を設計書セクション9に準拠して実装し、
統合テスト（test_fortune_flow.py）でフルフロー検証を行う。

## 受け入れ条件

- [ ] __init__.py が calculate_fortune, format_for_ai_prompt, format_for_display, format_human_star_chart_grid を公開
- [ ] 統合テスト5ケースがすべてパス
- [ ] ruff check / mypy エラーなし

## 対象スコープ

- src/fortune_engine/__init__.py（更新）
- tests/integration/test_fortune_flow.py（新規作成）

## スコープ外

- 個別モジュールの修正
