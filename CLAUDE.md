# CLAUDE.md

Instructions for Claude Code when working with browser-fetch.

## What This Tool Does

browser-fetch uses Playwright to fetch web content from authenticated sites (SSO, internal pages) by running a real browser with persistent session cookies.

## Server Mode (Recommended for Claude)

The server mode keeps a browser open and exposes an HTTP API for fetching pages.

### Starting the Server

User runs in a terminal:
```bash
uvx --from "git+https://github.com/benthomasson/browser-fetch" browser-fetch --serve --require-token https://internal.example.com
```

Server prints a security token. **Ask the user for this token.**

### Fetching Pages

Once you have the token:
```bash
curl -s 'http://localhost:8080/fetch?token=TOKEN&url=https://internal.example.com/page&text=true'
```

### Query Parameters

- `token` - Security token (required)
- `url` - URL to fetch (required)
- `text=true` - Extract text only (recommended for readability)
- `selector=main` - Extract specific CSS element
- `wait=10` - Wait N seconds for slow pages

### Checking Server Status

```bash
curl -s 'http://localhost:8080/health'
```

Returns `{"status": "ok"}` if running.

## Workflow

1. Check if server is running: `curl -s localhost:8080/health`
2. If not running, ask user to start it with `--serve --require-token`
3. Ask user for the security token
4. Fetch pages with curl using the token
5. For large pages, save to file and read: `curl ... > /tmp/page.txt`

## Common Issues

- **401 Unauthorized**: Token missing or wrong. Ask user for token.
- **Connection refused**: Server not running. Ask user to start it.
- **Login page returned**: User needs to log in via the browser window.

## Development

```bash
uv sync
uv run playwright install chromium
uv run browser-fetch --help
```

## Files

- `src/browser_fetch/__main__.py` - CLI entry point
- `src/browser_fetch/fetch.py` - Single-fetch mode
- `src/browser_fetch/server.py` - Server mode with HTTP API
