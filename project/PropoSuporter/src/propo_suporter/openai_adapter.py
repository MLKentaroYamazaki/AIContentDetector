"""OpenAI互換APIのAnthropicクライアント互換アダプター

Groq・Ollama等、OpenAI互換エンドポイントをAnthropicクライアントと
同じインターフェースで使えるようにするアダプターです。
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class _ContentBlock:
    text: str


@dataclass
class _AdaptedResponse:
    content: list[_ContentBlock]


class _MessagesAPI:
    def __init__(self, client: Any):
        self._client = client

    def create(self, model: str, max_tokens: int, messages: list[dict]) -> _AdaptedResponse:
        response = self._client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
        )
        text = response.choices[0].message.content
        return _AdaptedResponse(content=[_ContentBlock(text=text)])


class OpenAICompatibleAdapter:
    """OpenAI互換APIをAnthropicクライアントと同じインターフェースで使うアダプター

    対応バックエンド:
    - Groq API  (base_url: https://api.groq.com/openai/v1)
    - Ollama    (base_url: http://localhost:11434/v1)
    """

    def __init__(self, client: Optional[Any] = None, base_url: str = "", api_key: str = ""):
        if client is not None:
            self._client = client
        else:
            from openai import OpenAI
            self._client = OpenAI(base_url=base_url, api_key=api_key)

        self.messages = _MessagesAPI(self._client)
