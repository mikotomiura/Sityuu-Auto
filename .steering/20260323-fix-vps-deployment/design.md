# 設計メモ: VPSデプロイ問題の修正

- 日付: 2026-03-23

## 実装アプローチ

1. ローカルコードの改善（予防的修正）
2. サーバー接続して診断・修正（即時対応）

## 変更内容

### ローカル（コードベース）
1. **`.streamlit/config.toml` を新規作成** — `server.address = "0.0.0.0"`, `headless = true`, `gatherUsageStats = false`
2. **`ecosystem.config.cjs` を新規作成** — PM2 設定を明示的に定義（cwd, script, args, PATH）
3. **`deploy-workflow.md` を全面更新** — 旧プロジェクト（Node.js AI-paper-Canvas_demo）用から現プロジェクト（Python/Streamlit Sityuu-Auto）用に書き換え

### サーバー側
1. **UFW ポート 8501/tcp 開放** — `ufw allow 8501/tcp`
2. **`.streamlit/config.toml` を配置** — 使用統計の無効化とアドレス明示化
3. **PM2 プロセス再起動** — 新設定の反映

## 診断結果

- **根本原因:** ConoHa クラウドファイアウォール（セキュリティグループ）でポート 8501 が許可されていない
- **OS UFW:** 未開放だったため修正（コマンドで対応可能）
- **アプリケーション:** 正常動作中（エラーなし、HTTP 200）
- **PM2:** online 状態、正常リッスン

## 残課題

- ConoHa コントロールパネルでセキュリティグループにポート 8501/tcp を追加する必要あり（Web UI 操作が必要）

## 影響範囲

- デプロイ設定のみ。アプリケーションコードへの変更なし。
