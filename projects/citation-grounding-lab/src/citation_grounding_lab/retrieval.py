from __future__ import annotations

from collections import Counter
from math import log, sqrt

from .models import Chunk, Document, RetrievedChunk
from .text import count_content_tokens, normalize_whitespace, numeric_tokens


def chunk_documents(
    documents: list[Document], chunk_size: int, chunk_overlap: int
) -> list[Chunk]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be non-negative and smaller than chunk_size")

    chunks: list[Chunk] = []
    step = chunk_size - chunk_overlap
    for document in documents:
        words = normalize_whitespace(document.text).split()
        if not words:
            continue
        chunk_index = 1
        for start in range(0, len(words), step):
            end = min(start + chunk_size, len(words))
            window = words[start:end]
            if not window:
                continue
            chunks.append(
                Chunk(
                    doc_id=document.doc_id,
                    chunk_id=f"{document.doc_id}-chunk-{chunk_index:02d}",
                    title=document.title,
                    text=" ".join(window),
                    token_count=len(window),
                )
            )
            chunk_index += 1
            if end >= len(words):
                break
    return chunks


class LexicalRetriever:
    def __init__(self, chunks: list[Chunk]):
        self._chunks = chunks
        self._chunk_term_counts = {
            chunk.chunk_id: count_content_tokens(chunk.text) for chunk in self._chunks
        }
        self._chunk_lengths = {
            chunk.chunk_id: max(sum(term_counts.values()), 1)
            for chunk, term_counts in (
                (chunk, self._chunk_term_counts[chunk.chunk_id]) for chunk in self._chunks
            )
        }
        self._idf = self._build_idf()

    def _build_idf(self) -> dict[str, float]:
        document_frequency: Counter[str] = Counter()
        for chunk_id in self._chunk_term_counts:
            for token in self._chunk_term_counts[chunk_id]:
                document_frequency[token] += 1

        total_chunks = max(len(self._chunks), 1)
        return {
            token: log((1 + total_chunks) / (1 + frequency)) + 1.0
            for token, frequency in document_frequency.items()
        }

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if top_k <= 0:
            return []

        query_terms = count_content_tokens(query)
        query_numbers = numeric_tokens(query)
        if not query_terms and not query_numbers:
            return []

        scored_chunks: list[tuple[float, Chunk]] = []
        for chunk in self._chunks:
            chunk_terms = self._chunk_term_counts[chunk.chunk_id]
            overlapping_terms = set(query_terms) & set(chunk_terms)
            chunk_numbers = numeric_tokens(chunk.text)
            overlapping_numbers = query_numbers & chunk_numbers

            if not overlapping_terms and not overlapping_numbers:
                continue

            numerator = 0.0
            for token in overlapping_terms:
                weight = self._idf.get(token, 1.0)
                numerator += min(query_terms[token], chunk_terms[token]) * weight

            denominator = sqrt(max(sum(query_terms.values()), 1)) * sqrt(
                self._chunk_lengths[chunk.chunk_id]
            )
            lexical_score = numerator / denominator if denominator else 0.0

            numeric_bonus = (
                len(overlapping_numbers) / len(query_numbers) if query_numbers else 0.0
            )
            total_score = lexical_score + (0.15 * numeric_bonus)

            if total_score > 0.0:
                scored_chunks.append((total_score, chunk))

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievedChunk(
                doc_id=chunk.doc_id,
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                text=chunk.text,
                score=round(score, 4),
                rank=rank,
            )
            for rank, (score, chunk) in enumerate(scored_chunks[:top_k], start=1)
        ]
