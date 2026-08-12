# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.

## Current Skills

- `handoff` creates a self-contained prompt for continuing work in a new agent session and saves it in a temporary directory.
- `init-or-refactor-agents-md` initializes or compresses agent instruction files into one short `AGENTS.md` that coding agents are likely to follow. It emphasizes repro-first, behavior-only tests for confirmed bugs and avoids speculative test creation.
- `prune-tests` deletes tests that do not uniquely protect a durable contract, confirmed regression, or critical invariant.
- `ship` scans local changes for sensitive data, splits them into logical commits, and pushes.

## Tool Requirements

- Gemini CLI should be configured to load `AGENTS.md` as a project context file.
- The official Gemini CLI `context.fileName` setting accepts a string or an array. To prefer `AGENTS.md` while retaining existing `GEMINI.md` support, use:

```json
{
  "context": {
    "fileName": ["AGENTS.md", "GEMINI.md"]
  }
}
```
