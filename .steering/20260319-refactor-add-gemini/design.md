# 設計メモ: Gemini プロバイダー追加
- 日付: 2026-03-19

## 実装アプローチ
既存の Strategy パターン（LLMClient ABC）をそのまま活かし、GeminiClient を追加する。
フォールバックは GeminiClient 内部で候補モデルリストを順次試行する方式。

## 変更内容

### ai_service/client.py
- `GeminiClient(LLMClient)` を追加
  - google-genai SDK を使用
  - `models: list[str]` を受け取り、先頭から順に試行
  - 404（モデル利用不可）/ 429（レート制限）の場合に次のモデルへフォールバック
  - 全モデル失敗時に AIServiceError を送出
- `create_client()` に `provider="gemini"` 分岐を追加

### config.py
- `DEFAULT_API_PROVIDER` を `"gemini"` に変更
- `DEFAULT_MODEL` を `"gemini-2.5-flash"` に変更
- `GEMINI_FALLBACK_MODELS` リストを追加

### pages/01_reading.py
- `_get_api_key()` に `"gemini"` 分岐を追加（GEMINI_API_KEY）

### pyproject.toml
- `google-genai>=1.0` を dependencies に追加

## フォールバック戦略
```
gemini-2.5-flash → gemini-2.5-flash-lite → gemini-2.5-pro
```
- 404 (NOT_FOUND): モデル自体が利用不可 → 次のモデルへ
- 429 (RESOURCE_EXHAUSTED): レート制限 → 次のモデルへ
- 401 (UNAUTHENTICATED): APIキー不正 → 即座にエラー（フォールバックしない）
- その他: 即座にエラー
