# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:skip-file (avoids crash due to six.with_metaclass https://github.com/PyCQA/astroid/issues/713)
from typing import TYPE_CHECKING
from enum import Enum
from six import with_metaclass

from azure.core import CaseInsensitiveEnumMeta
from azure.core.pipeline.policies import HttpLoggingPolicy

from . import ChallengeAuthPolicy
from .._generated import KeyVaultClient as _KeyVaultClient
from .._sdk_moniker import SDK_MONIKER

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any
    from azure.core.credentials import TokenCredential


class ApiVersion(with_metaclass(CaseInsensitiveEnumMeta, str, Enum)):
    """Key Vault API versions supported by this package"""

    #: this is the default version
    V7_3 = "7.3"
    V7_2 = "7.2"
    V7_1 = "7.1"
    V7_0 = "7.0"
    V2016_10_01 = "2016-10-01"


DEFAULT_VERSION = ApiVersion.V7_3


class KeyVaultClientBase(object):
    def __init__(self, vault_url, credential, **kwargs):
        # type: (str, TokenCredential, **Any) -> None
        if not credential:
            raise ValueError(
                "credential should be an object supporting the TokenCredential protocol, "
                "such as a credential from azure-identity"
            )
        if not vault_url:
            raise ValueError("vault_url must be the URL of an Azure Key Vault")

        try:
            self.api_version = kwargs.pop("api_version", DEFAULT_VERSION)
            self._vault_url = vault_url.strip(" /")

            client = kwargs.get("generated_client")
            if client:
                # caller provided a configured client -> only models left to initialize
                self._client = client
                models = kwargs.get("generated_models")
                self._models = models or _KeyVaultClient.models(api_version=self.api_version)
                return

            pipeline = kwargs.pop("pipeline", None)
            transport = kwargs.pop("transport", None)
            http_logging_policy = HttpLoggingPolicy(**kwargs)
            http_logging_policy.allowed_header_names.update(
                {"x-ms-keyvault-network-info", "x-ms-keyvault-region", "x-ms-keyvault-service-version"}
            )

            self._client = _KeyVaultClient(
                api_version=self.api_version,
                pipeline=pipeline,
                transport=transport,
                authentication_policy=ChallengeAuthPolicy(credential),
                sdk_moniker=SDK_MONIKER,
                http_logging_policy=http_logging_policy,
                **kwargs
            )
            self._models = _KeyVaultClient.models(api_version=self.api_version)
        except ValueError:
            raise NotImplementedError(
                "This package doesn't support API version '{}'. ".format(self.api_version)
                + "Supported versions: {}".format(", ".join(v.value for v in ApiVersion))
            )

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url

    def __enter__(self):
        # type: () -> KeyVaultClientBase
        self._client.__enter__()
        return self

    def __exit__(self, *args):
        # type: (*Any) -> None
        self._client.__exit__(*args)

    def close(self):
        # type: () -> None
        """Close sockets opened by the client.

        Calling this method is unnecessary when using the client as a context manager.
        """
        self._client.close()
