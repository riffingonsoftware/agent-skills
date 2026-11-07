---
name: hill-climb
description: Hill climb work toward a goal, one kept or reverted change per round, until a scorer says the goal is met.
---

# Hill climb

Improve the work one change per round until the scorer says it meets the goal. Return the best kept version and the log.

## Set up

1. Create a temporary directory for the evidence, with one subfolder per round. Keep the log in it as `log.md`. Finish when the log names:
   - The goal: a score to reach, or a reference to match or beat.
   - The scorer: a command whose output decides the goal, such as an eval, test suite, or benchmark. Use judges only when no command can decide it.
   - The evidence: a fixed set of captures, such as the same screenshots, seeds, and inputs, that every round repeats.
   - The categories the judges score and the references they compare against, if judges are the scorer.
   - The fallback work, if the user named any.
2. Capture and score the current version as round 0. It is the first kept version.

## Rounds

Each round is one unit of work:

1. Make one change: the one expected to gain the most per unit of effort, guided by the last verdict's ranked gaps.
2. Recapture every piece of evidence from the changed version. Never use a capture from an earlier version as evidence of the changed one.
3. Score it.
4. Keep the change and commit it if it beats the last kept version: for a command, a better result with no other output worse; for judges, every judge calls it better and scores no category below the last kept version. Otherwise revert it.
5. Add a row to the log: round, change, kept or reverted, and each judge's verdict or score.

## Judges

- Use the judges the user's instructions name, if any. Otherwise use one subagent on the strongest model available, such as Claude Opus. In T3 Code, `delegate_task` reaches other providers' models.
- Start every judge in a fresh context. Give it the evidence for the current and last kept versions, the references, and what it needs to read them, such as which art is placeholder and which odd-looking choices are deliberate. Withhold your opinion of the change and the goal's score.
- Ask each judge: Is the current version better than the last kept one? Score the current version, the last kept version, and each reference from 1 to 10 in each category. Rank the remaining gaps by how much each would close per unit of effort.
- A round meets the goal when every judge scores every category at the goal's score, or at least each reference's score. With one judge, confirm with a second fresh judge on the same evidence; the goal is met only if both agree.
- Taste is the judges' call. Never stop or ask the user over a design or taste decision: make the call, log it, and continue.

## Stop

Stop at the first of:

1. The goal is met. Stop there; never raise the bar.
2. Stuck: the last two verdicts rank the same top gaps first, and closing them needs something only the user can supply, such as an asset, credentials, or access. Log what the user must supply, then start the fallback work, or stop if there is none.
3. A deadline, such as a burn-down's stop time. Report the goal as not met.

Report whether the goal was met, the best kept version's commit, the log's round table, the remaining gaps, and every decision for the user to revisit.
