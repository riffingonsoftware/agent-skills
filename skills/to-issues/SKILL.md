---
name: to-issues
description: Break a plan, spec, or conversation into AFK-ready issues in the repo's committed .issues/ kanban.
disable-model-invocation: true
---

# To Issues

Create self-contained issues an agent can implement without other context; create no other planning artifacts. Unless directed otherwise, create them under `.issues/`, commit, and push them.

## Tracker

- Use one `.issues/<feature-slug>/` directory per feature and one `NN-<slug>.md` file per issue, numbered from `01`.
- The first line is `Status: backlog`, `Status: claimed`, or `Status: ready`.
- An issue remains blocked while any path under `## Blocked by` exists; deletion marks that blocker complete.
- Complete work by deleting its issue file in the completing commit; git history is the archive.

## Process

1. Use the conversation context and read any referenced issue first.
2. Explore the repo as needed and identify prefactoring that simplifies the change. Draft independently verifiable tracer bullets in its domain language; each spans all applicable layers end to end. Put prefactoring slices first and never split work horizontally by layer.
   - For a mechanical refactor too wide to land green in one slice, use expand–contract: add the new form beside the old, migrate call sites in batches blocked by the expand, then remove the old form in a contract issue blocked by every batch.
3. Ask one question at a time, with a recommended answer, only when it changes product semantics, destructive or one-way behavior, data/security/rollback posture, whether an existing surface stays or goes, or acceptance behavior you cannot infer. Do not ask the user about issue boundaries, order, naming, or implementation approach.
4. Unless told to skip review, present each issue's title, purpose, blockers, and acceptance behavior before publishing.
5. Publish approved issues as `Status: ready`, then commit and push them. Add dependencies only for real blockers, not tidy ordering. Do not close, delete, or modify parent issues.

## Issue template

```md
Status: ready

# <Title>

## What to build

<Describe this slice end to end. Include file paths or code only as stable, necessary constraints.>

## Acceptance criteria

- [ ] <Observable behavior>

## Blocked by

None.

## When done

Commit the work, then delete this file; git history is the archive.
```

Add `## Decisions` only for human-owned decisions resolved while drafting. Under `## Blocked by`, list blocker issue files by path.
