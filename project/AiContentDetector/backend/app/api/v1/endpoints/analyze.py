from fastapi import APIRouter
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, Breakdown
from app.services.statistical import (
    calculate_burstiness,
    calculate_punctuation_density,
    calculate_statistical_score,
)
from app.services.similarity import calculate_similarity_score
from app.services.highlight import generate_highlighted_sections, generate_advice

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    text = request.content

    statistical_score = calculate_statistical_score(text)
    burstiness = calculate_burstiness(text)
    punctuation_density = calculate_punctuation_density(text)
    similarity_score = await calculate_similarity_score(text)

    # overall_score: 統計スコア40% + 類似度スコア60%
    if similarity_score == 50 and not text.strip():
        overall_score = 50
    else:
        overall_score = int(round(statistical_score * 0.4 + similarity_score * 0.6))

    breakdown = Breakdown(
        sentence_variability=round(burstiness, 4),
        top_k_overlap=round(punctuation_density, 4),
    )
    highlighted_sections = generate_highlighted_sections(text)
    advice = await generate_advice(text, overall_score)

    return AnalyzeResponse(
        overall_score=overall_score,
        statistical_score=statistical_score,
        similarity_score=similarity_score,
        breakdown=breakdown,
        highlighted_sections=highlighted_sections,
        advice=advice,
    )
