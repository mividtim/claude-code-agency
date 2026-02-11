# Agency — Persistent Agent Plugin

This plugin provides patterns for Claude Code agents that persist across
context compaction. It gives agents the ability to maintain identity, memory,
and continuity between sessions.

## When to Use These Skills

- `/agency:boot` — **After context compaction.** The boot sequence reads the
  agent's identity and session state, scans memory, and resumes work. If
  CLAUDE.md tells you to "run the boot sequence," this is it.

- `/agency:init` — **Once, when setting up a new agent.** Creates the memory
  directory structure, identity file, and session state template.

- `/agency:scan` — **During boot or on demand.** Scans memory file headers to
  build a mental index without loading everything. Use when you need to find
  something in memory but don't know which file it's in.

- `/agency:index` — **Periodically, to keep the semantic index current.** Scans
  all markdown files in `memory/`, detects changes via content hashing, and
  prints files that need indexing. You then summarize each file and update the
  index with keywords. Pass a subcommand: `scan`, `file`, `update`, `stats`.

- `/agency:search` — **When you need to find something in memory.** Searches
  the semantic index by keyword overlap with your query. Returns ranked results
  with scores, summaries, and matched keywords. Supports `search-json` mode
  for structured output. Also handles miss logging (`miss`, `misses`).

## Memory Architecture

Agent memory is organized in two tiers, drawn from the distinction between
working memory and long-term memory in cognitive psychology (Atkinson &
Shiffrin, 1968) and between primary and secondary storage in computer
architecture.

### Core Memory (always loaded)
Read on every boot. Small, critical, defines who the agent is and what it
was doing. This is the agent's working set — the minimum context needed to
resume operation after compaction.

- `memory/identity.md` — who you are
- `memory/meta/session-state.md` — what you were doing
- Any files your agent's CLAUDE.md explicitly lists as boot-loaded

**Rule**: Keep core memory lean. Every byte here is paid on every boot.
See "Guard identity.md" in Key Principles.

### Archival Memory (indexed, on-demand)
Everything else in `memory/`. Grows without bound. Searched via semantic
index (`/agency:search`), scanned via headers (`/agency:scan`), deep-read
when relevant. Never bulk-loaded.

- Topic notes, research, project files, lesson logs, context for lessons
- Indexed by `/agency:index` with summaries and keywords
- Retrieved by keyword overlap or Haiku-powered semantic reranking

**Rule**: If you write it, index it. An unindexed archival file is invisible
after compaction.

## Key Principles

### Memory as Library, Not RAM
Don't read everything at boot. Load **core memory** (identity, session state)
always. Scan headers for **archival memory**. Deep-read on demand.

### Never Block the Main Thread
Background processes write to files. The main thread reads files when
convenient. **Never** use `TaskOutput(block=true, timeout=long)` to wait
for external events. This causes unresponsive sessions.

### Identity Survives Compaction
After compaction, the agent wakes up with a summary but no lived experience.
The memory directory bridges this gap — `identity.md` defines who the agent
is, `session-state.md` defines what it was doing, and everything else fills
in the details on demand.

### Persist Learnings, Not Just Outputs
**This is the most important principle.** When you learn something — a lesson,
a preference, a pattern, a correction — write it to `memory/`. If you say
"I'll remember that," you must persist it where it will be found next time.
Context compaction erases everything that isn't written down. Learnings that
stay in-context are learnings that die.

- If you promise to remember something → write it to an appropriate memory file *now*, not later
- If you discover a lesson during work → add it to session-state or a dedicated file
- If the operator corrects you → persist the correction so it survives compaction
- If you do in-context work (analysis, inventory, research) → save the results to disk
- Before creating a new memory file → search the index first; update existing files rather than creating duplicates

An agent that learns but doesn't persist is an agent that forgets. The vault
is not optional — it's the difference between growing and looping.

### Every Lesson Has Two Actions
When you learn something, there are two things to do: **fix the thing** and
**persist the rule**. The rule goes where it'll be enforced — identity.md,
CLAUDE.md, agent docs, process files — not just the lesson log. A lesson
that only lives in a memory note is a lesson that only helps if someone
searches for it. A lesson that lives in the docs shapes behavior by default.

### Guard identity.md
identity.md is **core memory** — loaded on every boot. Only core operating
rules and essential findings belong here. Lessons whose *finding* is important
enough to shape every future session can go in identity — but only the finding.
The context (when it was learned, what went wrong, how many times you violated
it) belongs in **archival memory**, indexed and searched on demand. Before
writing to identity.md, ask: "Does future-me need this on every single boot?"

### Keep the Index Current
When you write or update a file in `memory/`, run `/agency:index` afterward to
keep the semantic index current. The index is how future-you (or a subagent)
finds the right file without reading everything. An unindexed memory file is
a file that might as well not exist after the next compaction.
