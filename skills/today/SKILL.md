---
name: today
description: Brief the user on what needs doing today from the wiki — open actions, what they are waiting on, today's meetings, and the merge state of any GitHub PR an action points at. Use when the user asks what is on their plate, what to do today, or for a morning briefing.
---

# What needs doing today

Every unchecked box in `wiki/daily/` lands in exactly one of the four briefing sections — nothing open goes unmentioned, nothing appears twice. Read `CLAUDE.md` for the wiki conventions.

## 1. Check the wiki is current

`date -u +%Y-%m-%dT%H:%MZ` and `cat wiki/.last-sync.*`. When the oldest watermark is more than 12 hours old, say so in the status line and offer `/sync` — then brief on what the wiki already holds rather than stopping. Skim `wiki/index.md` for the live topics.

## 2. Collect the open loops

- `grep -rn '^- \[ \]' wiki/daily/` — open actions. The filename gives each one its age.
- `grep -rn -A20 '^## Waiting on' wiki/daily/` — what others owe the owner, and since when. A line that names a deadline ("by EOD 2026-08-26", "needed by Friday") is **overdue** once that date has passed.

## 3. Check the PRs

Open actions cite GitHub PRs two ways: a full `https://github.com/ORG/REPO/pull/N` link, or a bare `#N` with the repo named in the surrounding text (`dag_repo PRs … #331`). Resolve each one:

```sh
gh pr view <url> --json state,mergedAt,title
gh pr view <N> --repo VOIDSTechnology/<repo> --json state,mergedAt,title
```

A bare `#N` whose repo the text does not name is skipped and listed as unresolved in the briefing. Every resolved PR gets a tag on its action line: `PR #104 open`, `PR #6 merged 2026-08-21`, `PR #303 closed unmerged`.

Merged is a **signal, not a done**. Two cases:

- The action *is* the PR — review, deploy, test, triage it. Merged means the action is probably complete: put it under `## Done since last brief?` and ask.
- The PR is *context* for a follow-up — "raise `min_replicas` after PR #6". Merged changes nothing; the follow-up stays where it belongs, with the tag on it.

## 4. Pull today's calendar

`mcp__claude_ai_Microsoft_365__outlook_calendar_search` for today, `order: oldest`. A meeting whose subject or attendees match an open action turns that action into prep work due before the meeting.

## 5. Deliver the briefing

Scannable first, complete second: the owner reads the status line and `## Today`, and everything below is there when they need it. One line per item where a line will do; two at most.

```md
**2026-08-27** · synced 11h ago · 13 open · 1 meeting

**Meetings** — 07:30 Daily Stand Up Tech Team (Tobi, Cristian, Illia, Pawan, Sergei)

## Today — 5 of 13
1. **Start the `drmersclub` pipeline** — [[Pia Bahr]] blocked, cannot trigger from admin · `2026-08-26`
2. **Deploy + test mcp_servers PR #104** — Cristian waiting since yesterday · PR #104 open · `2026-08-26`

## Done since last brief?
- **Triage dag_repo #303** — PR #303 merged 2026-08-26 · `2026-08-26` — check it off?

## Waiting on — 8
- ⚠ **#custom-integrations** — glow25 plan feedback, was due EOD 2026-08-26 · nudge at standup
- [[Jannis Baule]] — glow25 step 1 timeline · 1d
- [[Tobias Wandersleb]] — interview recording feedback · 1d; nango.dev + Entra role · 2d, not urgent

## Aging — 7+ days, 2
- **Answer Tom Kustak's 10 questions** — 24d, external · `2026-08-03` — still live, or drop?

## Backlog — 6
- Raise `voidsapi-external-prod` min_replicas → 2-3 · PR #6 merged 2026-08-21 · `2026-08-21`
- `magicperfumes` airbyte date — blocked on Pia naming it · `2026-08-24`
```

Rules of the layout:

- **Status line** first: date, sync age, open count, meeting count. The `/sync` offer goes here when the watermark is stale.
- **Today** — at most five, ranked: what someone else is blocked on or expecting, then prep for today's meetings, then everything else. Each item is `**verb-first title** — why now · PR tag if any · \`daily-note date\``. The date in backticks stands in for the path — `wiki/daily/<date>.md` is implied.
- **Done since last brief?** — only appears when a PR-is-the-action item resolved to merged. Omit the section when empty.
- **Waiting on** — one line per person, their items joined with `;`, each with age in days. ⚠ leads any line past a stated deadline, and those sort to the top.
- **Aging** — every action open 7+ days that is not in Today, each ending with the drop question. Age in days, not dates.
- **Backlog** — everything open that landed nowhere above. Terse: title, blocker or PR tag if any, date. This section exists so the four sections partition the open set exactly; an item that would need a fifth section belongs here.
- Section headings carry counts (`## Today — 5 of 13`) so the owner sees the shape of the day without reading the body.
- Name people, link them `[[Name]]` on first mention per section.

## 6. Open the checklist

After the briefing, run `python3 skills/today/scripts/todo.py`. It serves every open box as a clickable checklist at `http://127.0.0.1:8642/`, opens it in the browser, and stays running in the background (`python3 skills/today/scripts/todo.py stop` ends it). Ticking a box rewrites `- [ ]` to `- [x]` in the daily note the line came from — the same edit you would make by hand, so the next briefing drops it. End the briefing with the URL on its own line.

## 7. When the user marks items done in chat

Check the box in the daily note it came from (`- [x]`) and reply with the new open count and what moved into the top five. Person pages (`## Owed to`) are not touched here — whether a box was ticked on the page or in chat, `/lint` reconciles them.
