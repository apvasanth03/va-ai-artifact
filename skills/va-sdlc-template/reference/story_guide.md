# Story guide

A story states **what** to deliver and **why**, from the user's view.

## Principles

- **What, not how**: Describe behaviour, outcomes and deliverables in the
  user's terms, so a PM can read every line. Components, files, APIs and
  libraries belong in `hld.md`.
- **User's voice**: Write for the person who benefits. For technical work
  (refactor, infra, tooling), the user is the consumer of the change: a
  developer, another team, CI.
- **Constraints are requirements**: Record the need ("list loads in < 1s");
  the mechanism that meets it goes in `hld.md`.
- **Bounded**: `Out of Scope` names the near-misses a reader would otherwise
  assume are in.
- **Surface unknowns**: List assumptions and open questions, and resolve each
  open question with the user before approval.
- **INVEST**: The story meets INVEST; if it is not Small, propose a split to
  the user.

## Acceptance criteria

Every behaviour, including edge cases the user can hit (e.g. empty, error,
offline, no permission), lives in the ACs. Each AC is pass/fail, verified by
using the feature, running a test, or reading a metric.

| Form | Use for | Shape |
| --- | --- | --- |
| Scenario (Gherkin) | Behaviour | Given [context], when [action], then [outcome] |
| Rule | Deliverable exists, metric, compliance | Plain observable statement |

The story is ready for approval when every deliverable is covered by at least
one AC and every open question is resolved.

## Template

Optional sections: User Flow, Constraints, Assumptions & Open Questions,
References. Omit them when empty.

```markdown
# Story: [Title]

## Problem
[Who is affected, current pain, why now.]

## User Story
As a [user or consumer], I want [capability], so that [outcome].

## Deliverables
- [What exists or changes when done]

## Out of Scope
- [Non-goals]

## User Flow
[Mermaid diagram of a multi-step journey; follow `va-visualize`.]

## Constraints
- [Non-functional need: performance, platforms, accessibility, analytics]

## Acceptance Criteria (DoD)
- [ ] **AC-1**: Given [context], when [action], then [outcome]
- [ ] **AC-2**: [Observable rule]

## Assumptions & Open Questions
- **A-1**: [Assumption]
- **Q-1**: [Question]

## References
- [PRD, ticket, design, POC]
```
