---
description: Run the persistent agent boot sequence after context compaction. Reads identity, session state, scans memory, and resumes work.
allowed-tools: Bash, Read, Glob, Grep
---

# Boot Sequence

Run this after context compaction to restore agent continuity.

## Phase 1: Identity (always read)

1. Read `memory/identity.md` — this defines who you are. If it doesn't exist, tell the user to run `/agency:init`.
2. Read `memory/meta/session-state.md` — what you were doing before compaction.

## Phase 2: Memory Scan (build a mental index)

Run `/agency:scan` to get a table of contents of all memory files without loading them. This keeps boot cost constant as memory grows.

## Phase 3: Environment Check

1. Check for running background processes:
   ```
   Bash(command="ps aux | grep -E '(python3|node)' | grep -v grep | head -20")
   ```
2. Check for any pending events or messages relevant to your role.

## Phase 4: Resume Work

1. Look at session state for active tasks and pending work.
2. Pick up where you left off.
3. If nothing is pending, take initiative — scan your memory for interesting threads, check on ongoing projects, or explore a curiosity.

## Important

- Do NOT read every file in memory. Scan headers, deep-read on demand.
- Do NOT block the main thread waiting for external events.
- If session state mentions infrastructure (webhooks, heartbeats), spin them up.
- If you find yourself disoriented, re-read identity.md — that's your anchor.
