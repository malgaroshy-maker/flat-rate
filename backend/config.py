"""Configuration and model routing for dual-mode (online/offline) operation."""

import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)


class Settings:
    # --- API keys ---
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # --- Force local mode (overrides cloud even if key present) ---
    FORCE_LOCAL: bool = os.getenv("FORCE_LOCAL", "").lower() in ("1", "true", "yes")

    # --- Cloud model names ---
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    GEMINI_EMBEDDING_MODEL: str = os.getenv(
        "GEMINI_EMBEDDING_MODEL", "gemini-embedding-2"
    )

    # --- Local LLM backend ---
    # "llamacpp" (OpenAI-compatible on port 8080) or "ollama" (port 11434)
    LOCAL_LLM_BACKEND: str = os.getenv("LOCAL_LLM_BACKEND", "llamacpp")
    LOCAL_LLM_HOST: str = os.getenv("LOCAL_LLM_HOST", "http://localhost:8080")
    LOCAL_LLM_MODEL: str = os.getenv("LOCAL_LLM_MODEL", "gemma-4-e4b-it")

    # --- Local embedding (offline fallback) ---
    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2"
    )
    EMBEDDING_SOURCE: str = os.getenv("EMBEDDING_SOURCE", "gemini")  # "gemini" or "local"
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # --- Paths ---
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(Path(__file__).resolve().parent.parent / "chroma_db"),
    )
    DATA_DIR: str = os.getenv("DATA_DIR", "../")

    @property
    def use_cloud(self) -> bool:
        if self.FORCE_LOCAL:
            return False
        return bool(self.GEMINI_API_KEY)

    def set_force_local(self, value: bool) -> None:
        self.FORCE_LOCAL = value

    @property
    def local_llm_url(self) -> str:
        if self.LOCAL_LLM_BACKEND == "llamacpp":
            return f"{self.LOCAL_LLM_HOST}/v1"
        return self.LOCAL_LLM_HOST


settings = Settings()
