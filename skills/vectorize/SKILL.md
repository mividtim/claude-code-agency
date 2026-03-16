---
description: Build and maintain vector embeddings for semantic search over the memory vault. Supports full rebuild, incremental updates, and stats.
allowed-tools: Bash, Read
argument-hint: "[stats|<path>]"
---

# Vectorize Memory Vault

Build vector embeddings for all indexed memory files, enabling semantic
similarity search via `/agency:enrich`.

## Prerequisites

First, verify that sentence-transformers is installed:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vectorize.py --check-deps")
```

If not installed, tell the user to run: `pip install sentence-transformers`

## Full Build

Rebuild all embeddings from scratch. Run this after initial index build.

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vectorize.py")
```

## Incremental Update

After editing a memory file, update just that file's embedding:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vectorize.py update <path>")
```

After adding a journal entry, update its embedding:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vectorize.py update --journal <id>")
```

## Stats

Check embedding coverage and staleness:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vectorize.py --stats")
```

## Argument Handling

If `$ARGUMENTS` is provided:
- If it is `stats`, run `--stats`
- If it is a file path, run `update <path>`
- Otherwise, run a full build

## Notes

- Run full vectorization after initial index build. After that, use targeted updates.
- Model loads in ~3-5s on first call.
- Embeddings are stored alongside the semantic index for fast lookup.

`$ARGUMENTS` is passed as described above.
