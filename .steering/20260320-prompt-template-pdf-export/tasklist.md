# タスクリスト: プロンプトテンプレート管理 + PDFエクスポート
- 日付: 2026-03-20
- ステータス: 完了

## タスク
### データモデル・DB層
- [x] PromptTemplateRecord を db_service/models.py に追加
- [x] PromptTemplateRepository を新規作成
- [x] config.py にセッションキー追加

### AI連携層
- [x] prompt_builder.py にDB テンプレート対応関数を追加

### UI層（F-012）
- [x] 設定ページにテンプレート管理タブを追加
- [x] 鑑定ページにテンプレート選択UIを追加

### UI層（F-013）
- [x] pdf_export.py を新規作成
- [x] reading_result.py にPDFボタンを追加
- [x] history.py にPDFボタンを追加
- [x] pyproject.toml に reportlab 依存追加

### テスト・レビュー
- [x] ユニットテスト作成・実行（139件全パス）
- [x] コードレビュー・セキュリティチェック
- [x] レビュー指摘事項の修正

### ドキュメント
- [x] functional-design.md 更新
- [x] repository-structure.md 更新

## 完了条件
- [x] テスト通過（139/139）
- [x] レビュー済み・修正完了
