---
name: write-for-agents
description: Write or edit agent instructions, such as skills, AGENTS.md, CLAUDE.md, and docs they point to.
---

# Write for agents

Write instructions that make an agent follow the same process on every run.

## Process

1. Read the document, every pointer to it, every document that calls it, and the files and commands it describes.
2. Draft or revise it with the rules below.
3. Check every sentence against every rule, then apply `unslop`. Finish when every sentence passes both and every caller's steps still hold.

## Pointers

A pointer is a reference to other material in always-loaded context, such as a skill description or an `AGENTS.md` line with a doc link. Every word of a pointer costs tokens and attention on every turn.

- Put the word the user or agent would use for the task first.
- Write one trigger per distinct case. Cut synonyms of a case already listed.
- Cut information already in the target.
- When the agent skips must-have material, reword its pointer first. Inline the material only if rewording fails.

## Placement

- Keep in the main file what every case needs. Move what only some cases need to a separate file, and point to it.
- Keep a topic's definition, rules, and exceptions under one heading.

## Completion criteria

- End every step on a checkable completion criterion. Prefer exhaustive bounds ("every finding is fixed or skipped with a reason") to vague ones ("understand the code") and to adjectives ("be thorough").
- When the agent rushes a step to reach later ones, sharpen its criterion. If it still rushes, give that step to a fresh subagent whose context omits the later steps.

## Wording

- State the behavior you want rather than the one to avoid. Use a prohibition for a hard guardrail.
- Use one term for one concept everywhere. Prefer an established term that means exactly the intended behavior, such as YAGNI or tracer bullet, to a sentence that restates it. Define any term you coin. Spell out every condition the agent must check.

## Pruning

- Keep each rule in one place, and point to it from elsewhere.
- Leave out what the agent can find in one lookup, such as scripts, config, the directory layout, or `--help` output. Write down the conventions, reasons, and gotchas it cannot find.
- Delete a sentence that does not change behavior compared with the model's default. Delete the whole sentence rather than trimming words. Check the history first, and keep a rule added to fix an observed failure until a run without it shows the failure is gone.
- When you can't tell whether a sentence changes behavior, test it. Run the same task in fresh sessions with and without the sentence, at least three times each, with no hint of the test. Use a task large enough that the sentence applies, then compare what the agent did.
- Delete lines that are stale or do not bear on the document's task.
