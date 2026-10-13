---
name: ship
description: Commit and push local changes after scanning them for sensitive data, pruning affected tests, and splitting them into logical commits.
---

# Ship

Ship the changes a caller names, or all local changes when no caller names any.

1. Inspect `git status --short --untracked-files=all`, `git diff`, `git diff --staged`, every untracked file, and every unpushed commit. Never commit an uninspected file.
2. Scan the changes and unpushed commits for secrets, credentials, tokens, API or private keys, `.env` contents, personal data, or anything else that should not be committed. If a change may contain such data, stop without committing. Name the file and the kind of data without quoting the value, then ask whether to remove, redact, ignore, or intentionally keep it.
3. If the changes add, edit, or make tests obsolete, run `prune-tests` scoped to them.
4. Group the changes by purpose. Stage and commit one independently reviewable group of files or hunks at a time, with a message that states its purpose, and recheck status between commits. Finish when none of the changes remain uncommitted.
5. Run obvious, reasonably quick tests or checks before pushing. If one fails, stop and report it without pushing. Report each check you skip.
6. Push the current branch to its existing upstream. Ask before setting one.

Ask before destructive cleanup, reset, checkout, or deletion. End by reporting the commits, sensitive-data scan result, pruned tests, checks, and push result.
