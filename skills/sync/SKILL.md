---
name: sync
description: Sweep Slack DMs/mentions and Outlook mail since the last sync into a dated wiki note. Use when the user says sync, catch me up, pull my day, or when a scheduled daily ingest fires.
---

# Sync the day into the wiki

Every exchange in the window lands in the daily note or is counted in its `## Noise` line — nothing in the window goes unaccounted for. Read `CLAUDE.md` for layout and conventions, and `wiki/identity.md` for the owner's Slack id and mailbox (gitignored, never ships with the repo).

## 1. Fix the windows

End = `date -u +%Y-%m-%dT%H:%M:%SZ`. Start = `cat wiki/.last-sync.<source>` per source; a missing watermark means a first run — start 24 hours back. Report the windows in chat before sweeping.

## 2. Sweep each source

Follow each source file in full — it carries that connector's quirks:

- `sources/slack.md`
- `sources/outlook.md`

A source that errors is reported and keeps its watermark; the others still advance.

## 3. Write the daily note

Append to `wiki/daily/<today>.md`, creating it from this shape when absent; a second sync on the same day appends to the existing sections and extends `synced`.

```md
---
type: daily
date: 2026-08-26
synced: 2026-08-25T18:00:00Z → 2026-08-26T09:15:00Z
people: [Sam Rivera, Alex Brandt, Dana Fischer]
topics: [supplier-portal]
---
# 2026-08-26

## Actions
- [ ] Deploy and test the MCP branch PR — for [[Sam Rivera]], <PR link>

## Waiting on
- [[Alex Brandt]] — feedback on the two customer interviews, asked 2026-08-26

## Exchanges
### Slack
- **DM with [[Sam Rivera]]** — asked whether the promotions skill still exists; the answer was that the old direct-API skills look dead and can be deleted. <permalink>
### Email
- **Re: Supplier Portal** — [[Dana Fischer]] mapped the purchasing and inbound process end to end for review — [[topics/supplier-portal]]. <webLink>

## Noise
7 bulk messages skipped.
```

One line per exchange, stating what was *settled or asked* — a reader six weeks out should understand it without opening the link.

**No duplicate actions.** Before writing a `- [ ]`, `grep -rn '^- \[ \]' wiki/daily/ | grep -i '<stem>'`. Already open → append ` · re-raised <today>` to that existing line instead.

## 4. Maintain the wiki

- **People** — every `[[Name]]` in today's note has `wiki/people/<Name>.md` (shape: `type: person` frontmatter, `# Name`, `Role:`, `## Current threads`, `## Waiting on <Name>`, `## Owed to <Name>`, `## History`). Create missing pages; refresh the threads and open items of the people touched today and bump `updated`.
- **Topics** — promote once a subject spans three daily notes; link both ways.
- **Index** — add today's daily line to `wiki/index.md` and refresh the line of every page touched.
- **Log** — append `## [<today>] sync | <windows> | <n> slack, <n> mail, <n> new actions` to `wiki/log.md`.

## 5. Close the loop

Write each source's window end to its watermark, then report in chat: the windows, counts per source, and the new action lines verbatim.

## Scheduled runs

Not wired. The intended path is a launchd job running `claude -p /sync` in this repo; before trusting it, confirm the Slack and Microsoft 365 connectors resolve in a headless run — they are interactively authenticated and may be absent there.
