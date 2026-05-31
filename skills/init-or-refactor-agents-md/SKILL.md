---
name: init-or-refactor-agents-md
description: Create or compress project agent instructions into one short AGENTS.md with pragmatic repro-first testing guidance.
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
   - Bug fixes should use repro-first testing when practical: capture the confirmed failure with a failing behavior test, fix it, then keep the test as regression coverage. Flag instructions that encourage implementation-detail tests, speculative tests for planned behavior, vanity coverage targets, or tests not tied to a confirmed failure.
   - Flag instructions that allow adding dependencies without user approval.
   - Flag instructions that require preserving local patterns when they are unsound, accidental, or undocumented.
   - Flag instructions that discourage necessary rewrites solely because they are larger.

3. Draft one short `AGENTS.md`.
   Keep only:
   - one-line project description
   - non-obvious commands
   - hard rules, including repro-first bug testing
   - simplification discipline, quality bar, and rewrite guidance
   - dependency policy
   - critical safety or approval rules

4. Delete fluff.
   Remove vague, duplicate, or obvious advice.

5. Write terse rules.
   - Prefer bullets over prose.
   - Prefer rules over explanations.
   - State testing expectations briefly and operationally.
   - State dependency approval requirements explicitly.
   - State when to challenge local patterns and consider rewrites.
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

- For confirmed bugs, capture the failure with a failing behavior-level repro test when practical, then fix it and keep the test as a regression test.
- Do not write tests for planned behavior, predicted risk, implementation details, coverage targets, or test-count goals.
- For non-bug changes, use existing checks and focused manual verification unless the user explicitly asks for tests.
- Work in vertical slices: one behavior at a time.
- Test only observable behavior through public interfaces; never private internals.
- Prefer a focused bug repro over broad assertions or fixture-heavy tests.
- Mock only system boundaries.
- Refactor only after the fix is verified: simplify touched code without changing behavior.
- Ask before adding dependencies; prefer stdlib, existing deps, or small local code.
- Before proposing a dependency, check maintenance, license, docs, security, and transitive deps.
- Keep diffs small.
- Proactively simplify touched code; prefer explicit over clever.
- Follow existing patterns only when they are sound and intentional; proactively challenge them when they conflict with best practices or project goals.
- Prefer the correct fix over the smallest patch; propose or perform rewrites when local structure is the problem.
- Do not avoid necessary redesign because it is larger; explain the tradeoff and proceed in reviewable slices.
- Ask before risky or destructive changes.
- Run relevant checks before finishing.
```

## Output

Present:

1. Sources gathered
2. Conflicts found
3. Proposed `AGENTS.md`
4. Items removed
