# 設計メモ: Phase 1 — API設定 + 相談者管理
- 日付: 2026-03-20

## F-014: API設定ページ
### 実装アプローチ
- session_stateでプロバイダー・モデルを管理（既にキーが定義済み）
- 設定ページでselectbox/text_inputで設定変更
- 01_reading.pyをDEFAULT_*ハードコードからsession_state参照に変更
- APIキーは.envから読み取り、設定済みかどうかをステータス表示

### UI構成
- プロバイダー選択（selectbox: openai/anthropic/gemini）
- モデル名入力（text_input + プロバイダー別のデフォルト候補）
- APIキーステータス表示（設定済み/未設定）
- APIキー自体は.envでの管理を維持（セキュリティ上UIには入力させない）

## F-011: 相談者管理ページ
### 実装アプローチ
- client_repoの既存メソッド（find_all, search_by_name, update）を活用
- session_repoのfind_by_client_id()で鑑定回数を取得
- 一覧→詳細の2ビュー構成（02_historyと同パターン）

### UI構成
- 一覧ビュー: 検索フィルタ + 相談者カード（名前・生年月日・鑑定回数）
- 詳細ビュー: 相談者情報表示 + メモ編集 + 鑑定履歴リンク

## 影響範囲
- 01_reading.py: provider/modelの参照元をsession_stateに変更
- app.py: ナビゲーションに2ページ追加
