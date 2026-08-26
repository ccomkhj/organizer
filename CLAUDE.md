# Second brain

A wiki of what came through the owner's Slack and Outlook, and the actions that fell out of it. Two flows: `/sync` writes the day in, `/today` reads the day out.

## Wiki layout

`wiki/` is gitignored — note content never gets committed and never leaves this machine. Only the structure lives in git.

- `wiki/daily/YYYY-MM-DD.md` — one file per day: exchanges, actions, waiting-ons.
- `wiki/topics/<slug>.md` — running notes on a topic that keeps recurring. Create one once a topic has spanned three daily notes, and link it from them as `[[topics/<slug>]]`.
- `wiki/.last-sync` — ISO timestamp of the last sweep's end. `/sync` reads it and writes it.
- `wiki/identity.md` — the owner's Slack user id and mailbox. Gitignored, like everything under `wiki/`.

## Conventions

- Absolute dates always (`2026-08-26`), never "yesterday".
- An action is a markdown checkbox: `- [ ] <what> — <who it is for>, <source link>`. Daily notes are the single source of truth for actions; `/today` collects the unchecked boxes across `wiki/daily/`.
- What you owe someone goes under `## Actions`. What someone owes you goes under `## Waiting on`.
- Link people and topics as `[[Dana Fischer]]`, `[[topics/warehouse-rollout]]`.
- Name people rather than pronouning them (`Dana asked…`, not `she asked…`) — nobody in the wiki has stated their pronouns.
- Keep every source link (Slack permalink, Outlook `webLink`) — the wiki is an index into the real thing, not a replacement for it.

## Answering questions from the wiki

Grep `wiki/` before answering anything about what was said, decided, or promised (`grep -ril <term> wiki/`), and cite the daily-note path you drew from. When the wiki is silent, say so and offer a live Slack/Outlook search rather than guessing.
