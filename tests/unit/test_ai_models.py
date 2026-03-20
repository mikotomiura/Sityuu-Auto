"""AI応答データモデルのユニットテスト。"""

from datetime import datetime

from ai_service.models import AIListeningHintResponse, AIReadingResponse, AIResponse


class TestAIReadingResponse:
    """AIReadingResponse のテスト。"""

    def test_create_with_required_fields(self) -> None:
        """必須フィールドのみで生成できること。"""
        response = AIReadingResponse(
            reading_text="鑑定テキスト本文",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        assert response.reading_text == "鑑定テキスト本文"
        assert response.provider == "gemini"
        assert response.model == "gemini-2.5-flash"
        assert isinstance(response.generated_at, datetime)

    def test_generated_at_default(self) -> None:
        """generated_at がデフォルトで現在時刻に設定されること。"""
        before = datetime.now()
        response = AIReadingResponse(
            reading_text="テスト",
            provider="openai",
            model="gpt-4o",
        )
        after = datetime.now()
        assert before <= response.generated_at <= after

    def test_serialization_roundtrip(self) -> None:
        """JSON シリアライズ・デシリアライズが正常に動作すること。"""
        original = AIReadingResponse(
            reading_text="鑑定テキスト",
            provider="anthropic",
            model="claude-sonnet-4-20250514",
        )
        json_str = original.model_dump_json()
        restored = AIReadingResponse.model_validate_json(json_str)
        assert restored.reading_text == original.reading_text
        assert restored.provider == original.provider
        assert restored.model == original.model


class TestAIListeningHintResponse:
    """AIListeningHintResponse のテスト。"""

    def test_create_with_required_fields(self) -> None:
        """必須フィールドのみで生成できること。"""
        response = AIListeningHintResponse(
            listening_hint_text="傾聴ヒント本文",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        assert response.listening_hint_text == "傾聴ヒント本文"
        assert response.provider == "gemini"


class TestAIResponse:
    """AIResponse のテスト。"""

    def test_create_with_reading_only(self) -> None:
        """鑑定テキストのみで生成できること（傾聴ヒントなし）。"""
        reading = AIReadingResponse(
            reading_text="鑑定結果",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        response = AIResponse(reading=reading)
        assert response.reading_text == "鑑定結果"
        assert response.listening_hint_text is None

    def test_create_with_both_responses(self) -> None:
        """鑑定テキストと傾聴ヒント両方で生成できること。"""
        reading = AIReadingResponse(
            reading_text="鑑定結果",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        hint = AIListeningHintResponse(
            listening_hint_text="傾聴ヒント",
            provider="gemini",
            model="gemini-2.5-flash",
        )
        response = AIResponse(reading=reading, listening_hint=hint)
        assert response.reading_text == "鑑定結果"
        assert response.listening_hint_text == "傾聴ヒント"

    def test_reading_text_property(self) -> None:
        """reading_text プロパティが正しく動作すること。"""
        reading = AIReadingResponse(
            reading_text="テスト鑑定",
            provider="openai",
            model="gpt-4o",
        )
        response = AIResponse(reading=reading)
        assert response.reading_text == reading.reading_text

    def test_listening_hint_text_property_when_none(self) -> None:
        """listening_hint が None の場合、listening_hint_text が None を返すこと。"""
        reading = AIReadingResponse(
            reading_text="テスト",
            provider="openai",
            model="gpt-4o",
        )
        response = AIResponse(reading=reading, listening_hint=None)
        assert response.listening_hint_text is None
