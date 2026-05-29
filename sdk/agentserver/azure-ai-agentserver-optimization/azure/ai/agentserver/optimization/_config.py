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
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from azure.core.credentials import TokenCredential

from azure.ai.agentserver.optimization._models import (
    CandidateConfig,
    MetadataConfig,
    OptimizationConfig,
    Skill,
)
from azure.ai.agentserver.optimization._resolver import resolve_candidate

logger = logging.getLogger(__name__)


def load_config(
    *,
    config_dir: str | Path | None = None,
    credential: TokenCredential | None = None,
) -> OptimizationConfig | None:
    """Load optimization config with graceful fallback.

    Resolution order (first match wins):

    1. **Inline JSON** — ``OPTIMIZATION_CONFIG`` env var contains the
       full config as a JSON string.  Used by temporary agent versions
       during evaluation; this path is being deprecated.
    2. **Resolver API** — ``OPTIMIZATION_CANDIDATE_ID`` and
       ``OPTIMIZATION_RESOLVE_ENDPOINT`` are both set.  The endpoint
       should be the full job-scoped URL.  Fetches the candidate
       config from the remote optimization service and persists it
       to the local directory.
    3. **Local directory** — reads from
       ``<config_dir>/<candidate_id>/`` (or ``<config_dir>/baseline/``
       as fallback).  Defaults to ``.agent_configs/`` relative to the
       main script, overridable via ``OPTIMIZATION_LOCAL_DIR`` env var.
    4. When none of the above match, returns ``None``.

    :keyword config_dir: Path to the agent config directory.  When ``None``,
        falls back to the ``OPTIMIZATION_LOCAL_DIR`` env var, then
        to ``.agent_configs/`` next to the main script.
    :paramtype config_dir: str | Path | None
    :keyword credential: Optional credential for resolver API authentication.
        If omitted, resolver will not use authentication.
    :paramtype credential: ~azure.core.credentials.TokenCredential | None
    :return: The resolved optimization config, or ``None`` when no
        config source is found.
    :rtype: OptimizationConfig | None
    :raises ValueError: When a discovered config source is invalid
        (e.g. malformed JSON env var, unreadable metadata.yaml).
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
            raise ValueError(f"Bad {env_var} env var: {exc}") from exc

    # ── Priority 2: Candidate ID → resolver API ──────────────────────
    candidate_id = os.environ.get(OptimizationConfig.ENV_CANDIDATE_ID, "").strip()
    endpoint = (
        os.environ.get(OptimizationConfig.ENV_RESOLVE_ENDPOINT, "").strip().rstrip("/")
    )
    if candidate_id and endpoint:
        local_dir = _resolve_local_dir(config_dir)
        resolved = resolve_candidate(
            candidate_id, endpoint=endpoint, local_dir=local_dir, credential=credential
        )
        if resolved is not None:
            candidate = CandidateConfig.from_dict(resolved)
            logger.warning(
                "Loaded optimization config from resolver API for candidate %s",
                candidate_id,
            )
            return OptimizationConfig(
                instructions=candidate.instructions,
                model=candidate.model,
                temperature=candidate.temperature,
                skills=candidate.skills,
                skills_dir=resolved.get("skills_dir"),
                tool_definitions=candidate.tool_definitions,
                source=f"api:candidate:{candidate_id}",
                candidate_id=candidate_id,
            )
        logger.warning(
            "Failed to resolve candidate %s — falling through to local/defaults",
            candidate_id,
        )

    # ── Priority 3: Local directory (.agent_configs/) ──────────
    local_config = _load_local_dir(candidate_id or None, config_dir)
    if local_config is not None:
        logger.warning(
            "Loaded optimization config from local directory: %s (candidate_id=%s)",
            local_config.source,
            local_config.candidate_id,
        )
        return local_config

    # ── Priority 4: No config found ───────────────────────────────────
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
    :raises ValueError: When metadata.yaml exists but is unreadable or invalid.
    """
    if metadata_file.is_file():
        try:
            raw = yaml.safe_load(metadata_file.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError) as exc:
            raise ValueError(f"Invalid metadata file {metadata_file}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ValueError(
                f"Invalid metadata file {metadata_file}: expected a YAML mapping at the top level"
            )
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

        [{"type": "function", "function": {"name": "...",
         "description": "...", "parameters": {...}}}]

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
        logger.debug("Failed to read tools file %s: %s", tool_file, exc)
        return []


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
            logger.debug("Failed to read skill %s: %s", skill_file, exc)

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

    try:
        frontmatter = yaml.safe_load(fm_text) or {}
    except yaml.YAMLError as exc:
        logger.debug("Invalid YAML in skill frontmatter: %s", exc)
        frontmatter = {}
    if not isinstance(frontmatter, dict):
        logger.debug("Skill frontmatter is not a mapping, ignoring")
        frontmatter = {}

    return frontmatter, body
