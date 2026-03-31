# RAG Learning Project

This repository is a small, local Retrieval-Augmented Generation project built around a fictional engineering domain called `Acme Checkout`.

It is designed to teach core RAG ideas without hiding them behind a framework. The assistant retrieves from synthetic documentation, fake tickets, change notes, source code, and SQL artifacts, then answers with citations.

## Why This Repo Exists

Most RAG examples stop at "load some PDFs and ask a question."

This project is trying to show something more realistic while staying readable for beginners:

- multi-source retrieval instead of one document folder
- metadata-aware filtering
- source code retrieval
- SQL schema and query retrieval
- a small evaluation loop
- a narrow live-data demo for exact-value database questions

The repo stays intentionally local.

- no cloud setup
- no real Jira dependency
- no real company codebase
- no enterprise infrastructure required to run it

## What The Assistant Can Answer

Examples:

- Where is authentication handled?
- What does the notification module do?
- Why was retry logic added?
- Which ticket introduced this change?
- Which function performs the retry loop?
- Which table stores notification delivery history?
- Which query finds failed payment attempts?
- Which code module writes notification delivery records and which table stores them?

## Technical Highlights

- Source types: docs, tickets, change notes, code, database notes, schema, and query files
- Retrieval: local embeddings plus cosine ranking over a JSON index
- Filtering: `source_type`, `module`, `ticket_id`, `change_id`, `symbol`, `language`, `database_name`, `table_name`, `query_name`, `service_name`, and `updated_after`
- Evidence: grouped citations with similarity scores and structured metadata
- Evaluation: deterministic retrieval checks from `eval/questions.json`
- Live demo: a tiny allowlisted SQLite query path for exact-value operational questions

## Project Layout

```text
RAG_Learning/
├── data/
│   ├── changes/
│   ├── codebase/
│   ├── database/
│   ├── docs/
│   └── tickets/
├── docs/
│   ├── evaluation-guide.md
│   ├── enterprise-setup-guide.md
│   ├── phase-7-context-vs-retrieval.md
│   ├── phased-roadmap.md
│   ├── system-roadmap.md
│   └── technical-walkthrough.md
├── eval/
│   └── questions.json
├── src/
│   └── rag_learning/
├── tests/
├── pyproject.toml
└── requirements.txt
```

## Quick Start

Requirements:

- Python 3.11+
- Ollama running locally
- one chat model
- one embedding model

Example model setup:

```powershell
ollama pull gemma3:latest
ollama pull embeddinggemma:latest
```

Install from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Optional model overrides:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_CHAT_MODEL = "gemma3:latest"
$env:OLLAMA_EMBED_MODEL = "embeddinggemma:latest"
```

Build the index:

```powershell
python -m rag_learning.cli index
```

Ask a question:

```powershell
python -m rag_learning.cli ask "Why was retry logic added?"
python -m rag_learning.cli ask "Which function performs the retry loop?" --source-type code
python -m rag_learning.cli ask "Which table stores notification delivery history?" --source-type db_schema
```

Run the evaluation set:

```powershell
python -m rag_learning.cli evaluate
```

Prepare the local SQLite demo and ask a live question:

```powershell
python -m rag_learning.cli reset-db
python -m rag_learning.cli ask-live "Show the latest 2 failed payment attempts."
```

Run the tests:

```powershell
python -m unittest discover -s tests -v
```

## Core Documents

These are the main documents worth reading if you want to understand the project quickly.

- [docs/technical-walkthrough.md](docs/technical-walkthrough.md): code-oriented explanation of how indexing, retrieval, citations, evaluation, and the live database demo work
- [docs/evaluation-guide.md](docs/evaluation-guide.md): how the retrieval evaluation set is structured and how to interpret it
- [docs/phased-roadmap.md](docs/phased-roadmap.md): how the project grows from a minimal RAG demo to a broader engineering knowledge assistant
- [docs/system-roadmap.md](docs/system-roadmap.md): design direction for a stronger multi-source version

Additional architecture notes:

- [docs/phase-7-context-vs-retrieval.md](docs/phase-7-context-vs-retrieval.md)
- [docs/enterprise-setup-guide.md](docs/enterprise-setup-guide.md)

## What I Would Improve Next

This repository is intentionally simple, so several things are still deliberately lightweight.

- the index is a local JSON file
- hybrid retrieval is intentionally simple and does not yet have a dedicated re-ranker
- evaluation is small and mostly retrieval-focused
- the live database path is tightly scoped to a few safe patterns
- there is no web UI or API service layer

Those limitations are discussed in [docs/system-roadmap.md](docs/system-roadmap.md) and [docs/enterprise-setup-guide.md](docs/enterprise-setup-guide.md).

## Portfolio Note

This is a teaching project, but it is also structured to show engineering judgment:

- small surface area
- readable modules
- explicit metadata model
- deterministic evaluation inputs
- synthetic but coherent cross-source data
- clear separation between retrieval knowledge and live operational queries