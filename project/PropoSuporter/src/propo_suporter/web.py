"""FastAPI Webアプリケーション"""
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .main import PropoSuporter, _build_llm_client, _make_organizer_with_model, _make_generator_with_model
from .requirement_organizer import RequirementOrganizer
from .proposal_generator import ProposalGenerator


class RunRequest(BaseModel):
    raw_notes: str


class CheckIssueResponse(BaseModel):
    category: str
    description: str


class CheckResultResponse(BaseModel):
    is_ok: bool
    issues: list[CheckIssueResponse]


class RequirementsResponse(BaseModel):
    background: str
    issues: str
    requests: str


class ProposalResponse(BaseModel):
    proposal_points: list[str]
    development_policy: str


class RunResponse(BaseModel):
    requirements: RequirementsResponse
    proposal: ProposalResponse
    check: CheckResultResponse


def _build_app_instance() -> PropoSuporter:
    """環境変数 LLM_BACKEND に応じたPropoSuporterを生成する"""
    client = _build_llm_client()
    backend = os.getenv("LLM_BACKEND", "anthropic").lower()
    if backend in ("groq", "ollama"):
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant") if backend == "groq" \
            else os.getenv("OLLAMA_MODEL", "llama3.2")
        return PropoSuporter(
            organizer=_make_organizer_with_model(client, model),
            generator=_make_generator_with_model(client, model),
        )
    return PropoSuporter(
        organizer=RequirementOrganizer(client=client),
        generator=ProposalGenerator(client=client),
    )


def create_app(app_instance: Optional[PropoSuporter] = None) -> FastAPI:
    app = FastAPI(title="PropoSuporter API")
    _app_instance = app_instance or _build_app_instance()

    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index():
        html_path = static_dir / "index.html"
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    @app.post("/api/run", response_model=RunResponse)
    async def run(request: RunRequest):
        if not request.raw_notes.strip():
            raise HTTPException(status_code=422, detail="ヒアリングメモが空です")
        try:
            result = _app_instance.run(request.raw_notes)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"処理中にエラーが発生しました: {str(e)}")

        req = result["requirements"]
        prop = result["proposal"]
        check = result["check"]

        return RunResponse(
            requirements=RequirementsResponse(
                background=req.background,
                issues=req.issues,
                requests=req.requests,
            ),
            proposal=ProposalResponse(
                proposal_points=prop.proposal_points,
                development_policy=prop.development_policy,
            ),
            check=CheckResultResponse(
                is_ok=check.is_ok,
                issues=[
                    CheckIssueResponse(category=i.category, description=i.description)
                    for i in check.issues
                ],
            ),
        )

    return app


def main() -> None:
    import uvicorn
    from dotenv import load_dotenv
    load_dotenv()
    app = create_app()
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
