# 設計メモ: AI鑑定レポート生成ボタンが動作しないバグの修正
- 日付: 2026-03-19

## 実装アプローチ
session_stateに`concern`（悩みテキスト）を保存し、ページ再実行時にもAI生成ボタンのコードパスに到達できるようフローを修正する。

### 具体的な変更
1. `config.py` に `SESSION_KEY_CONCERN` を追加
2. `01_reading.py` のフロー修正:
   - フォーム送信時に `concern` を session_state に保存
   - `client_data is None` の場合でも fortune_result があれば早期リターンせず、AI生成ボタンを表示
   - AI生成時に session_state から concern を取得

## 代替案
- `st.form` の外にAI生成ボタンを置き、callbackで制御する → 不要な複雑性
- `client_data` 全体を session_state に保存する → 過剰（concern だけで十分）

## 影響範囲
- `src/pages/01_reading.py` — メインフロー修正
- `src/config.py` — キー追加のみ
