# Red-Team Critique Patterns

Reference guide for common argumentative vulnerabilities to probe during hostile assessment.

## Logical Fallacies

| Fallacy | Pattern | Example Probe |
|---------|---------|---------------|
| Circular reasoning | Conclusion assumed in premises | "How is the premise different from the conclusion?" |
| False dichotomy | Only two options presented | "What third alternatives exist?" |
| Hasty generalization | Small sample → broad claim | "What's the sample size and selection method?" |
| Post hoc | Correlation → causation | "What other variables could explain this?" |
| Straw man | Weak opponent constructed | "Is this the strongest version of the opposing view?" |
| Appeal to authority | Expert cited without evidence | "What evidence supports the authority's claim?" |
| Ad hominem | Attack on person, not argument | "Even if true about the person, does it refute the claim?" |
| Moving goalposts | Criteria shift when challenged | "What standard would actually falsify this claim?" |

## Hidden Assumption Categories

### Epistemological Assumptions
- The author can know X
- Source Y is reliable
- Method Z yields valid results
- Absence of evidence is evidence of absence

### Ontological Assumptions
- Categories used are natural/real
- Boundaries drawn are meaningful
- Trends will continue
- Entities discussed exist as described

### Value Assumptions
- What is measured is what matters
- Efficiency trumps other values
- Past patterns predict future
- Complexity can be reduced safely

### Rhetorical Assumptions
- Reader shares background knowledge
- Examples are representative
- Tone establishes credibility
- Length implies thoroughness

## Counter-Argument Generation

For any claim, generate counters along these dimensions:

1. **Neglected alternatives**: What other explanations fit the evidence?
2. **Selection bias**: What evidence would falsify this? Was it sought?
3. **Scope overreach**: Does the claim extend beyond what the evidence supports?
4. **Implementation barriers**: Even if true in theory, what prevents application?
5. **Temporal blindspots**: Does the argument fail at different time scales?
6. **Edge cases**: Does the argument collapse under extreme conditions?
7. **Reversal test**: If the opposite were argued with same evidence, would it seem valid?

## Severity Assessment Rubric

### Fatal Flaw Indicators
- Core thesis depends on the flawed premise
- Flaw appears in every key argument
- Undermines the author's credibility fundamentally
- Reveals dishonesty or deliberate distortion
- Invalidates stated conclusions even if premises hold

### Minor Quibble Indicators
- Limited to single subsection
- Doesn't affect downstream reasoning
- Acknowledged limitation the author accepts
- Stylistic rather than substantive
- Would be fixed by minor edit without structural change

## Hostile Reading Techniques

1. **Steel-man then destroy**: First strengthen the argument, then find its breaking point
2. **Devil's advocate**: What would a motivated opponent seize on?
3. **Inversion**: Assume the conclusion is false—does the evidence actually contradict this?
4. **Extremification**: Push claims to their logical extreme—do they become absurd?
5. **Missing data**: What evidence would settle this? Why wasn't it gathered?
6. **Comparative weakness**: Has a stronger version of this argument been made elsewhere?
