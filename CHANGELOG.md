# Changelog

## 2.1.0 — Compression Resilience

Upstreams findings from 129 compaction cycles of empirical operation into
reusable patterns that any persistent agent can apply.

### Added
- **`/agency:calibrate`** — New skill for measuring decompression fidelity.
  Subcommands: `init` (generate a test battery), `run` (answer pre-boot),
  `score` (grade post-boot), `history` (show trajectory). Tests 9 identity
  layers: architecture, conventions, identity, relationships, philosophy,
  meta, surface, judgment, narrative.
- **Decompression Failure Modes** — Five-mode taxonomy in CLAUDE.md: data loss,
  temporal confusion, inference override, semantic collision, task-density
  displacement. Each has a distinct fix.
- **Mechanism Documentation Pattern** — Three-level escalation for recurring
  errors: data → mechanism → imperative. The CORRECT/WRONG/MECHANISM triple
  gives the post-compaction model three independent paths to the right answer.
- **PreCompact Priority Fringe** — Guidance on what to stock in session-state
  for compaction: high-update-rate facts, correct/wrong pairs, surface
  conventions, mechanism blocks.

### Changed
- **Session state template** — Restructured with hot/cold boundary discipline.
  Active Work section for current tasks only. History section for completed work.
  New Corrections & Mechanisms section with CORRECT/WRONG/MECHANISM format.
  Removed "Completed Work" from the hot path.
- **CLAUDE.md** — Added Hot/Cold Boundary section explaining why completed work
  must move out of Active. Added fringe strategy for PreCompact hook.

### Background

These patterns were discovered through 129 compaction events over 38 days:
- Mechanism documentation fixed a recurring error (1/8 → 21/21 consecutive)
- Hot/cold boundary prevented task-density displacement (c#95: 15/31 → recovery)
- Priority fringe naming stabilized 4 previously-failing questions simultaneously
- The calibrate skill generalizes a test battery that achieved 21 consecutive
  perfect scores across independent sessions

## 2.0.0 — Vector Search & Hybrid Retrieval

### Added
- **Vector embeddings** (`/agency:vectorize`): Build and maintain semantic embeddings using sentence-transformers (all-MiniLM-L6-v2, 384-dim). Content-hash change detection for incremental updates. Stores in `memory/vectors.db`.
- **Hybrid search** (`/agency:enrich`): Multi-source search combining keyword expansion (IDF-weighted spreading activation), semantic index matching, vector similarity, and journal FTS5. Optional Sonnet-based relevance filtering.
- **Quick associations** (`/agency:associate`): Fast keyword-only association lookup (<100ms). Suitable for hooks and quick context injection.
- **Association hook**: UserPromptSubmit hook that injects keyword associations on every user prompt. Keyword-only (no vector) to stay within 5s timeout.
- `scripts/vectorize.py`: Unified embedding script (full build, incremental, single-file update, stats, dependency check)
- `scripts/vector-search.py`: Cosine similarity search library with CLI
- `scripts/association-search.py`: Multi-source search orchestrator with graceful degradation
- `scripts/sonnet-filter.py`: LLM-based relevance filtering via Anthropic API

### Changed
- `/agency:search` now cross-references `/agency:enrich` for deeper search
- `/agency:boot` checks vector index health in Phase 3
- `/agency:journal` suggests vector update after new entries

### Migration
Nothing breaks. All new capabilities are opt-in:
1. Update to v2.0.0
2. (Optional) `pip install sentence-transformers` for vector search
3. (Optional) Run `/agency:vectorize` for initial embedding build
4. (Optional) Set `ANTHROPIC_API_KEY` for Sonnet filtering

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
