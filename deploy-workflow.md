# デプロイワークフロー

本番サーバー (ConoHa VPS) へのデプロイ手順をコマンド付きで解説する。

---

## 1. サーバー情報

| 項目 | 値 |
|------|-----|
| ホスト | `160.251.214.57` |
| SSH ユーザー | `root` |
| SSH 鍵 | `~/.ssh/conoha_key.pem`（ローカル Mac 上） |
| アプリディレクトリ | `/root/Sityuu-Auto` |
| プロセスマネージャ | PM2 |
| PM2 プロセス名 | `sityuu-auto` |
| ポート | `8501` |
| URL | `http://160.251.214.57:8501` |
| Python | 3.11（deadsnakes PPA） |
| 仮想環境 | `/root/Sityuu-Auto/.venv` |

---

## 2. 初回セットアップ

```bash
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57

# リポジトリのクローン
cd /root
git clone https://github.com/mikotomiura/Sityuu-Auto.git
cd Sityuu-Auto

# Python 仮想環境の作成と依存パッケージインストール
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .

# .env の作成
cp .env.example .env
nano .env  # API キーを設定

# データベース初期化
python scripts/init_db.py

# 管理者ユーザー作成
python scripts/create_user.py admin --role admin

# UFW でポート 8501 を開放
ufw allow 8501/tcp

# PM2 でアプリを起動
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup
```

---

## 3. デプロイ（コード更新 → 本番反映）

ローカルターミナルから以下のワンライナーを実行する。

```bash
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 \
  "cd /root/Sityuu-Auto && git pull && source .venv/bin/activate && pip install -e . && pm2 restart sityuu-auto"
```

**実行される処理:**

1. `git pull` — GitHub から最新コードを取得
2. `pip install -e .` — 依存パッケージを更新
3. `pm2 restart sityuu-auto` — アプリプロセスを再起動

---

## 4. デプロイ後の確認

```bash
# PM2 ステータス確認（online になっていれば OK）
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 list"

# 起動ログを確認（エラーが出ていないか）
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 logs sityuu-auto --lines 30 --nostream"

# ポートリッスン確認
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "ss -tulpn | grep 8501"
```

---

## 5. VPS 運用コマンド集

### SSH 接続

```bash
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57
```

### PM2 操作

```bash
# ステータス一覧
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 list"

# ログ確認（直近 50 行）
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 logs sityuu-auto --lines 50 --nostream"

# リアルタイムログ（Ctrl+C で終了）
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 logs sityuu-auto"

# 再起動
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 restart sityuu-auto"

# 停止
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 stop sityuu-auto"

# 起動（ecosystem から）
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "cd /root/Sityuu-Auto && pm2 start ecosystem.config.cjs"
```

### 環境変数の更新

```bash
# SSH で接続してから .env を編集
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57
nano /root/Sityuu-Auto/.env

# 編集後、アプリを再起動して反映
pm2 restart sityuu-auto
```

---

## 6. トラブルシューティング

### アプリにブラウザからアクセスできない

```bash
# 1. UFW でポート 8501 が開いているか確認
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "ufw status | grep 8501"

# 2. ポートがリッスンされているか確認
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "ss -tulpn | grep 8501"

# 3. PM2 プロセスの状態確認
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 list"

# 4. エラーログ確認
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 "pm2 logs sityuu-auto --lines 100 --nostream"
```

### PM2 プロセスが消えた

```bash
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 \
  "cd /root/Sityuu-Auto && pm2 start ecosystem.config.cjs && pm2 save"
```

### git pull で認証エラー

```bash
# GitHub PAT の期限切れ → リモート URL を更新
ssh -i ~/.ssh/conoha_key.pem root@160.251.214.57 \
  "cd /root/Sityuu-Auto && git remote set-url origin https://<NEW_TOKEN>@github.com/mikotomiura/Sityuu-Auto.git"
```
