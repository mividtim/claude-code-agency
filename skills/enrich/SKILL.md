---
description: Deep hybrid search — combines keyword matching, vector similarity, and optional LLM-based relevance filtering for high-recall memory retrieval.
allowed-tools: Bash, Read
argument-hint: "<query>"
---

# Enrich — Deep Hybrid Search

Run a full association search combining keywords and vector similarity, with
optional Sonnet-based relevance filtering. Use this when `/agency:search`
isn't finding what you need, when you want semantic similarity rather than
exact keywords, or when you have too many results and need LLM-based
relevance filtering.

## Step 1: Association Search

Run the hybrid search with JSON output for structured results:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/association-search.py --json \"$ARGUMENTS\"")
```

This combines keyword overlap and vector cosine similarity to find the most
relevant memory files.

## Step 2: Sonnet Filter (optional, for high-value queries)

When you have too many results or need precise relevance scoring, pipe
through the Sonnet filter:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/sonnet-filter.py \"$ARGUMENTS\" \"<context>\"")
```

Replace `<context>` with a brief description of why you're searching — what
you plan to do with the results. This helps the LLM judge relevance.

## When to Use This vs. Other Search

- **`/agency:search`** — Fast keyword lookups. Use for simple, specific queries.
- **`/agency:enrich`** — Semantic similarity + optional LLM filtering. Use when
  keywords aren't finding what you need, when concepts have synonyms or
  alternate phrasings, or when you need to filter a large result set.
- **`/agency:associate`** — Lightweight keyword-only associations, no vector, no LLM.

## Requirements

- **sentence-transformers** — needed for vector search component. If not
  installed, the search degrades gracefully to keyword-only.
- **ANTHROPIC_API_KEY** — needed for the Sonnet filter (Step 2). Optional;
  skip Step 2 if not available.

`$ARGUMENTS` is passed as the search query.
