---
name: to-issues
description: Break a plan, spec, or conversation into AFK-ready issues in the repo's committed .issues/ kanban.
disable-model-invocation: true
---

# To Issues

Goal: issues an implementing agent can pick up later with no extra context. Create no other planning artifacts.

## Tracker

Issues live in the repo, committed and pushed:

- One feature per directory: `.issues/<feature-slug>/`
- One issue per file: `.issues/<feature-slug>/NN-<slug>.md`, numbered from `01`
- First line of each file: `Status: backlog`, `Status: claimed`, or `Status: ready`
- An issue is blocked while any file listed under its `## Blocked by` still exists; a deleted blocker is a finished blocker
- Done is a deletion, not a status: delete the issue file in the commit that completes the work; git history is the archive

Publish here unless the user directs otherwise.

## Process

1. Work from the conversation context. If the user passes an issue reference, read it first.
2. Explore the codebase if you have not already. Look for prefactoring that would make the change easy: make the change easy, then make the easy change.
3. Draft tracer-bullet slices. Each issue cuts through all layers end-to-end (schema, API, UI, tests), is verifiable on its own, and uses the project's domain language. Prefactoring comes first. No horizontal layer-by-layer issues.
   - Exception — wide mechanical refactors that can't land green in one slice: sequence as expand–contract. Expand (add the new form beside the old), migrate call sites in batches blocked by the expand, contract (delete the old form) blocked by every batch.
4. Resolve only the ambiguity that matters. Ask one question at a time, with a recommended answer, when the answer changes product semantics, destructive or one-way behavior, data/security/rollback posture, whether an existing surface lives or dies, or acceptance behavior that can't be inferred. Issue boundaries, ordering, naming, and implementation approach are the implementing agent's to decide — don't ask.
5. Present the issue set (title, purpose, blockers, acceptance behavior) before publishing, unless told to skip review.
6. Publish approved issues as `Status: ready`, commit them, and push. Add dependencies only for real blockers, not tidy sequencing. Do not close, delete, or modify parent issues.

## Issue template

```md
Status: ready

# <Title>

## What to build

End-to-end behavior of this slice, not layer-by-layer implementation. No file paths or code snippets unless they are stable, necessary constraints.

## Acceptance criteria

- [ ] <observable behavior>

## Blocked by

None.

## When done

Commit the work, then delete this file — git history is the archive.
```

Add `## Decisions` only when human-owned decisions were resolved during the ambiguity pass. Under `## Blocked by`, list blocker issue files by path.
