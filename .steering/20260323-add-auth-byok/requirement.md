# 要件定義: 認証システム・BYOK・マルチユーザー対応
- 日付: 2026-03-23
- 関連Issue/PR: advice.md

## 目的
シングルユーザーのローカルアプリを、複数ユーザーが利用可能な認証付きシステムに拡張する。
各ユーザーが自身のAPIキーを登録（BYOK）でき、将来的なローカルLLM運用にも対応する基盤を構築する。

## 受け入れ条件
- [ ] bcrypt によるパスワードハッシュ化
- [ ] users テーブル（id, username, password_hash, api_key, preferred_provider, preferred_model, role, created_at, updated_at）
- [ ] ログイン画面（未ログイン時はサイドバー非表示、ログインフォームのみ）
- [ ] セッション管理（st.session_state で user_id を管理）
- [ ] パスワード変更フォーム
- [ ] APIキー登録・更新フォーム（BYOK）
- [ ] AI呼び出し時のフォールバック（ユーザーAPIキー → システム.envキー）
- [ ] 初期アカウント発行スクリプト（scripts/create_user.py）

## 対象スコープ
- src/db_service/migrations/003_add_users.sql
- src/db_service/models.py（UserRecord追加）
- src/db_service/repositories/user_repo.py（新規）
- src/utils/auth.py（新規）
- src/utils/exceptions.py（AuthenticationError追加）
- src/config.py（認証関連キー追加）
- src/app.py（ログインゲート）
- src/pages/04_settings.py（拡張）
- src/pages/01_reading.py（BYOKフォールバック）
- src/db_init.py（初期管理者シード）
- scripts/create_user.py（新規）
- pyproject.toml（bcrypt追加）

## スコープ外
- プレミアムUI（実装済み）
- ユーザー管理画面（管理者向け、将来対応）
- ローカルLLM統合（将来対応だが設計は考慮）
