# /test — テスト実行ワークフロー

テストの実行・分析・改善を行う際のワークフロー。単体→統合→カバレッジ確認の順に実行する。

---

## 1. テスト対象の確認

1. `docs/development-guidelines.md` のテスト戦略セクションを確認
2. テスト対象のスコープを決定する：
   - **全体テスト:** 変更が広範囲に及ぶ場合、リリース前
   - **モジュールテスト:** 特定モジュールの変更後
   - **単一ファイルテスト:** 特定ファイルのデバッグ中

## 2. テスト環境の準備

1. 依存パッケージがインストールされているか確認

```bash
pip install -e ".[dev]"
```

2. テストDB（SQLite）が初期化されているか確認
3. テストフィクスチャ（`tests/fixtures/`）が最新か確認

## 3. ユニットテストの実行

**サブエージェント `test-runner` を起動** し、ユニットテストを実行：

```bash
pytest tests/unit/ -v --tb=short
```

対象モジュール別の確認：
- `test_calculator.py` — 命式算出ロジック
- `test_sanmei.py` — 算命学データ算出ロジック
- `test_prompt_builder.py` — プロンプト構築
- `test_validators.py` — バリデーション関数

## 4. 統合テストの実行

```bash
pytest tests/integration/ -v --tb=short
```

対象：
- `test_fortune_flow.py` — 入力→命式算出→AI連携の一連フロー
- `test_db_operations.py` — DB読み書きの一連操作

## 5. カバレッジ計測

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

カバレッジ目標との比較：
| モジュール | 目標 |
|-----------|------|
| `fortune_engine/` | 90% 以上 |
| `db_service/` | 80% 以上 |
| `ai_service/` | 70% 以上 |

## 6. テスト結果の分析

**サブエージェント `test-analyzer` を起動** し、以下を分析：

- 失敗テストの根本原因
- カバレッジ未達のモジュール
- 不足しているテストケース（境界値、異常系）

## 7. テストの追加・修正

分析結果に基づき、不足しているテストを追加する：

1. テストファイルを `tests/unit/` または `tests/integration/` に作成
2. テスト命名: `test_[対象]_[条件/期待結果]`
3. フィクスチャが必要な場合は `tests/conftest.py` に追加
4. 再度テストを実行して全件通過を確認

## 8. 結果の記録

テスト実行結果を `.steering/[今回]/tasklist.md` に記録する。
