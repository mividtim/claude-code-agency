from http.server import HTTPServer, BaseHTTPRequestHandler
import json, sys, os

WATERMARK_FILE = '/tmp/slack-webhook-watermark'
MY_BOT_ID = 'B0ADWQ06NSV'
ICON_FILE = '/tmp/slack-images/flaming_trumpet_v2.png'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve the bot icon on GET /icon.png (used by Slack for icon_url)."""
        if self.path == '/icon.png' and os.path.exists(ICON_FILE):
            with open(ICON_FILE, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', len(data))
            self.send_header('Cache-Control', 'public, max-age=86400')
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        # URL verification
        if data.get('type') == 'url_verification':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(data['challenge'].encode())
            return

        if data.get('type') == 'event_callback':
            event = data.get('event', {})

            # Only process message and app_mention events
            event_type = event.get('type', '')
            if event_type not in ('message', 'app_mention'):
                self.send_response(200)
                self.end_headers()
                print(f"Skipped non-message event type: {event_type}", flush=True)
                return

            # Skip only MY OWN bot messages (to avoid self-loops)
            # Other bots (Astra, Dexy, etc.) should be heard
            is_self = False
            if event.get('bot_id') == MY_BOT_ID:
                is_self = True
            if event.get('subtype') == 'bot_message' and event.get('bot_id') == MY_BOT_ID:
                is_self = True
            if event.get('subtype') == 'message_changed':
                msg = event.get('message', {})
                if msg.get('bot_id') == MY_BOT_ID:
                    is_self = True

            if is_self:
                self.send_response(200)
                self.end_headers()
                print("Skipped own bot message", flush=True)
                return

            # Check watermark - skip events older than last processed
            event_ts = event.get('event_ts', event.get('ts', '0'))
            try:
                with open(WATERMARK_FILE, 'r') as f:
                    watermark = f.read().strip()
            except FileNotFoundError:
                watermark = '0'

            if float(event_ts) <= float(watermark):
                self.send_response(200)
                self.end_headers()
                print(f"Skipped old event (ts={event_ts}, watermark={watermark})", flush=True)
                return

            # Real message - update watermark, write event, exit
            with open(WATERMARK_FILE, 'w') as f:
                f.write(event_ts)
            with open('/tmp/slack-event.json', 'w') as f:
                json.dump(data, f)
            self.send_response(200)
            self.end_headers()
            user = event.get('user', '?')
            text = event.get('text', '')[:80]
            print(f"Got message from {user}: {text}", flush=True)
            os._exit(0)

        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass

server = HTTPServer(('0.0.0.0', 9999), Handler)
print("Slack webhook listening on port 9999", flush=True)
server.handle_request()
while True:
    try:
        server.handle_request()
    except:
        break
