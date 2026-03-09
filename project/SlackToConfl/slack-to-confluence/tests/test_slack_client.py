import pytest
from unittest.mock import MagicMock, patch


class TestSlackClient:
    def setup_method(self):
        """各テスト前にSlackClientをモック付きで初期化"""
        with patch("slack_sdk.WebClient"):
            from slack_client import SlackClient
            self.client = SlackClient(token="xoxb-test-token")

    def test_get_messages_returns_list(self):
        """get_messagesがリストを返すこと"""
        mock_response = {
            "messages": [
                {"ts": "1704067200.000000", "user": "U12345", "text": "テストメッセージ"},
            ],
            "has_more": False,
        }
        self.client._client.conversations_history = MagicMock(return_value=mock_response)
        result = self.client.get_messages("CGVF155S7", 1704067200.0, 1704153600.0)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["text"] == "テストメッセージ"

    def test_get_messages_filters_bot_messages(self):
        """ボットメッセージがデフォルトで除外されること"""
        mock_response = {
            "messages": [
                {"ts": "1704067200.000000", "user": "U12345", "text": "通常メッセージ"},
                {"ts": "1704067300.000000", "bot_id": "B12345", "text": "ボットメッセージ"},
            ],
            "has_more": False,
        }
        self.client._client.conversations_history = MagicMock(return_value=mock_response)
        result = self.client.get_messages("CGVF155S7", 1704067200.0, 1704153600.0)
        assert len(result) == 1
        assert result[0]["text"] == "通常メッセージ"

    def test_get_messages_paginates(self):
        """ページネーションで全メッセージを取得すること"""
        first_response = {
            "messages": [
                {"ts": "1704067200.000000", "user": "U12345", "text": "メッセージ1"},
            ],
            "has_more": True,
            "response_metadata": {"next_cursor": "cursor123"},
        }
        second_response = {
            "messages": [
                {"ts": "1704067300.000000", "user": "U12345", "text": "メッセージ2"},
            ],
            "has_more": False,
        }
        self.client._client.conversations_history = MagicMock(
            side_effect=[first_response, second_response]
        )
        result = self.client.get_messages("CGVF155S7", 1704067200.0, 1704153600.0)
        assert len(result) == 2

    def test_get_user_name_returns_display_name(self):
        """get_user_nameがユーザーの表示名を返すこと"""
        mock_response = {
            "user": {
                "id": "U12345",
                "profile": {"display_name": "田中太郎", "real_name": "田中 太郎"},
            }
        }
        self.client._client.users_info = MagicMock(return_value=mock_response)
        result = self.client.get_user_name("U12345")
        assert result == "田中太郎"

    def test_get_user_name_falls_back_to_real_name(self):
        """display_nameが空の場合はreal_nameにフォールバックすること"""
        mock_response = {
            "user": {
                "id": "U12345",
                "profile": {"display_name": "", "real_name": "田中 太郎"},
            }
        }
        self.client._client.users_info = MagicMock(return_value=mock_response)
        result = self.client.get_user_name("U12345")
        assert result == "田中 太郎"

    def test_get_messages_retries_on_failure(self):
        """API失敗時に最大3回リトライすること"""
        from slack_sdk.errors import SlackApiError
        mock_response = MagicMock()
        mock_response.__getitem__ = MagicMock(return_value="ratelimited")

        success_response = {
            "messages": [{"ts": "1704067200.000000", "user": "U12345", "text": "OK"}],
            "has_more": False,
        }
        self.client._client.conversations_history = MagicMock(
            side_effect=[
                SlackApiError("ratelimited", mock_response),
                success_response,
            ]
        )
        result = self.client.get_messages("CGVF155S7", 1704067200.0, 1704153600.0)
        assert len(result) == 1
