# タスクリスト: テスト品質再分析
- 日付: 2026-03-28
- ステータス: 完了

## タスク
- [x] pytest tests/ -v --tb=short 全件実行・合否確認
- [x] pytest --cov=src --cov-report=term-missing カバレッジ計測
- [x] fortune_engine/ / db_service/ / ai_service/ 目標達成確認
- [x] auth_session_repo 0%解消確認
- [x] user_repo 75%→81%解消確認
- [x] 新規テストの命名規則・境界値・異常系確認
- [x] フラキー性確認（2回実行、同結果）
- [x] 残存リスク分類（Must/Should/Nice）

## 完了条件
- [x] テスト通過（335/335）
- [x] レポート出力
