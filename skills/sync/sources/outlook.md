# Outlook

Watermark: `wiki/.last-sync.outlook`.

`mcp__claude_ai_Microsoft_365__outlook_email_search` with `afterDateTime: <window start>`, `order: "newest"`, `limit: 25`, `offset: 0`, following `nextOffset` until the window is covered.

Sort each message into one of two piles:

- **Human mail** — a person writing to the owner, or a thread the owner is on. Read the body with `read_resource` on the message `uri` when the subject alone does not say what it asks for. Keep the `webLink`.
- **Bulk mail** — marketing, digests, product notifications (issue trackers, forges, surveys). Counted in `## Noise`, not written.
