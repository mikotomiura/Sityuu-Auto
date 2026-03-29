# 設計メモ: メールアドレスによるセルフサービスパスワードリセット

- 日付: 2026-03-29

## 実装アプローチ

既存の管理者発行パスワードリセット（PasswordResetRepository）を再利用し、
セルフサービスフローを追加する。

### セルフリセットフロー

1. ログイン画面に「パスワードを忘れた方」リンク表示
2. クリック → メールアドレス入力フォーム表示
3. メールアドレス入力 → ユーザー検索
4. 見つかった場合: リセットトークンを生成し、メール送信
5. 見つからない場合も同じメッセージ（情報漏洩防止）
6. ユーザーはメール内のリンクから既存のリセッ���フォームでパスワー��再設定

### SMTP設定

.envファイルで以下を設定:
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM
- 未設定時はセルフリセット機能を非表示にする

### PasswordResetRepository の変更

`created_by` をセルフリセット時は対象ユーザー自身のIDにする。
既存の管理者発行フローとの互換性を保つ。

## 変更内容

| ファイル | 変更内容 |
|---------|---------|
| `config.py` | SMTP関連定数追加 |
| `models.py` | UserRecord にemail追加 |
| `migrations/008_*.sql` | usersテーブルにemail列追加 |
| `user_repo.py` | find_by_email, update_email追加 |
| `utils/email_sender.py` | 新規: SMTP送信ユーティリティ |
| `auth.py` | セルフリセットフォーム + ログイン画面リンク |
| `pages/04_settings.py` | メールアドレス登録UI |
| `auth.py (_render_registration_form)` | メール入力欄追加 |

## 影響範囲

- UserRecord のフィールド追加 → _row_to_user_record の更新が必要
- 既存テストで UserRecord を生成している箇所は email=None で後方互換
