"""バリデーション関数のユニットテスト。"""

from datetime import date, timedelta

import pytest

from utils.validators import (
    validate_api_key,
    validate_birth_date,
    validate_client_name,
    validate_concern,
)


class TestValidateClientName:
    """validate_client_name のテスト。"""

    def test_valid_name(self) -> None:
        """有効な名前で None が返ること。"""
        assert validate_client_name("山田太郎") is None

    def test_empty_name(self) -> None:
        """空文字でエラーメッセージが返ること。"""
        result = validate_client_name("")
        assert result is not None
        assert "入力" in result

    def test_whitespace_only_name(self) -> None:
        """空白のみの名前でエラーメッセージが返ること。"""
        result = validate_client_name("   ")
        assert result is not None

    def test_max_length_name(self) -> None:
        """50文字ちょうどの名前で None が返ること。"""
        assert validate_client_name("あ" * 50) is None

    def test_over_max_length_name(self) -> None:
        """51文字の名前でエラーメッセージが返ること。"""
        result = validate_client_name("あ" * 51)
        assert result is not None
        assert "50" in result

    def test_single_char_name(self) -> None:
        """1文字の名前で None が返ること（最小値境界）。"""
        assert validate_client_name("A") is None


class TestValidateBirthDate:
    """validate_birth_date のテスト。"""

    def test_valid_date(self) -> None:
        """有効な日付で None が返ること。"""
        assert validate_birth_date(date(1990, 5, 15)) is None

    def test_today(self) -> None:
        """今日の日付で None が返ること。"""
        assert validate_birth_date(date.today()) is None

    def test_future_date(self) -> None:
        """未来の日付でエラーメッセージが返ること。"""
        future = date.today() + timedelta(days=1)
        result = validate_birth_date(future)
        assert result is not None
        assert "未来" in result

    def test_too_old_date(self) -> None:
        """1900年以前の日付でエラーメッセージが返ること。"""
        result = validate_birth_date(date(1899, 12, 31))
        assert result is not None
        assert "1900" in result

    def test_boundary_min_date(self) -> None:
        """1900-01-01（最小境界）で None が返ること。"""
        assert validate_birth_date(date(1900, 1, 1)) is None


class TestValidateConcern:
    """validate_concern のテスト。"""

    def test_valid_concern(self) -> None:
        """10文字以上の有効な悩みで None が返ること。"""
        assert validate_concern("これは10文字以上の悩みテキストです。") is None

    def test_too_short_concern(self) -> None:
        """10文字未満の悩みでエラーメッセージが返ること。"""
        result = validate_concern("短い悩み")
        assert result is not None
        assert "10" in result

    def test_exact_min_length_concern(self) -> None:
        """ちょうど10文字の悩みで None が返ること。"""
        assert validate_concern("1234567890") is None

    def test_too_long_concern(self) -> None:
        """2001文字の悩みでエラーメッセージが返ること。"""
        result = validate_concern("あ" * 2001)
        assert result is not None
        assert "2000" in result

    def test_whitespace_only_concern(self) -> None:
        """空白のみの悩みでエラーメッセージが返ること。"""
        result = validate_concern("          ")
        assert result is not None

    def test_max_length_concern(self) -> None:
        """ちょうど2000文字の悩みで None が返ること。"""
        assert validate_concern("あ" * 2000) is None


class TestValidateApiKey:
    """validate_api_key のテスト。"""

    def test_valid_openai_key(self) -> None:
        """有効な OpenAI キーで None が返ること。"""
        assert validate_api_key("sk-test1234567890abcdef", "openai") is None

    def test_valid_anthropic_key(self) -> None:
        """有効な Anthropic キーで None が返ること。"""
        assert validate_api_key("sk-ant-test1234567890", "anthropic") is None

    def test_valid_gemini_key(self) -> None:
        """Gemini キーはプレフィックスチェックなしで None が返ること。"""
        assert validate_api_key("AIzaSyTest1234567890", "gemini") is None

    def test_none_key(self) -> None:
        """None のキーでエラーメッセージが返ること。"""
        result = validate_api_key(None, "openai")
        assert result is not None
        assert "設定されていません" in result

    def test_empty_key(self) -> None:
        """空文字のキーでエラーメッセージが返ること。"""
        result = validate_api_key("", "openai")
        assert result is not None

    def test_wrong_prefix_openai(self) -> None:
        """OpenAI キーのプレフィックスが不正な場合エラーが返ること。"""
        result = validate_api_key("wrong-prefix-key", "openai")
        assert result is not None
        assert "形式" in result

    def test_wrong_prefix_anthropic(self) -> None:
        """Anthropic キーのプレフィックスが不正な場合エラーが返ること。"""
        result = validate_api_key("sk-wrong-key", "anthropic")
        assert result is not None
        assert "形式" in result

    @pytest.mark.parametrize("provider", ["gemini", "unknown_provider"])
    def test_no_prefix_check_for_other_providers(self, provider: str) -> None:
        """Gemini等のプロバイダーはプレフィックスチェックしないこと。"""
        assert validate_api_key("any-key-value", provider) is None
