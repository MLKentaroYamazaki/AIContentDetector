import pytest
from unittest.mock import MagicMock, patch
from modules.claude_client import ClaudeClient


@pytest.fixture
def mock_anthropic():
    with patch("modules.claude_client.Anthropic") as MockAnthropic:
        instance = MockAnthropic.return_value
        content = MagicMock()
        content.text = "<h2>決定事項</h2><ul><li>テスト決定</li></ul>"
        instance.messages.create.return_value.content = [content]
        yield instance


def test_summarize_returns_xhtml(mock_anthropic):
    client = ClaudeClient(api_key="test-key")
    messages = [
        {"user": "田中 太郎", "text": "今週の方針を決めましょう", "level": 0},
        {"user": "鈴木 花子", "text": "了解です", "level": 1},
    ]

    result = client.summarize(messages)

    assert "<h2>" in result
    mock_anthropic.messages.create.assert_called_once()
    call_kwargs = mock_anthropic.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-3-5-sonnet-20241022"
    assert call_kwargs["max_tokens"] == 4000


def test_format_messages_indents_replies():
    client = ClaudeClient(api_key="test-key")
    messages = [
        {"user": "A", "text": "親", "level": 0},
        {"user": "B", "text": "返信", "level": 1},
    ]
    formatted = client._format_messages(messages)
    lines = formatted.split("\n")
    assert lines[0].startswith("[A]")
    assert lines[1].startswith("  [B]")
