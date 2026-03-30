# Phase 7: Large Context Windows Versus Retrieval

This note explains a common beginner question:

If modern models can accept very large context windows, do we still need retrieval?

The short answer is:

- sometimes no, for very small systems
- often yes, for realistic systems
- and for live data, retrieval alone is still not enough

## The Core Idea

A large context window means the model can receive more text in one request.

That helps.

But it does not remove the need to decide:

- which information actually matters for this question
- which information is current
- which information the user is allowed to see
- which answers need a live tool instead of pasted context

In other words:

large context windows reduce pressure on retrieval design

but they do not make retrieval obsolete

## When You Can Skip Retrieval

You can often skip retrieval when all of these are true:

- the corpus is small
- the data rarely changes
- every user can see everything
- the questions are broad and general
- you do not need strong citations
- there is no live database or API involved

For the earliest version of this project, that would have been reasonable.

If the assistant only had a few markdown files in `data/docs`, you could paste those docs into the prompt and ask questions directly.

That would be simpler than building embeddings and ranking.

## Why Retrieval Still Matters

Once the project grows, retrieval gives you useful control.

### 1. Relevance

Most questions only need a small part of the total knowledge base.

If the question is:

`Where is authentication handled?`

then the best context is probably:

- the authentication docs
- the auth code
- maybe one ticket if it explains an important change

It is usually not helpful to also send notification history, payment retry notes, and unrelated SQL files.

### 2. Cost And Latency

Large prompts cost more and usually take longer.

If you send the full corpus on every question, the system stays expensive even when the user asks something narrow.

Retrieval keeps the prompt smaller and more targeted.

### 3. Freshness

Docs, code, tickets, and operational notes change.

Retrieval lets the assistant pull the latest indexed evidence at question time instead of relying on one frozen snapshot.

### 4. Traceability

Retrieval naturally supports citations.

That matters when you want the assistant to show which file, note, ticket, or schema informed the answer.

### 5. Access Control

In a professional system, not every user should see every source.

Retrieval is one place where permission filters can be applied before the model sees the text.

### 6. Mixed Source Types

This project now spans several source types:

- docs
- tickets
- change notes
- code
- database notes
- SQL schema files
- SQL query files

Retrieval helps the assistant pull the right mix instead of flattening everything into one giant prompt.

## What Large Context Windows Improve

Large context windows are still very helpful.

They make RAG systems easier to build well.

For example:

- you can keep larger chunks instead of aggressively splitting everything
- you can include more evidence in one answer
- multi-step questions become easier because more supporting material fits in one prompt
- prompt construction becomes less fragile

So a better rule is:

- use retrieval to select the right evidence
- use the larger context window to hold richer evidence once selected

## Retrieval Is Not Enough For Live Data

Large context does not solve live-data questions.

Neither does basic retrieval.

If the question is:

`Show the latest 2 failed payment attempts.`

then the assistant should not answer from a pasted snapshot alone.

It should:

1. retrieve the schema, notes, or query definitions that explain the data
2. run a safe live query against the current database
3. answer with both the result and supporting evidence

That is why this project now has both:

- retrieval over SQL-related artifacts
- a tiny live SQLite query path for exact-value questions

## A Practical Decision Rule

Use direct prompting without retrieval when:

- the knowledge base is tiny
- it is stable
- the whole corpus is relevant often enough
- exact citations are not a priority

Use retrieval when:

- the corpus is medium or large
- only some information is relevant per question
- you want citations
- the content changes over time
- you need metadata filtering
- you want predictable cost and latency

Use live tools when:

- the answer depends on current database state
- the answer depends on APIs or runtime systems
- the user asks for exact counts, rows, or latest values

## What This Means For This Project

For Phase 1, retrieval was mostly a teaching tool.

For the current project, retrieval is now part of the right architecture because the assistant needs to answer across different kinds of evidence.

Examples:

- `What does the notification module do?`
  Retrieval is useful.
- `Which ticket introduced retry logic?`
  Retrieval plus metadata filtering is useful.
- `Which code module writes notification delivery records and which table stores them?`
  Cross-source retrieval is useful.
- `Show the latest 2 failed payment attempts.`
  Retrieval plus a live database tool is the correct pattern.

## Recommended Modern Mental Model

Do not think in extremes such as:

- always use RAG
- never use retrieval because context windows are huge

Instead, use this pattern:

1. keep a small stable instruction prompt
2. retrieve the most relevant supporting evidence
3. use the large context window to include enough evidence comfortably
4. call live tools when the answer depends on current state

That is usually a stronger design than either extreme.