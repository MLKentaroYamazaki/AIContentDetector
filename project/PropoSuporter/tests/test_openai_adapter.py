"""OpenAI互換アダプター（Groq/Ollama対応）のテスト"""
import pytest
from unittest.mock import MagicMock, patch
from propo_suporter.openai_adapter import OpenAICompatibleAdapter


class TestOpenAICompatibleAdapter:
    """Anthropicクライアント互換のOpenAIアダプターテスト"""

    @pytest.fixture
    def mock_openai_client(self):
        client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "テスト応答"
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        client.chat.completions.create.return_value = mock_response
        return client

    @pytest.fixture
    def adapter(self, mock_openai_client):
        return OpenAICompatibleAdapter(client=mock_openai_client)

    def test_messages_create_returns_anthropic_compatible_response(self, adapter):
        """messages.create()がAnthropicと同じ形式のレスポンスを返す"""
        result = adapter.messages.create(
            model="llama3-8b-8192",
            max_tokens=1024,
            messages=[{"role": "user", "content": "テスト"}],
        )
        assert hasattr(result, "content")
        assert len(result.content) > 0
        assert hasattr(result.content[0], "text")

    def test_messages_create_content_text_matches_response(self, adapter, mock_openai_client):
        """content[0].textがOpenAIレスポンスのcontent値と一致する"""
        result = adapter.messages.create(
            model="llama3-8b-8192",
            max_tokens=1024,
            messages=[{"role": "user", "content": "テスト"}],
        )
        assert result.content[0].text == "テスト応答"

    def test_messages_create_calls_openai_chat_completions(self, adapter, mock_openai_client):
        """内部でOpenAIのchat.completions.createを呼び出す"""
        adapter.messages.create(
            model="llama3-8b-8192",
            max_tokens=1024,
            messages=[{"role": "user", "content": "テスト"}],
        )
        mock_openai_client.chat.completions.create.assert_called_once()

    def test_messages_create_passes_messages_to_openai(self, adapter, mock_openai_client):
        """messagesパラメータがOpenAI APIに渡される"""
        messages = [{"role": "user", "content": "テストメッセージ"}]
        adapter.messages.create(
            model="llama3-8b-8192",
            max_tokens=1024,
            messages=messages,
        )
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"] == messages

    def test_messages_create_passes_max_tokens_to_openai(self, adapter, mock_openai_client):
        """max_tokensパラメータがOpenAI APIに渡される"""
        adapter.messages.create(
            model="llama3-8b-8192",
            max_tokens=512,
            messages=[{"role": "user", "content": "テスト"}],
        )
        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 512
