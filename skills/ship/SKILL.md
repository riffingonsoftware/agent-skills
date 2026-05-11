---
name: ship
description: Scan local changes for sensitive data, split them into logical commits, and push.
---

# Ship Local Changes

Goal: safely turn all local changes into logical commits and push them upstream.

## Workflow

1. Inspect repository state.
   - Run `git status --short`.
   - Review tracked changes with `git diff`.
   - Review staged changes with `git diff --staged`.
   - Review untracked files before adding them.

2. Scan for sensitive data before committing.
   Look for secrets, credentials, tokens, API keys, private keys, `.env` contents, personal data, generated credentials, or anything that should not be committed.

3. If suspicious data is found, stop.
   - Do not commit.
   - Do not quote the secret value.
   - Describe the file/path and kind of concern.
   - Ask the user whether to remove, redact, ignore, or intentionally keep it.

4. Split changes into logical chunks.
   - Group related files and hunks by purpose.
   - Keep unrelated changes in separate commits.
   - Prefer focused commits that can be reviewed independently.

5. Commit each chunk.
   - Stage only the files/hunks for that chunk.
   - Use clear commit messages.
   - Re-check `git status --short` between chunks.

6. Push.
   - Push to the current branch's upstream.
   - If no upstream exists, ask before setting one.

## Safety rules

- Never skip the sensitive-data scan.
- Never commit files you did not inspect.
- Never stage all changes blindly when unrelated changes are present.
- Ask before destructive cleanup, reset, checkout, or deletion.
- If tests/checks are obvious and reasonably quick, run them before pushing; otherwise explain what was not run.

## Output

End with:

1. Commits created
2. Sensitive-data scan result
3. Checks run or skipped
4. Push result
