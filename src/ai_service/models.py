"""AI応答のデータモデル定義。

LLM API から返されるテキストを構造化し、型安全に扱うための
Pydantic モデルを提供する。
"""

from datetime import datetime

from pydantic import BaseModel, Field


class _BaseAIResponse(BaseModel):
    """AI応答の共通フィールドを持つ基底クラス。

    Attributes:
        provider: 使用した API プロバイダー名。
        model: 使用したモデル名。
        generated_at: 生成日時。
    """

    provider: str = Field(description="使用した API プロバイダー名")
    model: str = Field(description="使用したモデル名")
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="生成日時",
    )


class AIReadingResponse(_BaseAIResponse):
    """AI鑑定テキスト応答。

    LLM が生成した鑑定テキストと、生成時のメタ情報を保持する。

    Attributes:
        reading_text: AI が生成した鑑定テキスト本文。
    """

    reading_text: str = Field(description="AI が生成した鑑定テキスト本文")


class AIListeningHintResponse(_BaseAIResponse):
    """傾聴ヒント応答。

    LLM が生成した傾聴のヒントテキストと、生成時のメタ情報を保持する。

    Attributes:
        listening_hint_text: AI が生成した傾聴ヒントテキスト。
    """

    listening_hint_text: str = Field(description="AI が生成した傾聴ヒントテキスト")


class AIResponse(BaseModel):
    """AI応答の統合モデル。

    鑑定テキストと傾聴ヒントを統合して保持する。
    傾聴ヒントはオプショナル（生成失敗時は None）。

    Attributes:
        reading: 鑑定テキスト応答。
        listening_hint: 傾聴ヒント応答（生成失敗時は None）。
    """

    reading: AIReadingResponse = Field(description="鑑定テキスト応答")
    listening_hint: AIListeningHintResponse | None = Field(
        default=None,
        description="傾聴ヒント応答（生成失敗時は None）",
    )

    @property
    def reading_text(self) -> str:
        """鑑定テキスト本文を返す。"""
        return self.reading.reading_text

    @property
    def listening_hint_text(self) -> str | None:
        """傾聴ヒントテキストを返す。未生成の場合は None。"""
        if self.listening_hint is None:
            return None
        return self.listening_hint.listening_hint_text
