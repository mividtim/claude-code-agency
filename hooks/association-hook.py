#!/usr/bin/env python3
"""UserPromptSubmit hook: inject associative memory context.

Reads the user prompt from stdin (Claude Code hook JSON), runs association
search against the agent's memory vault, and outputs brief context for injection.

Designed to be fast (<500ms). If search fails or returns nothing, outputs
nothing (empty stdout = no context injection).

Stdin: {"prompt": "...", "session_id": "...", "cwd": "...", ...}
Stdout: plain text context (added to Claude's view) or nothing
"""

import importlib.util
import json
import os
import sys
import time

HOOK_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(HOOK_DIR)
SEARCH_MODULE = os.path.join(PLUGIN_ROOT, "scripts", "association-search.py")

# Cache the loaded module
_search_mod = None


def _load_search():
    global _search_mod
    if _search_mod is not None:
        return _search_mod
    if not os.path.isfile(SEARCH_MODULE):
        return None
    spec = importlib.util.spec_from_file_location("association_search", SEARCH_MODULE)
    if spec is None or spec.loader is None:
        return None
    _search_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_search_mod)
    return _search_mod


def main():
    t0 = time.time()

    # Read hook input from stdin
    try:
        raw = sys.stdin.read()
        hook_input = json.loads(raw)
    except Exception:
        sys.exit(0)  # Silent fail — don't block prompt

    prompt = hook_input.get("prompt", "")
    if not prompt or len(prompt) < 10:
        sys.exit(0)

    # Resolve CWD from hook input, fall back to plugin root
    cwd = hook_input.get("cwd", PLUGIN_ROOT)

    # Load and run association search
    search = _load_search()
    if search is None:
        sys.exit(0)

    try:
        # Skip vector search in the hook — model loading takes ~5s on first
        # call, which exceeds the 5s hook timeout. Keyword+expansion is <50ms
        # and sufficient for prompt-level associations. Vector search is
        # available via /agency:enrich for deeper queries.
        result = search.search_associations(prompt, top_k=8, vector_limit=0)
        assocs = result.get("results", [])
    except Exception as e:
        print(f"[assoc-hook] search error: {e}", file=sys.stderr)
        sys.exit(0)

    if not assocs:
        sys.exit(0)

    # Format concise output — file paths + one-line summaries
    lines = []
    seen_sources = set()
    for a in assocs[:5]:
        source = a.get("source", "")
        if source in seen_sources:
            continue
        seen_sources.add(source)

        atype = a.get("type", "")
        summary = a.get("summary", "")[:120]
        score = a.get("score", 0)

        # Only include if reasonably relevant
        if score < 0.1:
            continue

        if atype == "vault":
            lines.append(f"  {source}: {summary}")
        elif atype == "journal":
            lines.append(f"  {source}: {summary}")
        else:
            lines.append(f"  [{atype}] {source}: {summary}")

    elapsed_ms = int((time.time() - t0) * 1000)

    if lines:
        print(f"[Associations ({elapsed_ms}ms)]")
        print("\n".join(lines))

    sys.exit(0)


if __name__ == "__main__":
    main()
