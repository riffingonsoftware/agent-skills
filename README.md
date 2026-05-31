# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- Tool-specific wrappers should stay thin and adapt only metadata, packaging, or invocation style.

## Current Skills

- `init-or-refactor-agents-md` initializes or compresses agent instruction files into one short `AGENTS.md` that coding agents are likely to follow. It emphasizes repro-first, behavior-only tests for confirmed bugs and avoids speculative test creation.

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

## Repository Policy

- Keep behavioral logic in `skills/*/SKILL.md`.
- Do not hand-edit downstream wrappers to change workflow semantics.
- If a tool needs a wrapper, generate or derive it from the canonical skill rather than maintaining a forked copy.
