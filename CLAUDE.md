# Second brain

A wiki of what came through the owner's Slack and Outlook, and the actions that fell out of it. Three flows: `/sync` writes the day in, `/today` reads the day out (syncing first when the wiki is over 12 hours stale), `/lint` keeps the wiki honest.

## Wiki layout

`wiki/` is gitignored — note content never gets committed and never leaves this machine. Only the structure lives in git.

- `wiki/index.md` — catalog: one line per page (topics, people, daily notes by month). Read it first when answering anything; `/sync` keeps it current.
- `wiki/log.md` — append-only record, one `## [YYYY-MM-DD] sync|lint|query | …` heading per event. `grep "^## \[" wiki/log.md | tail -5` shows what happened recently.
- `wiki/daily/YYYY-MM-DD.md` — one file per day: exchanges, actions, waiting-ons.
- `wiki/topics/<slug>.md` — running notes on a topic that keeps recurring. Create one once a topic has spanned three daily notes, and link it from them as `[[topics/<slug>]]`.
- `wiki/people/<Name>.md` — one page per person linked as `[[Name]]`: role, current threads, what they owe and are owed, short history. Created on first link, refreshed by `/sync`.
- `wiki/.last-sync.<source>` — ISO timestamp of that source's last sweep end (`slack`, `outlook`). A failed source keeps its watermark; the others still advance.
- `wiki/identity.md` — the owner's Slack user id and mailbox. Gitignored, like everything under `wiki/`.

Every page opens with frontmatter: `type` (`daily`|`topic`|`person`|`index`), `date` (daily) or `updated` (everything else), and on daily notes the `people` and `topics` lists of what the note links.

## Conventions

- Absolute dates always (`2026-08-26`), never "yesterday".
- An action is a markdown checkbox: `- [ ] <what> — <who it is for>, <source link>`. Daily notes are the single source of truth for actions; `/today` collects the unchecked boxes across `wiki/daily/` and serves them as a checklist (`skills/today/scripts/todo.py`) whose ticks write `- [x]` straight back into the note.
- An action lives in exactly one daily note. Before writing one, grep the open boxes for it; if it is already open, append ` · re-raised YYYY-MM-DD` to the existing line instead of writing a new one.
- What you owe someone goes under `## Actions`. What someone owes you goes under `## Waiting on`.
- Link people, topics and days as `[[Dana Fischer]]`, `[[topics/warehouse-rollout]]`, `[[2026-08-26]]` — basenames resolve, so a person's page is `wiki/people/Dana Fischer.md`.
- Name people rather than pronouning them (`Dana asked…`, not `she asked…`) — nobody in the wiki has stated their pronouns.
- Keep every source link (Slack permalink, Outlook `webLink`) — the wiki is an index into the real thing, not a replacement for it.

## Answering questions from the wiki

Read `wiki/index.md`, then grep `wiki/` before answering anything about what was said, decided, or promised (`grep -ril <term> wiki/`), and cite the daily-note path you drew from. When the wiki is silent, say so and offer a live Slack/Outlook search rather than guessing. An answer worth keeping (a comparison, a timeline, a decision trail) is filed as a topic page and logged as `query`.
