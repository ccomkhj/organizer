# Organizer

A second brain for [Claude Code](https://claude.com/claude-code). It reads what came through your Slack and Outlook and writes it down as a wiki of exchanges, decisions and open actions. Two flows:

- `/sync` — sweep everything since the last sync into `wiki/daily/<today>.md`
- `/today` — collect the open actions across those notes, say what needs doing, and open them as a clickable checklist at `http://127.0.0.1:8642/` — a tick marks the box done in its daily note
- `/lint` — health-check the wiki: dangling links, duplicate or stale actions, topics due for promotion

Your notes stay out of this repo. `wiki/` is a clone of a separate private repo and is ignored here, so only the skills and the conventions are public.

## Setup

1. Create a private repo for the notes and clone it into `wiki/`:

   ```sh
   gh repo create <you>/organizer-wiki --private
   git clone git@github.com:<you>/organizer-wiki.git wiki
   ```

   Every flow that writes the wiki pulls it first and pushes `main` after. That is how the cloud routine and your laptop stay in step.
2. Connect the Slack and Microsoft 365 connectors at claude.ai → Customize → Connectors. The same connectors serve Claude Code on your laptop and in the cloud.
3. Create `wiki/identity.md` and commit it to the wiki repo. It is the only place your identity lives:

   ```md
   # Identity

   - Name: Ada Lovelace
   - Slack: `U01234567` (example.slack.com)
   - Mailbox: ada@example.com (Microsoft 365 / Outlook)
   ```

4. Run `/sync`. First run sweeps the last 24 hours and writes a `wiki/.last-sync.<source>` watermark per source; every run after that picks up where the last one stopped.
5. Run `/today` for the briefing.

## Layout

| Path | What |
| --- | --- |
| `skills/` | The three skills. `.claude/skills` is a symlink here, so anything you add is picked up. Connector specifics live in `skills/sync/sources/`; `skills/today/scripts/todo.py` is the checklist server (stdlib Python, `python3 skills/today/scripts/todo.py [stop]`). |
| `CLAUDE.md` | Wiki layout and note conventions — read by every run. |
| `wiki/` | Your notes: `daily/`, `topics/`, `people/`, plus `index.md` (catalog) and `log.md` (what happened when). A clone of your private wiki repo, ignored here. |

## Scheduling

A Claude Code routine runs the morning briefing in the cloud, so the laptop can stay off. Create it with `/schedule` or at claude.ai/code/routines:

- **Repos** — this one and your wiki repo. Allow unrestricted branch pushes on the wiki repo: each run clones `main`, so the sync must land there.
- **Connectors** — Slack and Microsoft 365 only.
- **Schedule** — weekdays 07:00 in your timezone.
- **Prompt**:

  ```
  You are running unattended — nobody will answer questions.
  1. In the organizer checkout, symlink the organizer-wiki checkout to ./wiki (ln -sfn). Never commit to organizer.
  2. Run /today as an unattended run (skills/today/SKILL.md, "Unattended runs").
  ```

Each run syncs, pushes the wiki, and sends the briefing as a Slack DM and an email to yourself. The laptop is the second writer: `/today` pulls first, and the checklist pushes each tick, so the routine does not re-raise what you have already done.

## Adding to it

The setup is deliberately small: three skills, one conventions file, markdown checkboxes as the only state. To add a source (calendar, Linear, GitHub), drop a `skills/sync/sources/<name>.md` describing its sweep and quirks, list it in `skills/sync/SKILL.md`, and add a section to the daily-note template — it gets its own `.last-sync.<name>` watermark and nothing else needs to know about it.
