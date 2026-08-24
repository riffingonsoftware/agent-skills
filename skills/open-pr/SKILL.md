---
name: open-pr
description: Deslop and review a change, unslop its prose, and open a ready pull request.
disable-model-invocation: true
---

# Open a PR

Prepare a narrow, landable pull request, open it ready for review, and return its URL. Opening a PR does not start babysitting it.

## Worktree

Read the repository instructions and determine the intended base, branch policy, and PR tooling. Prefer an isolated worktree from the base branch. Use the current worktree only when it contains the intended branch and no unrelated work. Never patch out, reset, discard, or overwrite user work without approval; stop and ask when the worktree is dirty or snarled.

Inspect the status, staged and unstaged diffs, every untracked file, branch ancestry, commit range, and remote state. Verify that every change belongs to the requested PR. Stop on ambiguous scope, merge conflicts, sensitive data, missing permission, or an unsafe history rewrite.

## Commits

Plan small, ordered commits that tell the story. Each commit should be independently reviewable and landable. Amend when a fix belongs in a just-made, unshared commit; create a new commit when it is separable. Ask before rebasing shared work or force-pushing.

Run `deslop` on the exact intended diff before each commit. Run `no-comments` on the complete PR diff before review. Replan and rerun `deslop` on changes produced by accepted comment findings.

Write commit subjects using Conventional Commits. Name the changed area as the scope. Keep the subject short and imperative, name a real symbol when useful, and omit the trailing period. A commit body explains facts not present in its subject; it never restates the subject. Apply `unslop` to every subject and body without changing the Conventional Commit syntax.

Use `ship` for each commit and push. Ask before setting an upstream. Recheck status between commits and never include unrelated work.

## Pull request

Also use Conventional Commit format for the PR title. Keep articles, use one plain word for each action, and avoid `-ing` when a direct verb works. Apply `unslop` to the title without changing that syntax.

Use these sections in order. Drop a section when it is empty.

- `## Why`. State the intent and why this approach fits.
- `## Scope`. State facts from the diff. Name real symbols and paths. Name both sides of a rename or retarget. State what is in and out when the boundary matters.
- `## Tradeoffs`. State real choices only. Skip this section when there are none.
- `## Blast Radius`. State who and what the change touches. Explain why the change is safe or risky. If main is red without the fix, name the continuing cost.
- `## Verification`. State how you ran each check and its rigor. Name the real path, such as control-cli, control-ui, or the targeted tests. State the outcome of each check, not only the command name.

After these sections, attach screenshots or videos when they prove a claim. Do not add `## Summary` or `## Test plan` boilerplate. A commit body does not restate its subject. Apply `unslop` to the completed description.

**Size and stacks.** Prefer five narrow PRs to one large PR. Use the repository's configured stacking tool, and keep the ordered stack visible to reviewers. Branch from the base only for independent work. Rebase on the latest base before substantial stack work.

**Readiness.** Open every PR ready, never as a draft. Cloud-agent PR tools default to draft, so set `draft: false` on every PR creation call. If a PR still opens as a draft, run the host's ready command, such as `gh pr ready <number>`. Run `gh pr view <number>` before you refer to PR status.

**Babysit.** Opening a PR does not start a babysit. Post the URL and keep building. Finish the phase or stack first. Run a separate babysit pass only when the user asks for one after the whole stack exists. A babysit for each new PR stalls the build and spends checks on commits that later waves restart. Push back when feedback drifts from intent.

A subagent that opens a PR runs `/deslop` and `/no-comments`. It returns the URL and does not babysit. Return to the parent.
