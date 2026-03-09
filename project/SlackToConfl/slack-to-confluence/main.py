import logging
import logging.handlers
import os
from datetime import datetime, timedelta

import pytz

from config import Config
from slack_client import SlackClient
from confluence_client import ConfluenceClient
from message_formatter import format_timestamp, resolve_mentions, build_page_content

JST = pytz.timezone("Asia/Tokyo")
logger = logging.getLogger(__name__)


def _setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/app.log", encoding="utf-8"),
        ],
    )


def get_time_range() -> tuple:
    """直前の火曜日15:00 JST から 今回の火曜日15:00 JST までの時刻範囲を返す"""
    now = datetime.now(JST)
    days_since_tuesday = (now.weekday() - 1) % 7
    this_tuesday = now.replace(hour=15, minute=0, second=0, microsecond=0) - timedelta(
        days=days_since_tuesday
    )
    last_tuesday = this_tuesday - timedelta(weeks=1)
    return last_tuesday.timestamp(), this_tuesday.timestamp()


def run():
    """メイン処理: Slackからメッセージ取得 → Confluenceにページ出力"""
    _setup_logging()

    config = Config()
    slack = SlackClient(token=config.slack_bot_token)
    confluence = ConfluenceClient(
        base_url=config.confluence_base_url,
        user_email=config.confluence_user_email,
        api_token=config.confluence_api_token,
    )

    start_ts, end_ts = get_time_range()
    start_dt = datetime.fromtimestamp(start_ts, tz=JST)
    end_dt = datetime.fromtimestamp(end_ts, tz=JST)
    period = {
        "start": start_dt.strftime("%Y-%m-%d"),
        "end": end_dt.strftime("%Y-%m-%d"),
    }
    today_str = end_dt.strftime("%Y%m%d")
    page_title = f"{today_str} 週次Slackレポート"

    logger.info("実行開始: %s〜%s", period["start"], period["end"])

    all_channels = {
        "#all_nippon_mlgr": config.channel_all_nippon_mlgr,
        "#announcements-all": config.channel_announcements_all,
    }
    aiba_channels = {
        "#aiba-all": config.channel_aiba_all,
        "#aiba-edx-all": config.channel_aiba_edx_all,
    }

    user_cache = {}

    def fetch_and_format(channels: dict) -> dict:
        result = {}
        for name, channel_id in channels.items():
            raw = slack.get_messages(channel_id, start_ts, end_ts)
            logger.info("%s: %d件取得", name, len(raw))
            formatted = []
            for msg in raw:
                user_id = msg.get("user", "")
                if user_id not in user_cache:
                    try:
                        user_cache[user_id] = slack.get_user_name(user_id)
                    except Exception:
                        user_cache[user_id] = user_id
                formatted.append(
                    {
                        "datetime": format_timestamp(msg["ts"]),
                        "user": user_cache[user_id],
                        "text": msg.get("text", ""),
                    }
                )
            result[name] = formatted
        return result

    all_messages = fetch_and_format(all_channels)
    aiba_messages = fetch_and_format(aiba_channels)

    parent_id = confluence.find_parent_page(config.confluence_space_key, today_str)
    if parent_id is None:
        logger.warning(
            "親ページが見つからないためスキップします: space=%s, date=%s",
            config.confluence_space_key,
            today_str,
        )
        return

    content = build_page_content(all_messages, aiba_messages, period)
    success = confluence.create_or_update_page(
        space_key=config.confluence_space_key,
        parent_id=parent_id,
        title=page_title,
        content=content,
    )

    if success:
        logger.info("完了: %s", page_title)
    else:
        logger.error("ページ出力に失敗しました: %s", page_title)


if __name__ == "__main__":
    run()
