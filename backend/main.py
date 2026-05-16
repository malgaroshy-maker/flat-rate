from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from middleware.input_sanitizer import InputSanitizerMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from routers.dictionary import router as dictionary_router
from routers.query import router as query_router
from routers.chat import router as chat_router

app = FastAPI(title="Smart Labor Cost Estimator API")

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(InputSanitizerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(query_router)
app.include_router(dictionary_router)
app.include_router(chat_router)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mode": "cloud" if settings.use_cloud else "local",
        "local_llm_backend": settings.LOCAL_LLM_BACKEND,
        "embedding_model": settings.EMBEDDING_MODEL,
        "force_local": settings.FORCE_LOCAL,
    }


class ModeToggle(BaseModel):
    force_local: bool


@app.post("/api/settings/mode")
async def set_mode(body: ModeToggle):
    settings.set_force_local(body.force_local)
    return {
        "mode": "cloud" if settings.use_cloud else "local",
        "force_local": settings.FORCE_LOCAL,
    }
