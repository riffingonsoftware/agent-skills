---
name: refactor-agents-md
description: Refactor an AGENTS.md file or equivalent AI-agent instruction set into a progressive-disclosure structure with a minimal root file and linked detail docs. Use when the user asks to reorganize AGENTS.md, CLAUDE.md, .cursorrules, or similar instruction files, consolidate conflicting guidance, or generate a docs/agents layout before writing changes.
---

# Refactor AGENTS.md

> Canonical source of truth for this skill. Tool-specific wrappers should adapt invocation and metadata, not fork the workflow.

Use this skill to refactor an AGENTS.md file, or an equivalent instruction file for AI coding agents, into a progressive-disclosure layout: essential guidance in the root file and detailed guidance in linked documents.

## Workflow

### 1. Gather instruction sources

Before analyzing, collect all existing agent instructions in the repository:

1. Read `AGENTS.md` if it exists.
2. Read `CLAUDE.md`, `.cursorrules`, and other platform-specific instruction files.
3. Check common locations such as `docs/AGENTS.md` or `.github/AGENTS.md`.

Combine the discovered instructions into a single corpus for analysis.

### 2. Find contradictions

Scan the corpus for instructions that conflict with each other. For each contradiction:

1. Present both conflicting instructions clearly.
2. Recommend which version to keep and why.
3. Ask the user to confirm before proceeding.

If no contradictions are found, state "No contradictions detected" and continue.

### 3. Identify what belongs in the root file

Keep only the material that belongs in the root `AGENTS.md`:

- One-sentence project description.
- Build system or package manager, only when it is non-standard for the ecosystem.
- Non-standard build, lint, typecheck, or test commands.
- Critical constraints that apply to every task.

Move everything else into linked documents.

### 4. Group the remaining guidance

Organize the rest into logical categories such as:

- Language conventions
- Testing patterns
- API design
- Git workflow
- Architecture
- Security
- Performance

### 5. Propose the target structure

Present:

#### 5a. Minimal root `AGENTS.md`

```markdown
# Project Name

One-sentence description.

## Quick Reference

- Build: `command`
- Test: `command`
- Lint: `command`

## Guidelines

Detailed guidelines are organized by topic:

- [Test-Driven Development](docs/agents/test-driven-development.md) - Mandatory Red-Green-Refactor protocol
- ...links to each file in docs/agents/ with a one-sentence description
```

#### 5b. `docs/agents/` structure

List each proposed file and the instructions that belong in it.

#### 5c. Instruction redirection

Recommend replacing `CLAUDE.md` and other platform-specific instruction files with:

```markdown
@AGENTS.md
```

Use this only where the platform supports include-style indirection.

### 6. Seed required docs when missing

Create or propose:

- `docs/agents/test-driven-development.md`
- `docs/agents/tests.md`
- `docs/agents/mocking.md`
- `docs/agents/deep-modules.md`
- `docs/agents/interface-design.md`
- `docs/agents/refactoring.md`
- `docs/agents/architecture.md`

Seed the TDD files from the bundled doc set in Appendix A below, not from an upstream GitHub source or a filesystem search outside the current repository. Preserve each provenance note exactly as bundled. Seed the rest with concrete, actionable guidance rather than vague principles.

### 7. Flag deletions

Identify redundant, vague, or obvious instructions to remove, such as:

- "Write clean code"
- "Follow best practices"
- "Use meaningful names"
- "Keep things simple"
- "Be consistent"
- "Think about performance"
- "Don't introduce bugs"
- "Test your changes"
- "Make sure code compiles"

Explain why each flagged item should be deleted.

## Output format

Present the refactor as:

1. Sources gathered
2. Contradictions found
3. Proposed root `AGENTS.md`
4. Proposed `docs/agents/` structure
5. Full content of each new file
6. Items flagged for deletion

## Appendix A: Bundled Seed Docs

### `docs/agents/test-driven-development.md`

````markdown
# Test-Driven Development

> Adapted local copy of `mattpocock/skills/tdd/SKILL.md`, retrieved on 2026-03-26.

## Philosophy

**Core principle**: Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** are integration-style: they exercise real code paths through public interfaces. They describe _what_ the system does, not _how_ it does it. A good test reads like a specification - "user can complete checkout with a valid cart" tells you exactly what capability exists. These tests survive refactors because they don't care about internal structure.

**Bad tests** are coupled to implementation. They mock internal collaborators, test private methods, or verify through external means (like querying a database directly instead of using the interface). The warning sign: your test breaks when you refactor, but behavior hasn't changed. If you rename an internal function and tests fail, those tests were testing implementation, not behavior.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Anti-Pattern: Horizontal Slices

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" - treating RED as "write all tests" and GREEN as "write all code."

This produces **crap tests**:

- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things (data structures, function signatures) rather than user-facing behavior
- Tests become insensitive to real changes - they pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

**Correct approach**: Vertical slices via tracer bullets. One test -> one implementation -> repeat. Each test responds to what you learned from the previous cycle. Because you just wrote the code, you know exactly what behavior matters and how to verify it.

```text
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED->GREEN: test1->impl1
  RED->GREEN: test2->impl2
  RED->GREEN: test3->impl3
  ...
```

## Workflow

### 1. Planning

Before writing any code:

- [ ] Confirm with user what interface changes are needed
- [ ] Confirm with user which behaviors to test (prioritize)
- [ ] Identify opportunities for [deep modules](deep-modules.md) (small interface, deep implementation)
- [ ] Design interfaces for [testability](interface-design.md)
- [ ] List the behaviors to test (not implementation steps)
- [ ] Get user approval on the plan

Ask: "What should the public interface look like? Which behaviors are most important to test?"

**You can't test everything.** Confirm with the user exactly which behaviors matter most. Focus testing effort on critical paths and complex logic, not every possible edge case.

### 2. Tracer Bullet

Write ONE test that confirms ONE thing about the system:

```text
RED:   Write test for first behavior -> test fails
GREEN: Write minimal code to pass -> test passes
```

This is your tracer bullet - proves the path works end-to-end.

### 3. Incremental Loop

For each remaining behavior:

```text
RED:   Write next test -> fails
GREEN: Minimal code to pass -> passes
```

Rules:

- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior

### 4. Refactor

After all tests pass, look for [refactor candidates](refactoring.md):

- [ ] Extract duplication
- [ ] Deepen modules (move complexity behind simple interfaces)
- [ ] Simplify interfaces and responsibilities where natural
- [ ] Consider what new code reveals about existing code
- [ ] Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

## Checklist Per Cycle

```text
[ ] Test describes behavior, not implementation
[ ] Test uses public interface only
[ ] Test would survive internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```
````

### `docs/agents/tests.md`

````markdown
# Good and Bad Tests

> Adapted local copy of `mattpocock/skills/tdd/tests.md`, retrieved on 2026-03-26.

## Good Tests

**Integration-style**: Test through real interfaces, not mocks of internal parts.

```text
# GOOD: Tests observable behavior
test "user can complete checkout with a valid cart":
  cart = create_cart()
  cart.add(item)
  result = checkout(cart, payment_method)
  assert result.status == "confirmed"
```

Characteristics:

- Tests behavior users/callers care about
- Uses public API only
- Survives internal refactors
- Describes WHAT, not HOW
- One logical assertion per test

## Bad Tests

**Implementation-detail tests**: Coupled to internal structure.

```text
# BAD: Tests implementation details
test "checkout delegates to payment processor":
  payment_processor = fake_processor()
  checkout(cart, payment_processor)
  assert payment_processor.charge was called with cart.total
```

Red flags:

- Mocking internal collaborators
- Testing private methods
- Asserting on call counts/order
- Test breaks when refactoring without behavior change
- Test name describes HOW not WHAT
- Verifying through external means instead of interface

```text
# BAD: Bypasses the interface to verify persistence details
test "creating a user writes to storage":
  create_user(name="Alice")
  row = storage_lookup("users", name="Alice")
  assert row exists

# GOOD: Verifies behavior through the public interface
test "creating a user makes that user retrievable":
  user = create_user(name="Alice")
  retrieved = get_user(user.id)
  assert retrieved.name == "Alice"
```
````

### `docs/agents/mocking.md`

````markdown
# When to Mock

> Adapted local copy of `mattpocock/skills/tdd/mocking.md`, retrieved on 2026-03-26.

Mock at **system boundaries** only:

- External APIs (payment, email, etc.)
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally:

```text
# Easy to mock
process_payment(order, payment_gateway):
  return payment_gateway.charge(order.total)

# Hard to mock
process_payment(order):
  gateway = create_payment_gateway_from_runtime_config()
  return gateway.charge(order.total)
```

**2. Prefer specific boundary operations over generic request wrappers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```text
# GOOD: Each operation is independently mockable
service:
  get_user(id)
  list_orders(user_id)
  create_order(data)

# BAD: One generic transport wrapper forces conditionals into every mock
service:
  request(operation, params)
```

The SDK approach means:

- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Clear contracts per operation
````

### `docs/agents/deep-modules.md`

````markdown
# Deep Modules

> Local copy of `mattpocock/skills/tdd/deep-modules.md`, retrieved on 2026-03-26.

From "A Philosophy of Software Design":

**Deep module** = small interface + lots of implementation

```text
+---------------------+
|   Small Interface   |  <- Few methods, simple params
+---------------------+
|                     |
|                     |
| Deep Implementation |  <- Complex logic hidden
|                     |
|                     |
+---------------------+
```

**Shallow module** = large interface + little implementation (avoid)

```text
+---------------------------------+
|       Large Interface           |  <- Many methods, complex params
+---------------------------------+
|    Thin Implementation          |  <- Just passes through
+---------------------------------+
```

When designing interfaces, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?
````

### `docs/agents/interface-design.md`

````markdown
# Interface Design for Testability

> Adapted local copy of `mattpocock/skills/tdd/interface-design.md`, retrieved on 2026-03-26.

Good interfaces make testing natural:

1. **Accept dependencies, don't create them**

   ```text
   # Testable
   process_order(order, payment_gateway)

   # Hard to test
   process_order(order):
     gateway = create_payment_gateway()
   ```

2. **Return results, don't produce side effects**

   ```text
   # Testable
   calculate_discount(cart) -> discount

   # Hard to test
   apply_discount(cart):
     cart.total = cart.total - discount
   ```

3. **Small surface area**

   - Fewer methods = fewer tests needed
   - Fewer params = simpler test setup
````

### `docs/agents/refactoring.md`

````markdown
# Refactor Candidates

> Adapted local copy of `mattpocock/skills/tdd/refactoring.md`, retrieved on 2026-03-26.

After TDD cycle, look for:

- **Duplication** -> Extract a shared helper or module
- **Long routines** -> Break into smaller internal helpers (keep tests on public interface)
- **Shallow modules** -> Combine or deepen
- **Feature envy** -> Move logic to where data lives
- **Primitive obsession** -> Introduce value objects
- **Existing code** the new code reveals as problematic
````

## Output Format

Present your refactoring as:

1. **Sources Gathered** (List all files found).
2. **Contradictions Found** (With recommendations).
3. **Proposed Root AGENTS.md** (Full content).
4. **Proposed docs/agents/ Structure** (File list).
5. **Full Content of Each New File**.
6. **Items Flagged for Deletion**.

**IMPORTANT:** Version your resulting documentation with both the version of this refactor skill (2026-03-26) and the model executing the command.

Ask user to confirm before writing any files.
