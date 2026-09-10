# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.

## Current Skills

- `babysit-pr` watches CI and all review bots until a PR is ready to merge, escalating ambiguity and human feedback.
- `deslop` removes AI-generated code slop from a branch diff while preserving behavior.
- `init-or-refactor-agents-md` initializes or compresses agent instruction files into one short `AGENTS.md` that coding agents are likely to follow. It emphasizes repro-first, behavior-only tests for confirmed bugs and avoids speculative test creation.
- `no-comments` audits edited code for comments to delete and fixes accepted findings.
- `open-pr` cleans and organizes a change, opens a pull request, and babysits it to merge readiness.
- `prune-tests` deletes tests that do not uniquely protect a durable contract, confirmed regression, or critical invariant.
- `ship` scans local changes for sensitive data, splits them into logical commits, and pushes.
- `unslop` removes AI tells from prose and adds human voice.

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
