# Close

Judge the finished epic against its story and HLD. Report first; changes wait
for the user.

- **Review**
  - Set `close` `in_progress`. If `pr_comments/` exists, check with the PR
    skill's `round.py status` that its last round is done; if not, ask the
    user whether to finish it first or close anyway. Review the epic's changes
    (the epic branch, or the `result` commits of tickets and issue groups in
    `state.json`) against `story.md`. Mark each AC met, with evidence (how it
    was verified, where it lives), or unmet.

- **HLD check**
  - Compare the delivered code with `hld.md`'s Key Decisions and, when
    present, Contracts. For each mismatch, propose an `hld.md` update or a
    follow-up ticket; the user picks.

- **Report**
  - Report the result to the user. Done when every AC is marked, with evidence,
    and every HLD mismatch is listed.

- **Follow up**
  - Propose tickets for the unmet ACs and HLD mismatches the user sent to a
    ticket. If the user approves any, add them, set `close` back to `todo`
    and stop: the epic returns to the ticket stage, and the final retro waits
    for the last close.

- **Retro**
  - Write the epic's final `retro.md` with [`va-retro`](../../va-retro/SKILL.md),
    from every session retro (`kickoff/`, `design/`, `tickets/*/`, `issues/`
    and `pr_comments/`) plus this session's own friction. The same friction
    across sessions is one finding that ranks higher. Propose each fix not yet
    `applied`. Done when every finding in a session retro is merged into a
    finding, listed under Minor, or marked `applied`. Then set `close` `done`.
