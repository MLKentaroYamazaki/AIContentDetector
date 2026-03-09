"""ハイライト・アドバイス機能のユニットテスト"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.highlight import generate_highlighted_sections, generate_advice
from app.schemas.analyze import HighlightedSection


# --- generate_highlighted_sections ---

class TestGenerateHighlightedSections:
    def test_returns_list_of_highlighted_sections(self):
        """複数の文からHighlightedSectionのリストを返す"""
        text = "今日は良い天気だ。散歩に行こうと思う。公園が気持ちよさそうだ。"
        result = generate_highlighted_sections(text)
        assert isinstance(result, list)
        assert all(isinstance(s, HighlightedSection) for s in result)

    def test_each_section_has_text_and_probability(self):
        """各セクションにtextとai_probabilityが含まれる"""
        text = "本日は晴れです。気温は20度です。"
        result = generate_highlighted_sections(text)
        for section in result:
            assert isinstance(section.text, str)
            assert len(section.text) > 0
            assert isinstance(section.ai_probability, float)
            assert 0.0 <= section.ai_probability <= 1.0

    def test_number_of_sections_matches_sentences(self):
        """セクション数は文の数と一致する"""
        text = "一文目です。二文目です。三文目です。"
        result = generate_highlighted_sections(text)
        assert len(result) == 3

    def test_empty_text_returns_empty_list(self):
        """空文字は空リストを返す"""
        result = generate_highlighted_sections("")
        assert result == []

    def test_uniform_sentences_have_high_ai_probability(self):
        """文長が均一なAIらしい文章は高いAI確率を持つ"""
        ai_text = (
            "本日は晴れの天気となっています。"
            "気温は20度前後で過ごしやすい一日です。"
            "午後からは雲が増える見込みとなります。"
            "夕方には一時的に雨が降る可能性があります。"
        )
        result = generate_highlighted_sections(ai_text)
        avg_probability = sum(s.ai_probability for s in result) / len(result)
        assert avg_probability >= 0.5

    def test_variable_sentences_have_lower_ai_probability(self):
        """文長にバラつきがある人間らしい文章は低めのAI確率を持つ"""
        human_text = (
            "今日は良い天気だ。"
            "朝から晴れていて、空気もとても澄んでいて気持ちがよかった。散歩した。"
            "公園でベンチに座って、しばらくぼーっとしていた。"
            "鳥が鳴いていた。"
        )
        result = generate_highlighted_sections(human_text)
        avg_probability = sum(s.ai_probability for s in result) / len(result)
        assert avg_probability < 0.7


# --- generate_advice ---

class TestGenerateAdvice:
    @pytest.mark.asyncio
    async def test_returns_non_empty_string(self):
        """アドバイスは空でない文字列を返す"""
        mock_advice = "文の長さにバラつきを持たせましょう。体験談を加えると人間らしくなります。"
        with patch("app.services.highlight.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_advice})()]
                })()
            )
            result = await generate_advice("テスト文章です。", overall_score=80)
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_calls_claude_api_once(self):
        """Claude APIを1回呼び出す"""
        mock_advice = "アドバイスのテキスト"
        with patch("app.services.highlight.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_advice})()]
                })()
            )
            await generate_advice("テスト文章", overall_score=75)
            mock_client.messages.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_low_score_returns_positive_message(self):
        """スコアが低い（人間らしい）場合はポジティブなメッセージを返す"""
        # スコアが低い場合はAPIを呼ばずに固定メッセージ
        result = await generate_advice("テスト文章", overall_score=20)
        assert isinstance(result, str)
        assert len(result) > 0
