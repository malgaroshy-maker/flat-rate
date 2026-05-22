"""Chat engine — RAG search + LLM generation with SSE streaming + multi-turn conversation."""

from __future__ import annotations

import json
from typing import AsyncGenerator

from embedding_router import embedding_router
from llm_router import llm_router
from query_engine import execute_query
from system_prompt import build_system_prompt, format_rag_context


async def stream_chat_response(
    message: str,
    session_id: str,
    lang: str = "ar",
    history_messages: list[dict] | None = None,
) -> AsyncGenerator[str, None]:
    """Generate a streaming chat response with RAG context and multi-turn history."""

    # 1. Run RAG if no meaningful conversation history (0-1 messages = first query)
    hits = []
    if not history_messages or len(history_messages) <= 1:
        query_result = execute_query(message, n_results=5)
        hits = query_result.get("hits", [])
    rag_context = format_rag_context(hits)

    # 2. Build system prompt
    system = build_system_prompt(lang)

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
    if llm_router.use_cloud:
        async for chunk in _stream_cloud_multi(system, history_messages or [], user_content):
            yield chunk
    else:
        async for chunk in _stream_local_multi(system, history_messages or [], user_content):
            yield chunk


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

    response = client.models.generate_content_stream(
        model=llm_router.active_model,
        contents=contents,
        config=config,
    )

    for chunk in response:
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
