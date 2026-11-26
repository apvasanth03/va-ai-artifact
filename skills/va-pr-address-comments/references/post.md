# Phase 6 Post

**Goal**: every approved reply is on its thread, and the user has the round's
outcome.

## Posting gate

The replies were approved card by card, so the gate asks with counts:

```markdown
Post <n> replies on PR #<n> (fix <n> · skip <n> · clarify <n>) · {sha} → `<sha7>`
Deviations: #5 reply updated — only if any
Approve?
```

Drop the `{sha}` part when the round has no `fix`. Show a deviation's text on
request.

On the yes:

```bash
python scripts/post_replies.py <workspace>            # --dry-run first if unsure
```

It refuses when the round commit isn't on origin, fills `{sha}`, appends the
marker and writes each `reply_id` back as it goes. A re-run after a partial
failure skips what is posted and adopts a reply already on GitHub, so it needs
no new approval.

## Round summary

```markdown
**Round <N> done** · PR #<n> · `<sha7>`
fix <n> · skip <n> · clarify <n> · posted <n>/<n>
Waiting on reviewer: <n> (incl. <n> clarify) — next round picks up their replies
```

- No `fix`: no `<sha7>`.
- `posted` below the total: the header reads **Round <N> incomplete** and lists
  the failed threads.

Reply URLs stay in `final_replies.json`; share them on request.

**Done when**: `round.py status` shows `done`, and the summary is shown.
