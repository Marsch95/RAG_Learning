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
DATABASE_DIR = DATA_DIR / "database"
DATABASE_NOTES_DIR = DATABASE_DIR / "notes"
DATABASE_RUNTIME_DIR = DATABASE_DIR / "runtime"
SQLITE_DB_FILE = DATABASE_RUNTIME_DIR / "acme_checkout.sqlite"
SQLITE_SEED_FILE = DATABASE_RUNTIME_DIR / "seed.sql"
INDEX_DIR = DATA_DIR / "index"
INDEX_FILE = INDEX_DIR / "index.json"
EVAL_DIR = PROJECT_ROOT / "eval"
EVAL_QUESTIONS_FILE = EVAL_DIR / "questions.json"
EVAL_REPORT_FILE = EVAL_DIR / "last-report.json"


@dataclass(slots=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    chat_model: str = os.getenv("OLLAMA_CHAT_MODEL", "gemma3:latest")
    embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "embeddinggemma:latest")
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))
    top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    vector_weight: float = float(os.getenv("RAG_VECTOR_WEIGHT", "0.7"))
    bm25_weight: float = float(os.getenv("RAG_BM25_WEIGHT", "0.3"))


def ensure_index_dir() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def ensure_eval_dir() -> None:
    EVAL_DIR.mkdir(parents=True, exist_ok=True)