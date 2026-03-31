from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
import re

from .config import INDEX_FILE, ensure_index_dir
from .corpus import Chunk
from .filters import SearchFilters, matches_filters


@dataclass(slots=True)
class IndexedChunk:
    chunk_id: str
    text: str
    source_path: str
    title: str
    source_type: str
    embedding: list[float]
    module: str = "general"
    ticket_id: str | None = None
    change_id: str | None = None
    updated_at: str | None = None
    symbol: str | None = None
    language: str | None = None
    database_name: str | None = None
    table_name: str | None = None
    query_name: str | None = None
    service_name: str | None = None

    @classmethod
    def from_chunk(cls, chunk: Chunk, embedding: list[float]) -> "IndexedChunk":
        return cls(**chunk.to_dict(), embedding=embedding)

    def to_dict(self) -> dict:
        return asdict(self)


def save_index(chunks: list[IndexedChunk], path: Path = INDEX_FILE) -> None:
    ensure_index_dir()
    payload = {"chunks": [chunk.to_dict() for chunk in chunks]}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_index(path: Path = INDEX_FILE) -> list[IndexedChunk]:
    if not path.exists():
        raise FileNotFoundError(
            "Index not found. Run 'python -m rag_learning.cli index' first."
        )

    payload = json.loads(path.read_text(encoding="utf-8"))
    return [IndexedChunk(**item) for item in payload.get("chunks", [])]


def rank_chunks(
    query_embedding: list[float],
    indexed_chunks: list[IndexedChunk],
    *,
    query_text: str | None = None,
    top_k: int,
    filters: SearchFilters | None = None,
    vector_weight: float = 0.7,
    bm25_weight: float = 0.3,
) -> list[tuple[float, IndexedChunk]]:
    filtered_chunks = [chunk for chunk in indexed_chunks if matches_filters(chunk, filters)]
    if not filtered_chunks:
        return []

    vector_scores = [cosine_similarity(query_embedding, chunk.embedding) for chunk in filtered_chunks]
    lexical_scores = bm25_scores(query_text or "", filtered_chunks)
    normalized_vector_scores = normalize_vector_scores(vector_scores)
    normalized_lexical_scores = normalize_lexical_scores(lexical_scores)
    vector_share, lexical_share = normalize_weight_pair(vector_weight, bm25_weight)

    scored_chunks = [
        (
            (vector_share * normalized_vector_scores[index])
            + (lexical_share * normalized_lexical_scores[index]),
            chunk,
        )
        for index, chunk in enumerate(filtered_chunks)
    ]
    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return scored_chunks[:top_k]


TOKEN_PATTERN = re.compile(r"[a-z0-9_]+(?:-[a-z0-9_]+)*")


def bm25_scores(
    query_text: str,
    chunks: list[IndexedChunk],
    *,
    k1: float = 1.5,
    b: float = 0.75,
) -> list[float]:
    query_tokens = tokenize_text(query_text)
    if not query_tokens or not chunks:
        return [0.0 for _ in chunks]

    tokenized_documents = [tokenize_text(build_lexical_text(chunk)) for chunk in chunks]
    document_frequencies: Counter[str] = Counter()
    term_frequencies: list[Counter[str]] = []
    document_lengths: list[int] = []

    for tokens in tokenized_documents:
        counts = Counter(tokens)
        term_frequencies.append(counts)
        document_lengths.append(len(tokens))
        for term in counts:
            document_frequencies[term] += 1

    average_length = sum(document_lengths) / len(document_lengths) if document_lengths else 0.0
    if average_length == 0:
        return [0.0 for _ in chunks]

    query_term_counts = Counter(query_tokens)
    document_count = len(chunks)
    scores: list[float] = []

    for document_length, counts in zip(document_lengths, term_frequencies):
        score = 0.0
        for term, query_count in query_term_counts.items():
            term_frequency = counts.get(term, 0)
            if term_frequency == 0:
                continue

            document_frequency = document_frequencies[term]
            inverse_document_frequency = math.log(
                1 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            normalization = k1 * (1 - b + b * (document_length / average_length))
            score += query_count * inverse_document_frequency * (
                (term_frequency * (k1 + 1)) / (term_frequency + normalization)
            )
        scores.append(score)

    return scores


def tokenize_text(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.casefold())


def build_lexical_text(chunk: IndexedChunk) -> str:
    parts = [
        chunk.title,
        chunk.source_path,
        chunk.source_type,
        chunk.module,
        chunk.chunk_id,
        chunk.text,
        chunk.ticket_id,
        chunk.change_id,
        chunk.symbol,
        chunk.language,
        chunk.database_name,
        chunk.table_name,
        chunk.query_name,
        chunk.service_name,
    ]
    return "\n".join(part for part in parts if part)


def normalize_vector_scores(scores: list[float]) -> list[float]:
    return [max(0.0, min(1.0, (score + 1.0) / 2.0)) for score in scores]


def normalize_lexical_scores(scores: list[float]) -> list[float]:
    max_score = max(scores, default=0.0)
    if max_score <= 0:
        return [0.0 for _ in scores]
    return [score / max_score for score in scores]


def normalize_weight_pair(vector_weight: float, bm25_weight: float) -> tuple[float, float]:
    total = max(vector_weight + bm25_weight, 0.0)
    if total == 0:
        return (0.5, 0.5)
    return (vector_weight / total, bm25_weight / total)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same length.")

    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return numerator / (left_norm * right_norm)