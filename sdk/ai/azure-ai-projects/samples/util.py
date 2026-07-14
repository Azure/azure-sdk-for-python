# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import hashlib
import os
import sys
import tempfile
import zipfile
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Any, AsyncIterator, Iterator, Optional, Tuple

_PKG_ROOT = Path(__file__).resolve().parents[1]
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.models import (
    AgentBlueprintReference,
    AgentDefinition,
    AgentEndpointConfig,
    AgentVersionDetails,
    FixedRatioVersionSelectionRule,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)


def _resolve_zip_file(zip_file: str) -> Path:
    zip_path = Path(zip_file)
    if zip_path.is_absolute():
        return zip_path

    for base_path in (Path.cwd(), Path(__file__).resolve().parent, Path(__file__).resolve().parents[1]):
        candidate = base_path / zip_path
        if candidate.exists():
            return candidate.resolve()

    return (Path.cwd() / zip_path).resolve()


def zip_directory(
    source_dir: Path, zip_filename: Optional[str] = None, *, env_var: str = "ZIP_FILE_PATH"
) -> Tuple[bytes, str, Path]:
    """Return zip bytes, SHA-256, and path for a source directory.

    Direct sample runs create a normal zip from ``source_dir`` in the temp folder.
    Callers can set ``env_var`` to load an existing zip file instead of creating
    a new archive.
    """
    configured_zip_file = os.environ.get(env_var)
    if configured_zip_file:
        zip_path = _resolve_zip_file(configured_zip_file)
        zip_bytes = zip_path.read_bytes()
        zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
        print(f"Loaded zip from {zip_path}: {len(zip_bytes)} bytes, sha256={zip_sha256}")
        return zip_bytes, zip_sha256, zip_path

    zip_path = Path(tempfile.gettempdir()).resolve() / (zip_filename or f"{source_dir.name}.zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if "__pycache__" in file_path.parts or file_path.suffix == ".pyc" or file_path.name == "README.md":
                continue
            zf.write(file_path, file_path.relative_to(source_dir).as_posix())

    zip_bytes = zip_path.read_bytes()
    zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
    print(f"Built zip from {source_dir}: {len(zip_bytes)} bytes, sha256={zip_sha256}, path={zip_path}")
    return zip_bytes, zip_sha256, zip_path


@contextmanager
def create_version_with_endpoint(
    project_client: AIProjectClient,
    agent_name: str,
    *,
    definition: AgentDefinition,
    metadata: Optional[dict[str, str]] = None,
    description: Optional[str] = None,
    blueprint_reference: Optional[AgentBlueprintReference] = None,
    draft: Optional[bool] = None,
    **kwargs: Any,
) -> Iterator[AgentVersionDetails]:
    """Create a version, point the agent endpoint to it, then restore and delete on exit."""
    created_version = None
    original_agent_endpoint = None

    try:
        created_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=definition,
            metadata=metadata,
            description=description,
            blueprint_reference=blueprint_reference,
            draft=draft,
            **kwargs,
        )

        original_agent_endpoint = project_client.agents.get(agent_name=agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        yield created_version
    finally:
        if original_agent_endpoint is not None:
            project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)

        if created_version is not None:
            project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )


@asynccontextmanager
async def create_version_with_endpoint_async(
    project_client: AsyncAIProjectClient,
    agent_name: str,
    *,
    definition: AgentDefinition,
    metadata: Optional[dict[str, str]] = None,
    description: Optional[str] = None,
    blueprint_reference: Optional[AgentBlueprintReference] = None,
    draft: Optional[bool] = None,
    **kwargs: Any,
) -> AsyncIterator[AgentVersionDetails]:
    """Async variant of :func:`create_version_with_endpoint`."""
    created_version = None
    original_agent_endpoint = None

    try:
        created_version = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=definition,
            metadata=metadata,
            description=description,
            blueprint_reference=blueprint_reference,
            draft=draft,
            **kwargs,
        )

        original_agent_endpoint = (await project_client.agents.get(agent_name=agent_name)).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        await project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        yield created_version
    finally:
        if original_agent_endpoint is not None:
            await project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)

        if created_version is not None:
            await project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )
