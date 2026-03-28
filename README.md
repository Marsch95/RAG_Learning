# RAG Learning Project

This project teaches Retrieval-Augmented Generation by building a small internal chatbot for a fictional software team.

The chatbot supports a fictional product called `Acme Checkout`.

It answers questions about:

- authentication behavior
- notification design
- retry logic for payment failures
- fake tickets that explain why changes happened
- fake change notes that link work back to tickets

The project is intentionally small and local.

- It uses synthetic markdown files.
- It runs with local Ollama models.
- It keeps the code readable for beginners.
- It grows in phases instead of jumping to enterprise architecture.

## Current State

Phase 2 is now implemented.

That means the chatbot can retrieve from:

- engineering docs in `data/docs`
- fake tickets in `data/tickets`
- fake change notes in `data/changes`

It also supports simple metadata-aware retrieval with filters for:

- `source_type`
- `module`
- `ticket_id`

This is enough to ask more realistic internal questions such as:

- Where is authentication handled?
- What does the notification module do?
- Why was retry logic added?
- Which ticket introduced retry logic?
- What do the docs say about the payment retry change?

## Project Structure

```text
RAG_Learning/
├── data/
│   ├── changes/
│   ├── docs/
│   ├── index/
│   └── tickets/
├── docs/
│   ├── phased-roadmap.md
│   └── technical-walkthrough.md
├── src/
│   └── rag_learning/
│       ├── chatbot.py
│       ├── cli.py
│       ├── config.py
│       ├── corpus.py
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

## Run Phase 2

### 1. Build the local index

```powershell
python -m rag_learning.cli index
```

This command now reads all three synthetic sources:

- `data/docs`
- `data/tickets`
- `data/changes`

It parses front matter metadata, chunks the text, creates embeddings, and writes the local JSON index to `data/index/index.json`.

### 2. Ask broad questions

```powershell
python -m rag_learning.cli ask "Why was retry logic added?"
python -m rag_learning.cli ask "Which ticket introduced retry logic?"
python -m rag_learning.cli ask "What does the notification module do?"
```

### 3. Ask filtered questions

Filter by source type:

```powershell
python -m rag_learning.cli ask "Why was retry logic added?" --source-type ticket
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
```

## How Phase 2 Works

The Phase 1 loop is still visible, but the input corpus is richer.

### Step 1: Load multiple source folders

The loader reads markdown files from docs, tickets, and change notes.

### Step 2: Parse front matter metadata

Each file can define fields such as:

- `title`
- `source_type`
- `module`
- `ticket_id`
- `change_id`
- `updated_at`

That metadata is carried into every chunk.

### Step 3: Chunk and embed as before

The chunking and embedding flow is still simple on purpose.

That keeps Phase 2 focused on understanding metadata, not on changing the retrieval algorithm.

### Step 4: Filter before ranking

If you pass CLI filters, the retriever narrows the candidate chunks before similarity ranking.

This is the first step toward more precise internal search.

### Step 5: Return richer citations

Each citation now shows not only the file path, but also the important metadata attached to that chunk.

That makes it easier to inspect whether retrieval found the right kind of evidence.

## Why Phase 2 Matters

Plain docs answer “what” questions reasonably well.

Tickets and change notes help answer “why” and “which change introduced this” questions.

That makes the learning project feel more like a real internal engineering assistant without making the code much more complex.

## Current Limitations

The project is still intentionally small.

- The index is still a JSON file.
- Retrieval still uses simple cosine similarity.
- There is no code retrieval yet.
- There is no evaluation loop yet.
- There is no database retrieval yet.

Those limitations are addressed in [docs/phased-roadmap.md](docs/phased-roadmap.md).

## Beginner Study Order

If you want to understand Phase 2 in a sensible order:

1. Read [docs/phased-roadmap.md](docs/phased-roadmap.md)
2. Read [docs/technical-walkthrough.md](docs/technical-walkthrough.md)
3. Read [src/rag_learning/metadata.py](src/rag_learning/metadata.py)
4. Read [src/rag_learning/corpus.py](src/rag_learning/corpus.py)
5. Read [src/rag_learning/retrieval.py](src/rag_learning/retrieval.py)
6. Read [src/rag_learning/chatbot.py](src/rag_learning/chatbot.py)
7. Read [src/rag_learning/cli.py](src/rag_learning/cli.py)
8. Run `index`
9. Run `ask` with and without filters

For a line-by-line explanation of the code, see [docs/technical-walkthrough.md](docs/technical-walkthrough.md).