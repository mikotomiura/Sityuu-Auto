# 要件定義: UI層とDB層の接続（鑑定結果保存）
- 日付: 2026-03-20
- 関連Issue/PR:

## 目的
鑑定ページ（01_reading.py）の「鑑定結果を保存」ボタンを実際にDB保存に接続し、
相談者情報と鑑定セッションデータをSQLiteに永続化する。

## 受け入れ条件
- [ ] 鑑定結果の保存ボタン押下で、相談者がclientsテーブルに保存される
- [ ] 同時にセッションデータ（命式・AI鑑定テキスト・傾聴ヒント等）がsessionsテーブルに保存される
- [ ] DB接続がStreamlitの再実行に耐えるよう @st.cache_resource でキャッシュされる
- [ ] 保存成功時にユーザーフィードバックを表示する
- [ ] エラー時に適切なエラーメッセージを表示する
- [ ] 既存テストが壊れない

## 対象スコープ
- `src/db_service/database.py` — Streamlit互換のcheck_same_thread対応
- `src/db_init.py`（新規）— Streamlit用DB接続キャッシュ
- `src/pages/01_reading.py` — 保存ボタンのDB接続
- `src/config.py` — 相談者名のsession_stateキー追加

## スコープ外
- 鑑定履歴一覧ページ（02_history.py）
- 相談者管理ページ（03_clients.py）
- 設定ページ（04_settings.py）
