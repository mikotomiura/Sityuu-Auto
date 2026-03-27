# 設計メモ: test_calculator.py 実装
- 日付: 2026-03-19

## 実装アプローチ
.claude/skills/test-standards/examples.md の命式算出テスト例に準拠し、
テストクラスを正常系・境界値・異常系の3つに分離。

## テスト構成
- TestCalculateNatalChartNormal: 正常系9件
- TestCalculateNatalChartBoundary: 境界値2件
- TestCalculateNatalChartError: 異常系1件

## 変更内容
- tests/unit/test_calculator.py 新規作成（12テスト）

## 影響範囲
- なし（テストコードのみの追加）
