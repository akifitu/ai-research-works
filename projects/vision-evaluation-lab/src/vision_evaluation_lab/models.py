from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BoundingBox:
    label: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "BoundingBox":
        return cls(
            label=str(raw["label"]),
            x_min=float(raw["x_min"]),
            y_min=float(raw["y_min"]),
            x_max=float(raw["x_max"]),
            y_max=float(raw["y_max"]),
            confidence=(
                None if raw.get("confidence") is None else float(raw.get("confidence"))
            ),
        )

    @property
    def area(self) -> float:
        return max(0.0, self.x_max - self.x_min) * max(0.0, self.y_max - self.y_min)


@dataclass(frozen=True)
class VisionSample:
    image_id: str
    ground_truth_label: str
    predicted_label: str
    ground_truth_boxes: list[BoundingBox]
    predicted_boxes: list[BoundingBox]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VisionBenchmark:
    benchmark_id: str
    description: str
    samples: list[VisionSample]


@dataclass(frozen=True)
class VisionConfig:
    experiment_name: str = "baseline-vision-eval"
    iou_threshold: float = 0.50
    min_confidence: float = 0.25

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "VisionConfig":
        return cls(
            experiment_name=str(raw.get("experiment_name", cls.experiment_name)),
            iou_threshold=float(raw.get("iou_threshold", cls.iou_threshold)),
            min_confidence=float(raw.get("min_confidence", cls.min_confidence)),
        )


@dataclass(frozen=True)
class DetectionMatch:
    image_id: str
    label: str
    truth_index: int
    prediction_index: int
    iou: float


@dataclass(frozen=True)
class ClassMetrics:
    label: str
    true_positive: int
    false_positive: int
    false_negative: int
    precision: float
    recall: float
    f1: float
    support: int


@dataclass(frozen=True)
class VisionSampleResult:
    image_id: str
    classification_correct: bool
    matches: list[DetectionMatch]
    false_positive_boxes: int
    false_negative_boxes: int


@dataclass(frozen=True)
class VisionExperimentResult:
    benchmark_id: str
    benchmark_description: str
    config: VisionConfig
    samples: list[VisionSampleResult]
    classification_metrics: list[ClassMetrics]
    detection_precision: float
    detection_recall: float
    detection_f1: float
    mean_iou: float
    generated_at: str
