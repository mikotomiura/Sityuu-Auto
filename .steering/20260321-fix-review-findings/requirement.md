# 要件定義: レビュー指摘事項の一括修正
- 日付: 2026-03-21
- 関連Issue/PR: コードレビュー結果（2026-03-21実施）

## 目的
統合レビューレポートで検出された Must Fix 5件・Should Fix 10件・Nice to Have 7件を一括修正する。

## 受け入れ条件
- [ ] MF-1: Gemini APIキーの失効・再発行（ユーザーアクション）
- [ ] MF-2: バリデーション二重管理の統一
- [ ] MF-3: database.py テストカバレッジ 80%以上
- [ ] MF-4: text_utils.py テストカバレッジ追加
- [ ] MF-5: import 順序修正（02_history.py）
- [ ] SF-1〜SF-10: Should Fix 全件対応
- [ ] NH-1〜NH-7: Nice to Have 全件対応
- [ ] 全テスト通過

## スコープ外
- MF-1（APIキー再発行）はユーザーアクションのため対象外
