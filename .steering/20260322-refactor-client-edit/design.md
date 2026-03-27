# 設計メモ: 相談者情報の全フィールド編集対応
- 日付: 2026-03-22

## 実装アプローチ
既存の動的 SQL 組み立てパターン（update メソッド）を拡張し、birth_date / birth_time / gender を追加する。
UI は既存の編集セクションを拡張し、全フィールドの入力ウィジェットを配置する。

## 変更内容

### 1. client_repo.py — update() メソッド
- パラメータ追加: `birth_date: date | None`, `birth_time: str | None`, `gender: str | None`
- birth_time / gender は「未設定に戻す」を区別するためセンチネル値を使用
  - デフォルト値を `_UNSET` とし、None が渡された場合は DB 上で NULL に更新する
  - `_UNSET` が渡された場合（デフォルト）は変更しない

### 2. 03_clients.py — _render_detail_view()
- 基本情報の metric 表示を編集フォームに置き換え
- 名前: text_input
- 生年月日: date_input
- 出生時間: time_input（任意）
- 性別: selectbox（男性/女性/未回答）
- フリガナ・メモ: 既存のまま

### 3. テスト追加
- birth_date, birth_time, gender それぞれの更新テスト

## 代替案
- birth_date 等を不変として扱う → 入力ミス修正ができず不便なため不採用

## 影響範囲
- client_repo.update() を呼び出す箇所: 03_clients.py のみ
- 既存セッションの命式データには影響なし（セッション単位で保存済み）
