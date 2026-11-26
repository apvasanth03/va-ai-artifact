# Kickoff

Turn the epic detail into an approved story: **what** to deliver and **why**,
then stop. The how belongs to the design stage, in a fresh session.

- **Start**
  - On a new epic, write `state.json` with `kickoff` `in_progress`, `design`
    and `close` `todo`, and empty `tickets` and `issues`, and start
    `progress.md` with its three headings. On a resume, build on what the
    workspace holds, such as a draft `story.md`.

- **Explore**
  - Read the user's context (docs, tickets, designs), and the code only where
    it leaves a gap about today's behaviour. Done when you can say, in user
    terms, what users see today and what the epic changes.

- **Grill**
  - Run the `grilling` skill on the epic detail until the problem,
    deliverables, acceptance criteria (ACs), out of scope and behaviour
    decisions are unambiguous. Technical questions wait for design.

- **Story**
  - Write `story.md` using the `va-sdlc-template` skill (story), with these
    epic changes:
    - INVEST's *Small* does not apply: an epic story is large, and design
      splits it into tickets.
    - Add a `Decisions` section after `Out of Scope`: each behaviour or domain
      choice, with its reason.
  - Done when every deliverable has an AC and every open question is resolved.
    **Approval required.**

- **Wrap up**
  - Set `kickoff` `done`, and add a line to `progress.md` only if kickoff left
    something the story doesn't carry. Write the session retro.
