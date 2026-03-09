"""Claude APIを使った類似度比較ロジック"""


async def reverse_prompt(text: str) -> str:
    """テキストからプロンプト（指示書）を推測する"""
    raise NotImplementedError


async def regenerate_text(prompt: str) -> str:
    """推測されたプロンプトをもとにテキストを再生成する"""
    raise NotImplementedError


def calculate_cosine_similarity(text_a: str, text_b: str) -> float:
    """2つのテキスト間のコサイン類似度を計算する（0.0〜1.0）"""
    raise NotImplementedError


async def calculate_similarity_score(text: str) -> int:
    """類似度スコアを計算する（0〜100、高いほどAIらしい）"""
    raise NotImplementedError
