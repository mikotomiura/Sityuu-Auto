# タスクリスト: セキュリティ強化

- 日付: 2026-03-29
- ステータス: 完了

## タスク

- [x] server.address を 127.0.0.1 に変更
- [x] XSRF/CORS設定を明示化（config.toml コメント追記）
- [x] Referrer-Policy メタタグ追加（app.py）
- [x] セッショントークンのURL即時削除（_try_restore_from_token）
- [x] トークン削除後の st.rerun() 追加（require_login）
- [x] 招待リンクのハードコード修正（05_admin.py）
- [x] テスト実行（338件全通過）
- [x] コードレビュー・指摘対応

## 完了条件

- [x] テスト通過（338/338）
- [x] レビュー済み
