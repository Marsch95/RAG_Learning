from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

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
    top_k: int,
    filters: SearchFilters | None = None,
) -> list[tuple[float, IndexedChunk]]:
    scored_chunks = [
        (cosine_similarity(query_embedding, chunk.embedding), chunk)
        for chunk in indexed_chunks
        if matches_filters(chunk, filters)
    ]
    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    return scored_chunks[:top_k]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors must have the same length.")

    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return numerator / (left_norm * right_norm)