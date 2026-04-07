from __future__ import annotations

from datetime import datetime, timezone

from .metrics import aggregate_detection_metrics, classification_metrics, evaluate_sample
from .models import VisionBenchmark, VisionConfig, VisionExperimentResult


class VisionEvaluationRunner:
    def __init__(self, config: VisionConfig):
        self.config = config

    def run_benchmark(self, benchmark: VisionBenchmark) -> VisionExperimentResult:
        sample_results = [evaluate_sample(sample, self.config) for sample in benchmark.samples]
        precision, recall, f1, mean_iou = aggregate_detection_metrics(sample_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return VisionExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            samples=sample_results,
            classification_metrics=classification_metrics(benchmark.samples),
            detection_precision=precision,
            detection_recall=recall,
            detection_f1=f1,
            mean_iou=mean_iou,
            generated_at=generated_at,
        )
