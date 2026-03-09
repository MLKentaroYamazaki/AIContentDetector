"""テキストハイライトとアドバイス生成ロジック"""
from app.schemas.analyze import HighlightedSection


def generate_highlighted_sections(text: str) -> list[HighlightedSection]:
    """各文にAI確率を付与したハイライトセクションを返す"""
    raise NotImplementedError


async def generate_advice(text: str, overall_score: int) -> str:
    """Claude APIを使って人間らしく修正するためのアドバイスを生成する"""
    raise NotImplementedError
