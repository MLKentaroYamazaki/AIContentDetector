"""テキストハイライトとアドバイス生成ロジック"""
import re
import numpy as np
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
    mean = float(np.mean(all_lengths))
    std = float(np.std(all_lengths)) if len(all_lengths) > 1 else 1.0
    if std == 0:
        return 0.8  # 全文の長さが同じ = AIらしい
    z = abs(len(sentence) - mean) / std
    # z が小さい（平均的な長さ）ほど AI らしい → 確率高
    probability = float(np.clip(1.0 - (z / 3.0), 0.0, 1.0))
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
    """Claude APIを使って人間らしく修正するためのアドバイスを生成する"""
    if overall_score < 50:
        return _LOW_SCORE_MESSAGE

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
