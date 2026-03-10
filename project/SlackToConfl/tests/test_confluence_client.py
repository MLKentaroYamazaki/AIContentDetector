import pytest
from unittest.mock import MagicMock, patch
from modules.confluence_client import ConfluenceClient


@pytest.fixture
def mock_confluence():
    with patch("modules.confluence_client.Confluence") as MockConfluence:
        instance = MockConfluence.return_value
        yield instance


def test_upsert_page_creates_new_when_not_exists(mock_confluence):
    mock_confluence.get_page_by_title.return_value = None
    mock_confluence.create_page.return_value = {"_links": {"webui": "/pages/123"}}

    client = ConfluenceClient(url="https://example.atlassian.net", username="user", token="token")
    result = client.upsert_page(space="SPACE", title="Test Page", body="<h2>Test</h2>")

    mock_confluence.create_page.assert_called_once_with(
        space="SPACE",
        title="Test Page",
        body="<h2>Test</h2>",
        representation="storage",
    )
    assert result["_links"]["webui"] == "/pages/123"


def test_upsert_page_updates_existing(mock_confluence):
    mock_confluence.get_page_by_title.return_value = {
        "id": "456",
        "version": {"number": 2},
    }
    mock_confluence.update_page.return_value = {"_links": {"webui": "/pages/456"}}

    client = ConfluenceClient(url="https://example.atlassian.net", username="user", token="token")
    result = client.upsert_page(space="SPACE", title="Existing Page", body="<h2>Updated</h2>")

    mock_confluence.update_page.assert_called_once_with(
        page_id="456",
        title="Existing Page",
        body="<h2>Updated</h2>",
        version=3,
        representation="storage",
    )
    assert result["_links"]["webui"] == "/pages/456"
