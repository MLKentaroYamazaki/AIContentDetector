import os
from anthropic import Anthropic

SYSTEM_PROMPT = (
    "あなたはプロフェッショナルな議事録作成者です。"
    "提供されたSlackログから「議論の背景」「決定事項」「ネクストアクション（担当者含む）」を抽出してください。"
    "出力はConfluence Storage Format (XHTML) で行い、<h2>, <ul>, <li> を使用してください。"
    "重要事項には <ac:structured-macro ac:name=\"info\"> 等のConfluence固有マクロを使用してください。"
    "余計な説明文や ```html ``` などのコードブロックは含めず、XHTMLのみを出力してください。"
)


class ClaudeClient:
    def __init__(self, api_key: str = None):
        self.client = Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])

    def summarize(self, messages: list[dict]) -> str:
        """SlackメッセージリストをConfluence用XHTMLで要約する"""
        log_text = self._format_messages(messages)
        prompt = f"以下のSlackログをConfluence用のHTML（Storage Format）形式で、決定事項とToDoを整理して要約してください:\n\n{log_text}"

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _format_messages(self, messages: list[dict]) -> str:
        lines = []
        for msg in messages:
            indent = "  " if msg.get("level", 0) > 0 else ""
            lines.append(f"{indent}[{msg['user']}]: {msg['text']}")
        return "\n".join(lines)
