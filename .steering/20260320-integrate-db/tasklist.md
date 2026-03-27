# タスクリスト: UI層とDB層の接続
- 日付: 2026-03-20
- ステータス: 完了

## タスク
- [x] `src/db_service/database.py` に `check_same_thread=False` 追加
- [x] `src/db_init.py` 新規作成（@st.cache_resource でDB接続キャッシュ）
- [x] `src/config.py` に `SESSION_KEY_CLIENT_NAME` 等追加
- [x] `src/pages/01_reading.py` の保存ボタンをDB接続に実装
- [x] 既存テスト実行（91件全パス）
- [x] code-reviewer レビュー → 重大2件修正（except Exception→DatabaseError、エラーメッセージ露出）
- [x] security-checker レビュー → DBファイルパーミッション修正（644→600）
- [x] レビュー指摘事項修正後テスト再実行（91件全パス）

## 完了条件
- [x] 保存ボタンが実際にDBへ書き込む
- [x] 既存テスト全パス
- [x] レビュー指摘事項修正済み
