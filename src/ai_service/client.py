"""LLM API クライアント。Strategy パターンで OpenAI / Anthropic / Gemini を切替。"""

import logging
import time
from abc import ABC, abstractmethod

import anthropic
import httpx
import openai
from google import genai
from google.genai import types as genai_types
from google.genai.errors import APIError as GeminiAPIError
from google.genai.errors import ClientError as GeminiClientError

from config import (
    API_MAX_RETRIES,
    API_MAX_TOKENS,
    API_RETRY_BASE_WAIT,
    API_TEMPERATURE,
    API_TIMEOUT_SECONDS,
)
from utils.exceptions import AIServiceConfigError, AIServiceError

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """LLM API クライアントの抽象基底クラス。"""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """テキストを生成する。

        Args:
            system_prompt: システムプロンプト（役割定義・指示）。
            user_prompt: ユーザープロンプト（入力データ）。

        Returns:
            生成されたテキスト。

        Raises:
            AIServiceError: API呼び出しに失敗した場合。
            AIServiceConfigError: 設定が不正な場合。
        """
        ...


class OpenAIClient(LLMClient):
    """OpenAI API クライアント。"""

    def __init__(self, api_key: str, model: str, timeout: int = API_TIMEOUT_SECONDS) -> None:
        if not api_key:
            raise AIServiceConfigError("OpenAI API キーが設定されていません")
        self._client = openai.OpenAI(api_key=api_key)
        self._model = model
        self._timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """OpenAI API でテキスト生成（リトライ付き）。"""
        client = self._client
        last_error: Exception | None = None

        for attempt in range(API_MAX_RETRIES + 1):
            try:
                response = client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=API_MAX_TOKENS,
                    temperature=API_TEMPERATURE,
                    timeout=self._timeout,
                )
                content = response.choices[0].message.content
                if not content:
                    raise AIServiceError("AIからの応答が空でした")
                return content

            except openai.AuthenticationError as e:
                logger.error("OpenAI 認証エラー")
                raise AIServiceConfigError("APIキーが無効です。設定を確認してください。") from e
            except (openai.RateLimitError, openai.APITimeoutError) as e:
                last_error = e
                if attempt < API_MAX_RETRIES:
                    wait = API_RETRY_BASE_WAIT * (2**attempt)
                    logger.warning(
                        "OpenAI 一時エラー (%s), %s秒後にリトライ (%d/%d)",
                        type(e).__name__,
                        wait,
                        attempt + 1,
                        API_MAX_RETRIES,
                    )
                    time.sleep(wait)
                    continue
            except openai.APIError as e:
                logger.error("OpenAI APIエラー: %s", type(e).__name__)
                raise AIServiceError(
                    "API呼び出しに失敗しました。しばらくしてから再試行してください。"
                ) from e

        raise AIServiceError(
            "API呼び出しがリトライ後も失敗しました。しばらくしてから再試行してください。"
        ) from last_error


class AnthropicClient(LLMClient):
    """Anthropic API クライアント。"""

    def __init__(self, api_key: str, model: str, timeout: int = API_TIMEOUT_SECONDS) -> None:
        if not api_key:
            raise AIServiceConfigError("Anthropic API キーが設定されていません")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Anthropic API でテキスト生成（リトライ付き）。"""
        client = self._client
        last_error: Exception | None = None

        for attempt in range(API_MAX_RETRIES + 1):
            try:
                response = client.messages.create(
                    model=self._model,
                    max_tokens=API_MAX_TOKENS,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    timeout=self._timeout,
                )
                content = response.content[0].text
                if not content:
                    raise AIServiceError("AIからの応答が空でした")
                return content

            except anthropic.AuthenticationError as e:
                logger.error("Anthropic 認証エラー")
                raise AIServiceConfigError("APIキーが無効です。設定を確認してください。") from e
            except (anthropic.RateLimitError, anthropic.APITimeoutError) as e:
                last_error = e
                if attempt < API_MAX_RETRIES:
                    wait = API_RETRY_BASE_WAIT * (2**attempt)
                    logger.warning(
                        "Anthropic 一時エラー (%s), %s秒後にリトライ (%d/%d)",
                        type(e).__name__,
                        wait,
                        attempt + 1,
                        API_MAX_RETRIES,
                    )
                    time.sleep(wait)
                    continue
            except anthropic.APIError as e:
                logger.error("Anthropic APIエラー: %s", type(e).__name__)
                raise AIServiceError(
                    "API呼び出しに失敗しました。しばらくしてから再試行してください。"
                ) from e

        raise AIServiceError(
            "API呼び出しがリトライ後も失敗しました。しばらくしてから再試行してください。"
        ) from last_error


class GeminiClient(LLMClient):
    """Google Gemini API クライアント。

    複数モデルのフォールバックに対応する。モデルが利用不可（404）または
    レート制限（429）の場合、次の候補モデルへ自動的に切り替えて再試行する。
    """

    def __init__(
        self,
        api_key: str,
        models: list[str],
        timeout: int = API_TIMEOUT_SECONDS,
    ) -> None:
        """GeminiClient を初期化する。

        Args:
            api_key: Gemini API キー。
            models: 試行するモデル名のリスト（先頭から順に試行）。
            timeout: タイムアウト秒数。
        """
        if not api_key:
            raise AIServiceConfigError("Gemini API キーが設定されていません")
        if not models:
            raise AIServiceConfigError("Gemini のモデルが1つも指定されていません")
        self._client = genai.Client(
            api_key=api_key,
            http_options=genai_types.HttpOptions(timeout=timeout * 1000),
        )
        self._models = models
        self._timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Gemini API でテキスト生成（モデルフォールバック付き）。

        候補モデルを先頭から順に試行し、利用不可やレート制限の場合は
        次のモデルへフォールバックする。認証エラーはフォールバックせず即座に送出する。
        """
        client = self._client

        last_error: Exception | None = None

        for model in self._models:
            try:
                logger.info("Gemini モデル試行: %s", model)
                response = client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=genai_types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=API_TEMPERATURE,
                        max_output_tokens=API_MAX_TOKENS,
                    ),
                )
                content = response.text
                if not content:
                    raise AIServiceError("AIからの応答が空でした")
                logger.info("Gemini モデル成功: %s", model)
                return content

            except GeminiClientError as e:
                last_error = e
                if _is_auth_error(e):
                    logger.error("Gemini 認証エラー")
                    raise AIServiceConfigError("APIキーが無効です。設定を確認してください。") from e
                if _is_retryable_error(e):
                    logger.warning(
                        "Gemini モデル %s 利用不可 (code=%s), 次のモデルへフォールバック",
                        model,
                        e.code,
                    )
                    continue
                logger.error("Gemini APIエラー: code=%s", e.code)
                raise AIServiceError(
                    "Gemini API呼び出しに失敗しました。しばらくしてから再試行してください。"
                ) from e

            except GeminiAPIError as e:
                last_error = e
                logger.error("Gemini サーバーエラー: code=%s", e.code)
                raise AIServiceError(
                    "Gemini APIサーバーでエラーが発生しました。しばらくしてから再試行してください。"
                ) from e

            except httpx.TransportError as e:
                last_error = e
                logger.warning(
                    "Gemini モデル %s ネットワークエラー (%s), 次のモデルへフォールバック",
                    model,
                    type(e).__name__,
                )
                continue

        # すべてのモデルが失敗した場合
        tried = ", ".join(self._models)
        logger.error("Gemini 全モデル失敗: %s", tried)
        raise AIServiceError(
            f"すべてのGeminiモデルが利用できませんでした（{tried}）。"
            "しばらくしてから再試行してください。"
        ) from last_error


def _is_auth_error(error: GeminiClientError) -> bool:
    """認証エラー（401）かどうかを判定する。"""
    return error.code == 401


def _is_retryable_error(error: GeminiClientError) -> bool:
    """フォールバック対象のエラー（404/429）かどうかを判定する。"""
    return error.code in (404, 429)


def create_client(
    provider: str,
    api_key: str,
    model: str,
    timeout: int = API_TIMEOUT_SECONDS,
    fallback_models: list[str] | None = None,
) -> LLMClient:
    """プロバイダーに応じた LLMClient を生成する。

    Args:
        provider: "openai", "anthropic", または "gemini"。
        api_key: APIキー。
        model: 使用するモデル名。
        timeout: タイムアウト秒数。
        fallback_models: Gemini 用のフォールバックモデルリスト。
            指定しない場合は model のみを使用する。

    Returns:
        LLMClient の具象インスタンス。

    Raises:
        AIServiceConfigError: 不明なプロバイダーが指定された場合。
    """
    if provider == "openai":
        return OpenAIClient(api_key=api_key, model=model, timeout=timeout)
    if provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=model, timeout=timeout)
    if provider == "gemini":
        models = fallback_models if fallback_models else [model]
        return GeminiClient(api_key=api_key, models=models, timeout=timeout)
    raise AIServiceConfigError(f"不明なAPIプロバイダー: {provider}")
