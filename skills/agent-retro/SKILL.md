---
name: agent-retro
description: Run a retrospective on agent sessions to find improvements to the agent's environment. Takes a timeframe, such as the last 7 days.
---

# Agent retro

Find changes to the agent's environment that would have prevented the trouble in these sessions. Return a report and change nothing.

## Steps

1. Collect the session logs from every local agent harness, such as Claude Code and Codex, for the requested timeframe. Without a timeframe, use the current session.
2. Search the logs for trouble before reading them in full: user corrections, interrupts, denied or failed tool calls, reverted edits, repeated searches, and repeated review findings. Read the excerpts around each.
3. Group the trouble by cause. Across several sessions, keep a cause only when it appears in at least two of them. Tag each cause as global, specific to one repo, or specific to one tech stack.
4. Propose a fix for each cause from the categories below, in the place its tag points to. Prefer a check or a review rule to an always-loaded instruction, because the implementing agent carries the most context. Apply `write-for-agents` to any instruction you propose.
5. Return the candidates ranked by how often each recurred and what it cost. Give each its category, tag, evidence (session, date, and a short quote with secrets redacted), and proposed fix. Finish when every cause from step 3 has a candidate.

## Categories

- `navigation`. The agent took long to find a file or fact, or missed a hidden dependency between files. Add a pointer where the agent looked first.
- `checks`. The agent made a mistake an automated check could catch, or the repo runs no lint, type, or test check before merge. Read the repo's check commands and CI first; a check that exists but is unwired or broken is the finding.
- `review`. A review agent or skill missed a mistake, or keeps flagging the same one. Give a mechanical violation, such as a banned API or import shape, a deterministic check: a lint rule, hook, or CI job. Keep review rules for judgment calls.
- `instructions`. The agent ignored or misread an instruction file or skill, a skill fired when it shouldn't or stayed silent when it should have fired, or an instruction changes nothing. Fix the wording before moving the instruction.
- `tools`. The agent made expensive or repeated tool calls, or a tool or MCP server wastes tokens.
- `access`. The agent lacked information it needed, such as server logs or read-only access to a service.
