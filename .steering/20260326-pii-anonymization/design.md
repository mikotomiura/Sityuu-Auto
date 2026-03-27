# 設計メモ: PII匿名化レイヤー
- 日付: 2026-03-26

## 実装アプローチ
AI連携層（ai_service/）にPII匿名化モジュールを新設し、プロンプト構築時に名前・フリガナをプレースホルダに置換する。

### 匿名化ルール
| 対象 | 匿名化前 | 匿名化後 |
|------|---------|---------|
| 名前 | 田中太郎 | 相談者様 |
| フリガナ | タナカタロウ | （省略） |

- 名前が空の場合は「（未入力）」のまま（既存挙動を維持）
- フリガナは匿名化時に空文字に置換（音韻鑑定はスキップされる）

### モジュール配置
`src/ai_service/pii_sanitizer.py` に配置。理由：
- 匿名化はプロンプト構築時のみ必要（API送信前の変換）
- utils/privacy.py はブラウザ側の制御に特化しており責務が異なる

### シグネチャ設計（後方互換）
`build_reading_prompt` に `anonymize: bool = False` パラメータを追加。
デフォルト False で既存呼び出し・テストは修正不要。

### 設定の永続化
SESSION_KEY_PII_ANONYMIZE をユーザー設定として扱い、鑑定リセット時にはクリアしない。
設定ページの新タブ「プライバシー」で制御。

## 変更内容
1. `src/ai_service/pii_sanitizer.py` — sanitize_name(), sanitize_name_kana() 関数
2. `src/ai_service/prompt_builder.py` — anonymize パラメータ追加、sanitizer呼び出し
3. `src/config.py` — SESSION_KEY_PII_ANONYMIZE 追加
4. `src/pages/01_reading.py` — session_state から匿名化設定を読み取りprompt_builderに渡す
5. `src/pages/04_settings.py` — プライバシー設定タブ追加

## 代替案
- **悩みテキストも匿名化**: 固有名詞の抽出が必要で複雑。AIの鑑定品質に直結するため今回は見送り
- **utils/privacy.py に統合**: ブラウザ制御とAPI送信前処理の責務が混在するため分離を選択

## 影響範囲
- prompt_builder.py の既存テスト13件 → デフォルト引数により影響なし
- pages/04_settings.py のタブ構成 → 4タブに拡張
