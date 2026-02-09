#!/usr/bin/env python3
"""Download Slack image files from event JSON or a direct message timestamp.

Usage:
  # From the last webhook event:
  python3 slack-image.py

  # From a specific message by timestamp:
  python3 slack-image.py --ts 1770521192.707369

  # From a specific message URL:
  python3 slack-image.py --url https://mividstudios.slack.com/archives/C0ADW24BYJV/p1770521192707369

Downloads images to /tmp/slack-images/ and prints their paths.
"""

import urllib.request, json, os, sys, re

TOKEN = os.environ.get('SLACK_BOT_TOKEN', '')
CHANNEL = os.environ.get('SLACK_CHANNEL_ID', 'C0ADW24BYJV')
IMAGE_DIR = '/tmp/slack-images'

os.makedirs(IMAGE_DIR, exist_ok=True)


def fetch_message(ts):
    """Fetch a specific message by timestamp."""
    req = urllib.request.Request(
        f'https://slack.com/api/conversations.history?channel={CHANNEL}&oldest={ts}&latest={ts}&inclusive=true&limit=1',
        headers={'Authorization': f'Bearer {TOKEN}'}
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    messages = data.get('messages', [])
    return messages[0] if messages else None


def download_image(file_info):
    """Download a Slack file using url_private_download with bot token auth.

    Uses url_private_download (direct download URL) and validates that the
    response is actually an image (not an HTML login redirect, which happens
    when the bot token lacks files:read scope).
    """
    url = file_info.get('url_private_download', file_info.get('url_private'))
    name = file_info.get('name', 'image.jpg')
    mimetype = file_info.get('mimetype', '')
    if not url:
        return None

    dest = os.path.join(IMAGE_DIR, name)
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOKEN}'})
    resp = urllib.request.urlopen(req)
    data = resp.read()
    content_type = resp.headers.get('Content-Type', '')

    # Validate we got an image, not an HTML login page
    if 'text/html' in content_type or data[:5] == b'<!DOC':
        print(f"ERROR: Got HTML instead of image for {name}")
        print(f"  This usually means the bot token lacks files:read scope.")
        print(f"  Add files:read at https://api.slack.com/apps -> OAuth & Permissions")
        return None

    with open(dest, 'wb') as f:
        f.write(data)
    print(f"  {len(data)} bytes, {content_type}")
    return dest


def extract_images_from_message(msg):
    """Extract and download all image files from a message."""
    files = msg.get('files', [])
    image_files = [f for f in files if f.get('mimetype', '').startswith('image/')]
    paths = []
    for f in image_files:
        path = download_image(f)
        if path:
            paths.append(path)
            print(f"Downloaded: {f.get('name')} -> {path}")
    return paths


def ts_from_url(url):
    """Extract timestamp from a Slack message URL."""
    match = re.search(r'/p(\d+)$', url)
    if match:
        raw = match.group(1)
        return raw[:10] + '.' + raw[10:]
    return None


if __name__ == '__main__':
    ts = None

    if '--url' in sys.argv:
        idx = sys.argv.index('--url') + 1
        ts = ts_from_url(sys.argv[idx])
    elif '--ts' in sys.argv:
        idx = sys.argv.index('--ts') + 1
        ts = sys.argv[idx]

    if ts:
        msg = fetch_message(ts)
        if not msg:
            print(f"No message found at ts={ts}")
            sys.exit(1)
    else:
        # Use last webhook event
        try:
            with open('/tmp/slack-event.json') as f:
                data = json.load(f)
            msg = data.get('event', {})
        except FileNotFoundError:
            print("No /tmp/slack-event.json found")
            sys.exit(1)

    paths = extract_images_from_message(msg)
    if not paths:
        print("No images found in message")
    else:
        print(f"\n{len(paths)} image(s) downloaded to {IMAGE_DIR}")
