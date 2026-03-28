# 設計メモ: ページ認証の防御深度強化

- 日付: 2026-03-29

## 実装アプローチ

utils/auth.pyに`require_page_auth()`関数を追加し、各ページのmain()冒頭で呼び出す。

- `is_logged_in()`がFalseならst.error + st.stop()
- 管理者ページでは`_require_admin()`の前にこのチェックを入れる

## 変更内容

1. `src/utils/auth.py`: `require_page_auth()`関数を追加
2. `src/pages/00_dashboard.py`: main()冒頭にチェック追加
3. `src/pages/01_reading.py`: 同上
4. `src/pages/02_history.py`: 同上
5. `src/pages/03_clients.py`: 同上
6. `src/pages/04_settings.py`: 同上
7. `src/pages/05_admin.py`: _require_admin()内にis_logged_inチェックを追加

## 影響範囲

- 通常の認証フローには影響なし（app.pyのゲートが先に動作）
- 万が一app.pyゲートが迂回された場合のフォールバックとして機能
