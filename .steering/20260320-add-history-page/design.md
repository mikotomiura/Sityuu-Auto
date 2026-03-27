# 設計メモ: 鑑定履歴閲覧ページ
- 日付: 2026-03-20

## 実装アプローチ

### ページ構成
02_history.py は2つのビューを持つ:
1. **一覧ビュー**: セッション一覧テーブル（相談者名・悩み概要・日付）+ 検索フィルタ
2. **詳細ビュー**: 選択したセッションの全情報（命式・AIレポート・傾聴ヒント）+ MDエクスポート

session_state でビュー切り替えを管理する。

### データフロー
1. SessionRepository.find_all() / search() → SessionRecord リスト
2. ClientRepository.find_by_id() で相談者名を逆引き
3. 詳細ビューでは NatalChart.model_validate_json() で命式を復元 → render_reading_result() で表示

### 新規メソッド
- SessionRepository に search_with_client() メソッドを追加（sessions JOIN clients で名前検索可能に）

## 変更内容
1. src/config.py — 履歴ページ用 session_state キー追加
2. src/db_service/repositories/session_repo.py — 検索メソッド追加
3. src/components/history_table.py — 一覧テーブルコンポーネント（新規）
4. src/pages/02_history.py — 履歴ページ（新規）

## 影響範囲
- 既存ファイルへの変更は config.py（定数追加のみ）と session_repo.py（メソッド追加のみ）
- 既存の render_reading_result() を詳細ビューで再利用
