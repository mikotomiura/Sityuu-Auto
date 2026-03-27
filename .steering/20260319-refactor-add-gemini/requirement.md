# 要件定義: Gemini プロバイダー追加 + モデルフォールバック機構
- 日付: 2026-03-19

## 目的
MVP検証のため、無料枠のGoogle Gemini APIを利用可能にする。
モデルの利用可不可が変動するため、複数モデルを順次試行するフォールバック機構を導入する。

## 受け入れ条件
- [ ] `GEMINI_API_KEY` を `.env` に設定すれば Gemini でAI鑑定が動作する
- [ ] config.py の `DEFAULT_API_PROVIDER` を `"gemini"` に変更するだけで切替可能
- [ ] モデル利用不可時に次のモデルへ自動フォールバックする
- [ ] 既存の OpenAI / Anthropic クライアントは変更なし

## 対象スコープ
- `src/ai_service/client.py` — GeminiClient 追加、create_client 拡張
- `src/config.py` — Gemini 用デフォルト設定追加、プロバイダー切替
- `src/pages/01_reading.py` — _get_api_key に Gemini 対応追加
- `pyproject.toml` — google-genai 依存追加

## スコープ外
- Gemini 固有のプロンプト最適化
- Vertex AI（GCP サービスアカウント）対応
