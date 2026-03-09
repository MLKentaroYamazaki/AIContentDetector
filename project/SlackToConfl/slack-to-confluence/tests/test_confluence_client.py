import pytest
from unittest.mock import MagicMock, patch


class TestConfluenceClient:
    def setup_method(self):
        """各テスト前にConfluenceClientをモック付きで初期化"""
        with patch("atlassian.Confluence"):
            from confluence_client import ConfluenceClient
            self.client = ConfluenceClient(
                base_url="https://test.atlassian.net",
                user_email="test@example.com",
                api_token="test-token",
            )

    def test_find_parent_page_by_date_prefix(self):
        """実行日のYYYYMMDDでタイトル検索して親ページを取得すること"""
        mock_pages = [
            {"id": "111", "title": "20260304 Team B"},
            {"id": "222", "title": "20260225 Team B"},
        ]
        self.client._confluence.get_all_pages_by_space = MagicMock(return_value=mock_pages)
        result = self.client.find_parent_page("CD", "20260304")
        assert result == "111"

    def test_find_parent_page_returns_none_when_not_found(self):
        """該当ページが見つからない場合はNoneを返すこと"""
        mock_pages = [
            {"id": "222", "title": "20260225 Team B"},
        ]
        self.client._confluence.get_all_pages_by_space = MagicMock(return_value=mock_pages)
        result = self.client.find_parent_page("CD", "20260304")
        assert result is None

    def test_create_page_when_not_exists(self):
        """同タイトルのページが存在しない場合に新規作成すること"""
        self.client._confluence.get_page_by_title = MagicMock(return_value=None)
        self.client._confluence.create_page = MagicMock(return_value={"id": "999"})
        result = self.client.create_or_update_page(
            space_key="CD",
            parent_id="111",
            title="20260304 週次Slackレポート",
            content="# テストコンテンツ",
        )
        assert result is True
        self.client._confluence.create_page.assert_called_once()

    def test_update_page_when_exists(self):
        """同タイトルのページが既存の場合は更新すること（冪等性）"""
        existing_page = {"id": "777", "version": {"number": 1}}
        self.client._confluence.get_page_by_title = MagicMock(return_value=existing_page)
        self.client._confluence.update_page = MagicMock(return_value={"id": "777"})
        result = self.client.create_or_update_page(
            space_key="CD",
            parent_id="111",
            title="20260304 週次Slackレポート",
            content="# 更新コンテンツ",
        )
        assert result is True
        self.client._confluence.update_page.assert_called_once()

    def test_create_or_update_returns_false_on_api_error(self):
        """API失敗時にFalseを返してエラーログを出力すること"""
        self.client._confluence.get_page_by_title = MagicMock(
            side_effect=Exception("API Error")
        )
        result = self.client.create_or_update_page(
            space_key="CD",
            parent_id="111",
            title="20260304 週次Slackレポート",
            content="# コンテンツ",
        )
        assert result is False
