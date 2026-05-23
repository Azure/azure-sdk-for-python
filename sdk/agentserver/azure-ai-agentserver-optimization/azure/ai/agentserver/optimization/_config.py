# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Config loader — resolves optimization config from multiple sources.

The local directory uses a reserved folder structure::

    <local_dir>/                         (default: .agent_configs/)
    ├── baseline/                        (fallback candidate)
    │   ├── metadata.yaml                (model, temperature, file pointers)
    │   ├── instructions.md              (system prompt)
    │   ├── tools.json                   (tool descriptions — dict or list format)
    │   └── skills/                      (learned skills)
    │       └── <skill_name>/
    │           └── SKILL.md
    └── <candidate_id>/                  (same layout as baseline/)
        ├── metadata.yaml
        ├── instructions.md
        ├── tools.json
        └── skills/
            └── <skill_name>/
                └── SKILL.md

All folder and file names are defined as constants on
:class:`~OptimizationConfig` (e.g. ``METADATA_FILE``, ``SKILLS_DIR``,
``BASELINE_DIR``).
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from azure.ai.agentserver.optimization._models import (
    CandidateConfig,
    MetadataConfig,
    OptimizationConfig,
    Skill,
    ToolDescription,
    _parse_tools_list,
)
from azure.ai.agentserver.optimization._resolver import resolve_candidate

logger = logging.getLogger("azure.ai.agentserver.optimization")


def load_config(
    *,
    default_instructions: str = "You are a helpful assistant.",
    default_model: str | None = None,
    default_temperature: float | None = None,
    default_skills_dir: str | None = None,
) -> OptimizationConfig:
    """Load optimization config with graceful fallback.

    Resolution order (first match wins):

    1. **Inline JSON** — ``OPTIMIZATION_CONFIG`` env var contains the
       full config as a JSON string.  Used by temporary agent versions
       during evaluation; this path is being deprecated.
    2. **Resolver API** — ``OPTIMIZATION_CANDIDATE_ID``,
       ``OPTIMIZATION_JOB_ID``, and ``OPTIMIZATION_RESOLVE_ENDPOINT``
       are all set.  Fetches the candidate config from the remote
       optimization service and persists it to the local directory.
    3. **Local directory** — reads from
       ``<local_dir>/<candidate_id>/`` (or ``baseline/`` as fallback).
       The local directory defaults to ``.agent_configs/`` relative to
       the main script, overridable via ``OPTIMIZATION_LOCAL_DIR``.
    4. **Defaults** — returns the caller-supplied defaults unchanged.
       The agent works exactly as if optimization were not installed.

    Safe to call at module load time.  Any unexpected error is caught
    and logged — the caller always gets a valid config back.
    """
    try:
        return _load_config_inner(
            default_instructions=default_instructions,
            default_model=default_model,
            default_temperature=default_temperature,
            default_skills_dir=default_skills_dir,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Unexpected error loading optimization config — returning defaults: %s", exc)
        model = default_model or os.environ.get("MODEL_DEPLOYMENT_NAME")
        return OptimizationConfig(
            instructions=default_instructions,
            model=model,
            temperature=default_temperature,
            skills_dir=default_skills_dir,
            source="defaults",
        )


def _load_config_inner(
    *,
    default_instructions: str,
    default_model: str | None,
    default_temperature: float | None,
    default_skills_dir: str | None,
) -> OptimizationConfig:
    """Internal config loader — may raise on unexpected errors."""
    # ── Priority 1: Inline JSON env var (used by temp agent versions, deprecating) ─
    env_var = OptimizationConfig.ENV_CONFIG
    raw_config = os.environ.get(env_var, "").strip()
    if raw_config:
        try:
            cfg = json.loads(raw_config)
            candidate = CandidateConfig.from_dict(cfg)
            logger.warning(
                "Loaded optimization config from %s env var (%d chars instructions)",
                env_var, len(candidate.instructions or ""),
            )
            return OptimizationConfig(
                instructions=candidate.instructions or default_instructions,
                model=candidate.model or default_model,
                temperature=candidate.temperature if candidate.temperature is not None else default_temperature,
                skills=candidate.skills,
                skills_dir=cfg.get("skills_dir", default_skills_dir),
                tool_descriptions=candidate.tool_descriptions,
                source=f"env:{env_var}",
            )
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Bad %s env var: %s", env_var, exc)

    # ── Priority 2: Candidate ID → resolver API ──────────────────────
    candidate_id = os.environ.get(OptimizationConfig.ENV_CANDIDATE_ID, "").strip()
    job_id = os.environ.get(OptimizationConfig.ENV_JOB_ID, "").strip()
    endpoint = os.environ.get(OptimizationConfig.ENV_RESOLVE_ENDPOINT, "").strip().rstrip("/")
    if candidate_id and job_id and endpoint:
        local_dir = _resolve_local_dir()
        resolved = resolve_candidate(candidate_id, job_id=job_id, endpoint=endpoint, local_dir=local_dir)
        if resolved is not None:
            candidate = CandidateConfig.from_dict(resolved)
            logger.warning(
                "Loaded optimization config from resolver API for candidate %s",
                candidate_id,
            )
            return OptimizationConfig(
                instructions=candidate.instructions or default_instructions,
                model=candidate.model or default_model,
                temperature=candidate.temperature if candidate.temperature is not None else default_temperature,
                skills=candidate.skills,
                skills_dir=resolved.get("skills_dir", default_skills_dir),
                tool_descriptions=candidate.tool_descriptions,
                source=f"api:candidate:{candidate_id}",
                candidate_id=candidate_id,
                job_id=job_id,
            )
        logger.warning(
            "Failed to resolve candidate %s — falling through to local/defaults",
            candidate_id,
        )

    # ── Priority 3: Local directory (.agent_configs/) ──────────
    local_config = _load_local_dir(
        candidate_id or None, default_instructions,
        default_model, default_temperature, default_skills_dir,
    )
    if local_config is not None:
        logger.warning(
            "Loaded optimization config from local directory: %s (candidate_id=%s)",
            local_config.source, local_config.candidate_id,
        )
        return local_config

    # ── Priority 4: Defaults ─────────────────────────────────────────
    model = default_model or os.environ.get("MODEL_DEPLOYMENT_NAME")
    return OptimizationConfig(
        instructions=default_instructions,
        model=model,
        temperature=default_temperature,
        skills_dir=default_skills_dir,
        source="defaults",
    )


def _resolve_local_dir() -> Path:
    """Resolve the local optimization directory path.

    Falls back to :pyattr:`OptimizationConfig.DEFAULT_LOCAL_DIR`
    (``".agent_configs"``) when the env var is not set.
    """
    local_dir_env = os.environ.get(OptimizationConfig.ENV_LOCAL_DIR, "").strip()
    explicitly_set = bool(local_dir_env)
    local_dir = Path(local_dir_env) if explicitly_set else Path(OptimizationConfig.DEFAULT_LOCAL_DIR)

    # Guard: reject paths with ".." components (path traversal)
    if ".." in local_dir.parts:
        logger.warning(
            "OPTIMIZATION_LOCAL_DIR contains '..' path traversal: %r — ignoring",
            local_dir_env,
        )
        local_dir = Path(OptimizationConfig.DEFAULT_LOCAL_DIR)
        explicitly_set = False

    if not local_dir.is_absolute():
        import sys
        main_mod = sys.modules.get("__main__")
        main_file = getattr(main_mod, "__file__", None) if main_mod else None
        if main_file is not None:
            local_dir = Path(main_file).resolve().parent / local_dir
    if explicitly_set and not local_dir.is_dir():
        logger.warning(
            "OPTIMIZATION_LOCAL_DIR is set to %r but the directory does not exist",
            str(local_dir),
        )
    return local_dir


def _load_local_dir(
    candidate_id: str | None,
    default_instructions: str,
    default_model: str | None,
    default_temperature: float | None,
    default_skills_dir: str | None,
) -> OptimizationConfig | None:
    """Load optimization config from a local directory."""
    local_dir = _resolve_local_dir()
    if not local_dir.is_dir():
        return None

    candidate_path = _resolve_candidate_folder(local_dir, candidate_id)
    if candidate_path is None:
        return None

    metadata_file = candidate_path / OptimizationConfig.METADATA_FILE

    return _load_candidate_from_metadata(
        candidate_path, metadata_file, candidate_id,
        default_instructions, default_model, default_temperature, default_skills_dir,
    )


def _load_candidate_from_metadata(
    candidate_path: Path,
    metadata_file: Path,
    candidate_id: str | None,
    default_instructions: str,
    default_model: str | None,
    default_temperature: float | None,
    default_skills_dir: str | None,
) -> OptimizationConfig | None:
    """Load candidate config from metadata.yaml + instructions.md layout.

    If ``metadata_file`` does not exist, all default paths
    (instructions.md, skills/, tools.json) are used.
    """
    if metadata_file.is_file():
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError:
            raw = _parse_simple_yaml(metadata_file)
        else:
            try:
                raw = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
            except (yaml.YAMLError, OSError) as exc:
                logger.warning("Failed to read %s: %s", metadata_file, exc)
                raw = {}
    else:
        raw = {}

    meta = MetadataConfig.from_dict(raw)

    # Read instructions from the referenced file (guard against traversal)
    instructions_path = candidate_path / meta.instruction_file
    if _is_safe_child(candidate_path, instructions_path) and instructions_path.is_file():
        instructions = instructions_path.read_text(encoding="utf-8").strip()
    else:
        if not _is_safe_child(candidate_path, instructions_path):
            logger.warning("Path traversal in instruction_file: %r", meta.instruction_file)
        instructions = default_instructions

    # Resolve skills directory (guard against traversal)
    skills_path = candidate_path / meta.skill_dir
    if _is_safe_child(candidate_path, skills_path) and skills_path.resolve().is_dir():
        skills = _load_skills_from_dir(skills_path.resolve())
        skills_dir = str(skills_path.resolve())
    else:
        if not _is_safe_child(candidate_path, skills_path):
            logger.warning("Path traversal in skill_dir: %r", meta.skill_dir)
        skills = []
        skills_dir = default_skills_dir

    # Load tool descriptions (guard against traversal)
    tool_file_path = candidate_path / meta.tool_file
    if _is_safe_child(candidate_path, tool_file_path):
        tool_descriptions = _load_tool_descriptions(tool_file_path)
    else:
        logger.warning("Path traversal in tool_file: %r", meta.tool_file)
        tool_descriptions = {}

    return OptimizationConfig(
        instructions=instructions,
        model=meta.model or default_model,
        temperature=meta.temperature if meta.temperature is not None else default_temperature,
        skills=skills,
        skills_dir=skills_dir,
        tool_descriptions=tool_descriptions,
        source=f"local:{candidate_path}",
        candidate_id=candidate_id,
    )


def _load_tool_descriptions(tool_file: Path) -> dict[str, ToolDescription]:
    """Load tool descriptions from a tools.json file.

    Supports both dict format ``{name: {description, parameters}}``
    and OpenAI function-calling list format ``[{type, function: {name, ...}}]``.
    """
    if not tool_file.is_file():
        return {}
    try:
        raw = tool_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, dict):
            return {
                name: ToolDescription.from_dict(v) if isinstance(v, dict) else ToolDescription(description=str(v))
                for name, v in data.items()
            }
        if isinstance(data, list):
            return _parse_tools_list(data)
        return {}
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read tools file %s: %s", tool_file, exc)
        return {}


def _parse_simple_yaml(path: Path) -> dict:
    """Minimal key: value parser for metadata.yaml when PyYAML is not installed.

    Coerces numeric-looking values to float/int and recognizes
    null/true/false literals.
    """
    result: dict = {}
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip()] = _coerce_yaml_value(value.strip())
    except OSError as exc:
        logger.warning("Failed to read %s: %s", path, exc)
    return result


def _coerce_yaml_value(value: str) -> Any:
    """Coerce a YAML scalar string to the appropriate Python type."""
    if not value or value in ("null", "~"):
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def _resolve_candidate_folder(local_dir: Path, candidate_id: str | None) -> Path | None:
    """Pick the candidate folder from the local optimization dir.

    Returns ``local_dir/<candidate_id>`` if it exists, otherwise falls
    back to ``local_dir/baseline/``.  Returns ``None`` if neither exists.
    """
    if candidate_id:
        exact = local_dir / candidate_id
        if not _is_safe_child(local_dir, exact):
            logger.warning("Path traversal detected in candidate_id: %r", candidate_id)
            return None
        if exact.is_dir():
            return exact
    baseline = local_dir / OptimizationConfig.BASELINE_DIR
    return baseline if baseline.is_dir() else None


def _is_safe_child(parent: Path, child: Path) -> bool:
    """Return True if *child* is strictly inside *parent* (no traversal)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _load_skills_from_dir(skills_dir: Path) -> list[Skill]:
    """Load skills from a directory of skill folders.

    Expected layout::

        skills/
        └── <skill_name>/
            └── SKILL.md
    """
    if not skills_dir.is_dir():
        return []

    skills: list[Skill] = []
    for skill_folder in sorted(skills_dir.iterdir()):
        if not skill_folder.is_dir():
            continue
        skill_file = skill_folder / OptimizationConfig.SKILL_FILE
        if not skill_file.is_file():
            continue
        try:
            content = skill_file.read_text(encoding="utf-8").strip()
            frontmatter, body = _parse_skill_frontmatter(content)
            name = frontmatter.get("name", skill_folder.name)
            description = frontmatter.get("description", "")
            if not frontmatter and body:
                lines = body.split("\n", 1)
                description = lines[0].lstrip("#").strip()
                body = lines[1].strip() if len(lines) > 1 else ""
            skills.append(Skill(name=name, description=description, body=body))
        except OSError as exc:
            logger.warning("Failed to read skill %s: %s", skill_file, exc)

    return skills


def _parse_skill_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a SKILL.md file."""
    if not content.startswith("---"):
        return {}, content

    end = content.find("---", 3)
    if end == -1:
        return {}, content

    fm_text = content[3:end].strip()
    body = content[end + 3:].strip()

    frontmatter: dict = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body
