# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta
from azure.core.pipeline.policies import HttpLoggingPolicy

from . import ChallengeAuthPolicy
from .._generated import KeyVaultClient as _KeyVaultClient
from .._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import TokenCredential


class ApiVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Key Vault API versions supported by this package"""

    #: this is the default version
    V7_4_PREVIEW_1 = "7.4-preview.1"
    V7_3 = "7.3"
    V7_2 = "7.2"


DEFAULT_VERSION = ApiVersion.V7_4_PREVIEW_1


class KeyVaultClientBase(object):
    def __init__(self, vault_url: str, credential: "TokenCredential", **kwargs) -> None:
        if not credential:
            raise ValueError(
                "credential should be an object supporting the TokenCredential protocol, "
                "such as a credential from azure-identity"
            )
        if not vault_url:
            raise ValueError("vault_url must be the URL of an Azure Key Vault")

        try:
            api_version = kwargs.pop("api_version", DEFAULT_VERSION)
            # If API version was provided as an enum value, need to make a plain string for 3.11 compatibility
            if hasattr(api_version, "value"):
                api_version = api_version.value
            self._vault_url = vault_url.strip(" /")
            client = kwargs.get("generated_client")
            if client:
                # caller provided a configured client -> only models left to initialize
                self._client = client
                models = kwargs.get("generated_models")
                self._models = models or _KeyVaultClient.models(api_version=api_version)
                return

            http_logging_policy = HttpLoggingPolicy(**kwargs)
            http_logging_policy.allowed_header_names.update(
                {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
            )

            verify_challenge = kwargs.pop("verify_challenge_resource", True)
            self._client = _KeyVaultClient(
                api_version=api_version,
                authentication_policy=ChallengeAuthPolicy(credential, verify_challenge_resource=verify_challenge),
                sdk_moniker=SDK_MONIKER,
                http_logging_policy=http_logging_policy,
                **kwargs
            )
            self._models = _KeyVaultClient.models(api_version=api_version)
        except ValueError:
            raise NotImplementedError(
                f"This package doesn't support API version '{api_version}'. "
                + f"Supported versions: {', '.join(v.value for v in ApiVersion)}"
            )

    @property
    def vault_url(self) -> str:
        return self._vault_url

    def __enter__(self) -> "KeyVaultClientBase":
        self._client.__enter__()
        return self

    def __exit__(self, *args: "Any") -> None:
        self._client.__exit__(*args)

    def close(self) -> None:
        """Close sockets opened by the client.

        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
