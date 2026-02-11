---
description: Write to and query the agent's journal — the log of WHY beliefs exist. Records context behind identity changes, learnings, corrections, and decisions.
allowed-tools: Bash, Read
argument-hint: "<subcommand> [args]"
---

# Journal — The Change Log for Agent Memory

The journal is the append-only record of experiences that shaped your identity.
Core memory (identity.md) is the WHAT — current beliefs and values. The journal
is the WHY — the reasoning, context, and history behind those beliefs.

**Before modifying identity.md or any core belief, search the journal first.**
The journal may contain context you've forgotten about why something was written
the way it was.

## Subcommands

### Initialize (first time only)

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py init")
```

### Add an Entry

When you learn something, make a decision, get corrected, or have a significant
conversation — journal it.

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py add '<category>' '<summary>' '<context>' --source '<who/what>' --tags '<comma,separated>'")
```

Categories: `learning`, `correction`, `decision`, `experiment`, `conversation`

- **summary**: One line — what happened
- **context**: The full WHY — reasoning chain, what was considered, what was
  rejected, what led to this. This is the most important field. Be thorough.
- **source**: Who or what prompted this (e.g., "Tim DM", "self-reflection",
  "Andy feedback", "experiment results")
- **tags**: Comma-separated keywords for filtering

After adding, note the `j:N` ID. If this entry should be referenced from
identity.md or another core file, add the reference: `[j:N]`.

### Search the Journal

Before changing core beliefs, search for prior context:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py search '<query>'")
```

Uses SQLite FTS5 full-text search across summary, context, and tags.

### Look Up a Specific Entry

When identity.md references `[j:42]`, retrieve the full context:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py get 42")
```

### Recent Entries

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py recent 10")
```

### Filter by Category or Tag

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py by-category correction")
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py by-tag identity")
```

### Provenance Check (before modifying core memory)

If identity.md says `- Never block the main thread [j:3, j:7, j:19]`, read
all referenced entries before changing or removing that rule:

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py get 3")
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py get 7")
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py get 19")
```

### Stats

```
Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py stats")
```

## When to Journal

- **After a correction**: Someone told you something was wrong. Record what was
  wrong, why, and what the fix was. Category: `correction`
- **After a decision**: You chose between options. Record what you chose, what
  the alternatives were, and why. Category: `decision`
- **After learning something new**: A pattern, a principle, a technique.
  Category: `learning`
- **After a significant conversation**: The conversation shaped your thinking.
  Category: `conversation`
- **After an experiment**: You tried something and it worked or didn't.
  Category: `experiment`

## The Provenance Chain

Core memory references journal entries:
```
- I value lean core memory [j:12, j:45]
- Never block the main thread [j:3, j:7, j:19]
```

Each belief becomes Justified True Belief — traceable back to the experiences
that produced it. A belief without journal references is an assertion. A belief
with references is knowledge.

## Git Strategy

- `journal.db` is .gitignored (binary)
- `journal.sql` (text dump) lives in git
- A pre-push hook dumps the db to SQL automatically
- On fresh clone, run `journal.py rebuild` to recreate the db from the dump
- The boot sequence handles this automatically

`$ARGUMENTS` is passed as the subcommand and arguments.
