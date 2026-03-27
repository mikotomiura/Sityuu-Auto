# 設計メモ: UI層とDB層の接続
- 日付: 2026-03-20

## 実装アプローチ
- Streamlit の `@st.cache_resource` でDB接続をシングルトンキャッシュ
- `src/db_init.py` に薄いラッパーを配置（DB層にStreamlit依存を持ち込まない）
- `01_reading.py` の保存ボタン押下時に ClientRepository.save → SessionRepository.save を順次実行
- 相談者名は session_state に保持し、保存時に参照

## 変更内容
1. `src/db_service/database.py` — `check_same_thread=False` 追加（Streamlit互換）
2. `src/db_init.py`（新規）— `get_db_connection()` を `@st.cache_resource` で提供
3. `src/config.py` — `SESSION_KEY_CLIENT_NAME` 追加
4. `src/pages/01_reading.py` — 保存ボタンのDB接続ロジック実装

## 代替案
- app.py でグローバルにDB接続 → ページごとにimportが面倒、session_stateで渡すのは冗長
- db_service/__init__.py に @st.cache_resource → DB層にStreamlit依存が入り、テスト困難

## 影響範囲
- `01_reading.py` — 保存ロジック追加
- `database.py` — 既存テストに影響なし（check_same_thread はデフォルトのTrueからFalseに変更だが既存テストはインメモリDB使用）
