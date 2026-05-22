"""Embedding router — Gemini Embedding 2 (primary) with local ST fallback.

Auto-detects corpus embedding model from ChromaDB metadata to avoid vector space mismatch.
"""

from __future__ import annotations

from config import settings


class EmbeddingRouter:
    def __init__(self) -> None:
        self._local_model = None
        self._corpus_model: str | None = None

    @property
    def use_cloud(self) -> bool:
        if not bool(settings.GEMINI_API_KEY):
            return False
        if settings.EMBEDDING_SOURCE != "gemini":
            return False
        return True  # trust EMBEDDING_SOURCE explicitly

    @property
    def active_model_name(self) -> str:
        if self.use_cloud:
            return settings.GEMINI_EMBEDDING_MODEL
        return self._detect_corpus_model() or settings.EMBEDDING_MODEL

    def _detect_corpus_model(self) -> str | None:
        if self._corpus_model is not None:
            return self._corpus_model if self._corpus_model else None
        try:
            from vector_store import get_or_create_collection
            col = get_or_create_collection()
            meta = col.metadata or {}
            val = meta.get("embedding_model", "")
            self._corpus_model = val if val else None
        except Exception:
            self._corpus_model = None
        return self._corpus_model

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Embed texts. Uses cloud Gemini if API key set + EMBEDDING_SOURCE=gemini.
        Only falls back to local when EMBEDDING_SOURCE != 'gemini'."""
        if self.use_cloud:
            return self._encode_cloud(texts)
        return self._encode_local(texts)

    def encode_single(self, text: str) -> list[float]:
        return self.encode([text])[0]

    def encode_cloud(self, texts: list[str]) -> list[list[float]]:
        return self._encode_cloud(texts)

    def _encode_local(self, texts: list[str]) -> list[list[float]]:
        import os

        os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
        if settings.HF_TOKEN:
            os.environ.setdefault("HF_TOKEN", settings.HF_TOKEN)

        from sentence_transformers import SentenceTransformer

        model_name = self._detect_corpus_model() or settings.EMBEDDING_MODEL
        if self._local_model is None:
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message=".*unauthenticated.*")
                self._local_model = SentenceTransformer(model_name)
        return self._local_model.encode(texts, show_progress_bar=False).tolist()

    def _encode_cloud(self, texts: list[str]) -> list[list[float]]:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        results: list[list[float]] = []
        # Batch 20 texts per API call to avoid rate limits
        batch_size = 20
        import time
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                result = client.models.embed_content(
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    contents=text,
                    config=types.EmbedContentConfig(output_dimensionality=384),
                )
                if result.embeddings:
                    results.append(list(result.embeddings[0].values))
                else:
                    results.append([0.0] * 384)
            if i + batch_size < len(texts):
                time.sleep(1)  # respect rate limits
        return results


embedding_router = EmbeddingRouter()

