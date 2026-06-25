# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Configuration helpers for the Foundry storage backend."""

from __future__ import annotations

from urllib.parse import quote as _url_quote

from azure.ai.agentserver.core._config import AgentConfig  # pylint: disable=import-error,no-name-in-module

_API_VERSION = "v1"


def _encode(value: str) -> str:
    return _url_quote(value, safe="")


class FoundryStorageSettings:
    """Immutable runtime configuration for :class:`FoundryStorageProvider`."""

    def __init__(self, *, storage_base_url: str) -> None:
        self.storage_base_url = storage_base_url

    @classmethod
    def from_env(cls) -> "FoundryStorageSettings":
        """Create settings by reading the ``FOUNDRY_PROJECT_ENDPOINT`` environment variable.

        :raises EnvironmentError: If the variable is missing or empty.
        :raises ValueError: If the variable does not contain a valid absolute URL.
        :returns: A new :class:`FoundryStorageSettings` configured from the environment.
        :rtype: FoundryStorageSettings
        """
        config = AgentConfig.from_env()
        if not config.project_endpoint:
            raise EnvironmentError(
                "The 'FOUNDRY_PROJECT_ENDPOINT' environment variable is required. "
                "In hosted environments, the Azure AI Foundry platform must set this variable."
            )
        return cls.from_endpoint(config.project_endpoint)

    @classmethod
    def from_endpoint(cls, endpoint: str) -> "FoundryStorageSettings":
        """Create settings from an explicit project endpoint URL.

        :param endpoint: Foundry project endpoint URL (e.g. ``https://myproject.foundry.azure.com``).
        :type endpoint: str
        :raises ValueError: If the endpoint is empty or not a valid absolute URL.
        :returns: A new :class:`FoundryStorageSettings`.
        :rtype: FoundryStorageSettings
        """
        if not endpoint:
            raise ValueError("endpoint must be a non-empty string")
        if not (endpoint.startswith("http://") or endpoint.startswith("https://")):
            raise ValueError(f"endpoint must be a valid absolute URL, got: {endpoint!r}")
        base = endpoint.rstrip("/") + "/storage/"
        return cls(storage_base_url=base)

    def build_url(self, path: str, **extra_params: str) -> str:  # pylint: disable=docstring-keyword-should-match-keyword-only
        """Build a full storage API URL for *path* with ``api-version`` appended.

        :param path: The resource path segment, e.g. ``responses/abc123``.
        :type path: str
        :returns: The complete URL string.
        :rtype: str
        """
        url = f"{self.storage_base_url}{path}?api-version={_encode(_API_VERSION)}"
        for key, value in extra_params.items():
            url += f"&{key}={_encode(value)}"
        return url
