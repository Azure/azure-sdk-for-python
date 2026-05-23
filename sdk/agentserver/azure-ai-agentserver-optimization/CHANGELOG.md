# Release History

## 1.0.0b1 (2026-05-22)

### Features Added

- Initial beta release.
- `load_config()` — single-call config loader with 4-priority resolution and graceful fallback (never crashes).
- `load_skills_from_dir(path)` — load skills from a directory on demand (not loaded inline by `load_config`).
- `OptimizationConfig` dataclass with instructions, model, temperature, skills_dir, tool descriptions, source tracking, candidate_id, and job_id.
- `OptimizationConfig.apply_tool_descriptions(tools)` — patch `__doc__` on @tool-decorated functions from optimized descriptions.
- `OptimizationConfig.compose_instructions()` — append skill catalog to instructions.
- `OptimizationConfig.get_tool_description(name)` / `get_tool_param_description(name, param)` — look up individual optimized descriptions.
- `CandidateConfig` — typed representation of the resolver API payload.
- `Skill` — learned skill model (name, description, body).
- `ToolDescription` — optimized tool description model (description, parameters).
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
