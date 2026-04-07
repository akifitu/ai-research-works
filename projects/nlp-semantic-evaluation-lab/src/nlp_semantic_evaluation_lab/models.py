from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NlpSample:
    sample_id: str
    reference: str
    prediction: str
    expected_entities: list[str] = field(default_factory=list)
    predicted_entities: list[str] = field(default_factory=list)
    expected_intent: str | None = None
    predicted_intent: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NlpBenchmark:
    benchmark_id: str
    description: str
    samples: list[NlpSample]


@dataclass(frozen=True)
class NlpEvaluationConfig:
    experiment_name: str = "baseline-nlp-eval"
    overlap_weight: float = 0.35
    sequence_weight: float = 0.35
    entity_weight: float = 0.20
    intent_weight: float = 0.10

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "NlpEvaluationConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            overlap_weight=float(raw.get("overlap_weight", cls.overlap_weight)),
            sequence_weight=float(raw.get("sequence_weight", cls.sequence_weight)),
            entity_weight=float(raw.get("entity_weight", cls.entity_weight)),
            intent_weight=float(raw.get("intent_weight", cls.intent_weight)),
        )


@dataclass(frozen=True)
class NlpSampleResult:
    sample_id: str
    token_overlap: float
    sequence_similarity: float
    entity_precision: float
    entity_recall: float
    entity_f1: float
    intent_correct: bool
    quality_score: float


@dataclass(frozen=True)
class NlpExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: NlpEvaluationConfig
    samples: list[NlpSampleResult]
    mean_quality_score: float
    mean_entity_f1: float
    intent_accuracy: float
    generated_at: str
