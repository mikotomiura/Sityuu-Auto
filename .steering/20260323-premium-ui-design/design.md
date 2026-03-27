# 設計メモ: プレミアムUI/UXデザインの注入
- 日付: 2026-03-23

## 実装アプローチ
`src/components/theme.py` に `inject_custom_theme()` 関数を作成し、`st.markdown(css, unsafe_allow_html=True)` で全ページ共通のカスタムCSSを注入する。`src/app.py` のページ設定直後に呼び出すことで、全ページに一括適用する。

## デザインコンセプト
- **基調色:** ミッドナイトブルー (#0a0e27) ～ 深紫 (#1a1a3e)
- **アクセント:** ゴールド (#d4af37) をプライマリボタン・見出しに、シルバー (#c0c0c0) をセカンダリ要素に
- **テクスチャ:** 微かなグラデーション背景で深みと神秘感を演出
- **コンポーネント:** 角丸 (border-radius: 12px)、カードシャドウ、ホバーアニメーション

## 変更内容
1. `src/components/theme.py` 新規作成 — CSS定義と注入関数
2. `src/app.py` 修正 — `inject_custom_theme()` 呼び出し追加

## 代替案
- Streamlit の `.streamlit/config.toml` でテーマ設定 → カスタマイズ範囲が限定的で却下
- 各ページに個別CSS注入 → 重複・保守性の問題で却下

## 影響範囲
- 全ページのUI表示に影響（配色・フォント・ボタン・フォーム等）
- 既存の `unsafe_allow_html=True` 使用箇所（natal_chart_display.py の五行カラー等）との競合に注意
