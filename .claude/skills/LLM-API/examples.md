# API連携 — 実装例とベストプラクティス

## LLMクライアントの実装例

```python
"""LLM API クライアント。Strategy パターンで OpenAI / Anthropic を切替。"""

import logging
import time as time_module
from abc import ABC, abstractmethod

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

    def __init__(self, api_key: str, model: str, timeout: int = 30) -> None:
        if not api_key:
            raise AIServiceConfigError("OpenAI API キーが設定されていません")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """OpenAI API でテキスト生成。"""
        import openai

        client = openai.OpenAI(api_key=self._api_key)

        try:
            response = client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=2000,
                temperature=0.7,
                timeout=self._timeout,
            )
            content = response.choices[0].message.content
            if not content:
                raise AIServiceError("AIからの応答が空でした")
            return content

        except openai.AuthenticationError as e:
            logger.error("OpenAI 認証エラー")
            raise AIServiceConfigError("APIキーが無効です。設定を確認してください。") from e
        except openai.RateLimitError as e:
            logger.warning("OpenAI レート制限")
            raise AIServiceError("API呼び出し制限に達しました。しばらくお待ちください。") from e
        except openai.APITimeoutError as e:
            logger.warning("OpenAI タイムアウト")
            raise AIServiceError("API応答がタイムアウトしました。") from e
        except openai.APIError as e:
            logger.error("OpenAI APIエラー: %s", type(e).__name__)
            raise AIServiceError(f"API呼び出しに失敗しました: {e}") from e


class AnthropicClient(LLMClient):
    """Anthropic API クライアント。"""

    def __init__(self, api_key: str, model: str, timeout: int = 30) -> None:
        if not api_key:
            raise AIServiceConfigError("Anthropic API キーが設定されていません")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Anthropic API でテキスト生成。"""
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)

        try:
            response = client.messages.create(
                model=self._model,
                max_tokens=2000,
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
        except anthropic.RateLimitError as e:
            logger.warning("Anthropic レート制限")
            raise AIServiceError("API呼び出し制限に達しました。しばらくお待ちください。") from e
        except anthropic.APITimeoutError as e:
            logger.warning("Anthropic タイムアウト")
            raise AIServiceError("API応答がタイムアウトしました。") from e
        except anthropic.APIError as e:
            logger.error("Anthropic APIエラー: %s", type(e).__name__)
            raise AIServiceError(f"API呼び出しに失敗しました: {e}") from e


def create_client(
    provider: str,
    api_key: str,
    model: str,
    timeout: int = 30,
) -> LLMClient:
    """プロバイダーに応じた LLMClient を生成する。

    Args:
        provider: "openai" または "anthropic"。
        api_key: APIキー。
        model: 使用するモデル名。
        timeout: タイムアウト秒数。

    Returns:
        LLMClient の具象インスタンス。

    Raises:
        ValueError: 不明なプロバイダーが指定された場合。
    """
    if provider == "openai":
        return OpenAIClient(api_key=api_key, model=model, timeout=timeout)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=model, timeout=timeout)
    raise ValueError(f"不明なAPIプロバイダー: {provider}")
```

---

## リトライ機能の実装例

```python
"""リトライ付きAPI呼び出し。"""

import logging
import time as time_module

from utils.exceptions import AIServiceError

logger = logging.getLogger(__name__)

MAX_RETRIES = 1
RETRY_DELAY_SECONDS = 2


def generate_with_retry(
    client: "LLMClient",
    system_prompt: str,
    user_prompt: str,
) -> str:
    """リトライ付きでテキスト生成を行う。

    1回失敗した場合、2秒待ってリトライする。
    2回目も失敗した場合は例外を送出する。

    Args:
        client: LLM API クライアント。
        system_prompt: システムプロンプト。
        user_prompt: ユーザープロンプト。

    Returns:
        生成されたテキスト。

    Raises:
        AIServiceError: リトライ後も失敗した場合。
    """
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            return client.generate(system_prompt, user_prompt)
        except AIServiceError as e:
            last_error = e
            if attempt < MAX_RETRIES:
                logger.warning(
                    "API呼び出し失敗 (attempt %d/%d): %s — %d秒後にリトライ",
                    attempt + 1,
                    MAX_RETRIES + 1,
                    str(e),
                    RETRY_DELAY_SECONDS,
                )
                time_module.sleep(RETRY_DELAY_SECONDS)
            else:
                logger.error("API呼び出し最終失敗: %s", str(e))

    raise AIServiceError(f"API呼び出しに失敗しました（{MAX_RETRIES + 1}回試行）") from last_error
```

---

## プロンプトテンプレートの例

### 鑑定テキスト生成用（reading_base.md）

```markdown
あなたは熟練のカウンセラーであり、東洋占術（四柱推命・算命学）に精通した鑑定師です。

以下の命式が示す相談者の本質（強み・弱み）を踏まえ、悩みに寄り添い、
相手の自己肯定感が高まるアドバイスのベースを作成してください。

## 命式データ
${natal_chart_text}

## 相談者の悩み
${concern_text}

## 出力フォーマット
以下の4つのセクションに分けて回答してください：

1. **命式から読み取れる相談者の本質**（3〜5行）
2. **悩みに対する占術的観点からの解釈**（3〜5行）
3. **具体的なアドバイス案**（3〜5項目、箇条書き）
4. **傾聴時の声掛けポイント**（3〜5項目、箇条書き）

## 注意事項
- 断定的な表現は避け、「〜の傾向があります」「〜と読み取れます」のような柔らかい表現を使用してください
- 相談者を否定するような内容は含めないでください
- 具体的で実行可能なアドバイスを心がけてください
```
