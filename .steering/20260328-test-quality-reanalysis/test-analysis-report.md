# テスト分析レポート
- 実行日時: 2026-03-29
- テスト総数: 338
- 成功: 338 / 失敗: 0 / スキップ: 0

## テスト内訳
- ユニットテスト: 286件
- 統合テスト: 52件
- E2Eテスト: 0件（未実装）

## カバレッジサマリ（全体: 72.0%）

| モジュール | カバレッジ | 目標 | 状態 |
|-----------|----------|------|------|
| fortune_engine/calculator.py | 93.9% | 90% | 達成 |
| fortune_engine/sanmei.py | 97.6% | 90% | 達成 |
| fortune_engine/formatter.py | 100% | 90% | 達成 |
| fortune_engine/models.py | 100% | 90% | 達成 |
| ai_service/client.py | 84.2% | 70% | 達成 |
| ai_service/pii_sanitizer.py | 100% | 70% | 達成 |
| ai_service/prompt_builder.py | 100% | 70% | 達成 |
| db_service/database.py | 94.8% | 80% | 達成 |
| db_service/repositories/auth_session_repo.py | 98.5% | 80% | 達成 |
| db_service/repositories/client_repo.py | 92.3% | 80% | 達成 |
| db_service/repositories/session_repo.py | 90.8% | 80% | 達成 |
| db_service/repositories/prompt_template_repo.py | 95.8% | 80% | 達成 |
| db_service/repositories/invitation_repo.py | 80.8% | 80% | 達成（ギリギリ） |
| db_service/repositories/user_repo.py | 81.1% | 80% | 達成（ギリギリ） |
| utils/auth.py | 17.4% | ※認証層 | 未達成（深刻） |
| utils/validators.py | 97.3% | 90% | 達成 |
| components/pdf_export.py | 88.4% | - | 良好 |
| app.py | 0% | - | 未テスト |
| components/* (UI) | 0% | - | 未テスト（UI層） |
| db_init.py | 0% | - | 未テスト |

## 深刻な未達成項目

### utils/auth.py (17.4% / 167文章 / 138未カバー)
テストされていない関数:
- `get_current_user_id()`, `get_current_display_name()`, `get_current_username()`
- `logout()` — DBセッション無効化パス全体
- `_restore_session_from_user()` — セッション復元ロジック全体
- `_try_restore_from_token()` — トークン検証ロジック全体
- `_login()` — ログインコアロジック全体
- `render_login_form()` — UIレンダリング全体
- `_render_registration_form()` — 招待トークン登録フロー全体
- `require_login()` — セッショントークン復元・招待フロー分岐全体

### 0%モジュール（統計から除外されるべきUI層）
- app.py, components/history_table.py, components/input_form.py
- components/natal_chart_display.py, components/reading_result.py
- components/theme.py, db_init.py

## テストケース品質評価

### 命名規則準拠
- 全338件中335件が `test_[対象]_[条件/期待結果]` パターンに準拠（99.1%）
- クラス命名も `TestXxx` 形式で一貫している

### 境界値・異常系テストの網羅性
- 良好: validators（max_length/min_length境界、空文字、whitespace）
- 良好: user_repo（SQLインジェクション、malformed JSON、存在しないユーザー）
- 良好: client.py（リトライ、認証エラー、フォールバックモデル）
- 不足: auth.py の認証失敗回数制限・ブルートフォース防止ロジック
- 不足: invitation_repo のトークン期限切れ・使用済みトークン境界テスト

### E2Eテスト
- 未実装。Streamlitアプリの動作確認テストは存在しない。

## 推奨アクション

1. [優先度高] utils/auth.py のテストカバレッジ向上（17%→60%以上）
   - logout() の全パス（トークン有無、DB例外）
   - _login() の成功・失敗・失敗回数制限パス
   - require_login() のトークン復元・招待登録フロー
   - Streamlit依存部はモックで対応可能

2. [優先度高] db_init.py のテスト追加（0%、DB初期化スキーマ検証）

3. [優先度中] invitation_repo.py のエラーパステスト追加（80.8%→90%以上）
   - 期限切れトークン、使用済みトークン、DB例外パス

4. [優先度中] user_repo.py のDB例外パステスト追加（81.1%→90%以上）
   - 各操作のDatabaseError発生時の挙動

5. [優先度低] Streamlit UIコンポーネントのスモークテスト導入（pytest-streamlit 等の検討）

