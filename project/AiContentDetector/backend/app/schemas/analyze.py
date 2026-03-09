from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    content: str = Field(max_length=5000)


class Breakdown(BaseModel):
    sentence_variability: float
    top_k_overlap: float


class HighlightedSection(BaseModel):
    text: str
    ai_probability: float


class AnalyzeResponse(BaseModel):
    overall_score: int
    statistical_score: int
    similarity_score: int
    breakdown: Breakdown
    highlighted_sections: list[HighlightedSection]
    advice: str = ""
