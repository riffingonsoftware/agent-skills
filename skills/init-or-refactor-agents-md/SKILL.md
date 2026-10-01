---
name: init-or-refactor-agents-md
description: Create or compress repo-local agent instructions into a short canonical AGENTS.md.
---

# Init or refactor AGENTS.md

Produce one short, high-signal canonical `AGENTS.md`.

## Workflow

1. Read `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `.cursorrules`, and similar repo-local instruction files.
2. Present conflicting instructions with their sources and ask which wins. Flag conflicts with the target policies below, especially speculative, implementation-detail, or fixture-heavy test matrices, unapproved dependencies, blind preservation of local patterns, and rejection of justified rewrites.
3. Prune before drafting, in order: delete vague, obvious, generic, or duplicate advice; collapse repeats; remove tool-wrapper noise and future ceremony; remove speculative, private, branch-matrix, fixture-heavy, or vanity tests and rules that preserve bad structure; retain repo-specific, safety-critical, or repeatedly violated rules. Prefer one bullet to a new section. Group removals as `delete`, `yagni`, `tool-noise`, `test-theater`, or `structure`.
4. Summarize existing branch, commit, PR, review, release, and deploy rules. Ask the user to confirm direct-default (work on `main` or `trunk`), branch/PR (use a focused branch and open or update its PR), or another workflow; recommend a clear repo convention. For direct-default or branch/PR, require scoped logical commits and early, frequent pushes; for branch/PR, open or update the PR after the first useful slice. Never rewrite shared history without approval. For another workflow, preserve only what the user supplies.
5. Draft `AGENTS.md` with only a one-line project description, non-obvious commands, the confirmed Git workflow, the target policies unless global instructions already give them to every agent in the repo, and critical safety or approval rules. Use terse bullets and no linked detail docs unless explicitly asked.
6. Present the sources, conflicts, Git choice, proposed `AGENTS.md`, and tagged removals. Get confirmation before writing.
7. Write `AGENTS.md`, then delete the other contributing instruction files after consolidating their retained instructions. Create no tool-specific instruction files unless explicitly asked.

## Target policies

- Most tests are debt. Keep or add one only if it would catch a realistic break that nothing else catches: a confirmed bug that could recur, a contract others rely on through a public interface, or a critical invariant (security, permissions, compatibility, concurrency, migrations, protocols, data loss).
- Verify every change with the cheapest check that shows it works: a run, a scratch script, a manual check. For a bug, reproduce it before fixing it when practical.
- Throw most of those checks away. When one meets the bar above, promote it instead of writing a new test: one deterministic scenario through the public interface, added to an existing test where one fits. A promoted regression check must still fail without the fix.
- Never test private helpers, framework or type guarantees, equivalent cases, or the code restated as assertions. Mock only at system boundaries.
- When you change behavior or touch tests, delete the ones below the bar and say why. Check history when intent is unclear.
- Never delete or weaken a failing test to get your change through. Find out why it fails.
- No unit-test-first TDD, coverage targets, test-only APIs, fixture scaffolding, or BDD tooling unless asked.
- Before adding code, use the first rung that works: remove the need; use existing repo code, config, tooling, or workflow; use standard-library or native features; use an installed dependency; write small local code; only then add an abstraction, file, service, config surface, or dependency. Stop there; prefer fewer files and explicit, boring code.
- Never simplify away security, trust-boundary validation, data-loss protection, accessibility, observability, or repo-specific safeguards.
- Before adding a dependency, compare credible alternatives, including adding none. Assess fit, license, maintenance, and security using current sources, including vulnerabilities, provenance, and transitive dependencies. Consider the code it replaces and the obligations it adds. Present a concise recommendation with sources and risks, then ask for approval.
- Work in vertical slices and keep changes reviewable. Simplify touched code. Follow local patterns only when sound and intentional. Prefer the correct fix over the smallest patch; explain the tradeoff and rewrite bad structure in reviewable slices.
- Ask before risky or destructive changes, and run relevant checks before finishing.
