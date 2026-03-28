# RAG Learning Project

This project teaches Retrieval-Augmented Generation by building a small internal chatbot for a fictional software team.

The chatbot supports a fictional product called `Acme Checkout`.

It answers questions about:

- authentication behavior
- notification design
- retry logic for payment failures
- fake tickets that explain why changes happened
- fake change notes that link work back to tickets
- synthetic source code that shows where behavior is implemented

The project is intentionally small and local.

- It uses synthetic markdown files.
- It runs with local Ollama models.
- It keeps the code readable for beginners.
- It grows in phases instead of jumping to enterprise architecture.

## Current State

Phase 4 is now implemented.

That means the chatbot can retrieve from:

- engineering docs in `data/docs`
- fake tickets in `data/tickets`
- fake change notes in `data/changes`
- synthetic Python files in `data/codebase`

It also supports simple metadata-aware retrieval with filters for:

- `source_type`
- `module`
- `ticket_id`
- `change_id`
- `symbol`
- `language`
- `updated_after`

Phase 4 also improves evidence presentation.

- citations are grouped by source type
- each evidence line shows similarity and important metadata
- mixed-source answers are easier to inspect

This is enough to ask more realistic internal questions such as:

- Where is authentication handled?
- What does the notification module do?
- Why was retry logic added?
- Which ticket introduced retry logic?
- What do the docs say about the payment retry change?
- Which function performs the retry loop?
- Which code module sends receipts?

## Project Structure

```text
RAG_Learning/
├── data/
│   ├── changes/
│   ├── codebase/
│   ├── docs/
│   ├── index/
│   └── tickets/
├── docs/
│   ├── phased-roadmap.md
│   └── technical-walkthrough.md
├── src/
│   └── rag_learning/
│       ├── chatbot.py
│       ├── citations.py
│       ├── cli.py
│       ├── code_loader.py
│       ├── config.py
│       ├── corpus.py
│       ├── filters.py
│       ├── metadata.py
│       ├── ollama_client.py
│       └── retrieval.py
├── requirements.txt
├── pyproject.toml
└── AGENTS.md
```

## Requirements

- Python 3.11+
- Ollama running locally
- one chat model available in Ollama
- one embedding model available in Ollama

Example setup:

```powershell
ollama pull gemma3:latest
ollama pull embeddinggemma:latest
```

## Installation

Run these commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

The editable install matters because this repository uses a `src/` layout.

## Configure Models

Default settings:

- chat model: `gemma3:latest`
- embedding model: `embeddinggemma:latest`
- Ollama URL: `http://localhost:11434`

Optional overrides:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_CHAT_MODEL = "gemma3:latest"
$env:OLLAMA_EMBED_MODEL = "embeddinggemma:latest"
```

## Run Phase 4

### 1. Build the local index

```powershell
python -m rag_learning.cli index
```

This command now reads all four synthetic sources:

- `data/docs`
- `data/tickets`
- `data/changes`
- `data/codebase`

It parses markdown metadata, loads Python code files, creates code-aware chunks, creates embeddings, and writes the local JSON index to `data/index/index.json`.

### 2. Ask broad questions

```powershell
python -m rag_learning.cli ask "Why was retry logic added?"
python -m rag_learning.cli ask "Which ticket introduced retry logic?"
python -m rag_learning.cli ask "What does the notification module do?"
python -m rag_learning.cli ask "Where is authentication handled?"
python -m rag_learning.cli ask "Which function performs the retry loop?" --source-type code
```

### 3. Ask more precise filtered questions

Filter by source type:

```powershell
python -m rag_learning.cli ask "Why was retry logic added?" --source-type ticket
python -m rag_learning.cli ask "Which code module sends receipts?" --source-type code
```

Filter across multiple source types:

```powershell
python -m rag_learning.cli ask "Which ticket or change note introduced retry logic?" --source-type ticket --source-type change
```

Filter by module:

```powershell
python -m rag_learning.cli ask "What changed in the notification module?" --module notifications
```

Filter by ticket:

```powershell
python -m rag_learning.cli ask "What changed for this ticket?" --ticket-id TKT-204
```

You can combine filters:

```powershell
python -m rag_learning.cli ask "What do the docs say about this ticket?" --source-type doc --ticket-id TKT-204
python -m rag_learning.cli ask "Which retry helper symbol is relevant here?" --source-type code --module payments --symbol retry
python -m rag_learning.cli ask "What changed after the retry ticket landed?" --updated-after 2026-03-10
python -m rag_learning.cli ask "Show me Python evidence for notification routing" --source-type code --language python --module notifications
```

### 4. Inspect grouped evidence

Phase 4 changes the terminal output.

Instead of one flat citation list, the CLI now groups evidence by source type and shows a cleaner line for each retrieved chunk.

That makes it easier to see whether the answer relied on docs, tickets, change notes, code, or a mixture.

## How Phase 4 Works

The Phase 1, Phase 2, and Phase 3 pieces are still visible, but Phase 4 adds a cleaner search layer on top of them.

### Step 1: Load multiple source folders

The loader reads markdown files from docs, tickets, and change notes, then loads Python files from the synthetic codebase.

### Step 2: Parse markdown metadata and code metadata

Each file can define fields such as:

- `title`
- `source_type`
- `module`
- `ticket_id`
- `change_id`
- `updated_at`

That metadata is carried into every chunk.

Code files also carry metadata such as:

- `source_type=code`
- `module`
- `symbol`
- `language=python`

### Step 3: Split code differently from markdown

Markdown files still use the simple text chunker.

Code files use a line-aware splitter so indentation and function boundaries stay easier to read in retrieved snippets.

The embedding step still stays simple on purpose.

### Step 4: Include code overviews and symbol documents

The code loader creates:

- one overview document for each Python file
- one symbol document for each top-level class or function

That means retrieval can match both broad code questions and specific symbol questions.

### Step 5: Filter before ranking

If you pass CLI filters, the retriever narrows the candidate chunks before similarity ranking.

Phase 4 makes those filters more expressive.

You can now narrow retrieval with:

- one or more source types
- one module
- one ticket ID
- one change ID
- symbol text for code searches
- language such as `python`
- an `updated_after` date

This makes the assistant less noisy as the local corpus grows.

### Step 6: Return grouped evidence with clearer citations

Each evidence line now shows:

- the document title
- the source path
- the similarity score
- important metadata such as module, ticket ID, change ID, symbol, and language

The CLI also groups those lines by source type so mixed-source retrieval is easier to inspect.

## Why Phase 4 Matters

Plain docs answer “what” questions reasonably well.

Tickets and change notes help answer “why” and “which change introduced this” questions.

Code retrieval answers “where is this implemented?” questions.

Phase 4 makes those answers easier to trust because you can narrow retrieval and inspect the supporting evidence more quickly.

## Current Limitations

The project is still intentionally small.

- The index is still a JSON file.
- Retrieval still uses simple cosine similarity.
- There is no evaluation loop yet.
- There is no database retrieval yet.

Those limitations are addressed in [docs/phased-roadmap.md](docs/phased-roadmap.md).

## Beginner Study Order

If you want to understand Phase 4 in a sensible order:

1. Read [docs/phased-roadmap.md](docs/phased-roadmap.md)
2. Read [docs/technical-walkthrough.md](docs/technical-walkthrough.md)
3. Read [src/rag_learning/code_loader.py](src/rag_learning/code_loader.py)
4. Read [src/rag_learning/metadata.py](src/rag_learning/metadata.py)
5. Read [src/rag_learning/corpus.py](src/rag_learning/corpus.py)
6. Read [src/rag_learning/filters.py](src/rag_learning/filters.py)
7. Read [src/rag_learning/retrieval.py](src/rag_learning/retrieval.py)
8. Read [src/rag_learning/citations.py](src/rag_learning/citations.py)
9. Read [src/rag_learning/chatbot.py](src/rag_learning/chatbot.py)
10. Read [src/rag_learning/cli.py](src/rag_learning/cli.py)
11. Run `index`
12. Run `ask` with and without filters such as `--source-type code --symbol retry`

For a line-by-line explanation of the code, see [docs/technical-walkthrough.md](docs/technical-walkthrough.md).