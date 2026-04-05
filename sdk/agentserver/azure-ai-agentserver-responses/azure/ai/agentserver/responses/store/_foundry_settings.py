# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Configuration helpers for the Foundry storage backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import quote as _url_quote

_PROJECT_ENDPOINT_ENV_VAR = "FOUNDRY_PROJECT_ENDPOINT"
_API_VERSION = "v1"


def _encode(value: str) -> str:
    return _url_quote(value, safe="")


@dataclass(frozen=True)
class FoundryStorageSettings:
    """Immutable runtime configuration for :class:`FoundryStorageProvider`."""

    storage_base_url: str

    @classmethod
    def from_env(cls) -> "FoundryStorageSettings":
        """Create settings by reading the ``FOUNDRY_PROJECT_ENDPOINT`` environment variable.

        :raises EnvironmentError: If the variable is missing or empty.
        :raises ValueError: If the variable does not contain a valid absolute URL.
        :returns: A new :class:`FoundryStorageSettings` configured from the environment.
        :rtype: FoundryStorageSettings
        """
        value = os.environ.get(_PROJECT_ENDPOINT_ENV_VAR)
        if not value:
            raise EnvironmentError(
                f"The '{_PROJECT_ENDPOINT_ENV_VAR}' environment variable is required. "
                "In hosted environments, the Azure AI Foundry platform must set this variable."
            )
        if not (value.startswith("http://") or value.startswith("https://")):
            raise ValueError(
                f"The '{_PROJECT_ENDPOINT_ENV_VAR}' environment variable must be a valid absolute URL, "
                f"got: {value!r}"
            )
        base = value.rstrip("/") + "/storage/"
        return cls(storage_base_url=base)

    def build_url(self, path: str, **extra_params: str) -> str:
        """Build a full storage API URL for *path* with ``api-version`` appended.

        :param path: The resource path segment, e.g. ``responses/abc123``.
        :type path: str
        :param extra_params: Additional query parameters; values are URL-encoded automatically.
        :type extra_params: str
        :returns: The complete URL string.
        :rtype: str
        """
        url = f"{self.storage_base_url}{path}?api-version={_encode(_API_VERSION)}"
        for key, value in extra_params.items():
            url += f"&{key}={_encode(value)}"
        return url
