import pytest
from unittest.mock import MagicMock, patch
from modules.slack_client import SlackClient


@pytest.fixture
def mock_slack_client():
    with patch("modules.slack_client.WebClient") as MockWebClient:
        instance = MockWebClient.return_value
        yield instance


def test_fetch_messages_basic(mock_slack_client):
    mock_slack_client.conversations_history.return_value = {
        "messages": [
            {"user": "U001", "text": "こんにちは", "ts": "1000000000.000001"},
        ]
    }
    mock_slack_client.users_info.return_value = {"user": {"real_name": "田中 太郎"}}

    client = SlackClient(token="xoxb-test")
    logs = client.fetch_messages(channel_id="C001", oldest=999999999.0)

    assert len(logs) == 1
    assert logs[0]["user"] == "田中 太郎"
    assert logs[0]["text"] == "こんにちは"
    assert logs[0]["level"] == 0


def test_fetch_messages_skips_bot(mock_slack_client):
    mock_slack_client.conversations_history.return_value = {
        "messages": [
            {"subtype": "bot_message", "text": "bot says hi", "ts": "1000000000.000001"},
            {"user": "U001", "text": "人間のメッセージ", "ts": "1000000000.000002"},
        ]
    }
    mock_slack_client.users_info.return_value = {"user": {"real_name": "鈴木 花子"}}

    client = SlackClient(token="xoxb-test")
    logs = client.fetch_messages(channel_id="C001", oldest=999999999.0)

    assert len(logs) == 1
    assert logs[0]["text"] == "人間のメッセージ"


def test_fetch_messages_with_thread(mock_slack_client):
    mock_slack_client.conversations_history.return_value = {
        "messages": [
            {
                "user": "U001",
                "text": "親メッセージ",
                "ts": "1000000000.000001",
                "thread_ts": "1000000000.000001",
            }
        ]
    }
    mock_slack_client.conversations_replies.return_value = {
        "messages": [
            {"user": "U001", "text": "親メッセージ", "ts": "1000000000.000001"},
            {"user": "U002", "text": "返信メッセージ", "ts": "1000000000.000002"},
        ]
    }
    mock_slack_client.users_info.side_effect = lambda user: {
        "U001": {"user": {"real_name": "田中 太郎"}},
        "U002": {"user": {"real_name": "山田 次郎"}},
    }[user]

    client = SlackClient(token="xoxb-test")
    logs = client.fetch_messages(channel_id="C001", oldest=999999999.0)

    assert len(logs) == 2
    assert logs[0]["level"] == 0
    assert logs[1]["level"] == 1
    assert logs[1]["text"] == "返信メッセージ"


def test_fetch_messages_skips_ignore_reaction(mock_slack_client):
    mock_slack_client.conversations_history.return_value = {
        "messages": [
            {
                "user": "U001",
                "text": "無視されるメッセージ",
                "ts": "1000000000.000001",
                "reactions": [{"name": "ignore"}],
            }
        ]
    }

    client = SlackClient(token="xoxb-test")
    logs = client.fetch_messages(channel_id="C001", oldest=999999999.0)

    assert len(logs) == 0
