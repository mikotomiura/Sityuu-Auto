---
name: python-standards
description: Python コーディング規約と型定義ルール。命名規則、型ヒント、docstring、import順序、エラーハンドリングを定義する。Pythonコードを新規作成・修正する際に必ず参照すべき。
allowed-tools: Read, Write, Grep, Glob
---

# Python 開発規約

## 型定義のルール

### 新しい型を定義する前に

1. `src/fortune_engine/models.py` に既存の型がないか確認する
2. `src/db_service/models.py` に既存の型がないか確認する
3. `docs/glossary.md` で用語と英語表記を確認する
4. 新規の型は必ず Pydantic の `BaseModel` を継承して定義する

### 型の命名規則

- クラス名: `PascalCase`（`NatalChart`, `ClientInputData`）
- Enum: `PascalCase`（メンバーは `UPPER_SNAKE_CASE`）
- TypeAlias: `PascalCase`（`StemType = Literal["甲", "乙", ...]`）
- ジェネリクス: `T`, `K`, `V` の慣例に従う

### 型ヒントの必須ルール

- すべての関数の引数と戻り値に型ヒントを付与する
- `Any` 型の使用は極力避ける。使用する場合はコメントで理由を明記する
- `Optional[X]` の代わりに `X | None` を使用する（Python 3.10+ 構文）
- コレクション型はビルトイン型を使用する（`list[str]`, `dict[str, int]`）

### 非同期関数の型定義

本プロジェクトでは Streamlit の制約上、基本的に同期関数を使用する。ただし AI連携層で非同期が必要な場合は以下に従う：

- `async def` 関数の戻り値は `Coroutine` ではなく実際の戻り値型を記述する
- 非同期関数名には `async_` プレフィックスを付けない（型ヒントで明確）

## docstring のルール

- Google スタイルを使用する
- モジュール、クラス、public 関数に必須
- private 関数（`_` 始まり）は簡潔な1行 docstring で可
- 日本語で記述する

## import のルール

順序: 標準ライブラリ → サードパーティ → ローカルモジュール（各グループ間に空行）

`from ... import ...` を優先し、名前空間の衝突がある場合のみ `import ...` を使用する。

## エラーハンドリングのルール

- `src/utils/exceptions.py` で定義されたカスタム例外を使用する
- `Exception` を直接 `raise` しない
- `except Exception:` で広範囲に捕捉しない
- 例外メッセージに個人情報を含めない

## ログ出力のルール

- `logging` モジュールを使用する（`print` 禁止）
- 個人情報（名前、生年月日、悩みテキスト）をログに含めない
- ログレベルを適切に使い分ける：
  - `DEBUG`: 開発時のデバッグ情報
  - `INFO`: 正常な処理の記録（処理開始・完了）
  - `WARNING`: 注意すべき状況（リトライ発生等）
  - `ERROR`: エラー発生
  - `CRITICAL`: アプリ継続不能なエラー

## 詳細情報

- 実装例とベストプラクティスは `examples.md` を参照
