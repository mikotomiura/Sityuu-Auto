"""LLMクライアントのユニットテスト（モック使用）。"""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from ai_service.client import (
    AnthropicClient,
    GeminiClient,
    LLMClient,
    OpenAIClient,
    create_client,
)
from utils.exceptions import AIServiceConfigError, AIServiceError


class TestCreateClient:
    """create_client ファクトリ関数のテスト。"""

    def test_create_openai_client(self) -> None:
        """provider="openai" で OpenAIClient が生成されること。"""
        client = create_client(provider="openai", api_key="sk-test", model="gpt-4o")

        assert isinstance(client, OpenAIClient)
        assert isinstance(client, LLMClient)

    def test_create_anthropic_client(self) -> None:
        """provider="anthropic" で AnthropicClient が生成されること。"""
        client = create_client(
            provider="anthropic", api_key="sk-ant-test", model="claude-3-5-sonnet-20241022"
        )

        assert isinstance(client, AnthropicClient)
        assert isinstance(client, LLMClient)

    def test_unknown_provider_raises_config_error(self) -> None:
        """不明なプロバイダーで AIServiceConfigError が発生すること。"""
        with pytest.raises(AIServiceConfigError, match="不明なAPIプロバイダー"):
            create_client(provider="unknown", api_key="key", model="model")


class TestOpenAIClient:
    """OpenAIClient のテスト。"""

    def test_empty_api_key_raises_config_error(self) -> None:
        """空のAPIキーで AIServiceConfigError が発生すること。"""
        with pytest.raises(AIServiceConfigError):
            OpenAIClient(api_key="", model="gpt-4o")

    @patch("ai_service.client.openai")
    def test_generate_returns_response_text(self, mock_openai: MagicMock) -> None:
        """正常時にレスポンステキストが返ること。"""
        # except 節で使われる例外クラスを正しい型に差し替え
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_message = MagicMock()
        mock_message.content = "鑑定結果テキスト"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(api_key="sk-test", model="gpt-4o")
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "鑑定結果テキスト"
        mock_client.chat.completions.create.assert_called_once()

    @patch("ai_service.client.openai")
    def test_generate_empty_response_raises_error(self, mock_openai: MagicMock) -> None:
        """空レスポンスで AIServiceError が発生すること。"""
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_message = MagicMock()
        mock_message.content = ""
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(api_key="sk-test", model="gpt-4o")
        with pytest.raises(AIServiceError, match="応答が空"):
            client.generate(system_prompt="system", user_prompt="user")

    @patch("ai_service.client.openai")
    def test_authentication_error_raises_config_error(self, mock_openai: MagicMock) -> None:
        """認証エラーで AIServiceConfigError が発生すること。"""
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client
        mock_client.chat.completions.create.side_effect = mock_openai.AuthenticationError()

        client = OpenAIClient(api_key="sk-invalid", model="gpt-4o")
        with pytest.raises(AIServiceConfigError):
            client.generate(system_prompt="system", user_prompt="user")


class TestAnthropicClient:
    """AnthropicClient のテスト。"""

    def test_empty_api_key_raises_config_error(self) -> None:
        """空のAPIキーで AIServiceConfigError が発生すること。"""
        with pytest.raises(AIServiceConfigError):
            AnthropicClient(api_key="", model="claude-3-5-sonnet-20241022")

    @patch("ai_service.client.anthropic")
    def test_generate_returns_response_text(self, mock_anthropic: MagicMock) -> None:
        """正常時にレスポンステキストが返ること。"""
        mock_anthropic.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_anthropic.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_anthropic.APIError = type("APIError", (Exception,), {})

        mock_content_block = MagicMock()
        mock_content_block.text = "傾聴ヒントテキスト"
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient(api_key="sk-ant-test", model="claude-3-5-sonnet-20241022")
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "傾聴ヒントテキスト"
        mock_client.messages.create.assert_called_once()

    @patch("ai_service.client.anthropic")
    def test_generate_empty_response_raises_error(self, mock_anthropic: MagicMock) -> None:
        """空レスポンスで AIServiceError が発生すること。"""
        mock_anthropic.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_anthropic.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_anthropic.APIError = type("APIError", (Exception,), {})

        mock_content_block = MagicMock()
        mock_content_block.text = ""
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient(api_key="sk-ant-test", model="claude-3-5-sonnet-20241022")
        with pytest.raises(AIServiceError, match="応答が空"):
            client.generate(system_prompt="system", user_prompt="user")

    @patch("ai_service.client.anthropic")
    def test_authentication_error_raises_config_error(self, mock_anthropic: MagicMock) -> None:
        """認証エラーで AIServiceConfigError が発生すること。"""
        mock_anthropic.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_anthropic.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_anthropic.APIError = type("APIError", (Exception,), {})

        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = mock_anthropic.AuthenticationError()

        client = AnthropicClient(api_key="sk-ant-invalid", model="claude-3-5-sonnet-20241022")
        with pytest.raises(AIServiceConfigError):
            client.generate(system_prompt="system", user_prompt="user")


class TestGeminiClient:
    """GeminiClient のテスト。"""

    def test_empty_api_key_raises_config_error(self) -> None:
        """空のAPIキーで AIServiceConfigError が発生すること。"""
        with pytest.raises(AIServiceConfigError):
            GeminiClient(api_key="", models=["gemini-2.5-flash"])

    def test_empty_models_raises_config_error(self) -> None:
        """空のモデルリストで AIServiceConfigError が発生すること。"""
        with pytest.raises(AIServiceConfigError):
            GeminiClient(api_key="test-key", models=[])

    @patch("ai_service.client.genai")
    def test_transport_error_triggers_fallback(self, mock_genai: MagicMock) -> None:
        """SSL/ネットワークエラーで次のモデルへフォールバックすること。"""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client

        # 1回目: SSL エラー、2回目: 成功
        mock_response = MagicMock()
        mock_response.text = "鑑定結果テキスト"
        mock_client.models.generate_content.side_effect = [
            httpx.ConnectError("[SSL: UNEXPECTED_EOF_WHILE_READING]"),
            mock_response,
        ]

        client = GeminiClient(
            api_key="test-key",
            models=["gemini-2.5-flash", "gemini-2.5-flash-lite"],
        )
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "鑑定結果テキスト"
        assert mock_client.models.generate_content.call_count == 2

    @patch("ai_service.client.genai")
    def test_all_models_transport_error_raises_ai_service_error(
        self, mock_genai: MagicMock
    ) -> None:
        """全モデルでネットワークエラーの場合 AIServiceError が発生すること。"""
        mock_client = MagicMock()
        mock_genai.Client.return_value = mock_client
        mock_client.models.generate_content.side_effect = httpx.ConnectError(
            "[SSL: UNEXPECTED_EOF_WHILE_READING]"
        )

        client = GeminiClient(
            api_key="test-key",
            models=["model-a", "model-b"],
        )
        with pytest.raises(AIServiceError, match="すべてのGeminiモデルが利用できませんでした"):
            client.generate(system_prompt="system", user_prompt="user")
