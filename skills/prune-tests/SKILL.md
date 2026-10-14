---
name: prune-tests
description: Delete tests that do not uniquely protect a contract, confirmed regression, or critical invariant.
---

# Prune tests

Reduce test-suite cost without weakening meaningful protection.

## Keep

Keep a test only when it uniquely protects:

- A contract callers rely on through a public interface.
- A confirmed regression that remains possible.
- A critical security, permissions, compatibility, concurrency, migration, protocol, or data-loss invariant.

A public interface may be an API, CLI, module interface, protocol, workflow, or artifact boundary. Tests that cover private mechanics, duplicate stronger coverage, enumerate equivalent cases, preserve dead behavior, test framework or type guarantees, restate the code as assertions, or depend on structure rather than behavior do not qualify. Coverage percentage is not a reason to keep a test.

## Scope

Default to the whole suite. When a caller scopes the run to a diff, consider only tests the diff adds or changes and tests that cover code it changes or removes.

## Workflow

1. Run the in-scope tests and record their runtime. If any fail, stop and report the failures.
2. Group every in-scope test by what it protects under Keep. Put tests that protect nothing in one group.
3. Investigate each group whose protection is unclear. Search the history for the fix that added it, read the code it covers and that code's callers, and temporarily break the behavior it asserts to see whether another test also fails. Treat a regression as confirmed only if the history shows the fix or the test fails with the change's fix reverted.
4. Classify each group as `keep`, `consolidate` (merge into one test with the same protection), or `delete`. Delete a group when you cannot name what it uniquely protects. Finish when every group has a class.
5. Apply the changes one group at a time; do not alter production behavior.
6. Rerun the in-scope tests and every test that used a fixture you removed. Finish when they pass.

Report the tests, fixtures, and lines removed, the runtime saved, and the reason for each deletion and consolidation.
