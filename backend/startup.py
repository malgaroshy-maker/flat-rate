#!/usr/bin/env python3
"""Startup: seed ChromaDB from baked-in MiniLM data if empty on volume, then start uvicorn."""
import shutil
import sys
import chromadb
from pathlib import Path

CHROMA_PATH = Path("/app/chroma_db")
SEED_PATH = Path("/app/chroma_db_seed")


def chroma_has_data() -> bool:
    try:
        client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        collections = client.list_collections()
        for col in collections:
            if col.count() > 0:
                print(f"Collection '{col.name}' has {col.count()} records — skipping seed")
                return True
    except Exception as e:
        print(f"ChromaDB check failed: {e}")
    return False


def seed_chroma() -> None:
    if not SEED_PATH.exists() or not any(SEED_PATH.iterdir()):
        print("No seed data found.")
        return
    print(f"Copying seed data from {SEED_PATH} to {CHROMA_PATH}...")
    for item in SEED_PATH.iterdir():
        dst = CHROMA_PATH / item.name
        if item.is_dir():
            if dst.exists():
                shutil.rmtree(str(dst))
            shutil.copytree(str(item), str(dst))
        else:
            shutil.copy2(str(item), str(dst))
    print("Seed copy complete.")


def main() -> None:
    if not chroma_has_data():
        seed_chroma()
    else:
        # Clear seed flag so on restart we don't overwrite
        # (e.g., after Gemini ingestion)
        pass

    print("Starting uvicorn...")

    # Run uvicorn in-process to avoid KeyboardInterrupt during shutdown
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")


if __name__ == "__main__":
    main()
