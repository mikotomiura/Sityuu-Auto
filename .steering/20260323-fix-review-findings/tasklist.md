# タスクリスト: レビュー指摘事項一括修正
- 日付: 2026-03-23
- ステータス: 完了

## タスク
- [x] MF-1: update_password 戻り値チェック
- [x] MF-2: _auth_fail_count を config.py 定数化 (SESSION_KEY_AUTH_FAIL_COUNT)
- [x] MF-3: .env パーミッション修正 (644→600)
- [x] MF-4: setup_logging() を app.py で呼び出し
- [x] MF-5: パスワード生成関数を user_repo.py に共通化 (generate_random_password)
- [x] SF-1: load_dotenv() を app.py に一本化（ページファイルから削除）
- [x] SF-2: APIキー保存時に strip() バリデーション追加
- [x] SF-3: create_user.py にPW最低文字数チェック追加 (PASSWORD_MIN_LENGTH定数)
- [x] SF-4: PW変更フォームに試行回数制限追加（5回でロックアウト）
- [x] SF-5: --password オプションにシェル履歴の警告をdocstringに追記
- [x] SF-6: UNIQUE INDEX 重複削除（UNIQUE制約のみに統一）
- [x] SF-7: テスト追加 (generate_random_password 4件 + エッジケース 5件 = 計9件)
- [x] 全テスト実行（267件全通過）

## 完了条件
- [x] 全テスト通過（267/267）
- [x] 全12件修正完了
