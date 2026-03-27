# 要件定義: advice.md 改善案の実装
- 日付: 2026-03-26
- 関連Issue/PR: なし（advice.md による改善提案）

## 目的
advice.md に記載された2つの改善提案を検証・実装する。

### 改善案1: UIデザインの質素さ改善
- **判定: 部分的に有効**
- 既に包括的なカスタムテーマ（theme.py ~300行CSS）が実装済み
- ただしページコンテンツの構造的な質素さは改善余地あり
- ログインページ、ページヘッダー、カード、空状態の視覚強化を実施

### 改善案2: autocomplete による個人情報漏洩リスク
- **判定: 有効（プライバシーバグ）**
- input_form.py のみに autocomplete 無効化が実装されている
- 03_clients.py、auth.py、02_history.py には未適用
- 全フォームに一貫して適用すべき

## 受け入れ条件
- [ ] 全ての個人情報入力フォームで autocomplete が無効化されている
- [ ] ログインページの視覚的リッチ化
- [ ] 各ページヘッダーの装飾強化
- [ ] カード・空状態の視覚的改善

## 対象スコープ
- src/components/theme.py（UI強化CSS追加）
- src/components/input_form.py（autocomplete方式の改善）
- src/pages/03_clients.py（autocomplete適用）
- src/pages/02_history.py（autocomplete適用）
- src/utils/auth.py（autocomplete適用 + ログインUI強化）

## スコープ外
- Streamlit以外のフレームワークへの移行
- 新規ページの追加
- バックエンドロジックの変更
