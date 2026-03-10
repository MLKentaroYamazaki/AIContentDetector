"""Claude APIを使った類似度比較ロジック"""
import re
import math
from collections import Counter
import anthropic
from app.core.config import settings

anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-haiku-4-5-20251001"


def _tokenize_japanese(text: str) -> list[str]:
    """日本語テキストを文字bigramに分割してリストで返す"""
    cleaned = re.sub(r'[\s\u3000]', '', text)
    if len(cleaned) < 2:
        return list(cleaned)
    return [cleaned[i:i+2] for i in range(len(cleaned) - 1)]


def calculate_cosine_similarity(text_a: str, text_b: str) -> float:
    """2つのテキスト間のコサイン類似度を計算する（0.0〜1.0）"""
    if not text_a.strip() and not text_b.strip():
        return 0.0

    tokens_a = _tokenize_japanese(text_a)
    tokens_b = _tokenize_japanese(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    # TF-IDF（簡易版: 2文書なのでIDFはスキップしTFのみでコサイン類似度を計算）
    freq_a = Counter(tokens_a)
    freq_b = Counter(tokens_b)
    vocab = set(freq_a) | set(freq_b)

    vec_a = [freq_a.get(t, 0) / len(tokens_a) for t in vocab]
    vec_b = [freq_b.get(t, 0) / len(tokens_b) for t in vocab]

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return min(1.0, max(0.0, dot / (norm_a * norm_b)))


async def reverse_prompt(text: str) -> str:
    """テキストからプロンプト（指示書）を推測する"""
    response = await anthropic_client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[
            {
                "role": "user",
                "content": (
                    "以下のテキストを生成するために使われたと考えられる指示文（プロンプト）を"
                    "日本語で簡潔に1〜3文で推測してください。指示文のみを返してください。\n\n"
                    f"テキスト:\n{text}"
                ),
            }
        ],
    )
    return response.content[0].text


async def regenerate_text(prompt: str) -> str:
    """推測されたプロンプトをもとにテキストを再生成する"""
    response = await anthropic_client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    return response.content[0].text


async def calculate_similarity_score(text: str) -> int:
    """類似度スコアを計算する（0〜100、高いほどAIらしい）
    Claude APIが利用できない場合は -1 を返す。
    """
    if not text.strip():
        return 50

    try:
        inferred_prompt = await reverse_prompt(text)
        regenerated = await regenerate_text(inferred_prompt)
        similarity = calculate_cosine_similarity(text, regenerated)
        return int(round(similarity * 100))
    except anthropic.BadRequestError:
        return -1
    except anthropic.APIStatusError:
        return -1
