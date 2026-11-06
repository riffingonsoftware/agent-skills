# Agent skills

Portable, tool-agnostic agent skills. `skills/*/SKILL.md` is the canonical source of truth.

## Git workflow

- Work directly on `trunk`; commit and push early and often, one coherent change per commit.

## Rules

- Keep skills short and imperative. Apply `write-for-agents` whenever you edit a skill,
  `AGENTS.md`, or `CLAUDE.md`.
- When adding, renaming, or removing a skill, update `skills/.devin-plugin/plugin.json`, the skill links
  in `riffingonsoftware/dotfiles`, and the Windows install list in `riffingonsoftware/starfleet`. `cz apply` stops while this
  checkout has uncommitted changes.
- Preserve attribution for forked skills (see README).
- No build, tests, or dependencies. A skill may ship scripts that run on Python 3.9, macOS's system Python, with
  only the standard library. Ask before adding any other tooling.
