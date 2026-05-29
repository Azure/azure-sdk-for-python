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

import yaml  # type: ignore[import-untyped]

from azure.core import PipelineClient
from azure.core.credentials import TokenCredential
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, RetryPolicy
from azure.core.rest import HttpRequest
from azure.identity import DefaultAzureCredential

from azure.ai.agentserver.optimization._models import OptimizationConfig

logger = logging.getLogger(__name__)

_downloaded: set[str] = set()

# API path and version constants
_API_VERSION = "2025-11-15-preview"
_AUTH_SCOPE = "https://ai.azure.com/.default"


def resolve_candidate(
    candidate_id: str,
    endpoint: str,
    local_dir: pathlib.Path | None = None,
    credential: TokenCredential | None = None,
) -> dict[str, Any] | None:
    """Resolve a candidate's full config from the optimization service.

    ``endpoint`` should be the full job-scoped URL,
    The resolver appends ``/candidates/{candidate_id}/config``.

    Downloads config and skills into ``local_dir/<candidate_id>/``
    following the standard local directory layout.
    Returns ``None`` only when the candidate is already available locally
    and no remote refresh is needed.

    :param candidate_id: Candidate identifier.
    :type candidate_id: str
    :param endpoint: Full job-scoped endpoint URL.
    :type endpoint: str
    :param local_dir: Local directory for persisting config.
    :type local_dir: pathlib.Path | None
    :param credential: Optional credential for bearer token auth.
        If omitted, resolver will not use authentication.
    :type credential: ~azure.core.credentials.TokenCredential | None
    :return: Candidate config dict, or ``None`` when an existing local copy is reused.
    :rtype: dict[str, Any] | None
    :raises ValueError: When remote config or required skill files cannot be fetched.
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

    with _build_client(endpoint, credential) as client:
        config = _fetch_candidate_config(client, candidate_id)

        logger.info(
            "Resolved candidate %s: model=%s, instructions=%d chars, "
            "skills=%d, tool_definitions=%d",
            candidate_id,
            config.get("model", "?"),
            len(config.get("instructions", "")),
            len(config.get("skills", [])),
            len(config.get("tools", [])),
        )

        if local_dir is not None:
            candidate_path = local_dir / candidate_id
            try:
                _persist_to_local_layout(candidate_path, config)
            except OSError as exc:
                logger.debug(
                    "Failed to persist candidate %s to disk: %s", candidate_id, exc
                )
            else:
                _download_skill_files(client, candidate_id, candidate_path)

                skills_path = candidate_path / OptimizationConfig.SKILLS_DIR
                if skills_path.is_dir():
                    config["skills_dir"] = str(skills_path)

        _downloaded.add(candidate_id)
        return config


def _fetch_candidate_config(client: PipelineClient, candidate_id: str) -> dict[str, Any]:
    """Fetch the primary candidate config payload.

    :param client: Azure PipelineClient for API calls.
    :type client: PipelineClient
    :param candidate_id: Candidate identifier.
    :type candidate_id: str
    :return: Candidate config payload.
    :rtype: dict[str, Any]
    :raises ValueError: When the candidate config cannot be fetched.
    """
    try:
        return _api_get_json(
            client,
            f"/candidates/{candidate_id}/config",
            params={"api-version": _API_VERSION},
        )
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        raise ValueError(
            f"Failed to fetch config for candidate {candidate_id}: {exc}"
        ) from exc


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
            fm: dict[str, str] = {"name": skill_name}
            if skill.get("description"):
                fm["description"] = skill["description"]
            fm_text = yaml.dump(
                fm, default_flow_style=False, allow_unicode=True, width=float("inf")
            ).rstrip("\n")
            parts: list[str] = [f"---\n{fm_text}\n---"]
            if skill.get("body"):
                parts.append(skill["body"])
            skill_file = skill_folder / OptimizationConfig.SKILL_FILE
            skill_file.write_text("\n".join(parts) + "\n", encoding="utf-8")
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
    :raises ValueError: When the manifest or any referenced skill file
        is invalid or cannot be fetched.
    """
    try:
        manifest = _api_get_json(
            client,
            f"/candidates/{candidate_id}",
            params={"api-version": _API_VERSION},
        )
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        raise ValueError(
            f"Failed to fetch manifest for candidate {candidate_id}: {exc}"
        ) from exc

    if not isinstance(manifest, dict):
        raise ValueError(
            f"Invalid manifest for candidate {candidate_id}: expected an object response"
        )

    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise ValueError(
            f"Invalid manifest for candidate {candidate_id}: expected 'files' to be a list"
        )

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
            raise ValueError(
                f"Invalid manifest for candidate {candidate_id}: skill file path is empty"
            )

        try:
            content = _api_get_text(
                client,
                f"/candidates/{candidate_id}/files",
                params={"path": file_path, "api-version": _API_VERSION},
            )
        except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            raise ValueError(
                f"Failed to download skill file for candidate {candidate_id}: {file_path}: {exc}"
            ) from exc

        # file_path is like "skills/math/SKILL.md" → write to skills_dir/math/SKILL.md
        rel_path = file_path
        prefix = OptimizationConfig.SKILLS_DIR + "/"
        if rel_path.startswith(prefix):
            rel_path = rel_path[len(prefix) :]

        out_path = (skills_dir / rel_path).resolve()
        if not str(out_path).startswith(str(skills_dir.resolve())):
            raise ValueError(
                f"Invalid skill file path for candidate {candidate_id}: {file_path}"
            )

        if not isinstance(content, str):
            raise ValueError(
                f"Invalid skill file content for candidate {candidate_id}: {file_path}"
            )

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


def _build_client(endpoint: str, credential: TokenCredential | None = None) -> PipelineClient:
    """Create a PipelineClient with credential-based auth and retry.

    :param endpoint: Base URL for the API.
    :type endpoint: str
    :param credential: Azure credential for bearer token auth.
        If ``None``, falls back to ``DefaultAzureCredential``.
    :type credential: ~azure.core.credentials.TokenCredential | None
    :return: Configured pipeline client.
    :rtype: PipelineClient
    """
    policies: list = [RetryPolicy()]

    # Use provided credential or fall back to DefaultAzureCredential
    auth_credential = credential
    if auth_credential is None:
        try:
            auth_credential = DefaultAzureCredential()
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.debug("Could not create DefaultAzureCredential: %s", exc)

    if auth_credential is not None:
        policies.insert(0, BearerTokenCredentialPolicy(auth_credential, _AUTH_SCOPE))

    return PipelineClient(base_url=endpoint, policies=policies)


def _api_get_json(
    client: PipelineClient, path: str, params: dict[str, str] | None = None
) -> dict[str, Any]:
    """GET a JSON endpoint; raises on non-2xx or transport failure.

    :param client: Azure PipelineClient.
    :type client: PipelineClient
    :param path: API path to append to the base URL.
    :type path: str
    :param params: Query parameters.
    :type params: dict[str, str] | None
    :return: Parsed response dict.
    :rtype: dict[str, Any]
    """
    url = f"{client._base_url.rstrip('/')}{path}"  # pylint: disable=protected-access
    request = HttpRequest("GET", url, params=params)
    logger.debug("GET %s", url)
    response = client.send_request(request)
    response.raise_for_status()
    return response.json()


def _api_get_text(
    client: PipelineClient, path: str, params: dict[str, str] | None = None
) -> str:
    """GET an endpoint; raises on non-2xx or transport failure.

    :param client: Azure PipelineClient.
    :type client: PipelineClient
    :param path: API path to append to the base URL.
    :type path: str
    :param params: Query parameters.
    :type params: dict[str, str] | None
    :return: Response body text.
    :rtype: str
    """
    url = f"{client._base_url.rstrip('/')}{path}"  # pylint: disable=protected-access
    request = HttpRequest("GET", url, params=params)
    logger.debug("GET %s", url)
    response = client.send_request(request)
    response.raise_for_status()
    return response.text()
