# 設計メモ: advice.md 記載のバグ修正・改善

- 日付: 2026-03-30

## 実装アプローチ

### Bug#1: セッション永続化強化

**原因分析:** Streamlit の `st.query_params` がページ遷移・リロード時に消失するケースがある。
特に DB ロック問題（修正済み）の影響で `validate_token()` が失敗し、トークンがURLから削除される可能性があった。

**修正方針:**
- Cookie バックアップ: ログイン成功時に `st.html()` で JavaScript を注入し Cookie にトークンを保存
- `_try_restore_from_token()` で query_params にトークンがない場合、Cookie（`st.context.headers`）からフォールバック取得
- ログアウト時に Cookie を削除

### Bug#2: 相談者の重複検知

**修正方針:**
- `ClientRepository` に `find_duplicate(name, birth_date, user_id)` メソッドを追加
- `_save_session_to_db()` で新規作成前に重複チェックし、既存レコードがあればその `client_id` を再利用

### 改善#3: 保存成功通知

**修正方針:**
- 主要な保存操作に `st.toast()` を追加（既存の `st.success()` に加え、浮動通知で視認性向上）

### 改善#4: 管理者ユーザー一覧の情報拡充

**修正方針:**
- `_render_user_management()` に `display_name` と `email` の表示を追加
- `UserRecord` は既にこれらのフィールドを持つため、DB・モデル変更は不要

## 影響範囲

- 認証フロー（auth.py）
- 鑑定保存フロー（reading.py, client_repo.py）
- 各ページのUI表示（admin, settings, clients, reading）
