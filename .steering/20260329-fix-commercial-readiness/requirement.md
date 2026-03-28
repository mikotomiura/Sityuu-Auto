# 要件定義: 商用販売前の品質・セキュリティ修正

- 日付: 2026-03-29
- 関連: 統合レビューレポート Must Fix 4件

## 目的

ココナラ商用販売のブロッカーとなる4件の問題を修正する。

## 受け入れ条件

- [ ] .env の実在APIキーをダミー値に置換
- [ ] 04_settings.py の XSS脆弱性を修正（html.escape）
- [ ] utils/auth.py のテストカバレッジを17%→60%以上に引き上げ
- [ ] 00_dashboard.py の関数内importをファイル先頭に移動
- [ ] 全既存テスト通過

## 対象スコープ

- .env
- src/pages/04_settings.py
- src/pages/00_dashboard.py
- src/utils/auth.py
- tests/unit/test_auth.py（新規）
