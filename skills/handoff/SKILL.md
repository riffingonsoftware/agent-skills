---
name: handoff
description: Create a focused handoff prompt shaped by why the user wants to continue in a new agent session.
argument-hint: "Why start a new session, and what should it accomplish?"
disable-model-invocation: true
---

# Handoff

Generate a prompt for a new agent session; do not start the session or continue the work.

1. Identify why the user wants a new session. Use that argument to decide what the next agent should inherit, reconsider, or ignore, and preserve it explicitly. If the reason or next goal is materially unclear, ask before writing.
2. Distill only the context needed to act: the objective, current state, user requirements, decisions and rationale, evidence and paths, constraints, unresolved questions, exact next step, success criteria, and validation. Distinguish observed facts from agent conclusions and assumptions; preserve conflicts rather than silently resolving them.
3. Keep exact values, commands, and outcomes when they matter. Do not dump the transcript, repeat generic instructions, invent missing context, or include secrets; name their approved retrieval mechanism instead when needed.
4. Write the result as a prompt addressed directly to the next agent in `handoff.md`, inside a new private, collision-resistant directory under the platform's temporary directory. Do not modify the repository or fall back to it. Treat the created path as fixed, and note that temporary storage may be cleaned by the platform.
5. Return the absolute file path and one sentence describing what the prompt prepares the next agent to do. Do not paste the prompt into chat unless asked.
