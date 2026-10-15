# Agent skills

Portable agent skills and tool adapters.

## Layout

- `skills/` contains canonical open-standard skills. These are the source of truth.
- `skills/.devin-plugin/plugin.json` lets Devin install `skills/` as a plugin without the repo's `AGENTS.md`.

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

Six skills are adapted from MIT-licensed upstreams. Each keeps the upstream copyright and permission notice in its own `LICENSE` file, so the notice travels with the skill.

- `agent-retro` is inspired by and includes portions of Matt Pocock's [`retro` skill](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/retro), © 2026 Matt Pocock.
- `deslop` comes from the [`deslop` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/cursor-team-kit/skills/deslop) in Cursor's cursor-team-kit, © 2026 Cursor.
- `no-comments` comes from pstack's [`no-comments` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/pstack/skills/no-comments) and [Comment Sicko agent](https://github.com/cursor/plugins/blob/99559f2f52047978602ef365589275831e76af07/pstack/agents/comment-sicko.md), © 2026 Lauren Tan.
- `open-pr` is inspired by and includes portions of pstack's [opening-a-pr playbook](https://github.com/cursor/plugins/blob/99559f2f52047978602ef365589275831e76af07/pstack/skills/poteto-mode/playbooks/opening-a-pr.md), © 2026 Lauren Tan.
- `review` is inspired by OpenAI's [Codex review rubric](https://github.com/openai/codex/blob/922510f4d7570b42838e015787ed53abfa8761a1/codex-rs/prompts/templates/review/rubric.md) and [adversarial-review prompt](https://github.com/openai/codex-plugin-cc/blob/db52e28f4d9ded852ab3942cea316258ae4ef346/plugins/codex/prompts/adversarial-review.md).
- `unslop` comes from pstack's [`unslop` skill](https://github.com/cursor/plugins/tree/99559f2f52047978602ef365589275831e76af07/pstack/skills/unslop), © 2026 Lauren Tan.
- `write-for-agents` is inspired by and includes portions of Matt Pocock's [`writing-for-agents` skill](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/productivity/writing-for-agents), © 2026 Matt Pocock.
