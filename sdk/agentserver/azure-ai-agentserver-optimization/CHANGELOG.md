# Release History

## 1.0.0b1

### Features Added

- Initial beta release.
- `load_config()` — single-call config loader with 4-priority resolution and graceful fallback (never crashes).
- `OptimizationConfig` dataclass with instructions, model, temperature, skills, tool descriptions, source tracking, candidate_id, and job_id.
- 4-priority resolution order:
  1. Inline JSON via `OPTIMIZATION_CONFIG` env var.
  2. Resolver API via `OPTIMIZATION_CANDIDATE_ID` + `OPTIMIZATION_JOB_ID` + `OPTIMIZATION_RESOLVE_ENDPOINT`.
  3. Local directory layout (`OPTIMIZATION_LOCAL_DIR`, defaults to `.agent_configs/`).
  4. Caller-supplied defaults.
- Local directory layout: `metadata.yaml` + `instructions.md` + `tools.json` + `skills/` per candidate, with `baseline/` fallback.
- 3 tool description formats: `tool_descriptions` dict, `toolDescriptions` (legacy camelCase), and OpenAI function-calling `tools` list.
- Skill loading from `SKILL.md` files with YAML frontmatter.
- Resolver API persists fetched configs to local directory for offline use.
- Path traversal (zip-slip) protection on all untrusted path inputs.
