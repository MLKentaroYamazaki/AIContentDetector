import os
import sys
import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.slack_client import SlackClient
from modules.claude_client import ClaudeClient
from modules.confluence_client import ConfluenceClient

load_dotenv()


def main():
    channel_id = os.environ["CHANNEL_ID"]
    conf_space = os.environ["CONF_SPACE"]

    now = datetime.datetime.now()
    oldest = (now - datetime.timedelta(days=7)).timestamp()

    print(f"[INFO] 対象期間: {now - datetime.timedelta(days=7):%Y/%m/%d} 〜 {now:%Y/%m/%d}")

    slack = SlackClient()
    claude = ClaudeClient()
    confluence = ConfluenceClient()

    print("[INFO] Slackメッセージを取得中...")
    messages = slack.fetch_messages(channel_id=channel_id, oldest=oldest)
    print(f"[INFO] {len(messages)} 件のメッセージを取得しました")

    if not messages:
        print("[WARN] メッセージが存在しないため処理を終了します")
        return

    print("[INFO] Claude でサマリーを生成中...")
    summary_xhtml = claude.summarize(messages)

    page_title = f"{now:%Y%m%d} 週次Slackレポート"
    print(f"[INFO] Confluenceページを作成/更新中: {page_title}")

    result = confluence.upsert_page(space=conf_space, title=page_title, body=summary_xhtml)
    page_url = result.get("_links", {}).get("webui", "")
    print(f"[INFO] 完了: {page_url}")


if __name__ == "__main__":
    main()
