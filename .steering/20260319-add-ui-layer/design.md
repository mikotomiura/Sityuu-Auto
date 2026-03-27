# 設計メモ: UI層の実装
- 日付: 2026-03-19

## 実装アプローチ
- Streamlit マルチページ構成を採用（`src/app.py` + `src/pages/`）
- コンポーネントは `src/components/` に `render_*` 関数として切り出し
- 状態管理は `st.session_state` + `config.py` の定数キー
- 既存の `fortune_engine` / `ai_service` / `db_service` をそのまま利用

## 変更内容
1. `src/app.py` — `st.set_page_config` + サイドバーナビゲーション
2. `src/components/input_form.py` — `render_client_input_form()` → `ClientInputData | None`
3. `src/components/natal_chart_display.py` — `render_natal_chart(chart)` → None
4. `src/components/reading_result.py` — `render_reading_result(result, ai_text)` → None
5. `src/pages/01_reading.py` — 入力→命式算出→AI鑑定→結果表示→保存フロー

## 影響範囲
- `src/config.py` — セッションキー追加（FORTUNE_RESULT用）
- 既存のロジック層・AI層・DB層は変更なし
