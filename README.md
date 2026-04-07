# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- Tool-specific wrappers should stay thin and adapt only metadata, packaging, or invocation style.

## Current Skills

- `init-or-refactor-agents-md` initializes or refactors `AGENTS.md` and related agent-instruction files into a progressive-disclosure layout.

## Provenance

- `init-or-refactor-agents-md` draws its progressive-disclosure `AGENTS.md` refactor workflow from Matt Pocock's article, [A Complete Guide To AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md). This repository was checked against that article on 2026-04-07.
- Appendix seed docs embedded by `init-or-refactor-agents-md` are local adapted copies of files from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/tdd). They were originally retrieved on 2026-03-26 and rechecked against upstream on 2026-04-07.
- The `deep modules` concept cited by the seed docs originates with John Ousterhout's [A Philosophy of Software Design](https://www.web.stanford.edu/~ouster/cgi-bin/aposd.php). That conceptual attribution was rechecked on 2026-04-07.

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
