# 設計メモ: テスト品質再分析

- 日付: 2026-03-28

## 実装アプローチ
1. pytest tests/ -v --tb=short で全件実行
2. pytest --cov=src --cov-report=term-missing で計測
3. 新規テストファイルの内容・命名規則を静的確認
4. 未カバー行の内容確認（除外妥当性を評価）
5. 3回実行でフラキー性チェック（2回実施）

## 分析結果概要

### テスト総数・合否
- 335件 / 335 passed / 0 failed / 0 skipped
- 実行時間: 約15秒（安定）

### カバレッジ（対象3層）
| 層 | カバレッジ | 目標 | 判定 |
|----|-----------|------|------|
| fortune_engine/ | 99%相当（calculator 94%, sanmei 98%, 他100%） | 90% | PASS |
| db_service/ | auth_session 98%, client_repo 92%, invitation 81%, prompt_template 96%, session 91%, user_repo 81% | 80% | PASS（全モジュール80%超） |
| ai_service/ | client.py 84%, models 100%, pii_sanitizer 100%, prompt_builder 100% | 70% | PASS |

### 前回指摘の解消状況
- auth_session_repo: 0% → 98% （解消）
- user_repo: 75% → 81% （解消）

## 残存カバレッジギャップ
- user_repo.py 81%: 未カバー行はすべてexceptブロック（sqlite3.Error）のログ+raise行
- invitation_repo.py 81%: 同様にexcept句（DB障害パス）
- client.py 84%: OpenAI/AnthropicのAPIError except句、Geminiの非retryableエラーパス

## 影響範囲
分析のみ。コード変更なし。
