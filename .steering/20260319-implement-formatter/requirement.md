# 要件定義: formatter.py 実装

- 日付: 2026-03-19
- 関連Issue/PR:

## 目的

命式計算エンジンの出力フォーマッタ（formatter.py）を実装する。
AIプロンプト用テキスト整形・UI表示用辞書変換・人体星図グリッド表示の3関数を提供する。

## 受け入れ条件

- [ ] format_for_ai_prompt が設計書7.1のフォーマットに準拠
- [ ] format_for_display がStreamlit表示用の辞書を返す
- [ ] format_human_star_chart_grid が人体星図をテキストグリッドで表現
- [ ] ruff check エラーなし
- [ ] mypy エラーなし

## 対象スコープ

- src/fortune_engine/formatter.py（新規作成）

## スコープ外

- テストファイルの作成（別タスク）
- __init__.py の更新（別タスク）
