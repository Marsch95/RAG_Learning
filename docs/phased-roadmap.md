# Phased Roadmap

This roadmap grows the project from a tiny local RAG demo into the design of a more professional engineering knowledge assistant.

Each phase is useful on its own.

## Phase 1: Simple RAG Over Markdown Docs

### Purpose

Build the smallest possible RAG chatbot that works locally with Ollama.

### Limitations Solved

- Answers are no longer based only on the model's memory.
- The chatbot can point to local documentation.
- You can inspect retrieval with citations.

### Files Created

- `data/docs/*.md`
- `src/rag_learning/corpus.py`
- `src/rag_learning/retrieval.py`
- `src/rag_learning/ollama_client.py`
- `src/rag_learning/chatbot.py`
- `src/rag_learning/cli.py`
- `README.md`

### Code

Core ideas in this phase:

- load markdown files
- split text into chunks
- embed chunks with Ollama
- store vectors locally
- retrieve top chunks for a question
- generate an answer with citations

### Explanation

This phase teaches the basic RAG loop without depending on a large framework.

That makes it easier to understand what retrieval is actually doing.

### Next Phase Preview

Phase 2 will make the project feel more like an internal engineering assistant by adding structured metadata and fake tickets.

## Phase 2: Add Fake Tickets And Better Metadata

### Purpose

Expand from plain docs to synthetic professional signals such as fake issue tickets and change notes.

### Limitations Solved

- You can start asking change-history questions.
- Documents can be filtered by type.
- Chunks carry richer metadata.

### Files Created

- `data/tickets/*.md`
- `data/changes/*.md`
- `src/rag_learning/metadata.py`
- updates to `src/rag_learning/corpus.py`
- updates to `src/rag_learning/retrieval.py`
- updates to `src/rag_learning/chatbot.py`
- updates to `src/rag_learning/cli.py`

### Code

This phase adds:

- metadata fields such as `source_type`, `module`, `ticket_id`, and `updated_at`
- metadata-aware retrieval
- CLI filters for `source_type`, `module`, and `ticket_id`
- fake tickets that explain why changes were made
- fake change notes that link implementation summaries back to tickets

### Explanation

Professional internal assistants usually rely on more than just documentation.

Tickets explain intent, tradeoffs, and change history.

This is the first phase where the chatbot can answer questions about why work happened, not just what a module does.

### Next Phase Preview

Phase 3 will add simple source code retrieval using a synthetic codebase.

## Phase 3: Add Source Code Retrieval

### Purpose

Teach how RAG can answer questions across both docs and code.

### Limitations Solved

- The chatbot can now point to implementation details.
- Questions like "Where is authentication handled?" can reference docs and code together.

### Files Created

- `data/codebase/*.py`
- `src/rag_learning/code_loader.py`
- updates to `src/rag_learning/corpus.py`
- updates to `src/rag_learning/retrieval.py`
- updates to `src/rag_learning/chatbot.py`
- updates to `src/rag_learning/cli.py`

### Code

This phase adds:

- synthetic Python modules
- file and symbol metadata
- code retrieval alongside doc retrieval
- line-aware code chunking

### Explanation

Engineering assistants are much more useful when retrieval spans architecture docs and implementation files.

This phase is where “what do the docs say?” and “where is that actually implemented?” can start using the same assistant.

### Next Phase Preview

Phase 4 will improve answer quality with sharper filters and cleaner citation formatting.

## Phase 4: Add Metadata Filtering And Better Citations

### Purpose

Help the chatbot retrieve the right evidence more precisely.

### Limitations Solved

- Retrieval can be narrowed to docs, code, or tickets.
- Citations become easier to inspect.
- Answers become less noisy.

### Files Created

- `src/rag_learning/filters.py`
- `src/rag_learning/citations.py`
- optional simple UI or richer CLI output

### Code

This phase adds:

- more expressive query-time filters such as multiple source types, change IDs, symbols, languages, and update dates
- stronger citation formatting and grouping
- cleaner evidence presentation for mixed sources

### Explanation

As the corpus grows, retrieval quality depends on selective search, not just more documents.

### Next Phase Preview

Phase 5 will focus on evaluation so you can measure whether changes help.

## Phase 5: Add Evaluation

### Purpose

Measure the system instead of guessing whether it improved.

### Limitations Solved

- You can compare prompt and retrieval changes.
- You can create a repeatable test set.
- You can spot regressions early.

### Files Created

- `eval/questions.json`
- `src/rag_learning/evaluation.py`
- `docs/evaluation-guide.md`
- updates to `src/rag_learning/chatbot.py`
- updates to `src/rag_learning/cli.py`
- updates to `README.md`

### Code

This phase adds:

- a small labeled question set
- retrieval inspection metrics
- answer quality review workflow
- a CLI evaluation command that writes a JSON report

### Explanation

Even a small manual evaluation loop is valuable.

It turns experimentation into something you can learn from.

### Next Phase Preview

Phase 6 will turn the learning project into a roadmap for a more professional multi-source assistant.

## Phase 6: Professional Multi-Source Engineering Knowledge Assistant Roadmap

### Purpose

Define how this simple learning project would evolve into a stronger internal assistant.

### Limitations Solved

- You now have a path from a toy project to a realistic architecture.
- The roadmap can guide future implementation work without jumping there too early.

### Files Created

- `docs/system-roadmap.md`
- updates to `README.md`
- updates to `docs/technical-walkthrough.md`

### Code

This phase is primarily design-oriented.

Likely additions:

- stronger indexing strategy
- more robust chunking
- hybrid retrieval
- re-ranking
- source-specific ingestion pipelines
- background refresh jobs
- evaluation dashboards
- database schema and query retrieval

### Explanation

The final concept should support:

- source code retrieval
- documentation retrieval
- fake ticket retrieval
- metadata filtering
- citations
- evaluation
- database retrieval

This phase keeps the project grounded: learn the small version first, then grow it deliberately.

### Next Phase Preview

There is no required next phase inside this repository.

The next practical implementation step would be to add synthetic database sources based on the roadmap in `docs/system-roadmap.md`.

That first follow-up step has now been implemented with local SQL schema and query files under `data/database`.