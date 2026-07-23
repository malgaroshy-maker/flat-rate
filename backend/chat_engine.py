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


class GeminiKeyError(Exception):
    """Raised when the active Gemini key can't serve the request — invalid,
    revoked, or out of quota (all surface as 4xx from the API). Distinct
    from a 5xx ServerError (Gemini's own outage), where a different key
    wouldn't help, so that stays a generic error."""


# Embedding similarity below this is not a real match — it's just whatever
# ChromaDB's nearest-neighbor search returns for *any* query, including
# greetings and small talk. Calibrated against real traffic: genuine labor
# queries score ~0.80-0.83, greetings/small-talk score ~0.60-0.66. Below
# this, the hits are noise and must not be fed to the model as if they were
# candidate matches — the model would otherwise dutifully apply the
# "always cite record counts and ranges" rule to irrelevant records.
RELEVANCE_THRESHOLD = 0.72


async def stream_chat_response(
    message: str,
    session_id: str,
    lang: str = "ar",
    history_messages: list[dict] | None = None,
    user_api_key: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Generate a streaming chat response with RAG context and multi-turn history.

    Yields event dicts:
    - {"status": "searching" | "thinking"} — progress markers for the client
      to render before the first model token arrives
    - {"text": "..."} — a chunk of the assistant's reply
    - {"error_type": "gemini_key_error"} — the active key (shared, or the
      caller's own if `user_api_key` was passed) is invalid or out of
      quota. The client can retry with a personal key it has saved, or
      prompt the user to provide one — see routers/chat.py.

    `user_api_key`: an optional caller-supplied Gemini key, used instead of
    the server's shared one for this request only. Never logged or stored.
    """

    yield {"status": "searching"}

    # 1. Run RAG on every message so follow-ups ("and the rear bumper?") also
    # get fresh matches, not just the first message in a session.
    t0 = time.perf_counter()
    query_result = await asyncio.to_thread(execute_query, message, n_results=5)
    rag_ms = (time.perf_counter() - t0) * 1000
    hits = query_result.get("hits", [])
    matched_terms = query_result.get("matched_terms", [])

    top_sim = hits[0]["similarity"] if hits else 0.0
    # A dictionary term match (exact substring, not embedding distance) is a
    # stronger relevance signal than a mediocre embedding score — keep the
    # hits if either condition holds so a real but rare operation isn't
    # dropped just because the embedding search alone came in under threshold.
    is_relevant = top_sim >= RELEVANCE_THRESHOLD or bool(matched_terms)
    relevant_hits = hits if is_relevant else []
    rag_context = format_rag_context(relevant_hits, matched_terms, lang)

    logger.info(
        "rag_search session=%s hits=%d relevant=%s matched_terms=%d top_similarity=%.3f elapsed_ms=%.1f",
        session_id, len(hits), is_relevant, len(matched_terms), top_sim, rag_ms,
    )

    # 2. Build system prompt
    system = build_system_prompt(lang)

    yield {"status": "thinking"}

    # 3. Build the user message. The estimation rules (ranges, record counts,
    # the emoji-sectioned format) only apply when this is actually a labor/
    # maintenance question — retrieved_relevant tells the model whether the
    # RAG context below is real candidate data or genuinely irrelevant, so it
    # doesn't force-fit the data-analysis persona onto a greeting.
    if not is_relevant:
        retrieval_note = (
            "No relevant historical labor data was found for this message — "
            "it does not appear to describe a specific maintenance/repair job."
        )
    else:
        retrieval_note = "Relevant historical labor data was found below."

    if history_messages:
        user_content = f"""{rag_context}Latest message from user: {message}

{retrieval_note}

You are in an ongoing conversation. Use the conversation history above to understand the full scope of the user's request — the user's previous messages and your previous responses contain any vehicle details, job scope, and estimates already discussed. Do NOT treat this as a new query if it's a follow-up.

If this message (in light of the conversation) is asking for a labor estimate, follow the estimation rules: hour ranges, record counts, ask clarifying questions if needed. If it's a greeting, thanks, or general conversation, just respond naturally and briefly — do not mention records, ranges, or data at all."""
    else:
        user_content = f"""User message: {message}

{rag_context}

{retrieval_note}

If this is a labor/maintenance estimate question, use the historical data above and follow the estimation rules: hour ranges (P10-P90), record counts, ask clarifying questions if needed. If it's a greeting, thanks, or general conversation unrelated to car maintenance, just respond naturally and briefly in the same language — do not mention records, ranges, or data at all."""

    # 4. Stream with multi-turn history
    t_llm_start = time.perf_counter()
    first_token_ms: float | None = None
    total_chars = 0
    key_error = False
    try:
        if llm_router.use_cloud:
            stream = _stream_cloud_multi(system, history_messages or [], user_content, api_key_override=user_api_key)
        else:
            stream = _stream_local_multi(system, history_messages or [], user_content)
        async for chunk in stream:
            if first_token_ms is None:
                first_token_ms = (time.perf_counter() - t_llm_start) * 1000
            total_chars += len(chunk)
            yield {"text": chunk}
    except GeminiKeyError as e:
        key_error = True
        logger.warning(
            "gemini_key_error session=%s used_user_key=%s: %s",
            session_id, bool(user_api_key), e,
        )
        yield {"error_type": "gemini_key_error"}
    finally:
        logger.info(
            "llm_stream session=%s cloud=%s first_token_ms=%s total_ms=%.1f chars=%d key_error=%s",
            session_id, llm_router.use_cloud,
            f"{first_token_ms:.1f}" if first_token_ms is not None else "n/a",
            (time.perf_counter() - t_llm_start) * 1000, total_chars, key_error,
        )


async def _stream_cloud_multi(
    system: str, history: list[dict], user_content: str, api_key_override: str | None = None
) -> AsyncGenerator[str, None]:
    from google import genai
    from google.genai import errors as genai_errors
    from google.genai import types

    client = genai.Client(api_key=api_key_override or llm_router._api_key_or_none())

    contents = []
    for m in history:
        role = "user" if m["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_content)]))

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=0.3,
    )

    try:
        # Use the async client (client.aio) — the sync client.models.generate_content_stream()
        # blocks the event loop while iterating, which serializes it with every other
        # request FastAPI is serving and makes tokens arrive in bursts instead of
        # smoothly. The async client yields control back to the loop between chunks.
        stream = await client.aio.models.generate_content_stream(
            model=llm_router.active_model,
            contents=contents,
            config=config,
        )
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
    except genai_errors.ClientError as e:
        # 4xx: invalid/revoked key or quota exhausted — a different key can
        # resolve this. genai_errors.ServerError (5xx, Gemini's own outage)
        # is intentionally NOT caught here and propagates as a generic error.
        raise GeminiKeyError(str(e)) from e


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
