---
name: deslop
description: Remove AI-generated code slop and clean up code style
---

# Remove AI code slop

Check the diff against the base branch and remove AI-generated slop introduced in the branch.

## Focus Areas

- Extra comments that are unnecessary
- Defensive checks or try/catch blocks or similar guardrails that are abnormal for trusted code paths
- Casts to `any` (or similar language-specific overly broad type) used only to bypass type issues
- Deeply nested code that should be simplified with early returns

## Guardrails

- Keep behavior unchanged unless fixing a clear bug.
- Prefer minimal, focused edits over broad rewrites.
- Keep the final summary concise (1-3 sentences).
