---
name: handoff
description: Create a focused handoff prompt shaped by why the user wants to continue in a new agent session.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

# Handoff

Write a self-contained prompt for a fresh agent to continue the current work. The user's argument describes what the next session will be used for: use it to choose and emphasize context, define the next objective, and omit unrelated threads. If no argument was provided and the intended focus is ambiguous, ask before writing.

Address the prompt directly to the next agent. Include the objective, relevant state, user requirements, decisions and rationale, evidence, unresolved questions, next actions, success criteria, and validation. Distinguish facts and confirmed decisions from assumptions. Preserve exact commands, values, and outcomes when they matter.

Do not duplicate information already captured in artifacts such as plans, issues, commits, or diffs; reference their paths or URLs instead. Suggest only available skills that would materially help the next agent.

Redact secrets and sensitive personal information. When the next agent needs protected information, name its approved retrieval mechanism instead.

Save the prompt as `handoff.md` in a new private, collision-resistant directory under the operating system's temporary directory, never in the workspace. Do not start the new session or continue its work. Return the absolute path and one sentence describing the handoff; do not paste the prompt unless asked.
