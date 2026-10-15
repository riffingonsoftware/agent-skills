# Agent skills

Portable, tool-agnostic agent skills. `skills/*/SKILL.md` is the canonical source of truth.

## Git workflow

- Work directly on `trunk`; commit and push early and often, one coherent change per commit.

## Rules

- Keep skills short and imperative. Apply `write-for-agents` whenever you edit a skill,
  `AGENTS.md`, or `CLAUDE.md`.
- When adding, renaming, or removing a skill, update `skills/.devin-plugin/plugin.json` and the install lists in
  `~/projects/config`. That repo's bootstrap installs these skills and stops while this checkout has uncommitted
  changes.
- Preserve attribution for forked skills (see README).
- Markdown-only repo: no build, tests, or dependencies. Ask before adding any tooling.
