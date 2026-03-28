from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(slots=True)
class Document:
    text: str
    source_path: str
    title: str
    source_type: str = "doc"


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    text: str
    source_path: str
    title: str
    source_type: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_markdown_documents(docs_dir: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        title = first_heading(text) or path.stem.replace("_", " ").title()
        documents.append(
            Document(
                text=text,
                source_path=str(path.relative_to(docs_dir.parent.parent)),
                title=title,
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
        for index, chunk_text in enumerate(split_text(document.text, chunk_size, chunk_overlap)):
            chunks.append(
                Chunk(
                    chunk_id=f"{Path(document.source_path).stem}-chunk-{index + 1}",
                    text=chunk_text,
                    source_path=document.source_path,
                    title=document.title,
                    source_type=document.source_type,
                )
            )
    return chunks


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