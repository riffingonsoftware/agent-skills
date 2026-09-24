# Agent Skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- `skills/.devin-plugin/plugin.json` lets Devin install `skills/` as a plugin without the repo's `AGENTS.md`.

## Current skills

- `babysit-pr` watches CI and all review bots until a PR is ready to merge, escalating ambiguity and human feedback.
- `deslop` removes AI-generated code slop from a branch diff while preserving behavior.
- `init-or-refactor-agents-md` initializes or compresses agent instruction files into one short `AGENTS.md` that coding agents are likely to follow. It emphasizes repro-first, behavior-only tests for confirmed bugs and avoids speculative test creation.
- `no-comments` audits edited code for comments to delete and fixes accepted findings.
- `open-pr` cleans and organizes a change, opens a pull request, and babysits it to merge readiness.
- `prune-tests` deletes tests that do not uniquely protect a durable contract, confirmed regression, or critical invariant.
- `ship` scans local changes for sensitive data, splits them into logical commits, and pushes.
- `unslop` removes AI tells from prose.

## Tool requirements

- Gemini CLI should be configured to load `AGENTS.md` as a project context file.
- The official Gemini CLI `context.fileName` setting accepts a string or an array. To prefer `AGENTS.md` while retaining existing `GEMINI.md` support, use:

```json
{
  "context": {
    "fileName": ["AGENTS.md", "GEMINI.md"]
  }
}
```

## Credits

Four skills are adapted from MIT-licensed upstreams. Each keeps the upstream copyright and permission notice in its own `LICENSE` file, so the notice travels with the skill.

- `deslop` comes from the [`deslop` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/cursor-team-kit/skills/deslop) in Cursor's cursor-team-kit, © 2026 Cursor.
- `no-comments` comes from pstack's [`no-comments` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/pstack/skills/no-comments) and [Comment Sicko agent](https://github.com/cursor/plugins/blob/99559f2f52047978602ef365589275831e76af07/pstack/agents/comment-sicko.md), © 2026 Lauren Tan.
- `open-pr` comes from pstack's [opening-a-pr playbook](https://github.com/cursor/plugins/blob/99559f2f52047978602ef365589275831e76af07/pstack/skills/poteto-mode/playbooks/opening-a-pr.md), © 2026 Lauren Tan.
- `unslop` comes from pstack's [`unslop` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/pstack/skills/unslop), © 2026 Lauren Tan.
