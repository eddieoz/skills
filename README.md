# Writing Assistant Skills

A collection of Hermes Agent skills for reviewing, assessing, validating, and critiquing written content — articles, essays, blog posts, reports, and more.

## Skills Overview

| Skill | Purpose | Best For |
|-------|---------|----------|
| **[critique-content](writing-assistant/critique-content/)** | Hostile, red-team critical analysis | Exposing logic holes, unsupported assumptions, factual errors |
| **[document-reference-validator](writing-assistant/document-reference-validator/)** | Citation & reference verification | Validating Markdown links, footnotes, bibliographies |
| **[persuasive-analysis](writing-assistant/persuasive-analysis/)** | Rhetorical effectiveness (logos/ethos/pathos) | Marketing copy, speeches, op-eds, pitch decks |
| **[proof-read](writing-assistant/proof-read/)** | Mechanical + editorial polish | Final pass before publication; humanizing AI text |
| **[text-assessment](writing-assistant/text-assessment/)** | 5-dimension systematic evaluation | General-purpose review for clarity, logic, accuracy |

---

## Installing as a Hermes plugin

This repo is also a Hermes Agent **plugin pack**. The root now ships a `plugin.json` (Agent Plugins v1 manifest) and a `skills/` directory, so you can install the entire pack from the Hermes desktop "Install from Git" dialog or via:

```bash
hermes plugins install https://github.com/eddieoz/skills
```

Individual skills remain installable on their own from `skills/<name>` (or the legacy `writing-assistant/<name>` path).

## Quick Start

These skills live in the `writing-assistant/` subdirectory. To use them with Hermes Agent:

### Option 1: Copy into your profile's skills directory

```bash
# From your Hermes profile directory (e.g., ~/.hermes/profiles/cadmus/)
cp -r /path/to/skills/writing-assistant/* skills/
```

### Option 2: Symlink (keeps them synced)

```bash
ln -s /path/to/skills/writing-assistant/* ~/.hermes/profiles/cadmus/skills/
```

### Option 3: Reference directly in agent instructions

```yaml
# In your agent config or system prompt
skills:
  - writing-assistant/critique-content
  - writing-assistant/document-reference-validator
  - writing-assistant/persuasive-analysis
  - writing-assistant/proof-read
  - writing-assistant/text-assessment
```

Once installed, invoke them naturally in conversation:

> "Use the **critique-content** skill to red-team this essay."
> "Run **document-reference-validator** on my article.md with parallel mode."
> "Analyze this sales page with **persuasive-analysis**."
> "Give this a **proof-read** pass — it feels robotic."
> "Do a **text-assessment** on this draft before I send it."

---

## Skill Details

### critique-content
**Hostile critical assessment** — dispatches parallel sub-agents by section to identify logic holes, unsupported assumptions, and unaddressed counter-arguments. Outputs a red-team report distinguishing fatal flaws from minor quibbles.

- Uses sequential-thinking for planning and synthesis
- Requires internet research to validate factual claims
- Severity classification: **Fatal Flaw** (undermines core thesis) vs **Minor Quibble** (limited impact)

### document-reference-validator
**Citation verification** — extracts references from Markdown (inline links, footnotes, reference-style, autolinks, citation style), fetches source content, and verifies claims via semantic analysis.

- Parallel processing (`validate_parallel.py`) for speed on documents with 5+ references
- Authority checking against known reliable sources
- Citation-aware verification (title + author + publication ID matching)
- Outputs human-readable report + machine-readable JSON log

### persuasive-analysis
**Rhetorical diagnosis** — applies Aristotle's modes (logos, ethos, pathos) to evaluate how effectively a text achieves its influence goals.

- Structured framework: Goal → Mode Analysis → Structure → Devices → Assessment
- Identifies logical fallacies, credibility gaps, emotional manipulation
- Delivers prioritized recommendations ranked by impact

### proof-read
**Final polish** — three-pass system: Mechanical (accuracy) → Editorial (clarity) → Humanization (tone/flow).

- Specialized for removing AI-generated text markers
- Delivers edited text + change summary (word count, fixes by category)
- Red flags: word count increase, lost main point, sounds like different person

### text-assessment
**Systematic evaluation** — five dimensions: Clarity, Logic, Factual Accuracy, Communication, Completeness.

- Produces executive summary, dimension scores, prioritized improvements, quick wins
- Macro-before-micro: structure before commas
- Audience-aware: always considers who reads this and why

---

## Common Workflows

### Pre-Publication Pipeline
```text
Draft → text-assessment (structural) → critique-content (red-team) 
  → document-reference-validator (citations) → persuasive-analysis (if persuasive)
  → proof-read (final polish) → Publish
```

### Fact-Checking Focus
```text
document-reference-validator (parallel mode) → critique-content (factual claims)
```

### Polish Only
```text
proof-read → (optional) text-assessment for quick sanity check
```

### Persuasive Content
```text
persuasive-analysis → proof-read
```

---

## Requirements

- **Hermes Agent** with sub-agent delegation support (for `critique-content`)
- **Python 3.10+** (for `document-reference-validator` scripts)
- **sequential-thinking** MCP server (for `critique-content` planning/synthesis)
- **Internet access** (for fact-checking and reference fetching)

---

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for the full terms.

---

## Contributing

Skills are designed to be composable. When adding new skills:

1. Follow the SKILL.md frontmatter format (`name`, `description`, `license`)
2. Include clear "When to Use" / "Do NOT Use For" sections
3. Provide executable scripts where applicable
4. Document the output format
5. Add to this README's comparison table