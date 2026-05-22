"""JSON file-based chat session store."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config import settings

CHATS_DIR = Path(__file__).resolve().parent / "data" / "chats"
CHATS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _session_path(session_id: str) -> Path:
    return CHATS_DIR / f"{session_id}.json"


def create_session(title: str = "", lang: str = "ar") -> dict:
    sid = str(uuid.uuid4())[:8]
    return create_session_with_id(sid, title, lang)


def create_session_with_id(session_id: str, title: str = "", lang: str = "ar") -> dict:
    now = _now()
    session = {
        "id": session_id,
        "title": title,
        "lang": lang,
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    _session_path(session_id).write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
    return session


def get_session(session_id: str) -> dict | None:
    p = _session_path(session_id)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def list_sessions() -> list[dict]:
    sessions = []
    for p in sorted(CHATS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            s = json.loads(p.read_text(encoding="utf-8"))
            # Return summary without messages
            sessions.append({
                "id": s["id"],
                "title": s["title"],
                "lang": s.get("lang", "ar"),
                "created_at": s["created_at"],
                "updated_at": s["updated_at"],
                "message_count": len(s.get("messages", [])),
            })
        except Exception:
            pass
    return sessions


def add_message(session_id: str, role: str, content: str, rag_hits: list[dict] | None = None) -> dict | None:
    s = get_session(session_id)
    if s is None:
        return None
    msg = {
        "role": role,
        "content": content,
        "timestamp": _now(),
    }
    if rag_hits is not None:
        msg["rag_hits"] = rag_hits
    s["messages"].append(msg)
    s["updated_at"] = _now()

    # Auto-name session from first user message
    if not s["title"] and role == "user":
        s["title"] = content[:60]

    _session_path(session_id).write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    return msg


def delete_session(session_id: str) -> bool:
    p = _session_path(session_id)
    if not p.exists():
        return False
    p.unlink()
    return True


def get_messages(session_id: str) -> list[dict]:
    s = get_session(session_id)
    if s is None:
        return []
    return s.get("messages", [])
