# タスクリスト: セッション永続化 + サイドバー修正
- 日付: 2026-03-26
- ステータス: 完了

## タスク
- [x] CSSセレクタをStreamlit 1.55対応に更新（要素型指定を除去、テストID更新）
- [x] auth_sessionsテーブル用マイグレーション作成（005_add_auth_sessions.sql）
- [x] AuthSessionRecordモデル追加（models.py）
- [x] AuthSessionRepositoryリポジトリ作成（auth_session_repo.py）
- [x] セッション関連定数追加（config.py）
- [x] auth.pyにトークン生成・復元・無効化ロジック追加
- [x] app.pyにauth_session_repo統合
- [x] テスト実行（全288件パス）
- [x] デプロイ + マイグレーション適用

## 完了条件
- [x] 既存テスト通過
- [x] VPSデプロイ完了
- [x] auth_sessionsテーブル作成確認
