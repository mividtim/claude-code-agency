---
description: Build or update the semantic index of the agent's memory vault. Scans for changed files and prints them for indexing.
allowed-tools: Bash, Read, Task
argument-hint: "[scan|file <path>|update <path> <summary> <keywords>|stats]"
---

# Index Memory Vault

Build a keyword-based semantic index of all markdown files in `memory/`.
The index enables fast search across the vault without loading every file.

**IMPORTANT: Use a Haiku subagent for summary/keyword generation.** This is
commodity work — don't burn Opus tokens on it. Spawn a Task with
`model="haiku"` to read each file and produce the summary + keywords.

## Quick Start (full reindex)

1. Scan for files that need indexing:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py scan")
```

2. For each `NEEDS_INDEX` file, spawn a Haiku subagent to generate summary + keywords:

```
Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt="Read the file at memory/path/to/note.md. Generate:
    1. A one-line semantic summary
    2. 5-15 keywords (mix of concrete terms and abstract themes, include synonyms)
    3. Related file paths from the vault (if any)
    Format your response as:
    SUMMARY: <summary>
    KEYWORDS: <comma-separated keywords>
    RELATED: <comma-separated paths or 'none'>"
)
```

3. Use the Haiku output to update the index:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py update memory/path/to/note.md 'summary from haiku' 'keywords,from,haiku' 'related/paths.md'")
```

4. Repeat for each file that needs indexing.

## Commands

- **scan** — Find files needing indexing. Compares content hashes to detect changes.
- **file `<path>`** — Print a file's content and hash for you to summarize.
- **update `<path>` `<summary>` `<keywords-csv>` `[related-csv]`** — Write an index entry.
- **stats** — Show index statistics (file counts, keyword counts, stale entries).

## Index Location

The index is stored at `memory/meta/semantic-index.json`. Each entry contains:
- `source_path` — path to the markdown file
- `content_hash` — short SHA-256 hash for change detection
- `summary` — one-line semantic summary (Haiku generates this)
- `keywords` — list of searchable keywords (Haiku generates these)
- `related` — optional list of related file paths

## Guidelines for Haiku Keyword Generation

Include these in the prompt to the Haiku subagent:
- Include 5-15 keywords per file
- Mix concrete terms (names, tools, concepts) with abstract themes
- Include synonyms the searcher might use
- For identity/meta files, include the agent's name and role

If `$ARGUMENTS` is provided, pass it as the command (e.g., `/agency:index scan`).
