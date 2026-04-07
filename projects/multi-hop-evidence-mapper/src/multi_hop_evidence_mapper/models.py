from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ReasoningHop:
    hop_id: str
    claim: str
    bridge_terms: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MultiHopCase:
    case_id: str
    question: str
    answer: str
    documents: list[Document]
    reasoning_hops: list[ReasoningHop]
    conclusion_claim: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MultiHopBenchmark:
    benchmark_id: str
    description: str
    cases: list[MultiHopCase]


@dataclass(frozen=True)
class HopDocumentScore:
    doc_id: str
    title: str
    support_score: float
    lexical_overlap: float
    bridge_term_ratio: float


@dataclass(frozen=True)
class HopEvaluation:
    hop: ReasoningHop
    support_score: float
    mapped_doc_ids: list[str]
    doc_scores: list[HopDocumentScore]


@dataclass(frozen=True)
class BridgeEvaluation:
    from_hop_id: str
    to_hop_id: str
    shared_bridge_terms: list[str]
    support_score: float


@dataclass(frozen=True)
class CaseFinding:
    finding_id: str
    category: str
    severity: str
    related_ids: list[str]
    description: str


@dataclass(frozen=True)
class CaseMetrics:
    hop_count: int
    mean_hop_support: float
    mean_bridge_support: float
    conclusion_support: float
    mapped_document_coverage: float
    finding_count: int


@dataclass(frozen=True)
class AggregateMetrics:
    case_count: int
    total_hops: int
    mean_hop_support: float
    mean_bridge_support: float
    mean_conclusion_support: float
    mean_mapped_document_coverage: float
    total_findings: int


@dataclass(frozen=True)
class CaseResult:
    case: MultiHopCase
    hop_evaluations: list[HopEvaluation]
    bridge_evaluations: list[BridgeEvaluation]
    conclusion_support: float
    findings: list[CaseFinding]
    metrics: CaseMetrics


@dataclass(frozen=True)
class MappingConfig:
    experiment_name: str = "baseline"
    hop_support_threshold: float = 0.45
    bridge_support_threshold: float = 0.50
    conclusion_support_threshold: float = 0.48
    doc_contribution_threshold: float = 0.20

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MappingConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            hop_support_threshold=float(
                raw.get("hop_support_threshold", cls.hop_support_threshold)
            ),
            bridge_support_threshold=float(
                raw.get("bridge_support_threshold", cls.bridge_support_threshold)
            ),
            conclusion_support_threshold=float(
                raw.get(
                    "conclusion_support_threshold",
                    cls.conclusion_support_threshold,
                )
            ),
            doc_contribution_threshold=float(
                raw.get("doc_contribution_threshold", cls.doc_contribution_threshold)
            ),
        )


@dataclass(frozen=True)
class ExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: MappingConfig
    cases: list[CaseResult]
    aggregate_metrics: AggregateMetrics
    generated_at: str
