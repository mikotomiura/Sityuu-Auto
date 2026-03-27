# 設計メモ: DB拡張子統一・AI鑑定レポートMDエクスポート
- 日付: 2026-03-20

## 実装アプローチ

### 改善1: DB_PATH統一
- config.py の `DB_PATH` を `Path` 型に変更し `.sqlite3` 拡張子に統一
- database.py から独自の `DB_PATH` を削除し、config.py からインポート
- database.py の `create_connection()` に既存 `.db` ファイルの自動リネーム処理を追加
- db_init.py は database.py 経由で DB_PATH を取得（変更なし）

### 改善2: MDエクスポート
- reading_result.py に `build_reading_report_markdown()` 関数を追加
- 命式情報 + AI鑑定テキスト + 傾聴ヒントを統合したMarkdownテキストを生成
- `st.download_button` でMDファイルダウンロードを提供
- ファイル名: `鑑定レポート_{相談者名}_{日付}.md`

## 変更内容
1. config.py: DB_PATH を Path 型 + `.sqlite3` 拡張子に変更
2. database.py: DB_PATH 削除、config からインポート、旧DB自動移行ロジック追加
3. db_init.py: import元を database.py → config.py に変更
4. components/reading_result.py: MDエクスポート機能追加
5. pages/01_reading.py: エクスポートボタン用の相談者名をコンポーネントに渡す

## 影響範囲
- DB層: パスの参照元が変わるのみ、動作に変更なし
- UI層: ダウンロードボタンの追加（既存動作に影響なし）
