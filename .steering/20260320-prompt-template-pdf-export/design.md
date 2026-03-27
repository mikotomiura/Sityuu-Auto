# 設計メモ: プロンプトテンプレート管理 + PDFエクスポート
- 日付: 2026-03-20

## 実装アプローチ

### F-012: プロンプトテンプレート管理
- DBの `prompt_templates` テーブル（既にスキーマ定義済み）を活用
- `PromptTemplateRepository` で CRUD 操作を提供
- `prompt_builder.py` に `build_reading_prompt_from_template()` を追加し、DB保存テンプレートからプロンプト構築
- 設定ページに「プロンプトテンプレート」タブを追加
- 鑑定ページにテンプレート選択セレクトボックスを追加
- 初回起動時に既存の `reading_base.md` / `listening_hint.md` をデフォルトテンプレートとしてDBに登録

### F-013: PDFエクスポート
- `reportlab` を採用（Pure Python、軽量、CJKフォント内蔵）
- `reportlab.lib.pagesizes` で A4 サイズ
- `reportlab.platypus` の `SimpleDocTemplate` + `Paragraph` で構造化
- CID フォント（HeiseiMin-W3 / HeiseiKakuGo-W5）で日本語対応
- 既存の `build_reading_report_markdown()` と同じ構造でPDF生成

## 変更内容
1. `db_service/models.py` — PromptTemplateRecord 追加
2. `db_service/repositories/prompt_template_repo.py` — 新規作成
3. `ai_service/prompt_builder.py` — DB テンプレート対応の関数追加
4. `config.py` — セッションキー追加
5. `pages/04_settings.py` — テンプレート管理タブ追加
6. `pages/01_reading.py` — テンプレート選択UI追加
7. `components/pdf_export.py` — 新規作成（PDF生成ロジック）
8. `components/reading_result.py` — PDFボタン追加
9. `pages/02_history.py` — PDFボタン追加
10. `pyproject.toml` — reportlab 追加

## 代替案
- PDF: weasyprint（HTML→PDF）は依存が重く、OS依存のライブラリが必要
- PDF: fpdf2 は軽量だがCJK対応がやや弱い
- → reportlab を採用（CJKフォント内蔵、安定性高い）

## 影響範囲
- AI連携層: prompt_builder のインターフェース拡張（後方互換性維持）
- UI層: settings, reading, history ページに変更
- DB層: 新リポジトリ追加（既存テーブル利用）
