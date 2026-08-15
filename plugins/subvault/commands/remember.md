---
description: Recall from SubVault. Bare /remember opens with last session's state; /remember <topic> recalls context about that topic.
---

The user invoked /remember. Follow the subvault skill.

Arguments: $ARGUMENTS

- No arguments: call the `remember` tool with `mode="session"` and `situation="session open"`. This returns the session recap: last session's summary, then Decided, Done, Next, and Notes. Show everything from the session header line through the end of Notes exactly as written. Do not paraphrase, reorder, or trim it. Then wait for the user's direction.
- Arguments given: call the `remember` tool with a `situation` string built from the arguments. Be specific: pass what the user is asking about, not a generic phrase. Use the returned context in your reply. Do not read it back or announce the call. If the result contains a session block, show it exactly as written, from its header line through the end of Notes.
