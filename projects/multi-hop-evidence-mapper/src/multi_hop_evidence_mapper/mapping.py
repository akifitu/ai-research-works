from __future__ import annotations

import re

from .models import BridgeEvaluation, Document, HopDocumentScore, HopEvaluation, ReasoningHop

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "because",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "used",
    "was",
    "which",
    "with",
}
TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?")


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _content_tokens(text: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(_normalized(text))
        if token not in STOPWORDS and len(token) > 1
    }


def lexical_support(source_text: str, target_text: str) -> float:
    source_tokens = _content_tokens(source_text)
    if not source_tokens:
        return 1.0
    target_tokens = _content_tokens(target_text)
    return len(source_tokens & target_tokens) / len(source_tokens)


def _bridge_term_ratio(bridge_terms: list[str], text: str) -> float:
    if not bridge_terms:
        return 1.0
    normalized_text = _normalized(text)
    matched = sum(_normalized(term) in normalized_text for term in bridge_terms)
    return matched / len(bridge_terms)


def map_hop_to_documents(hop: ReasoningHop, documents: list[Document]) -> HopEvaluation:
    doc_scores: list[HopDocumentScore] = []
    for document in documents:
        lexical_overlap = lexical_support(hop.claim, document.text)
        bridge_ratio = _bridge_term_ratio(hop.bridge_terms, document.text)
        support_score = (0.75 * lexical_overlap) + (0.25 * bridge_ratio)
        doc_scores.append(
            HopDocumentScore(
                doc_id=document.doc_id,
                title=document.title,
                support_score=round(support_score, 4),
                lexical_overlap=round(lexical_overlap, 4),
                bridge_term_ratio=round(bridge_ratio, 4),
            )
        )

    doc_scores.sort(key=lambda item: item.support_score, reverse=True)
    best_support = doc_scores[0].support_score if doc_scores else 0.0
    mapped_doc_ids = [score.doc_id for score in doc_scores if score.support_score > 0.0]
    return HopEvaluation(
        hop=hop,
        support_score=round(best_support, 4),
        mapped_doc_ids=mapped_doc_ids,
        doc_scores=doc_scores,
    )


def evaluate_bridge_with_documents(
    previous_hop: HopEvaluation,
    next_hop: HopEvaluation,
    documents: list[Document],
) -> BridgeEvaluation:
    shared_terms = [
        term
        for term in previous_hop.hop.bridge_terms
        if _normalized(term) in {_normalized(candidate) for candidate in next_hop.hop.bridge_terms}
    ]
    if not shared_terms:
        return BridgeEvaluation(
            from_hop_id=previous_hop.hop.hop_id,
            to_hop_id=next_hop.hop.hop_id,
            shared_bridge_terms=[],
            support_score=0.0,
        )

    doc_texts = {document.doc_id: document.text for document in documents}
    previous_primary_doc = previous_hop.doc_scores[0].doc_id if previous_hop.doc_scores else ""
    next_primary_doc = next_hop.doc_scores[0].doc_id if next_hop.doc_scores else ""
    previous_bridge_ratio = _bridge_term_ratio(shared_terms, doc_texts.get(previous_primary_doc, ""))
    next_bridge_ratio = _bridge_term_ratio(shared_terms, doc_texts.get(next_primary_doc, ""))

    support_score = (
        0.40 * min(previous_hop.support_score, next_hop.support_score)
        + 0.60 * min(previous_bridge_ratio, next_bridge_ratio)
    )
    return BridgeEvaluation(
        from_hop_id=previous_hop.hop.hop_id,
        to_hop_id=next_hop.hop.hop_id,
        shared_bridge_terms=shared_terms,
        support_score=round(support_score, 4),
    )


def conclusion_support(conclusion_claim: str, mapped_documents: list[Document]) -> float:
    combined_text = " ".join(document.text for document in mapped_documents)
    return round(lexical_support(conclusion_claim, combined_text), 4)
