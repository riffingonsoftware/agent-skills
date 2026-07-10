---
name: handoff
description: Compact the conversation into a handoff for a fresh agent.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Summarize the current conversation into a handoff for a fresh agent. Write it to the OS temporary directory, never the workspace. If arguments were passed, use them as the next session's focus.

Recommend skills for the next agent in a "suggested skills" section. Reference existing artifacts (plans, issues, commits, diffs) by path or URL instead of duplicating them. Redact sensitive information, including credentials and personally identifiable information.
