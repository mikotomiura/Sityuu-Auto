# 要件定義: UIデザイン改善 + AI分析結果の充実
- 日付: 2026-03-19

## 目的
1. UI の視認性・分かりやすさを改善（セクション整理、タブ活用、メトリクス表示）
2. AI分析の出力を充実させる（命式の評価コメント、具体的な分析結果、傾聴ヒント）

## 受け入れ条件
- [ ] 鑑定ページが視覚的に整理され、各セクションが明確に分かれている
- [ ] 命式表・人体星図・AI分析がタブで切り替えられる
- [ ] AI鑑定結果に命式の具体的な評価・分析コメントが含まれる
- [ ] 傾聴ヒントが生成・表示される
- [ ] streamlit run src/app.py で正常動作する

## 対象スコープ
- src/app.py — サイドバーの情報充実
- src/components/input_form.py — フォームレイアウト改善
- src/components/natal_chart_display.py — 命式表の見た目改善
- src/components/reading_result.py — タブ構成・AI分析表示の刷新
- src/pages/01_reading.py — フロー改善、傾聴ヒント生成追加
- src/ai_service/templates/reading_base.md — プロンプト改善

## スコープ外
- 新規ページの追加
- DB保存の実装
