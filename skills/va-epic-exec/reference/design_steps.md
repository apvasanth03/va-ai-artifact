# Design

Turn the approved story into an approved HLD (**how**) and a set of tickets,
then stop.

- **Orient**
  - Set `design` `in_progress`. Read `story.md` and all of `progress.md`; on a
    resume, `progress.md` says which approval is pending.

- **Explore**
  - Understand the code the epic touches, starting from the story and widening
    only as needed. Done when you can say what exists, what changes and what it
    affects, without guessing.

- **HLD**
  - Ask the user if they have a design before drafting one. If so, validate it
    against the story and what you explored, and run the `grilling` skill on
    the gaps; update it in place if it is in the workspace, otherwise write it
    to `hld.md`. If not, draft `hld.md` using the `va-sdlc-template` skill
    (HLD), with its Context linking to `story.md`.
  - Fog of war: design only as far as you can see. Each technical unknown in
    Risks & Unknowns is owned by the user or by a POC ticket.
  - **Approval required.**

- **Split**
  - Propose the tickets as a table of title, type, blocked by, what it
    delivers and what it serves (story ACs or HLD contracts). Each ticket:
    - fits one session;
    - is verifiable on its own, against its HLD contract or a story AC;
    - names its blockers.
  - Default to component by component, in dependency order, following the
    HLD; slice vertically when the user asks or the epic suits it. Each story
    AC is served by the ticket that completes it. A POC ticket stands in for
    each unknown that blocks planning further, and the tickets that depend on
    its finding list it in `Blocked by`.
  - Done when every story AC is served by a ticket and every blocking unknown
    has a POC ticket. Iterate with the user on granularity and blockers.
    **Approval required.**

- **Create**
  - Write the tickets from [`ticket_template.md`](ticket_template.md) and add
    them to `state.json`, every ticket `todo`; ask the user for the epic branch
    if there is one. Set `design` `done`, update `progress.md` and write the
    session retro. Done when every ticket has its file and `state.json` lists
    them.
