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
- synthetic SQL schema and query files that show where operational data would live

The project is intentionally small and local.

- It uses synthetic markdown files.
- It runs with local Ollama models.
- It keeps the code readable for beginners.
- It grows in phases instead of jumping to enterprise architecture.

## Current State

Phase 6 is now implemented.

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

Phase 5 adds a small evaluation loop.

- a labeled question set lives in `eval/questions.json`
- a new `evaluate` command scores retrieval behavior
- detailed JSON reports make regression review easier

Phase 6 adds the professional roadmap.

- `docs/system-roadmap.md` explains how this small project could grow into a stronger multi-source engineering knowledge assistant
- the roadmap now includes database retrieval as the next major source type
- the repository ends with a design handoff instead of pretending the learning project is already production-ready

That first database step is now implemented as a local extension.

- markdown notes under `data/database/notes` are indexed as `db_note`
- SQL schema files under `data/database/schema` are indexed as `db_schema`
- SQL query files under `data/database/queries` are indexed as `db_query`
- the chatbot can filter by database-specific metadata such as `database_name`, `table_name`, `query_name`, and `service_name`

This is enough to ask more realistic internal questions such as:

- Where is authentication handled?
- What does the notification module do?
- Why was retry logic added?
- Which ticket introduced retry logic?
- What do the docs say about the payment retry change?
- Which function performs the retry loop?
- Which code module sends receipts?
- Which table stores notification delivery history?
- Which query finds failed payment attempts?

## Project Structure

```text
RAG_Learning/
├── data/
│   ├── changes/
│   ├── codebase/
│   ├── database/
│   ├── docs/
│   ├── index/
│   └── tickets/
├── docs/
│   ├── evaluation-guide.md
│   ├── phased-roadmap.md
│   ├── system-roadmap.md
│   └── technical-walkthrough.md
├── eval/
│   └── questions.json
├── src/
│   └── rag_learning/
│       ├── chatbot.py
│       ├── citations.py
│       ├── cli.py
│       ├── code_loader.py
│       ├── config.py
│       ├── corpus.py
│       ├── db_loader.py
│       ├── evaluation.py
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

## Run Phase 6

### 0. Create or reset the seeded local SQLite database

```powershell
python -m rag_learning.cli seed-db
python -m rag_learning.cli reset-db
```

These commands prepare the small local SQLite database used for exact-value demo questions.

### 1. Build the local index

```powershell
python -m rag_learning.cli index
```

This command now reads all seven synthetic source folders:

- `data/docs`
- `data/tickets`
- `data/changes`
- `data/codebase`
- `data/database/notes`
- `data/database/schema`
- `data/database/queries`

It parses markdown metadata, loads Python code files, creates code-aware chunks, creates embeddings, and writes the local JSON index to `data/index/index.json`.

### 2. Ask broad questions

```powershell
python -m rag_learning.cli ask "Why was retry logic added?"
python -m rag_learning.cli ask "Which ticket introduced retry logic?"
python -m rag_learning.cli ask "What does the notification module do?"
python -m rag_learning.cli ask "Where is authentication handled?"
python -m rag_learning.cli ask "Which function performs the retry loop?" --source-type code
python -m rag_learning.cli ask "Which service writes notification delivery records?" --source-type db_note
python -m rag_learning.cli ask "Which table stores notification delivery history?" --source-type db_schema
python -m rag_learning.cli ask "Which query finds failed payment attempts?" --source-type db_query
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
python -m rag_learning.cli ask "Which service writes notification delivery records?" --source-type db_note --service-name NotificationService
python -m rag_learning.cli ask "Which database table stores notification failures?" --source-type db_schema --table-name notification_deliveries
python -m rag_learning.cli ask "Which SQL query finds failed payment attempts?" --source-type db_query --database-name acme_checkout --table-name payment_attempts
python -m rag_learning.cli ask "What stores failed payment attempts and which query reads them?" --source-type db_note --source-type db_schema --source-type db_query --table-name payment_attempts
```

### 4. Inspect grouped evidence

Phase 4 changes the terminal output.

Instead of one flat citation list, the CLI now groups evidence by source type and shows a cleaner line for each retrieved chunk.

That makes it easier to see whether the answer relied on docs, tickets, change notes, code, or a mixture.

### 5. Run the evaluation set

```powershell
python -m rag_learning.cli evaluate
```

This command loads `eval/questions.json`, runs each case against the current index, prints a retrieval summary, and writes a detailed report to `eval/last-report.json`.

If you want model answers in the report too, run:

```powershell
python -m rag_learning.cli evaluate --with-answers
```

### 5b. Ask exact-value live database questions

```powershell
python -m rag_learning.cli ask-live "How many failed payment attempts are there?"
python -m rag_learning.cli ask-live "Which orders had failed payment attempts?"
python -m rag_learning.cli ask-live "Show the latest 2 failed payment attempts."
python -m rag_learning.cli ask-live "How many failed notifications are there?"
python -m rag_learning.cli ask-live "Which recipients had failed notifications?"
```

This path first retrieves the relevant schema, notes, and query context, then runs a small safe read-only SQL query against the seeded SQLite database.

You can still ask cross-source retrieval questions when you want relationships instead of exact values:

```powershell
python -m rag_learning.cli ask "Which code module writes notification delivery records and which table stores them?" --source-type code --source-type db_schema
```

### 6. Read the professional roadmap

Open [docs/system-roadmap.md](docs/system-roadmap.md).

That document explains how to evolve this project into a stronger internal engineering assistant with:

- multi-source ingestion pipelines
- hybrid retrieval and re-ranking
- stronger evaluation workflows
- database retrieval using synthetic schema and query files

## How Phase 6 Works

The earlier phases still handle ingestion, retrieval, filtering, and answer generation.

Phase 5 adds a repeatable way to measure whether that pipeline is still behaving well.

Phase 6 adds the final architecture document that turns the learning project into a practical roadmap.

After that roadmap work, this repository also adds a first database retrieval step using local SQL files.

The latest extension adds a tiny live SQLite path for exact-value questions and a synthetic repository module that connects application code to the notification delivery table.

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
- optional database fields such as `database_name`, `table_name`, and `service_name`
- `language=python`

Database files carry metadata such as:

- `source_type=db_schema` or `source_type=db_query`
- `database_name`
- `table_name`
- `query_name`
- `service_name`
- `language=sql`

### Step 3: Split code differently from markdown

Markdown files still use the simple text chunker.

Code files use a line-aware splitter so indentation and function boundaries stay easier to read in retrieved snippets.

The embedding step still stays simple on purpose.

### Step 4: Include code overviews and symbol documents

The code loader creates:

- one overview document for each Python file
- one symbol document for each top-level class or function

That means retrieval can match both broad code questions and specific symbol questions.

### Step 4b: Load SQL schema and query documents

The database loader reads SQL files with metadata comments at the top.

It turns them into retrieval documents that include:

- a short plain-English summary built from the metadata
- the raw SQL body
- structured database metadata for filtering and citations

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
- database name
- table name
- query name
- service name
- an `updated_after` date

This makes the assistant less noisy as the local corpus grows.

### Step 6: Return grouped evidence with clearer citations

Each evidence line now shows:

- the document title
- the source path
- the similarity score
- important metadata such as module, ticket ID, change ID, symbol, and language

For database sources, citations can also show:

- database name
- table name
- query name
- service name

The CLI also groups those lines by source type so mixed-source retrieval is easier to inspect.

### Step 7: Evaluate with a small labeled dataset

The evaluation runner reads each case from `eval/questions.json` and checks whether retrieval returned the expected evidence.

The current metrics are intentionally simple:

- expected source type coverage
- expected module hit
- expected ticket or change hit
- expected symbol hit for code questions
- expected database, table, query, and service hits for SQL questions
- expected path hit
- overall per-case hit

This is enough to catch common regressions without burying the project in framework code.

### Step 8: Map the learning project to a stronger system design

The roadmap in [docs/system-roadmap.md](docs/system-roadmap.md) explains how to grow the project without breaking its teaching value.

It covers:

- source-specific ingestion pipelines
- a more consistent metadata model
- hybrid retrieval and re-ranking
- audit-friendly citations
- database retrieval using synthetic schema and query artifacts
- stronger evaluation and regression review

## Why Phase 6 Matters

Plain docs answer “what” questions reasonably well.

Tickets and change notes help answer “why” and “which change introduced this” questions.

Code retrieval answers “where is this implemented?” questions.

Phase 4 makes those answers easier to trust because you can narrow retrieval and inspect the supporting evidence more quickly.

Phase 5 makes it easier to measure whether those improvements are still working after future changes.

Phase 6 matters because it shows how to keep growing the project deliberately instead of jumping from a small demo straight into an overcomplicated system.

## Current Limitations

The project is still intentionally small.

- The index is still a JSON file.
- Retrieval still uses simple cosine similarity.
- Evaluation is still lightweight and mostly retrieval-focused.
- Database retrieval is still synthetic and file-based rather than connected to a live database.

Those limitations are addressed in [docs/phased-roadmap.md](docs/phased-roadmap.md).

The design direction for solving them is described in [docs/system-roadmap.md](docs/system-roadmap.md).

## Beginner Study Order

If you want to understand the full Phase 1 to Phase 6 journey in a sensible order:

1. Read [docs/phased-roadmap.md](docs/phased-roadmap.md)
2. Read [docs/technical-walkthrough.md](docs/technical-walkthrough.md)
3. Read [src/rag_learning/code_loader.py](src/rag_learning/code_loader.py)
4. Read [src/rag_learning/metadata.py](src/rag_learning/metadata.py)
5. Read [src/rag_learning/corpus.py](src/rag_learning/corpus.py)
6. Read [src/rag_learning/filters.py](src/rag_learning/filters.py)
7. Read [src/rag_learning/retrieval.py](src/rag_learning/retrieval.py)
8. Read [src/rag_learning/citations.py](src/rag_learning/citations.py)
9. Read [src/rag_learning/chatbot.py](src/rag_learning/chatbot.py)
10. Read [src/rag_learning/evaluation.py](src/rag_learning/evaluation.py)
11. Read [src/rag_learning/cli.py](src/rag_learning/cli.py)
12. Read [docs/evaluation-guide.md](docs/evaluation-guide.md)
13. Run `index`
14. Run `evaluate`
15. Run `ask` with and without filters such as `--source-type code --symbol retry`
16. Read [docs/system-roadmap.md](docs/system-roadmap.md)
17. Read [src/rag_learning/db_loader.py](src/rag_learning/db_loader.py)

For a line-by-line explanation of the code, see [docs/technical-walkthrough.md](docs/technical-walkthrough.md).