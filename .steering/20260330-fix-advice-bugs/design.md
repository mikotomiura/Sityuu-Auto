# 設計メモ: advice.md 記載の3バグ修正
- 日付: 2026-03-30

## 実装アプローチ

### Bug 3: _save_session_to_db の戻り値追加
- `_save_session_to_db` の戻り値を `None` → `bool` に変更
- `True`: 保存成功、`False`: 保存失敗
- 呼び出し元で `SESSION_KEY_SESSION_SAVED = saved` とし、成否をそのまま反映
- 保存失敗時は `SESSION_KEY_SESSION_SAVED = False` となり、再保存UIを表示

### Bug 2: session_state フラグによる成功メッセージ永続化
- `_SUCCESS_MSG_KEY = "_settings_success_msg"` をsession_stateキーとして定義
- 保存成功時: `st.session_state[key] = msg` → `st.rerun()`
- 各タブの描画開始時: `_show_deferred_success()` でメッセージ表示 & クリア
- 対象: API設定、アカウント設定（表示名・メール・APIキー）、テンプレート管理

### Bug 1: セッション復元の多重防御
- `require_page_auth()`: トークンが残っている場合、復元を直接試行
- `auth_session_repo.refresh_expiry()`: トークン復元成功時にTTLを現在時刻+7日に延長
- lazy import で `db_init.get_db_connection` を取得（レイヤー違反を最小化）

## 代替案
- Bug 2: `st.toast()` を使用 → rerun前に送信されても表示されない可能性があるため不採用
- Bug 1: session_stateにauth_session_repoを保存 → SQLite接続はserializableでないため不採用

## 影響範囲
- 鑑定ページ: 保存ステータスの判定ロジック変更
- 設定ページ: 全保存操作のフィードバック方式変更
- 認証: require_page_auth の動作変更（より積極的に復元を試行）
