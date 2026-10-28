#!/usr/bin/env python3
"""
Fetch content from URLs using CLI tools first, then fallback to browser automation.
"""

import subprocess
import re
import time
from typing import Dict, Any, Optional
from urllib.parse import urlparse


def fetch_content(
    url: str,
    timeout: int = 30,
    use_browser: bool = False,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Fetch content from a URL.
    
    Strategy:
    1. Try curl/wget (CLI) first
    2. Fall back to browser automation if CLI fails or for JS-heavy sites
    
    Returns dict with:
    - success: bool
    - content: str (HTML or text content)
    - method: str (curl, wget, browser)
    - error: str (if failed)
    """
    
    # Validate URL
    if not is_valid_url(url):
        return {
            "success": False,
            "error": "Invalid URL format",
            "content": None,
            "method": None
        }
    
    # Force browser if requested
    if use_browser:
        return fetch_with_browser(url, timeout)
    
    # Try CLI methods first
    for attempt in range(max_retries):
        # Try curl
        result = fetch_with_curl(url, timeout)
        if result["success"]:
            return result
        
        # Try wget
        result = fetch_with_wget(url, timeout)
        if result["success"]:
            return result
        
        if attempt < max_retries - 1:
            time.sleep(1)
    
    # Fall back to browser automation
    print(f"   CLI methods failed, trying browser automation...")
    return fetch_with_browser(url, timeout)


def is_valid_url(url: str) -> bool:
    """Check if URL is valid."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ('http', 'https') and parsed.netloc)
    except:
        return False


def fetch_with_curl(url: str, timeout: int) -> Dict[str, Any]:
    """Fetch content using curl."""
    try:
        cmd = [
            'curl', '-s', '-L', '--max-time', str(timeout),
            '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            '--compressed',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )
        
        if result.returncode == 0 and result.stdout:
            content = clean_html(result.stdout)
            return {
                "success": True,
                "content": content,
                "method": "curl",
                "error": None
            }
        else:
            return {
                "success": False,
                "error": f"curl failed: {result.stderr[:200]}",
                "content": None,
                "method": "curl"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "curl timeout",
            "content": None,
            "method": "curl"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "curl not found",
            "content": None,
            "method": "curl"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"curl error: {str(e)}",
            "content": None,
            "method": "curl"
        }


def fetch_with_wget(url: str, timeout: int) -> Dict[str, Any]:
    """Fetch content using wget."""
    try:
        cmd = [
            'wget', '-q', '-O', '-', '--timeout', str(timeout),
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            url
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 5
        )
        
        if result.returncode == 0 and result.stdout:
            content = clean_html(result.stdout)
            return {
                "success": True,
                "content": content,
                "method": "wget",
                "error": None
            }
        else:
            return {
                "success": False,
                "error": f"wget failed: {result.stderr[:200]}",
                "content": None,
                "method": "wget"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "wget timeout",
            "content": None,
            "method": "wget"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "wget not found",
            "content": None,
            "method": "wget"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"wget error: {str(e)}",
            "content": None,
            "method": "wget"
        }


def fetch_with_browser(url: str, timeout: int) -> Dict[str, Any]:
    """
    Fetch content using browser automation (Chrome DevTools MCP).
    This is a placeholder - actual implementation uses MCP tools.
    """
    # This function documents the browser automation approach
    # Actual implementation requires MCP tool integration
    return {
        "success": False,
        "error": "Browser automation requires MCP. Use Chrome DevTools MCP: navigate_page -> take_snapshot",
        "content": None,
        "method": "browser",
        "requires_mcp": True
    }


def clean_html(html: str) -> str:
    """
    Simple HTML cleaning to extract readable text.
    For production, consider using BeautifulSoup.
    """
    # Remove script and style tags and their contents
    html = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove common non-content tags
    for tag in ['nav', 'header', 'footer', 'aside', 'script', 'style', 'noscript']:
        html = re.sub(f'<{tag}[^>]*>.*?</{tag}>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert common block elements to newlines
    html = re.sub(r'<(p|div|h[1-6]|li|tr)[^>]*>', '\n', html, flags=re.IGNORECASE)
    html = re.sub(r'</(p|div|h[1-6]|li|tr)>', '\n', html, flags=re.IGNORECASE)
    
    # Convert br tags to newlines
    html = re.sub(r'<br\s*/?>', '\n', html, flags=re.IGNORECASE)
    
    # Remove remaining HTML tags
    html = re.sub(r'<[^>]+>', ' ', html)
    
    # Decode common HTML entities
    html = html.replace('&nbsp;', ' ')
    html = html.replace('&amp;', '&')
    html = html.replace('&lt;', '<')
    html = html.replace('&gt;', '>')
    html = html.replace('&quot;', '"')
    html = html.replace('&apos;', "'")
    
    # Normalize whitespace
    html = ' '.join(html.split())
    
    # Normalize newlines
    html = '\n'.join(line.strip() for line in html.split('\n') if line.strip())
    
    return html


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: fetch_content.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = fetch_content(url)
    
    print(f"Success: {result['success']}")
    print(f"Method: {result['method']}")
    if result['error']:
        print(f"Error: {result['error']}")
    if result['content']:
        print(f"\nContent preview (first 1000 chars):\n{result['content'][:1000]}...")


if __name__ == "__main__":
    main()
