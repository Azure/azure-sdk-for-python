# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    ContentDecodePolicy,
    UserAgentPolicy,
    DistributedTracingPolicy,
    HttpLoggingPolicy,
)
from azure.core.pipeline.transport import RequestsTransport

from .multi_api import load_generated_api
from .challenge_auth_policy import ChallengeAuthPolicy
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.configuration import Configuration


def _get_policies(config, **kwargs):
    logging_policy = HttpLoggingPolicy(**kwargs)
    logging_policy.allowed_header_names.add("x-ms-keyvault-network-info")

    return [
        config.headers_policy,
        UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs),
        config.proxy_policy,
        ContentDecodePolicy(),
        config.redirect_policy,
        config.retry_policy,
        config.authentication_policy,
        config.logging_policy,
        DistributedTracingPolicy(**kwargs),
        logging_policy,
    ]


def _build_pipeline(config, transport=None, **kwargs):
    # type: (Configuration, HttpTransport, **Any) -> Pipeline
    policies = _get_policies(config)
    if transport is None:
        transport = RequestsTransport(**kwargs)

    return Pipeline(transport, policies=policies)


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

        self._vault_url = vault_url.strip(" /")
        client = kwargs.get("generated_client")
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return

        api_version = kwargs.pop("api_version", None)
        generated = load_generated_api(api_version)

        pipeline = kwargs.pop("pipeline", None)
        if not pipeline:
            config = generated.config_cls(credential, **kwargs)
            config.authentication_policy = ChallengeAuthPolicy(credential)
            pipeline = _build_pipeline(config, **kwargs)

        # generated clients don't use their credentials parameter
        self._client = generated.client_cls(credentials="", pipeline=pipeline)
        self._models = generated.models

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
        self._client.__exit__()
