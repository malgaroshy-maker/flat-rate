"""Dictionary API routes."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from dictionary_store import dictionary_store

router = APIRouter(prefix="/api/dictionary", tags=["dictionary"])


class TermCreate(BaseModel):
    arabic_term: str
    standard_category: str
    english_term: str = ""


class TermUpdate(BaseModel):
    arabic_term: Optional[str] = None
    standard_category: Optional[str] = None
    english_term: Optional[str] = None


class PendingCreate(BaseModel):
    term_text: str
    query_text: str = ""


class PendingResolve(BaseModel):
    arabic_term: str
    standard_category: str
    english_term: str = ""


@router.get("")
async def list_terms(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
):
    terms = dictionary_store.list_terms(search=search, category=category)
    return {"terms": terms, "count": len(terms)}


@router.post("")
async def create_term(body: TermCreate):
    term_id = dictionary_store.add_term(
        arabic_term=body.arabic_term,
        standard_category=body.standard_category,
        english_term=body.english_term,
    )
    return {"id": term_id, **dictionary_store.get_term(term_id)}


@router.put("/{term_id}")
async def update_term(term_id: str, body: TermUpdate):
    ok = dictionary_store.update_term(
        term_id=term_id,
        arabic_term=body.arabic_term,
        standard_category=body.standard_category,
        english_term=body.english_term,
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Term not found")
    return dictionary_store.get_term(term_id)


@router.delete("/{term_id}")
async def delete_term(term_id: str):
    ok = dictionary_store.delete_term(term_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Term not found")
    return {"status": "deleted"}


@router.post("/pending")
async def create_pending(body: PendingCreate):
    pending_id = dictionary_store.add_pending(
        term_text=body.term_text,
        query_text=body.query_text,
    )
    return {"id": pending_id}


@router.get("/pending")
async def list_pending():
    items = dictionary_store.list_pending()
    return {"pending": items, "count": len(items)}


@router.post("/pending/{pending_id}/resolve")
async def resolve_pending(pending_id: str, body: PendingResolve):
    term_id = dictionary_store.resolve_pending(
        pending_id=pending_id,
        arabic_term=body.arabic_term,
        standard_category=body.standard_category,
        english_term=body.english_term,
    )
    if term_id is None:
        raise HTTPException(status_code=404, detail="Pending term not found")
    return {"resolved_term_id": term_id}
