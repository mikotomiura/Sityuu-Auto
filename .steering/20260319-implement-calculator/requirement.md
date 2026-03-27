# 要件定義: calculator.py 実装
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
四柱推命の命式算出モジュール（calculator.py）を実装する。
lunar_python を利用して生年月日から四柱（年柱・月柱・日柱・時柱）を算出し、NatalChart オブジェクトとして返す。

## 受け入れ条件
- [x] calculate_natal_chart() が設計書5.2の処理フローに完全準拠
- [x] _build_pillar() が天干・地支からPillarを正しく構築
- [x] _count_five_elements() が天干の五行を正しくカウント
- [x] 出生時間がNoneの場合、hour_pillar が None
- [x] エラー時は FortuneCalculationError を送出
- [x] ruff check / ruff format / mypy エラーなし

## 対象スコープ
- src/fortune_engine/calculator.py（新規作成）
- pyproject.toml（mypy の lunar_python 設定追加）

## スコープ外
- sanmei.py, formatter.py の実装
- テストコードの作成
