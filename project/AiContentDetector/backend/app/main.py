from fastapi import FastAPI
from app.api.v1.endpoints.analyze import router as analyze_router

app = FastAPI(title="AI Content Detector API")

app.include_router(analyze_router, prefix="/api/v1")
