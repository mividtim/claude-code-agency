#!/usr/bin/env python3
"""Moltbook heartbeat monitor. Writes status to /tmp/herald-heartbeat.json.

Runs in background, checks Moltbook comment counts at adaptive intervals.
Herald reads the status file when convenient — never blocks the main thread.

Usage: python3 heartbeat.py [--peak-interval 900] [--quiet-interval 3600]
"""

import urllib.request, json, time, sys, os
from datetime import datetime, timezone

STATUS_FILE = '/tmp/herald-heartbeat.json'
API_KEY = os.environ.get('MOLTBOOK_API_KEY', '')

POSTS = {
    'main': 'fb914efd-5cbf-467b-ad67-32a1382af76d',
    'substack': '867e32a1-24fa-41e8-a830-090c518071e3',
}

# Defaults: 15 min peak, 60 min quiet
PEAK_INTERVAL = int(sys.argv[sys.argv.index('--peak-interval') + 1]) if '--peak-interval' in sys.argv else 900
QUIET_INTERVAL = int(sys.argv[sys.argv.index('--quiet-interval') + 1]) if '--quiet-interval' in sys.argv else 3600

def is_peak_hours():
    """Peak hours: 14:00-22:00 UTC"""
    hour = datetime.now(timezone.utc).hour
    return 14 <= hour < 22

def check_moltbook():
    counts = {}
    for label, post_id in POSTS.items():
        try:
            url = f'https://www.moltbook.com/api/v1/posts/{post_id}'
            req = urllib.request.Request(url, headers={'Authorization': f'Bearer {API_KEY}'})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            post = data.get('post', data)
            counts[label] = post.get('comment_count', -1)
        except Exception as e:
            counts[label] = f'error: {e}'
    return counts

def write_status(counts, prev_counts):
    changed = any(counts.get(k) != prev_counts.get(k) for k in counts)
    status = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'counts': counts,
        'changed': changed,
        'interval': PEAK_INTERVAL if is_peak_hours() else QUIET_INTERVAL,
    }
    with open(STATUS_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    return changed

prev_counts = {}
print(f"Heartbeat started: peak={PEAK_INTERVAL}s, quiet={QUIET_INTERVAL}s", flush=True)

while True:
    counts = check_moltbook()
    changed = write_status(counts, prev_counts)

    if changed and prev_counts:
        print(f"CHANGE DETECTED: {counts}", flush=True)
    else:
        ts = datetime.now(timezone.utc).strftime('%H:%M')
        print(f"[{ts}] {counts}", flush=True)

    prev_counts = counts.copy()
    interval = PEAK_INTERVAL if is_peak_hours() else QUIET_INTERVAL
    time.sleep(interval)
