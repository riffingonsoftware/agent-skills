---
name: open-pr
description: Deslop and review a change, unslop its prose, open a pull request, and babysit it to merge readiness.
---

# Open a PR

Prepare a narrow, landable pull request, open it ready for review, and babysit it to merge readiness. Return its URL and final status.

## Worktree

Read the repository instructions and determine the intended base, branch policy, PR tooling, and commit and PR conventions. Where the repository sets a commit convention or PR template, follow it instead of the ones below. Use the current worktree when its changes are the PR, creating the intended branch there if needed. Otherwise prefer an isolated worktree from the base branch. Never patch out, reset, discard, or overwrite user work without approval; stop and ask when the worktree mixes the PR's changes with unrelated work or is snarled.

Inspect the status, staged and unstaged diffs, every untracked file, branch ancestry, commit range, and remote state. Verify that every change belongs to the requested PR. Stop on ambiguous scope, merge conflicts, sensitive data, missing permission, or an unsafe history rewrite.

## Commits

Plan small, ordered commits that tell the story. Each commit should be independently reviewable and landable. Amend when a fix belongs in a just-made, unshared commit; create a new commit when it is separable. Ask before rebasing shared work or force-pushing.

Run `deslop` on the exact intended diff before each commit. Run `no-comments` on the complete PR diff before review. Replan and rerun `deslop` on changes produced by accepted comment findings.

Write commit subjects using Conventional Commits. Name the changed area as the scope. Keep the subject short and imperative, name a real symbol when useful, and omit the trailing period. A commit body explains facts not present in its subject; it never restates the subject. Apply `unslop` to every subject and body without changing the Conventional Commit syntax.

Use `ship` for each commit and push, naming the changes that belong in that commit.

## Pull request

Also use Conventional Commit format for the PR title. Keep articles, use one plain word for each action, and avoid `-ing` when a direct verb works. Apply `unslop` to the title without changing that syntax.

Open with a paragraph, without a heading, that states the problem, with a concrete failing case when one exists, and what the change does about it. Name the key symbols. Add a sentence on what is out of scope or on both sides of a rename when that matters. Don't walk through the diff.

Then add these sections in order:

- `## Tradeoffs`. State real choices, rejected alternatives, known limits, and what could break. Say what stays the same when a reviewer might wonder. If the base branch fails without the fix, name the continuing cost. Drop this section when there is nothing to say.
- `## Verification`. State how you ran each check and its rigor. Name the real path, such as the CLI command, the UI flow, or the targeted tests. State the outcome of each check, not only the command name.

After these sections, attach screenshots or videos when they prove a claim. Do not add `## Summary` or `## Test plan` boilerplate. Apply `unslop` to the completed description.

Prefer five narrow PRs to one large PR. Use the repository's configured stacking tool, and keep the ordered stack visible to reviewers. Branch from the base only for independent work. Rebase on the latest base before substantial stack work.

Open every PR ready, never as a draft. Cloud-agent PR tools default to draft, so set `draft: false` on every PR creation call. If a PR still opens as a draft, run the host's ready command, such as `gh pr ready <number>`. Run `gh pr view <number>` before you refer to PR status.

After opening each PR, invoke `babysit-pr` for that PR and carry it through to readiness or a reported blocker. Do this for every PR, including each PR in a stack. Opening the PR alone does not complete this workflow.

A subagent that opens a PR runs `deslop` and `no-comments`, then also babysits it. Relay human feedback and ambiguous findings to the parent for the user. Return the PR URL and final status.
