"""提案骨子作成機能"""
from dataclasses import dataclass
from typing import Optional
from anthropic import Anthropic

from .requirement_organizer import OrganizedRequirements, _extract_json


@dataclass
class ProposalDraft:
    proposal_points: list[str]
    development_policy: str


class ProposalGenerator:
    """与件整理結果から「ご提案ポイント」「開発方針」のドラフトを生成する"""

    def __init__(self, client: Optional[Anthropic] = None):
        self._client = client or Anthropic()

    def generate(self, requirements: OrganizedRequirements) -> ProposalDraft:
        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "以下の与件整理情報をもとに、提案書の「ご提案ポイント（3〜4点）」と「開発方針」を作成してください。\n"
                        "必ずJSON形式のみで回答し、他の文章は一切含めないでください。\n\n"
                        "出力形式:\n"
                        '{"proposal_points": ["点1", "点2", "点3"], "development_policy": "..."}\n\n'
                        f"背景: {requirements.background}\n"
                        f"課題: {requirements.issues}\n"
                        f"要望: {requirements.requests}"
                    ),
                }
            ],
        )

        data = _extract_json(response.content[0].text)
        return ProposalDraft(
            proposal_points=data["proposal_points"],
            development_policy=data["development_policy"],
        )
