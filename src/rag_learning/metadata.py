from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class DocumentMetadata:
    source_type: str
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
        symbol=empty_to_none(front_matter.get("symbol")),
        language=empty_to_none(front_matter.get("language")),
        database_name=empty_to_none(front_matter.get("database_name")),
        table_name=empty_to_none(front_matter.get("table_name")),
        query_name=empty_to_none(front_matter.get("query_name")),
        service_name=empty_to_none(front_matter.get("service_name")),
    )


def empty_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None
