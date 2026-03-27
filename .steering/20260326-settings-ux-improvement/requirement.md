# 要件定義: 設定ページUX改善（APIキー移動 + 表示名分離）
- 日付: 2026-03-26
- 関連Issue/PR: なし（advice.mdによるフィードバック）

## 目的
1. APIキー管理(BYOK)を「アカウント設定」タブから「API設定」タブに移動し、UXを改善
2. ログイン用ID（username）と表示名（display_name）を分離し、表示名を変更可能にする

## 受け入れ条件
- [ ] APIキー管理がAPI設定タブ内に配置されている
- [ ] アカウント設定タブからAPIキー管理が除去されている
- [ ] usersテーブルにdisplay_nameカラムが追加されている
- [ ] アカウント設定で表示名を変更できる
- [ ] サイドバーの「ログイン中: xxx」に表示名が表示される
- [ ] ログインは引き続きusername（アカウントID）で行う
- [ ] 既存ユーザーのdisplay_nameはusernameの値で初期化される

## 対象スコープ
- src/pages/04_settings.py（タブ構造変更）
- src/db_service/models.py（UserRecord拡張）
- src/db_service/migrations/（新マイグレーション）
- src/db_service/repositories/user_repo.py（update_display_name追加）
- src/utils/auth.py（display_name対応）
- src/config.py（新session_stateキー）
- src/app.py（サイドバー表示名対応）

## スコープ外
- アカウントID（username）の変更機能
