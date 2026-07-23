import logging
import os
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings

# INFO-level logs (chat_engine, query_engine) are silent by default under
# Python's root logger — without this, the only way to see what a request
# actually did in Render's log stream was adding a one-off debug endpoint
# each time, then removing it (see git history: "debug: show actual
# ChromaDB error in health endpoint").
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

_STARTED_AT = datetime.now(timezone.utc).isoformat()
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(query_router)
app.include_router(dictionary_router)
app.include_router(chat_router)


@app.get("/api/version")
async def version():
    """Confirms exactly what's live — Render sets RENDER_GIT_COMMIT
    automatically for git-linked deploys, so this needs no build-time
    injection. Used by the smoke test and, eventually, an in-app update
    check.
    """
    commit = os.getenv("RENDER_GIT_COMMIT", "unknown")
    return {
        "git_commit": commit,
        "git_commit_short": commit[:7] if commit != "unknown" else commit,
        "started_at": _STARTED_AT,
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "mode": "cloud" if settings.use_cloud else "local",
        "local_llm_backend": settings.LOCAL_LLM_BACKEND,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_source": settings.EMBEDDING_SOURCE,
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
