# Authoritative Sources Reference

This file documents known authoritative and reliable sources for reference validation.

## Categories

### Academic & Research
**Trust Level: High**

| Domain | Type |
|--------|------|
| *.edu | US Universities |
| *.ac.uk | UK Universities |
| *.ac.jp | Japanese Universities |
| *.ac.au, *.ac.nz | Australian/NZ Universities |
| arxiv.org | Preprint server |
| doi.org | DOI resolver |
| pubmed.ncbi.nlm.nih.gov | Medical literature |
| nature.com, science.org | Top-tier journals |
| ieee.org, acm.org | Professional societies |
| springer.com, wiley.com | Academic publishers |

**Usage Notes:**
- Prefer peer-reviewed sources over preprints
- Check publication date for recency
- Verify journal is not predatory

### Government & Official
**Trust Level: High**

| Domain | Type |
|--------|------|
| *.gov | US Government |
| *.gov.uk | UK Government |
| *.gov.au | Australian Government |
| europa.eu | European Union |
| un.org | United Nations |
| who.int | World Health Organization |
| worldbank.org | World Bank |
| imf.org | International Monetary Fund |
| cdc.gov, fda.gov, nih.gov | US Health agencies |
| epa.gov, noaa.gov, usgs.gov | US Science agencies |

**Usage Notes:**
- Official government positions may have political bias
- Check publication date for policy changes
- Some agencies have specific domain patterns

### Established News
**Trust Level: Medium-High**

| Domain | Type |
|--------|------|
| reuters.com, apnews.com | Wire services |
| bbc.com, nytimes.com, wsj.com | Major outlets |
| economist.com, ft.com | Financial news |
| npr.org, pbs.org | Public broadcasting |
| cnn.com, foxnews.com | Cable news (note bias) |

**Usage Notes:**
- All news has some editorial perspective
- Prefer original reporting over opinion pieces
- Check date for breaking vs. developing stories
- Verify story has been updated/corrected if needed

### Technology & Research Companies
**Trust Level: Medium-High**

| Domain | Type |
|--------|------|
| research.google, ai.google | Google Research |
| openai.com, anthropic.com | AI labs |
| research.microsoft.com | Microsoft Research |
| deepmind.com | DeepMind |
| github.com | Code repositories |
| huggingface.co | ML community |

**Usage Notes:**
- Company research may promote their products
- Check for peer review of claims
- Blog posts vs. research papers have different rigor

### Fact-Checking
**Trust Level: High**

| Domain | Focus |
|--------|-------|
| snopes.com | General fact-checking |
| factcheck.org | Political claims |
| politifact.com | Political fact-checking |
| fullfact.org | UK fact-checking |
| reuters.com/fact-check | News fact-checking |
| apnews.com/hub/ap-fact-check | AP fact-checking |

### Data & Statistics
**Trust Level: High**

| Domain | Focus |
|--------|-------|
| statista.com | Market data |
| pewresearch.org | Social trends |
| ourworldindata.org | Global development |
| data.worldbank.org | Economic indicators |
| oecd.org | Economic data |
| census.gov | US demographic data |

### Encyclopedias
**Trust Level: Medium**

| Domain | Notes |
|--------|-------|
| wikipedia.org | Good starting point, verify citations |
| britannica.com | Traditional encyclopedia |
| plato.stanford.edu | Philosophy (peer-reviewed) |
| iep.utm.edu | Internet Encyclopedia of Philosophy |

**Usage Notes:**
- Wikipedia is good for overview, not primary citation
- Always check original sources in encyclopedia entries
- Some specialized encyclopedias have peer review

## Warning Signs (Low Trust)

**Suspicious TLDs:**
- .tk, .ml, .ga, .cf, .gq (often free, abused)
- .top, .click, .link (often spam)

**Domain Red Flags:**
- Excessive numbers in domain
- Very long domain names
- Terms like "truth", "real", "exposed", "uncensored"
- Mimics legitimate sites with typos

**Content Red Flags:**
- No author attribution
- No publication date
- No sources cited
- Extreme clickbait headlines
- Aggressive advertising
- No "About" page or contact info

## Adding Sources

To add new authoritative sources:

1. Edit `scripts/check_authority.py` and add domains to `DEFAULT_AUTHORITATIVE_SOURCES`
2. Or create `references/authoritative-sources.json` with custom sources:

```json
{
  "my_category": {
    "domains": ["example.com", "sub.example.org"],
    "description": "Description of source type"
  }
}
```

## Source Verification Tips

When a source is not in this list:

1. **Check About page** - Who runs the site? What's their mission?
2. **Look for editorial standards** - Do they have a corrections policy?
3. **Search for reviews** - What do others say about this source?
4. **Check Media Bias/Fact Check** - mbfcnews.com has source ratings
5. **Verify expertise** - Are authors qualified in the subject area?
6. **Cross-reference** - Can the claim be found in other reliable sources?

## Confidence Levels

- **High**: Established institution with editorial standards
- **Medium**: Generally reliable but check specifics
- **Low**: Unknown source, verify carefully or find alternative
