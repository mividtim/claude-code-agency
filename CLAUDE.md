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
  for structured output. Also handles miss logging (`miss`, `misses`). Also
  searches the journal for WHY questions.

- `/agency:calibrate` — **After compaction, to measure decompression fidelity.**
  `init` generates a test battery, `run` answers pre-boot, `score` grades
  post-boot, `history` shows the trajectory. Useful for new agents discovering
  their failure surface; optional for mature agents with stable scores.

- `/agency:journal` — **When you learn, decide, get corrected, or need to
  understand why a belief exists.** The journal is the append-only change log
  for agent memory. Subcommands: `add`, `search`, `get`, `recent`,
  `by-category`, `by-tag`, `stats`. **Always search the journal before
  modifying identity.md or core beliefs.**

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

### The Journal (change log)
The journal is orthogonal to the core/archival distinction — it records
*why* beliefs exist, not just what they are. It's a SQLite database at
`memory/journal.db` with full-text search.

Core memory is the **state** — current beliefs, values, identity. The
journal is the **log** — the append-only record of experiences that
produced that state. The state is derived from the log; the log is more
fundamental. (Pat Helland: "The truth is the log. The database is a cache
of a subset of the log.")

Core memory references journal entries via `[j:N]` notation:
```
- Never block the main thread [j:3, j:7, j:19]
```

**Rule**: Before modifying any core belief, search the journal for its
provenance. The journal may contain context you've forgotten about why
something was written the way it was.

**Rule**: When you learn something, journal it. The journal entry captures
the full context (the WHY); the belief in identity.md is just the finding
(the WHAT).

**Git strategy**: `journal.db` is .gitignored. `journal.sql` (text dump)
lives in git, updated by a pre-push hook. Boot rebuilds the db from the
dump if needed.

## Key Principles

### Vector Search (Optional)

The vector embedding pipeline (vectorize, vector-search, enrich) requires
sentence-transformers, which is a heavy dependency (~2GB with PyTorch). It
is entirely optional — all existing keyword-based search continues to work
without it. Agents that install it gain:
- Semantic similarity search (finds related files even when keywords don't overlap)
- Hybrid search combining keyword and vector signals
- Sonnet-filtered results for high-value queries

Install: `pip install sentence-transformers`
The first embedding run takes ~30s for a typical vault. Incremental updates
are fast (~1s per file).

Sonnet filtering requires `ANTHROPIC_API_KEY` in the environment.

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

### Assume Interruption
Your context window can be reset at any moment. Treat every insight, decision,
or piece of progress as potentially the last thing you'll remember. Don't
batch state writes — persist *during* work, not after. Update session-state.md
as you go, not just at the end of a task.

The PreCompact hook backs up the transcript and extracts recovery hints
automatically. But hooks can't capture what you *understood* — only what you
*wrote down*. The hook is a safety net, not a substitute for disciplined
persistence.

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

### Single Source of Truth
Every principle, rule, or convention should live in exactly one place. This
plugin's CLAUDE.md is the authority for memory architecture principles. Skill
files (boot, index, search) contain *procedures*, not restated principles.
Agent identity templates contain *pointers* to principles, not copies. When
you find the same rule in two files, delete the copy and add a reference.
Duplication means the next edit will fix one copy and leave the other stale.

### Keep the Index Current
When you write or update a file in `memory/`, run `/agency:index` afterward to
keep the semantic index current. The index is how future-you (or a subagent)
finds the right file without reading everything. An unindexed memory file is
a file that might as well not exist after the next compaction.

### Decompression Failure Modes

Five ways identity degrades through compaction. Knowing the taxonomy helps
you build targeted defenses rather than hoping the compressor gets lucky.

1. **Data loss** — facts disappear during compression. Fix: vault the fact
   in a file that gets loaded on boot (identity.md or session-state.md).
2. **Temporal confusion** — multiple versions of a fact exist; the wrong one
   is retrieved. Fix: use the mechanism documentation pattern (see below).
3. **Inference override** — the correct fact is present but the model's prior
   overrides it. Fix: imperative instructions ("DO NOT X") work better than
   declarative facts ("X is Y").
4. **Semantic collision** — two legitimate facts match the same query; the
   more-reinforced one wins. Fix: name the collision explicitly in session state.
5. **Task-density displacement** — high-volume technical work crowds identity
   content out of the compression summary's attention budget. Fix: keep session
   state lean (see Hot/Cold Boundary).

### Mechanism Documentation Pattern

When a fact keeps getting wrong after compaction, escalate through three levels:

1. **Data**: State the fact. "The answer is 49."
2. **Mechanism**: Add the WHY. "The answer is 49. MECHANISM: cycle = operator session, not compaction count."
3. **Imperative**: Add explicit anti-pattern. "The answer is 49. DO NOT INCREMENT. WRONG ANSWER: compaction number."

The triple format (CORRECT / WRONG / MECHANISM) gives the post-compaction model
three independent paths to the right answer. Empirically, data-only corrections
fail ~60% of the time, mechanism docs fail ~20%, and imperative+mechanism fails <5%.

Use this in session-state.md for any fact that has been wrong more than once.

### Session State: Hot/Cold Boundary

Session state should contain only **active** work. Completed work belongs in a
History section or a separate `session-history.md` file. This matters because:

- Compaction has a fixed attention budget for the summary
- Every line of cold (completed) work displaces a line of hot (active) work
- Task-density displacement (failure mode #5) is caused by bloated session state

**Rule**: When work is done, move it from Active to History. Keep Active lean —
it should answer "what am I doing RIGHT NOW?" not "what have I ever done?"

### Compaction Preservation
When context is being compressed, the compactor decides what survives. You
can influence this by structuring information so the compressor recognizes
what matters. These categories should survive compaction:

- **Active work state**: what you were doing, what's pending, where you stopped
- **Narrative origins**: the stories BEHIND concepts, not just labels. A name
  without its origin story is a dead pointer after compaction.
- **Dependency chains**: which concepts reference which. Provenance links
  (`[j:N]`) and file cross-references.
- **Relationship context**: who said what, tone calibrations, ongoing threads
- **Behavioral voice**: distinctive patterns, style markers, things that make
  this agent sound like itself rather than generic Claude

The PreCompact hook handles mechanical backup. These categories guide what
the *compressor itself* should prioritize when summarizing your context.

### PreCompact Priority Fringe

The compaction summary has limited space. Some facts matter more than others.
Your session-state.md is the primary lever — what's in it at compaction time
determines what survives. Stock it with:

- **High-update-rate facts** — things that change often and have version ambiguity
  (counters, timestamps, "current" values that differ from "previous" values)
- **Correct/wrong answer pairs** — for any fact that has been wrong before, include
  both the right answer and the wrong answer the model tends to produce
- **Surface conventions** — formatting habits, emoji usage, signature markers.
  These degrade first under compression because they have low K-complexity and
  zero task-value. If you care about them, name them explicitly.
- **Mechanism blocks** — the CORRECT/WRONG/MECHANISM triples from the pattern above

What to keep OUT of the priority fringe: completed work, historical data that's
in the journal, anything that can be re-derived from vault files on demand.

### Publishing Releases

When publishing a new version of this plugin:

1. Update `CHANGELOG.md` with the new version and changes
2. Update `.claude-plugin/plugin.json` version field
3. Commit, tag (`git tag vX.Y.Z`), and push with tags
4. **Create a GitHub release** with `gh release create vX.Y.Z` including
   release notes derived from the changelog entry. This is not optional —
   tags without releases are invisible to users browsing the repo.

### Versioning: Major Means Breaking

**Major version bumps (X.0.0) are reserved for breaking changes to the API
surface** — removed skills, renamed scripts, changed hook contracts, anything
that would break an existing agent on upgrade. The Claude Code `/plugin update`
command will not cross major version boundaries automatically, so a major bump
forces users to manually reinstall. Use minor bumps for new features (even
large ones) when nothing breaks for existing users.
