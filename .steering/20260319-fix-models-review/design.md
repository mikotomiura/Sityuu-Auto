# 設計メモ: models.py コードレビュー指摘修正
- 日付: 2026-03-19

## 実装アプローチ

### TENKO / TENKO2 の改名方針
- `TENKO = "天胡星"` → `TENKOSEI = "天胡星"`（胡→ko、星→sei で明確化）
- `TENKO2 = "天庫星"` → `TENKUSEI = "天庫星"`（庫→ku、星→sei で明確化）
- 理由: 漢字の音読みを使い、サフィックス `-SEI`（星）で統一感を出す。
  他のメンバー（TENPOU, TENIN等）との命名パターンとの一貫性も考慮し、
  短縮形 `TENKOSEI` / `TENKUSEI` を採用。

### その他の修正
- モジュール docstring: セクション番号 → 見出しテキスト参照に変更
- 設計書: StrEnum化、INOSHISHI化、TENKO改名を反映

## 変更内容
1. src/fortune_engine/models.py — TENKO→TENKOSEI, TENKO2→TENKUSEI, docstring修正
2. docs/fortune-engine-detail.md — セクション3のEnum定義を最新コードに同期

## 影響範囲
- 現時点で models.py を参照する実装コードは存在しない（constants.py 等は未実装）
- 設計書を同時更新することで、将来の実装者が正しい名前を使用できる
