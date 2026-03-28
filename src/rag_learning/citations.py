from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(slots=True)
class Citation:
    chunk_id: str
    title: str
    source_path: str
    source_type: str
    module: str
    score: float
    ticket_id: str | None = None
    change_id: str | None = None
    updated_at: str | None = None
    symbol: str | None = None
    language: str | None = None
    database_name: str | None = None
    table_name: str | None = None
    query_name: str | None = None
    service_name: str | None = None

    def metadata_parts(self) -> list[str]:
        parts = [f"module={self.module}"]
        if self.symbol:
            parts.append(f"symbol={self.symbol}")
        if self.ticket_id:
            parts.append(f"ticket_id={self.ticket_id}")
        if self.change_id:
            parts.append(f"change_id={self.change_id}")
        if self.language:
            parts.append(f"language={self.language}")
        if self.database_name:
            parts.append(f"database_name={self.database_name}")
        if self.table_name:
            parts.append(f"table_name={self.table_name}")
        if self.query_name:
            parts.append(f"query_name={self.query_name}")
        if self.service_name:
            parts.append(f"service_name={self.service_name}")
        if self.updated_at:
            parts.append(f"updated_at={self.updated_at}")
        return parts

    def prompt_label(self) -> str:
        return (
            f"{self.chunk_id} | {self.source_type} | {self.source_path} | "
            f"similarity={self.score:.3f} | {', '.join(self.metadata_parts())}"
        )

    def display_line(self) -> str:
        return (
            f"{self.title} | {self.source_path} | similarity={self.score:.3f} | "
            f"{', '.join(self.metadata_parts())}"
        )


@dataclass(slots=True)
class CitationGroup:
    source_type: str
    citations: list[Citation]

    @property
    def heading(self) -> str:
        return source_type_heading(self.source_type)


def build_citations(ranked: list[tuple[float, object]]) -> list[Citation]:
    citations: list[Citation] = []
    for score, chunk in ranked:
        citations.append(
            Citation(
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                source_path=chunk.source_path,
                source_type=chunk.source_type,
                module=chunk.module,
                score=score,
                ticket_id=chunk.ticket_id,
                change_id=chunk.change_id,
                updated_at=chunk.updated_at,
                symbol=chunk.symbol,
                language=chunk.language,
                database_name=chunk.database_name,
                table_name=chunk.table_name,
                query_name=chunk.query_name,
                service_name=chunk.service_name,
            )
        )
    return citations


def group_citations(citations: list[Citation]) -> list[CitationGroup]:
    grouped: dict[str, list[Citation]] = defaultdict(list)
    for citation in citations:
        grouped[citation.source_type].append(citation)

    ordered_source_types = sorted(grouped, key=source_type_sort_key)
    return [CitationGroup(source_type=source_type, citations=grouped[source_type]) for source_type in ordered_source_types]


def source_type_heading(source_type: str) -> str:
    headings = {
        "doc": "Documentation",
        "ticket": "Tickets",
        "change": "Change Notes",
        "code": "Code",
        "db_note": "Database Notes",
        "db_schema": "Database Schema",
        "db_query": "Database Queries",
    }
    return headings.get(source_type, source_type.title())


def source_type_sort_key(source_type: str) -> tuple[int, str]:
    order = {"doc": 0, "ticket": 1, "change": 2, "code": 3, "db_note": 4, "db_schema": 5, "db_query": 6}
    return (order.get(source_type, 99), source_type)