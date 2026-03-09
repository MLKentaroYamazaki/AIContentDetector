"""与件整理機能のテスト"""
import pytest
from unittest.mock import MagicMock, patch
from propo_suporter.requirement_organizer import RequirementOrganizer, OrganizedRequirements


class TestOrganizedRequirements:
    """与件整理結果のデータ構造テスト"""

    def test_has_background_field(self):
        result = OrganizedRequirements(
            background="背景テキスト",
            issues="課題テキスト",
            requests="要望テキスト",
        )
        assert result.background == "背景テキスト"

    def test_has_issues_field(self):
        result = OrganizedRequirements(
            background="背景テキスト",
            issues="課題テキスト",
            requests="要望テキスト",
        )
        assert result.issues == "課題テキスト"

    def test_has_requests_field(self):
        result = OrganizedRequirements(
            background="背景テキスト",
            issues="課題テキスト",
            requests="要望テキスト",
        )
        assert result.requests == "要望テキスト"


class TestRequirementOrganizer:
    """与件整理機能のテスト"""

    @pytest.fixture
    def mock_client(self):
        client = MagicMock()
        return client

    @pytest.fixture
    def organizer(self, mock_client):
        return RequirementOrganizer(client=mock_client)

    def test_organize_returns_organized_requirements(self, organizer, mock_client):
        """乱雑なメモからOrganizedRequirementsを返す"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "background": "顧客は新しいシステム導入を検討している",
            "issues": "現行システムが老朽化し、業務効率が低下している",
            "requests": "2025年4月までにシステムを刷新したい"
        }"""
        mock_client.messages.create.return_value = mock_response

        raw_notes = "先方から話を聞いた。なんかシステムが古くて困ってるらしい。4月までになんとかしたいって言ってた。"
        result = organizer.organize(raw_notes)

        assert isinstance(result, OrganizedRequirements)
        assert result.background != ""
        assert result.issues != ""
        assert result.requests != ""

    def test_organize_calls_claude_api(self, organizer, mock_client):
        """Claude APIを呼び出すことを確認"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "background": "背景",
            "issues": "課題",
            "requests": "要望"
        }"""
        mock_client.messages.create.return_value = mock_response

        raw_notes = "ヒアリングメモ"
        organizer.organize(raw_notes)

        mock_client.messages.create.assert_called_once()

    def test_organize_includes_raw_notes_in_prompt(self, organizer, mock_client):
        """ヒアリングメモがAPIのプロンプトに含まれることを確認"""
        mock_response = MagicMock()
        mock_response.content[0].text = """{
            "background": "背景",
            "issues": "課題",
            "requests": "要望"
        }"""
        mock_client.messages.create.return_value = mock_response

        raw_notes = "ユニークなヒアリングメモ12345"
        organizer.organize(raw_notes)

        call_args = mock_client.messages.create.call_args
        messages = call_args.kwargs.get("messages") or call_args.args[0]
        prompt_text = str(messages)
        assert raw_notes in prompt_text

    def test_organize_with_empty_notes_raises_value_error(self, organizer):
        """空のメモはValueErrorを発生させる"""
        with pytest.raises(ValueError, match="ヒアリングメモが空です"):
            organizer.organize("")
