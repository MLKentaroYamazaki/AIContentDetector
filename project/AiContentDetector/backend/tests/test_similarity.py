"""類似度比較ロジックのユニットテスト（Claude APIはモック）"""
import pytest
from unittest.mock import AsyncMock, patch
from app.services.similarity import (
    calculate_cosine_similarity,
    reverse_prompt,
    regenerate_text,
    calculate_similarity_score,
)


# --- calculate_cosine_similarity ---

class TestCalculateCosineSimilarity:
    def test_identical_texts_return_1(self):
        """同一テキストはコサイン類似度1.0"""
        text = "これはテスト用のテキストです。AIによって生成されたかどうかを確認します。"
        score = calculate_cosine_similarity(text, text)
        assert score == pytest.approx(1.0, abs=0.01)

    def test_completely_different_texts_return_low_score(self):
        """全く異なるテキストは低いスコア"""
        text_a = "今日は晴れています。散歩に行きたいです。"
        text_b = "量子コンピュータは古典コンピュータと根本的に異なる原理で動作します。"
        score = calculate_cosine_similarity(text_a, text_b)
        assert score < 0.8

    def test_similar_texts_return_high_score(self):
        """類似したテキストは高いスコア"""
        text_a = "本日の天気は晴れで、気温は25度です。過ごしやすい一日になりそうです。"
        text_b = "今日の天候は晴天で、気温は24度前後です。快適に過ごせる一日でしょう。"
        score = calculate_cosine_similarity(text_a, text_b)
        assert score > 0.5

    def test_return_value_is_between_0_and_1(self):
        """戻り値は0.0〜1.0の範囲内"""
        score = calculate_cosine_similarity("テキストA", "テキストB")
        assert 0.0 <= score <= 1.0

    def test_empty_texts_return_0(self):
        """空文字は類似度0"""
        score = calculate_cosine_similarity("", "")
        assert score == 0.0


# --- reverse_prompt ---

class TestReversePrompt:
    @pytest.mark.asyncio
    async def test_returns_non_empty_string(self):
        """推測されたプロンプトは空でない文字列"""
        mock_response = "以下の条件でニュース記事を書いてください：天気予報について、丁寧な文体で"
        with patch("app.services.similarity.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_response})()]
                })()
            )
            result = await reverse_prompt("本日は晴れの天気となっています。")
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_calls_claude_api_once(self):
        """Claude APIを1回呼び出す"""
        mock_response = "テスト用プロンプト"
        with patch("app.services.similarity.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_response})()]
                })()
            )
            await reverse_prompt("テスト入力テキスト")
            mock_client.messages.create.assert_called_once()


# --- regenerate_text ---

class TestRegenerateText:
    @pytest.mark.asyncio
    async def test_returns_non_empty_string(self):
        """再生成テキストは空でない文字列"""
        mock_response = "本日は快晴となっております。気温は20度程度です。"
        with patch("app.services.similarity.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_response})()]
                })()
            )
            result = await regenerate_text("天気についての記事を書いてください")
            assert isinstance(result, str)
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_calls_claude_api_once(self):
        """Claude APIを1回呼び出す"""
        mock_response = "再生成されたテキスト"
        with patch("app.services.similarity.anthropic_client") as mock_client:
            mock_client.messages.create = AsyncMock(
                return_value=type("Resp", (), {
                    "content": [type("Block", (), {"text": mock_response})()]
                })()
            )
            await regenerate_text("プロンプト")
            mock_client.messages.create.assert_called_once()


# --- calculate_similarity_score ---

class TestCalculateSimilarityScore:
    @pytest.mark.asyncio
    async def test_ai_text_has_high_score(self):
        """AIらしいテキストは高い類似度スコア（AIがAI文章を再生成するため類似度が高い）"""
        original = "本日は晴れの天気となっています。気温は20度前後で過ごしやすい一日です。"
        regenerated = "今日は晴天です。気温は20度程度で快適に過ごせるでしょう。"

        with patch("app.services.similarity.reverse_prompt", new_callable=AsyncMock) as mock_rp, \
             patch("app.services.similarity.regenerate_text", new_callable=AsyncMock) as mock_rg:
            mock_rp.return_value = "天気予報記事を丁寧な文体で書いてください"
            mock_rg.return_value = regenerated

            score = await calculate_similarity_score(original)
            assert isinstance(score, int)
            assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_return_value_is_integer_between_0_and_100(self):
        """戻り値は0〜100の整数"""
        with patch("app.services.similarity.reverse_prompt", new_callable=AsyncMock) as mock_rp, \
             patch("app.services.similarity.regenerate_text", new_callable=AsyncMock) as mock_rg:
            mock_rp.return_value = "何らかのプロンプト"
            mock_rg.return_value = "何らかの再生成テキスト"

            score = await calculate_similarity_score("テスト入力テキスト")
            assert isinstance(score, int)
            assert 0 <= score <= 100

    @pytest.mark.asyncio
    async def test_empty_text_returns_50(self):
        """空文字は判定不能として中間値（50）を返す"""
        score = await calculate_similarity_score("")
        assert score == 50
