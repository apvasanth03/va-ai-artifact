# PR comments

Address the review comments on the epic's one PR, round by round. Follow
[`va-pr-address-comments`](../../va-pr-address-comments/SKILL.md) with these
inputs and additions.

- **Inputs**
  - Workspace: `<workspace>/pr_comments/`.
  - Context: `story.md` and `hld.md`. When a comment's claim needs more, find
    the work that changed the commented code: `git log` on the file, matched
    against the `result` commits in `state.json`, names the ticket or issue
    group. Read its plan or issue file.

- **Work beyond the round**
  - A comment that needs more than a round fix becomes an issue group (a bug)
    or a story change and a ticket (a new requirement), proposed on its card.
    A fix that changes an HLD contract or story behaviour proposes that update.
    All per the approval principle.
  - After the card is approved, and before the posting gate, write the item:
    an issue group per the Triage step of [`issue_steps.md`](issue_steps.md),
    or a ticket from [`ticket_template.md`](ticket_template.md), each added to
    `state.json`. Record the thread URL in the item.
  - The reply says it in words the reviewer can read, since workspace ids are
    local: "Valid; it will be fixed in a later commit on this PR." The PR skill
    won't walk that thread again (it waits on the reviewer), so the reply on
    the fix is the user's, per the PR threads principle.

- **Session end**
  - Update `progress.md` per the Progress principle, including where an
    unfinished round stands (e.g. "PR round 2 at the walk"), and write the
    session retro.
