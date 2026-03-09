"""与件整理機能"""
import json
import re
from dataclasses import dataclass
from typing import Optional
from anthropic import Anthropic


def _extract_json(text: str) -> dict:
    """LLMレスポンスからJSONオブジェクトを抽出する。

    LLMが前後に説明文やmarkdownコードブロックを付けた場合にも対応する。
    """
    # ```json ... ``` または ``` ... ``` ブロックを優先的に抽出
    code_block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block:
        return json.loads(code_block.group(1))

    # テキスト中の最初の { ... } を抽出
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        return json.loads(brace_match.group(0))

    raise ValueError(f"LLMレスポンスからJSONを抽出できませんでした。レスポンス: {text[:200]}")


@dataclass
class OrganizedRequirements:
    background: str
    issues: str
    requests: str


class RequirementOrganizer:
    """乱雑なヒアリングメモから「背景」「課題」「要望」を構造化する"""

    def __init__(self, client: Optional[Anthropic] = None):
        self._client = client or Anthropic()

    def organize(self, raw_notes: str) -> OrganizedRequirements:
        if not raw_notes.strip():
            raise ValueError("ヒアリングメモが空です")

        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "以下のヒアリングメモから「背景」「課題」「要望」を抽出・整理してください。\n"
                        "必ずJSON形式のみで回答し、他の文章は一切含めないでください。\n\n"
                        "出力形式:\n"
                        '{"background": "...", "issues": "...", "requests": "..."}\n\n'
                        f"ヒアリングメモ:\n{raw_notes}"
                    ),
                }
            ],
        )

        data = _extract_json(response.content[0].text)
        return OrganizedRequirements(
            background=data["background"],
            issues=data["issues"],
            requests=data["requests"],
        )
