"""LLM router — dispatches to Gemini API (online) or llama-cpp (offline)."""

from __future__ import annotations

import json
from typing import Optional

import httpx

from config import settings


class LLMRouter:
    @property
    def use_cloud(self) -> bool:
        return settings.use_cloud

    @property
    def active_model(self) -> str:
        if self.use_cloud:
            return settings.GEMINI_MODEL
        return settings.LOCAL_LLM_MODEL

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        if self.use_cloud:
            return self._generate_cloud(prompt, system)
        return self._generate_local(prompt, system)

    def _api_key_or_none(self) -> Optional[str]:
        return settings.GEMINI_API_KEY if self.use_cloud else None

    def _base_url(self) -> str:
        return settings.local_llm_url

    def _generate_cloud(self, prompt: str, system: Optional[str] = None) -> str:
        from google import genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        contents = [prompt]
        config = None
        if system:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system
            )
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config,
        )
        return response.text

    def _generate_local(self, prompt: str, system: Optional[str] = None) -> str:
        url = f"{settings.local_llm_url}/chat/completions"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": settings.LOCAL_LLM_MODEL,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024,
        }
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]


llm_router = LLMRouter()
