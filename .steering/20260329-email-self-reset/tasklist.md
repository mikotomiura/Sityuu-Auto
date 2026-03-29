# タスクリスト: メールアドレスによるセルフサービスパスワードリセット

- 日付: 2026-03-29
- ステータス: 完了

## タスク

- [x] config.py にSMTP関連定数追加
- [x] 008_add_email_to_users.sql マイグレーション作成
- [x] models.py の UserRecord にemail追加
- [x] user_repo.py に find_by_email, update_email 追加 + _row_to_user_record 更新
- [x] auth_session_repo.py の UserRecord生成にemail追加
- [x] utils/email_sender.py 作成
- [x] auth.py にセルフリセットフォーム追加 + ログイン画面リンク
- [x] 04_settings.py にメールアドレス登録UI追加
- [x] auth.py の登録フォームにメール入力欄追加
- [x] .env.example にSMTP設定テンプレート追加
- [x] テスト作成・実行（393件全通過）
- [x] セキュリティチェック
- [x] ドキュメント更新（functional-design, repository-structure, architecture, README）

## 完了条件

- [x] テスト通過（393件全通過）
- [x] レビュー済み
