# タスクリスト: advice.md 記載の3バグ修正
- 日付: 2026-03-30
- ステータス: 完了

## タスク
- [x] Bug 3: `_save_session_to_db` を `bool` 戻り値に変更
- [x] Bug 3: 呼び出し元で戻り値チェック＋SESSION_KEY_SESSION_SAVED に反映
- [x] Bug 3: 保存失敗時の再保存UI追加
- [x] Bug 2: `_SUCCESS_MSG_KEY` + `_show_deferred_success()` ヘルパー追加
- [x] Bug 2: 表示名・メール・APIキー保存の成功メッセージをフラグ方式に変更
- [x] Bug 2: テンプレート操作の成功メッセージをフラグ方式に変更
- [x] Bug 1: `auth_session_repo.refresh_expiry()` メソッド追加
- [x] Bug 1: `_try_restore_from_token` でTTLリフレッシュ
- [x] Bug 1: `require_page_auth` でトークン復元を試行
- [x] テスト実行（全404テスト通過）
- [x] コードレビュー（Must Fix 1件対応済み）

## 完了条件
- [x] テスト通過
- [x] レビュー済み
