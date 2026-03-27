# タスクリスト: Phase 1 — API設定 + 相談者管理
- 日付: 2026-03-20
- ステータス: 完了

## タスク
- [x] ベースラインテスト確認 — 107/107
- [x] config.py: 設定・相談者ページ用キー追加 + API_KEY_ENV_MAP一元化
- [x] pages/04_settings.py: API設定ページ新規作成
- [x] pages/01_reading.py: session_state参照に変更 + API_KEY_ENV_MAP統合
- [x] pages/03_clients.py: 相談者管理ページ新規作成
- [x] app.py: ナビゲーションに2ページ追加
- [x] テスト実行 — 107/107 全パス
- [x] コードレビュー — DRY違反修正、docstring補完、KeyErrorリスク対策
- [x] セキュリティチェック — SQLi対策OK、APIキー非表示OK
- [x] ruff format / ruff check — 全パス

## 完了条件
- [x] テスト通過（107/107）
- [x] ruff check 通過
- [x] レビュー・セキュリティチェック済み
