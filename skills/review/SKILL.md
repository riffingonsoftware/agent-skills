---
name: review
description: Review a PR, branch, commit, or uncommitted change. Use when asked to review one or whether anything jumps out.
---

# Review

Review adversarially. Try to break the change, and take the goal as given. Check for storage, files, or caches that nothing cleans up, and for input size, work, or request rate a caller can drive without limit; reviews have missed both, and one leak shipped and grew to 177 GB. A finding survives only when a run against the real code proves it, such as a failing test, a repro script, or command output that shows wrong behavior: output that contradicts the intent, the behavior before the change, or a documented contract. Leave out what you did not prove with a run, including style, naming, structure, and risks that need a future change to matter.

If you wrote or changed the target in this session, hand this skill and the target to a fresh subagent and relay its report.

Don't comment on, approve, or request changes on a PR; draft any comment for the user, with the line to put it on.

## Snapshot

Read and run everything in a snapshot of the target's head, never in the user's checkout. In the checkout, run only the commands below; even `git status` and `git diff` can rewrite its index.

1. Find the checkout. For a PR, it's `~/projects/<repo>`; if that path doesn't exist, clone the repository there with `gh repo clone <owner>/<repo> ~/projects/<repo>`. Clone the checkout into a new temporary directory with `git clone --shared --no-checkout`. Resolve refs to SHAs in the checkout with `git rev-parse`, because the snapshot's `origin/<branch>` is the checkout's local branch.
2. Check out the head:
   - For a PR, fetch `pull/<number>/head` and `baseRefOid` from the PR's repository URL, confirm the head matches `headRefOid`, and read the change as `git diff <baseRefOid>...<headRefOid>`, because the checkout's branches can be weeks old. Pass the PR URL to every `gh pr` command, because `gh` can't find the repository from the snapshot.
   - For uncommitted changes, check out `HEAD`, then list the changed paths in the checkout with `git diff-index --name-only HEAD` and `git ls-files -o --exclude-standard`. Copy each into the snapshot, keeping symlinks as links, or delete it there if the checkout no longer has it.
   - For a merge commit, read the change with `git show --first-parent`.
3. Run the repository's focused checks and rerun any checks you were told passed. Before you drop a suspected defect, including one you found only by reading code, try to prove it with a small throwaway command in the snapshot. If proving it needs something the snapshot lacks, such as credentials or a cluster, list it as unverified instead of dropping it. Install dependencies only with the repository's locked install command, such as `npm ci`. If the repository uses mise, prefix commands with `MISE_TRUSTED_CONFIG_PATHS=<snapshot path>`, because mise ignores config at an untrusted path. If a check needs ignored config such as `.env`, list it as unverified instead of copying the config.
4. Rerun each finding's command. Keep a finding when its output still shows wrong behavior. Drop the rest. Merge findings that share a root cause.
5. Record the head SHA. Before reporting, look it up again, and for uncommitted changes rerun both path lists and compare every path on the old or new lists with its snapshot copy. If anything changed, update the snapshot and review again.

Delete the snapshot before you return, including when you stop early.

## Report

Open with one sentence on what the change does, then `Reviewed <target> at <short head SHA>.`

Number the findings, most severe first. For each:

- Tag its priority, `[P0]` for a universal blocker or `[P1]` to `[P3]` from urgent to nice to have, and whether the change introduced it or it was already there.
- Give every line it rests on, including both sides when one place accepts what another rejects. For a PR, link each line: one in the diff to `https://github.com/<owner>/<repo>/pull/<number>/files#diff-<SHA-256 of path>R<line>` (`L<line>` for a removed line), any other to `https://github.com/<owner>/<repo>/blob/<head SHA>/<path>#L<line>`. Otherwise give `path:line`.
- Describe the failure as a concrete scenario in plain words: the input or sequence, then what goes wrong. Then show what the fix looks like.
- Give the exact command, the output it printed, and the output it should print, with what requires it: the intent, the behavior before the change, or a documented contract.

End with open questions, what you couldn't verify, how many suspected defects you dropped and why, and a verdict, ship or not yet, based only on findings the change introduced. If nothing holds up, say so.
