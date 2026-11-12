# Kickoff

Turn the epic into an approved spec and a set of tickets, then stop. Build on
whatever the workspace already holds, such as a spec from an interrupted kickoff.

- **Explore**
  - Understand the code the epic touches, starting from the user's context and
    widening only as needed. Done when you can say what exists and what the
    epic affects, without guessing.

- **Grill**
  - Run the `grilling` skill on the epic detail until the background, outcome
    and epic-level DoD are unambiguous. Unknowns that can't be resolved now stay
    as open unknowns: fog of war, so plan only as far as you can see.

- **Spec**
  - Write `spec.md` from [`spec_template.md`](spec_template.md). Done when a
    fresh session could pick any ticket and see why it exists. **Approval
    required.**

- **Split**
  - Propose the tickets as a table of title, type, blocked by and what it
    delivers. Each ticket is a tracer bullet that fits one session. A POC or
    research ticket stands in for each open unknown that blocks planning
    further. Done when every DoD item in the spec is covered by a ticket or an
    open unknown. Iterate with the user on granularity and blockers. **Approval
    required.**

- **Create**
  - Write the tickets from [`ticket_template.md`](ticket_template.md) and
    `state.json` with every ticket `todo`; ask the user for the epic branch if
    there is one. Start `progress.md`, with a first handoff only if kickoff left
    something the spec and tickets don't carry. Write the session retro in
    `kickoff/retro.md` with [`va-retro`](../../va-retro/SKILL.md), if the session
    had friction. Done when every ticket has its file and `state.json` lists
    them.
