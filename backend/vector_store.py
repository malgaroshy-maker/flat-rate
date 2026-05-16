"""Vector store operations using ChromaDB."""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings

from config import settings

COLLECTION_NAME = "labor_records"


def get_client():
    persist_dir = Path(settings.CHROMA_PERSIST_DIR)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(
        path=str(persist_dir),
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_or_create_collection():
    client = get_client()
    existing = client.list_collections()
    if COLLECTION_NAME in [c.name for c in existing]:
        return client.get_collection(COLLECTION_NAME)
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def reset_collection(metadata: dict | None = None):
    client = get_client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    return client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine", **(metadata or {})},
    )


def add_to_collection(collection, ids, embeddings, metadatas, documents):
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents,
    )


def query_collection(collection, query_embedding, n_results=10, where=None):
    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"],
    )


def search_with_metadata(
    collection, query_embedding, n_results=10, where=None
):
    """Extended query returning distances + full metadata for QA metrics.

    Returns list of {id, metadata, distance, document} dicts.
    """
    result = query_collection(collection, query_embedding, n_results, where)
    hits = []
    for i in range(len(result["ids"][0])):
        hits.append(
            {
                "id": result["ids"][0][i],
                "metadata": result["metadatas"][0][i],
                "distance": result["distances"][0][i],
                "document": result["documents"][0][i] if result["documents"] else "",
            }
        )
    return hits
