---
name: review
description: Review a PR, branch, commit, or uncommitted change. Use when asked to review one or whether anything jumps out.
---

# Review

Review adversarially. Try to break the change and its chosen approach, ask whether a smaller change would do, and take the goal as given. Look hardest at compatibility, data loss, observability gaps, partial failure, races, resource exhaustion (stored data, files, or caches with no cleanup; input size, work, or request rate a caller can drive without limit), security, stale state, unsafe retries or rollback, and violations of documented conventions.

Only in changes the user or their agents wrote, flag each test the change adds or edits that fails the Keep bar in `prune-tests`, unless the repository's instructions require it. Those are uncommitted changes, commits by the user's git identity, and PRs that the user's `gh` login opened, or for Devin, requested. Never suggest that anyone else delete a test.

If you wrote or changed the target in this session, hand this skill and the target to a fresh subagent and relay its report.

Don't comment on, approve, or request changes on a PR; draft any comment for the user, with the line to put it on.

## Snapshot

Read and run everything in a snapshot of the target's head, never in the user's checkout. In the checkout, run only the commands below; even `git status` and `git diff` can rewrite its index.

1. Clone the checkout into a new temporary directory with `git clone --shared --no-checkout`. Resolve refs to SHAs in the checkout with `git rev-parse`, because the snapshot's `origin/<branch>` is the checkout's local branch.
2. Check out the head:
   - For a PR, fetch `pull/<number>/head` from the PR's repository URL and confirm it matches `headRefOid`. Pass the PR URL to every `gh pr` command, because `gh` can't find the repository from the snapshot. If the checkout isn't a clone of that repository, clone the repository instead.
   - For uncommitted changes, check out `HEAD`, then list the changed paths in the checkout with `git diff-index --name-only HEAD` and `git ls-files -o --exclude-standard`. Copy each into the snapshot, keeping symlinks as links, or delete it there if the checkout no longer has it.
   - For a merge commit, read the change with `git show --first-parent`.
3. Run the repository's focused checks, rerun any checks you were told passed, and reproduce suspected defects with small throwaway commands; a reproduced failure outranks a suspicion. Install dependencies only with the repository's locked install command, such as `npm ci`. If a check needs ignored config such as `.env`, list it as unverified instead of copying the config.
4. Record the head SHA. Before reporting, look it up again, and for uncommitted changes rerun both path lists and compare every path on the old or new lists with its snapshot copy. If anything changed, update the snapshot and review again.

Delete the snapshot before you return, including when you stop early.

## Report

Open with one sentence on what the change does, then `Reviewed <target> at <short head SHA>.`

Number the findings, most severe first. For each:

- Tag its priority, `[P0]` for a universal blocker or `[P1]` to `[P3]` from urgent to nice to have, and whether the change introduced it or it was already there.
- Give every line it rests on, including both sides when one place accepts what another rejects. For a PR, link each line: one in the diff to `https://github.com/<owner>/<repo>/pull/<number>/files#diff-<SHA-256 of path>R<line>` (`L<line>` for a removed line), any other to `https://github.com/<owner>/<repo>/blob/<head SHA>/<path>#L<line>`. Otherwise give `path:line`.
- Describe the failure as a concrete scenario in plain words: the input or sequence, then what goes wrong. Then show what the fix looks like.
- Quote the code or command output it rests on, and label inference as inference.

End with open questions, what you couldn't verify, and a verdict, ship or not yet, based only on findings the change introduced. If nothing holds up, say so.
