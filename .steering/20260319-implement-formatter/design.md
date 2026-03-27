# 設計メモ: formatter.py 実装

- 日付: 2026-03-19

## 実装アプローチ

設計書 docs/fortune-engine-detail.md セクション7.1 のコードをベースに、
format_for_display と format_human_star_chart_grid を追加実装する。

## 変更内容

### format_for_ai_prompt(result: FortuneResult) -> str
- 設計書7.1のコードに完全準拠

### format_for_display(result: FortuneResult) -> dict[str, Any]
- 四柱推命命式、算命学データをStreamlit表示用辞書に変換
- キー: pillars（四柱テーブル）, human_star_chart, tenchusatsu, total_energy, five_elements_balance

### format_human_star_chart_grid(chart: HumanStarChart) -> str
- ユーザー指定のグリッドレイアウトに従う

## 影響範囲

- fortune_engine モジュール内で完結（他モジュールへの影響なし）
