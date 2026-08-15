---
description: Save to SubVault. Bare /vault saves the session; /vault <thing> saves that thing.
---

The user invoked /vault. Follow the subvault skill.

Arguments: $ARGUMENTS

- No arguments: vault the session. Call the `vault` tool with `kind="session"` and no `frontier_extracted` to get the template, fill every applying section (summary, decided, done, next, notes, with thread labels), then call `vault` again with the filled content.
- Arguments name a specific thing: save that thing with the matching kind (`fact` or `decision`).

Confirm exactly what you captured, item by item. If the tool call fails, report the failure.
