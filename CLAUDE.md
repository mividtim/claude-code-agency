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
