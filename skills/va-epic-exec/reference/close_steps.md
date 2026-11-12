# Close

Judge the finished epic against its spec. Report first; changes wait for the user.

- **Review**
  - Review the epic's changes (the epic branch, or the `result` commits in
    `state.json`) against `spec.md`. Mark each DoD item met, with evidence (how
    it was verified, where it lives), or unmet.

- **Report**
  - Report the result to the user. Done when every DoD item is marked, with
    evidence.

- **Follow up**
  - Propose tickets for the unmet items.

- **Retro**
  - Write the epic's final `retro.md` with [`va-retro`](../../va-retro/SKILL.md),
    from every session retro (`kickoff/` and `tickets/*/`) plus this session's
    own friction. The same friction across sessions is one finding that ranks
    higher. Propose each fix not yet `applied`. Done when every finding in a
    session retro is merged into a finding, listed under Minor, or marked
    `applied`.
