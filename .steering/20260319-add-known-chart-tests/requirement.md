# 要件定義: 既知命式データとの照合テスト追加
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
実際の命式データとの照合テストを追加し、calculator.py の算出結果の正確性を検証する。

## 受け入れ条件
- [x] 3つの生年月日の算出結果を確認・記録
- [x] tests/fixtures/expected_natal_charts.json に期待値を保存
- [x] TestKnownNatalCharts クラスに照合テスト3件を追加
- [x] ruff check / ruff format / mypy エラーなし
- [x] 全16テスト通過

## 対象スコープ
- tests/fixtures/expected_natal_charts.json（新規作成）
- tests/unit/test_calculator.py（照合テスト追加）

## スコープ外
- 他モジュールのテスト
