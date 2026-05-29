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
_AUTH_SCOPE = "https://ai.azure.com/.default"


def resolve_candidate(
    candidate_id: str,
    endpoint: str,
    local_dir: pathlib.Path | None = None,
) -> dict[str, Any] | None:
    """Resolve a candidate's full config from the optimization service.

    ``endpoint`` should be the full job-scoped URL,
    The resolver appends ``/candidates/{candidate_id}/config``.

    Downloads config and skills into ``local_dir/<candidate_id>/``
    following the standard local directory layout.
    Returns ``None`` if the call fails.

    :param candidate_id: Candidate identifier.
    :type candidate_id: str
    :param endpoint: Full job-scoped endpoint URL.
    :type endpoint: str
    :param local_dir: Local directory for persisting config.
    :type local_dir: pathlib.Path | None
    :return: Candidate config dict, or ``None`` on failure.
    :rtype: dict[str, Any] | None
    """
    if candidate_id in _downloaded:
        if local_dir is not None and (local_dir / candidate_id).is_dir():
            logger.warning("Candidate %s already downloaded — skipping", candidate_id)
            return None
        logger.warning(
            "Candidate %s was downloaded but folder is missing — re-downloading",
            candidate_id,
        )
        _downloaded.discard(candidate_id)

    client = _build_client(endpoint)

    # ── Step 1: Fetch config ─────────────────────────────────────────
    config = _api_get_json(
        client,
        f"/candidates/{candidate_id}/config",
        params={"api-version": _API_VERSION},
    )
    if config is None:
        client.close()
        return None

    logger.info(
        "Resolved candidate %s: model=%s, instructions=%d chars, skills=%d, tool_definitions=%d",
        candidate_id,
        config.get("model", "?"),
        len(config.get("instructions", "")),
        len(config.get("skills", [])),
        len(config.get("tools", [])),
    )

    # ── Step 2: Persist to local directory layout ────────────────────
    if local_dir is not None:
        candidate_path = local_dir / candidate_id
        try:
            _persist_to_local_layout(candidate_path, config)
            _download_skill_files(client, candidate_id, candidate_path)
        except OSError as exc:
            logger.warning(
                "Failed to persist candidate %s to disk: %s", candidate_id, exc
            )
        # Point skills_dir to the downloaded skills folder
        skills_path = candidate_path / OptimizationConfig.SKILLS_DIR
        if skills_path.is_dir():
            config["skills_dir"] = str(skills_path)

    client.close()
    _downloaded.add(candidate_id)
    return config


def _persist_to_local_layout(
    candidate_path: pathlib.Path, config: dict[str, Any]
) -> None:
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

    :param candidate_path: Target directory for the candidate layout.
    :type candidate_path: pathlib.Path
    :param config: Candidate config dict from the API.
    :type config: dict[str, Any]
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

    # tools.json — write tool definitions in list format
    tools_list = config.get("tools")
    if tools_list and isinstance(tools_list, list):
        tools_file = candidate_path / OptimizationConfig.TOOLS_FILE
        tools_file.write_text(
            json.dumps(tools_list, indent=2, ensure_ascii=False), encoding="utf-8"
        )

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
        logger.info(
            "Persisted %d inline skill(s) to %s", len(inline_skills), skills_dir
        )

    logger.info("Persisted config to local layout: %s", candidate_path)


def _download_skill_files(
    client: PipelineClient,
    candidate_id: str,
    candidate_path: pathlib.Path,
) -> None:
    """Fetch manifest and download skill files into candidate_path/skills/<name>/SKILL.md.

    :param client: Azure PipelineClient for API calls.
    :type client: PipelineClient
    :param candidate_id: Candidate identifier.
    :type candidate_id: str
    :param candidate_path: Local directory for the candidate.
    :type candidate_path: pathlib.Path
    """
    manifest = _api_get_json(
        client,
        f"/candidates/{candidate_id}",
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
        len(skill_files),
        candidate_id,
    )

    skills_dir = candidate_path / OptimizationConfig.SKILLS_DIR
    for file_entry in skill_files:
        file_path = file_entry.get("path", "")
        if not file_path:
            continue

        content = _api_get_text(
            client,
            f"/candidates/{candidate_id}/files",
            params={"path": file_path, "api-version": _API_VERSION},
        )
        if content is None:
            logger.warning("Failed to download skill file: %s", file_path)
            continue

        # file_path is like "skills/math/SKILL.md" → write to skills_dir/math/SKILL.md
        rel_path = file_path
        prefix = OptimizationConfig.SKILLS_DIR + "/"
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix) :]

        out_path = (skills_dir / rel_path).resolve()
        if not str(out_path).startswith(str(skills_dir.resolve())):
            logger.warning(
                "Path traversal detected in skill file path: %r — skipping", file_path
            )
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        logger.info("  → %s (%d bytes)", out_path, len(content))


def _is_skill_file(file_entry: dict) -> bool:
    """Check if a manifest entry is a skill file.

    :param file_entry: Manifest entry dict.
    :type file_entry: dict
    :return: ``True`` if the entry represents a skill file.
    :rtype: bool
    """
    path = file_entry.get("path", "")
    file_type = file_entry.get("type", "")
    return file_type == "skill" or path.startswith("skills/")


# ── HTTP helpers (azure.core transport) ──────────────────────────────


def _build_client(endpoint: str) -> PipelineClient:
    """Create a PipelineClient with credential-based auth and retry.

    :param endpoint: Base URL for the API.
    :type endpoint: str
    :return: Configured pipeline client.
    :rtype: PipelineClient
    """
    policies: list = [RetryPolicy()]
    try:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        policies.insert(0, BearerTokenCredentialPolicy(credential, _AUTH_SCOPE))
    except Exception:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.debug(
            "azure-identity not available or credentials failed — proceeding without auth"
        )
    return PipelineClient(base_url=endpoint, policies=policies)


def _api_get_json(
    client: PipelineClient, path: str, params: dict[str, str] | None = None
) -> dict[str, Any] | None:
    """GET a JSON endpoint, return parsed dict or None on failure.

    :param client: Azure PipelineClient.
    :type client: PipelineClient
    :param path: API path to append to the base URL.
    :type path: str
    :param params: Query parameters.
    :type params: dict[str, str] | None
    :return: Parsed response dict or ``None``.
    :rtype: dict[str, Any] | None
    """
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
    """GET an endpoint, return response body as text or None on failure.

    :param client: Azure PipelineClient.
    :type client: PipelineClient
    :param path: API path to append to the base URL.
    :type path: str
    :param params: Query parameters.
    :type params: dict[str, str] | None
    :return: Response body text or ``None``.
    :rtype: str | None
    """
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
