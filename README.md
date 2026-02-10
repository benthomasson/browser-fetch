# browser-fetch

Fetch authenticated web content using a browser session. Uses Playwright with persistent browser profiles to maintain login sessions across requests.

## Quick Start

```bash
# Install with uv (no clone needed)
uvx --from "git+https://github.com/benthomasson/browser-fetch" browser-fetch --help

# Or clone and install locally
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

## How It Works

1. **Persistent profile**: Stores cookies and session data in `~/.config/browser-fetch/profile`
2. **Real browser**: Uses Chromium via Playwright, handles JavaScript and SSO
3. **Session reuse**: Login once, fetch many times until session expires

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
# Fetch and save for Claude to read
browser-fetch --headless --text -o /tmp/page.txt https://internal.example.com/doc

# Then Claude can read /tmp/page.txt
```

## Troubleshooting

### "Session expired"
Re-run with `--login` to refresh your session.

### "Playwright not installed"
```bash
uv run playwright install chromium
```

### "Page load timeout"
Increase timeout: `--timeout 60`

### SSO redirect loops
Some SSO systems need more wait time: `--wait 10`

## Security

- Session data stored in `~/.config/browser-fetch/profile`
- Profile directory permissions should be restricted
- Sessions expire when the site's auth expires
- Don't share your profile directory
