from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = DATA_DIR / "docs"
TICKETS_DIR = DATA_DIR / "tickets"
CHANGES_DIR = DATA_DIR / "changes"
CODEBASE_DIR = DATA_DIR / "codebase"
INDEX_DIR = DATA_DIR / "index"
INDEX_FILE = INDEX_DIR / "index.json"


@dataclass(slots=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "gemma3:latest")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "embeddinggemma:latest")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
    top_k: int = int(os.getenv("RAG_TOP_K", "3"))


def ensure_index_dir() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)