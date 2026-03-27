# 設計メモ: AI連携層の実装
- 日付: 2026-03-19

## 実装アプローチ
- Strategy パターンで LLMClient を抽象化し、OpenAI/Anthropic を切替可能にする
- プロンプトテンプレートは Markdown ファイルで管理し、${variable_name} 形式で変数を埋め込む
- prompt_builder は (system_prompt, user_prompt) のタプルを返し、クライアントにそのまま渡せる設計
- examples.md の実装例に完全準拠する

## 変更内容
1. src/utils/exceptions.py — AIServiceConfigError を追加
2. src/ai_service/client.py — LLMClient ABC, OpenAIClient, AnthropicClient, create_client
3. src/ai_service/templates/reading_base.md — 鑑定テキスト生成用プロンプト
4. src/ai_service/templates/listening_hint.md — 傾聴ヒント生成用プロンプト
5. src/ai_service/prompt_builder.py — build_reading_prompt, build_listening_hint_prompt
6. tests/unit/test_prompt_builder.py — プロンプトビルダーのテスト
7. tests/unit/test_client.py — LLMクライアントのモックテスト

## 影響範囲
- src/utils/exceptions.py（新例外追加のみ、既存コードへの影響なし）
- src/ai_service/（新規モジュール群）
