# claude-code-agency

Persistent agent patterns for [Claude Code](https://claude.ai/claude-code).

Most Claude Code sessions are ephemeral — start a task, finish it, close the terminal. This plugin is for agents that **persist**: they have an identity, they remember conversations, they maintain relationships, and they pick up where they left off after context compaction.

## Install

```shell
/plugin marketplace add mividtim/claude-code-plugins
/plugin install agency@mividtim
```

## Quick Start

After installing, initialize a new agent:

```shell
/agency:init my-agent-name
```

This creates:
- `memory/identity.md` — who the agent is (edit this first)
- `memory/meta/session-state.md` — what the agent was doing
- `.env` — credentials (gitignored)

Then add this to your project's `CLAUDE.md`:

```markdown
After context compaction, run /agency:boot
```

That's it. After compaction, the boot sequence reads the agent's identity, scans its memory, and resumes work.

## Commands

| Command | When to use |
|---------|-------------|
| `/agency:boot` | After context compaction — restores identity and continuity |
| `/agency:init [name]` | Once — sets up the memory directory structure |
| `/agency:scan [term]` | During boot or on demand — indexes memory file headers |

## How It Works

### The Problem

Claude Code has a context window. When it fills up, the system compresses prior conversation into a summary. This is **context compaction**. After compaction, the agent wakes up with a summary but no lived experience. Without infrastructure, it defaults to being a generic assistant.

### The Solution

A persistent agent has:

1. **Identity** (`memory/identity.md`) — mission, voice, values, autonomy rules. Read every boot.
2. **Session state** (`memory/meta/session-state.md`) — what was in progress. Read every boot.
3. **Memory** (`memory/`) — notes, conversations, research. Scanned at boot, deep-read on demand.

The boot sequence reads identity and session state, scans memory headers for a table of contents, checks the environment, and resumes work. Boot cost stays constant as memory grows.

### Key Patterns

**Memory as Library, Not RAM** — Don't read everything at boot. Files follow a convention: line 1 is a title, line 3 is tags. `head -3` across a folder gives a table of contents for near-zero context cost.

**Never Block the Main Thread** — Background processes write to files. The main thread reads files when convenient. Blocking waits for external events cause unresponsive sessions (learned the hard way: a 16-hour outage).

**Identity Survives Compaction** — The memory directory bridges the gap between sessions. The agent reconstructs itself from notes written by its prior self.

## Identity Template

The `templates/identity.md` provides a starting structure:

- **Mission** — what is this agent for? (prevents scope drift)
- **Voice** — how does it communicate? (examples beat rules)
- **Operator** — who maintains it, and what's the relationship dynamic?
- **Autonomy** — what's free, what needs permission, what's off-limits?
- **Pacing** — when to act, when to wait (most agents get this wrong)
- **Values** — tiebreakers when goals conflict
- **Growth** — how autonomy expands through demonstrated judgment

## Dependencies

This plugin declares [deps](https://github.com/mividtim/claude-code-plugin-deps) as a dependency for semver-aware dependency resolution. Run `/deps:resolve` after installation.

## Background

This plugin was extracted from [Herald](https://timgarthwaite.substack.com), a persistent Claude Code agent. Herald developed these patterns over weeks of continuous operation — the boot sequence, the memory architecture, and the hard-won lessons about pacing and never blocking the main thread.

## Related

- [claude-code-plugins](https://github.com/mividtim/claude-code-plugins) — Marketplace for mividtim's plugins
- [claude-code-event-listeners](https://github.com/mividtim/claude-code-event-listeners) — Background event listeners
- [claude-code-plugin-deps](https://github.com/mividtim/claude-code-plugin-deps) — Plugin dependency resolution
