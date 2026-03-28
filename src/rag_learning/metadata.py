from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class DocumentMetadata:
    source_type: str
    module: str = "general"
    ticket_id: str | None = None
    change_id: str | None = None
    updated_at: str | None = None
    symbol: str | None = None
    language: str | None = None


@dataclass(slots=True)
class SearchFilters:
    source_type: str | None = None
    module: str | None = None
    ticket_id: str | None = None

    def is_empty(self) -> bool:
        return not any([self.source_type, self.module, self.ticket_id])

    def describe(self) -> str:
        parts: list[str] = []
        if self.source_type:
            parts.append(f"source_type={self.source_type}")
        if self.module:
            parts.append(f"module={self.module}")
        if self.ticket_id:
            parts.append(f"ticket_id={self.ticket_id}")
        return ", ".join(parts) if parts else "none"


def parse_markdown_with_front_matter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text.strip()

    metadata: dict[str, str] = {}
    closing_line_index: int | None = None
    for index, line in enumerate(lines[1:], start=1):
        stripped = line.strip()
        if stripped == "---":
            closing_line_index = index
            break
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        metadata[key.strip()] = value.strip()

    if closing_line_index is None:
        return {}, text.strip()

    body = "\n".join(lines[closing_line_index + 1 :]).strip()
    return metadata, body


def build_document_metadata(
    front_matter: dict[str, str],
    *,
    default_source_type: str,
    default_module: str = "general",
) -> DocumentMetadata:
    return DocumentMetadata(
        source_type=front_matter.get("source_type", default_source_type) or default_source_type,
        module=front_matter.get("module", default_module) or default_module,
        ticket_id=empty_to_none(front_matter.get("ticket_id")),
        change_id=empty_to_none(front_matter.get("change_id")),
        updated_at=empty_to_none(front_matter.get("updated_at")),
    )


def matches_filters(item: Any, filters: SearchFilters | None) -> bool:
    if filters is None or filters.is_empty():
        return True

    if filters.source_type and normalize_text(getattr(item, "source_type", None)) != normalize_text(filters.source_type):
        return False
    if filters.module and normalize_text(getattr(item, "module", None)) != normalize_text(filters.module):
        return False
    if filters.ticket_id and normalize_ticket_id(getattr(item, "ticket_id", None)) != normalize_ticket_id(filters.ticket_id):
        return False
    return True


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def normalize_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().casefold()


def normalize_ticket_id(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().upper()
