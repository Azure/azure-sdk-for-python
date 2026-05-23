# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Candidate config resolution via the optimization service API.

Fetches candidate config and skill files from the remote optimization
service and persists them into the standard local directory layout::

    <local_dir>/
    └── <candidate_id>/
        ├── config.json
        └── skills/
            └── <skill_name>/
                └── SKILL.md
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import shutil
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from azure.ai.agentserver.optimization._models import (
    OptimizationConfig)

logger = logging.getLogger("azure.ai.agentserver.optimization")

_downloaded: set[str] = set()


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
    if candidate_id in _downloaded:
        if local_dir is not None and (local_dir / candidate_id).is_dir():
            logger.debug("Candidate %s already downloaded — skipping", candidate_id)
            return None
        logger.warning("Candidate %s was downloaded but folder is missing — re-downloading", candidate_id)
        _downloaded.discard(candidate_id)

    headers = _build_headers()

    # ── Step 1: Fetch config ─────────────────────────────────────────
    config = _api_get_json(f"{endpoint}/agent_optimization_jobs/{job_id}/candidates/{candidate_id}/config", headers)
    if config is None:
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
            _download_skill_files(endpoint, job_id, candidate_id, headers, candidate_path)
        except OSError as exc:
            logger.warning("Failed to persist candidate %s to disk: %s", candidate_id, exc)
        # Point skills_dir to the downloaded skills folder
        skills_path = candidate_path / OptimizationConfig.SKILLS_DIR
        if skills_path.is_dir():
            config["skills_dir"] = str(skills_path)

    _downloaded.add(candidate_id)
    return config


def _persist_to_local_layout(candidate_path: pathlib.Path, config: dict[str, Any]) -> None:
    """Write config into the standard local directory layout.

    Produces the same structure that ``_load_local_dir`` reads::

        <candidate_path>/
        ├── metadata.yaml
        ├── instructions.md
        └── tools.json

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
    tool_descs = config.get("tool_descriptions") or config.get("toolDescriptions")
    tools_list = config.get("tools")
    if tool_descs and isinstance(tool_descs, dict):
        tools_file = candidate_path / OptimizationConfig.TOOLS_FILE
        tools_file.write_text(json.dumps(tool_descs, indent=2, ensure_ascii=False), encoding="utf-8")
    elif tools_list and isinstance(tools_list, list):
        tools_file = candidate_path / OptimizationConfig.TOOLS_FILE
        tools_file.write_text(json.dumps(tools_list, indent=2, ensure_ascii=False), encoding="utf-8")

    logger.info("Persisted config to local layout: %s", candidate_path)


def _download_skill_files(
    endpoint: str,
    job_id: str,
    candidate_id: str,
    headers: dict[str, str],
    candidate_path: pathlib.Path,
) -> None:
    """Fetch manifest and download skill files into candidate_path/skills/<name>/SKILL.md."""
    manifest = _api_get_json(f"{endpoint}/agent_optimization_jobs/{job_id}/candidates/{candidate_id}", headers)
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
            f"{endpoint}/agent_optimization_jobs/{job_id}/candidates/{candidate_id}/files",
            headers,
            params={"path": file_path},
        )
        if content is None:
            logger.warning("Failed to download skill file: %s", file_path)
            continue

        # file_path is like "skills/math/SKILL.md" → write to skills_dir/math/SKILL.md
        rel_path = file_path
        prefix = OptimizationConfig.SKILLS_DIR + "/"
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix):]

        out_path = skills_dir / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        logger.info("  → %s (%d bytes)", out_path, len(content))


def _is_skill_file(file_entry: dict) -> bool:
    """Check if a manifest entry is a skill file."""
    path = file_entry.get("path", "")
    file_type = file_entry.get("type", "")
    return file_type == "skill" or path.startswith("skills/")


# ── HTTP helpers ─────────────────────────────────────────────────────


def _build_headers() -> dict[str, str]:
    headers: dict[str, str] = {"Accept": "application/json"}
    token = _get_bearer_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _api_get_json(url: str, headers: dict[str, str]) -> dict[str, Any] | None:
    """GET a JSON endpoint, return parsed dict or None on failure."""
    logger.debug("GET %s", url)
    try:
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError, OSError) as exc:
        logger.error("GET %s failed: %s", url, exc)
        return None


def _api_get_text(
    url: str, headers: dict[str, str], params: dict[str, str] | None = None
) -> str | None:
    """GET an endpoint, return response body as text or None on failure."""
    if params:
        query = "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in params.items())
        url = f"{url}?{query}"
    logger.debug("GET %s", url)
    try:
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError) as exc:
        logger.error("GET %s failed: %s", url, exc)
        return None


def _get_bearer_token() -> str | None:
    """Acquire a bearer token for the resolver API.

    Uses ``azure-identity`` if available; returns ``None`` otherwise.
    This keeps azure-identity as an optional dependency.
    """
    try:
        from azure.identity import DefaultAzureCredential  # type: ignore[import-untyped]

        cred = DefaultAzureCredential()
        token = cred.get_token("https://ai.azure.com/.default")
        return token.token
    except Exception:  # noqa: BLE001
        return None
