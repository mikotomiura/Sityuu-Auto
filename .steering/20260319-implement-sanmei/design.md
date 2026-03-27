# 設計メモ: implement-sanmei
- 日付: 2026-03-19

## 実装アプローチ
docs/fortune-engine-detail.md セクション5.3の擬似コードに完全準拠して実装する。既存の calculator.py のパターン（logging, エラーハンドリング, docstring スタイル）に合わせる。

## 変更内容
- src/fortune_engine/sanmei.py を新規作成
  - calculate_sanmei_data(): 公開関数。NatalChart → SanmeiData
  - _lookup_judai(): JUDAI_TABLE による十大主星引き当て
  - _lookup_junidai(): TWELVE_PHASES_TABLE → JUNIUNSEI_TO_JUNIDAI の2段階ルックアップ

## 代替案
- lunar_python の十二長生表 API を使う案 → 独自テーブル（TWELVE_PHASES_TABLE）で統一性を確保

## 影響範囲
- fortune_engine パッケージ内で完結。他モジュールへの影響なし。
