# 設計メモ: advice.md 改善案の実装
- 日付: 2026-03-21

## 実装アプローチ

### 修正1: autocomplete 無効化
- `st.markdown()` で JavaScript を注入し、フォーム内の input/textarea 要素に `autocomplete="off"` を設定
- Streamlit の `st.text_input` は直接 autocomplete 属性を制御できないため、DOM操作で対応

### 修正2: 新規鑑定ボタン
- 鑑定結果表示後（保存ボタンの近くまたはページ上部）に「新規鑑定を開始」ボタンを配置
- クリック時に全読み取りセッションキーを None にリセットし `st.rerun()` で画面更新
- `_clear_reading_state()` ヘルパー関数を追加

### 修正3: タブ遷移時の不整合解消
- 前回の鑑定結果がある場合、フォーム上部に「前回の鑑定: ○○さん」と表示
- 「新規鑑定を開始」ボタンを併設し、ワンクリックでリセット可能に
- 修正2のリセット機能と共通化

## 変更内容
- `src/components/input_form.py`: autocomplete 無効化 JS 注入
- `src/pages/01_reading.py`: リセット機能、前回結果の明示表示

## 影響範囲
- 鑑定ページのみ。他ページへの影響なし。
