# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- Tool-specific wrappers should stay thin and adapt only metadata, packaging, or invocation style.

## Current Skills

- `init-or-refactor-agents-md` initializes or refactors `AGENTS.md` and related agent-instruction files into a progressive-disclosure layout.

## Repository Policy

- Keep behavioral logic in `skills/*/SKILL.md`.
- Do not hand-edit downstream wrappers to change workflow semantics.
- If a tool needs a wrapper, generate or derive it from the canonical skill rather than maintaining a forked copy.
