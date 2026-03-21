"""LLMクライアントのリトライロジックのユニットテスト。"""

from unittest.mock import MagicMock, patch

import pytest

from ai_service.client import AnthropicClient, OpenAIClient
from utils.exceptions import AIServiceError


class TestOpenAIClientRetry:
    """OpenAIClient のリトライロジックのテスト。"""

    @patch("ai_service.client.time.sleep")
    @patch("ai_service.client.openai")
    def test_retries_on_rate_limit_error(
        self, mock_openai: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """RateLimitError 時にリトライされること。"""
        RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = RateLimitError
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_message = MagicMock()
        mock_message.content = "成功レスポンス"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            RateLimitError(),
            mock_response,
        ]
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(api_key="sk-test", model="gpt-4o")
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "成功レスポンス"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once()

    @patch("ai_service.client.time.sleep")
    @patch("ai_service.client.openai")
    def test_retries_on_timeout_error(self, mock_openai: MagicMock, mock_sleep: MagicMock) -> None:
        """APITimeoutError 時にリトライされること。"""
        APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.APITimeoutError = APITimeoutError
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_message = MagicMock()
        mock_message.content = "成功"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            APITimeoutError(),
            mock_response,
        ]
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(api_key="sk-test", model="gpt-4o")
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "成功"
        assert mock_client.chat.completions.create.call_count == 2

    @patch("ai_service.client.time.sleep")
    @patch("ai_service.client.openai")
    def test_raises_after_max_retries(self, mock_openai: MagicMock, mock_sleep: MagicMock) -> None:
        """最大リトライ回数を超えた場合に AIServiceError が発生すること。"""
        RateLimitError = type("RateLimitError", (Exception,), {})
        mock_openai.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_openai.RateLimitError = RateLimitError
        mock_openai.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_openai.APIError = type("APIError", (Exception,), {})

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = RateLimitError()
        mock_openai.OpenAI.return_value = mock_client

        client = OpenAIClient(api_key="sk-test", model="gpt-4o")
        with pytest.raises(AIServiceError, match="リトライ後も失敗"):
            client.generate(system_prompt="system", user_prompt="user")


class TestAnthropicClientRetry:
    """AnthropicClient のリトライロジックのテスト。"""

    @patch("ai_service.client.time.sleep")
    @patch("ai_service.client.anthropic")
    def test_retries_on_rate_limit_error(
        self, mock_anthropic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """RateLimitError 時にリトライされること。"""
        RateLimitError = type("RateLimitError", (Exception,), {})
        mock_anthropic.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_anthropic.RateLimitError = RateLimitError
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_anthropic.APIError = type("APIError", (Exception,), {})

        mock_content_block = MagicMock()
        mock_content_block.text = "成功レスポンス"
        mock_response = MagicMock()
        mock_response.content = [mock_content_block]

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = [
            RateLimitError(),
            mock_response,
        ]
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient(api_key="sk-ant-test", model="claude-3-5-sonnet-20241022")
        result = client.generate(system_prompt="system", user_prompt="user")

        assert result == "成功レスポンス"
        assert mock_client.messages.create.call_count == 2
        mock_sleep.assert_called_once()

    @patch("ai_service.client.time.sleep")
    @patch("ai_service.client.anthropic")
    def test_raises_after_max_retries(
        self, mock_anthropic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """最大リトライ回数を超えた場合に AIServiceError が発生すること。"""
        RateLimitError = type("RateLimitError", (Exception,), {})
        mock_anthropic.AuthenticationError = type("AuthenticationError", (Exception,), {})
        mock_anthropic.RateLimitError = RateLimitError
        mock_anthropic.APITimeoutError = type("APITimeoutError", (Exception,), {})
        mock_anthropic.APIError = type("APIError", (Exception,), {})

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = RateLimitError()
        mock_anthropic.Anthropic.return_value = mock_client

        client = AnthropicClient(api_key="sk-ant-test", model="claude-3-5-sonnet-20241022")
        with pytest.raises(AIServiceError, match="リトライ後も失敗"):
            client.generate(system_prompt="system", user_prompt="user")
