from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints.analyze import router as analyze_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Multi-Agent ATS Resume Evaluation and Tailoring API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(analyze_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "message": "ATS Resume AI Backend is running.",
        "docs": "/docs",
        "api_v1": settings.API_V1_STR
    }

