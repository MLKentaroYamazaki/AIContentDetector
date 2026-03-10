import os
from atlassian import Confluence


class ConfluenceClient:
    def __init__(self, url: str = None, username: str = None, token: str = None):
        self.client = Confluence(
            url=url or os.environ["CONF_URL"],
            username=username or os.environ["CONF_USER"],
            password=token or os.environ["CONF_TOKEN"],
        )

    def upsert_page(self, space: str, title: str, body: str) -> dict:
        """同一タイトルのページがあればバージョンアップ、なければ新規作成する"""
        existing = self.client.get_page_by_title(space=space, title=title)
        if existing:
            page_id = existing["id"]
            version = existing["version"]["number"] + 1
            return self.client.update_page(
                page_id=page_id,
                title=title,
                body=body,
                version=version,
                representation="storage",
            )
        else:
            return self.client.create_page(
                space=space,
                title=title,
                body=body,
                representation="storage",
            )
