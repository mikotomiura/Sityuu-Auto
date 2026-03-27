# 設計メモ: 招待リンクによるWebユーザー登録 + 管理者ページ
- 日付: 2026-03-26

## 実装アプローチ

### 招待トークンの仕組み
- `secrets.token_urlsafe(32)` で安全なトークンを生成
- invitation_tokens テーブルに保存（有効期限付き、ワンタイム）
- URLクエリパラメータ `?token=xxx` でトークンを受け渡し
- `st.query_params` でトークンを検出し、登録フォームを表示

### 登録フロー
1. 管理者が管理画面で「招待リンクを生成」
2. URLが表示される（例: `http://host:8501/?token=abc123`）
3. 招待URLにアクセスすると、ログイン画面の代わりに登録フォームが表示
4. ユーザー名・パスワード・パスワード確認を入力して登録
5. トークンは使用済みにマーク、ユーザーはログイン画面へ

### 管理者ページ
- pages/05_admin.py に配置
- app.py のナビゲーションでadminロール判定
- タブ構成: 「ユーザー管理」「招待リンク管理」

## 変更内容
| ファイル | 変更種別 | 内容 |
|---|---|---|
| src/db_service/migrations/004_add_invitation_tokens.sql | 新規 | 招待トークンテーブルDDL |
| src/db_service/models.py | 修正 | InvitationTokenRecord 追加 |
| src/db_service/repositories/invitation_repo.py | 新規 | 招待トークンCRUD |
| src/db_service/repositories/user_repo.py | 修正 | find_all, delete 追加 |
| src/config.py | 修正 | セッションキー追加 |
| src/utils/auth.py | 修正 | セルフ登録フォーム追加 |
| src/pages/05_admin.py | 新規 | 管理者ページ |
| src/app.py | 修正 | ナビゲーションにadminページ追加 |
| tests/unit/test_invitation_repo.py | 新規 | 招待トークンテスト |

## 代替案
- メール招待方式 → メールサーバー不要のため却下
- 登録コード（短いコード）方式 → URLパラメータのほうがUXが良い

## 影響範囲
- 認証フロー（auth.py）に分岐追加
- app.py のナビゲーション構成
- db_init.py でマイグレーション自動適用
