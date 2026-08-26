# Slack

Watermark: `wiki/.last-sync.slack`. Read `wiki/identity.md` for `<SLACK_ID>`.

Three searches with `mcp__claude_ai_Slack__slack_search_public_and_private`, `sort: "timestamp"`, `include_context: false`, `limit: 20`:

| What | `keywords` | `filters` |
| --- | --- | --- |
| DMs and group DMs | `[]` | `is:dm after:<DATE>` |
| Mentions of the owner | `["<@SLACK_ID>"]` | `after:<DATE>` |
| What the owner said | `[]` | `from:<@SLACK_ID> after:<DATE>` |

The owner's own messages matter as much as the inbound ones — that is where the commitments live.

Quirks:
- `after:` is date-granular **and excludes the named date** — pass the day *before* the window start and expect a little overlap; passing the window start's own date silently drops that whole day. `on:YYYY-MM-DD` sweeps a single day.
- Results page at 20: follow the cursor until the oldest hit predates the window, otherwise a busy morning silently truncates.
- Search returns snippets. When a hit carries a decision, a question aimed at the owner, or a commitment, pull the conversation with `slack_read_thread` (threaded) or `slack_read_channel` (channel context) so the note records what was settled, not a fragment.
