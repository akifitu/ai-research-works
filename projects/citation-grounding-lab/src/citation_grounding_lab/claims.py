from __future__ import annotations

from .citations import extract_citation_ids, strip_inline_citations
from .models import BenchmarkSample, Claim
from .text import content_tokens, split_sentences

MIN_CLAIM_TOKENS = 3


def extract_claims(sample: BenchmarkSample) -> list[Claim]:
    claims: list[Claim] = []
    for sentence_index, sentence in enumerate(split_sentences(sample.answer), start=1):
        cleaned_sentence = strip_inline_citations(sentence)
        if len(content_tokens(cleaned_sentence)) < MIN_CLAIM_TOKENS:
            continue
        claims.append(
            Claim(
                claim_id=f"{sample.sample_id}-claim-{sentence_index:02d}",
                sample_id=sample.sample_id,
                sentence_index=sentence_index,
                text=cleaned_sentence,
                cited_doc_ids=extract_citation_ids(sentence),
            )
        )
    return claims
