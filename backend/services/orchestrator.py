"""Pipeline orchestrator — coordinates multi-stage RAG execution with quality gates.

Inspired by Agents Orchestrator: autonomous pipeline manager with dev-QA loops.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Optional

from services.pipeline_stages import (
    ComputeInput,
    ComputeOutput,
    EmbedInput,
    EmbedOutput,
    ExplainInput,
    ExplainOutput,
    GenerateInput,
    GenerateOutput,
    PipelineState,
    SearchInput,
    SearchOutput,
    StageResult,
)
from services.quality_gates import GATE_MAP


class PipelineOrchestrator:
    def __init__(self):
        self._embed_fn: Optional[Callable] = None
        self._search_fn: Optional[Callable] = None
        self._compute_fn: Optional[Callable] = None
        self._explain_fn: Optional[Callable] = None
        self._generate_fn: Optional[Callable] = None

    def set_embed_stage(self, fn: Callable[[EmbedInput], EmbedOutput]):
        self._embed_fn = fn

    def set_search_stage(self, fn: Callable[[SearchInput], SearchOutput]):
        self._search_fn = fn

    def set_compute_stage(self, fn: Callable[[ComputeInput], ComputeOutput]):
        self._compute_fn = fn

    def set_explain_stage(self, fn: Callable[[ExplainInput], ExplainOutput]):
        self._explain_fn = fn

    def set_generate_stage(self, fn: Callable[[GenerateInput], GenerateOutput]):
        self._generate_fn = fn

    def _run_stage(self, stage_name: str, fn: Callable, input_data: Any, gate_name: str | None = None) -> StageResult:
        t0 = time.perf_counter()
        try:
            result = fn(input_data)
            elapsed = time.perf_counter() - t0
            gate_result = (True, "ok")
            if gate_name and gate_name in GATE_MAP:
                gate_result = GATE_MAP[gate_name](result)
            return StageResult(
                stage=stage_name,
                status="ok" if gate_result[0] else "warning",
                data=result,
                error="" if gate_result[0] else gate_result[1],
                elapsed_ms=round(elapsed * 1000, 2),
            )
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            return StageResult(
                stage=stage_name,
                status="error",
                data=None,
                error=str(exc),
                elapsed_ms=round(elapsed * 1000, 2),
            )

    def run_query_pipeline(
        self,
        query_text: str,
        n_results: int = 5,
        department_filter: Optional[str] = None,
        output_language: str = "ar",
        generate_response: bool = False,
    ) -> tuple[dict, PipelineState]:
        state = PipelineState(query_text=query_text)
        t_total = time.perf_counter()

        sr = self._run_stage("embed", self._embed_fn, EmbedInput(query_text=query_text), "embed")
        state.stages.append(sr)
        if sr.status == "error" or sr.data is None:
            state.total_elapsed_ms = round((time.perf_counter() - t_total) * 1000, 1)
            return _empty_result(query_text), state
        embed_out: EmbedOutput = sr.data

        sr = self._run_stage(
            "search",
            self._search_fn,
            SearchInput(embedding=embed_out.embedding, n_results=n_results, department_filter=department_filter),
            "search",
        )
        state.stages.append(sr)
        if sr.status == "error" or sr.data is None:
            state.total_elapsed_ms = round((time.perf_counter() - t_total) * 1000, 1)
            return _empty_result(query_text), state
        search_out: SearchOutput = sr.data

        sr = self._run_stage("compute", self._compute_fn, ComputeInput(hits=search_out.hits), "compute")
        state.stages.append(sr)
        compute_out = sr.data if sr.status != "error" and sr.data else ComputeOutput({}, [])

        sr = self._run_stage(
            "explain",
            self._explain_fn,
            ExplainInput(hits=search_out.hits, confidence_range=compute_out.confidence_range),
            "explain",
        )
        state.stages.append(sr)
        explain_out = sr.data if sr.status != "error" and sr.data else ExplainOutput([], "none", None, 0)

        result = {
            "query": query_text,
            "query_language": embed_out.query_language,
            "hits": search_out.hits,
            "confidence_range": compute_out.confidence_range,
            "outliers": compute_out.outliers,
            "mode": search_out.mode,
            "explanation": {
                "contributions": explain_out.contributions,
                "confidence": explain_out.confidence,
                "top_model": explain_out.top_model,
                "model_count": explain_out.model_count,
            },
        }

        if generate_response and self._generate_fn:
            sr = self._run_stage(
                "generate",
                self._generate_fn,
                GenerateInput(
                    query_text=query_text,
                    hits=search_out.hits,
                    confidence_range=compute_out.confidence_range,
                    output_language=output_language,
                ),
                "generate",
            )
            state.stages.append(sr)
            if sr.status != "error" and sr.data:
                result["natural_response"] = sr.data.response_text

        state.total_elapsed_ms = round((time.perf_counter() - t_total) * 1000, 1)
        state.quality_gates_passed = sum(1 for s in state.stages if s.status == "ok")
        state.quality_gates_failed = sum(1 for s in state.stages if s.status in ("warning", "error"))

        result["pipeline_state"] = {
            "stages": [(s.stage, s.status, s.elapsed_ms) for s in state.stages],
            "total_ms": state.total_elapsed_ms,
            "gates_passed": state.quality_gates_passed,
            "gates_failed": state.quality_gates_failed,
        }

        return result, state


def _empty_result(query_text: str) -> dict:
    return {
        "query": query_text,
        "query_language": "unknown",
        "hits": [],
        "confidence_range": {},
        "outliers": [],
        "mode": "unknown",
        "explanation": {"contributions": [], "confidence": "none", "top_model": None, "model_count": 0},
    }
