#!/usr/bin/env python3
"""Render startup: seed ChromaDB from baked-in data, then start uvicorn on $PORT."""
import os
import shutil
from pathlib import Path

CHROMA_PATH = Path("/app/chroma_db")
SEED_PATH = Path("/app/chroma_db_seed")


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


def main() -> None:
    if not chroma_has_data():
        seed_chroma()

    # Create data dirs (ephemeral, won't persist across restarts)
    Path("/app/data/chats").mkdir(parents=True, exist_ok=True)

    port = int(os.getenv("PORT", "8000"))
    print(f"Starting uvicorn on port {port}...")

    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
