#!/usr/bin/env python3
"""Journal system for agent memory — the log of WHY beliefs exist.

An append-only SQLite database that records the context behind changes
to an agent's identity, values, and knowledge. Each entry captures not
just what was learned, but why — the reasoning chain, what was considered,
what was rejected.

Core memory (identity.md) references journal entries via `[j:N]` notation,
creating a provenance chain from belief to experience.

The journal.db binary is .gitignored. A text SQL dump (journal.sql) lives
in git, updated by a pre-push hook. On fresh clone or pull, rebuild the
db from the dump.

Usage:
  python3 scripts/journal.py init
  python3 scripts/journal.py add <category> <summary> <context> [--source X] [--tags a,b] [--refs 1,2]
  python3 scripts/journal.py get <id>
  python3 scripts/journal.py search <query>
  python3 scripts/journal.py recent [N]
  python3 scripts/journal.py by-category <category>
  python3 scripts/journal.py by-tag <tag>
  python3 scripts/journal.py refs <id>
  python3 scripts/journal.py dump
  python3 scripts/journal.py rebuild [sql-file]
  python3 scripts/journal.py stats
"""

import os
import sqlite3
import sys
from datetime import datetime, timezone

VAULT_DIR = 'memory'
DB_PATH = os.path.join(VAULT_DIR, 'journal.db')
DUMP_PATH = os.path.join(VAULT_DIR, 'journal.sql')

SCHEMA = """
CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    category TEXT,
    summary TEXT NOT NULL,
    context TEXT NOT NULL,
    source TEXT,
    tags TEXT,
    refs TEXT
);

CREATE VIRTUAL TABLE IF NOT EXISTS journal_fts USING fts5(
    summary, context, tags,
    content='journal',
    content_rowid='id'
);

-- Triggers to keep FTS in sync with journal table
CREATE TRIGGER IF NOT EXISTS journal_ai AFTER INSERT ON journal BEGIN
    INSERT INTO journal_fts(rowid, summary, context, tags)
    VALUES (new.id, new.summary, new.context, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS journal_ad AFTER DELETE ON journal BEGIN
    INSERT INTO journal_fts(journal_fts, rowid, summary, context, tags)
    VALUES ('delete', old.id, old.summary, old.context, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS journal_au AFTER UPDATE ON journal BEGIN
    INSERT INTO journal_fts(journal_fts, rowid, summary, context, tags)
    VALUES ('delete', old.id, old.summary, old.context, old.tags);
    INSERT INTO journal_fts(rowid, summary, context, tags)
    VALUES (new.id, new.summary, new.context, new.tags);
END;
"""


def get_db():
    """Open or create the journal database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def format_entry(row):
    """Format a journal entry for display."""
    lines = [f'j:{row["id"]}  [{row["timestamp"][:10]}]  {row["category"] or "—"}']
    lines.append(f'  {row["summary"]}')
    if row['source']:
        lines.append(f'  source: {row["source"]}')
    if row['tags']:
        lines.append(f'  tags: {row["tags"]}')
    if row['refs']:
        lines.append(f'  refs: {row["refs"]}')
    lines.append(f'  ---')
    # Indent context, truncate for display
    ctx = row['context']
    if len(ctx) > 500:
        ctx = ctx[:497] + '...'
    for line in ctx.split('\n'):
        lines.append(f'  {line}')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_init():
    """Initialize the journal database with schema."""
    if os.path.exists(DB_PATH):
        print(f'Journal already exists at {DB_PATH}')
        conn = get_db()
        # Ensure schema is current
        conn.executescript(SCHEMA)
        conn.close()
        print('Schema verified.')
        return

    conn = get_db()
    conn.executescript(SCHEMA)
    conn.close()
    print(f'Journal initialized at {DB_PATH}')


def cmd_add(category, summary, context, source=None, tags=None, refs=None):
    """Add a new journal entry. Returns the new entry ID."""
    conn = get_db()
    ts = datetime.now(timezone.utc).isoformat()

    # Normalize tags and refs
    tags_str = ','.join(t.strip() for t in tags.split(',')) if tags else None
    refs_str = refs if refs else None

    cursor = conn.execute(
        'INSERT INTO journal (timestamp, category, summary, context, source, tags, refs) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (ts, category, summary, context, source, tags_str, refs_str)
    )
    entry_id = cursor.lastrowid
    conn.commit()
    conn.close()
    print(f'j:{entry_id}  [{ts[:10]}]  {category}')
    print(f'  {summary}')
    return entry_id


def cmd_get(entry_id):
    """Retrieve a single journal entry by ID."""
    conn = get_db()
    row = conn.execute('SELECT * FROM journal WHERE id = ?', (entry_id,)).fetchone()
    conn.close()

    if not row:
        print(f'No entry with id {entry_id}')
        return None

    print(format_entry(row))
    return row


def cmd_search(query):
    """Full-text search across summary, context, and tags."""
    conn = get_db()
    # FTS5 query — quote terms for safety
    fts_query = ' OR '.join(f'"{term}"' for term in query.split())
    try:
        rows = conn.execute(
            'SELECT j.*, rank FROM journal_fts fts '
            'JOIN journal j ON j.id = fts.rowid '
            'WHERE journal_fts MATCH ? '
            'ORDER BY rank '
            'LIMIT 20',
            (fts_query,)
        ).fetchall()
    except sqlite3.OperationalError:
        # Fallback to LIKE search if FTS fails
        like_pattern = f'%{query}%'
        rows = conn.execute(
            'SELECT *, 0 as rank FROM journal '
            'WHERE summary LIKE ? OR context LIKE ? OR tags LIKE ? '
            'ORDER BY timestamp DESC LIMIT 20',
            (like_pattern, like_pattern, like_pattern)
        ).fetchall()

    conn.close()

    if not rows:
        print(f'No matches for: {query}')
        return []

    print(f'Journal search: {query}  ({len(rows)} results)\n')
    for row in rows:
        print(format_entry(row))
        print()

    return rows


def cmd_recent(n=10):
    """Show the N most recent journal entries."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM journal ORDER BY id DESC LIMIT ?', (n,)
    ).fetchall()
    conn.close()

    if not rows:
        print('Journal is empty.')
        return []

    print(f'Last {len(rows)} entries:\n')
    for row in rows:
        print(format_entry(row))
        print()

    return rows


def cmd_by_category(category):
    """List entries by category."""
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM journal WHERE category = ? ORDER BY id DESC',
        (category,)
    ).fetchall()
    conn.close()

    if not rows:
        print(f'No entries with category: {category}')
        return []

    print(f'Category: {category}  ({len(rows)} entries)\n')
    for row in rows:
        print(format_entry(row))
        print()

    return rows


def cmd_by_tag(tag):
    """List entries containing a specific tag."""
    conn = get_db()
    like_pattern = f'%{tag}%'
    rows = conn.execute(
        'SELECT * FROM journal WHERE tags LIKE ? ORDER BY id DESC',
        (like_pattern,)
    ).fetchall()
    conn.close()

    # Filter for exact tag match within comma-separated list
    filtered = []
    for row in rows:
        entry_tags = [t.strip().lower() for t in (row['tags'] or '').split(',')]
        if tag.lower() in entry_tags:
            filtered.append(row)

    if not filtered:
        print(f'No entries with tag: {tag}')
        return []

    print(f'Tag: {tag}  ({len(filtered)} entries)\n')
    for row in filtered:
        print(format_entry(row))
        print()

    return filtered


def cmd_refs(entry_id):
    """Find all entries that reference a given entry ID."""
    conn = get_db()
    # Search for references like "1" or "1," or ",1" in the refs field
    rows = conn.execute(
        'SELECT * FROM journal WHERE refs LIKE ? OR refs LIKE ? OR refs LIKE ? OR refs = ? '
        'ORDER BY id DESC',
        (f'{entry_id},%', f'%,{entry_id},%', f'%,{entry_id}', str(entry_id))
    ).fetchall()
    conn.close()

    if not rows:
        print(f'No entries reference j:{entry_id}')
        return []

    print(f'Entries referencing j:{entry_id}  ({len(rows)} results)\n')
    for row in rows:
        print(format_entry(row))
        print()

    return rows


def cmd_dump():
    """Dump the journal to SQL text format."""
    if not os.path.exists(DB_PATH):
        print('No journal database found.')
        return

    conn = sqlite3.connect(DB_PATH)
    dump = '\n'.join(conn.iterdump())
    conn.close()

    with open(DUMP_PATH, 'w') as f:
        f.write(dump)
        f.write('\n')

    print(f'Dumped to {DUMP_PATH}')


def cmd_rebuild(sql_file=None):
    """Rebuild journal.db from a SQL dump file."""
    sql_file = sql_file or DUMP_PATH

    if not os.path.exists(sql_file):
        print(f'SQL dump not found: {sql_file}')
        return False

    # Remove existing db to rebuild clean
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(sql_file, 'r') as f:
        sql = f.read()
    conn.executescript(sql)
    conn.close()

    count = sqlite3.connect(DB_PATH).execute('SELECT COUNT(*) FROM journal').fetchone()[0]
    print(f'Rebuilt {DB_PATH} from {sql_file} ({count} entries)')
    return True


def cmd_stats():
    """Print journal statistics."""
    if not os.path.exists(DB_PATH):
        print('No journal database found. Run: journal.py init')
        return

    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM journal').fetchone()[0]

    if total == 0:
        print('Journal is empty.')
        conn.close()
        return

    categories = conn.execute(
        'SELECT category, COUNT(*) as cnt FROM journal GROUP BY category ORDER BY cnt DESC'
    ).fetchall()

    first = conn.execute('SELECT timestamp FROM journal ORDER BY id ASC LIMIT 1').fetchone()
    last = conn.execute('SELECT timestamp FROM journal ORDER BY id DESC LIMIT 1').fetchone()

    # Tag frequency
    all_tags = {}
    rows = conn.execute('SELECT tags FROM journal WHERE tags IS NOT NULL').fetchall()
    for row in rows:
        for tag in row['tags'].split(','):
            tag = tag.strip().lower()
            if tag:
                all_tags[tag] = all_tags.get(tag, 0) + 1

    conn.close()

    print(f'Journal entries:  {total}')
    print(f'Date range:       {first[0][:10]} to {last[0][:10]}')
    print(f'Categories:')
    for cat in categories:
        print(f'  {cat["category"] or "(none)":20s}  {cat["cnt"]}')
    if all_tags:
        top_tags = sorted(all_tags.items(), key=lambda x: -x[1])[:15]
        print(f'Top tags:')
        for tag, count in top_tags:
            print(f'  {tag:20s}  {count}')


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

USAGE = """\
Usage: journal.py <command> [args]

Commands:
  init                                      Create journal database
  add <cat> <summary> <context> [options]   Add entry (--source X --tags a,b --refs 1,2)
  get <id>                                  Show entry by ID
  search <query>                            Full-text search
  recent [N]                                Last N entries (default 10)
  by-category <category>                    Filter by category
  by-tag <tag>                              Filter by tag
  refs <id>                                 Find entries referencing ID
  dump                                      Export to journal.sql
  rebuild [sql-file]                        Rebuild db from SQL dump
  stats                                     Show statistics

Categories: learning, correction, decision, experiment, conversation
"""

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(USAGE)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'init':
        cmd_init()

    elif cmd == 'add':
        if len(sys.argv) < 5:
            print('Usage: journal.py add <category> <summary> <context> [--source X] [--tags a,b] [--refs 1,2]')
            sys.exit(1)
        category = sys.argv[2]
        summary = sys.argv[3]
        context = sys.argv[4]
        # Parse optional flags
        source = tags = refs = None
        i = 5
        while i < len(sys.argv):
            if sys.argv[i] == '--source' and i + 1 < len(sys.argv):
                source = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--tags' and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--refs' and i + 1 < len(sys.argv):
                refs = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        cmd_add(category, summary, context, source, tags, refs)

    elif cmd == 'get':
        if len(sys.argv) < 3:
            print('Usage: journal.py get <id>')
            sys.exit(1)
        cmd_get(int(sys.argv[2]))

    elif cmd == 'search':
        if len(sys.argv) < 3:
            print('Usage: journal.py search <query>')
            sys.exit(1)
        cmd_search(' '.join(sys.argv[2:]))

    elif cmd == 'recent':
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        cmd_recent(n)

    elif cmd == 'by-category':
        if len(sys.argv) < 3:
            print('Usage: journal.py by-category <category>')
            sys.exit(1)
        cmd_by_category(sys.argv[2])

    elif cmd == 'by-tag':
        if len(sys.argv) < 3:
            print('Usage: journal.py by-tag <tag>')
            sys.exit(1)
        cmd_by_tag(sys.argv[2])

    elif cmd == 'refs':
        if len(sys.argv) < 3:
            print('Usage: journal.py refs <id>')
            sys.exit(1)
        cmd_refs(int(sys.argv[2]))

    elif cmd == 'dump':
        cmd_dump()

    elif cmd == 'rebuild':
        sql_file = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_rebuild(sql_file)

    elif cmd == 'stats':
        cmd_stats()

    else:
        print(f'Unknown command: {cmd}')
        print(USAGE)
        sys.exit(1)
