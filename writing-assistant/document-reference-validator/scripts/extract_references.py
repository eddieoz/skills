#!/usr/bin/env python3
"""
Extract references from Markdown documents.
Supports inline links, reference-style links, footnotes, and autolinks.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Tuple


def extract_references(doc_path: str) -> List[Dict[str, Any]]:
    """
    Extract all references from a Markdown document.
    
    Returns list of dicts with:
    - url: The reference URL
    - type: Reference type (inline, reference, footnote, autolink, plain)
    - text: Link text (if available)
    - claim: The claim being made (sentence/paragraph before reference)
    - context: Surrounding context for verification
    """
    content = Path(doc_path).read_text(encoding="utf-8")
    references = []
    
    # Extract inline links [text](url) or [text](url "title")
    inline_links = extract_inline_links(content)
    references.extend(inline_links)
    
    # Extract reference-style links [text][id] with [id]: url
    ref_links = extract_reference_style_links(content)
    references.extend(ref_links)
    
    # Extract footnotes [^1] with [^1]: url or description
    footnotes = extract_footnotes(content)
    references.extend(footnotes)
    
    # Extract autolinks <http://example.com>
    autolinks = extract_autolinks(content)
    references.extend(autolinks)
    
    # Extract plain text URLs (URLs not in link syntax)
    plain_urls = extract_plain_urls(content)
    references.extend(plain_urls)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_refs = []
    for ref in references:
        if ref["url"] not in seen:
            seen.add(ref["url"])
            unique_refs.append(ref)
    
    return unique_refs


def extract_inline_links(content: str) -> List[Dict[str, Any]]:
    """Extract inline Markdown links [text](url)."""
    # Pattern matches [text](url) and [text](url "title")
    pattern = r'\[([^\]]+)\]\(([^)"\s]+)(?:\s+"[^"]*")?\)'
    
    references = []
    for match in re.finditer(pattern, content):
        text = match.group(1)
        url = match.group(2)
        
        # Get claim from surrounding context
        claim, context = extract_claim_context(content, match.start())
        
        references.append({
            "url": url,
            "type": "inline",
            "text": text,
            "claim": claim,
            "context": context,
            "position": match.start()
        })
    
    return references


def extract_reference_style_links(content: str) -> List[Dict[str, Any]]:
    """Extract reference-style links [text][id] with [id]: url definitions."""
    # First, find all reference definitions [id]: url
    ref_def_pattern = r'^\[([^\]]+)\]:\s*(\S+)(?:\s+.*)?$'
    definitions = {}
    
    for match in re.finditer(ref_def_pattern, content, re.MULTILINE):
        ref_id = match.group(1).lower()
        url = match.group(2)
        definitions[ref_id] = url
    
    # Then find all reference usages [text][id] or [text][]
    ref_use_pattern = r'\[([^\]]+)\](?:\[([^\]]*)\])?'
    
    references = []
    for match in re.finditer(ref_use_pattern, content):
        text = match.group(1)
        ref_id = match.group(2) if match.group(2) else text
        ref_id = ref_id.lower()
        
        if ref_id in definitions:
            url = definitions[ref_id]
            claim, context = extract_claim_context(content, match.start())
            
            references.append({
                "url": url,
                "type": "reference",
                "text": text,
                "claim": claim,
                "context": context,
                "position": match.start()
            })
    
    return references


def extract_footnotes(content: str) -> List[Dict[str, Any]]:
    """Extract footnote references [^1] with [^1]: definitions."""
    # Find footnote definitions [^id]: content (may contain URL)
    footnote_def_pattern = r'^\[\^(\w+)\]:\s*(.+)$'
    definitions = {}
    
    for match in re.finditer(footnote_def_pattern, content, re.MULTILINE):
        footnote_id = match.group(1)
        footnote_content = match.group(2)
        
        # Try to extract URL from footnote content
        url_match = re.search(r'https?://\S+', footnote_content)
        if url_match:
            definitions[footnote_id] = {
                "url": url_match.group(0),
                "content": footnote_content
            }
    
    # Find footnote usages [^id]
    footnote_use_pattern = r'\[\^(\w+)\]'
    
    references = []
    for match in re.finditer(footnote_use_pattern, content):
        footnote_id = match.group(1)
        
        if footnote_id in definitions:
            def_info = definitions[footnote_id]
            claim, context = extract_claim_context(content, match.start())
            
            references.append({
                "url": def_info["url"],
                "type": "footnote",
                "text": def_info["content"],
                "claim": claim,
                "context": context,
                "position": match.start()
            })
    
    return references


def extract_autolinks(content: str) -> List[Dict[str, Any]]:
    """Extract autolinks <http://example.com>."""
    pattern = r'<(https?://[^>]+)>'
    
    references = []
    for match in re.finditer(pattern, content):
        url = match.group(1)
        claim, context = extract_claim_context(content, match.start())
        
        references.append({
            "url": url,
            "type": "autolink",
            "text": url,
            "claim": claim,
            "context": context,
            "position": match.start()
        })
    
    return references


def extract_claim_context(content: str, position: int) -> Tuple[str, str]:
    """
    Extract the claim (sentence/paragraph before reference) and context.
    
    Returns:
        (claim, context) tuple
    """
    # Get text before the reference
    before_text = content[:position]
    
    # Find the start of current paragraph
    para_start = before_text.rfind('\n\n')
    if para_start == -1:
        para_start = 0
    else:
        para_start += 2
    
    # Get current paragraph
    paragraph = before_text[para_start:].strip()
    
    # Find the last sentence (split by .!? followed by space or end)
    sentence_enders = ['. ', '! ', '? ', '.”', '.”', '.”', '.\'', '?\'', '!\'']
    last_sentence_start = 0
    
    for i in range(len(paragraph) - 1, -1, -1):
        for ender in sentence_enders:
            if paragraph[i:i+len(ender)] == ender:
                last_sentence_start = i + len(ender)
                break
        if last_sentence_start > 0:
            break
    
    claim = paragraph[last_sentence_start:].strip()
    
    # Get broader context (current paragraph + next paragraph)
    after_text = content[position:]
    next_para_end = after_text.find('\n\n')
    if next_para_end == -1:
        next_para_end = len(after_text)
    
    context = paragraph + " " + after_text[:next_para_end].strip()
    
    # Clean up claim
    claim = clean_claim(claim)
    
    return claim, context


def extract_plain_urls(content: str) -> List[Dict[str, Any]]:
    """
    Extract plain text URLs that aren't part of Markdown link syntax.
    These are often at the end of lines or standalone.
    """
    # Pattern to match URLs not inside () or <>
    # Match http/https URLs that are standalone or at end of lines
    url_pattern = r'https?://[^\s<>\])\'"]+(?=[\s\n]|$)'
    
    references = []
    
    # Find all potential URLs
    for match in re.finditer(url_pattern, content):
        url = match.group(0)
        
        # Skip if this URL is inside a Markdown link () or autolink <>
        start_pos = match.start()
        
        # Check if preceded by ]( (inside link parens)
        preceding = content[max(0, start_pos-2):start_pos]
        if preceding.endswith(']('):
            continue
            
        # Check if preceded by < and followed by > (autolink)
        if start_pos > 0 and content[start_pos-1] == '<':
            end_pos = match.end()
            if end_pos < len(content) and content[end_pos] == '>':
                continue
        
        # Clean trailing punctuation
        url = url.rstrip('.,;:!?)\'"')
        
        # Get claim from surrounding context
        claim, context = extract_claim_context(content, start_pos)
        
        references.append({
            "url": url,
            "type": "plain",
            "text": url,
            "claim": claim,
            "context": context,
            "position": start_pos
        })
    
    return references


def clean_claim(claim: str) -> str:
    """Clean up extracted claim text."""
    # Remove leading/trailing whitespace
    claim = claim.strip()
    
    # Remove leading markdown list markers
    claim = re.sub(r'^[\*\-\+]\s+', '', claim)
    claim = re.sub(r'^\d+\.\s+', '', claim)
    
    # Remove leading > (blockquote)
    claim = re.sub(r'^>\s*', '', claim)
    
    # Normalize whitespace
    claim = ' '.join(claim.split())
    
    return claim


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: extract_references.py <document.md>")
        sys.exit(1)
    
    doc_path = sys.argv[1]
    refs = extract_references(doc_path)
    
    print(f"Found {len(refs)} reference(s):\n")
    for i, ref in enumerate(refs, 1):
        print(f"[{i}] {ref['type'].upper()}: {ref['url'][:60]}...")
        if ref.get('claim'):
            print(f"    Claim: {ref['claim'][:100]}...")
        print()


if __name__ == "__main__":
    main()
