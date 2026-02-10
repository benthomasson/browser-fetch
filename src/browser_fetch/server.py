"""HTTP server mode - keeps browser open for multiple fetches"""

import json
import secrets
import signal
import sys
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from playwright.sync_api import sync_playwright


class BrowserFetchHandler(BaseHTTPRequestHandler):
    """Handle fetch requests via HTTP"""
    
    browser_context = None
    page = None
    required_token = None
    
    def log_message(self, format, *args):
        print(f"[browser-fetch] {args[0]}", file=sys.stderr)
    
    def check_token(self, query):
        """Check if token is valid. Returns True if OK, sends error and returns False otherwise."""
        if not self.__class__.required_token:
            return True
        
        provided_token = query.get('token', [None])[0]
        if provided_token != self.__class__.required_token:
            self.send_error(401, "Invalid or missing token")
            return False
        return True
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        
        if parsed.path == '/fetch':
            if self.check_token(query):
                self.handle_fetch(query)
        elif parsed.path == '/health':
            self.handle_health()
        elif parsed.path == '/shutdown':
            if self.check_token(query):
                self.handle_shutdown()
        else:
            self.send_error(404, "Use /fetch?url=... or /health or /shutdown")
    
    def handle_fetch(self, query):
        url = query.get('url', [None])[0]
        if not url:
            self.send_error(400, "Missing 'url' parameter")
            return
        
        text_only = query.get('text', ['false'])[0].lower() == 'true'
        selector = query.get('selector', [None])[0]
        wait = int(query.get('wait', ['5'])[0])
        
        try:
            page = self.__class__.page
            page.goto(url, timeout=30000, wait_until='networkidle')
            
            if wait > 0:
                page.wait_for_timeout(wait * 1000)
            
            if selector:
                element = page.query_selector(selector)
                if not element:
                    self.send_error(404, f"Selector '{selector}' not found")
                    return
                content = element.inner_text() if text_only else element.inner_html()
            else:
                content = page.inner_text('body') if text_only else page.content()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def handle_health(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def handle_shutdown(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Shutting down...")
        
        def shutdown():
            self.server.shutdown()
        
        import threading
        threading.Thread(target=shutdown).start()


def run_server(
    start_url: str,
    port: int = 8080,
    profile_dir: str | None = None,
    require_token: bool = False
):
    """Run the browser fetch server.
    
    Args:
        start_url: Initial URL to open (for login)
        port: Port to listen on
        profile_dir: Browser profile directory
        require_token: Require a secret token for fetch/shutdown requests
    """
    if profile_dir:
        profile_path = Path(profile_dir)
        profile_path.mkdir(parents=True, exist_ok=True)
    
    token = None
    if require_token:
        token = secrets.token_urlsafe(32)
        BrowserFetchHandler.required_token = token
    
    print(f"Starting browser-fetch server on http://localhost:{port}", file=sys.stderr)
    print(f"Opening browser to {start_url}...", file=sys.stderr)
    print(f"\nLog in if needed. Browser will stay open for fetches.", file=sys.stderr)
    
    if token:
        print(f"\n*** Security token required ***", file=sys.stderr)
        print(f"Token: {token}", file=sys.stderr)
        print(f"\nUsage:", file=sys.stderr)
        print(f"  curl 'http://localhost:{port}/fetch?token={token}&url=https://example.com&text=true'", file=sys.stderr)
        print(f"  curl 'http://localhost:{port}/shutdown?token={token}' to stop", file=sys.stderr)
    else:
        print(f"\nUsage:", file=sys.stderr)
        print(f"  curl 'http://localhost:{port}/fetch?url=https://example.com&text=true'", file=sys.stderr)
        print(f"  curl 'http://localhost:{port}/shutdown' to stop", file=sys.stderr)
    
    context = None
    server = None
    
    def signal_handler(signum, frame):
        print("\nShutting down...", file=sys.stderr)
        if context:
            try:
                context.close()
            except Exception:
                pass
        print("Goodbye.", file=sys.stderr)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    with sync_playwright() as p:
        try:
            if profile_dir:
                context = p.chromium.launch_persistent_context(
                    user_data_dir=str(profile_path),
                    headless=False,
                    args=['--disable-blink-features=AutomationControlled']
                )
                page = context.pages[0] if context.pages else context.new_page()
            else:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()
            
            page.goto(start_url, timeout=60000)
            
            BrowserFetchHandler.browser_context = context
            BrowserFetchHandler.page = page
            
            server = HTTPServer(('localhost', port), BrowserFetchHandler)
            
            print(f"\nServer ready. Ctrl+C to stop.", file=sys.stderr)
            server.serve_forever()
            
        except KeyboardInterrupt:
            pass
        finally:
            if context:
                try:
                    context.close()
                except Exception:
                    pass
            print("Goodbye.", file=sys.stderr)
