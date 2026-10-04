# Slack

Watermark: `wiki/.last-sync.slack`. Read `wiki/identity.md` for `<SLACK_ID>`.

Three searches with `mcp__claude_ai_Slack__slack_search_public_and_private`, `sort: "timestamp"`, `include_context: false`, `response_format: "concise"`, `limit: 20`:

| What | `keywords` | `filters` | `channel_types` |
| --- | --- | --- | --- |
| DMs and group DMs | `[]` | `is:dm after:<DATE>` | default |
| Mentions of the owner | `["<@SLACK_ID>"]` | `after:<DATE>` | default |
| What the owner said | `[]` | `from:<@SLACK_ID> after:<DATE>` | `public_channel,private_channel` |

The owner's own messages matter as much as the inbound ones — that is where the commitments live. The DM sweep already returns both sides of every DM, so scope the third search to channels — left at the default it re-walks the same DMs for pages.

Quirks:
- `after:` is date-granular **and excludes the named date** — pass the day *before* the window start and expect a little overlap; passing the window start's own date silently drops that whole day. `on:YYYY-MM-DD` sweeps a single day.
- Results page at 20: follow the cursor until the oldest hit predates the window, otherwise a busy morning silently truncates.
- `concise` is the sweep format and costs well under half of `detailed` for the same 20 hits — on a multi-day window that is the difference between fitting and not. It returns **no `message_ts`**, though, and a permalink cannot be rebuilt from the printed time. So never assemble one from the timestamp: a hit that earns a line in the note gets its real link from the `slack_read_thread` / `slack_read_channel` call below, or from one narrow `detailed` re-query (`on:<DATE>`, `in:<#channel>`).
- Search returns snippets. When a hit carries a decision, a question aimed at the owner, or a commitment, pull the conversation with `slack_read_thread` (threaded) or `slack_read_channel` (channel context) so the note records what was settled, not a fragment.
