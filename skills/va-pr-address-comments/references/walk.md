# Phase 2 Group · Phase 3 Walk

**Goal**: every thread in the round has an approved decision and reply in
`final_replies.json`, and every `fix` has its section in `plan.md`.

Read each thread from `rounds/N/comments.json`. `comment_queue.md` is the
user's view and the walk's progress.

## Group

Threads share a group when one root cause and one answer cover them (round
after round, bots repeat one complaint across many files). Same file alone is
not a reason. Write the group ids (`G1`, `G2`, …) into the queue's `Group`
column, then propose in chat:

```markdown
## Groups · round <N> · full list: `rounds/<N>/comment_queue.md`

| Group | Threads | Shared root cause |
|---|---|---|
| G1 | #1–9, #14 | <root cause> |

Singles: #10 · #11 (after groups, by file)

Approve, or move threads between groups.
```

Decisions wait for the cards. With no groups, say "No groups; walking <n>
threads by file" and go straight to the walk. Walk order: groups first, then
singles by file path, so neighbouring comments share fresh context.

## Card

Before each card, read what the claim needs: the commented code, its callers,
a sibling implementation, the project rule it cites, and for an outdated thread
the current code. Then show:

```markdown
**3/9 · #5 · Minor · `type_field_handler.dart:61`** · coderabbitai · ⚠️
**Comment:** <the claim, one sentence>
**Analysis:** <holds | partly holds | doesn't hold> — <key evidence, one sentence>
**Proposal:** fix | clarify | skip — <approach or reason, one sentence>
**Reply:** <exact text to post, 1–2 sentences>
approve · edit · expand · or guide me
```

| Optional line | When |
|---|---|
| `+ Scope: same in <files> — approve separately` | Same issue beyond the commented lines |
| `Earlier: <decision> · Reviewer now: "<one line>"` | A thread from an earlier round with a new reply |
| `G1 · <n> threads (#…)` in the header | A group card; the reply is posted on each thread |

Severity appears when the comment carries one. An outdated thread whose concern
the current code already answers is a `skip` pointing to the commit that
answered it.

The user answers:

- **approve** — with the scope line, if any; **approve without extra scope** drops it.
- **edit** — they name the field and the change; apply it and record.
- **expand** — show the full cleaned comment, the thread URL, the suggested
  change, the evidence snippets and the plan section you intend; then wait.
- **guide me** — their direction for this comment; re-analyse and show the card again.

## Reply

The reply is the only text that leaves the workspace; it is approved as shown
on the card.

| Decision | Shape |
|---|---|
| `fix` | `Fixed in {sha}: <what changed>.` + `Also applied to <X> for consistency.` with extra scope |
| `skip` | `<reason>.` + `Tracked in <ticket / issue / follow-up PR>.` when deferred |
| `clarify` | `<what we understood>; <the question>?` |

Plain and specific; a human reviewer gets a warmer tone than a bot. The thread
already notifies its participants, so names stay unmentioned.

## Record

On approve or edit, record the card at once:

```bash
python scripts/walk_item.py add <workspace> --rows 5 --decision fix <<'EOF'
Fixed in {sha}: Type is cleared on failure, so picking it again retries.
EOF
```

A group passes all its rows (`--rows 1-9,14`). A repeat `add` replaces the
row's item, so a changed mind is one more `add`. Then show one line and the
next card:

```markdown
✓ #5 fix · 4/9 next
```

For a `fix`, write its section in `rounds/N/plan.md` right after recording,
while the code is fresh, using `va-sdlc-template` (plan, simple layout, one section
per fix or group, including approved extra scope). A re-decided row updates or
removes its section with it. Cross-fix notes and Verification are Phase 4's.

## Resume

`round.py status` lists the pending rows; continue with the first in walk order.

**Done when**: `round.py status` shows no pending row, and every `fix` row has
its section in `plan.md`.
