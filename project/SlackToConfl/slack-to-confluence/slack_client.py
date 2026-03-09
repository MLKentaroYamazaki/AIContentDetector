import logging
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 1


class SlackClient:
    def __init__(self, token: str):
        self._client = WebClient(token=token)

    def get_messages(
        self,
        channel_id: str,
        oldest: float,
        latest: float,
        exclude_bots: bool = True,
    ) -> list:
        """指定チャンネルの指定期間のメッセージを取得する（ページネーション対応）"""
        messages = []
        cursor = None

        while True:
            params = {
                "channel": channel_id,
                "oldest": str(oldest),
                "latest": str(latest),
                "limit": 200,
            }
            if cursor:
                params["cursor"] = cursor

            response = self._call_with_retry(
                self._client.conversations_history, **params
            )

            for msg in response.get("messages", []):
                if exclude_bots and "bot_id" in msg:
                    continue
                messages.append(msg)

            if not response.get("has_more"):
                break

            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

            time.sleep(0.5)

        return messages

    def get_user_name(self, user_id: str) -> str:
        """ユーザーIDからユーザー名（display_name or real_name）を取得する"""
        response = self._call_with_retry(self._client.users_info, user=user_id)
        profile = response["user"]["profile"]
        return profile.get("display_name") or profile.get("real_name", user_id)

    def _call_with_retry(self, func, **kwargs):
        """最大MAX_RETRIES回リトライしてAPI呼び出しを実行する"""
        for attempt in range(MAX_RETRIES):
            try:
                return func(**kwargs)
            except SlackApiError as e:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(
                        "Slack API エラー（%d/%d回目）: %s", attempt + 1, MAX_RETRIES, e
                    )
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    logger.error("Slack API 失敗（最大リトライ回数超過）: %s", e)
                    raise
