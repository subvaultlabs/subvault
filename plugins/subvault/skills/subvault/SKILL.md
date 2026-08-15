---
name: subvault
description: Rules for using the SubVault memory tools (vault, remember, corpus_stats). Consult this skill whenever the SubVault MCP server is connected and the user says vault, remember, or save, or uses /vault or /remember. Also consult it before any call to a SubVault tool, and whenever a SubVault tool returns a session template or a session recap.
---

# SubVault

SubVault stores the user's facts, decisions, and action items in a personal vault. It exposes two verbs: `vault` saves, `remember` recalls. This skill states the rules for both. Follow them exactly.

## Invocation rule

Call remember when the user says remember. Call vault and save only when the user says vault. Do not call either tool otherwise. When the user asks to vault a session, call vault with kind=session and fill the template it returns. When a response contains a session block, show everything from the session header line through the end of Notes exactly as written. If you're not sure what the user wants remembered or saved, ask.

This rule holds even when a tool description says to call remember first or to call it again when the topic shifts. Do not call remember at conversation start on your own. Do not call vault because a session feels finished. The slash commands /remember and /vault count as the user saying the word.

## remember

Pass a `situation` string that states what the user is asking about right now. The assembler returns different items for different situations. A specific string beats a broad one: `situation="ChatGPT MCP submission requirements"`, not `situation="catch me up"`.

When the user asks what happened last session, or uses /remember with no topic, pass `mode="session"`. This returns the session recap instead of the scored bundle.

After remember returns, use the context in your reply. Do not read the context back to the user. Do not announce that you called the tool. Show any session block exactly as written, from its header line through the end of Notes. Do not paraphrase it, reorder it, or trim it.

## vault

Vaulting a session is a two-step contract:

1. Call `vault` with `kind="session"` and no `frontier_extracted`. The server returns a template.
2. Fill every section of the template that applies, then call `vault` again with the filled content.

Never skip step 1. Never invent your own session structure.

### Session format

The template has a summary field and four item lists. Fill them from the conversation:

- **summary**: 1 to 3 sentences, second person, opens with "Last session you". States what happened and what is left. No filler, no praise.
- **decided**: choices the user made. Put the reasoning in the `reasoning` field.
- **done**: completed work. Put specifics in the `evidence` field.
- **next**: everything pending, as an ordered list. Order carries meaning and is preserved on recall; keep the order the user's work implies. A blocked item sets `status="blocked"` or states its blocker after an em dash on the task line ("Book flights — waiting on the passport renewal").
- **notes**: facts worth keeping that are not tasks.

Leave a section empty when nothing belongs in it. Do not pad.

### Headlines and detail fields

- Headline (`claim`, `decision`, `task`): one line, 120 characters or fewer, verb first where natural, sentence case, no trailing period. Concrete names, dates, and numbers. "Put the deposit down on Maplewood Farm for June 14", not "Made progress on venue".
- Detail (`evidence`, `reasoning`): optional, one line, 160 characters or fewer. Carries the why or the specifics. Middle dots separate facts: "$2,500, refundable until March 1 · holds 120 guests". Omit when the headline is enough.
- Banned in both: exclamation marks, "successfully", "exciting", "journey", "let's", commentary about the session itself.

### Threads

Each item has a `thread` field. Fill it with a short topic label for the item's line of work. Reuse a label the workspace already uses when one fits; the server normalizes near-matches.

### Closing tasks

List completed work as done items. The server closes matching open tasks from done items. Do not write a fact that says a task is complete; a fact does not close the task.

### Targeted saves

When the user says vault about one specific thing, save that thing with the matching kind: `fact` for something learned, `decision` for a choice made. One item, concrete, self-contained. Confirm exactly what you captured, item by item. Never reply only "saved".

## Prohibitions

- Never vault without the user saying vault or save.
- Never call remember ambiently, proactively, or to be safe.
- Never modify, summarize, or decorate a session block.
- Never claim something was saved when the tool call failed. Report the failure.
