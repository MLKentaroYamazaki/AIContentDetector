import os
import pytest
from unittest.mock import patch


class TestConfig:
    def test_load_slack_bot_token(self):
        """SLACK_BOT_TOKENが環境変数から読み込まれること"""
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "CONFLUENCE_BASE_URL": "https://test.atlassian.net",
            "CONFLUENCE_USER_EMAIL": "test@example.com",
            "CONFLUENCE_API_TOKEN": "test-api-token",
            "SLACK_CHANNEL_ID_ALL_NIPPON_MLGR": "CGVF155S7",
            "SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL": "C80JUUUMU",
            "SLACK_CHANNEL_ID_AIBA_ALL": "C08LJCL2JTG",
            "SLACK_CHANNEL_ID_AIBA_EDX_ALL": "C0AK24S555F",
            "CONFLUENCE_SPACE_KEY": "CD",
        }
        with patch.dict(os.environ, env, clear=True):
            from config import Config
            config = Config()
            assert config.slack_bot_token == "xoxb-test-token"

    def test_load_confluence_settings(self):
        """Confluence関連の設定が正しく読み込まれること"""
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "CONFLUENCE_BASE_URL": "https://test.atlassian.net",
            "CONFLUENCE_USER_EMAIL": "test@example.com",
            "CONFLUENCE_API_TOKEN": "test-api-token",
            "SLACK_CHANNEL_ID_ALL_NIPPON_MLGR": "CGVF155S7",
            "SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL": "C80JUUUMU",
            "SLACK_CHANNEL_ID_AIBA_ALL": "C08LJCL2JTG",
            "SLACK_CHANNEL_ID_AIBA_EDX_ALL": "C0AK24S555F",
            "CONFLUENCE_SPACE_KEY": "CD",
        }
        with patch.dict(os.environ, env, clear=True):
            from config import Config
            config = Config()
            assert config.confluence_base_url == "https://test.atlassian.net"
            assert config.confluence_user_email == "test@example.com"
            assert config.confluence_api_token == "test-api-token"
            assert config.confluence_space_key == "CD"

    def test_load_channel_ids(self):
        """SlackチャンネルIDが正しく読み込まれること"""
        env = {
            "SLACK_BOT_TOKEN": "xoxb-test-token",
            "CONFLUENCE_BASE_URL": "https://test.atlassian.net",
            "CONFLUENCE_USER_EMAIL": "test@example.com",
            "CONFLUENCE_API_TOKEN": "test-api-token",
            "SLACK_CHANNEL_ID_ALL_NIPPON_MLGR": "CGVF155S7",
            "SLACK_CHANNEL_ID_ANNOUNCEMENTS_ALL": "C80JUUUMU",
            "SLACK_CHANNEL_ID_AIBA_ALL": "C08LJCL2JTG",
            "SLACK_CHANNEL_ID_AIBA_EDX_ALL": "C0AK24S555F",
            "CONFLUENCE_SPACE_KEY": "CD",
        }
        with patch.dict(os.environ, env, clear=True):
            from config import Config
            config = Config()
            assert config.channel_all_nippon_mlgr == "CGVF155S7"
            assert config.channel_announcements_all == "C80JUUUMU"
            assert config.channel_aiba_all == "C08LJCL2JTG"
            assert config.channel_aiba_edx_all == "C0AK24S555F"

    def test_missing_required_env_raises_error(self):
        """必須環境変数が未設定の場合にエラーが発生すること"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises((ValueError, KeyError)):
                from config import Config
                Config()
