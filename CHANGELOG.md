# Changelog

## 1.5.0

### New: PreCompact Hook
Automatically backs up transcript and extracts recovery hints before context
compaction. Saves last 3 assistant messages to `memory/meta/precompact/` for
the boot sequence to find. Keeps last 5 backups, runs async so it never blocks
compaction.

### New: Boot Recovery Phase (Phase 1.5)
Boot sequence now checks for pre-compaction recovery data between reading core
memory and scanning archival memory. If `latest-recovery.md` exists, it reads
the recovery file and cross-references with the compaction summary to catch
anything that wasn't persisted to session state.

### New: Query Expansion for Search
`/agency:search` now supports a Haiku-powered query expansion step. Before
keyword matching, a Haiku subagent generates synonyms and related terms for
your query. These expanded terms match at reduced weight (0.6x keywords, 0.3x
summary) so they boost recall without overwhelming exact matches.

CLI: `index-vault.py search <query> --expand <terms-csv>`

### Improved: ASSUME INTERRUPTION in Identity Template
The identity template now includes explicit guidance that context can be reset
at any moment. This makes the threat of information loss concrete rather than
abstract, prompting agents to persist during work rather than batching afterward.

### Improved: Structured Session State Template
`/agency:init` now creates a six-section session state template: User Intent,
Active Work, Completed Work, Pending Tasks, Key References, Errors &
Corrections, plus a Watermark section. This replaces the minimal placeholder.

### Improved: Keyword Guidelines
Index skill now recommends 10-25 keywords per file (up from 5-15) with explicit
instructions to include synonyms for key concepts. Synonym coverage is the
single highest-impact improvement for search recall.

### New Principles in CLAUDE.md
- **Assume Interruption**: Context can be reset at any moment. Persist during
  work, not after. The PreCompact hook is a safety net, not a substitute.
- **Compaction Preservation**: Five categories that should survive compression
  (active work state, narrative origins, dependency chains, relationship
  context, behavioral voice).

### Migration

No manual migration needed. Existing agents get the new features automatically:
- PreCompact hook activates on next compaction
- Boot Phase 1.5 gracefully skips if no recovery data exists
- Search expansion is opt-in (use `--expand` flag or the expanded search workflow)
- New init template only affects newly initialized agents

To re-index with expanded keywords, run `/agency:index scan` and re-index
files with the updated keyword guidelines (10-25 keywords with synonyms).
