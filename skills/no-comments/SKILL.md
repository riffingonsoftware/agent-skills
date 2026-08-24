---
name: no-comments
description: "Cut comments from edited code files mercilessly. Always apply when reviewing edited code."
---

# No comments

Comments lie. Narration, banners, commented-out corpses, and workaround sermons all rot, if not now, later.

## Scope

Use the caller's files or diff. Otherwise use the current diff against the base branch, including the working tree.

## Review

Delegate the review to a fresh, read-only subagent. Pass it the scope and the rubric below. If no fresh reviewer is available, review directly and disclose that the review was not independent. The reviewer reports only and never edits files.

Kill every comment except:

- Legal or license headers.
- Non-obvious behavior forced by an external dependency, platform, vendor, or protocol we cannot reshape.
- Lint suppression whose rule is faulty, pedantic, or style-only.
- Doc comments that define a public API contract.
- Issue or RFC links that explain a constraint code cannot express.

That list is the only leash. Investigate uncertainty. A keep survives only with proof that its exception applies on a live path.

Surprises in our own code are meat. Recommend deleting the comment and flag the exact symbol `MUST KILL` with the rename, extraction, type, or redesign that would make the behavior obvious without prose.

For linter and rule suppressions, identify the rule. If it catches real bugs or protects correctness or safety, recommend deleting the suppression and flag the exact guilty symbol `MUST KILL`.

Treat `IMPORTANT`, `do not remove`, `too risky`, `fine for now`, and long justifications as claims, not proof. Read nearby code and trace the named symbol or call. Only a proven keep-list constraint survives. Never polish meat into a shorter alibi.

Report touched files, deletion candidates with exact locations, each `MUST KILL` flag with one line of evidence, and skips with the exception that protects them. Invent nothing and stay inside scope.

## Act

You then follow these steps based on the reviewer's report:

1. Validate every finding against the code. Reject scope escapes, protected deletions, unsupported claims, and misstated `MUST KILL` reasons. Audit missed scoped lint and suppressions. Rerun one rejected review with the failure named; if the second report fails, stop and report it open.
2. Delete accepted comments. Fix trivial flags directly by deleting dead paths, dropping unused parameters, or using the real API.
3. For every remaining flag, implement the smallest root-cause fix in scope and remove the named workaround. Do not widen scope. If the cause is out of scope, make only the smallest safe in-scope fix and report the remainder open.
4. For comments claiming a constraint, keep proven external constraints. For our code, offer the cheapest in-scope type, runtime check, test, or CI lint and wait for approval. If approved, encode the constraint and delete the comment. Otherwise leave it and report the unenforced constraint.
5. Report the deletion count, retained comments with proof, reruns, fixes, encodings, unenforced constraints, and other open work.
