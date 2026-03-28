# RAG Learning Project

This project teaches Retrieval-Augmented Generation (RAG) by building a small internal chatbot for a fictional software team.

The chatbot starts with a single job:

- read local markdown documents
- retrieve the most relevant notes for a question
- ask a local Ollama model to answer using those notes
- show citations so you can inspect the retrieved evidence

The project is designed for learning first.

- It uses synthetic local data.
- It avoids enterprise setup.
- It keeps the code small and readable.
- It grows in phases instead of trying to solve everything at once.

## Fictional Product Domain

The chatbot supports a fictional product called `Acme Checkout`.

This is a small retailer checkout platform used by a software team to handle:

- cashier authentication
- receipt and alert notifications
- retry logic for payment-related services
- internal engineering notes

That lets you ask questions such as:

- Where is authentication handled?
- What does the notification module do?
- Why was retry logic added?
- How does the checkout system handle temporary payment failures?
- What do the docs say about this module?

## Phase 1 Goal

Phase 1 implements simple RAG over markdown documentation.

You will learn these concepts directly:

1. Loading documents
2. Chunking text into smaller pieces
3. Generating embeddings with Ollama
4. Ranking chunks by similarity
5. Building a grounded prompt
6. Returning citations with the answer

The code intentionally does not hide these steps behind a large framework.

## Project Structure

```text
RAG_Learning/
├── data/
│   └── docs/
│       ├── architecture.md
│       ├── authentication.md
│       ├── notifications.md
│       └── retries.md
├── docs/
│   └── phased-roadmap.md
├── src/
│   └── rag_learning/
│       ├── __init__.py
│       ├── chatbot.py
│       ├── cli.py
│       ├── config.py
│       ├── corpus.py
│       ├── ollama_client.py
│       └── retrieval.py
├── requirements.txt
└── AGENTS.md
```

## Requirements

- Python 3.11+
- Ollama running locally
- at least one chat model pulled in Ollama
- at least one embedding model pulled in Ollama

Example setup:

```powershell
ollama pull gemma3:latest
ollama pull embeddinggemma:latest
```

You can use different model names if you already have preferred local models.

## Installation

Create and activate a virtual environment, then install the package in editable mode.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

`pip install -e .` matters here because this project uses a `src/` layout.

The Python package lives in `src/rag_learning`, not at the repository root.

Editable install tells Python to treat your local working copy as an installed package, so commands like `python -m rag_learning.cli index` can import `rag_learning` correctly.

If you skip the editable install, Python usually will not find `rag_learning` unless you manually modify `PYTHONPATH` or run commands from a specially configured environment.

## Configure Models

The CLI uses these defaults:

- chat model: `gemma3:latest`
- embedding model: `embeddinggemma:latest`
- Ollama URL: `http://localhost:11434`

These defaults were chosen because Gemma appears to be the more stable option on your local machine.

You can override them with environment variables:

```powershell
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:OLLAMA_CHAT_MODEL = "gemma3:latest"
$env:OLLAMA_EMBED_MODEL = "embeddinggemma:latest"
```

If your local Ollama installation uses different model names, set these environment variables before running the commands.

## Run Phase 1

Run the commands from the repository root after activating the virtual environment.

### 1. Build the local index

```powershell
python -m rag_learning.cli index
```

This command:

- reads the markdown files in `data/docs`
- splits them into chunks
- generates embeddings with Ollama
- stores the index in `data/index/index.json`

### 2. Ask a question

```powershell
python -m rag_learning.cli ask "Where is authentication handled?"
```

Example questions:

```powershell
python -m rag_learning.cli ask "What does the notification module do?"
python -m rag_learning.cli ask "Why was retry logic added?"
python -m rag_learning.cli ask "What do the docs say about retries?"
```

Do not pass a file path to `-m`.

This is wrong:

```powershell
python -m .\src\rag_learning\rag_learning.cli index
```

`-m` expects a Python module name, not a filesystem path.

This project exposes the CLI as the module `rag_learning.cli`, so the correct form is:

```powershell
python -m rag_learning.cli index
```

When Python runs `python -m rag_learning.cli` it:

1. Finds the installed `rag_learning` package
2. Loads the `cli.py` module inside that package
3. Sets that module as the entry module for the process
4. Runs the `if __name__ == "__main__": main()` block

That is why the commands work as normal CLI commands even though you are starting them through Python's module system.

## How Phase 1 Works

The full loop is intentionally visible.

### Step 1: Load documents

The code reads markdown files from `data/docs`.

Each file becomes a document with metadata:

- file path
- title
- source type

### Step 2: Chunk documents

Long documents are split into smaller chunks.

This matters because embeddings and retrieval work better when each unit has a focused idea instead of an entire long file.

### Step 3: Create embeddings

Each chunk is sent to the Ollama embeddings endpoint.

The result is a vector for each chunk.

Vectors let us compare semantic similarity instead of exact keyword matches.

### Step 4: Retrieve relevant chunks

When you ask a question, the question is also embedded.

The code computes cosine similarity between the question vector and the stored chunk vectors.

The top matches become the context for the final answer.

### Step 5: Ask the model to answer from context

The prompt tells the model:

- answer only from the retrieved context
- say when the context is missing something
- cite the supporting chunks

### Step 6: Print citations

The CLI prints:

- the answer
- the retrieved chunk citations

This helps you inspect whether retrieval is working well.

## Why This Is A Good Starting Point

This first phase is small but complete.

It is already useful because you can ask grounded questions over local docs.

It is also a strong teaching base because later phases can extend the same pipeline with:

- source code files
- fake tickets
- metadata filtering
- better citations
- evaluation and comparison

## Limitations In Phase 1

This version is intentionally limited.

- It only reads markdown docs.
- It stores the index in a JSON file.
- It uses a simple chunking strategy.
- It does not yet support ticket tracing.
- It does not yet retrieve code files.
- It does not yet run formal evaluation.

Those limitations are addressed in the roadmap.

See [docs/phased-roadmap.md](docs/phased-roadmap.md).

## Beginner Study Order

If you want to learn the concepts step by step, use this order:

1. Read [docs/phased-roadmap.md](docs/phased-roadmap.md)
2. Read [docs/technical-walkthrough.md](docs/technical-walkthrough.md)
3. Read [src/rag_learning/corpus.py](src/rag_learning/corpus.py)
4. Read [src/rag_learning/retrieval.py](src/rag_learning/retrieval.py)
5. Read [src/rag_learning/ollama_client.py](src/rag_learning/ollama_client.py)
6. Read [src/rag_learning/chatbot.py](src/rag_learning/chatbot.py)
7. Run `index`
8. Run `ask`
9. Change a document and rebuild the index

That will make the full RAG loop much easier to understand.

For a deeper line-by-line explanation of the Phase 1 code, see [docs/technical-walkthrough.md](docs/technical-walkthrough.md).