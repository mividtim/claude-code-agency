---
description: Search the agent's memory vault by keyword. Returns ranked results with scores, summaries, and matched keywords.
allowed-tools: Bash, Read, Task
argument-hint: "<query>"
---

# Search Memory Vault

Search the semantic index built by `/agency:index`. Finds memory files by
keyword overlap between your query and each file's indexed keywords and summary.

## Quick Search (human-readable output)

For simple lookups where keyword matching is sufficient:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py search '$ARGUMENTS'")
```

Results are ranked by relevance score:
- Full keyword match = 1.0 points
- Summary term match = 0.5 points
- Top 10 results shown

## Deep Search with Haiku Reranking

For complex or ambiguous queries, use a Haiku subagent to rerank results
by semantic relevance. This catches matches that keyword overlap misses.

1. Get structured candidates:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py search-json '$ARGUMENTS'")
```

2. Spawn a Haiku subagent to rerank:

```
Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt="Given the search query '<query>' and these candidate results:
    <paste search-json output>
    Score each candidate 0-10 for semantic relevance to the query.
    Consider: Does the summary suggest the file actually answers the query?
    Could the file contain useful context even if keywords don't match exactly?
    Return results sorted by your score, format:
    SCORE: <0-10> | PATH: <path> | REASON: <why relevant>"
)
```

3. Deep-read the top-scored files.

## Logging Misses

If a search didn't surface a file you expected, log it for evaluation:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py miss 'query terms' 'expected/file/path.md' 'optional reason'")
```

Review the miss log to improve keywords:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/index-vault.py misses")
```

## Tips

- Use quick search for simple lookups (`identity drift`, `slack webhook`)
- Use Haiku reranking for complex queries (`how does the agent handle voice drift`)
- If no results, the index may need updating — run `/agency:index scan`
- After finding candidates, deep-read the top results
- Log misses — they help you improve keyword coverage over time

`$ARGUMENTS` is passed as the search query.
