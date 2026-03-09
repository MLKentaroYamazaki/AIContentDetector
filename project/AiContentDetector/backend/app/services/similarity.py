"""Claude APIを使った類似度比較ロジック"""
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
import anthropic
from app.core.config import settings

anthropic_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-haiku-4-5-20251001"


def _tokenize_japanese(text: str) -> str:
    """日本語テキストを文字bigramに分割してスペース区切りで返す"""
    cleaned = re.sub(r'[\s\u3000]', '', text)
    if len(cleaned) < 2:
        return cleaned
    bigrams = [cleaned[i:i+2] for i in range(len(cleaned) - 1)]
    return " ".join(bigrams)


def calculate_cosine_similarity(text_a: str, text_b: str) -> float:
    """2つのテキスト間のコサイン類似度を計算する（0.0〜1.0）"""
    if not text_a.strip() and not text_b.strip():
        return 0.0

    tokenized_a = _tokenize_japanese(text_a)
    tokenized_b = _tokenize_japanese(text_b)

    if not tokenized_a or not tokenized_b:
        return 0.0

    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([tokenized_a, tokenized_b])
    except ValueError:
        return 0.0

    similarity = sklearn_cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
    return float(np.clip(similarity[0][0], 0.0, 1.0))


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
