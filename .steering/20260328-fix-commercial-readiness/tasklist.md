# タスクリスト: ココナラ販売前 品質・セキュリティ修正
- 日付: 2026-03-28
- ステータス: 完了

## タスク
- [x] M-1: RSA秘密鍵をGitから除去、.gitignoreに*.pem *.key追加
- [x] M-3: ruff lintエラー7件修正（自動4件+手動3件）
- [x] S-4: assert文をif条件チェック+st.errorに置換
- [x] S-5: ValidationError新設、DatabaseError誤用を修正
- [x] M-2: auth_session_repo テスト新規作成（20件、カバレッジ98%）
- [x] S-3: user_repo update_display_name/find_all テスト追加（9件、カバレッジ81%）
- [x] S-1: 依存パッケージ脆弱性対応（cryptography 46.0.6, requests 2.33.0に更新）
- [x] 全テスト実行（335件全パス）・レビュー完了

## 完了条件
- [x] 全テスト通過（335件）
- [x] ruff check エラー0件
- [x] コードレビュー通過
