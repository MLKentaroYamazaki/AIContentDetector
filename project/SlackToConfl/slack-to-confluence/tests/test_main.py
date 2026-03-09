import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch
import pytz


class TestGetTimeRange:
    def test_returns_tuple_of_two_floats(self):
        """get_time_rangeがfloatのタプルを返すこと"""
        from main import get_time_range
        start, end = get_time_range()
        assert isinstance(start, float)
        assert isinstance(end, float)

    def test_range_is_7_days(self):
        """取得期間が7日間（前回火曜15:00〜今回火曜15:00）であること"""
        from main import get_time_range
        start, end = get_time_range()
        diff_seconds = end - start
        assert abs(diff_seconds - 7 * 24 * 3600) < 1

    def test_end_time_is_tuesday_15_jst(self):
        """終了時刻が火曜日15:00 JSTであること"""
        from main import get_time_range
        JST = pytz.timezone("Asia/Tokyo")
        _, end = get_time_range()
        end_dt = datetime.fromtimestamp(end, tz=JST)
        assert end_dt.weekday() == 1  # 火曜日
        assert end_dt.hour == 15
        assert end_dt.minute == 0


class TestRun:
    @patch("main.ConfluenceClient")
    @patch("main.SlackClient")
    @patch("main.Config")
    def test_run_fetches_all_channels(self, mock_config_cls, mock_slack_cls, mock_confluence_cls):
        """runが全チャンネルのメッセージを取得すること"""
        mock_config = MagicMock()
        mock_config.slack_bot_token = "xoxb-test"
        mock_config.confluence_base_url = "https://test.atlassian.net"
        mock_config.confluence_user_email = "test@example.com"
        mock_config.confluence_api_token = "test-token"
        mock_config.confluence_space_key = "CD"
        mock_config.channel_all_nippon_mlgr = "CGVF155S7"
        mock_config.channel_announcements_all = "C80JUUUMU"
        mock_config.channel_aiba_all = "C08LJCL2JTG"
        mock_config.channel_aiba_edx_all = "C0AK24S555F"
        mock_config_cls.return_value = mock_config

        mock_slack = MagicMock()
        mock_slack.get_messages.return_value = []
        mock_slack.get_user_name.return_value = "テストユーザー"
        mock_slack_cls.return_value = mock_slack

        mock_confluence = MagicMock()
        mock_confluence.find_parent_page.return_value = "111"
        mock_confluence.create_or_update_page.return_value = True
        mock_confluence_cls.return_value = mock_confluence

        from main import run
        run()

        # 4チャンネル分取得されること
        assert mock_slack.get_messages.call_count == 4

    @patch("main.ConfluenceClient")
    @patch("main.SlackClient")
    @patch("main.Config")
    def test_run_skips_when_parent_page_not_found(
        self, mock_config_cls, mock_slack_cls, mock_confluence_cls
    ):
        """親ページが見つからない場合はページ作成をスキップすること"""
        mock_config = MagicMock()
        mock_config.slack_bot_token = "xoxb-test"
        mock_config.confluence_base_url = "https://test.atlassian.net"
        mock_config.confluence_user_email = "test@example.com"
        mock_config.confluence_api_token = "test-token"
        mock_config.confluence_space_key = "CD"
        mock_config.channel_all_nippon_mlgr = "CGVF155S7"
        mock_config.channel_announcements_all = "C80JUUUMU"
        mock_config.channel_aiba_all = "C08LJCL2JTG"
        mock_config.channel_aiba_edx_all = "C0AK24S555F"
        mock_config_cls.return_value = mock_config

        mock_slack = MagicMock()
        mock_slack.get_messages.return_value = []
        mock_slack_cls.return_value = mock_slack

        mock_confluence = MagicMock()
        mock_confluence.find_parent_page.return_value = None
        mock_confluence_cls.return_value = mock_confluence

        from main import run
        run()

        mock_confluence.create_or_update_page.assert_not_called()
