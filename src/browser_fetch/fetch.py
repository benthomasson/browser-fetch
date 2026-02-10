"""Core fetch functionality using Playwright"""

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def fetch_url(
    url: str,
    profile_dir: str,
    text_only: bool = False,
    selector: str | None = None,
    wait_seconds: int = 5,
    login_mode: bool = False,
    headless: bool = False,
    timeout: int = 30
) -> str:
    """Fetch a URL using a browser with persistent profile.
    
    Args:
        url: URL to fetch
        profile_dir: Directory to store browser profile/cookies
        text_only: Extract text content only (no HTML)
        selector: CSS selector to extract specific element
        wait_seconds: Seconds to wait after page load
        login_mode: Open browser for manual login
        headless: Run in headless mode
        timeout: Page load timeout in seconds
        
    Returns:
        Page content (HTML or text)
    """
    profile_path = Path(profile_dir)
    profile_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless and not login_mode,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        page = context.pages[0] if context.pages else context.new_page()
        
        if login_mode:
            print(f"Opening {url} for login...", file=sys.stderr)
            print("Log in to the site, then press Enter here when done.", file=sys.stderr)
            
            page.goto(url, timeout=timeout * 1000)
            input("\nPress Enter after you've logged in...")
            
            print("Session saved. You can now fetch pages with --headless.", file=sys.stderr)
            context.close()
            return "Login session saved."
        
        page.goto(url, timeout=timeout * 1000, wait_until='networkidle')
        
        if wait_seconds > 0:
            page.wait_for_timeout(wait_seconds * 1000)
        
        if selector:
            element = page.query_selector(selector)
            if not element:
                raise ValueError(f"Selector '{selector}' not found on page")
            
            if text_only:
                content = element.inner_text()
            else:
                content = element.inner_html()
        else:
            if text_only:
                content = page.inner_text('body')
            else:
                content = page.content()
        
        context.close()
        return content
