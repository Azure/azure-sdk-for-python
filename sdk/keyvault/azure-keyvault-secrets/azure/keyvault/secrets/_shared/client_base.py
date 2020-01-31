# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import UserAgentPolicy, DistributedTracingPolicy, HttpLoggingPolicy
from azure.core.pipeline.transport import RequestsTransport
from ._generated.v7_0.version import VERSION as V7_0_VERSION
from ._generated.v2016_10_01.version import VERSION as V2016_10_01_VERSION
from .challenge_auth_policy import ChallengeAuthPolicy
from .._user_agent import USER_AGENT

if TYPE_CHECKING:
    # pylint:disable=unused-import
    from typing import Any, Optional
    from azure.core.credentials import TokenCredential
    from azure.core.pipeline.transport import HttpTransport
    from azure.core.configuration import Configuration

DEFAULT_API_VERSION = V7_0_VERSION



class KeyVaultClientBase(object):
    """Base class for Key Vault clients"""

    @staticmethod
    def _get_configuration_class(api_version):
        # type: (str) -> KeyVaultClientConfiguration
        """
        Get the versioned configuration implementation corresponding to the current profile.
        :return: The versioned configuration implementation.
        """
        if api_version == V7_0_VERSION:
            from ._generated.v7_0._configuration import KeyVaultClientConfiguration as ImplConfig
        elif api_version == V2016_10_01_VERSION:
            from ._generated.v2016_10_01._configuration import KeyVaultClientConfiguration as ImplConfig
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))
        return ImplConfig

    @staticmethod
    def _create_config(credential, api_version=DEFAULT_API_VERSION, **kwargs):
        # type: (TokenCredential, Optional[str], **Any) -> Configuration
        config = KeyVaultClientBase._get_configuration_class(api_version)(credential, **kwargs)
        config.authentication_policy = ChallengeAuthPolicy(credential)

        # replace the autorest-generated UserAgentPolicy and its hard-coded user agent
        # https://github.com/Azure/azure-sdk-for-python/issues/6637
        config.user_agent_policy = UserAgentPolicy(base_user_agent=USER_AGENT, **kwargs)

        # Override config policies if found in kwargs
        # TODO: should be unnecessary after next regeneration (written 2019-08-02)
        if "user_agent_policy" in kwargs:
            config.user_agent_policy = kwargs["user_agent_policy"]
        if "headers_policy" in kwargs:
            config.headers_policy = kwargs["headers_policy"]
        if "proxy_policy" in kwargs:
            config.proxy_policy = kwargs["proxy_policy"]
        if "logging_policy" in kwargs:
            config.logging_policy = kwargs["logging_policy"]
        if "retry_policy" in kwargs:
            config.retry_policy = kwargs["retry_policy"]
        if "custom_hook_policy" in kwargs:
            config.custom_hook_policy = kwargs["custom_hook_policy"]
        if "redirect_policy" in kwargs:
            config.redirect_policy = kwargs["redirect_policy"]

        return config

    @staticmethod
    def _create_client(credential, pipeline, api_version):
        # type: (TokenCredential, Pipeline, str) -> KeyVaultClient
        if api_version == V7_0_VERSION:
            from ._generated.v7_0 import KeyVaultClient as ImplClient
        elif api_version == V2016_10_01_VERSION:
            from ._generated.v2016_10_01 import KeyVaultClient as ImplClient
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))
        return ImplClient(credentials=credential, pipeline=pipeline)

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
        api_version = kwargs.pop('api_version', None) or DEFAULT_API_VERSION
        self._api_version = api_version

        client = kwargs.get("generated_client")
        if client:
            # caller provided a configured client -> nothing left to initialize
            self._client = client
            return
        config = self._create_config(credential, api_version, **kwargs)
        transport = kwargs.pop("transport", None)
        pipeline = kwargs.pop("pipeline", None) or self._build_pipeline(config, transport=transport, **kwargs)

        self._client = self._create_client(credential, pipeline, api_version)


    # pylint:disable=no-self-use
    def _build_pipeline(self, config, transport, **kwargs):
        # type: (Configuration, HttpTransport, **Any) -> Pipeline
        logging_policy = HttpLoggingPolicy(**kwargs)
        logging_policy.allowed_header_names.add("x-ms-keyvault-network-info")
        policies = [
            config.headers_policy,
            config.user_agent_policy,
            config.proxy_policy,
            config.redirect_policy,
            config.retry_policy,
            config.authentication_policy,
            config.logging_policy,
            DistributedTracingPolicy(**kwargs),
            logging_policy,
        ]

        if transport is None:
            transport = RequestsTransport(**kwargs)

        return Pipeline(transport, policies=policies)

    @property
    def vault_url(self):
        # type: () -> str
        return self._vault_url

    @property
    def _models(self):
        """Module depends on the API version:
            * 2016-10-01: :mod:`v2016_10_01.models<azure.keyvault._generated.v2016_10_01.models>`
            * 7.0: :mod:`v7_0.models<azure.keyvault._generated.v7_0.models>`
        """
        if self._api_version == V7_0_VERSION:
            from ._generated.v7_0 import models as impl_models
        elif self._api_version == V2016_10_01_VERSION:
            from ._generated.v2016_10_01 import models as impl_models
        else:
            raise NotImplementedError("APIVersion {} is not available".format(self._api_version))
        return impl_models

    def __enter__(self, *args, **kwargs):
        """
        Calls __enter__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        self._client.__enter__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        """
        Calls __exit__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        self._client.__exit__(*args, **kwargs)
        return self
