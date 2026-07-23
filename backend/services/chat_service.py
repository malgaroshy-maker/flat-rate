"""Chat service using the pipeline orchestrator with SSE streaming.

Wraps chat_engine.py streaming as an orchestrated pipeline stage.
"""

from __future__ import annotations

from typing import Any, AsyncIterator

from chat_engine import stream_chat_response


async def chat_with_orchestrator(
    message: str,
    session_id: str,
    lang: str = "ar",
) -> AsyncIterator[dict[str, Any]]:
    async for event in stream_chat_response(message, session_id, lang):
        yield event
