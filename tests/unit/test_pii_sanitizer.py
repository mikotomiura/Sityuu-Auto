"""PII匿名化モジュールのユニットテスト。"""

from ai_service.pii_sanitizer import (
    sanitize_for_prompt,
    sanitize_name,
    sanitize_name_kana,
)
from ai_service.prompt_builder import build_reading_prompt


class TestSanitizeName:
    """sanitize_name のテスト。"""

    def test_replaces_name_with_placeholder(self) -> None:
        """名前がプレースホルダに置換されること。"""
        result = sanitize_name("田中太郎")

        assert result == "相談者様"
        assert "田中" not in result

    def test_empty_string_returns_empty(self) -> None:
        """空文字が渡された場合はそのまま返すこと。"""
        result = sanitize_name("")

        assert result == ""

    def test_single_character_name(self) -> None:
        """1文字の名前でも匿名化されること。"""
        result = sanitize_name("花")

        assert result == "相談者様"


class TestSanitizeNameKana:
    """sanitize_name_kana のテスト。"""

    def test_replaces_kana_with_empty(self) -> None:
        """フリガナが空文字に置換されること。"""
        result = sanitize_name_kana("タナカタロウ")

        assert result == ""

    def test_empty_string_returns_empty(self) -> None:
        """空文字が渡された場合はそのまま返すこと。"""
        result = sanitize_name_kana("")

        assert result == ""


class TestSanitizeForPrompt:
    """sanitize_for_prompt のテスト。"""

    def test_anonymizes_both_name_and_kana(self) -> None:
        """名前とフリガナの両方が匿名化されること。"""
        name, kana = sanitize_for_prompt("田中太郎", "タナカタロウ")

        assert name == "相談者様"
        assert kana == ""

    def test_empty_inputs_preserved(self) -> None:
        """空文字の入力がそのまま保持されること。"""
        name, kana = sanitize_for_prompt("", "")

        assert name == ""
        assert kana == ""

    def test_only_name_provided(self) -> None:
        """名前のみ提供された場合の動作。"""
        name, kana = sanitize_for_prompt("佐藤花子", "")

        assert name == "相談者様"
        assert kana == ""

    def test_only_kana_provided(self) -> None:
        """フリガナのみ提供された場合の動作。"""
        name, kana = sanitize_for_prompt("", "サトウハナコ")

        assert name == ""
        assert kana == ""


class TestBuildReadingPromptAnonymization:
    """build_reading_prompt の匿名化パラメータのテスト。"""

    def test_anonymize_true_removes_name_from_prompt(self) -> None:
        """anonymize=True で名前がプロンプトから除外されること。"""
        _system, user = build_reading_prompt(
            natal_chart_text="テスト命式",
            concern="テスト悩み",
            name="田中太郎",
            name_kana="タナカタロウ",
            anonymize=True,
        )

        assert "田中太郎" not in user
        assert "タナカタロウ" not in user
        assert "相談者様" in user

    def test_anonymize_false_keeps_name_in_prompt(self) -> None:
        """anonymize=False で名前がプロンプトに含まれること。"""
        _system, user = build_reading_prompt(
            natal_chart_text="テスト命式",
            concern="テスト悩み",
            name="田中太郎",
            name_kana="タナカタロウ",
            anonymize=False,
        )

        assert "田中太郎" in user
        assert "タナカタロウ" in user

    def test_anonymize_default_is_true(self) -> None:
        """anonymize のデフォルト値が True であること（セーフデフォルト）。"""
        _system, user = build_reading_prompt(
            natal_chart_text="テスト命式",
            concern="テスト悩み",
            name="田中太郎",
            name_kana="タナカタロウ",
        )

        assert "田中太郎" not in user
        assert "相談者様" in user
