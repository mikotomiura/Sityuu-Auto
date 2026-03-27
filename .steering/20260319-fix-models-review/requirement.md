# 要件定義: models.py コードレビュー指摘修正
- 日付: 2026-03-19
- 関連Issue/PR: なし（内部コードレビュー）

## 目的
code-reviewer サブエージェントによるレビュー指摘を反映し、models.py と設計書の整合性を確保する。

## 症状
1. TwelveBranch.INOSHISHI — 設計書では `I` だがコードは `INOSHISHI`（ruff E741回避）。設計書未更新。
2. StrEnum — 設計書では `str, Enum` だがコードは `StrEnum`（ruff UP042対応）。設計書未更新。
3. TENKO / TENKO2 — 数字サフィックスで意味不明瞭。天胡星(TENKO)と天庫星(TENKO2)の区別が困難。
4. モジュール docstring — 「セクション3」というハードコード参照が将来腐る。

## 受け入れ条件
- [ ] 設計書(fortune-engine-detail.md)のセクション3が最新のコードと一致
- [ ] TENKO / TENKO2 が意味的に明確な名前に改名
- [ ] ruff check / mypy がエラーなし
- [ ] モジュール docstring が安定した参照を使用

## 対象スコープ
- src/fortune_engine/models.py
- docs/fortune-engine-detail.md（セクション3）

## スコープ外
- constants.py（次タスクで実装予定。models.pyの変更に追従する）
- calculator.py / sanmei.py（未実装）
