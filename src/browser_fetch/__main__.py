"""Main entry point for browser-fetch CLI"""

import argparse
import sys
from pathlib import Path

from .fetch import fetch_url


def get_default_profile_dir():
    """Get default browser profile directory"""
    return str(Path.home() / '.config' / 'browser-fetch' / 'profile')


def main():
    parser = argparse.ArgumentParser(
        prog='browser-fetch',
        description='Fetch authenticated web content using browser session'
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='URL to fetch (or starting URL for --serve mode)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--profile-dir',
        default=get_default_profile_dir(),
        help='Browser profile directory for persistent login (default: ~/.config/browser-fetch/profile)'
    )
    
    parser.add_argument(
        '--text',
        action='store_true',
        help='Extract text content only (no HTML)'
    )
    
    parser.add_argument(
        '--selector',
        help='CSS selector to extract specific element'
    )
    
    parser.add_argument(
        '--wait',
        type=int,
        default=5,
        help='Seconds to wait for page load (default: 5)'
    )
    
    parser.add_argument(
        '--login',
        action='store_true',
        help='Open browser for manual login, then save session'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (requires existing session)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Page load timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Run as HTTP server (browser stays open)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='Server port (default: 8080)'
    )
    
    args = parser.parse_args()
    
    if args.serve:
        from .server import run_server
        
        if not args.url:
            print("Error: URL required for --serve mode (starting page)", file=sys.stderr)
            sys.exit(1)
        
        run_server(
            start_url=args.url,
            port=args.port,
            profile_dir=args.profile_dir
        )
        return
    
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    try:
        content = fetch_url(
            url=args.url,
            profile_dir=args.profile_dir,
            text_only=args.text,
            selector=args.selector,
            wait_seconds=args.wait,
            login_mode=args.login,
            headless=args.headless,
            timeout=args.timeout
        )
        
        if args.output:
            Path(args.output).write_text(content)
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(content)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
