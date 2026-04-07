from __future__ import annotations

from dataclasses import dataclass

from .models import (
    CONTRADICTED,
    PARTIAL,
    SUPPORTED,
    UNSUPPORTED,
    Claim,
    ClaimAssessment,
    ExperimentConfig,
    RetrievedChunk,
)
from .text import negation_markers, numeric_tokens, unique_content_tokens


@dataclass(frozen=True)
class CandidateSignal:
    chunk: RetrievedChunk
    overlap_score: float
    numeric_alignment: float
    citation_alignment: float
    combined_score: float
    contradiction: bool


def _overlap_score(claim_text: str, evidence_text: str) -> float:
    claim_tokens = unique_content_tokens(claim_text)
    evidence_tokens = unique_content_tokens(evidence_text)
    if not claim_tokens:
        return 0.0
    return len(claim_tokens & evidence_tokens) / len(claim_tokens)


def _numeric_alignment(claim_text: str, evidence_text: str) -> tuple[float, bool]:
    claim_values = numeric_tokens(claim_text)
    evidence_values = numeric_tokens(evidence_text)
    if not claim_values:
        return 1.0, False
    if not evidence_values:
        return 0.0, False
    overlap = len(claim_values & evidence_values) / len(claim_values)
    return overlap, overlap == 0.0


def _has_negation_conflict(claim_text: str, evidence_text: str) -> bool:
    claim_negations = negation_markers(claim_text)
    evidence_negations = negation_markers(evidence_text)
    return bool(claim_negations) != bool(evidence_negations)


def _score_candidate(
    claim: Claim, candidate: RetrievedChunk, config: ExperimentConfig
) -> CandidateSignal:
    overlap_score = _overlap_score(claim.text, candidate.text)
    numeric_alignment, numeric_conflict = _numeric_alignment(claim.text, candidate.text)
    citation_alignment = (
        1.0 if not claim.cited_doc_ids else float(candidate.doc_id in claim.cited_doc_ids)
    )
    contradiction = (
        overlap_score >= config.citation_match_threshold
        and (numeric_conflict or _has_negation_conflict(claim.text, candidate.text))
    )
    combined_score = (
        (0.75 * overlap_score)
        + (0.15 * numeric_alignment)
        + (0.10 * citation_alignment)
    )
    return CandidateSignal(
        chunk=candidate,
        overlap_score=overlap_score,
        numeric_alignment=numeric_alignment,
        citation_alignment=citation_alignment,
        combined_score=combined_score,
        contradiction=contradiction,
    )


def assess_claim(
    claim: Claim, evidence: list[RetrievedChunk], config: ExperimentConfig
) -> ClaimAssessment:
    if not evidence:
        rationale = "No retriever output was available for this claim."
        return ClaimAssessment(
            claim=claim,
            label=UNSUPPORTED,
            support_score=0.0,
            citation_precision=0.0 if claim.cited_doc_ids else 1.0,
            matched_doc_ids=[],
            evidence=[],
            rationale=rationale,
        )

    candidate_signals = [_score_candidate(claim, candidate, config) for candidate in evidence]
    best_signal = max(candidate_signals, key=lambda signal: signal.combined_score)
    matched_doc_ids = [
        signal.chunk.doc_id
        for signal in candidate_signals
        if signal.overlap_score >= config.citation_match_threshold
    ]
    deduped_matches = list(dict.fromkeys(matched_doc_ids))

    if claim.cited_doc_ids:
        cited_set = set(claim.cited_doc_ids)
        citation_precision = len(cited_set & set(deduped_matches)) / len(cited_set)
    else:
        citation_precision = 1.0

    if best_signal.contradiction:
        label = CONTRADICTED
    elif best_signal.combined_score >= config.support_threshold:
        label = SUPPORTED
    elif best_signal.combined_score >= config.partial_threshold:
        label = PARTIAL
    else:
        label = UNSUPPORTED

    rationale_parts = [
        (
            f"Best evidence {best_signal.chunk.chunk_id} scored "
            f"{best_signal.combined_score:.2f} with lexical overlap "
            f"{best_signal.overlap_score:.2f}."
        )
    ]
    if claim.cited_doc_ids and citation_precision < 1.0:
        rationale_parts.append("Inline citations did not fully align with the retrieved support.")
    if best_signal.contradiction:
        rationale_parts.append("A contradiction pattern was detected through numeric or negation mismatch.")

    return ClaimAssessment(
        claim=claim,
        label=label,
        support_score=round(best_signal.combined_score, 4),
        citation_precision=round(citation_precision, 4),
        matched_doc_ids=deduped_matches,
        evidence=evidence,
        rationale=" ".join(rationale_parts),
    )
