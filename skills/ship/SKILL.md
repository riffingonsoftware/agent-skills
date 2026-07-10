---
name: ship
description: Scan local changes for sensitive data, split them into logical commits, and push.
---

# Ship

1. Inspect `git status --short`, `git diff`, `git diff --staged`, and every untracked file. Never commit an uninspected file.
2. Scan all changes for secrets, credentials, tokens, API or private keys, `.env` contents, personal data, or anything else that should not be committed. If concerned, stop without committing or quoting the value; name the file and concern, then ask whether to remove, redact, ignore, or intentionally keep it.
3. Group all changes by purpose. Stage and commit one independently reviewable group of files or hunks at a time, with a clear message; recheck status between commits.
4. Run obvious, reasonably quick tests or checks before pushing; otherwise report what was skipped.
5. Push the current branch to its existing upstream. Ask before setting one.

Ask before destructive cleanup, reset, checkout, or deletion. End by reporting the commits, sensitive-data scan result, checks, and push result.
