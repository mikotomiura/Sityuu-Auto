# 設計メモ: calculator.py 実装
- 日付: 2026-03-19

## 実装アプローチ
docs/fortune-engine-detail.md セクション5.2の擬似コードに完全準拠して実装。
lunar_python の Solar → Lunar → EightChar のフローで四柱データを取得。

## 変更内容
1. `calculate_natal_chart()`: Solar生成 → Lunar変換 → EightChar取得 → 各柱構築 → NatalChart返却
2. `_build_pillar()`: 天干・地支・干支からPillarオブジェクト構築。納音は LunarUtil.NAYIN から取得
3. `_count_five_elements()`: Counter で天干の五行をカウント、全五行を0含めて返却
4. pyproject.toml: lunar_python の mypy override（follow_imports = "skip"）を追加

## 代替案
- 納音取得: EightChar のメソッドから直接取得する案 → LunarUtil.NAYIN dict の方がシンプルで確実
- 五行カウント: 地支も含める案 → 設計書が「天干の五行」と明記しているため天干のみ

## 影響範囲
- fortune_engine.__init__.py（既に calculator を import する設計）
- fortune_engine.sanmei（NatalChart を入力として使用）
