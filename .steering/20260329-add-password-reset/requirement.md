# 要件定義: パスワードリセット機能

- 日付: 2026-03-29
- 関連Issue/PR: advice.md #1

## 目的

ユーザーがパスワードを忘れた場合に、管理者が発行するリセットリンクを通じてパスワードを再設定できるようにし、UXを向上させる。

## 受け入れ条件

- [ ] 管理者が任意のユーザーに対してパスワードリセットリンクを生成できる
- [ ] リセットリンクにアクセスしたユーザーが新しいパスワードを設定できる
- [ ] リセットトークンは一回使用で無効化される
- [ ] リセットトークンには有効期限がある（デフォルト24時間）
- [ ] 既存の招待トークン機構と同様のセキュリティレベルを確保
- [ ] ユニットテストが通過する

## 対象スコープ

- `src/db_service/migrations/007_add_password_reset_tokens.sql` — 新規テーブル
- `src/db_service/models.py` — PasswordResetTokenRecord 追加
- `src/db_service/repositories/password_reset_repo.py` — 新規リポジトリ
- `src/utils/auth.py` — リセットフォーム表示・処理
- `src/pages/05_admin.py` — リセットリンク発行UI
- `src/config.py` — リセット関連の設定定数
- `tests/unit/test_password_reset_repo.py` — ユニットテスト

## スコープ外

- メール送信によるセルフサービスリセット（ローカルファーストのためSMTP不要）
- メールアドレスの収集・保存
