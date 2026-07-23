"""Chat engine — RAG search + LLM generation with SSE streaming + multi-turn conversation."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, AsyncGenerator

from embedding_router import embedding_router
from llm_router import llm_router
from query_engine import execute_query
from system_prompt import build_system_prompt, format_rag_context

logger = logging.getLogger("chat_engine")


async def stream_chat_response(
    message: str,
    session_id: str,
    lang: str = "ar",
    history_messages: list[dict] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate a streaming chat response with RAG context and multi-turn history.

    Yields event dicts:
    - {"status": "searching" | "thinking"} — progress markers for the client
      to render before the first model token arrives
    - {"text": "..."} — a chunk of the assistant's reply
    """

    yield {"status": "searching"}

    # 1. Run RAG on every message so follow-ups ("and the rear bumper?") also
    # get fresh matches, not just the first message in a session.
    t0 = time.perf_counter()
    query_result = await asyncio.to_thread(execute_query, message, n_results=5)
    rag_ms = (time.perf_counter() - t0) * 1000
    hits = query_result.get("hits", [])
    matched_terms = query_result.get("matched_terms", [])
    rag_context = format_rag_context(hits, matched_terms, lang)

    top_sim = hits[0]["similarity"] if hits else 0.0
    logger.info(
        "rag_search session=%s hits=%d matched_terms=%d top_similarity=%.3f elapsed_ms=%.1f",
        session_id, len(hits), len(matched_terms), top_sim, rag_ms,
    )

    # 2. Build system prompt
    system = build_system_prompt(lang)

    yield {"status": "thinking"}

    # 3. Build the user message
    if history_messages:
        user_content = f"""{rag_context}Latest message from user: {message}

You are in an ongoing conversation. Use the conversation history above to understand the full scope of the user's request. The user's previous messages and your previous responses contain all the vehicle details, job scope, and estimates already discussed. Do NOT treat this as a new query — this is a follow-up message.

Based on the full conversation context, provide a helpful response. Remember: always give hour ranges (P10-P90), mention record counts, and ask clarifying questions if needed."""
    else:
        user_content = f"""User query: {message}

{rag_context}

Based on the historical data above, provide a useful estimate or answer.
Remember: always give hour ranges (P10-P90), mention record counts,
and ask clarifying questions if needed."""

    # 4. Stream with multi-turn history
    t_llm_start = time.perf_counter()
    first_token_ms: float | None = None
    total_chars = 0
    stream_fn = _stream_cloud_multi if llm_router.use_cloud else _stream_local_multi
    try:
        async for chunk in stream_fn(system, history_messages or [], user_content):
            if first_token_ms is None:
                first_token_ms = (time.perf_counter() - t_llm_start) * 1000
            total_chars += len(chunk)
            yield {"text": chunk}
    finally:
        logger.info(
            "llm_stream session=%s cloud=%s first_token_ms=%s total_ms=%.1f chars=%d",
            session_id, llm_router.use_cloud,
            f"{first_token_ms:.1f}" if first_token_ms is not None else "n/a",
            (time.perf_counter() - t_llm_start) * 1000, total_chars,
        )


async def _stream_cloud_multi(system: str, history: list[dict], user_content: str) -> AsyncGenerator[str, None]:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=llm_router._api_key_or_none())

    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_content)]))

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.3,
    )

    # Use the async client (client.aio) — the sync client.models.generate_content_stream()
    # blocks the event loop while iterating, which serializes it with every other
    # request FastAPI is serving and makes tokens arrive in bursts instead of
    # smoothly. The async client yields control back to the loop between chunks.
    async for chunk in await client.aio.models.generate_content_stream(
        model=llm_router.active_model,
        contents=contents,
        config=config,
    ):
        if chunk.text:
            yield chunk.text


async def _stream_local_multi(system: str, history: list[dict], user_content: str) -> AsyncGenerator[str, None]:
    import httpx

    messages = [{"role": "system", "content": system}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_content})

    url = f"{llm_router._base_url()}/chat/completions"
    payload = {
        "model": llm_router.active_model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024,
        "stream": True,
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("POST", url, json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except Exception:
                        pass
