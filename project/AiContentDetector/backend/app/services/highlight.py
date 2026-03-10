"""テキストハイライトとアドバイス生成ロジック"""
import re
import math
import anthropic
from app.core.config import settings
from app.schemas.analyze import HighlightedSection

anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-haiku-4-5-20251001"

_LOW_SCORE_MESSAGE = (
    "このテキストは人間らしい特徴を十分に持っています。そのまま使用できます。"
)


def _split_sentences(text: str) -> list[str]:
    sentences = re.split(r'(?<=[。！？])', text)
    return [s for s in sentences if s.strip()]


def _sentence_ai_probability(sentence: str, all_lengths: list[float]) -> float:
    """文の長さが全文の平均に近いほどAIらしい（確率が高い）"""
    if not all_lengths:
        return 0.5
    mean = sum(all_lengths) / len(all_lengths)
    if len(all_lengths) > 1:
        variance = sum((x - mean) ** 2 for x in all_lengths) / len(all_lengths)
        std = math.sqrt(variance)
    else:
        std = 1.0
    if std == 0:
        return 0.8  # 全文の長さが同じ = AIらしい
    z = abs(len(sentence) - mean) / std
    # z が小さい（平均的な長さ）ほど AI らしい → 確率高
    probability = min(1.0, max(0.0, 1.0 - (z / 3.0)))
    return round(probability, 4)


def generate_highlighted_sections(text: str) -> list[HighlightedSection]:
    """各文にAI確率を付与したハイライトセクションを返す"""
    if not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    all_lengths = [float(len(s)) for s in sentences]

    return [
        HighlightedSection(
            text=sentence,
            ai_probability=_sentence_ai_probability(sentence, all_lengths),
        )
        for sentence in sentences
    ]


async def generate_advice(text: str, overall_score: int) -> str:
    """Claude APIを使って人間らしく修正するためのアドバイスを生成する。
    Claude APIが利用できない場合はスコアに基づいた固定アドバイスを返す。
    """
    if overall_score < 50:
        return _LOW_SCORE_MESSAGE

    try:
        response = await anthropic_client.messages.create(
            model=MODEL,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"以下のテキストはAIが生成した可能性が高いと判定されました（AI確信度: {overall_score}%）。\n"
                        "このテキストをより人間らしく自然に修正するための具体的なアドバイスを、"
                        "箇条書き3点以内で日本語で答えてください。アドバイスのみを返してください。\n\n"
                        f"テキスト:\n{text}"
                    ),
                }
            ],
        )
        return response.content[0].text
    except anthropic.BadRequestError:
        return _fallback_advice(overall_score)
    except anthropic.APIStatusError:
        return _fallback_advice(overall_score)


def _fallback_advice(overall_score: int) -> str:
    """Claude API利用不可時のフォールバックアドバイス"""
    if overall_score >= 75:
        return (
            "・文の長さにバラつきを持たせましょう。短い文と長い文を意図的に混ぜてみてください。\n"
            "・体験談や感情表現を加えると、より人間らしい文章になります。\n"
            "・「〜となっています」「〜の見込みです」などの定型表現を言い換えてみましょう。"
        )
    return (
        "・一部の表現を口語的に書き直すと、より自然な印象になります。\n"
        "・接続詞を使いすぎている場合は、文を分割してみましょう。"
    )
