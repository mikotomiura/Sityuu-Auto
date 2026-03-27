# 要件定義: PII匿名化レイヤー
- 日付: 2026-03-26
- 関連Issue/PR: advice.md / architecture.md 4.2

## 目的
LLM API送信時に相談者の個人情報（名前・フリガナ）を匿名化し、外部サービスへの個人情報流出リスクを低減する。
architecture.md 4.2に記載済みだが未実装の要件を実装する。

## 受け入れ条件
- [ ] 名前・フリガナがプレースホルダに置換されてからLLM APIに送信される
- [ ] 匿名化のON/OFFをユーザーが設定画面から制御可能
- [ ] デフォルトは匿名化ON
- [ ] 匿名化ONでも鑑定品質（命式分析・悩み解釈）が維持される
- [ ] 既存テストが破壊されない（後方互換性のあるシグネチャ）
- [ ] 新規ユニットテストが作成されている

## 対象スコープ
- src/ai_service/pii_sanitizer.py（新規）
- src/ai_service/prompt_builder.py（変更）
- src/config.py（SESSION_KEY追加）
- src/pages/01_reading.py（匿名化適用）
- src/pages/04_settings.py（プライバシー設定UI）
- tests/unit/test_pii_sanitizer.py（新規）

## スコープ外
- 悩みテキストの匿名化（AIの鑑定機能に必須のため今回は対象外）
- DB保存時の暗号化（別タスク）
- APIキーの暗号化保存（別タスク）
- ローカルLLM対応（将来拡張）
