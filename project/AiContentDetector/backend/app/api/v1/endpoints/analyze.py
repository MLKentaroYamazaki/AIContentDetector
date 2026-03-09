from fastapi import APIRouter
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, Breakdown, HighlightedSection
from app.services.statistical import (
    calculate_burstiness,
    calculate_punctuation_density,
    calculate_statistical_score,
)

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    text = request.content

    statistical_score = calculate_statistical_score(text)
    burstiness = calculate_burstiness(text)
    punctuation_density = calculate_punctuation_density(text)

    # Phase3実装前は similarity_score をプレースホルダー（-1）とする
    similarity_score = -1

    # overall_score: Phase3実装前は統計スコアのみで算出
    overall_score = statistical_score

    breakdown = Breakdown(
        sentence_variability=round(burstiness, 4),
        top_k_overlap=round(punctuation_density, 4),
    )

    return AnalyzeResponse(
        overall_score=overall_score,
        statistical_score=statistical_score,
        similarity_score=similarity_score,
        breakdown=breakdown,
        highlighted_sections=[],
    )
