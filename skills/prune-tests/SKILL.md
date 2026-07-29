---
name: prune-tests
description: Delete tests that do not uniquely protect a durable contract, confirmed regression, or critical invariant.
---

# Prune Tests

Reduce test-suite cost without weakening meaningful protection.

## Keep

Keep a test only when it uniquely protects:

- A durable contract through a stable seam.
- A confirmed regression that remains possible.
- A critical security, permissions, compatibility, concurrency, migration, protocol, or data-loss invariant.

A seam may be an API, CLI, module interface, protocol, workflow, or artifact boundary.

## Workflow

1. Establish a green baseline.
2. Group tests by the obligation they protect.
3. Check history before removing likely regression coverage.
4. Classify each group as `keep`, `consolidate`, `delete`, or `investigate`.
5. Propose deletions and get confirmation.
6. Delete in small batches; do not alter production behavior.
7. Run focused checks and the full suite.

Delete tests that cover private mechanics, duplicate stronger coverage, enumerate equivalent cases, preserve dead behavior, test framework guarantees, or depend on structure rather than behavior.

If no unique, durable obligation can be named, propose deletion.

Report tests, fixtures, runtime, and lines removed. Do not optimize for coverage percentage.
