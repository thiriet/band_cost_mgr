from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuration CORS stricte pour autoriser la SPA (Vue/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": f"Bienvenue sur l'API {settings.PROJECT_NAME}", "status": "online"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.4",
        "openrouter_configured": bool(settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY.strip()),
        "openrouter_model": settings.OPENROUTER_MODEL,
        "gemini_configured": bool(settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip())
    }

from app.api.api import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
