# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Config loader — resolves optimization config from multiple sources.

The local directory uses a reserved folder structure::

    <local_dir>/                         (default: .agent_configs/)
    ├── baseline/                        (fallback candidate)
    │   ├── metadata.yaml                (model, temperature, file pointers)
    │   ├── instructions.md              (system prompt)
    │   ├── tools.json                   (tool definitions — list format)
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
)
from azure.ai.agentserver.optimization._resolver import resolve_candidate

logger = logging.getLogger("azure.ai.agentserver.optimization")

# Header name used by the optimization service to pass candidate ID per request.
OPTIMIZATION_CANDIDATE_HEADER = "x-foundry-optimization-candidate-id"


def _get_candidate_id_from_request() -> str | None:
    """Try to extract the candidate ID from the current HTTP request header.

    Supports Flask/Quart (``flask.request``) and FastAPI/Starlette
    (``starlette.requests.Request`` via contextvars).  Returns ``None``
    when no framework is detected or the header is absent.
    """
    # Flask / Quart — thread-local request proxy
    try:
        from flask import request as flask_request  # type: ignore[import-untyped]

        value = flask_request.headers.get(OPTIMIZATION_CANDIDATE_HEADER, "").strip()
        if value:
            return value
    except Exception:  # noqa: BLE001
        pass

    return None


def load_config(
    *,
    config_dir: str | Path | None = None,
    candidate_id: str | None = None,
    required: bool = True,
) -> OptimizationConfig | None:
    """Load optimization config with graceful fallback.

    Resolution order (first match wins):

    1. **Inline JSON** — ``OPTIMIZATION_CONFIG`` env var contains the
       full config as a JSON string.  Used by temporary agent versions
       during evaluation; this path is being deprecated.
    2. **Resolver API** — candidate ID is resolved from (in order):
       *candidate_id* parameter, the ``X-Foundry-Optimization-Candidate-Id``
       request header (auto-detected from Flask/Quart), or the
       ``OPTIMIZATION_CANDIDATE_ID`` env var.  Combined with
       ``OPTIMIZATION_RESOLVE_ENDPOINT`` to fetch the candidate config
       from the remote optimization service and persist it locally.
    3. **Local directory** — reads from
       ``<config_dir>/<candidate_id>/`` (or ``<config_dir>/baseline/``
       as fallback).  Defaults to ``.agent_configs/`` relative to the
       main script, overridable via ``OPTIMIZATION_LOCAL_DIR`` env var.
    4. When none of the above match:

       - ``required=True``  (default) → raises ``ValueError``.
       - ``required=False`` → returns ``None``.

    :keyword config_dir: Path to the agent config directory.  When ``None``,
        falls back to the ``OPTIMIZATION_LOCAL_DIR`` env var, then
        to ``.agent_configs/`` next to the main script.
    :paramtype config_dir: str | Path | None
    :keyword candidate_id: Candidate identifier.  When ``None`` (the default),
        the value is automatically extracted from the
        ``X-Foundry-Optimization-Candidate-Id`` request header (Flask/Quart) or
        the ``OPTIMIZATION_CANDIDATE_ID`` env var.  Explicit values
        take precedence over both auto-detection sources.
    :paramtype candidate_id: str | None
    :keyword required: If ``True`` (default), raise ``ValueError`` when no
        config source is found.  Set to ``False`` during initial
        setup or testing.
    :paramtype required: bool
    :return: The resolved optimization config, or ``None`` when not found
        and *required* is ``False``.
    :rtype: OptimizationConfig | None
    :raises ValueError: When *required* is ``True`` and no config source
        (env var, resolver API, or local directory) provides a
        valid config.
    """
    try:
        return _load_config_inner(
            config_dir=config_dir, candidate_id=candidate_id, required=required
        )
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.error("Unexpected error loading optimization config: %s", exc)
        return None


def _load_config_inner(
    *,
    config_dir: str | Path | None,
    candidate_id: str | None,
    required: bool,
) -> OptimizationConfig | None:
    """Internal config loader — may raise on unexpected errors.

    :keyword config_dir: Path to the agent config directory.
    :paramtype config_dir: str | Path | None
    :keyword candidate_id: Candidate identifier (from parameter or header).
    :paramtype candidate_id: str | None
    :keyword required: Whether to raise on missing config.
    :paramtype required: bool
    :return: Resolved config or ``None``.
    :rtype: OptimizationConfig | None
    """
    # ── Priority 1: Inline JSON env var (used by temp agent versions, deprecating) ─
    env_var = OptimizationConfig.ENV_CONFIG
    raw_config = os.environ.get(env_var, "").strip()
    if raw_config:
        try:
            cfg = json.loads(raw_config)
            candidate = CandidateConfig.from_dict(cfg)
            logger.warning(
                "Loaded optimization config from %s env var (%d chars instructions)",
                env_var,
                len(candidate.instructions or ""),
            )
            return OptimizationConfig(
                instructions=candidate.instructions,
                model=candidate.model,
                temperature=candidate.temperature,
                skills=candidate.skills,
                tool_definitions=candidate.tool_definitions,
                source=f"env:{env_var}",
            )
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Bad %s env var: %s", env_var, exc)

    # ── Priority 2: Candidate ID → resolver API ──────────────────────
    # Resolution: explicit param > request header > env var.
    resolved_candidate_id = (
        (candidate_id or "").strip()
        or _get_candidate_id_from_request()
        or os.environ.get(OptimizationConfig.ENV_CANDIDATE_ID, "").strip()
    )
    endpoint = (
        os.environ.get(OptimizationConfig.ENV_RESOLVE_ENDPOINT, "").strip().rstrip("/")
    )
    if resolved_candidate_id and endpoint:
        local_dir = _resolve_local_dir(config_dir)
        resolved = resolve_candidate(
            resolved_candidate_id, endpoint=endpoint, local_dir=local_dir
        )
        if resolved is not None:
            candidate = CandidateConfig.from_dict(resolved)
            logger.warning(
                "Loaded optimization config from resolver API for candidate %s",
                resolved_candidate_id,
            )
            return OptimizationConfig(
                instructions=candidate.instructions,
                model=candidate.model,
                temperature=candidate.temperature,
                skills=candidate.skills,
                skills_dir=resolved.get("skills_dir"),
                tool_definitions=candidate.tool_definitions,
                source=f"api:candidate:{resolved_candidate_id}",
                candidate_id=resolved_candidate_id,
            )
        logger.warning(
            "Failed to resolve candidate %s — falling through to local/defaults",
            resolved_candidate_id,
        )

    # ── Priority 3: Local directory (.agent_configs/) ──────────
    local_config = _load_local_dir(resolved_candidate_id or None, config_dir)
    if local_config is not None:
        logger.warning(
            "Loaded optimization config from local directory: %s (candidate_id=%s)",
            local_config.source,
            local_config.candidate_id,
        )
        return local_config

    # ── Priority 4: No config found ───────────────────────────────────
    if required:
        local_dir = _resolve_local_dir(config_dir)
        raise ValueError(
            "No optimization config found. Prepare a baseline folder at "
            f"'{local_dir / OptimizationConfig.BASELINE_DIR}' with a "
            "metadata.yaml file, or pass required=False."
        )
    logger.warning("No optimization config found — returning None")
    return None


def _resolve_local_dir(config_dir: str | Path | None = None) -> Path:
    """Resolve the local optimization directory path.

    Priority: *config_dir* argument → ``OPTIMIZATION_LOCAL_DIR`` env
    var → ``OptimizationConfig.DEFAULT_LOCAL_DIR`` (``.agent_configs``).

    :param config_dir: Explicit config directory path.
    :type config_dir: str | Path | None
    :return: Resolved directory path.
    :rtype: Path
    """
    if config_dir is not None:
        local_dir = Path(config_dir)
        explicitly_set = True
    else:
        local_dir_env = os.environ.get(OptimizationConfig.ENV_LOCAL_DIR, "").strip()
        explicitly_set = bool(local_dir_env)
        local_dir = (
            Path(local_dir_env)
            if explicitly_set
            else Path(OptimizationConfig.DEFAULT_LOCAL_DIR)
        )

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
    config_dir: str | Path | None,
) -> OptimizationConfig | None:
    """Load optimization config from a local directory.

    :param candidate_id: Candidate identifier, or ``None`` for baseline.
    :type candidate_id: str | None
    :param config_dir: Explicit config directory path.
    :type config_dir: str | Path | None
    :return: Loaded config or ``None`` if directory does not exist.
    :rtype: OptimizationConfig | None
    """
    local_dir = _resolve_local_dir(config_dir)
    if not local_dir.is_dir():
        return None

    candidate_path = _resolve_candidate_folder(local_dir, candidate_id)
    if candidate_path is None:
        return None

    metadata_file = candidate_path / OptimizationConfig.METADATA_FILE

    return _load_candidate_from_metadata(candidate_path, metadata_file, candidate_id)


def _load_candidate_from_metadata(
    candidate_path: Path,
    metadata_file: Path,
    candidate_id: str | None,
) -> OptimizationConfig | None:
    """Load candidate config from metadata.yaml + instructions.md layout.

    If ``metadata_file`` does not exist, all default paths
    (instructions.md, skills/, tools.json) are used.

    :param candidate_path: Path to the candidate folder.
    :type candidate_path: Path
    :param metadata_file: Path to the metadata.yaml file.
    :type metadata_file: Path
    :param candidate_id: Candidate identifier.
    :type candidate_id: str | None
    :return: Loaded config or ``None``.
    :rtype: OptimizationConfig | None
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

    # Read instructions from the referenced file
    instructions_path = candidate_path / meta.instruction_file
    if instructions_path.is_file():
        instructions: str | None = instructions_path.read_text(encoding="utf-8").strip()
    else:
        instructions = None

    # Resolve skills directory
    skills_dir: str | None
    skills_path = candidate_path / meta.skill_dir
    if skills_path.resolve().is_dir():
        skills_dir = str(skills_path.resolve())
    else:
        skills_dir = None

    # Load tool definitions
    tool_file_path = candidate_path / meta.tool_file
    tool_definitions = _load_tool_definitions(tool_file_path)

    return OptimizationConfig(
        instructions=instructions,
        model=meta.model,
        temperature=meta.temperature,
        skills_dir=skills_dir,
        tool_definitions=tool_definitions,
        source=f"local:{candidate_path}",
        candidate_id=candidate_id,
    )


def _load_tool_definitions(tool_file: Path) -> list[dict]:
    """Load tool definitions from a tools.json file.

    Expects the OpenAI function-calling list format::

        [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]

    :param tool_file: Path to the tools.json file.
    :type tool_file: Path
    :return: List of tool definition dicts.
    :rtype: list[dict]
    """
    if not tool_file.is_file():
        return []
    try:
        raw = tool_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read tools file %s: %s", tool_file, exc)
        return []


def _parse_simple_yaml(path: Path) -> dict:
    """Minimal key: value parser for metadata.yaml when PyYAML is not installed.

    Coerces numeric-looking values to float/int and recognizes
    null/true/false literals.

    :param path: Path to the YAML file.
    :type path: Path
    :return: Parsed key-value mapping.
    :rtype: dict
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
    """Coerce a YAML scalar string to the appropriate Python type.

    :param value: Raw YAML scalar string.
    :type value: str
    :return: Coerced Python value.
    :rtype: Any
    """
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

    :param local_dir: Root optimization directory.
    :type local_dir: Path
    :param candidate_id: Candidate identifier.
    :type candidate_id: str | None
    :return: Resolved candidate folder path, or ``None``.
    :rtype: Path | None
    """
    if candidate_id:
        exact = local_dir / candidate_id
        if exact.is_dir():
            return exact
    baseline = local_dir / OptimizationConfig.BASELINE_DIR
    return baseline if baseline.is_dir() else None


def load_skills_from_dir(skills_dir: Path) -> list[Skill]:
    """Load skills from a directory of skill folders.

    Expected layout::

        skills/
        └── <skill_name>/
            └── SKILL.md

    :param skills_dir: Path to the skills directory.
    :type skills_dir: Path
    :return: List of loaded skills.
    :rtype: list[Skill]
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
    """Extract YAML frontmatter and body from a SKILL.md file.

    :param content: Raw SKILL.md content.
    :type content: str
    :return: Tuple of (frontmatter dict, body text).
    :rtype: tuple[dict, str]
    """
    if not content.startswith("---"):
        return {}, content

    end = content.find("---", 3)
    if end == -1:
        return {}, content

    fm_text = content[3:end].strip()
    body = content[end + 3 :].strip()

    frontmatter: dict = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()

    return frontmatter, body
