from __future__ import annotations

from datetime import datetime, timezone

from .mapping import conclusion_support, evaluate_bridge_with_documents, map_hop_to_documents
from .metrics import summarize_benchmark, summarize_case
from .models import (
    CaseFinding,
    CaseResult,
    ExperimentResult,
    MappingConfig,
    MultiHopBenchmark,
    MultiHopCase,
)


class ExperimentRunner:
    def __init__(self, config: MappingConfig):
        self.config = config

    def run_case(self, case: MultiHopCase) -> CaseResult:
        hop_evaluations = [
            map_hop_to_documents(hop, case.documents) for hop in case.reasoning_hops
        ]
        bridge_evaluations = [
            evaluate_bridge_with_documents(previous_hop, next_hop, case.documents)
            for previous_hop, next_hop in zip(hop_evaluations, hop_evaluations[1:])
        ]

        mapped_doc_ids = {
            score.doc_id
            for hop in hop_evaluations
            for score in hop.doc_scores
            if score.support_score >= self.config.doc_contribution_threshold
        }
        mapped_documents = [
            document for document in case.documents if document.doc_id in mapped_doc_ids
        ]
        lexical_conclusion_support = conclusion_support(case.conclusion_claim, mapped_documents)
        chain_support = (
            sum(bridge.support_score for bridge in bridge_evaluations) / len(bridge_evaluations)
            if bridge_evaluations
            else (
                sum(hop.support_score for hop in hop_evaluations) / len(hop_evaluations)
                if hop_evaluations
                else 0.0
            )
        )
        final_conclusion_support = round(
            (0.55 * lexical_conclusion_support) + (0.45 * chain_support),
            4,
        )

        findings: list[CaseFinding] = []
        finding_index = 1

        def add_finding(
            category: str,
            severity: str,
            related_ids: list[str],
            description: str,
        ) -> None:
            nonlocal finding_index
            findings.append(
                CaseFinding(
                    finding_id=f"{case.case_id}-finding-{finding_index:02d}",
                    category=category,
                    severity=severity,
                    related_ids=related_ids,
                    description=description,
                )
            )
            finding_index += 1

        for hop in hop_evaluations:
            if hop.support_score < self.config.hop_support_threshold:
                add_finding(
                    category="MISSING_HOP_SUPPORT",
                    severity="high",
                    related_ids=[hop.hop.hop_id],
                    description=(
                        f"Hop `{hop.hop.hop_id}` support remained at {hop.support_score:.2f}, "
                        "below the configured threshold."
                    ),
                )

        for bridge in bridge_evaluations:
            if bridge.support_score < self.config.bridge_support_threshold:
                add_finding(
                    category="BROKEN_BRIDGE",
                    severity="high",
                    related_ids=[bridge.from_hop_id, bridge.to_hop_id],
                    description=(
                        f"Bridge continuity between `{bridge.from_hop_id}` and "
                        f"`{bridge.to_hop_id}` scored {bridge.support_score:.2f}."
                    ),
                )

        if final_conclusion_support < self.config.conclusion_support_threshold:
            add_finding(
                category="UNSUPPORTED_CONCLUSION",
                severity="high",
                related_ids=[case.case_id],
                description=(
                    f"The conclusion support score was {final_conclusion_support:.2f}, "
                    "which indicates weak grounding across the mapped evidence."
                ),
            )

        for document in case.documents:
            max_contribution = max(
                (score.support_score for hop in hop_evaluations for score in hop.doc_scores if score.doc_id == document.doc_id),
                default=0.0,
            )
            if max_contribution < self.config.doc_contribution_threshold:
                add_finding(
                    category="DOC_GAP",
                    severity="low",
                    related_ids=[document.doc_id],
                    description=(
                        f"Document `{document.doc_id}` contributed only {max_contribution:.2f} "
                        "to the reasoning chain."
                    ),
                )

        mapped_document_coverage = len(mapped_doc_ids) / len(case.documents) if case.documents else 0.0
        metrics = summarize_case(
            hop_supports=[evaluation.support_score for evaluation in hop_evaluations],
            bridge_supports=[evaluation.support_score for evaluation in bridge_evaluations],
            conclusion_support=final_conclusion_support,
            mapped_document_coverage=mapped_document_coverage,
            finding_count=len(findings),
        )
        return CaseResult(
            case=case,
            hop_evaluations=hop_evaluations,
            bridge_evaluations=bridge_evaluations,
            conclusion_support=final_conclusion_support,
            findings=findings,
            metrics=metrics,
        )

    def run_benchmark(self, benchmark: MultiHopBenchmark) -> ExperimentResult:
        case_results = [self.run_case(case) for case in benchmark.cases]
        aggregate_metrics = summarize_benchmark(case_results)
        generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        return ExperimentResult(
            benchmark_id=benchmark.benchmark_id,
            benchmark_description=benchmark.description,
            config=self.config,
            cases=case_results,
            aggregate_metrics=aggregate_metrics,
            generated_at=generated_at,
        )
