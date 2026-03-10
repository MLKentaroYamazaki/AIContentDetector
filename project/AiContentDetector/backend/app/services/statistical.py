"""統計的アプローチによるAIコンテンツ検出ロジック"""
import re
import math


def _split_sentences(text: str) -> list[str]:
    """句点（。！？）で文を分割する"""
    sentences = re.split(r'[。！？]', text)
    return [s for s in sentences if s.strip()]


def calculate_burstiness(text: str) -> float:
    """文長のバースト性を計算する（0.0〜1.0、高いほど人間らしい）

    バースト性 = 文長の標準偏差 / 文長の平均
    （変動係数: CV）を0〜1にクリップして返す
    """
    if not text.strip():
        return 0.0

    sentences = _split_sentences(text)
    if len(sentences) <= 1:
        return 0.0

    lengths = [float(len(s)) for s in sentences]
    mean = sum(lengths) / len(lengths)
    if mean == 0:
        return 0.0

    variance = sum((x - mean) ** 2 for x in lengths) / len(lengths)
    std = math.sqrt(variance)
    cv = std / mean
    # CV=1.0 を上限1.0にクリップ（人間らしい文章では通常0.5〜1.0程度）
    return float(min(cv, 1.0))


def calculate_punctuation_density(text: str) -> float:
    """読点（、）や句点（。）の密度を計算する（句読点数 / 総文字数）"""
    if not text:
        return 0.0

    punctuation_count = sum(1 for c in text if c in '、。')
    return punctuation_count / len(text)


def calculate_statistical_score(text: str) -> int:
    """統計的スコアを計算する（0〜100、高いほどAIらしい）

    burstinessが低い（均一）ほどAIらしい → スコアが高い
    """
    if not text.strip():
        return 50

    burstiness = calculate_burstiness(text)

    # burstiness が低いほど AI らしい（スコア高）
    # burstiness=0.0 → score=100、burstiness=1.0 → score=0
    raw_score = (1.0 - burstiness) * 100
    return int(round(max(0, min(100, raw_score))))
