---
name: today
description: Brief the user on what needs doing today from the wiki — open actions, what they are waiting on, and today's meetings. Use when the user asks what is on their plate, what to do today, or for a morning briefing.
---

# What needs doing today

Every unchecked box in `wiki/daily/` lands in exactly one section of the briefing — nothing open goes unmentioned. Read `CLAUDE.md` for the wiki conventions.

## 1. Check the wiki is current

`date +%Y-%m-%d` and `cat wiki/.last-sync.*`. When the oldest watermark is more than 12 hours old, say so in one line and offer `/sync` — then brief on what the wiki already holds rather than stopping. Skim `wiki/index.md` for the live topics.

## 2. Collect the open loops

- `grep -rn '^- \[ \]' wiki/daily/` — open actions. The filename gives each one its age.
- `grep -rn -A20 '^## Waiting on' wiki/daily/` — what others owe the owner, and since when.

## 3. Pull today's calendar

`mcp__claude_ai_Microsoft_365__outlook_calendar_search` for today. A meeting whose subject matches an open action turns that action into prep work due before the meeting.

## 4. Deliver the briefing

```md
## Today
1. <action> — <why now: meeting at 14:00 / promised 3 days ago> (wiki/daily/2026-08-24.md)

## Waiting on others
- [[Alex Brandt]] — interview feedback, 2 days out

## Aging (open 7+ days)
- <action> (wiki/daily/2026-08-14.md) — still live, or drop it?
```

Rank `## Today` by what someone else is blocked on or expecting, then prep for today's meetings, then everything else — at most five items. Anything open 7+ days goes under `## Aging` with the drop question, rather than sitting in the top list forever.

When the user says an item is done, check its box in the daily note it came from (`- [x]`) so the next briefing drops it, and drop it from the person's `## Owed to` if listed there.
