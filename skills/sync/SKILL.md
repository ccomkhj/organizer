---
name: sync
description: Sweep Slack DMs/mentions and Outlook mail since the last sync into a dated wiki note. Use when the user says sync, catch me up, pull my day, or when a scheduled daily ingest fires.
---

# Sync the day into the wiki

Every exchange in the window lands in the daily note or is counted in its `## Noise` line — nothing in the window goes unaccounted for. Read `CLAUDE.md` for the wiki layout and conventions before writing.

`wiki/identity.md` holds the owner's Slack user id and mailbox — read it first and substitute for `<SLACK_ID>` below. It is gitignored, so identity never ships with this repo.

## 1. Fix the window

`date -u +%Y-%m-%dT%H:%M:%SZ` for the end, and `cat wiki/.last-sync` for the start. No `.last-sync` file means a first run: start 24 hours back. Report the window in chat before sweeping.

## 2. Sweep Slack

Three searches with `mcp__claude_ai_Slack__slack_search_public_and_private`, `sort: "timestamp"`, `include_context: false`, `limit: 20`, `<DATE>` being the window start as `YYYY-MM-DD`:

| What | `keywords` | `filters` |
| --- | --- | --- |
| DMs and group DMs | `[]` | `is:dm after:<DATE>` |
| Mentions of the owner | `["<@SLACK_ID>"]` | `after:<DATE>` |
| What the owner said | `[]` | `from:<@SLACK_ID> after:<DATE>` |

The owner's own messages matter as much as the inbound ones — that is where the commitments live. Slack's `after:` is date-granular, so round the window start down to its date and expect a little overlap with the previous sync.

Each search pages at 20 results: follow the returned cursor until the oldest hit predates the window, otherwise a busy morning silently truncates.

Search returns snippets. When a hit carries a decision, a question aimed at the owner, or a commitment, pull the surrounding conversation with `slack_read_thread` (threaded) or `slack_read_channel` (channel context) so the note records what was actually settled rather than a fragment.

## 3. Sweep Outlook

`mcp__claude_ai_Microsoft_365__outlook_email_search` with `afterDateTime: <window start>`, `order: "newest"`, `limit: 25`, `offset: 0`, following `nextOffset` until the window is covered.

Sort each message into one of two piles:

- **Human mail** — a person writing to the owner, or a thread the owner is on. Read the body with `read_resource` on the message `uri` when the subject alone does not say what it asks for.
- **Bulk mail** — marketing, digests, product notifications (issue trackers, forges, surveys). These get counted, not written.

## 4. Write the note

Append to `wiki/daily/<today>.md`, creating it from this shape when absent:

```md
# 2026-08-26

Synced: 2026-08-25T18:00:00Z → 2026-08-26T09:15:00Z

## Actions
- [ ] Deploy and test the MCP branch PR — for [[Sam Rivera]], <PR link>

## Waiting on
- [[Alex Brandt]] — feedback on the two customer interviews, asked 2026-08-26

## Exchanges
### Slack
- **DM with [[Sam Rivera]]** — asked whether the promotions skill still exists; the answer was that the old direct-API skills look dead and can be deleted. <permalink>
### Email
- **Re: Supplier Portal** — [[Dana Fischer]] mapped the purchasing and inbound process end to end for review. <webLink>

## Noise
7 bulk messages skipped.
```

Write what was *settled or asked*, one line per exchange — a reader six weeks out should understand the exchange without opening the link. A second sync on the same day appends to the existing sections instead of starting a new file.

Promote a topic to `wiki/topics/<slug>.md` once it has appeared in three daily notes, and link it both ways.

## 5. Close the loop

Write the window end to `wiki/.last-sync`, then report in chat: the window, counts per source, and the new action lines verbatim.

## Scheduled runs

Not wired. The intended path is a launchd job running `claude -p /sync` in this repo; before trusting it, confirm the Slack and Microsoft 365 connectors resolve in a headless run — they are interactively authenticated and may be absent there.
