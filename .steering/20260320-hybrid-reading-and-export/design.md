# 設計メモ: ハイブリッド鑑定 & エクスポート改善
- 日付: 2026-03-20

## 実装アプローチ

### A. ハイブリッド鑑定
- input_form.py に `name_kana` フィールド追加
- prompt_builder.py の `build_reading_prompt` に `name`, `name_kana` 引数追加
- reading_base.md に名前×命式の掛け合わせ鑑定ルールを追加
  - 画数占い禁止を明記
  - 漢字の語義・音韻と五行の関連を解釈する指示
- Template 変数: `${name}`, `${name_kana}` を追加

### B. エクスポート改善
- reading_base.md の「5. メンター向け傾聴ガイド」を維持（画面表示では有用）
- エクスポート時に `include_mentor_content` フラグで制御
  - False: セクション5 + 傾聴ヒントを除外
  - True: 全内容を含む（現行動作）
- MD/PDF 両方のエクスポート関数に同フラグを追加

## 変更内容
1. ClientInputData に name_kana: str | None 追加
2. config.py に SESSION_KEY_CLIENT_NAME_KANA 追加
3. reading_base.md にハイブリッド鑑定セクション追加
4. prompt_builder.build_reading_prompt に name, name_kana 引数追加
5. 01_reading.py でフリガナをsession_stateに保持しプロンプトに渡す
6. reading_result.py でエクスポートモード選択UIを追加
7. pdf_export.py に include_mentor_content パラメータ追加
8. DB clients テーブルに name_kana カラム追加

## 影響範囲
- 鑑定ページ全体のフロー
- エクスポート機能
- DB保存処理
