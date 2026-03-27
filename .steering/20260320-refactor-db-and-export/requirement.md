# 要件定義: DB拡張子統一・AI鑑定レポートMDエクスポート
- 日付: 2026-03-20
- 関連Issue/PR: advice.md 改善案 #1, #2

## 目的
1. DB_PATH の定義を一本化し、拡張子を `.sqlite3` に統一してDBブラウザツールとの互換性を向上
2. AI鑑定レポートをMarkdownファイルとしてダウンロードできる機能を追加

## 受け入れ条件
- [ ] DB_PATH が config.py のみで定義され、他モジュールはそこからインポートしている
- [ ] DB拡張子が `.sqlite3` に統一されている
- [ ] 既存 `.db` ファイルがある場合、自動的にリネーム移行される
- [ ] AI鑑定レポート生成後、MDファイルとしてダウンロードできるボタンが表示される
- [ ] ダウンロードされるMDファイルに命式情報・鑑定テキスト・傾聴ヒントが含まれる
- [ ] 全テストが通過する

## 対象スコープ
- src/config.py
- src/db_service/database.py
- src/db_init.py
- src/components/reading_result.py
- src/pages/01_reading.py

## スコープ外
- DB Browser for SQLite 等の外部ツールの設定
- PDF エクスポート（将来対応）
- 履歴ページからのエクスポート（将来対応）
