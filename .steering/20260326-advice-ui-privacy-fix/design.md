# 設計メモ: advice.md 改善案の実装
- 日付: 2026-03-26

## 実装アプローチ

### 1. autocomplete 無効化の統一（プライバシー修正）
- 現在の `input_form.py` の `_inject_autocomplete_off()` を共通ユーティリティに移動
- `st.components.v1.html()` を使用（height=0）して確実にJS実行
  - 理由: `st.markdown` の `<script>` タグはStreamlitバージョンにより除去される可能性がある
- 全ページから共通関数を呼び出し

### 2. UIデザイン強化
- theme.py にページヘッダー装飾、セクション区切りCSS追加
- ログインページにロゴエリア、装飾枠線を追加
- 各ページのタイトルにアイコンとサブタイトルを追加
- 空状態メッセージの視覚改善

## 変更内容
1. `src/utils/privacy.py` — 新規: autocomplete無効化の共通ユーティリティ
2. `src/components/theme.py` — 拡張: UI強化CSS追加
3. `src/components/input_form.py` — 修正: 共通ユーティリティに委譲
4. `src/pages/03_clients.py` — 修正: autocomplete無効化追加
5. `src/pages/02_history.py` — 修正: autocomplete無効化追加
6. `src/utils/auth.py` — 修正: autocomplete無効化 + ログインUI強化

## 代替案
- autocomplete="new-password" HTML属性: ブラウザ依存が大きく不採用
- iframe経由でのフォーム表示: Streamlitの状態管理と相性が悪く不採用

## 影響範囲
- 全ページのUIに軽微な変更（視覚的改善のみ）
- フォーム動作に影響なし（autocomplete属性の変更のみ）
