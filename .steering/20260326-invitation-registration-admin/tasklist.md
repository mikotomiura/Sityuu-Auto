# タスクリスト: 招待リンクによるWebユーザー登録 + 管理者ページ
- 日付: 2026-03-26
- ステータス: 完了

## タスク
- [x] DBマイグレーション: invitation_tokens テーブル追加
- [x] InvitationTokenRecord モデル追加
- [x] InvitationRepository 実装
- [x] UserRepository に find_all / delete 追加
- [x] config.py にセッションキー追加
- [x] auth.py にセルフ登録フォーム追加
- [x] pages/05_admin.py 管理者ページ実装
- [x] app.py にadminページナビゲーション追加
- [x] ユニットテスト作成・実行（55テスト全パス）
- [x] ruff format / ruff check パス
- [x] functional-design.md 更新（F-021, F-022追加）
- [x] repository-structure.md 更新

## 完了条件
- [x] テスト通過
- [x] ruff check パス
