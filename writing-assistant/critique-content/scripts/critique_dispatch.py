#!/usr/bin/env python3
"""
Critique dispatch helper for critique-content skill.
Manages parallel sub-agent dispatch for section-by-section hostile analysis.
"""

import sys
from typing import List, Dict, Any

def split_text_into_sections(text: str, max_sections: int = 8) -> List[str]:
    """
    Split text into logical sections for parallel critique.
    
    Strategy:
    1. Respect explicit section breaks (headers, dividers)
    2. If no breaks, split by paragraph clusters
    3. Balance section sizes for parallel efficiency
    """
    # Look for explicit section markers
    markers = ['\n## ', '\n# ', '\n---', '\n===', '\n\n\n\n']
    
    for marker in markers:
        if marker in text:
            raw_sections = [s.strip() for s in text.split(marker) if s.strip()]
            if len(raw_sections) > 1:
                return raw_sections[:max_sections]
    
    # No explicit markers - split by paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if len(paragraphs) <= max_sections:
        return paragraphs
    
    # Cluster paragraphs into balanced sections
    section_size = max(1, len(paragraphs) // max_sections)
    sections = []
    
    for i in range(0, len(paragraphs), section_size):
        cluster = paragraphs[i:i + section_size]
        sections.append('\n\n'.join(cluster))
    
    return sections[:max_sections]

def generate_subagent_prompt(section_text: str, section_num: int, total_sections: int) -> str:
    """Generate the hostile critique prompt for a sub-agent."""
    
    return f"""You are a Hostile Critic analyzing SECTION {section_num} of {total_sections}.

YOUR MANDATE: Expose weakness. Ignore politeness. Be surgically precise.

SECTION TEXT:
---
{section_text}
---

CRITIQUE MISSION:
1. **LOGICAL HOLES**: Identify fallacies, circular reasoning, non-sequiturs, or gaps
2. **UNSUPPORTED ASSUMPTIONS**: Flag every claim assumed without evidence
3. **MISSING COUNTER-ARGUMENTS**: What obvious objections did the author ignore?
4. **SEVERITY ASSESSMENT**: For each issue, label as FATAL or MINOR

FATAL = Undermines core thesis, invalidates conclusion, or reveals fundamental dishonesty
MINOR = Technical issue, overstatement, or stylistic weakness without structural impact

OUTPUT FORMAT (JSON-like structure for parsing):

```
SECTION: {section_num}/{total_sections}
FATAL_COUNT: [n]
MINOR_COUNT: [n]

FATAL FLAWS:
1. [Quote/location]: [Issue description]
   Impact: [How this damages the argument]
   Missing: [What should have been addressed]

MINOR QUIBBLES:
1. [Quote/location]: [Issue description]
   Impact: [Limited scope]

SECTION_ASSESSMENT: [COLLAPSED / DAMAGED / COMPROMISED / INTACT / CLEAR]
```

If you find NO issues, write:
"NO FLAWS DETECTED (suspicious—verify you haven't missed anything)"

Be ruthless. If the text seems airtight, you're not looking hard enough."""

def aggregate_critiques(section_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate individual section critiques into unified report structure.
    Called during synthesis phase.
    """
    fatal_flaws = []
    minor_quibbles = []
    section_assessments = []
    
    for result in section_results:
        section_num = result.get('section', 0)
        
        # Collect fatal flaws
        for flaw in result.get('fatal_flaws', []):
            fatal_flaws.append({
                'section': section_num,
                'location': flaw.get('location', 'Unknown'),
                'description': flaw.get('description', ''),
                'impact': flaw.get('impact', ''),
                'missing': flaw.get('missing', '')
            })
        
        # Collect minor quibbles
        for quibble in result.get('minor_quibbles', []):
            minor_quibbles.append({
                'section': section_num,
                'location': quibble.get('location', 'Unknown'),
                'description': quibble.get('description', ''),
                'impact': quibble.get('impact', '')
            })
        
        section_assessments.append({
            'section': section_num,
            'status': result.get('assessment', 'UNKNOWN')
        })
    
    return {
        'total_sections': len(section_results),
        'fatal_count': len(fatal_flaws),
        'minor_count': len(minor_quibbles),
        'fatal_flaws': fatal_flaws,
        'minor_quibbles': minor_quibbles,
        'section_statuses': section_assessments
    }

def print_dispatch_plan(text: str, max_sections: int = 8):
    """Print the dispatch plan for the user."""
    sections = split_text_into_sections(text, max_sections)
    
    print(f"CRITIQUE DISPATCH PLAN")
    print(f"=" * 50)
    print(f"Total text length: {len(text)} characters")
    print(f"Sections to analyze: {len(sections)}")
    print(f"Parallel sub-agents: {len(sections)}")
    print()
    
    for i, section in enumerate(sections, 1):
        char_count = len(section)
        preview = section[:100].replace('\n', ' ')
        print(f"Section {i}: {char_count} chars | Preview: {preview}...")
    
    return sections

if __name__ == "__main__":
    # Read text from stdin or file
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    
    if not text.strip():
        print("Error: No text provided", file=sys.stderr)
        sys.exit(1)
    
    sections = print_dispatch_plan(text)
    
    # Output section count for scripting
    print(f"\nTOTAL_SECTIONS: {len(sections)}")