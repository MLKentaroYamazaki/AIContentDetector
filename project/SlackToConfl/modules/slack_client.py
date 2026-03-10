import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackClient:
    def __init__(self, token: str = None):
        self.client = WebClient(token=token or os.environ["SLACK_BOT_TOKEN"])

    def fetch_messages(self, channel_id: str, oldest: float) -> list[dict]:
        """過去7日間のメッセージ（スレッド含む）を取得する"""
        logs = []
        try:
            res = self.client.conversations_history(channel=channel_id, oldest=oldest)
        except SlackApiError as e:
            raise RuntimeError(f"Slack conversations.history failed: {e.response['error']}")

        for msg in res["messages"]:
            if msg.get("subtype") == "bot_message":
                continue
            if "ignore" in [r.get("name") for r in msg.get("reactions", [])]:
                continue

            user_name = self._get_user_name(msg.get("user"))
            logs.append({
                "user": user_name,
                "text": msg.get("text", ""),
                "ts": msg.get("ts"),
                "level": 0,
            })

            if "thread_ts" in msg:
                logs.extend(self._fetch_thread(channel_id, msg["thread_ts"]))

        return logs

    def _fetch_thread(self, channel_id: str, thread_ts: str) -> list[dict]:
        replies = []
        try:
            res = self.client.conversations_replies(channel=channel_id, ts=thread_ts)
        except SlackApiError as e:
            raise RuntimeError(f"Slack conversations.replies failed: {e.response['error']}")

        for r in res["messages"][1:]:  # 最初のメッセージはスレッド親なのでスキップ
            if r.get("subtype") == "bot_message":
                continue
            user_name = self._get_user_name(r.get("user"))
            replies.append({
                "user": user_name,
                "text": r.get("text", ""),
                "ts": r.get("ts"),
                "level": 1,
            })
        return replies

    def _get_user_name(self, user_id: str) -> str:
        if not user_id:
            return "Unknown"
        try:
            info = self.client.users_info(user=user_id)
            return info["user"]["real_name"]
        except SlackApiError:
            return user_id
