"""Chat API routes with SSE streaming."""

from __future__ import annotations

import asyncio
import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from chat_engine import stream_chat_response
from chat_store import (
    add_message,
    create_session,
    delete_session,
    get_messages,
    get_session,
    list_sessions,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/sessions")
async def get_sessions():
    return {"sessions": list_sessions()}


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    s = get_session(session_id)
    if s is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    ok = delete_session(session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "deleted"}


@router.post("/send")
async def send_message(
    request: Request,
    message: str = Query(..., description="User message text"),
    session_id: Optional[str] = Query(None, description="Existing session ID"),
    lang: str = Query("ar", description="Language (ar/en)"),
):
    # Create or resume session
    if session_id:
        s = get_session(session_id)
        if s is None:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        s = create_session(lang=lang)
        session_id = s["id"]

    # Save user message
    add_message(session_id, "user", message)

    # Get conversation history as structured messages
    history = get_messages(session_id)
    history_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in history[:-1]  # exclude the just-saved user message
    ]

    async def event_stream():
        full_response = ""

        yield f"data: {json.dumps({'session_id': session_id, 'lang': lang})}\n\n"

        try:
            async for chunk in stream_chat_response(message, session_id, lang, history_messages):
                full_response += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0)  # yield control

            # Save assistant response
            add_message(session_id, "assistant", full_response)
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            error_msg = f"Error: {e}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            add_message(session_id, "assistant", error_msg)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
