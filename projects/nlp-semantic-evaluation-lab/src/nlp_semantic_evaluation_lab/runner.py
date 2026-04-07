from __future__ import annotations

from datetime import datetime, timezone

from .models import NlpBenchmark, NlpEvaluationConfig, NlpExperimentResult, NlpSample, NlpSampleResult
from .semantics import entity_f1, lcs_similarity, safe_divide, token_overlap


class NlpSemanticEvaluationRunner:
    def __init__(self, config: NlpEvaluationConfig):
        self.config = config

    def run_sample(self, sample: NlpSample) -> NlpSampleResult:
        overlap = token_overlap(sample.reference, sample.prediction)
        sequence = lcs_similarity(sample.reference, sample.prediction)
        entity_precision, entity_recall, entity_score = entity_f1(
            sample.expected_entities,
            sample.predicted_entities,
        )
        intent_correct = sample.expected_intent == sample.predicted_intent
        quality_score = (
            self.config.overlap_weight * overlap
            + self.config.sequence_weight * sequence
            + self.config.entity_weight * entity_score
            + self.config.intent_weight * float(intent_correct)
        )
        return NlpSampleResult(
            sample_id=sample.sample_id,
            token_overlap=overlap,
            sequence_similarity=sequence,
            entity_precision=entity_precision,
            entity_recall=entity_recall,
            entity_f1=entity_score,
            intent_correct=intent_correct,
            quality_score=quality_score,
        )

    def run_benchmark(self, benchmark: NlpBenchmark) -> NlpExperimentResult:
        sample_results = [self.run_sample(sample) for sample in benchmark.samples]
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return NlpExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            samples=sample_results,
            mean_quality_score=safe_divide(
                sum(result.quality_score for result in sample_results),
                len(sample_results),
            ),
            mean_entity_f1=safe_divide(
                sum(result.entity_f1 for result in sample_results),
                len(sample_results),
            ),
            intent_accuracy=safe_divide(
                sum(result.intent_correct for result in sample_results),
                len(sample_results),
            ),
            generated_at=generated_at,
        )
