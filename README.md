<p align="center">
  <img src="assets/logo-512.png" width="96" alt="SubVault" />
</p>

<h1 align="center">SubVault</h1>

<p align="center">
  <strong>Give your AI permanent memory. Two words: vault and remember.</strong>
</p>

<p align="center">
  <a href="https://subvault.ai"><img src="https://img.shields.io/badge/website-subvault.ai-2060E8" alt="website" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-black" alt="license" /></a>
  <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compliant-black" alt="MCP" /></a>
  <a href="SECURITY.md"><img src="https://img.shields.io/badge/security-info@subvault.ai-black" alt="security" /></a>
</p>

<p align="center">
  <img src="assets/hero-demo.gif" width="640" alt="SubVault demo" />
</p>

---

SubVault is an MCP server that gives Claude, Cursor, and Copilot shared memory. Say **vault** to save a session. Say **remember** to load it back later, in the same tool or a different one. Your AI never starts from zero.

## Install

```bash
curl -fsSL https://subvault.ai/install.sh | bash -s YOUR_API_KEY
```

Sign up at [subvault.ai](https://subvault.ai/signup) for the API key. One command configures Claude Desktop, Cursor, and VS Code, and it is safe to re-run.

Prefer a file? Claude Desktop has a one-click extension: download [subvault.mcpb](https://subvault.ai/subvault.mcpb) and double-click it. Claude.ai on the web connects through its Connectors UI: add `https://mcp.subvault.ai/mcp` as a custom connector and sign in.

Full setup at [subvault.ai/docs/setup](https://subvault.ai/docs/setup.html).

## What gets saved

When you say vault, your AI sends the session's facts, decisions, and action items to SubVault. When you say remember, SubVault sends back the ones that match, in about 2,000 tokens.

| Kind | Example |
| --- | --- |
| Decisions + reasoning | Chose PostgreSQL over MongoDB. Billing needs relational integrity. |
| People + relationships | Sarah owns frontend, Mike handles DevOps, report to Lisa. |
| Action items + status | Update billing webhook before Friday. Blocked on Stripe keys. |
| Project context | API at v2, migration from v1 in progress, 3 endpoints left. |

## Why not just transcripts

| Transcripts & built-in memory | SubVault |
| --- | --- |
| Dumps entire transcripts | Keeps decisions, people, open threads |
| No relevance ranking | Ranks by who said it, how fresh, how relevant |
| Fills the context window | The current truth in ~2,000 tokens |
| Same info every time | Shapes context to the question |
| Locked to one AI tool | One memory, under every MCP client |

## Where your data lives

When you say vault, your AI extracts the facts, decisions, and action items from the session and sends those, not the transcript. A 1,000-word conversation arrives as a dozen short entries.

- **Only saved items are sent.** When you vault, your AI sends the items being saved and nothing else. SubVault has no access to the rest of the conversation.
- **One vault, one SQLite database.** Each vault is its own SQLite database. There are no shared tables between users.
- **Deletion.** Deleting your vault deletes the database. Backups are removed on the retention cycle.
- **Standard format.** Your vault is one standard SQLite database, not a proprietary store.

## How it works

What happens when you say vault:

| Stage | What happens |
| --- | --- |
| Structured extraction | A session is saved as separate facts, decisions, people, and action items. Each entry makes sense without the original conversation. |
| Ranking | Results are ranked by source, recency, and relevance. Things you stated outrank things the model inferred. |
| Query classification | "Who is Sarah?" returns people. "What's the status?" returns action items. |
| Token budget | Every response fits a fixed budget of about 2,000 tokens. |
| Deduplication | Items are hashed on save. Vaulting the same thing twice stores it once. |
| Injection protection | Every item is checked for prompt-injection patterns before it enters your AI's context. |

Current production numbers, measured on the production server: about 300 ms median context assembly, about 2,000 tokens per assembled context, one SQLite database per vault.

## Demos

#### Save knowledge from a chat
<img src="assets/demo-vault-conv.gif" width="640" alt="Vault from conversation" />

#### Recall it in a different tool
<img src="assets/demo-remember-conv.gif" width="640" alt="Remember across chats" />

#### Capture decisions while you code
<img src="assets/demo-vault-dev.gif" width="640" alt="Vault from code" />

#### Pull yesterday's context into today's work
<img src="assets/demo-remember-dev.gif" width="640" alt="Remember in editor" />

## How your AI uses it

| Tool | What it does |
| --- | --- |
| `subvault:vault` | Saves a fact, decision, action item, or person. |
| `subvault:remember` | Pulls relevant records for the current conversation. |
| `subvault:corpus_stats` | Returns counts of what is stored. Numbers only, never content. |

Your AI decides when to call them. You just say *"vault this"* or ask a question that needs context.

## Works with

Claude Desktop, Claude Code, Cursor, VS Code + Copilot, Windsurf. Any other client that speaks [MCP](https://modelcontextprotocol.io) should work.

## Docs

Full documentation at [subvault.ai/docs](https://subvault.ai/docs): setup, tool reference, troubleshooting.

Security disclosures: [SECURITY.md](SECURITY.md) or <info@subvault.ai>.

## Working on this repo

The `docs/*.html` pages are generated from per-page sources in `docs/_src/` plus the shared layout in `tools/build-docs.py`. After editing any source file, regenerate:

```bash
python3 tools/build-docs.py
```

`python3 tools/build-docs.py --check` exits non-zero if checked-in HTML is stale, which is useful in CI.

Setup script tests:

```bash
bash tools/test-setup.sh ./setup.sh
```

Both run on the Python 3 standard library only, with no external dependencies.

## License

[MIT](LICENSE).
