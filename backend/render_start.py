#!/usr/bin/env python3
"""Render startup: seed ChromaDB from baked-in data, verify it loaded, then start uvicorn on $PORT."""
import os
import shutil
import sys
from pathlib import Path

CHROMA_PATH = Path("/app/chroma_db")
SEED_PATH = Path("/app/chroma_db_seed")

# config.py's default CHROMA_PERSIST_DIR is computed as
# Path(__file__).resolve().parent.parent / "chroma_db" — correct for a
# normal checkout (backend/config.py -> repo_root/chroma_db), but the
# Dockerfile flattens backend/'s contents into /app (COPY backend/ .), so
# that same computation resolves to "/chroma_db", not "/app/chroma_db"
# where this script actually seeds data. Pin it explicitly so the app
# doesn't silently depend on a CHROMA_PERSIST_DIR env var configured only
# in the Render dashboard (invisible in this repo, easy to lose track of).
os.environ.setdefault("CHROMA_PERSIST_DIR", str(CHROMA_PATH))


def chroma_has_data() -> bool:
    if not CHROMA_PATH.exists():
        return False
    dirs = [d for d in CHROMA_PATH.iterdir() if d.is_dir()]
    if not dirs:
        return False
    for d in dirs:
        if (d / "data_level0.bin").exists():
            return True
    return False


def seed_chroma() -> None:
    if not SEED_PATH.exists() or not any(SEED_PATH.iterdir()):
        print("No seed data found.")
        return
    print(f"Seeding ChromaDB from {SEED_PATH}...")
    if CHROMA_PATH.exists():
        shutil.rmtree(str(CHROMA_PATH))
    CHROMA_PATH.mkdir(parents=True)
    for item in SEED_PATH.iterdir():
        dst = CHROMA_PATH / item.name
        if item.is_dir():
            shutil.copytree(str(item), str(dst))
        else:
            shutil.copy2(str(item), str(dst))
    print("Seed complete.")


def verify_collection() -> int:
    """Open the collection and return its record count, logging loudly.

    A build that boots with zero records would otherwise serve every chat
    request with empty RAG context — degraded but not obviously broken.
    Failing the deploy here (Render marks it failed, previous deploy stays
    live) is much easier to notice than "the AI got worse" days later.
    """
    sys.path.insert(0, "/app")
    from vector_store import get_or_create_collection  # noqa: E402

    collection = get_or_create_collection()
    count = collection.count()
    if count == 0:
        print("FATAL: ChromaDB collection loaded but contains 0 records — refusing to start.", file=sys.stderr)
        sys.exit(1)
    print(f"ChromaDB collection verified: {count} chunks loaded.")
    return count


def main() -> None:
    if not chroma_has_data():
        seed_chroma()

    verify_collection()

    # Create data dirs (ephemeral, won't persist across restarts)
    Path("/app/data/chats").mkdir(parents=True, exist_ok=True)

    port = int(os.getenv("PORT", "8000"))
    print(f"Starting uvicorn on port {port}...")

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
