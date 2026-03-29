# 要件定義: テスト品質再分析（ココナラ商用販売判断）
- 日付: 2026-03-28
- 関連Issue/PR: なし

## 目的
前回テスト分析からの修正（test_auth_session_repo.py新規20件 / test_user_repo.py追加9件）を受け、
ここがテスト品質の最終状態として商用販売可能かを判断する。

## 受け入れ条件
- [ ] 全テストの合否を確認
- [ ] fortune_engine/ 90%以上
- [ ] db_service/ 80%以上
- [ ] ai_service/ 70%以上
- [ ] auth_session_repo 0%問題の解消確認
- [ ] user_repo 75%問題の解消確認
- [ ] 残存リスクをMust/Should/Nice分類

## 対象スコープ
- /Users/johnd/sityu-auto/tests/ 全体
- /Users/johnd/sityu-auto/src/ カバレッジ対象
