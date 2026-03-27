# タスクリスト: レビュー指摘事項の一括修正
- 日付: 2026-03-21
- ステータス: 完了

## Must Fix
- [x] MF-2: input_form.py でバリデータ関数を使うよう統一
- [x] MF-3: database.py のテスト追加（14テスト追加）
- [x] MF-4: text_utils.py のテスト追加（7テスト追加）
- [x] MF-5: 02_history.py の import 順序修正

## Should Fix
- [x] SF-1: _save_session_to_db のエラーメッセージ固定化（ロジック自体は既に適切に分離済み）
- [x] SF-2: st.error(str(e)) を固定文字列に変更（04_settings.py 全4箇所、01_reading.py 1箇所）
- [x] SF-3: PromptTemplateRecord.is_default を bool 化
- [x] SF-4: typing.Any を除去 → TypedDict (DisplayData) に変更
- [x] SF-5: _render_human_star_chart の引数型を DisplayData に変更
- [x] SF-6: docstring の Args/Returns 追加（4関数）
- [x] SF-7: DB リポジトリの except sqlite3.Error テスト追加（19テスト追加）
- [x] SF-8: ai_service/client.py リトライテスト追加（5テスト追加）
- [x] SF-9: .env.example の sk- プレフィックス除去
- [x] SF-10: validate_birth_time のスタブ削除（関数・テスト両方）

## Nice to Have
- [x] NH-1: 03_clients.py の N+1 問題修正（count_sessions_by_client メソッド追加）
- [x] NH-2: 02_history.py にページネーション適用（limit=50）
- [x] NH-3: マジックナンバー統一（CONCERN_PREVIEW_LENGTH = 40）
- [x] NH-4: _fonts_registered を functools.lru_cache に変更
- [x] NH-5: SF-1 再検討: build_reading_report_markdown は reading_result.py にあるが、現状のコンポーネント構成で適切
- [x] NH-6: 統合テストの DB フィクスチャを integration/conftest.py に集約
- [x] NH-7: unsafe_allow_html 3箇所にセキュリティコメント追加

## 完了条件
- [x] 全テスト通過（224テスト / 0失敗）
- [x] ruff format / ruff check クリア
