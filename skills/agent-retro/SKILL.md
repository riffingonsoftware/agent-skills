---
name: agent-retro
description: Run a retrospective on agent sessions to find improvements to the agent's environment. Takes a timeframe, such as the last 7 days.
---

# Agent retro

Find changes to the agent's environment that would have prevented the trouble in these sessions. Return a report and change nothing.

## Steps

1. Run `python3 scripts/collect.py --since <date>` from this skill's directory. Without a timeframe, review the current session instead.
2. Search the logs for trouble before reading them in full: user corrections, interrupts, denied or failed tool calls, approval and sign-in prompts, browser automation, content the user pasted in, reverted edits, repeated searches, repeated review findings, and commands or inline scripts repeated across sessions. Read the excerpts around each.
3. Group the trouble by cause. Across several sessions, keep a cause only when it appears in at least two of them. Count a subagent or review thread as part of the session that started it. Tag each cause as global, specific to one repo, or specific to one tech stack.
4. For each `Remove-When:` trailer the script lists, check its condition and whether the cause its commit names recurred. Propose deleting a fix whose condition holds, that a higher-tier fix now covers, or that misfires. Propose a higher-tier fix for a cause that recurred after its fix.
5. Propose a fix for each cause from the categories below, in the place its tag points to. Prefer, in order: config or an installed tool; a script, lint rule, compiler deprecation, or CI check; a harness hook; a skill; an always-loaded instruction. For a hook or anything after it, name the higher-tier fix you ruled out. A hook runs on every matching call in one harness, so match narrowly, print only on a hit, and name what other harnesses lose. Give each fix a `Remove-When:` trailer for the commit that adds it, naming a condition you can check with the fix still in place, such as a tool, model, or upstream change; a cause stays absent while its fix works, so its absence can't show the fix is unneeded. Apply `write-for-agents` to any instruction you propose.
6. Return the candidates ranked by how often each recurred and what it cost. Give each its category, tag, evidence (session, date, and a short quote with secrets redacted), and proposed fix. Mark a cause whose fix already exists as fixed, and say how to confirm the fix took effect. Name the harnesses the script read, and quote any error it printed. Finish when every cause from step 3 has a candidate and every trailer from step 4 has an outcome.

## Categories

- `navigation`. The agent took long to find a file or fact, or missed a hidden dependency between files. Add a pointer where the agent looked first.
- `checks`. The agent made a mistake an automated check could catch, or the repo runs no lint, type, or test check before merge. Read the repo's check commands and CI first; a check that exists but is unwired or broken is the finding.
- `codify`. Agents repeated mechanical work across sessions, such as polling a status, writing an API client, extracting logs, or running setup steps. Propose a checked-in script or task-runner target that exits nonzero on failure, in the repo the work belongs to.
- `review`. A review agent or skill missed a mistake, or keeps flagging the same one. Give a mechanical violation, such as a banned API or import shape, a deterministic check: a lint rule, hook, or CI job. Keep review rules for judgment calls.
- `instructions`. The agent ignored or misread an instruction file or skill, a skill fired when it shouldn't or stayed silent when it should have fired, or an instruction changes nothing. Fix the wording before moving the instruction.
- `tools`. The agent made expensive or repeated tool calls, or a tool or MCP server wastes tokens. For an MCP server that fails or asks for sign-in where a CLI for the same service works, propose removing the server.
- `access`. The agent lacked information it needed, such as server logs or read-only access to a service, or reached a service through browser automation or content the user pasted in where an MCP server or CLI could have done the same job. Propose the service's MCP server, or its CLI when one is already installed and working, and name the sign-in it needs.
