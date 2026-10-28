# AGENTS.md — Writing Assistant Skills

Instructions for AI agents to install, configure, and use the writing-assistant skills programmatically.

## Repository Structure

```
# Repo root is now also a Hermes Agent plugin pack:
#   plugin.json   (Agent Plugins v1 manifest)
#   SKILL.md      (meta-skill index)
#   skills/       (symlinks to writing-assistant/*)

writing-assistant/
    ├── critique-content/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   └── critique_dispatch.py
    │   └── references/
    │       └── red-team-patterns.md
    ├── document-reference-validator/
    │   ├── SKILL.md
    │   ├── scripts/
    │   │   ├── __init__.py
    │   │   ├── check_authority.py
    │   │   ├── extract_references.py
    │   │   ├── fetch_content.py
    │   │   ├── validate_document.py
    │   │   ├── validate_parallel.py
    │   │   └── verify_claim.py
    │   └── references/
    │       └── authoritative-sources.md
    ├── persuasive-analysis/
    │   └── SKILL.md
    ├── proof-read/
    │   └── SKILL.md
    └── text-assessment/
        └── SKILL.md
```

## Installation

### Via Hermes Plugin Install (pack)

The repository root is a valid Hermes Agent plugin pack. Install the whole collection at once:

```bash
hermes plugins install https://github.com/eddieoz/skills
```

or paste `https://github.com/eddieoz/skills` into the desktop "Install from Git" dialog. Individual skills remain available under `skills/<name>` (and the legacy `writing-assistant/<name>` path).

### Via Claude Code (pack)

The repository ships a Claude Code plugin manifest at `.claude-plugin/plugin.json` (and `claude-plugin.json` at the root). Install the whole collection with:

```bash
claude plugin install https://github.com/eddieoz/skills
```

Skills under `skills/` are discovered automatically. Individual skills remain available under `skills/<name>`.

### Via Hermes Agent Config

Add to your profile's `config.yaml`:

```yaml
skills:
  - name: critique-content
    source: file:///absolute/path/to/skills/writing-assistant/critique-content
  - name: document-reference-validator
    source: file:///absolute/path/to/skills/writing-assistant/document-reference-validator
  - name: persuasive-analysis
    source: file:///absolute/path/to/skills/writing-assistant/persuasive-analysis
  - name: proof-read
    source: file:///absolute/path/to/skills/writing-assistant/proof-read
  - name: text-assessment
    source: file:///absolute/path/to/skills/writing-assistant/text-assessment
```

### Via Symlink (Recommended for Development)

```bash
# From your Hermes profile directory
PROFILE_SKILLS=~/.hermes/profiles/cadmus/skills
mkdir -p "$PROFILE_SKILLS"
for skill in critique-content document-reference-validator persuasive-analysis proof-read text-assessment; do
  ln -sfn /absolute/path/to/skills/writing-assistant/$skill "$PROFILE_SKILLS/$skill"
done
```

### Verification

After installation, verify skills are loadable:

```bash
# In Hermes session
skill_view(name="critique-content")
skill_view(name="document-reference-validator")
skill_view(name="persuasive-analysis")
skill_view(name="proof-read")
skill_view(name="text-assessment")
```

Each should return the skill's full SKILL.md content.

## Runtime Dependencies

| Skill | Requires |
|-------|----------|
| critique-content | `sequential-thinking` MCP server, sub-agent delegation (`delegate_task`), web search |
| document-reference-validator | Python 3.10+, `requests`, `beautifulsoup4`, `lxml` (see `scripts/requirements.txt` if present) |
| persuasive-analysis | None (pure reasoning) |
| proof-read | None (pure reasoning) |
| text-assessment | None (pure reasoning) |

Install Python deps for document-reference-validator:

```bash
cd /path/to/skills/writing-assistant/document-reference-validator/scripts
pip install -r requirements.txt  # if exists, else:
pip install requests beautifulsoup4 lxml
```

## Agent Usage Patterns

### 1. critique-content — Hostile Red-Team Analysis

**Trigger phrases:** "critique this", "red-team", "hostile review", "find flaws", "tear this apart"

**Agent workflow:**
```python
# 1. Load skill
skill_view(name="critique-content")

# 2. Plan with sequential-thinking (MCP)
#    - Analyze text structure
#    - Determine sectioning strategy
#    - Plan critique dimensions per section
#    - Define fact-checking targets

# 3. Dispatch parallel sub-agents via delegate_task
#    One sub-agent per section with the Hostile Critic prompt

# 4. Synthesize with sequential-thinking
#    - Aggregate findings
#    - Identify cross-cutting patterns
#    - Assess structural integrity

# 5. Deliver red-team report format
```

**Key constraint:** Do NOT be polite. Be precise. Fact-check via web search.

### 2. document-reference-validator — Citation Verification

**Trigger phrases:** "validate references", "check citations", "verify sources", "fact-check links"

**Agent workflow:**
```python
# 1. Load skill
skill_view(name="document-reference-validator")

# 2. Choose mode:
#    - Few refs (<5): python scripts/validate_document.py doc.md
#    - Many refs (5+): python scripts/validate_parallel.py doc.md --max-workers 10

# 3. Parse output:
#    - validation-report.md (human-readable)
#    - validation-log.json (machine-readable)
#    - failed-fetches.log (problematic URLs)

# 4. Report statuses: ✅ Verified, ⚠️ Partial, ❌ Mismatch, 🔍 Failed, 🚫 Unreliable, 💥 Error
```

**Key flags:**
- `--check-authority` — validate source reliability
- `--semantic-threshold 0.5` — stricter matching (default 0.35)
- `--use-browser` — force browser automation for JS-heavy sites

### 3. persuasive-analysis — Rhetorical Diagnosis

**Trigger phrases:** "analyze persuasion", "rhetorical analysis", "why isn't this convincing", "logos ethos pathos"

**Agent workflow:**
```python
# 1. Load skill
skill_view(name="persuasive-analysis")

# 2. Identify: Goal + Audience + Context

# 3. Analyze three modes:
#    Logos: claim clarity, evidence quality, reasoning validity, counter-args addressed
#    Ethos: credentials, transparency, fairness, consistency, tone
#    Pathos: emotional hooks, values alignment, vivid language, empathy, ethics

# 4. Evaluate structure: opening, flow, pacing, closing

# 5. Deliver: Rating + Mode breakdown + Top 3 strengths/weaknesses + Prioritized recommendations
```

**Do NOT use for:** Pure info text (use text-assessment), creative writing, fact-checking.

### 4. proof-read — Final Polish

**Trigger phrases:** "proofread", "polish", "humanize", "fix AI tone", "final pass"

**Agent workflow:**
```python
# 1. Load skill
skill_view(name="proof-read")

# 2. Three-pass system:
#    Pass 1 - Mechanical: spelling, grammar, punctuation, facts, consistency
#    Pass 2 - Editorial: wordiness, repetition, complex sentences, weak openings, jargon, passive voice
#    Pass 3 - Humanization: remove AI markers (hedging, generic intensifiers, abstract opens, etc.)

# 3. Deliver:
#    - Edited text (ready to use)
#    - Summary: word count delta, mechanical fixes, editorial changes, humanization fixes, flow improvements
```

**Red flags to stop on:** word count increased, main point lost, sounds like different person, can't read aloud smoothly.

### 5. text-assessment — Systematic Evaluation

**Trigger phrases:** "assess this", "review draft", "evaluate writing", "feedback on this text"

**Agent workflow:**
```python
# 1. Load skill
skill_view(name="text-assessment")

# 2. Read for understanding (identify core message)

# 3. Evaluate 5 dimensions:
#    Clarity, Logic, Factual Accuracy, Communication, Completeness

# 4. Identify priority issues (macro before micro)

# 5. Deliver report:
#    - Executive summary + single most important improvement
#    - Dimension scores (Excellent/Good/Fair/Poor + justification)
#    - Priority improvements (3-5, ranked High/Medium/Low with "because")
#    - Quick wins (2-3 immediate low-effort fixes)
```

**Do NOT use for:** Proofreading only, specialized domain review, style guide enforcement.

## Composite Workflows (Agent-Orchestrated)

### Pre-Publication Pipeline
```python
# For articles, essays, blog posts before publish
async def pre_publication_review(document_path: str):
    # 1. Structural + completeness check
    assessment = await run_skill("text-assessment", document_path)
    if assessment.overall in ["needs work", "major revision"]:
        return assessment  # Stop early
    
    # 2. Red-team critique
    critique = await run_skill("critique-content", document_path)
    if critique.fatal_flaws > 0:
        return critique  # Stop early
    
    # 3. Citation validation (if references present)
    if has_references(document_path):
        validation = await run_skill("document-reference-validator", document_path, parallel=True)
        if validation.mismatch_or_failed > 0:
            return validation
    
    # 4. Persuasive check (if persuasive intent)
    if is_persuasive(document_path):
        persuasive = await run_skill("persuasive-analysis", document_path)
        if persuasive.rating in ["Weakly Persuasive", "Not Persuasive"]:
            return persuasive
    
    # 5. Final polish
    return await run_skill("proof-read", document_path)
```

### Fact-Check Heavy
```python
# For research-heavy content
async def fact_check_pipeline(document_path: str):
    validation = await run_skill("document-reference-validator", document_path, 
                                  parallel=True, check_authority=True)
    critique = await run_skill("critique-content", document_path)  # focuses on factual claims
    return {"validation": validation, "critique": critique}
```

### Polish Only
```python
# For near-final drafts
async def polish_only(document_path: str):
    assessment = await run_skill("text-assessment", document_path, quick=True)
    if assessment.quick_wins:
        return await run_skill("proof-read", document_path)
    return assessment
```

## Skill Invocation Reference

| Skill | Primary Entry Point | Output Format |
|-------|---------------------|---------------|
| critique-content | Sequential-thinking + delegate_task | Red-team report (markdown) |
| document-reference-validator | `python scripts/validate_parallel.py` | `validation-report.md`, `validation-log.json` |
| persuasive-analysis | Reasoning + structured analysis | Rating + mode breakdown + recommendations |
| proof-read | Three-pass editing | Edited text + change summary |
| text-assessment | 5-dimension evaluation | Executive summary + scores + prioritized fixes |

## Error Handling

| Failure Mode | Recovery |
|--------------|----------|
| critique-content sub-agent timeout | Reduce section count; increase timeout |
| document-reference-validator fetch failures | Check `failed-fetches.log`; retry with `--use-browser` |
| sequential-thinking unavailable | Fall back to single-pass analysis (note in output) |
| Python script import errors | Verify venv + dependencies in `scripts/` |

## Testing Checklist

After installation, verify each skill:

- [ ] `skill_view(name="critique-content")` returns content
- [ ] `skill_view(name="document-reference-validator")` returns content
- [ ] `python scripts/validate_parallel.py --help` works
- [ ] `skill_view(name="persuasive-analysis")` returns content
- [ ] `skill_view(name="proof-read")` returns content
- [ ] `skill_view(name="text-assessment")` returns content

## Versioning

Skills are versioned by their directory timestamp. No semantic versioning — pull latest from source to update.

## Support

Issues: Check individual skill `SKILL.md` for "Common Mistakes" and "Red Flags" sections.
For Hermes integration issues, consult Hermes Agent documentation.