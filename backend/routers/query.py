"""Query API routes."""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import Response

from pdf_generator import generate_pdf
from query_engine import execute_query, generate_natural_response
from services.query_service import query_with_orchestrator

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/query")
async def query_labor(
    q: str = Query(..., description="Natural language query text"),
    n: int = Query(5, ge=1, le=20, description="Number of results"),
    department: Optional[str] = Query(None, description="Filter by department"),
    generate: bool = Query(False, description="Generate natural language response"),
    lang: str = Query("ar", description="Output language (ar/en)"),
    orchestrate: bool = Query(False, description="Use pipeline orchestrator"),
):
    if orchestrate:
        result = query_with_orchestrator(
            query_text=q, n_results=n, department_filter=department,
            lang=lang, generate=generate,
        )
    else:
        result = execute_query(q, n_results=n, department_filter=department)
        if generate:
            result["natural_response"] = generate_natural_response(result, lang)
    return result


@router.post("/export/pdf")
async def export_pdf(
    q: str = Query(..., description="Natural language query text"),
    n: int = Query(5, ge=1, le=20, description="Number of results"),
    department: Optional[str] = Query(None, description="Filter by department"),
    lang: str = Query("ar", description="Output language (ar/en)"),
):
    result = execute_query(q, n_results=n, department_filter=department)

    pdf_bytes = generate_pdf(
        query_text=q,
        hits=result.get("hits", []),
        confidence_range=result.get("confidence_range", {}),
        outliers=result.get("outliers", []),
        language=lang,
    )

    filename = "labor-estimate.pdf"
    if result.get("hits"):
        top_model = (result["hits"][0].get("model") or "vehicle").strip()
        top_model = re.sub(r'[\\/*?:"<>|]', "", top_model)[:40]
        today = date.today().isoformat()
        filename = f"labor-estimate_{top_model}_{today}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
