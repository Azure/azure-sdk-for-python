# Release History

## 0.1.0b1 (Unreleased)

### Features Added

- Initial beta release.
- `load_config()` — single-call config loader with graceful fallback.
- `OptimizationConfig` dataclass with instructions, model, temperature, skills, and tool definitions.
- Candidate resolution via `OPTIMIZATION_CANDIDATE_ID` env var and remote resolver API.
- Inline JSON config via `OPTIMIZATION_CONFIG` env var.
- Local directory layout support (`metadata.yaml` + `instructions.md` + `skills/`).
- Skill loading from `SKILL.md` files with YAML frontmatter.
- Tool definition loading from `tools.json`.
