import pytest
from message_formatter import (
    format_timestamp,
    resolve_mentions,
    format_messages_as_table,
    build_page_content,
)


class TestFormatTimestamp:
    def test_unix_timestamp_to_jst(self):
        """UNIXタイムスタンプをJST形式に変換すること"""
        # 1704067200 = 2024-01-01 00:00:00 UTC = 2024-01-01 09:00:00 JST
        result = format_timestamp("1704067200.000000")
        assert result == "2024-01-01 09:00"

    def test_fractional_timestamp(self):
        """小数点付きタイムスタンプが正しく変換されること"""
        # 1704070800 = 2024-01-01 01:00:00 UTC = 2024-01-01 10:00:00 JST
        result = format_timestamp("1704070800.123456")
        assert result == "2024-01-01 10:00"

    def test_timestamp_format_is_yyyy_mm_dd_hh_mm(self):
        """出力形式がYYYY-MM-DD HH:MM形式であること"""
        result = format_timestamp("1704067200.000000")
        import re
        assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", result)


class TestResolveMentions:
    def test_resolve_single_mention(self):
        """単一のメンションをユーザー名に変換すること"""
        user_map = {"U12345": "田中太郎"}
        result = resolve_mentions("こんにちは <@U12345>!", user_map)
        assert result == "こんにちは @田中太郎!"

    def test_resolve_multiple_mentions(self):
        """複数のメンションを正しく変換すること"""
        user_map = {"U12345": "田中太郎", "U67890": "佐藤花子"}
        result = resolve_mentions("<@U12345> と <@U67890>", user_map)
        assert result == "@田中太郎 と @佐藤花子"

    def test_unknown_mention_kept_as_is(self):
        """user_mapに存在しないメンションはそのまま残すこと"""
        user_map = {}
        result = resolve_mentions("<@UUNKNOWN>", user_map)
        assert result == "<@UUNKNOWN>"

    def test_no_mention(self):
        """メンションがない場合はそのまま返すこと"""
        result = resolve_mentions("メンションなし", {})
        assert result == "メンションなし"


class TestFormatMessagesAsTable:
    def test_empty_messages_returns_no_messages(self):
        """メッセージが空の場合はメッセージなし文言を返すこと"""
        result = format_messages_as_table([])
        assert "メッセージなし" in result

    def test_single_message_table(self):
        """1件のメッセージがMarkdownテーブルとして整形されること"""
        messages = [
            {"datetime": "2024-01-01 09:00", "user": "田中太郎", "text": "おはようございます"}
        ]
        result = format_messages_as_table(messages)
        assert "| 日時 | 投稿者 | メッセージ |" in result
        assert "2024-01-01 09:00" in result
        assert "田中太郎" in result
        assert "おはようございます" in result

    def test_pipe_in_message_is_escaped(self):
        """メッセージ中のパイプ文字がエスケープされること"""
        messages = [
            {"datetime": "2024-01-01 09:00", "user": "テスト", "text": "A | B"}
        ]
        result = format_messages_as_table(messages)
        assert "A \\| B" in result

    def test_newline_in_message_is_replaced(self):
        """メッセージ中の改行が<br>に変換されること"""
        messages = [
            {"datetime": "2024-01-01 09:00", "user": "テスト", "text": "行1\n行2"}
        ]
        result = format_messages_as_table(messages)
        assert "<br>" in result


class TestBuildPageContent:
    def test_page_has_all_sections(self):
        """ページコンテンツに全社員向けとAIBAメンバー向けセクションが含まれること"""
        all_messages = {
            "#all_nippon_mlgr": [],
            "#announcements-all": [],
        }
        aiba_messages = {
            "#aiba-all": [],
            "#aiba-edx-all": [],
        }
        period = {"start": "2024-01-01", "end": "2024-01-07"}
        result = build_page_content(all_messages, aiba_messages, period)
        assert "全社員向けメッセージ" in result
        assert "AIBAメンバー向けメッセージ" in result
        assert "#all_nippon_mlgr" in result
        assert "#announcements-all" in result
        assert "#aiba-all" in result
        assert "#aiba-edx-all" in result

    def test_page_includes_period(self):
        """ページコンテンツに期間が含まれること"""
        all_messages = {"#all_nippon_mlgr": [], "#announcements-all": []}
        aiba_messages = {"#aiba-all": [], "#aiba-edx-all": []}
        period = {"start": "2024-01-01", "end": "2024-01-07"}
        result = build_page_content(all_messages, aiba_messages, period)
        assert "2024-01-01" in result
        assert "2024-01-07" in result

    def test_page_title_includes_date(self):
        """ページコンテンツのタイトルに日付が含まれること"""
        all_messages = {"#all_nippon_mlgr": [], "#announcements-all": []}
        aiba_messages = {"#aiba-all": [], "#aiba-edx-all": []}
        period = {"start": "2024-01-07", "end": "2024-01-14"}
        result = build_page_content(all_messages, aiba_messages, period)
        assert "週次Slackレポート" in result
