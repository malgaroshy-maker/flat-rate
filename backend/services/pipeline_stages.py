"""Pipeline stage definitions — discrete, typed stages for the RAG pipeline.

Inspired by Agents Orchestrator: each stage is a self-contained specialist.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class StageResult:
    stage: str
    status: str  # "ok" | "warning" | "error"
    data: Any = None
    error: str = ""
    elapsed_ms: float = 0.0


@dataclass
class EmbedInput:
    query_text: str


@dataclass
class EmbedOutput:
    embedding: list[float]
    query_language: str


@dataclass
class SearchInput:
    embedding: list[float]
    n_results: int = 5
    department_filter: Optional[str] = None


@dataclass
class SearchOutput:
    hits: list[dict]
    mode: str


@dataclass
class ComputeInput:
    hits: list[dict]


@dataclass
class ComputeOutput:
    confidence_range: dict
    outliers: list[dict]


@dataclass
class ExplainInput:
    hits: list[dict]
    confidence_range: dict


@dataclass
class ExplainOutput:
    contributions: list[dict]
    confidence: str
    top_model: Optional[str]
    model_count: int


@dataclass
class GenerateInput:
    query_text: str
    hits: list[dict]
    confidence_range: dict
    output_language: str
    system_prompt: str = ""


@dataclass
class GenerateOutput:
    response_text: str


@dataclass
class PipelineState:
    """Tracks state across one complete pipeline execution."""
    query_text: str = ""
    stages: list[StageResult] = field(default_factory=list)
    total_elapsed_ms: float = 0.0
    quality_gates_passed: int = 0
    quality_gates_failed: int = 0
