from __future__ import annotations

from datetime import datetime, timezone

from .claims import extract_claims
from .grounding import assess_claim
from .metrics import summarize_assessments
from .models import Benchmark, ExperimentConfig, ExperimentResult, SampleResult
from .retrieval import LexicalRetriever, chunk_documents


class ExperimentRunner:
    def __init__(self, config: ExperimentConfig):
        self.config = config

    def run_sample(self, sample) -> SampleResult:
        claims = extract_claims(sample)
        chunks = chunk_documents(sample.documents, self.config.chunk_size, self.config.chunk_overlap)
        retriever = LexicalRetriever(chunks)
        assessments = [
            assess_claim(claim, retriever.retrieve(claim.text, self.config.top_k), self.config)
            for claim in claims
        ]
        metrics = summarize_assessments(assessments)
        return SampleResult(
            sample=sample,
            claims=claims,
            assessments=assessments,
            metrics=metrics,
        )

    def run_benchmark(self, benchmark: Benchmark) -> ExperimentResult:
        sample_results = [self.run_sample(sample) for sample in benchmark.samples]
        all_assessments = [
            assessment
            for sample_result in sample_results
            for assessment in sample_result.assessments
        ]
        aggregate_metrics = summarize_assessments(all_assessments)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            samples=sample_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
