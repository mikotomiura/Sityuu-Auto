# 要件定義: implement-sanmei
- 日付: 2026-03-19
- 関連Issue/PR:

## 目的
算命学データ算出モジュール（sanmei.py）を実装する。命式（NatalChart）から十大主星・十二大従星・天中殺・エネルギーを算出し SanmeiData を返す。

## 受け入れ条件
- [ ] calculate_sanmei_data() が設計書5.3の処理フローに完全準拠
- [ ] 十大主星5箇所 + 伴星を正しく算出
- [ ] 十二大従星3箇所を正しく算出
- [ ] 天中殺グループを正しく判定
- [ ] エネルギー合計を正しく算出
- [ ] ruff check / mypy エラーなし

## 対象スコープ
- src/fortune_engine/sanmei.py（新規作成）

## スコープ外
- テストコード（別タスク）
- formatter.py
