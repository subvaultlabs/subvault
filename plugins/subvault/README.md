# SubVault for Claude

SubVault is your personal memory database. Your facts, decisions, and open tasks live in one vault at [subvault.ai](https://subvault.ai) and move with you: the session you close in Claude opens in any client you connect next.

## What this plugin installs

- **MCP connection** to the hosted SubVault server (`mcp.subvault.ai`). Sign-in uses OAuth; your first tool call opens the login flow.
- **The subvault skill.** It teaches Claude the rules: save only when you say vault, recall only when you say remember, and write sessions in a fixed five-section format that the next session reads back verbatim.
- **Two commands, matching the two verbs:**
  - `/vault` saves the session. `/vault <thing>` saves that thing.
  - `/remember` opens with last session's state: what you decided, what got done, what comes next. `/remember <topic>` recalls context about that topic.

## The two verbs

**vault** saves. Claude fills a structured session template: a summary, decisions with reasoning, completed work, an ordered next list, and notes. Completed work closes matching open tasks.

**remember** recalls. The assembler picks items for your current situation. Last session comes back exactly as you left it; older material is picked by relevance.

Claude never saves without you asking and never recalls on its own. The verbs invoke on their literal words.

## Install

In Claude Code:

```
/plugin marketplace add subvaultlabs/subvault
/plugin install subvault@subvault
```

Or add it from the plugin directory in Cowork under Plugins.

## Requirements

- A SubVault account ([subvault.ai](https://subvault.ai))
- Claude Code or Cowork with plugins enabled

## Data

Your vault is yours. Structured items live in a per-workspace database on SubVault's servers. The extraction schema and MCP spec are open source at [github.com/subvaultlabs](https://github.com/subvaultlabs).

## License

MIT (this plugin). The SubVault service is proprietary.
