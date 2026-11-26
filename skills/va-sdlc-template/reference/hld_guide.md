# HLD guide

An HLD records **how** the solution is shaped: the components, the boundaries
between them, and the decisions behind them. It is written only when the work
needs new or complex design; work that follows known patterns goes straight to
the plan, which names the pattern.

## Principles

- **New only**: Design what is new or complex; depth matches the risk. A known
  pattern the design relies on gets one line in `Known Patterns`, pointing to
  where it is documented.
- **Spans plans**: A choice belongs here when changing it would change more
  than one plan: modules, layers, boundaries, data flow. A choice that touches
  one plan belongs in that plan. Names stay at module and component level.
- **Decisions with rationale**: Each significant choice records the options
  considered, the one picked and the trade-off it accepts. Technical decisions
  live here; behaviour and domain decisions live in the story.
- **Traceable**: Every decision serves a DoD item, an AC or a constraint from
  the story.
- **Unknowns owned**: An unknown that blocks the design is resolved with the
  user or owned by a POC.

The HLD is ready for approval when every new piece in the overview is covered
by a decision or a known pattern, every constraint is served by a decision, and
every unknown is resolved or owned by a POC.

## Template

Optional sections: Contracts, Behaviour, Known Patterns. Omit them when empty.

```markdown
# HLD: [Title]

## Context
[Link to the story. What is new, and why it needs design.]

## Solution Overview
[Mermaid diagram of the modules or layers touched, new pieces marked; follow
`va-visualize`. A few lines on how they fit together.]

## Key Decisions
| ID | Decision | Options considered | Trade-off | Serves |
| --- | --- | --- | --- | --- |
| D-1 | [Choice] | [Alternatives] | [What it costs] | [DoD-1, AC-2, constraint] |

## Contracts
| Boundary | What crosses it | Shape | Failure cases |
| --- | --- | --- | --- |
| [Module ↔ module, app ↔ platform] | [Data, events, calls] | [Fields, in domain terms] | [Errors and how each surfaces] |

## Behaviour
[Flows, state and lifecycle of the new parts, including recovery; Mermaid
sequence or state diagram.]

## Known Patterns
- [Area]: follows [pattern]; see [doc or skill]

## Risks & Unknowns
- **R-1**: [Risk]; mitigation: [how]
- **U-1**: [Unknown]; resolved by: [user decision or POC]
```
