---
name: init-or-refactor-agents-md
description: Create or compress repo-local agent instructions into a short canonical AGENTS.md with a CLAUDE.md pointer.
---

# Init or Refactor AGENTS.md

Produce one short, high-signal canonical `AGENTS.md`.

## Ownership

`setup-matt-pocock-skills` owns the `## Agent skills` block and `docs/agents/*`, including issue-tracker configuration. Preserve an existing block verbatim in the canonical `AGENTS.md` and leave its referenced files untouched. Do not create, edit, summarize, or remove this configuration; its absence is not a gap to fill.

## Workflow

1. Read `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `.cursorrules`, and similar repo-local instruction files.
2. Present conflicting instructions with their sources and ask which wins. Flag conflicts with the target policies below, especially speculative, implementation-detail, or fixture-heavy test matrices, unapproved dependencies, blind preservation of local patterns, and rejection of justified rewrites.
3. Prune before drafting, in order: delete vague, obvious, generic, or duplicate advice; collapse repeats; remove tool-wrapper noise and future ceremony; remove speculative, private, branch-matrix, fixture-heavy, or vanity tests and rules that preserve bad structure; retain repo-specific, safety-critical, or repeatedly violated rules. Prefer one bullet to a new section. Group removals as `delete`, `yagni`, `tool-noise`, `test-theater`, or `structure`.
4. Summarize existing branch, commit, PR, review, release, and deploy rules. Ask the user to confirm direct-default (work on `main` or `trunk`), branch/PR (use a focused branch and open or update its PR), or another workflow; recommend a clear repo convention. For direct-default or branch/PR, require scoped logical commits and early, frequent pushes; for branch/PR, open or update the PR after the first useful slice. Never rewrite shared history without approval. For another workflow, preserve only what the user supplies.
5. Draft `AGENTS.md` with only a one-line project description, non-obvious commands, the confirmed Git workflow, the target policies, critical safety or approval rules, and any preserved `## Agent skills` block. Use terse bullets and no other linked detail docs unless explicitly asked.
6. Present the sources, conflicts, Git choice, proposed `AGENTS.md`, and tagged removals. Get confirmation before writing.
7. Write `AGENTS.md`. Ensure `CLAUDE.md` exists and its entire contents are exactly:

   ```md
   @AGENTS.md
   ```

   Create it if absent. Create no other tool-specific file unless explicitly asked.

## Target policies

- Tests are executable acceptance criteria, not a design method. For agreed behavior or a confirmed bug, prefer one smallest scenario through a public interface or artifact boundary; extend an existing scenario first. For bugs, prove the failure when practical, then retain the regression. Stop once broken and fixed behavior are distinguished.
- Otherwise use existing checks or focused manual verification. Do not use unit-test-first TDD or test private mechanics, speculative cases, equivalent branches, or coverage targets; avoid test-only APIs, fixture scaffolding, and mocks except at system boundaries. Add BDD tooling only when explicitly asked.
- Before adding code, use the first rung that works: remove the need; use existing repo code, config, tooling, or workflow; use standard-library or native features; use an installed dependency; write small local code; only then add an abstraction, file, service, config surface, or dependency. Stop there; prefer fewer files and explicit, boring code.
- Never simplify away security, trust-boundary validation, data-loss protection, accessibility, observability, or repo-specific safeguards.
- Ask before adding a dependency; prefer the standard library, installed dependencies, or small local code. Evaluate maintenance, license, docs, security, and transitive dependencies before proposing one.
- Work in vertical slices and keep changes reviewable. Simplify touched code. Follow local patterns only when sound and intentional. Prefer the correct fix over the smallest patch; explain the tradeoff and rewrite bad structure in reviewable slices.
- Ask before risky or destructive changes, and run relevant checks before finishing.
