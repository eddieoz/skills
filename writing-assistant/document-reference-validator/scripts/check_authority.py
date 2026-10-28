#!/usr/bin/env python3
"""
Check if a source is authoritative/reliable.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse
import json
import re


# Default authoritative source categories
DEFAULT_AUTHORITATIVE_SOURCES = {
    "academic": {
        "domains": [
            # Academic journals and publishers
            "arxiv.org",
            "doi.org",
            "jstor.org",
            "pubmed.ncbi.nlm.nih.gov",
            "ncbi.nlm.nih.gov",
            "scholar.google.com",
            "ieee.org",
            "acm.org",
            "springer.com",
            "nature.com",
            "science.org",
            "cell.com",
            "thelancet.com",
            "nejm.org",
            "bmj.com",
            "pnas.org",
            "frontiersin.org",
            "mdpi.com",
            "plos.org",
            "wiley.com",
            "tandfonline.com",
            "sciencedirect.com",
            "researchgate.net",
            "academia.edu",
            "semanticscholar.org",
            "ssrn.com",
            # Universities (common domains)
            ".edu",
            ".ac.uk",
            ".ac.jp",
            ".ac.au",
            ".ac.nz",
            ".ac.in",
        ],
        "description": "Academic journals, universities, and research institutions"
    },
    "government": {
        "domains": [
            # US Government
            ".gov",
            "whitehouse.gov",
            "congress.gov",
            "supremecourt.gov",
            "cdc.gov",
            "fda.gov",
            "epa.gov",
            "nih.gov",
            "nsf.gov",
            "nasa.gov",
            "noaa.gov",
            "usgs.gov",
            "census.gov",
            "bls.gov",
            "bea.gov",
            "federalreserve.gov",
            "treasury.gov",
            "state.gov",
            "defense.gov",
            "justice.gov",
            "uspto.gov",
            "osti.gov",
            # International government domains
            ".gov.uk",
            ".gov.au",
            ".gov.ca",
            ".gov.nz",
            ".gov.in",
            ".go.jp",
            ".go.kr",
            ".gob.mx",
            ".gouv.fr",
            ".bund.de",
            "europa.eu",
            "un.org",
            "who.int",
            "worldbank.org",
            "imf.org",
        ],
        "description": "Government agencies and international organizations"
    },
    "news_established": {
        "domains": [
            # Major international news
            "reuters.com",
            "apnews.com",
            "associatedpress.com",
            "afp.com",
            "bbc.com",
            "bbc.co.uk",
            "cnn.com",
            "nytimes.com",
            "washingtonpost.com",
            "wsj.com",
            "economist.com",
            "ft.com",
            "theguardian.com",
            "aljazeera.com",
            "npr.org",
            "pbs.org",
            "cbsnews.com",
            "abcnews.go.com",
            "nbcnews.com",
            "foxnews.com",
            "usatoday.com",
            "latimes.com",
            "chicagotribune.com",
            "bloomberg.com",
            "cnbc.com",
            "forbes.com",
            "time.com",
            "newsweek.com",
            "theatlantic.com",
            "newyorker.com",
            "politico.com",
            " Axios",
            " Axios.com",
            " axios.com",
            "propublica.org",
            "mcclatchydc.com",
            "gannett.com",
            "hearst.com",
        ],
        "description": "Established news organizations with editorial standards"
    },
    "tech_research": {
        "domains": [
            # Tech companies with research
            "research.google",
            "ai.google",
            "blog.google",
            "microsoft.com",
            "research.microsoft.com",
            "openai.com",
            "anthropic.com",
            "deepmind.com",
            "ai.facebook.com",
            "research.fb.com",
            "amazon.science",
            "aws.amazon.com",
            "apple.com",
            "research.apple.com",
            "ibm.com",
            "research.ibm.com",
            "intel.com",
            "nvidia.com",
            "tesla.com",
            "spacex.com",
            "neuralink.com",
            "huggingface.co",
            "github.com",
            "stackoverflow.com",
            "stackexchange.com",
            "medium.com",
            "dev.to",
        ],
        "description": "Technology companies and research labs"
    },
    "encyclopedia": {
        "domains": [
            "wikipedia.org",
            "britannica.com",
            "worldcat.org",
            "encyclopedia.com",
            "stanford.edu",  # Stanford Encyclopedia of Philosophy
            "iep.utm.edu",
            "plato.stanford.edu",
        ],
        "description": "Encyclopedias and reference works (use with caution for citations)"
    },
    "fact_checking": {
        "domains": [
            "snopes.com",
            "factcheck.org",
            "politifact.com",
            "fullfact.org",
            "checkyourfact.com",
            "reuters.com/fact-check",
            "apnews.com/hub/ap-fact-check",
            "leadstories.com",
            "truthorfiction.com",
        ],
        "description": "Fact-checking organizations"
    },
    "data_statistics": {
        "domains": [
            "statista.com",
            "pewresearch.org",
            "gallup.com",
            "ourworldindata.org",
            "data.worldbank.org",
            " OECD.org",
            "oecd.org",
            "imf.org",
            "data.un.org",
            "ipums.org",
            "dhs.gov",
            "data.gov",
            "kaggle.com",
            " FiveThirtyEight",
            "fivethirtyeight.com",
        ],
        "description": "Data and statistics organizations"
    },
}


def load_authority_config() -> Dict[str, Any]:
    """Load authoritative sources configuration."""
    config_path = Path(__file__).parent.parent / "references" / "authoritative-sources.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    
    return DEFAULT_AUTHORITATIVE_SOURCES


def check_authority(url: str) -> Dict[str, Any]:
    """
    Check if a URL is from an authoritative source.
    
    Returns:
        dict with:
        - is_authoritative: bool
        - category: str (if authoritative)
        - reason: str (explanation)
        - confidence: str (high/medium/low)
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for matching
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Load authoritative sources
        sources = load_authority_config()
        
        # Check against each category
        for category, info in sources.items():
            for auth_domain in info.get("domains", []):
                # Handle suffix matching (e.g., .edu, .gov)
                if auth_domain.startswith('.'):
                    if domain.endswith(auth_domain) or f".{domain}".endswith(auth_domain):
                        return {
                            "is_authoritative": True,
                            "category": info["description"],
                            "category_key": category,
                            "reason": f"Recognized {info['description']}",
                            "confidence": "high"
                        }
                # Handle exact domain matching
                elif domain == auth_domain or domain.endswith(f".{auth_domain}"):
                    return {
                        "is_authoritative": True,
                        "category": info["description"],
                        "category_key": category,
                        "reason": f"Recognized {info['description']}",
                        "confidence": "high"
                    }
        
        # Not in authoritative list - check for warning signs
        warnings = check_warning_signs(domain)
        if warnings:
            return {
                "is_authoritative": False,
                "category": None,
                "reason": f"Warning signs: {', '.join(warnings)}",
                "confidence": "medium"
            }
        
        # Unknown source
        return {
            "is_authoritative": False,
            "category": None,
            "reason": "Not in recognized authoritative sources list. Verify credibility manually.",
            "confidence": "low"
        }
        
    except Exception as e:
        return {
            "is_authoritative": False,
            "category": None,
            "reason": f"Error checking authority: {str(e)}",
            "confidence": "low"
        }


def check_warning_signs(domain: str) -> list:
    """Check for domain warning signs."""
    warnings = []
    domain_lower = domain.lower()
    
    # Suspicious TLDs often used for spam
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.xyz', '.click', '.link']
    for tld in suspicious_tlds:
        if domain_lower.endswith(tld):
            warnings.append(f"suspicious TLD ({tld})")
            break
    
    # Very long domains
    if len(domain) > 50:
        warnings.append("unusually long domain")
    
    # Numbers and hyphens (common in spam)
    if re.search(r'\d{4,}', domain):
        warnings.append("excessive numbers in domain")
    
    # Check for common misleading terms
    misleading = ['truth', 'real', 'uncensored', 'exposed', 'secret', 'hidden', 'forbidden']
    for term in misleading:
        if term in domain_lower:
            warnings.append(f"potentially misleading term ('{term}')")
            break
    
    return warnings


def main():
    """CLI entry point for testing."""
    import sys
    import re
    
    if len(sys.argv) < 2:
        print("Usage: check_authority.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    result = check_authority(url)
    
    print(f"URL: {url}")
    print(f"Authoritative: {result['is_authoritative']}")
    if result['category']:
        print(f"Category: {result['category']}")
    print(f"Reason: {result['reason']}")
    print(f"Confidence: {result['confidence']}")


if __name__ == "__main__":
    main()
