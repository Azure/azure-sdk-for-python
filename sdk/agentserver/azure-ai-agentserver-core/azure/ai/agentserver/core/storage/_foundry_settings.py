# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Configuration helpers for Foundry activity state storage."""
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype
# pylint: disable=docstring-keyword-should-match-keyword-only

from __future__ import annotations

from urllib.parse import quote as _url_quote

from azure.ai.agentserver.core._config import AgentConfig

_DEFAULT_API_VERSION = "v1"


def _encode(value: str) -> str:
    return _url_quote(value, safe="")


class FoundryActivityStateSettings:
    """Immutable runtime configuration for :class:`FoundryActivityStateClient`."""

    def __init__(self, *, storage_base_url: str, api_version: str = _DEFAULT_API_VERSION) -> None:
        self.storage_base_url = storage_base_url
        self.api_version = api_version

    @classmethod
    def from_env(cls, *, api_version: str = _DEFAULT_API_VERSION) -> "FoundryActivityStateSettings":
        """Create settings by reading the ``FOUNDRY_PROJECT_ENDPOINT`` environment variable."""
        config = AgentConfig.from_env()
        if not config.project_endpoint:
            raise EnvironmentError(
                "The 'FOUNDRY_PROJECT_ENDPOINT' environment variable is required. "
                "In hosted environments, the Azure AI Foundry platform must set this variable."
            )
        return cls.from_endpoint(config.project_endpoint, api_version=api_version)

    @classmethod
    def from_endpoint(cls, endpoint: str, *, api_version: str = _DEFAULT_API_VERSION) -> "FoundryActivityStateSettings":
        """Create settings from an explicit Foundry project endpoint URL."""
        if not endpoint:
            raise ValueError("endpoint must be a non-empty string")
        if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
            raise ValueError(f"endpoint must be a valid absolute URL, got: {endpoint!r}")
        return cls(storage_base_url=endpoint.rstrip("/") + "/storage/", api_version=api_version)

    def build_url(self, path: str, **extra_params: str) -> str:
        """Build a full storage API URL for *path* with ``api-version`` appended."""
        url = f"{self.storage_base_url}{path}?api-version={_encode(self.api_version)}"
        for key, value in extra_params.items():
            url += f"&{key}={_encode(value)}"
        return url
