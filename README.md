# browser-fetch

Fetch authenticated web content using a browser session. Uses Playwright with persistent browser profiles to maintain login sessions across requests.

## Quick Start

```bash
# Server mode with security token (recommended)
uvx --from "git+https://github.com/benthomasson/browser-fetch" browser-fetch --serve --require-token https://internal.example.com

# Server prints a token. Use it to fetch:
curl 'http://localhost:8080/fetch?token=YOUR_TOKEN&url=https://internal.example.com/page&text=true'
```

```bash
# Or single-fetch mode
uvx --from "git+https://github.com/benthomasson/browser-fetch" browser-fetch --help

# Clone and install locally
git clone https://github.com/benthomasson/browser-fetch
cd browser-fetch
uv sync
uv run playwright install chromium
```

## Usage

### First: Login to save session

```bash
# Open browser for manual login
browser-fetch --login https://internal.example.com

# Log in via the browser window, then press Enter
# Session is saved to ~/.config/browser-fetch/profile
```

### Then: Fetch pages headlessly

```bash
# Fetch full HTML
browser-fetch --headless https://internal.example.com/page

# Fetch text only (no HTML tags)
browser-fetch --headless --text https://internal.example.com/page

# Extract specific element
browser-fetch --headless --selector "main" https://internal.example.com/page

# Save to file
browser-fetch --headless -o /tmp/page.html https://internal.example.com/page
```

## Options

| Option | Description |
|--------|-------------|
| `--login` | Open browser for manual login, save session |
| `--headless` | Run without visible browser (requires saved session) |
| `--text` | Extract text content only (no HTML) |
| `--selector CSS` | Extract specific element by CSS selector |
| `-o FILE` | Save output to file |
| `--wait N` | Wait N seconds after page load (default: 5) |
| `--timeout N` | Page load timeout in seconds (default: 30) |
| `--profile-dir DIR` | Custom profile directory |
| `--serve` | Run as HTTP server (browser stays open) |
| `--port N` | Server port (default: 8080) |
| `--require-token` | Require secret token for requests (recommended) |

## Server Mode

Keep browser open for multiple fetches - best for SSO sites:

```bash
# Start server with security token (recommended)
uvx --from "git+https://github.com/benthomasson/browser-fetch" browser-fetch --serve --require-token https://internal.example.com

# Server prints:
# *** Security token required ***
# Token: abc123xyz...

# Log in via the browser window, then fetch via curl with token:
curl 'http://localhost:8080/fetch?token=abc123xyz&url=https://internal.example.com/page'
curl 'http://localhost:8080/fetch?token=abc123xyz&url=https://internal.example.com/other&text=true'

# Check health (no token needed)
curl 'http://localhost:8080/health'

# Shutdown (token required)
curl 'http://localhost:8080/shutdown?token=abc123xyz'
```

**Query parameters:**
- `token` - security token (required if --require-token used)
- `url` - URL to fetch (required)
- `text=true` - extract text only (no HTML)
- `selector=CSS` - extract specific element
- `wait=N` - wait N seconds after load

## How It Works

1. **Persistent profile**: Stores cookies and session data in `~/.config/browser-fetch/profile`
2. **Real browser**: Uses Chromium via Playwright, handles JavaScript and SSO
3. **Session reuse**: Login once, fetch many times until session expires
4. **Security token**: Random token generated on startup prevents unauthorized access

## Examples

### Fetch internal docs

```bash
# Login first
browser-fetch --login https://docs.internal.company.com

# Then fetch headlessly
browser-fetch --headless --text https://docs.internal.company.com/page
```

### Extract specific content

```bash
# Get just the main content
browser-fetch --headless --selector "article" --text https://wiki.example.com/page

# Get a specific div
browser-fetch --headless --selector "#content" https://intranet.example.com/page
```

### Use with Claude

```bash
# Start server with token
browser-fetch --serve --require-token https://internal.example.com

# Give the token to Claude, then Claude can fetch via curl:
curl 'http://localhost:8080/fetch?token=TOKEN&url=https://internal.example.com/doc&text=true'
```

## Troubleshooting

### "Session expired"
Re-run with `--login` to refresh your session.

### "401 Unauthorized"
You need to include the token in your request. Check the server output for the token.

### "Playwright not installed"
```bash
uv run playwright install chromium
```

### "Page load timeout"
Increase timeout: `--timeout 60`

### SSO redirect loops
Some SSO systems need more wait time: `--wait 10`

## Security

- **Use --require-token**: Prevents other local processes from using your session
- Token is randomly generated on each server start
- Session data stored in `~/.config/browser-fetch/profile`
- Server binds to localhost only (not accessible from network)
- Profile directory permissions should be restricted
- Sessions expire when the site's auth expires
- Don't share your profile directory or token
