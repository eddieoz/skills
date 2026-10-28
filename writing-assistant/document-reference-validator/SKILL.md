---
name: document-reference-validator
description: Validates document references by checking if linked content supports the claims being made. Supports parallel processing for faster validation of multiple references. Use when user wants to verify citations, validate source reliability, fact-check document references, validate document links in Markdown, or process multiple references in parallel for speed.
---

# Document Reference Validator

Validate Markdown document references by extracting citations, fetching source content, and verifying claims through semantic analysis. Supports parallel processing for faster validation of documents with many references.

## Quick Start

```bash
# Validate all references (sequential - good for few references)
python scripts/validate_document.py <path/to/document.md>

# Validate with parallel processing (faster for many references)
python scripts/validate_parallel.py <path/to/document.md> --max-workers 10

# Validate with custom output directory
python scripts/validate_parallel.py <path/to/document.md> --output ./validation-reports
```

## Workflow

1. **Extract references** from Markdown (inline links, footnotes, citations)
2. **Identify claims** from surrounding context (sentences/paragraphs before reference)
3. **Fetch source content** (CLI first, fallback to browser automation)
4. **Verify claims** via semantic analysis
5. **Check source authority** against known reliable sources
6. **Generate report** with flags and alternative suggestions
7. **Log all issues** for human review

## Reference Formats Supported

- **Inline links**: `[text](url)` and `[text](url "title")`
- **Reference-style**: `[text][id]` with `[id]: url` elsewhere in document
- **Footnotes**: `[^1]` with `[^1]: url` or `[^1]: description url`
- **Autolinks**: `<http://example.com>`
- **Markdown citation style**: `[@source]` with bibliography section

## Scripts

### Parallel Validation (Recommended)

`scripts/validate_parallel.py` - Orchestrates full validation workflow with parallel processing for speed.

**Usage:**
```bash
python scripts/validate_parallel.py <document.md> [options]

Options:
  --output DIR          Output directory for reports (default: ./validation-output)
  --max-workers N       Number of parallel workers (default: 5)
  --timeout SECONDS     Request timeout per reference (default: 30)
  --use-browser         Force browser automation for all links
  --check-authority     Validate source authority/reliability
  --semantic-threshold  Match threshold 0-1 (default: 0.6)
```

**When to use parallel mode:**
- Documents with 5+ references
- Time-sensitive validation tasks
- Independent network requests (no shared state)

**Output files:**
- `validation-report.md` - Human-readable report with timing stats
- `validation-log.json` - Machine-readable log with parallel config
- `failed-fetches.log` - URLs that couldn't be accessed

### Sequential Validation

`scripts/validate_document.py` - Original sequential validation (good for few references or debugging).

### Supporting Scripts

- `scripts/extract_references.py` - Extract all reference URLs from Markdown
- `scripts/fetch_content.py` - Fetch content via CLI (curl) with browser fallback
- `scripts/verify_claim.py` - Semantic analysis to verify claim against content
- `scripts/check_authority.py` - Check domain against authoritative sources list

## Validation Report Format

The report includes:

| Status | Meaning |
|--------|---------|
| ✅ Verified | Source content supports claim |
| ⚠️ Partial | Source partially supports claim |
| ❌ Mismatch | Source contradicts or doesn't support claim |
| 🔍 Failed | Could not fetch source content |
| 🚫 Unreliable | Source is not authoritative/reliable |
| 💥 Error | Processing error occurred |

Each entry includes:
- Original claim text
- Reference URL
- Verification status
- Confidence score
- Processing time (parallel mode)
- Alternative sources (if mismatch)
- Flag for human review indicator

**Parallel reports additionally include:**
- Number of workers used
- Total processing time
- Average time per reference

## Authority Checking

See [references/authoritative-sources.md](references/authoritative-sources.md) for the list of known reliable sources by category:
- Academic journals and institutions
- Government sources
- Major news organizations
- Research databases
- Fact-checking organizations

Add domains to this file as you encounter reliable sources.

## Handling Failures

When a link fails (timeout, captcha, 404, etc.):

1. Log to `failed-fetches.log`
2. Flag for human review in report
3. Suggest searching for the claim with search engines
4. Continue with remaining references

Use Chrome DevTools MCP for difficult sites:
```python
# Browser automation via Chrome DevTools MCP
navigate_page(type="url", url="<problematic-url>")
take_snapshot()  # Get page content
```

## Semantic Analysis

The verification uses multiple strategies optimized for academic citations:

### Citation-Aware Verification

For citation-style claims (common in academic documents):
1. **Quoted Title Matching** (highest priority) - Extracts titles in quotes and checks presence in source
2. **Author Name Matching** - Verifies author appears in source
3. **Publication ID Matching** - arXiv, DOI, PMID identifiers
4. **Entity Overlap** - Named entities comparison
5. **Key Phrase Matching** - Important phrase overlap

### Thresholds (configurable via `--semantic-threshold`)

**Default threshold: 0.35** (optimized for citation-style documents)

- **Verified (≥0.7)**: Strong match (title + author or high semantic overlap)
- **Partial (≥0.35)**: Moderate match (title found but limited content)
- **Mismatch (<0.35)**: Weak match (use `--semantic-threshold 0.5` for stricter checks)

### Boost Factors

- Title + Author combination: +30% confidence boost
- Publication ID match: +50% confidence
- Authoritative source: Validated separately

### Anti-Scraping Detection

Content < 200 characters is flagged as "failed" (not "mismatch") since it likely indicates:
- Cloudflare/anti-bot protection
- JavaScript-required sites
- Paywalls
- Rate limiting

## Log File Format

`validation-log.json` structure:
```json
{
  "document": "path/to/doc.md",
  "timestamp": "2026-03-12T10:00:00Z",
  "total_references": 10,
  "verified": 5,
  "partial": 2,
  "mismatch": 1,
  "failed": 2,
  "entries": [
    {
      "claim": "AI improves productivity by 40%",
      "url": "https://example.com/study",
      "status": "verified",
      "confidence": 0.85,
      "requires_review": false,
      "alternatives": []
    }
  ]
}
```
