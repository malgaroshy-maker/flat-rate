"""Chat API routes with SSE streaming — supports stateless mode via client-provided history."""

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
    create_session_with_id,
    delete_session,
    get_messages,
    get_session,
    list_sessions,
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _safe_add_message(session_id: str, role: str, content: str) -> None:
    try:
        add_message(session_id, role, content)
    except Exception:
        pass


@router.get("/sessions")
async def get_sessions():
    try:
        return {"sessions": list_sessions()}
    except Exception:
        return {"sessions": []}


@router.get("/sessions/{session_id}")
async def get_session_detail(session_id: str):
    try:
        s = get_session(session_id)
        if s is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return s
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Session not found")


@router.delete("/sessions/{session_id}")
async def delete_session_endpoint(session_id: str):
    try:
        ok = delete_session(session_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception:
        pass
    return {"status": "deleted"}


@router.post("/send")
async def send_message(
    request: Request,
    message: str = Query(..., description="User message text"),
    session_id: Optional[str] = Query(None, description="Existing session ID"),
    lang: str = Query("ar", description="Language (ar/en)"),
    history: Optional[str] = Query(None, description="JSON-encoded list of {role,content} for stateless mode"),
):
    history_messages: list[dict] = []
    if history:
        try:
            history_messages = json.loads(history)
        except (json.JSONDecodeError, TypeError):
            pass

    if session_id:
        s = get_session(session_id)
        if s is None:
            create_session_with_id(session_id, lang=lang)
    else:
        s = create_session(lang=lang)
        session_id = s["id"]

    _safe_add_message(session_id, "user", message)

    if not history_messages:
        try:
            server_history = get_messages(session_id)
            history_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in server_history[:-1]
            ]
        except Exception:
            history_messages = []

    async def event_stream():
        full_response = ""

        yield f"data: {json.dumps({'session_id': session_id, 'lang': lang})}\n\n"

        try:
            async for chunk in stream_chat_response(message, session_id, lang, history_messages):
                full_response += chunk
                yield f"data: {json.dumps({'text': chunk})}\n\n"
                await asyncio.sleep(0)

            # Save assistant response
            _safe_add_message(session_id, "assistant", full_response)
            yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

        except Exception as e:
            error_msg = f"Error: {e}"
            yield f"data: {json.dumps({'error': error_msg})}\n\n"
            _safe_add_message(session_id, "assistant", error_msg)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
