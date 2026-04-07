from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SUPPORTED = "SUPPORTED"
PARTIAL = "PARTIAL"
UNSUPPORTED = "UNSUPPORTED"
CONTRADICTED = "CONTRADICTED"


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BenchmarkSample:
    sample_id: str
    question: str
    answer: str
    documents: list[Document]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Benchmark:
    benchmark_id: str
    description: str
    samples: list[BenchmarkSample]


@dataclass(frozen=True)
class Claim:
    claim_id: str
    sample_id: str
    sentence_index: int
    text: str
    cited_doc_ids: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Chunk:
    doc_id: str
    chunk_id: str
    title: str
    text: str
    token_count: int


@dataclass(frozen=True)
class RetrievedChunk:
    doc_id: str
    chunk_id: str
    title: str
    text: str
    score: float
    rank: int


@dataclass(frozen=True)
class ClaimAssessment:
    claim: Claim
    label: str
    support_score: float
    citation_precision: float
    matched_doc_ids: list[str]
    evidence: list[RetrievedChunk]
    rationale: str


@dataclass(frozen=True)
class AggregateMetrics:
    claim_count: int
    supported_claims: int
    partial_claims: int
    unsupported_claims: int
    contradicted_claims: int
    citation_precision: float
    support_rate: float
    contradiction_rate: float
    mean_support_score: float
    faithfulness_score: float


@dataclass(frozen=True)
class SampleResult:
    sample: BenchmarkSample
    claims: list[Claim]
    assessments: list[ClaimAssessment]
    metrics: AggregateMetrics


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_name: str = "baseline"
    chunk_size: int = 80
    chunk_overlap: int = 20
    top_k: int = 4
    support_threshold: float = 0.58
    partial_threshold: float = 0.34
    citation_match_threshold: float = 0.30

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ExperimentConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            chunk_size=int(raw.get("chunk_size", cls.chunk_size)),
            chunk_overlap=int(raw.get("chunk_overlap", cls.chunk_overlap)),
            top_k=int(raw.get("top_k", cls.top_k)),
            support_threshold=float(raw.get("support_threshold", cls.support_threshold)),
            partial_threshold=float(raw.get("partial_threshold", cls.partial_threshold)),
            citation_match_threshold=float(
                raw.get("citation_match_threshold", cls.citation_match_threshold)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: ExperimentConfig
    samples: list[SampleResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
