---
description: Lightweight keyword-only association search — fast (<100ms), no vector embeddings, no LLM. Returns quick context associations from the memory vault.
allowed-tools: Bash, Read
argument-hint: "<text>"
---

# Associate — Fast Keyword Associations

Run a lightweight keyword-only association search against the memory vault.
Unlike `/agency:enrich`, this is fast (<100ms) and requires no vector
embeddings or LLM calls.

## Usage

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/association-search.py \"$ARGUMENTS\" --no-vector")
```

Results are returned as concise context lines showing matched files with
relevance indicators.

## When to Use This

Run this when you want quick associations from your memory vault — a fast
scan of what's related to a concept or phrase. Good for:

- Checking what you already know about a topic before writing
- Finding related files to read before making a decision
- Quick context gathering during conversation

For deeper semantic search with vector similarity and LLM filtering, use
`/agency:enrich` instead.

`$ARGUMENTS` is passed as the text to find associations for.
