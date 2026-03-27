# タスクリスト: PII匿名化レイヤー
- 日付: 2026-03-26
- ステータス: 完了

## タスク
- [x] src/ai_service/pii_sanitizer.py を新規作成
- [x] src/ai_service/prompt_builder.py に anonymize パラメータを追加
- [x] src/config.py に SESSION_KEY_PII_ANONYMIZE を追加
- [x] src/pages/01_reading.py で匿名化設定を適用
- [x] src/pages/04_settings.py にプライバシー設定タブを追加
- [x] tests/unit/test_pii_sanitizer.py を新規作成
- [x] コードレビュー・セキュリティチェック実施
- [x] レビュー指摘事項を修正（anonymizeデフォルト値をTrueに変更）
- [x] ドキュメント更新（functional-design.md, architecture.md, repository-structure.md）

## 完了条件
- [x] テスト通過（24件全通過）
- [x] レビュー済み
