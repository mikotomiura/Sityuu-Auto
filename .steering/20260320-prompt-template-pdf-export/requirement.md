# 要件定義: プロンプトテンプレート管理 + PDFエクスポート
- 日付: 2026-03-20
- 関連Issue/PR: Phase 3 (advice.md)

## 目的
運用の幅を広げる2機能を実装する：
1. F-012: プロンプトテンプレート管理 — 相談内容に応じたプロンプト切替
2. F-013: PDFエクスポート — 鑑定レポートのPDF出力

## 受け入れ条件
### F-012
- [ ] 設定ページにテンプレート管理タブが表示される
- [ ] テンプレートの新規作成・編集・削除ができる
- [ ] デフォルトテンプレートを設定できる
- [ ] 鑑定ページでテンプレートを選択して鑑定できる
- [ ] 初回起動時に既存ファイルテンプレートがDBに初期登録される

### F-013
- [ ] 鑑定結果ページでPDFダウンロードボタンが表示される
- [ ] 鑑定履歴詳細ページでもPDFダウンロードできる
- [ ] 日本語フォントが正しくレンダリングされる

## 対象スコープ
- src/db_service/models.py
- src/db_service/repositories/prompt_template_repo.py (新規)
- src/ai_service/prompt_builder.py
- src/pages/04_settings.py
- src/pages/01_reading.py
- src/components/reading_result.py
- src/components/pdf_export.py (新規)
- src/pages/02_history.py
- src/config.py
- pyproject.toml

## スコープ外
- テンプレートのバージョニング・ロールバック
- テンプレートのインポート/エクスポート
- PDF内への画像（命式チャート）埋め込み
