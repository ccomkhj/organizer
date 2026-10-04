---
name: today
description: Morning briefing from the wiki — open actions, what the user is waiting on, today's meetings, and the merge state of any PR an action cites; syncs first when the wiki is stale. Use when the user asks what is on their plate, what to do today, or for a briefing.
---

# What needs doing today

Every unchecked box in `wiki/daily/` lands in exactly one of the four briefing sections — nothing open goes unmentioned, nothing appears twice. Read `CLAUDE.md` for the wiki conventions.

## 1. Bring the wiki current

`git -C wiki pull --rebase --autostash` first. Syncs and ticks made by the other writer arrive this way. Then `date -u +%Y-%m-%dT%H:%MZ` and `cat wiki/.last-sync.*`. Oldest watermark over 12 hours old → say the wiki is `<n>h` stale and run `/sync` before briefing; it writes the notes for the days the window spans, and their new `- [ ]` lines join the open set. Under 12 hours → brief on the wiki as it stands.

A failed source or a connector that will not resolve never cancels the briefing: report it in the status line and brief on what the wiki holds. Then skim `wiki/index.md` for the live topics.

## 2. Collect the open loops

- `grep -rn '^- \[ \]' wiki/daily/` — open actions. The filename gives each one its age.
- `grep -rn -A20 '^## Waiting on' wiki/daily/` — what others owe the owner, and since when. A line naming a deadline ("by EOD 2026-08-26") is **overdue** once that date has passed.

## 3. Check the PRs

Actions cite PRs as a full `https://github.com/ORG/REPO/pull/N` link or as a bare `#N` with the repo named nearby (`dag_repo PRs … #331`). Resolve each:

```sh
gh pr view <url> --json state,mergedAt,title
gh pr view <N> --repo VOIDSTechnology/<repo> --json state,mergedAt,title
```

A bare `#N` with no repo in the text is listed as unresolved. Every resolved PR gets a tag on its line: `PR #104 open`, `PR #6 merged 2026-08-21`, `PR #303 closed unmerged`.

Merged is a **signal, not a done**:

- The action *is* the PR — review, deploy, test, triage it → it goes under `## Done since last brief?` with the question.
- The PR is *context* for a follow-up ("raise `min_replicas` after PR #6") → the follow-up stays where it belongs, tag attached.

## 4. Pull today's calendar

`mcp__claude_ai_Microsoft_365__outlook_calendar_search` for today, `order: oldest`. Times in Europe/Berlin — the tool returns UTC. List only meetings still ahead. A meeting whose subject or attendees match an open action turns that action into prep work due before it.

## 5. Deliver the briefing

Scannable first, complete second: the owner reads the status line and `## Today`; the rest is there when needed. One line per item, two at most.

```md
**2026-08-27** · synced just now · 4 slack, 2 mail, 3 new actions · 13 open · 1 meeting left

**Meetings** — 09:30 Daily Stand Up Tech Team (Tobi, Cristian, Illia, Pawan, Sergei)

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

What the example cannot show:

- **Today** holds at most five, ranked: what someone else is blocked on or expecting, then prep for today's meetings, then the rest. The backticked date stands for `wiki/daily/<date>.md`.
- **Waiting on** is one line per person, items joined with `;`, each with its age in days; ⚠ lines sort first.
- **Aging** is every action open 7+ days that is not in Today. **Backlog** is everything else, so the four sections partition the open set exactly — an item that seems to need a fifth section belongs here.
- `## Done since last brief?` is omitted when empty. People are linked `[[Name]]` on first mention per section.

## 6. Open the checklist

Run `python3 skills/today/scripts/todo.py` — it serves the open boxes as a checklist whose ticks write `- [x]` back into the notes, and prints its URL. End the briefing with that URL on its own line.

## 7. When the user acts on an item in chat

- **Marks it done** → check the box in its daily note and reply with the new open count and what moved into the top five.
- **Asks you to do it** → look at the target system's current state first: the line was written from a Slack fragment and may already be partly done. Then do it, check the box, and append the outcome to the line (`· DSE-1618, PE-1597 created 2026-08-28`).

Each box checked here is committed and pushed as `tick <date>`, the same way `todo.py` pushes its ticks. Otherwise the routine re-raises the action the next morning. Person pages (`## Owed to`) are not touched here; `/lint` reconciles them.

## Unattended runs

When the cloud routine runs this, nobody is in chat. Never ask, never wait.

- **Always sync** in step 1, whatever the watermarks say. A morning briefing that skips the night is the one failure this run exists to prevent.
- **Sync in full.** Follow every cursor, read the threads that carry a decision or a question, and refresh people pages, exactly as `/sync` says. Nobody is waiting on this run, so never sample or abridge. Anything left unread inside the window is lost for good once its watermark advances.
- **Load connector tools before calling them.** They may be deferred. Fetch each one with ToolSearch first, `outlook_send_mail` included. A tool counts as missing only when ToolSearch cannot find it.
- **Skip steps 6 and 7.** There is no checklist server and nobody to act in chat.
- **Deliver the briefing twice.** The owner's Slack id and mailbox are in `wiki/identity.md`.
  - **Slack DM** — `mcp__claude_ai_Slack__slack_send_message` with `channel_id` = the owner's Slack id. Send the status line, the meetings line, `## Today`, and any ⚠ waiting-on lines, then the session link. Write it in standard markdown (the tool converts it), with `[[Name]]` as plain names and at most 5000 characters.
  - **Email** — `mcp__claude_ai_Microsoft_365__outlook_send_mail` to the owner's mailbox, subject `Briefing <date>`, `bodyType: "html"`. Send the full briefing, then the session link.
- **Session link** — `echo "https://claude.ai/code/${CLAUDE_CODE_REMOTE_SESSION_ID/#cse_/session_}"`.
- **Failures are reported, never fatal.** A channel that fails is named in the other one (`Slack DM failed: <error>`) and never stops it. If both fail, say so in the transcript. A failed sync is reported in the status line of both, as in step 1.
