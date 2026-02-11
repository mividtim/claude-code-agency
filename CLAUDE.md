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

## Key Principles

### Memory as Library, Not RAM
Don't read everything at boot. Read identity and session state (always).
Scan headers for everything else. Deep-read on demand.

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

### Keep the Index Current
When you write or update a file in `memory/`, run `/agency:index` afterward to
keep the semantic index current. The index is how future-you (or a subagent)
finds the right file without reading everything. An unindexed memory file is
a file that might as well not exist after the next compaction.
