from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SearchFilters:
    source_types: tuple[str, ...] = field(default_factory=tuple)
    module: str | None = None
    ticket_id: str | None = None
    change_id: str | None = None
    symbol: str | None = None
    language: str | None = None
    updated_after: str | None = None

    def is_empty(self) -> bool:
        return not any(
            [
                self.source_types,
                self.module,
                self.ticket_id,
                self.change_id,
                self.symbol,
                self.language,
                self.updated_after,
            ]
        )

    def describe(self) -> str:
        parts: list[str] = []
        if self.source_types:
            parts.append(f"source_types={', '.join(self.source_types)}")
        if self.module:
            parts.append(f"module={self.module}")
        if self.ticket_id:
            parts.append(f"ticket_id={self.ticket_id}")
        if self.change_id:
            parts.append(f"change_id={self.change_id}")
        if self.symbol:
            parts.append(f"symbol~={self.symbol}")
        if self.language:
            parts.append(f"language={self.language}")
        if self.updated_after:
            parts.append(f"updated_after={self.updated_after}")
        return ", ".join(parts) if parts else "none"

    @classmethod
    def from_cli(
        cls,
        *,
        source_types: list[str] | None = None,
        module: str | None = None,
        ticket_id: str | None = None,
        change_id: str | None = None,
        symbol: str | None = None,
        language: str | None = None,
        updated_after: str | None = None,
    ) -> "SearchFilters":
        return cls(
            source_types=normalize_source_types(source_types),
            module=clean_text(module),
            ticket_id=normalize_ticket_id(ticket_id),
            change_id=clean_text(change_id),
            symbol=clean_text(symbol),
            language=normalize_text(language),
            updated_after=clean_text(updated_after),
        )


def matches_filters(item: Any, filters: SearchFilters | None) -> bool:
    if filters is None or filters.is_empty():
        return True

    if filters.source_types:
        item_source_type = normalize_text(getattr(item, "source_type", None))
        if item_source_type not in filters.source_types:
            return False

    if filters.module and normalize_text(getattr(item, "module", None)) != normalize_text(filters.module):
        return False

    if filters.ticket_id and normalize_ticket_id(getattr(item, "ticket_id", None)) != normalize_ticket_id(filters.ticket_id):
        return False

    if filters.change_id and normalize_text(getattr(item, "change_id", None)) != normalize_text(filters.change_id):
        return False

    if filters.symbol:
        item_symbol = normalize_text(getattr(item, "symbol", None))
        if item_symbol is None or normalize_text(filters.symbol) not in item_symbol:
            return False

    if filters.language and normalize_text(getattr(item, "language", None)) != normalize_text(filters.language):
        return False

    if filters.updated_after:
        item_updated_at = clean_text(getattr(item, "updated_at", None))
        if item_updated_at is None or item_updated_at < filters.updated_after:
            return False

    return True


def normalize_source_types(source_types: list[str] | None) -> tuple[str, ...]:
    if not source_types:
        return ()
    normalized = []
    for source_type in source_types:
        cleaned = normalize_text(source_type)
        if cleaned and cleaned not in normalized:
            normalized.append(cleaned)
    return tuple(normalized)


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def normalize_text(value: str | None) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.casefold()


def normalize_ticket_id(value: str | None) -> str | None:
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    return cleaned.upper()