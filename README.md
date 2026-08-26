# Organizer

A second brain for [Claude Code](https://claude.com/claude-code). It reads what came through your Slack and Outlook and writes it down as a wiki of exchanges, decisions and open actions. Two flows:

- `/sync` — sweep everything since the last sync into `wiki/daily/<today>.md`
- `/today` — collect the open actions across those notes and say what needs doing
- `/lint` — health-check the wiki: dangling links, duplicate or stale actions, topics due for promotion

Your notes never leave your machine: `wiki/` is gitignored, so only the skills and the conventions are public.

## Setup

1. Connect the Slack and Microsoft 365 connectors in Claude Code (`/mcp`).
2. Create `wiki/identity.md` — gitignored, and the only place your identity lives:

   ```md
   # Identity

   - Name: Ada Lovelace
   - Slack: `U01234567` (example.slack.com)
   - Mailbox: ada@example.com (Microsoft 365 / Outlook)
   ```

3. Run `/sync`. First run sweeps the last 24 hours and writes a `wiki/.last-sync.<source>` watermark per source; every run after that picks up where the last one stopped.
4. Run `/today` for the briefing.

## Layout

| Path | What |
| --- | --- |
| `skills/` | The three skills. `.claude/skills` is a symlink here, so anything you add is picked up. Connector specifics live in `skills/sync/sources/`. |
| `CLAUDE.md` | Wiki layout and note conventions — read by every run. |
| `wiki/` | Your notes: `daily/`, `topics/`, `people/`, plus `index.md` (catalog) and `log.md` (what happened when). Gitignored. |

## Scheduling

Unwired by design — `/sync` is manual. The intended path is a launchd or cron job running `claude -p /sync` in this repo; before trusting it, confirm the Slack and Microsoft 365 connectors resolve in a headless run, since they are interactively authenticated and may be absent there.

## Adding to it

The setup is deliberately small: three skills, one conventions file, markdown checkboxes as the only state. To add a source (calendar, Linear, GitHub), drop a `skills/sync/sources/<name>.md` describing its sweep and quirks, list it in `skills/sync/SKILL.md`, and add a section to the daily-note template — it gets its own `.last-sync.<name>` watermark and nothing else needs to know about it.
