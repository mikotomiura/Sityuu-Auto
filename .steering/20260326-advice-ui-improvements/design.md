# 設計メモ: advice.md UI改善3点
- 日付: 2026-03-26

## 実装アプローチ

### 1. サイドバートグル復元
- theme.pyの`header[data-testid="stHeader"]`を`display:none`から`background:transparent`に変更
- ツールバー・デコレーション・ステータスウィジェットは引き続き非表示
- サイドバートグルボタンはstHeader内に含まれるため、ヘッダー自体は残す必要がある

### 2. 入力欄のplaceholder化
- `st.date_input`の`value`を`date(1990,1,1)`から`None`に変更
- `st.time_input`の`value`を`None`に変更（未選択状態で表示）
- Streamlitのネイティブ機能で空欄表示をサポート

### 3. バリデーション強化
- `validate_birth_date()`にNoneチェックを追加（型を`date | None`に拡張）
- `input_form.py`のバリデーション処理に`validate_birth_date`呼び出しを追加

## 影響範囲
- 鑑定ページ（01_reading.py）の入力フォーム表示
- 全ページのヘッダー/サイドバー表示
