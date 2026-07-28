---
name: codex-grill-with-docs
description: Run Matt Pocock's grill-with-docs with GPT-calibrated question selection and stopping criteria.
disable-model-invocation: true
---

Load and run the installed `/grill-with-docs` skill with the additional constraints below. If it is unavailable, stop and report the missing prerequisite instead of recreating it.

- Ask only unresolved, human-owned questions whose answers could materially change scope, observable behavior, acceptance, a difficult-to-reverse decision, or data, security, and rollback risk.
- Before asking, identify what would change based on the answer. Skip the question if the outcome or recommendation would remain the same.
- Do not ask about discoverable facts, reversible implementation details, speculative branches, or preferences already implied by the context.
- Stop when the remaining uncertainty can be resolved safely during implementation. Use no fixed question limit; depth follows consequential uncertainty, not every branch that can be imagined.

All other behavior comes from `/grill-with-docs`.
