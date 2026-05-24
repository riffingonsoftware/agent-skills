---
name: init-or-refactor-agents-md
description: Create or compress project agent instructions into one short AGENTS.md with pragmatic behavior-first testing guidance.
---

# Init Or Refactor AGENTS.md

Goal: produce one short, high-signal `AGENTS.md` that agents will actually follow. Prefer one canonical file.

## Workflow

1. Read existing instruction files:
   - `AGENTS.md`
   - `CLAUDE.md`
   - `CODEX.md`
   - `.cursorrules`
   - similar repo-local agent instruction files

2. Show conflicts.
   - If instructions disagree, show both and ask which one wins.
   - Behavior-changing work should use TDD by default. Flag instructions that encourage implementation-detail tests, vanity coverage targets, or tests without clear behavioral value.

3. Draft one short `AGENTS.md`.
   Keep only:
   - one-line project description
   - non-obvious commands
   - hard rules, including behavior-first testing
   - simplification discipline (refactor step + proactive cleanup)
   - dependency policy
   - critical safety or approval rules

4. Delete fluff.
   Remove vague, duplicate, or obvious advice.

5. Write terse rules.
   - Prefer bullets over prose.
   - Prefer rules over explanations.
   - State testing expectations briefly and operationally.
   - Do not create linked docs unless explicitly asked.
   - Do not create tool-specific files unless needed.
   - If `CLAUDE.md` is needed, its entire contents must be exactly `@AGENTS.md`.

Ask for confirmation before writing files.

## Example `AGENTS.md`

```md
# Project Name

## Commands

- Build: `...`
- Test: `...`
- Lint: `...`

## Rules

- Use TDD for behavior changes: failing behavior test -> minimal fix -> refactor.
- Do not add tests for their own sake; skip docs-only, formatting-only, and mechanical changes unless risk justifies them.
- Work in vertical slices: one behavior at a time.
- Test through public interfaces; don’t test private internals.
- Prefer focused behavioral proof over coverage targets or test-count goals.
- Mock only system boundaries.
- Refactor only when green: simplify touched code without changing behavior.
- Prefer stdlib and existing deps.
- Keep diffs small.
- Proactively simplify touched code; prefer explicit over clever.
- Ask before risky or destructive changes.
- Run relevant checks before finishing.
```

## Output

Present:

1. Sources gathered
2. Conflicts found
3. Proposed `AGENTS.md`
4. Items removed
