---
name: to-tickets
description: Turn plans, specs, or conversations into AFK-ready tickets in a committed .tickets/ kanban.
disable-model-invocation: true
---

# To Tickets

Create self-contained tickets an agent can execute without context, and no other planning artifacts. Default to `.tickets/`; commit and push.

## Tracker

- One `.tickets/<feature-slug>/` per feature; name tickets `NN-<slug>.md` from `01`.
- First line: `Status: backlog`, `Status: claimed`, or `Status: ready`.
- A ticket is blocked while a path under `## Blocked by` exists; deleting the path clears it.
- Delete completed tickets in their implementation commits; git history is the archive.

## Process

1. Read the context and referenced tickets; inspect the repo as needed.
2. Find simplifying prefactors. Draft independently verifiable, end-to-end tracer bullets in domain terms. Put prefactors first; never split by layer.
   - For oversized mechanical refactors, expand–contract: add the new form, migrate batches blocked by it, then remove the old form in a ticket blocked by every batch.
3. Ask one recommended question at a time only about product semantics, destructive or one-way behavior, data/security/rollback, surface retention, or acceptance you cannot infer. Never ask about ticket boundaries, order, names, or implementation.
4. Unless review is waived, present each ticket's title, purpose, blockers, and acceptance behavior.
5. Publish approved tickets as `Status: ready`; commit and push. Use only real blockers. Leave parent tickets unchanged.

## Ticket template

```md
Status: ready

# <Title>

## What to build

<Describe the end-to-end slice; mention paths or code only as stable constraints.>

## Acceptance criteria

- [ ] <Observable behavior>

## Blocked by

None.

## When done

Commit, then delete this ticket; git history is the archive.
```

Add `## Decisions` only for resolved human-owned decisions. List blocker ticket paths under `## Blocked by`.
