# 要件定義: ココナラ販売前 品質・セキュリティ修正
- 日付: 2026-03-28
- 関連Issue/PR: なし（レビュー結果に基づく修正）

## 目的
統合コードレビューで検出されたMust Fix 3件 + Should Fix 5件を修正し、ココナラ販売可能な状態にする。

## 受け入れ条件
- [ ] M-1: RSA秘密鍵がGit追跡対象から除去されている
- [ ] M-2: auth_session_repo.pyのテストカバレッジが80%以上
- [ ] M-3: ruff check src/ がエラー0件
- [ ] S-1: 依存パッケージの既知CVEが解消されている
- [ ] S-3: user_repo.pyのカバレッジが80%以上
- [ ] S-4: assert文がカスタム例外に置換されている
- [ ] S-5: ValidationErrorが新設されDatabaseError誤用が修正されている
- [ ] 全306件以上のテストがパス

## 対象スコープ
- .gitignore
- src/components/input_form.py
- src/utils/exceptions.py
- src/db_service/repositories/user_repo.py
- src/ai_service/prompt_builder.py
- src/pages/04_settings.py
- src/pages/01_reading.py
- src/app.py
- src/db_service/repositories/auth_session_repo.py
- tests/unit/test_auth_session_repo.py（新規）
- tests/unit/test_user_repo.py（追加）

## スコープ外
- パフォーマンス改善（キャッシュ・インデックス）
- UI/UXの変更
- PII匿名化OFF時の同意確認フロー
