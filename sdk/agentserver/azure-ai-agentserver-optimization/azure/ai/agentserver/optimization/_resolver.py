# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Candidate config resolution via the optimization service API.

Fetches candidate config and skill files from the remote optimization
service and persists them into the standard local directory layout::

    <local_dir>/
    └── <candidate_id>/
        ├── metadata.yaml
        ├── instructions.md
        ├── tools.json
        └── skills/
            └── <skill_name>/
                └── SKILL.md
"""

from __future__ import annotations

import json
import logging
import pathlib
import shutil
from typing import Any

from azure.core import PipelineClient
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, RetryPolicy
from azure.core.rest import HttpRequest

from azure.ai.agentserver.optimization._models import OptimizationConfig

logger = logging.getLogger("azure.ai.agentserver.optimization")

_downloaded: set[str] = set()

# API path and version constants
_API_VERSION = "2025-11-15-preview"
_JOBS_PATH = "agent_optimization_jobs"
_AUTH_SCOPE = "https://ai.azure.com/.default"


def resolve_candidate(
    candidate_id: str,
    job_id: str,
    endpoint: str,
    local_dir: pathlib.Path | None = None,
) -> dict[str, Any] | None:
    """Resolve a candidate's full config from the optimization service.

    Downloads config and skills into ``local_dir/<candidate_id>/``
    following the standard local directory layout.
    Returns ``None`` if the call fails.
    """
    # Guard against path traversal in candidate_id
    if local_dir is not None:
        candidate_path_check = (local_dir / candidate_id).resolve()
        if not str(candidate_path_check).startswith(str(local_dir.resolve())):
            logger.error("Path traversal detected in candidate_id: %r — aborting", candidate_id)
            return None

    if candidate_id in _downloaded:
        if local_dir is not None and (local_dir / candidate_id).is_dir():
            logger.debug("Candidate %s already downloaded — skipping", candidate_id)
            return None
        logger.warning("Candidate %s was downloaded but folder is missing — re-downloading", candidate_id)
        _downloaded.discard(candidate_id)

    client = _build_client(endpoint)

    # ── Step 1: Fetch config ─────────────────────────────────────────
    config = _api_get_json(
        client,
        f"/{_JOBS_PATH}/{job_id}/candidates/{candidate_id}/config",
        params={"api-version": _API_VERSION},
    )
    if config is None:
        client.close()
        return None

    logger.info(
        "Resolved candidate %s: model=%s, instructions=%d chars, skills=%d, tool_descriptions=%d",
        candidate_id,
        config.get("model", "?"),
        len(config.get("instructions", "")),
        len(config.get("skills", [])),
        len(config.get("toolDescriptions", {}) or config.get("tool_descriptions", {})),
    )

    # ── Step 2: Persist to local directory layout ────────────────────
    if local_dir is not None:
        candidate_path = local_dir / candidate_id
        try:
            _persist_to_local_layout(candidate_path, config)
            _download_skill_files(client, job_id, candidate_id, candidate_path)
        except OSError as exc:
            logger.warning("Failed to persist candidate %s to disk: %s", candidate_id, exc)
        # Point skills_dir to the downloaded skills folder
        skills_path = candidate_path / OptimizationConfig.SKILLS_DIR
        if skills_path.is_dir():
            config["skills_dir"] = str(skills_path)

    client.close()
    _downloaded.add(candidate_id)
    return config


def _persist_to_local_layout(candidate_path: pathlib.Path, config: dict[str, Any]) -> None:
    """Write config into the standard local directory layout.

    Produces the same structure that ``_load_local_dir`` reads::

        <candidate_path>/
        ├── metadata.yaml
        ├── instructions.md
        ├── tools.json
        └── skills/
            └── <skill_name>/
                └── SKILL.md

    If the folder already exists it is removed and re-created.
    """
    if candidate_path.is_dir():
        logger.info("Overwriting existing candidate folder: %s", candidate_path)
        shutil.rmtree(candidate_path)

    candidate_path.mkdir(parents=True, exist_ok=True)

    # metadata.yaml
    meta_lines: list[str] = []
    if config.get("model"):
        meta_lines.append(f"model: {config['model']}")
    if config.get("temperature") is not None:
        meta_lines.append(f"temperature: {config['temperature']}")
    meta_lines.append(f"instruction_file: {OptimizationConfig.INSTRUCTIONS_FILE}")
    meta_lines.append(f"skill_dir: {OptimizationConfig.SKILLS_DIR}")
    meta_lines.append(f"tool_file: {OptimizationConfig.TOOLS_FILE}")
    meta_file = candidate_path / OptimizationConfig.METADATA_FILE
    meta_file.write_text("\n".join(meta_lines) + "\n", encoding="utf-8")

    # instructions.md
    instructions = config.get("instructions", "")
    if instructions:
        instr_file = candidate_path / OptimizationConfig.INSTRUCTIONS_FILE
        instr_file.write_text(instructions, encoding="utf-8")

    # tools.json — write tool_descriptions / toolDescriptions as dict format
    tool_data = config.get("tool_descriptions") or config.get("toolDescriptions")
    tools_list = config.get("tools")
    if tool_data and isinstance(tool_data, dict):
        tools_file = candidate_path / OptimizationConfig.TOOLS_FILE
        tools_file.write_text(json.dumps(tool_data, indent=2, ensure_ascii=False), encoding="utf-8")
    elif tools_list and isinstance(tools_list, list):
        tools_file = candidate_path / OptimizationConfig.TOOLS_FILE
        tools_file.write_text(json.dumps(tools_list, indent=2, ensure_ascii=False), encoding="utf-8")

    # skills/ — write inline skills as <skills_dir>/<name>/SKILL.md
    inline_skills = config.get("skills", [])
    if inline_skills and isinstance(inline_skills, list):
        skills_dir = candidate_path / OptimizationConfig.SKILLS_DIR
        for skill in inline_skills:
            if not isinstance(skill, dict) or not skill.get("name"):
                continue
            skill_name = skill["name"]
            skill_folder = skills_dir / skill_name
            skill_folder.mkdir(parents=True, exist_ok=True)
            # Build SKILL.md with YAML frontmatter
            lines: list[str] = ["---"]
            lines.append(f"name: {skill_name}")
            if skill.get("description"):
                lines.append(f"description: {skill['description']}")
            lines.append("---")
            if skill.get("body"):
                lines.append("")
                lines.append(skill["body"])
            skill_file = skill_folder / OptimizationConfig.SKILL_FILE
            skill_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        logger.info("Persisted %d inline skill(s) to %s", len(inline_skills), skills_dir)

    logger.info("Persisted config to local layout: %s", candidate_path)


def _download_skill_files(
    client: PipelineClient,
    job_id: str,
    candidate_id: str,
    candidate_path: pathlib.Path,
) -> None:
    """Fetch manifest and download skill files into candidate_path/skills/<name>/SKILL.md."""
    manifest = _api_get_json(
        client,
        f"/{_JOBS_PATH}/{job_id}/candidates/{candidate_id}",
        params={"api-version": _API_VERSION},
    )
    if manifest is None:
        logger.debug("Could not fetch manifest for candidate %s", candidate_id)
        return

    files = manifest.get("files", [])
    skill_files = [f for f in files if _is_skill_file(f)]
    if not skill_files:
        logger.debug("No skill files in manifest for candidate %s", candidate_id)
        return

    logger.info(
        "Downloading %d skill file(s) for candidate %s",
        len(skill_files), candidate_id,
    )

    skills_dir = candidate_path / OptimizationConfig.SKILLS_DIR
    for file_entry in skill_files:
        file_path = file_entry.get("path", "")
        if not file_path:
            continue

        content = _api_get_text(
            client,
            f"/{_JOBS_PATH}/{job_id}/candidates/{candidate_id}/files",
            params={"path": file_path, "api-version": _API_VERSION},
        )
        if content is None:
            logger.warning("Failed to download skill file: %s", file_path)
            continue

        # file_path is like "skills/math/SKILL.md" → write to skills_dir/math/SKILL.md
        rel_path = file_path
        prefix = OptimizationConfig.SKILLS_DIR + "/"
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix):]

        out_path = (skills_dir / rel_path).resolve()
        if not str(out_path).startswith(str(skills_dir.resolve())):
            logger.warning("Path traversal detected in skill file path: %r — skipping", file_path)
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        logger.info("  → %s (%d bytes)", out_path, len(content))


def _is_skill_file(file_entry: dict) -> bool:
    """Check if a manifest entry is a skill file."""
    path = file_entry.get("path", "")
    file_type = file_entry.get("type", "")
    return file_type == "skill" or path.startswith("skills/")


# ── HTTP helpers (azure.core transport) ──────────────────────────────


def _build_client(endpoint: str) -> PipelineClient:
    """Create a PipelineClient with credential-based auth and retry."""
    policies: list = [RetryPolicy()]
    try:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        policies.insert(0, BearerTokenCredentialPolicy(credential, _AUTH_SCOPE))
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.debug("azure-identity not available or credentials failed — proceeding without auth")
    return PipelineClient(base_url=endpoint, policies=policies)


def _api_get_json(
    client: PipelineClient, path: str, params: dict[str, str] | None = None
) -> dict[str, Any] | None:
    """GET a JSON endpoint, return parsed dict or None on failure."""
    url = f"{client._base_url.rstrip('/')}{path}"  # pylint: disable=protected-access
    request = HttpRequest("GET", url, params=params)
    logger.debug("GET %s", url)
    try:
        response = client.send_request(request)
        if response.status_code != 200:
            logger.error("GET %s returned %d", url, response.status_code)
            return None
        return response.json()
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.error("GET %s failed: %s", url, exc)
        return None


def _api_get_text(
    client: PipelineClient, path: str, params: dict[str, str] | None = None
) -> str | None:
    """GET an endpoint, return response body as text or None on failure."""
    url = f"{client._base_url.rstrip('/')}{path}"  # pylint: disable=protected-access
    request = HttpRequest("GET", url, params=params)
    logger.debug("GET %s", url)
    try:
        response = client.send_request(request)
        if response.status_code != 200:
            logger.error("GET %s returned %d", url, response.status_code)
            return None
        return response.text()
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.error("GET %s failed: %s", url, exc)
        return None
