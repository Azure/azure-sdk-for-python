# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from dataclasses import dataclass, field

from azure.core.credentials_async import AsyncTokenCredential


@dataclass(frozen=True)
class HttpServerConfiguration:
    """Resolved configuration for the HTTP server.

    :ivar str host: The host address the server listens on. Defaults to '0.0.0.0'.
    :ivar int port: The port number the server listens on. Defaults to 8088.
    """

    host: str = "0.0.0.0"
    port: int = 8088


class ToolsConfiguration:
    """Resolved configuration for the Tools subsystem.

    :ivar int catalog_cache_ttl: The time-to-live (TTL) for the tool catalog cache in seconds.
        Defaults to 600 seconds (10 minutes).
    :ivar int catalog_cache_max_size: The maximum size of the tool catalog cache.
        Defaults to 1024 entries.
    """

    catalog_cache_ttl: int = 600
    catalog_cache_max_size: int = 1024


@dataclass(frozen=True, kw_only=True)
class AgentServerConfiguration:
    """Resolved configuration for the Agent Server application."""

    agent_name: str = "$default"
    project_endpoint: str
    credential: AsyncTokenCredential
    http: HttpServerConfiguration = field(default_factory=HttpServerConfiguration)
    tools: ToolsConfiguration = field(default_factory=ToolsConfiguration)
