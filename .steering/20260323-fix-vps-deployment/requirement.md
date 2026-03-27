# 要件定義: VPSデプロイ問題の修正

- 日付: 2026-03-23
- 関連Issue/PR: なし（advice.md による改善指示）

## 目的

ConoHa VPS上の Sityuu-Auto（Streamlit アプリ）がブラウザからアクセスできない問題を解決する。

## 受け入れ条件

- [ ] `.streamlit/config.toml` でサーバーアドレスを `0.0.0.0` に設定
- [ ] PM2 用 `ecosystem.config.js` を作成
- [ ] `deploy-workflow.md` を現プロジェクト（Python/Streamlit）用に更新
- [ ] サーバー上で UFW ポート 8501 が開放されている
- [ ] サーバー上で PM2 プロセスが online で 8501 をリッスン

## 対象スコープ

- `.streamlit/config.toml`（新規）
- `ecosystem.config.js`（新規）
- `deploy-workflow.md`（更新）
- サーバー側設定（UFW、PM2、.env、依存パッケージ）

## スコープ外

- アプリケーション機能の変更
- CI/CD パイプライン構築
