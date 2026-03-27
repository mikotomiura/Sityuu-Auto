# タスクリスト: Gemini プロバイダー追加
- 日付: 2026-03-19
- ステータス: 完了

## タスク
- [x] google-genai パッケージをインストール
- [x] pyproject.toml に依存追加
- [x] config.py に Gemini 設定を追加、デフォルトプロバイダーを gemini に変更
- [x] ai_service/client.py に GeminiClient を追加（フォールバック機構付き）
- [x] pages/01_reading.py の _get_api_key に gemini 分岐を追加
- [x] .env.example に GEMINI_API_KEY を追加
- [x] 起動確認（HTTP 200 OK）
- [x] Gemini API 実呼び出し確認（成功: "ようこそ。星々がお呼びですね。"）
- [x] コードレビュー実施

## 完了条件
- [x] streamlit run src/app.py で起動し、Gemini でAI鑑定が動作すること
