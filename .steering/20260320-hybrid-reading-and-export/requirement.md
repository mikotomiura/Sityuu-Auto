# 要件定義: ハイブリッド鑑定 & エクスポート改善
- 日付: 2026-03-20
- 関連: advice.md

## 目的
1. 名前（漢字の意味・音韻）と四柱推命を掛け合わせた独自のハイブリッド鑑定を実現
2. エクスポート（MD/PDF）時にメンター向けコンテンツを分離し、相談者向けレポートを生成可能にする

## 受け入れ条件
- [ ] フリガナ入力欄が追加されている
- [ ] AIプロンプトに名前・フリガナが渡され、名前の意味・音韻を考慮した鑑定が生成される
- [ ] 画数占いは行わない旨がプロンプトに明記されている
- [ ] エクスポート時に「相談者向け」（メンター情報除外）と「メンター用」（全情報）を選択できる
- [ ] 既存テストが通る

## 対象スコープ
- src/components/input_form.py
- src/ai_service/prompt_builder.py
- src/ai_service/templates/reading_base.md
- src/pages/01_reading.py
- src/components/reading_result.py
- src/components/pdf_export.py
- src/config.py
- src/db_service/ (clients テーブルに name_kana カラム追加)

## スコープ外
- listening_hint.md テンプレートの変更（既に独立しておりそのまま）
- DBマイグレーションスクリプトの新規作成（ALTER TABLEで対応）
