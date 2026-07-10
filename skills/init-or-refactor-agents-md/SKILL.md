---
name: init-or-refactor-agents-md
description: Create or compress repo-local agent instructions into a short canonical AGENTS.md with a CLAUDE.md pointer.
---

# Init or Refactor AGENTS.md

Produce one short, high-signal canonical `AGENTS.md`.

## Workflow

1. Read `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `.cursorrules`, and similar repo-local instruction files.
2. Present conflicting instructions with their sources and ask which wins. Flag conflicts with the target policies below, especially speculative or implementation-detail tests, unapproved dependencies, blind preservation of local patterns, and rejection of justified rewrites.
3. Prune before drafting, in order: delete vague, obvious, generic, or duplicate advice; collapse repeats; remove tool-wrapper noise and future ceremony; remove speculative, private, or vanity tests and rules that preserve bad structure; retain repo-specific, safety-critical, or repeatedly violated rules. Prefer one bullet to a new section. Group removals as `delete`, `yagni`, `tool-noise`, `test-theater`, or `structure`.
4. Summarize existing branch, commit, PR, review, release, and deploy rules. Ask the user to confirm direct-default, branch/PR, or another workflow; recommend a clear repo convention. For direct-default or branch/PR, require scoped logical commits and early, frequent pushes. For another workflow, preserve only what the user supplies.
5. Draft `AGENTS.md` with only a one-line project description, non-obvious commands, the confirmed Git workflow, the target policies, and critical safety or approval rules. Use terse bullets and no linked detail docs.
6. Present the sources, conflicts, Git choice, proposed `AGENTS.md`, and tagged removals. Get confirmation before writing.
7. Write `AGENTS.md`. Ensure `CLAUDE.md` exists and its entire contents are exactly:

   ```md
   @AGENTS.md
   ```

   Create it if absent. Create no other tool-specific file unless explicitly asked.

## Target policies

- For a confirmed bug, when practical capture a focused failing behavior-level repro through a public interface, fix it, and retain the regression test. For agreed user-visible behavior, define acceptance criteria and, when a suitable harness exists, add or update one focused public-interface acceptance test before or with implementation.
- Otherwise use existing checks and focused manual verification. Avoid unit-test-first TDD, private, speculative, or unagreed tests, broad fixture-heavy assertions, and coverage-driven tests; mock only system boundaries. Use Given/When/Then phrasing only when it clarifies a scenario, and do not add BDD/Gherkin/Cucumber tooling unless explicitly asked. Refactor after the fix is verified.
- Before adding code, use the first rung that works: remove the need; use existing repo code, config, tooling, or workflow; use standard-library or native features; use an installed dependency; write small local code; only then add an abstraction, file, service, config surface, or dependency. Stop there; prefer fewer files and explicit, boring code.
- Never simplify away security, trust-boundary validation, data-loss protection, accessibility, observability, or repo-specific safeguards.
- Ask before adding a dependency; prefer the standard library, installed dependencies, or small local code. Evaluate maintenance, license, docs, security, and transitive dependencies before proposing one.
- Work in vertical slices and keep changes reviewable. Simplify touched code. Follow local patterns only when sound and intentional. Prefer the correct fix over the smallest patch; rewrite bad structure in reviewable slices.
- Ask before risky or destructive changes, and run relevant checks before finishing.
