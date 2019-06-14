# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from collections import namedtuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Mapping, Optional
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport

try:
    import urllib.parse as parse
except ImportError:
    import urlparse as parse  # pylint: disable=import-error

from azure.core import Configuration
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import BearerTokenCredentialPolicy, HTTPPolicy
from azure.core.pipeline.transport import RequestsTransport

from ._generated import KeyVaultClient


_VaultId = namedtuple("VaultId", ["vault_url", "collection", "name", "version"])


KEY_VAULT_SCOPE = "https://vault.azure.net/.default"


def _parse_vault_id(url):
    try:
        parsed_uri = parse.urlparse(url)
    except Exception:  # pylint: disable=broad-except
        raise ValueError("'{}' is not not a valid url".format(url))
    if not (parsed_uri.scheme and parsed_uri.hostname):
        raise ValueError("'{}' is not not a valid url".format(url))

    path = list(filter(None, parsed_uri.path.split("/")))

    if len(path) < 2 or len(path) > 3:
        raise ValueError("'{}' is not not a valid vault url".format(url))

    return _VaultId(
        vault_url="{}://{}".format(parsed_uri.scheme, parsed_uri.hostname),
        collection=path[0],
        name=path[1],
        version=path[2] if len(path) == 3 else None,
    )


class _KeyVaultClientBase(object):
    """
    :param credential:  A credential or credential provider which can be used to authenticate to the vault,
        a ValueError will be raised if the entity is not provided
    :type credential: azure.core.credentials.TokenCredential
    :param str vault_url: The url of the vault to which the client will connect,
        a ValueError will be raised if the entity is not provided
    :param ~azure.core.configuration.Configuration config:  The configuration for the KeyClient
    """

    @staticmethod
    def create_config(credential, api_version=None, **kwargs):
        # type: (TokenCredential, Optional[str], Mapping[str, Any]) -> Configuration
        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION
        config = KeyVaultClient.get_configuration_class(api_version, aio=False)(credential, **kwargs)
        config.authentication_policy = BearerTokenCredentialPolicy(credential, KEY_VAULT_SCOPE)
        return config

    def __init__(self, vault_url, credential, config=None, transport=None, api_version=None, **kwargs):
        # type: (str, TokenCredential, Configuration, Optional[HttpTransport], Optional[str], **Any) -> None
        if not credential:
            raise ValueError(
                "credential should be an object supporting the TokenCredential protocol, such as a credential from azure-identity"
            )
        if not vault_url:
            raise ValueError("vault_url must be the URL of an Azure Key Vault")

        self._vault_url = vault_url.strip(" /")

        client = kwargs.pop("generated_client", None)
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        if api_version is None:
            api_version = KeyVaultClient.DEFAULT_API_VERSION

        config = config or self.create_config(credential, api_version=api_version, **kwargs)
        pipeline = kwargs.pop("pipeline", None) or self._build_pipeline(config, transport)
        self._client = KeyVaultClient(credential, api_version=api_version, pipeline=pipeline, aio=False, **kwargs)

    def _build_pipeline(self, config, transport):
        # type: (Configuration, HttpTransport) -> Pipeline
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.logging_policy,
        ]

        if transport is None:
            transport = RequestsTransport(config)

        return Pipeline(transport, policies=policies)

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url
