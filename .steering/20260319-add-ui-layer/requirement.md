# 要件定義: UI層の実装（Streamlitエントリーポイント + 鑑定ページ）
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
Streamlit UI層を構築し、鑑定ページ（入力→命式算出→AI鑑定→結果表示→保存）の一連のフローを動作可能にする。

## 受け入れ条件
- [ ] `streamlit run src/app.py` で起動できる
- [ ] サイドバーにナビゲーションが表示される
- [ ] 鑑定ページで入力フォームが表示される
- [ ] 命式算出が実行され、命式表が表示される
- [ ] AI鑑定テキストの生成と表示ができる（API設定時）
- [ ] 鑑定結果が統合表示される（命式 + 人体星図 + AIテキスト）

## 対象スコープ
- `src/app.py` — エントリーポイント
- `src/components/input_form.py` — 入力フォーム
- `src/components/natal_chart_display.py` — 命式表表示
- `src/components/reading_result.py` — 鑑定結果表示
- `src/pages/01_reading.py` — 鑑定ページ

## スコープ外
- 鑑定履歴ページ（02_history.py）
- 相談者管理ページ（03_clients.py）
- 設定ページ（04_settings.py）
- DB保存の完全な実装（スタブレベルで対応）
