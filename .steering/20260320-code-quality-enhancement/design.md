# 設計メモ: コード品質強化（Phase 2）
- 日付: 2026-03-20

## 実装アプローチ

### 1. AI応答データモデル (src/ai_service/models.py)
- Pydantic BaseModel で AI応答を構造化
- `AIReadingResponse`: 鑑定テキスト応答（raw_text + メタデータ）
- `AIListeningHintResponse`: 傾聴ヒント応答
- `AIResponse`: 統合レスポンス（鑑定 + 傾聴ヒント）
- 現在 str で返している `LLMClient.generate()` の戻り値は変更しない（互換性維持）
- モデルは応答テキストの構造化ラッパーとして機能する

### 2. ロギング設定 (src/utils/logger.py)
- `setup_logging()` 関数で統一設定を提供
- 個人情報マスキングフィルタ (`PrivacyFilter`) を実装
- ファイルハンドラ + コンソールハンドラの2系統
- 各モジュールは従来通り `logging.getLogger(__name__)` を使用

### 3. バリデーション関数 (src/utils/validators.py)
- input_form.py のインラインバリデーションを関数に抽出
- `validate_client_name()`, `validate_birth_date()`, `validate_birth_time()`, `validate_concern()`, `validate_api_key()` を提供
- `ValidationError` を返す or bool + メッセージのタプル

### 4. テストデータ整備
- sample_clients.json: 5件のサンプル相談者データ（名前は架空）
- seed_data.py: init_db.py と同様のパターンでDBに投入

## 変更内容
- 新規ファイル4件 + テストファイル3件 + フィクスチャ1件
- 既存ファイルへの変更なし（Phase 2は土台整備のみ）

## 影響範囲
- 既存コードへの影響なし（新規モジュールの追加のみ）
- 将来的に既存モジュールからこれらのユーティリティを利用する
