# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Literal, TypedDict, Union

from typing_extensions import NotRequired

from azure.core.credentials import TokenCredential
from azure.core.credentials_async import AsyncTokenCredential


class AgentServerOptions(TypedDict):
    """Configuration options for the Agent Server.

    Attributes:
        project_endpoint (str, optional): The endpoint URL for the project. Defaults to current project.
        credential (Union[AsyncTokenCredential, TokenCredential], optional): The credential used for authentication.
            Defaults to current project's managed identity.
    """
    project_endpoint: NotRequired[str]
    credential: NotRequired[Union[AsyncTokenCredential, TokenCredential]]
    http: NotRequired["HttpServerOptions"]
    toos: NotRequired["ToolsOptions"]


class HttpServerOptions(TypedDict):
    """Configuration options for the HTTP server.

    Attributes:
        host (str, optional): The host address the server listens on.
    """
    host: NotRequired[Literal["127.0.0.1", "localhost", "0.0.0.0"]]


class ToolsOptions(TypedDict):
    """Configuration options for the Tools subsystem.

    Attributes:
        catalog_cache_ttl (int, optional): The time-to-live (TTL) for the tool catalog cache in seconds.
            Defaults to 600 seconds (10 minutes).
        catalog_cache_max_size (int, optional): The maximum size of the tool catalog cache.
            Defaults to 1024 entries.
    """
    catalog_cache_ttl: NotRequired[int]
    catalog_cache_max_size: NotRequired[int]
