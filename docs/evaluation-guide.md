# Evaluation Guide

Phase 5 adds a small evaluation loop.

The goal is not to create a perfect benchmark.

The goal is to stop guessing.

With this phase, you can run the same set of questions repeatedly and inspect whether retrieval is still finding the right evidence.

## What This Phase Adds

Phase 5 introduces three pieces:

1. a JSON question set in `eval/questions.json`
2. an evaluation runner in `src/rag_learning/evaluation.py`
3. a CLI command: `python -m rag_learning.cli evaluate`

The dataset is intentionally small and synthetic.

That keeps it beginner-friendly while still teaching the habit of measuring changes.

## Why Evaluation Matters

Earlier phases made the chatbot more capable.

But capability changes can accidentally make retrieval worse.

For example:

- a chunking change might hide a key symbol
- a prompt change might make answers less grounded
- a metadata change might break one filter without you noticing

Phase 5 helps you catch those problems earlier.

## The Evaluation Dataset

The dataset lives in `eval/questions.json`.

Each entry contains:

- a `case_id`
- a `question`
- optional `filters`
- expected metadata such as source types, module, ticket ID, change ID, symbol, and paths
- optional database-specific expectations such as database name, table name, query name, and service name
- `reference_points` for manual answer review

This project keeps the labels simple on purpose.

They are not trying to be mathematically perfect.

They are trying to be useful.

## Run The Evaluation

First, make sure the index exists.

```powershell
python -m rag_learning.cli index
```

Then run the evaluation set.

```powershell
python -m rag_learning.cli evaluate
```

If you are running from the repo without an editable install, use the `src` layout directly:

```powershell
$env:PYTHONPATH = "src"
python -m rag_learning.cli evaluate
```

This prints a small summary and writes a detailed JSON report to `eval/last-report.json`.

## Generate Answers For Manual Review

Retrieval metrics are useful, but sometimes you also want to inspect the actual answers.

Run:

```powershell
python -m rag_learning.cli evaluate --with-answers
```

This adds model answers to the report together with blank review fields.

Those review fields are intentionally manual.

That keeps the project realistic: beginner projects usually benefit more from simple human review than from building a complicated automatic judge too early.

## What The Summary Metrics Mean

The CLI summary focuses on a few easy-to-understand retrieval checks.

### `source_type_hit`

Did the retrieved evidence include the expected source types?

Example: a question about retry history might be expected to surface docs, tickets, and change notes.

### `module_hit`

Did any retrieved citation come from the expected module?

Example: a notification question should retrieve `module=notifications`.

### `path_hit`

Did retrieval return at least one expected source file?

This is a simple but concrete check.

### `ticket_hit`, `change_hit`, `symbol_hit`

Did retrieval surface the expected metadata anchor?

These checks are especially useful for questions about change history and code locations.

### `database_hit`, `table_hit`, `query_hit`, `service_hit`

These checks are used for SQL-backed retrieval cases.

They help verify that the assistant found the correct schema or query artifact, not just something generally related to payments or notifications.

They also help with cross-source database questions where retrieval should surface a mix of notes, schema, and query evidence.

### `overall_hit`

Did all relevant expectations for that case pass?

This is the main high-level score for the current dataset.

## How To Read The JSON Report

Each result contains:

- the original question
- the active filters
- retrieval metrics
- the top citation
- all retrieved citations
- reference points
- optional model answer
- a manual review template if `--with-answers` was used

This means the report is useful for both technical debugging and manual inspection.

## Good Beginner Workflow

Use this loop:

1. change retrieval, chunking, prompts, or filters
2. rebuild the index if needed
3. run `evaluate`
4. inspect the summary
5. open `eval/last-report.json` if something regressed
6. rerun with `--with-answers` if retrieval looks correct but the answer still seems weak

## Current Limitations

This evaluation phase is intentionally lightweight.

- it does not use a large benchmark
- it does not score semantic answer quality automatically
- it does not compare multiple model runs side by side yet

That is acceptable here.

The project is teaching the habit of measurement before adding more complex evaluation systems.