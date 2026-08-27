---
name: lint
description: Health-check the wiki — dangling links, topics due for promotion, duplicate or stale actions, people pages out of date, index drift. Use when the user says lint the wiki, check the wiki, or once a week after a sync.
---

# Lint the wiki

Read `CLAUDE.md` first. Report everything, then fix only what the user confirms — except `wiki/index.md` and `wiki/log.md`, which are always safe to regenerate.

## Checks

1. **Dangling links** — every `[[Name]]` has `wiki/people/<Name>.md`, every `[[topics/x]]` and `[[YYYY-MM-DD]]` exists. `grep -oh '\[\[[^]]*\]\]' -r wiki/ | sort -u` against `ls`.
2. **Promotion due** — a subject (repeated keyword, PR, ticket, customer) in three or more daily notes with no topic page.
3. **Actions** — the same stem open in more than one file (duplicates); anything open 14+ days (propose: close, or move to the topic's `## Still open`).
4. **People** — pages whose `updated` predates their last daily mention; people linked 5+ times with no page; `## Owed to` lines whose action is checked off (or gone) in the daily note it cites — remove the line, and the heading when it is left empty.
5. **Index** — pages missing from `wiki/index.md`; index lines pointing at nothing.
6. **Orphans** — topic or people pages with no inbound link.

## Output

One table per check: finding → proposed fix → file. Apply the confirmed fixes, then append `## [<today>] lint | <n> findings, <n> fixed` to `wiki/log.md`.
