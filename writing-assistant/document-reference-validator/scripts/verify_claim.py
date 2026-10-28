#!/usr/bin/env python3
"""
Verify if source content supports a claim through semantic analysis.
Enhanced for citation-style claims with title matching.
"""

import re
from typing import Dict, Any, List, Set, Tuple
from difflib import SequenceMatcher


def verify_claim(
    claim: str,
    source_content: str,
    threshold: float = 0.4  # Lowered default for citation-style documents
) -> Dict[str, Any]:
    """
    Verify if source content supports a claim.
    
    Enhanced for academic citations:
    1. Extract and match quoted titles
    2. Check author name presence
    3. Check publication identifiers (arXiv, DOI)
    4. Standard semantic analysis
    
    Returns:
        dict with status, confidence, excerpt
    """
    if not claim or not source_content:
        return {
            "status": "mismatch",
            "confidence": 0.0,
            "excerpt": "",
            "reason": "Empty claim or source"
        }
    
    # Normalize texts
    claim_norm = normalize_text(claim)
    source_norm = normalize_text(source_content)
    
    scores = []
    reasons = []
    
    # Check 1: Quoted Title Matching (highest priority for citations)
    title_match = check_quoted_title(claim, source_norm)
    if title_match["found"]:
        scores.append((title_match["score"] * 0.9, "title_match"))
        reasons.append(f"Title match: {title_match['title'][:50]}...")
    
    # Check 2: Author name matching
    author_match = check_author_in_source(claim, source_norm)
    if author_match["found"]:
        scores.append((author_match["score"] * 0.3, "author_match"))
        reasons.append(f"Author found: {author_match['author']}")
    
    # Check 3: Publication identifier matching (arXiv, DOI, etc.)
    id_match = check_publication_id(claim, source_content)
    if id_match["found"]:
        scores.append((id_match["score"] * 0.5, "id_match"))
        reasons.append(f"ID match: {id_match['id']}")
    
    # Check 4: Standard semantic analysis (entity overlap)
    entity_score = calculate_entity_overlap(
        extract_entities(claim_norm),
        extract_entities(source_norm)
    )
    scores.append((entity_score * 0.2, "entity_overlap"))
    
    # Check 5: Key phrase matching
    claim_phrases = extract_key_phrases(claim_norm)
    phrase_matches = find_phrase_matches(claim_phrases, source_norm)
    phrase_score = len(phrase_matches) / max(len(claim_phrases), 1)
    scores.append((phrase_score * 0.15, "phrase_match"))
    
    # Check 6: Direct text similarity for significant content
    if len(claim) > 50:  # Only for substantial claims (not just titles)
        similarity = text_similarity(claim_norm, source_norm)
        scores.append((similarity * 0.2, "text_similarity"))
    
    # Calculate weighted confidence
    confidence = sum(score for score, _ in scores)
    
    # Boost confidence if we have title + author combination
    has_title = any(r.startswith("Title match") for r in reasons)
    has_author = any(r.startswith("Author found") for r in reasons)
    if has_title and has_author:
        confidence = min(1.0, confidence * 1.3)  # 30% boost
    
    # Determine status with adjusted thresholds for citations
    if confidence >= 0.7 or (has_title and confidence >= 0.5):
        status = "verified"
    elif confidence >= threshold or has_title:
        status = "partial"
    else:
        status = "mismatch"
    
    # Find best excerpt
    excerpt = find_relevant_excerpt(claim_norm, source_content, phrase_matches)
    
    return {
        "status": status,
        "confidence": round(confidence, 2),
        "excerpt": excerpt,
        "reason": "; ".join(reasons) if reasons else "No strong matches found",
        "details": {
            "title_match": title_match,
            "author_match": author_match,
            "id_match": id_match,
            "entity_score": round(entity_score, 2),
            "phrase_score": round(phrase_score, 2),
            "scores_breakdown": {name: round(score, 2) for score, name in scores}
        }
    }


def check_quoted_title(claim: str, source_norm: str) -> Dict[str, Any]:
    """Extract and check quoted titles from claim against source."""
    # Extract text in quotes (single or double)
    title_patterns = [
        r'"([^"]{10,200})"',  # Double quotes, min 10 chars
        r"'([^']{10,200})'",  # Single quotes, min 10 chars
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, claim)
        if match:
            title = match.group(1)
            title_norm = normalize_text(title)
            
            # Check for title in source (allowing for some word variation)
            title_words = set(title_norm.split())
            source_words = set(source_norm.split())
            
            if len(title_words) >= 3:
                overlap = title_words.intersection(source_words)
                # Require at least 70% of title words to match
                match_ratio = len(overlap) / len(title_words)
                
                if match_ratio >= 0.7:
                    return {
                        "found": True,
                        "title": title,
                        "score": 0.8 + (match_ratio * 0.2),  # 0.8-1.0 range
                        "match_ratio": round(match_ratio, 2)
                    }
                elif match_ratio >= 0.5:
                    return {
                        "found": True,
                        "title": title,
                        "score": 0.5 + (match_ratio * 0.3),  # 0.5-0.8 range
                        "match_ratio": round(match_ratio, 2)
                    }
    
    return {"found": False, "title": "", "score": 0, "match_ratio": 0}


def check_author_in_source(claim: str, source_norm: str) -> Dict[str, Any]:
    """Check if author name from claim appears in source."""
    # Extract potential author names (Capitalized Words in claim)
    # Look for patterns like "Gerlich (2025)", "Smith and Jones", etc.
    author_patterns = [
        r'([A-Z][a-z]+(?:\s+(?:and|&)?\s*[A-Z][a-z]+)?)\s*\(\d{4}\)',  # Name (Year)
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*-',  # Name - at start
        r'^([A-Z][a-z]+)\s*\(\d{4}\)',  # Simple Name (Year) at start
    ]
    
    for pattern in author_patterns:
        match = re.search(pattern, claim)
        if match:
            author = match.group(1)
            # Normalize for matching
            author_norm = author.lower()
            
            # Check if author appears in source
            if author_norm in source_norm:
                return {"found": True, "author": author, "score": 1.0}
            
            # Check individual parts for multi-word authors
            author_parts = author_norm.split()
            if len(author_parts) > 1:
                # Check if any part appears (last name is often enough)
                if author_parts[-1] in source_norm:
                    return {"found": True, "author": author, "score": 0.7}
    
    return {"found": False, "author": "", "score": 0}


def check_publication_id(claim: str, source_content: str) -> Dict[str, Any]:
    """Check for publication identifiers like arXiv:1234.56789"""
    id_patterns = [
        (r'arXiv[\s:]*(\d{4}\.\d{4,5})', 'arxiv'),  # arXiv:2508.05867
        (r'arXiv[\s:]*(\d{4}\.\d{4,5}v\d+)', 'arxiv'),  # with version
        (r'10\.\d{4,}/[^\s]+', 'doi'),  # DOI
        (r'PMC\d+', 'pmc'),  # PubMed Central
        (r' PMID[:\s]*(\d+)', 'pmid'),  # PMID
    ]
    
    source_lower = source_content.lower()
    
    for pattern, id_type in id_patterns:
        match = re.search(pattern, claim, re.IGNORECASE)
        if match:
            pub_id = match.group(1) if len(match.groups()) > 0 else match.group(0)
            # Check if ID appears in source
            if pub_id.lower() in source_lower:
                return {
                    "found": True,
                    "id": f"{id_type}:{pub_id}",
                    "score": 0.95,
                    "type": id_type
                }
    
    return {"found": False, "id": "", "score": 0, "type": ""}


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = ' '.join(text.split())
    # Remove punctuation but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    text = ' '.join(text.split())
    return text


def extract_entities(text: str) -> Set[str]:
    """Extract named entities and important terms."""
    entities = set()
    
    # Extract numbers (including percentages, dates)
    numbers = re.findall(r'\b\d+(?:\.\d+)?(?:\s*%|\s*percent)?\b', text)
    entities.update(numbers)
    
    # Extract significant words and phrases
    words = text.split()
    
    # Extract bigrams
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if len(bigram) > 8:
            entities.add(bigram)
    
    # Add individual significant words
    stop_words = {
        'about', 'above', 'after', 'again', 'against', 'all', 'also', 'am', 'an', 'and',
        'any', 'are', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below',
        'between', 'both', 'but', 'by', 'can', 'could', 'did', 'do', 'does', 'doing',
        'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have',
        'having', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how',
        'if', 'in', 'into', 'is', 'it', 'its', 'itself', 'let', 'me', 'more', 'most',
        'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
        'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she',
        'should', 'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs',
        'them', 'themselves', 'then', 'there', 'these', 'they', 'this', 'those',
        'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were',
        'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with',
        'would', 'you', 'your', 'yours', 'yourself', 'yourselves', 'according',
        'study', 'research', 'found', 'showed', 'reported', 'said', 'says', 'article',
        'published', 'journal', 'paper', 'abstract', 'introduction', 'conclusion'
    }
    
    for word in words:
        if len(word) > 4 and word not in stop_words:
            entities.add(word)
    
    return entities


def calculate_entity_overlap(claim_entities: Set[str], source_entities: Set[str]) -> float:
    """Calculate entity overlap score."""
    if not claim_entities:
        return 0.0
    overlap = claim_entities.intersection(source_entities)
    return len(overlap) / len(claim_entities)


def extract_key_phrases(text: str) -> List[str]:
    """Extract key phrases from text."""
    phrases = []
    words = text.split()
    
    # Extract n-grams (2-4 words)
    for n in range(2, 5):
        for i in range(len(words) - n + 1):
            phrase = ' '.join(words[i:i+n])
            if len(phrase) > 10 and not any(w in phrase for w in ['http', 'www', 'com']):
                phrases.append(phrase)
    
    return phrases[:15]  # Limit to top 15


def find_phrase_matches(phrases: List[str], source: str) -> List[str]:
    """Find matching phrases in source text."""
    matches = []
    for phrase in phrases:
        if phrase in source:
            matches.append(phrase)
    return matches


def text_similarity(text1: str, text2: str) -> float:
    """Calculate text similarity using sequence matching."""
    matcher = SequenceMatcher(None, text1, text2)
    return matcher.ratio()


def find_relevant_excerpt(
    claim_norm: str,
    source: str,
    matched_phrases: List[str] = None
) -> str:
    """Find the most relevant excerpt from source."""
    paragraphs = source.split('\n')
    best_para = ""
    best_score = 0.0
    
    claim_words = set(claim_norm.split())
    
    for para in paragraphs:
        if len(para) < 30:
            continue
        
        para_norm = normalize_text(para)
        para_words = set(para_norm.split())
        overlap = len(claim_words.intersection(para_words))
        score = overlap / max(len(claim_words), 1)
        
        # Boost score if matched phrases appear
        if matched_phrases:
            for phrase in matched_phrases:
                if phrase in para_norm:
                    score += 0.1
        
        if score > best_score:
            best_score = score
            best_para = para[:600]  # Limit excerpt length
    
    return best_para


def main():
    """CLI entry point for testing."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: verify_claim.py '<claim>' '<source_content>'")
        print("\nExample:")
        print('verify_claim.py \'Gerlich (2025) - "AI Tools in Society"\' \'AI Tools in Society: Impacts on Cognitive Offloading...\'')
        sys.exit(1)
    
    claim = sys.argv[1]
    source = sys.argv[2]
    
    result = verify_claim(claim, source)
    
    print(f"Status: {result['status']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reason: {result['reason']}")
    if result['excerpt']:
        print(f"\nExcerpt: {result['excerpt'][:200]}...")
    print(f"\nDetails: {result['details']}")


if __name__ == "__main__":
    main()
