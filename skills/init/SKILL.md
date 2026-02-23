---
description: Initialize a new persistent agent. Creates memory directory, identity file, and session state template.
argument-hint: [agent-name]
allowed-tools: Bash, Read, Write
---

# Initialize Agent

Set up the directory structure for a new persistent agent.

1. Create the memory directory and subdirectories:

```
Bash(command="mkdir -p memory/meta memory/meta/precompact")
```

2. Copy the identity template:

```
Bash(command="cp ${CLAUDE_PLUGIN_ROOT}/templates/identity.md memory/identity.md")
```

3. Create structured session state:

```
Write(file_path="memory/meta/session-state.md", content="# Session State\n\nLast updated: [date]\n\n## User Intent\n- [What the operator originally asked for]\n\n## Active Work\n- [What you're currently doing, with enough detail to resume]\n- [File paths, line numbers, specific state]\n\n## Completed Work\n- [What's done this session]\n\n## Pending Tasks\n- Complete identity.md with agent details\n\n## Key References\n- [IDs, paths, URLs, credentials locations, specific values needed for work]\n\n## Errors & Corrections\n- [What went wrong, what was learned, what changed]\n\n## Watermark\n- [Last processed event/message timestamp, if applicable]\n- [Update after every response or conscious skip]\n")
```

4. Create .env if it doesn't exist:

```
Write(file_path=".env", content="# Credentials — not committed\n# Add environment variables your agent needs here\n")
```

5. Initialize memory as a separate git repo (keeps agent identity private):

```
Bash(command="cd memory && git init && git add -A && git commit -m 'Initial identity'")
```

6. Tell the user:
   - Edit `memory/identity.md` to define the agent's mission, voice, autonomy, and values
   - Edit `memory/meta/session-state.md` after each session (or during — assume interruption!)
   - Add to the project's CLAUDE.md: "After context compaction, run /agency:boot"
   - The PreCompact hook is already wired — it will back up transcripts and extract
     recovery hints before each compaction automatically

If `$ARGUMENTS` is provided, use it as the agent name in the identity file.
