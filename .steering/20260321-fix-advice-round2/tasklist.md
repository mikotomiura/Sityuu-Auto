# タスクリスト: advice.md 改善案（第2弾）
- 日付: 2026-03-21
- ステータス: 完了

## タスク
- [x] config.py に SESSION_KEY_FORM_VERSION / API_MAX_RETRIES / API_RETRY_BASE_WAIT 追加、タイムアウト 30→60 変更
- [x] input_form.py でフォームキーにバージョンを使用
- [x] 01_reading.py の _clear_reading_state() でバージョンインクリメント
- [x] ai_service/client.py にリトライ機構追加（OpenAI / Anthropic / Gemini）
- [x] レビュー指摘修正: ハードコード値を config 定数に統一（max_tokens / temperature / timeout）
- [x] テスト実行（175/175 パス）
- [x] コードレビュー（指摘事項修正済み）

## 完了条件
- [x] テスト通過
- [x] レビュー済み
