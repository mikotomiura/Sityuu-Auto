# 設計メモ: ココナラ販売前 品質・セキュリティ修正
- 日付: 2026-03-28

## 実装アプローチ
レビューで検出されたMust Fix 3件 + Should Fix 5件を最小限の変更で修正する。

## 変更内容

### セキュリティ
- RSA秘密鍵(key-2026-03-23-21-20.pem, publickey.pem)をgit追跡から除去
- .gitignoreに*.pem *.keyパターンを追加
- cryptography 46.0.5→46.0.6, requests 2.32.5→2.33.0に更新（CVE修正）

### コード品質
- ruff lintエラー7件を修正（import順序、未使用import、f-string、行長超過）
- sqlite3.Row用の.get()はサポートされないため、row.keys()でのチェックにnoqa付与
- assert文をif条件チェック+st.error表示に置換（-Oフラグ対策）
- ValidationError例外クラスを新設し、DatabaseErrorの誤用を修正

### テスト
- auth_session_repo.py: テストを新規作成（20件、カバレッジ0%→98%）
- user_repo.py: update_display_name/find_allテストを追加（9件、カバレッジ75%→81%）

## 代替案
- sqlite3.Rowのdisplay_nameアクセス: row.get()はsqlite3.Rowでサポートされないため不可。
  try/except KeyErrorも検討したが、既存パターンとの一貫性からrow.keys()チェック+noqaを採用。

## 影響範囲
- utils/exceptions.py: ValidationError追加 → user_repo.py, settings.pyが使用
- user_repo.py: ValidationErrorへの変更 → test_user_repo.pyでimport追加
- auth_session_repo.py, user_repo.py: noqa追加 → 機能変更なし
