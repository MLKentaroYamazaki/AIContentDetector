import logging
from typing import Optional
from atlassian import Confluence

logger = logging.getLogger(__name__)


class ConfluenceClient:
    def __init__(self, base_url: str, user_email: str, api_token: str):
        self._confluence = Confluence(
            url=base_url,
            username=user_email,
            password=api_token,
            cloud=True,
        )

    def find_parent_page(self, space_key: str, date_str: str) -> Optional[str]:
        """スペース内で実行日付(YYYYMMDD)で始まるタイトルのページを検索してIDを返す"""
        try:
            pages = self._confluence.get_all_pages_by_space(
                space=space_key, start=0, limit=50, expand="title"
            )
            for page in pages:
                if page["title"].startswith(date_str):
                    return page["id"]
            logger.warning("親ページが見つかりません: space=%s, date=%s", space_key, date_str)
            return None
        except Exception as e:
            logger.error("親ページ検索中にエラー: %s", e)
            return None

    def create_or_update_page(
        self, space_key: str, parent_id: str, title: str, content: str
    ) -> bool:
        """指定タイトルのページを作成または更新する（冪等性保証）"""
        try:
            existing = self._confluence.get_page_by_title(space=space_key, title=title)
            if existing:
                version = existing["version"]["number"] + 1
                self._confluence.update_page(
                    page_id=existing["id"],
                    title=title,
                    body=content,
                    version=version,
                )
                logger.info("ページを更新しました: %s", title)
            else:
                self._confluence.create_page(
                    space=space_key,
                    title=title,
                    body=content,
                    parent_id=parent_id,
                )
                logger.info("ページを作成しました: %s", title)
            return True
        except Exception as e:
            logger.error("ページ作成/更新中にエラー: %s", e)
            return False
