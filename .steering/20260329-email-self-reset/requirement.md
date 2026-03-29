# 要件定義: メールアドレスによるセルフサービスパスワードリセット

- 日付: 2026-03-29
- 関連: advice.md #1, .steering/20260329-add-password-reset/

## 目的

管理者に連絡せずとも、ユーザーが自力でパスワードをリセットできるようにする。
メールアドレスを登録済みのユーザーは、ログイン画面からメールでリセットリンクを受け取り再設定できる。

## 受け入れ条件

- [ ] usersテーブルにemail列が追加されている
- [ ] 設定ページでメールアドレスを登録・変更できる
- [ ] 新規登録時にメールアドレスを任意入力できる
- [ ] ログイン画面に「パスワードを忘れた方」リンクがある
- [ ] メールアドレス入力→リセットリンクがメール送信される
- [ ] SMTP設定は.envで管理される（未設定時はセルフリセット無効）
- [ ] 既存の管理者発行リセット機能は引き続き利用可能
- [ ] ユニットテストが通過する

## 対象スコープ

- `src/db_service/migrations/008_add_email_to_users.sql`
- `src/db_service/models.py` — UserRecord にemail追加
- `src/db_service/repositories/user_repo.py` — find_by_email, update_email追加
- `src/utils/email_sender.py` — 新規: SMTP送信ユーティリティ
- `src/utils/auth.py` — セルフリセットフォーム追加
- `src/pages/04_settings.py` — メールアドレス登録UI
- `src/config.py` — SMTP関連定数

## スコープ外

- メールアドレスの検証（確認メール送信）
- 複数メールアドレスの登録
