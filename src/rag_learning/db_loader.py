from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .metadata import DocumentMetadata, empty_to_none


@dataclass(slots=True)
class DatabaseDocument:
    text: str
    source_path: str
    title: str
    module: str
    database_name: str | None = None
    table_name: str | None = None
    query_name: str | None = None
    service_name: str | None = None
    updated_at: str | None = None
    language: str = "sql"
    source_type: str = "db_schema"


def load_database_documents(database_dir: Path, project_root: Path) -> list[DatabaseDocument]:
    documents: list[DatabaseDocument] = []

    for path in sorted((database_dir / "schema").glob("*.sql")):
        documents.append(load_database_document(path, project_root, default_source_type="db_schema"))

    for path in sorted((database_dir / "queries").glob("*.sql")):
        documents.append(load_database_document(path, project_root, default_source_type="db_query"))

    return documents


def load_database_document(
    path: Path,
    project_root: Path,
    *,
    default_source_type: str,
) -> DatabaseDocument:
    raw_text = path.read_text(encoding="utf-8")
    metadata, sql_text = parse_sql_with_comment_metadata(raw_text)
    document_metadata = build_database_metadata(metadata, default_source_type=default_source_type)
    title = metadata.get("title") or path.stem.replace("_", " ").replace("-", " ").title()
    summary = summarize_database_document(document_metadata, path.stem)

    text = "\n".join(
        [
            summary,
            "SQL:",
            sql_text.strip(),
        ]
    ).strip()

    return DatabaseDocument(
        text=text,
        source_path=str(path.relative_to(project_root)),
        title=title,
        module=document_metadata.module,
        database_name=document_metadata.database_name,
        table_name=document_metadata.table_name,
        query_name=document_metadata.query_name,
        service_name=document_metadata.service_name,
        updated_at=document_metadata.updated_at,
        source_type=document_metadata.source_type,
    )


def parse_sql_with_comment_metadata(text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    body_lines: list[str] = []
    header_complete = False

    for line in text.splitlines():
        stripped = line.strip()
        if not header_complete and stripped.startswith("--") and ":" in stripped[2:]:
            key, value = stripped[2:].split(":", 1)
            metadata[key.strip()] = value.strip()
            continue

        if not header_complete and not stripped:
            header_complete = True
            continue

        header_complete = True
        body_lines.append(line)

    return metadata, "\n".join(body_lines).strip()


def build_database_metadata(
    metadata: dict[str, str],
    *,
    default_source_type: str,
) -> DocumentMetadata:
    return DocumentMetadata(
        source_type=metadata.get("source_type", default_source_type) or default_source_type,
        module=metadata.get("module", "general") or "general",
        updated_at=empty_to_none(metadata.get("updated_at")),
        language="sql",
        database_name=empty_to_none(metadata.get("database_name")),
        table_name=empty_to_none(metadata.get("table_name")),
        query_name=empty_to_none(metadata.get("query_name")),
        service_name=empty_to_none(metadata.get("service_name")),
    )


def summarize_database_document(metadata: DocumentMetadata, file_stem: str) -> str:
    parts = [f"Database file: {file_stem}.sql"]
    if metadata.database_name:
        parts.append(f"Database: {metadata.database_name}")
    if metadata.table_name:
        parts.append(f"Table: {metadata.table_name}")
    if metadata.query_name:
        parts.append(f"Query name: {metadata.query_name}")
    if metadata.service_name:
        parts.append(f"Service: {metadata.service_name}")
    parts.append(f"Module: {metadata.module}")
    parts.append(f"Source type: {metadata.source_type}")
    return "\n".join(parts)