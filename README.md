# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- Compatibility wrappers compose upstream skills without copying them, keeping upstream updates independent.

## Current Skills

- `codex-grill-with-docs` runs Matt Pocock's `grill-with-docs` with GPT-calibrated question selection and stopping criteria.
- `init-or-refactor-agents-md` initializes or compresses agent instruction files into one short `AGENTS.md` that coding agents are likely to follow. It emphasizes repro-first, behavior-only tests for confirmed bugs and avoids speculative test creation.
- `prune-tests` deletes tests that do not uniquely protect a durable contract, confirmed regression, or critical invariant.
- `ship` scans local changes for sensitive data, splits them into logical commits, and pushes.

`codex-grill-with-docs` requires the independently installed [Matt Pocock skills](https://github.com/mattpocock/skills). It contains only the compatibility directions; the upstream workflow remains independently updateable.

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
