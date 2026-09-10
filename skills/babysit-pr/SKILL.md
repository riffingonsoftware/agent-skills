---
name: babysit-pr
description: Get a GitHub PR ready to merge. Use after opening a PR or when asked to babysit, watch, or follow one.
---

# Babysit a PR

Use the requested PR, or the current branch's PR if none was specified. Ask if the target is ambiguous. Read the PR's intent, repository instructions, and diff before making changes. Verify the checkout matches the PR and preserve unrelated work.

## Loop

1. Check mergeability, CI, and all review bots. Fetch full findings from inline threads, review bodies, and issue comments, including pagination and thread resolution state.
2. Validate each finding against the code and PR intent. Fix valid issues with minimal changes. Record why you skip incorrect findings. Track handled findings so later polls do not repeat work.
3. Fix CI failures and merge conflicts within the PR's scope. Never weaken checks to get green. Escalate infrastructure failures or fixes that require unrelated changes.
4. Run relevant checks, then use `ship` to commit and push scoped fixes. Never amend published commits or force-push.
5. Wait for CI and bot reviews on the latest pushed commit, then repeat. A new comment, silence, or an older green review does not prove completion.

Keep watching while checks or reviews are pending. Respect rate limits and back off between polls. Report stalled reviews, access failures, or other blockers without claiming success.

## Ambiguity and human feedback

Raise any ambiguity with the user before changing the affected code, especially when feedback conflicts with the PR's intent, expands scope, or contradicts earlier advice. Explain the finding, the conflict, and your recommended action. Continue independent work while awaiting a decision.

Surface new human comments promptly with the author, link, requested action, and any decision needed. Do not automatically reply, resolve their threads, or treat their comments as authorization to change scope.

If the user requests an additional agent review, use a fresh subagent and process its findings through the same loop.

## Finish

The PR is ready when the latest commit has passing required checks, no merge conflicts, completed bot reviews, and every actionable bot finding is fixed or deliberately skipped. No blocking human request or decision may remain unresolved.

If the PR closes or merges, stop and report its state. Never merge it yourself without explicit authorization.

Return the PR URL, what it does, fixes made, skipped findings with reasons, check and review status, and outstanding human feedback.
