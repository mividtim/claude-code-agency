---
description: Initialize a new persistent agent. Creates memory directory, identity file, and session state template.
argument-hint: [agent-name]
allowed-tools: Bash, Read, Write
---

# Initialize Agent

Set up the directory structure for a new persistent agent.

1. Create the memory directory and subdirectories:

```
Bash(command="mkdir -p memory/meta")
```

2. Copy the identity template:

```
Bash(command="cp ${CLAUDE_PLUGIN_ROOT}/templates/identity.md memory/identity.md")
```

3. Create session state:

```
Write(file_path="memory/meta/session-state.md", content="# Session State\n\nLast updated: [date]\n\n## Current Session\n- Mode: [initial setup]\n\n## Active Tasks\n- Complete identity.md with agent details\n")
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
   - Edit `memory/meta/session-state.md` after each session
   - Add the agent's CLAUDE.md to the project root with: "After context compaction, run /agency:boot"

If `$ARGUMENTS` is provided, use it as the agent name in the identity file.
