from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from .code_loader import load_code_documents
from .config import CHANGES_DIR, CODEBASE_DIR, DATABASE_DIR, DATABASE_NOTES_DIR, DOCS_DIR, PROJECT_ROOT, TICKETS_DIR
from .db_loader import load_database_documents
from .metadata import build_document_metadata, parse_markdown_with_front_matter


@dataclass(slots=True)
class Document:
    text: str
    source_path: str
    title: str
    source_type: str = "doc"
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


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    text: str
    source_path: str
    title: str
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

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


def load_project_documents() -> list[Document]:
    documents: list[Document] = []
    sources = (
        (DOCS_DIR, "doc"),
        (TICKETS_DIR, "ticket"),
        (CHANGES_DIR, "change"),
        (DATABASE_NOTES_DIR, "db_note"),
    )

    for directory, source_type in sources:
        if directory.exists():
            documents.extend(
                load_markdown_documents(directory, default_source_type=source_type)
            )

    if CODEBASE_DIR.exists():
        code_documents = load_code_documents(CODEBASE_DIR, PROJECT_ROOT)
        documents.extend(
            Document(
                text=document.text,
                source_path=document.source_path,
                title=document.title,
                source_type=document.source_type,
                module=document.module,
                ticket_id=document.ticket_id,
                updated_at=document.updated_at,
                symbol=document.symbol,
                language=document.language,
                database_name=document.database_name,
                table_name=document.table_name,
                query_name=document.query_name,
                service_name=document.service_name,
            )
            for document in code_documents
        )

    if DATABASE_DIR.exists():
        database_documents = load_database_documents(DATABASE_DIR, PROJECT_ROOT)
        documents.extend(
            Document(
                text=document.text,
                source_path=document.source_path,
                title=document.title,
                source_type=document.source_type,
                module=document.module,
                updated_at=document.updated_at,
                language=document.language,
                database_name=document.database_name,
                table_name=document.table_name,
                query_name=document.query_name,
                service_name=document.service_name,
            )
            for document in database_documents
        )

    return documents


def load_markdown_documents(
    docs_dir: Path,
    *,
    default_source_type: str,
) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(docs_dir.glob("*.md")):
        raw_text = path.read_text(encoding="utf-8")
        front_matter, text = parse_markdown_with_front_matter(raw_text)
        metadata = build_document_metadata(
            front_matter,
            default_source_type=default_source_type,
        )
        title = (
            front_matter.get("title")
            or first_heading(text)
            or path.stem.replace("_", " ").replace("-", " ").title()
        )
        documents.append(
            Document(
                text=text,
                source_path=str(path.relative_to(PROJECT_ROOT)),
                title=title,
                source_type=metadata.source_type,
                module=metadata.module,
                ticket_id=metadata.ticket_id,
                change_id=metadata.change_id,
                updated_at=metadata.updated_at,
                symbol=metadata.symbol,
                language=metadata.language,
                database_name=metadata.database_name,
                table_name=metadata.table_name,
                query_name=metadata.query_name,
                service_name=metadata.service_name,
            )
        )
    return documents


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def chunk_documents(
    documents: Iterable[Document],
    *,
    chunk_size: int,
    chunk_overlap: int,
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        splitter = split_code_text if document.language in {"python", "sql"} or document.source_type in {"code", "db_schema", "db_query"} else split_text
        for index, chunk_text in enumerate(splitter(document.text, chunk_size, chunk_overlap)):
            chunks.append(
                Chunk(
                    chunk_id=build_chunk_id(document, index + 1),
                    text=chunk_text,
                    source_path=document.source_path,
                    title=document.title,
                    source_type=document.source_type,
                    module=document.module,
                    ticket_id=document.ticket_id,
                    change_id=document.change_id,
                    updated_at=document.updated_at,
                    symbol=document.symbol,
                    language=document.language,
                    database_name=document.database_name,
                    table_name=document.table_name,
                    query_name=document.query_name,
                    service_name=document.service_name,
                )
            )
    return chunks


def build_chunk_id(document: Document, chunk_number: int) -> str:
    base_parts = [document.source_type, Path(document.source_path).stem]
    if document.symbol:
        base_parts.append(document.symbol)
    elif document.table_name:
        base_parts.append(document.table_name)
    elif document.query_name:
        base_parts.append(document.query_name)
    normalized_parts = [normalize_identifier(part) for part in base_parts]
    return f"{'-'.join(normalized_parts)}-chunk-{chunk_number}"


def normalize_identifier(value: str) -> str:
    normalized_characters = [character.lower() if character.isalnum() else "-" for character in value]
    normalized = "".join(normalized_characters)
    while "--" in normalized:
        normalized = normalized.replace("--", "-")
    return normalized.strip("-")


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    start = 0
    while start < len(cleaned_text):
        end = min(len(cleaned_text), start + chunk_size)
        if end < len(cleaned_text):
            boundary = cleaned_text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = cleaned_text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned_text):
            break

        start = max(0, end - chunk_overlap)

    return chunks


def split_code_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    lines = text.splitlines()
    if not lines:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[str] = []
    current_lines: list[str] = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1
        if current_lines and current_length + line_length > chunk_size:
            chunks.append("\n".join(current_lines).strip())
            overlap_lines = collect_overlap_lines(current_lines, chunk_overlap)
            current_lines = overlap_lines.copy()
            current_length = sum(len(existing_line) + 1 for existing_line in current_lines)

        current_lines.append(line)
        current_length += line_length

    if current_lines:
        chunks.append("\n".join(current_lines).strip())

    return [chunk for chunk in chunks if chunk]


def collect_overlap_lines(lines: list[str], chunk_overlap: int) -> list[str]:
    overlap_lines: list[str] = []
    overlap_length = 0
    for line in reversed(lines):
        line_length = len(line) + 1
        if overlap_lines and overlap_length + line_length > chunk_overlap:
            break
        overlap_lines.insert(0, line)
        overlap_length += line_length
    return overlap_lines