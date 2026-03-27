# 設計メモ: 認証システム・BYOK・マルチユーザー対応
- 日付: 2026-03-23

## 実装アプローチ
既存のレイヤードアーキテクチャ（UI→ロジック→AI→DB）に沿い、DB層から順に積み上げる。

1. **DB層**: users テーブル + UserRepository（既存パターン踏襲）
2. **Utils層**: auth.py（ログイン検証・セッション管理）
3. **UI層**: app.py にログインゲート、04_settings.py にパスワード/APIキー管理
4. **AI層**: 01_reading.py の _get_api_key を BYOK フォールバック対応

## 変更内容

### データモデル
- `UserRecord`: id, username, password_hash, api_key, preferred_provider, preferred_model, role, created_at, updated_at
- role は "admin" / "user" の2値（将来拡張可能）
- api_key はプロバイダーごとにJSON形式で保存（{"gemini": "xxx", "openai": "yyy"}）

### 認証フロー
1. app.py: ページ設定後、auth.require_login() を呼び出し
2. 未ログイン → ログインフォーム表示（st.stop()でページ遷移を阻止）
3. ログイン成功 → session_state["auth_user_id"], session_state["auth_username"] を設定
4. 各ページでは auth.py の関数でユーザー情報を取得

### BYOK フォールバック
1. ログインユーザーの api_key (JSON) から現在のプロバイダーのキーを取得
2. あればそれを使用
3. なければ .env のシステムキーにフォールバック

## 代替案
- streamlit-authenticator ライブラリ: 外部依存が増え、カスタマイズ性が低い → 不採用
- JWT: ローカルアプリなので過剰 → session_state で十分

## 影響範囲
- app.py: ログインゲート追加
- 全ページ: ログイン前提
- 01_reading.py: APIキー取得ロジック変更
- 04_settings.py: タブ追加
