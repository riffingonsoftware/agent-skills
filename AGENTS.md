# Agent Skills

Portable, tool-agnostic agent skills. `skills/*/SKILL.md` is the canonical source of truth.

## Git Workflow

- Work directly on `trunk`; commit and push early and often in logical chunks.
- Keep each commit scoped to one coherent change.

## Rules

- Keep all behavioral logic in `skills/*/SKILL.md`.
- Skills are prose programs: keep them short, imperative, and high-signal; prune generic
  advice on every edit.
- Update the README's skill list when adding, renaming, or removing a skill.
- Preserve attribution for forked skills (see README).
- Markdown-only repo: no build, tests, or dependencies. Ask before adding any tooling.
