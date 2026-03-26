# Claude Code Skills

Open-source skills for [Claude Code](https://claude.ai/claude-code).

Each skill lives in its own directory and is centered around a `SKILL.md` entry point plus any bundled scripts it needs.

## Available Skills

| Skill                                         | What it does                                                                                                                                         | Requirements                         |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| [gemini-image-gen](gemini-image-gen/SKILL.md) | Generate images with the official Gemini API and save organized output folders with `prompt.md`, generated image files, and optional `request.json`. | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |

## Install

```bash
npx skills add aouos/skills
```

Install a single skill with Claude Code:

```bash
claude skill add --from https://github.com/aouos/skills/tree/main/gemini-image-gen
```

For `gemini-image-gen`, set `GEMINI_API_KEY` or `GOOGLE_API_KEY` in your environment before use.

Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

## How These Skills Work

- Claude Code uses a skill's `description` to decide when to trigger it.
- `SKILL.md` contains the workflow and usage guidance the agent follows.
- Bundled scripts are usually non-interactive CLI tools; the interactive experience comes from the agent workflow, not from the script prompting on its own.

## Project Structure

```text
skills/
├── <skill-name>/
│   ├── SKILL.md
│   └── scripts/
└── ...
```

## Contributing

PRs are welcome. When adding a new skill:

1. Create a directory named after the skill.
2. Add a concise `SKILL.md` with accurate `name` and `description` frontmatter.
3. Keep scripts small and dependency-light; prefer standard library tooling when possible.
4. Put durable workflow guidance in `SKILL.md` and avoid overloading it with fast-changing product details.
5. Verify the skill can be installed and that its main command path works end to end.

## License

[MIT](LICENSE)
