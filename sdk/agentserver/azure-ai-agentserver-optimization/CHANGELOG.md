# Release History

## 1.0.0b2 (Unreleased)

### Features Added

### Breaking Changes

### Bugs Fixed

### Other Changes

## 1.0.0b1 (2026-05-24)

### Features Added

- Initial beta release.
- `load_config(*, config_dir)` — single-call config loader with 4-priority resolution and graceful fallback.
- `load_skills_from_dir(path)` — load skills from a directory on demand (not loaded inline by `load_config`).
- `OptimizationConfig` with instructions, model, temperature, skills, skills_dir, tool_definitions, source, and candidate_id.
- `OptimizationConfig.apply_tool_descriptions(tools)` — patch `__doc__`, `.description`, and `input_model` parameter descriptions on @tool-decorated functions from optimized tool definitions.
- `OptimizationConfig.compose_instructions()` — append skill catalog to instructions.
- `CandidateConfig` — typed representation of the resolver API payload.
- `Skill` — learned skill model (name, description, body).
- 4-priority resolution order:
  1. Inline JSON via `OPTIMIZATION_CONFIG` env var.
  2. Resolver API via `OPTIMIZATION_CANDIDATE_ID` + `OPTIMIZATION_RESOLVE_ENDPOINT` (endpoint is the full job-scoped URL).
  3. Local directory layout (`OPTIMIZATION_LOCAL_DIR` or `config_dir` param, defaults to `.agent_configs/`).
  4. No config found → returns `None`.
- Local directory layout: `metadata.yaml` + `instructions.md` + `tools.json` + `skills/` per candidate, with `baseline/` fallback.
- Tool definitions use the OpenAI function-calling list format exclusively.
- Skill loading from `SKILL.md` files with YAML frontmatter.
- Resolver API persists fetched configs and skill files to local directory for offline use.
- Path traversal (zip-slip) protection on skill file downloads from the API.
