import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.slack_bot_token = self._require("SLACK_BOT_TOKEN")
        self.confluence_base_url = self._require("CONFLUENCE_BASE_URL")
        self.confluence_user_email = self._require("CONFLUENCE_USER_EMAIL")
        self.confluence_api_token = self._require("CONFLUENCE_API_TOKEN")
        self.confluence_space_key = self._require("CONFLUENCE_SPACE_KEY")
        self.channel_all_nippon_mlgr = self._require("SLACK_CHANNEL_ID_ALL_NIPPON_MLGR")
        self.channel_announcements_all = self._require("SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL")
        self.channel_aiba_all = self._require("SLACK_CHANNEL_ID_AIBA_ALL")
        self.channel_aiba_edx_all = self._require("SLACK_CHANNEL_ID_AIBA_EDX_ALL")

    def _require(self, key: str) -> str:
        value = os.environ.get(key)
        if not value:
            raise ValueError(f"必須環境変数が設定されていません: {key}")
        return value
