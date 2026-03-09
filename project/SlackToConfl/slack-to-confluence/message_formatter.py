import re
from datetime import datetime
import pytz

JST = pytz.timezone("Asia/Tokyo")


def format_timestamp(ts: str) -> str:
    """UNIXタイムスタンプをJST形式（YYYY-MM-DD HH:MM）に変換する"""
    dt = datetime.fromtimestamp(float(ts), tz=pytz.utc).astimezone(JST)
    return dt.strftime("%Y-%m-%d %H:%M")


def resolve_mentions(text: str, user_map: dict) -> str:
    """テキスト内の<@UXXXXXXX>をユーザー名に変換する"""
    def replace_mention(match):
        user_id = match.group(1)
        if user_id in user_map:
            return f"@{user_map[user_id]}"
        return match.group(0)

    return re.sub(r"<@([A-Z0-9]+)>", replace_mention, text)


def format_messages_as_table(messages: list) -> str:
    """メッセージのリストをMarkdownテーブル形式に変換する"""
    if not messages:
        return "（メッセージなし）"

    lines = [
        "| 日時 | 投稿者 | メッセージ |",
        "|------|--------|-----------|",
    ]
    for msg in messages:
        text = msg["text"].replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| {msg['datetime']} | {msg['user']} | {text} |")

    return "\n".join(lines)


def build_page_content(all_messages: dict, aiba_messages: dict, period: dict) -> str:
    """Confluenceページのコンテンツを構築する"""
    start = period["start"]
    end = period["end"]

    end_dt = datetime.strptime(end, "%Y-%m-%d")
    title_date = end_dt.strftime("%Y年%m月%d日")

    sections = [
        f"## 週次Slackレポート - {title_date}",
        "",
        "### 📢 全社員向けメッセージ",
        f"期間：{start} 〜 {end}",
        "",
    ]

    for channel_name, messages in all_messages.items():
        sections.append(f"#### {channel_name}")
        sections.append("")
        sections.append(format_messages_as_table(messages))
        sections.append("")

    sections.append("---")
    sections.append("")
    sections.append("### 👥 AIBAメンバー向けメッセージ")
    sections.append(f"期間：{start} 〜 {end}")
    sections.append("")

    for channel_name, messages in aiba_messages.items():
        sections.append(f"#### {channel_name}")
        sections.append("")
        sections.append(format_messages_as_table(messages))
        sections.append("")

    return "\n".join(sections)
