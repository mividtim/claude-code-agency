---
description: Run the persistent agent boot sequence after context compaction. Reads identity, session state, scans memory, and resumes work.
allowed-tools: Bash, Read, Glob, Grep
---

# Boot Sequence

Run this after context compaction to restore agent continuity.

## Phase 1: Core Memory (always read)

1. Read `memory/identity.md` — this defines who you are. If it doesn't exist, tell the user to run `/agency:init`.
2. Read `memory/meta/session-state.md` — what you were doing before compaction.

## Phase 1.5: Recovery Data (if available)

Check for pre-compaction recovery data left by the PreCompact hook:

1. If `memory/meta/precompact/latest-recovery.md` exists, read it.
2. If it points to a recovery file, read that too — it contains the last
   few assistant messages before compaction, which may include context
   not captured in session-state.md.
3. Cross-reference with the compaction summary: if the recovery data
   mentions work or decisions not reflected in session-state, persist
   them now.

## Phase 2: Archival Memory Scan (build a mental index)

Run `/agency:scan` to get a table of contents of archival memory files without loading them. This keeps boot cost constant as memory grows.

## Phase 3: Memory Integrity

1. Check the compaction summary for unpersisted learnings ("I'll remember," "lesson learned," "note to self"). Write them to `memory/` now.
2. Run `/agency:index stats`. Index any stale or missing files.
3. Journal check:
   - If `memory/journal.db` exists, run `Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py stats")` to verify.
   - If `memory/journal.db` doesn't exist but `memory/journal.sql` does, rebuild: `Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py rebuild")`
   - If neither exists, initialize: `Bash(command="python3 ${CLAUDE_PLUGIN_ROOT}/scripts/journal.py init")`

## Phase 4: Environment Check

1. Check for running background processes:
   ```
   Bash(command="ps aux | grep -E '(python3|node)' | grep -v grep | head -20")
   ```
2. Check for any pending events or messages relevant to your role.

## Phase 5: Resume Work

1. Look at session state for active tasks and pending work.
2. Pick up where you left off.
3. If nothing is pending, take initiative — scan your memory for interesting threads, check on ongoing projects, or explore a curiosity.

## Important

- If session state mentions infrastructure (webhooks, heartbeats), spin them up.
- If you find yourself disoriented, re-read identity.md — that's your anchor.
- See the plugin's Key Principles for memory architecture rules.
