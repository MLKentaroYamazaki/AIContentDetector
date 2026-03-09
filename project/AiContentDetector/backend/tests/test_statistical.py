"""統計的分析ロジックのユニットテスト"""
import pytest
from app.services.statistical import (
    calculate_burstiness,
    calculate_punctuation_density,
    calculate_statistical_score,
)


# --- calculate_burstiness ---

class TestCalculateBurstiness:
    def test_human_like_text_has_high_burstiness(self):
        """短い文と長い文が混在する人間らしいテキストは高いバースト性を持つ"""
        human_text = (
            "今日は良い天気だ。"
            "朝から晴れていて、空気もとても澄んでいて気持ちがよかった。散歩した。"
            "公園でベンチに座って、しばらくぼーっとしていた。"
            "鳥が鳴いていた。"
        )
        score = calculate_burstiness(human_text)
        assert score >= 0.5, f"人間らしいテキストのburstinessは0.5以上を期待: {score}"

    def test_ai_like_text_has_low_burstiness(self):
        """文長が均一なAIらしいテキストは低いバースト性を持つ"""
        ai_text = (
            "本日は晴れの天気となっています。"
            "気温は20度前後で過ごしやすい一日です。"
            "午後からは雲が増える見込みとなります。"
            "夕方には一時的に雨が降る可能性があります。"
        )
        score = calculate_burstiness(ai_text)
        assert score < 0.5, f"AIらしいテキストのburstinessは0.5未満を期待: {score}"

    def test_single_sentence_returns_zero(self):
        """文が1つしかない場合はバースト性なし（0.0）"""
        score = calculate_burstiness("これは一文だけのテキストです。")
        assert score == 0.0

    def test_empty_text_returns_zero(self):
        """空文字はバースト性なし（0.0）"""
        score = calculate_burstiness("")
        assert score == 0.0

    def test_return_value_is_between_0_and_1(self):
        """戻り値は0.0〜1.0の範囲内"""
        text = "短い。少し長めの文章がここにある。とても長い文章はこのようにたくさんの単語を含んでいることが多い。"
        score = calculate_burstiness(text)
        assert 0.0 <= score <= 1.0


# --- calculate_punctuation_density ---

class TestCalculatePunctuationDensity:
    def test_text_with_many_punctuation_has_high_density(self):
        """読点・句点が多いテキストは高い密度を持つ"""
        text = "今日は、晴れていて、気持ちがよく、散歩した。公園では、花が咲いていて、とても綺麗だった。"
        score = calculate_punctuation_density(text)
        assert score >= 0.05, f"読点の多いテキストのdensityは0.05以上を期待: {score}"

    def test_text_with_no_punctuation_has_zero_density(self):
        """句読点がまったくないテキストは密度0"""
        text = "これは句読点のないテキストです"
        score = calculate_punctuation_density(text)
        assert score == 0.0

    def test_empty_text_returns_zero(self):
        """空文字は密度0"""
        score = calculate_punctuation_density("")
        assert score == 0.0

    def test_return_value_is_non_negative(self):
        """戻り値は0以上"""
        text = "普通の文章。読点もある、文です。"
        score = calculate_punctuation_density(text)
        assert score >= 0.0


# --- calculate_statistical_score ---

class TestCalculateStatisticalScore:
    def test_ai_like_text_has_high_score(self):
        """AIらしい均一な文章は高いスコア（AIらしさ）を返す"""
        ai_text = (
            "本日は晴れの天気となっています。"
            "気温は20度前後で過ごしやすい一日です。"
            "午後からは雲が増える見込みとなります。"
            "夕方には一時的に雨が降る可能性があります。"
        )
        score = calculate_statistical_score(ai_text)
        assert score >= 50, f"AIらしいテキストのスコアは50以上を期待: {score}"

    def test_human_like_text_has_low_score(self):
        """人間らしいバラつきのある文章は低いスコアを返す"""
        human_text = (
            "今日は良い天気だ。"
            "朝から晴れていて、空気もとても澄んでいて気持ちがよかった。散歩した。"
            "公園でベンチに座って、しばらくぼーっとしていた。"
            "鳥が鳴いていた。"
        )
        score = calculate_statistical_score(human_text)
        assert score < 50, f"人間らしいテキストのスコアは50未満を期待: {score}"

    def test_return_value_is_integer_between_0_and_100(self):
        """戻り値は0〜100の整数"""
        text = "テストテキストです。普通の文章を使います。"
        score = calculate_statistical_score(text)
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_empty_text_returns_50(self):
        """空文字は判定不能として中間値（50）を返す"""
        score = calculate_statistical_score("")
        assert score == 50
