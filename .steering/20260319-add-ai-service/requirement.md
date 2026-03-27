# 要件定義: AI連携層の実装
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
AI連携層（ai_service）のコアモジュールを実装し、LLM APIによる鑑定テキスト生成・傾聴ヒント生成を可能にする。

## 受け入れ条件
- [ ] LLMClient 抽象基底クラスと OpenAI/Anthropic 実装が動作する
- [ ] create_client ファクトリ関数でプロバイダーを切替可能
- [ ] build_reading_prompt が命式テキストと悩みを含む (system_prompt, user_prompt) を返す
- [ ] build_listening_hint_prompt が傾聴ヒント用の (system_prompt, user_prompt) を返す
- [ ] プロンプトテンプレートが templates/ にMarkdown形式で管理される
- [ ] ユニットテストがすべてパスする（モックを使用、実APIは呼ばない）

## 対象スコープ
- src/ai_service/client.py
- src/ai_service/prompt_builder.py
- src/ai_service/templates/reading_base.md
- src/ai_service/templates/listening_hint.md
- src/utils/exceptions.py（AIServiceConfigError 追加）
- tests/unit/test_prompt_builder.py
- tests/unit/test_client.py

## スコープ外
- リトライ機能（別タスクで実装）
- UI層との統合
- プロンプトテンプレートのDB管理（F-012）
