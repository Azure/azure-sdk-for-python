# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Optional, Any, Union
from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.pipeline import policies

from azure.appconfiguration._generated import models as _models
from azure.appconfiguration._generated._azure_app_configuration import (
    AzureAppConfiguration as AzureAppConfigurationGenerated,
)
from azure.appconfiguration._generated._configuration import (
    AzureAppConfigurationConfiguration as AzureAppConfigurationConfigurationGenerated,
    VERSION,
)
from azure.appconfiguration._generated._serialization import Deserializer, Serializer


class AzureAppConfiguration(AzureAppConfigurationGenerated):
    """AzureAppConfiguration.

    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :param endpoint: The endpoint of the App Configuration instance to send requests to. Required.
    :type endpoint: str
    :param sync_token: Used to guarantee real-time consistency between requests. Default value is
     None.
    :type sync_token: str
    :keyword api_version: Api Version. Default value is "2023-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
     Retry-After header is present.
    """

    def __init__(
        self,
        credential: Union[TokenCredential, AzureKeyCredential],
        endpoint: str,
        sync_token: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._config = AzureAppConfigurationConfiguration(
            credential=credential, endpoint=endpoint, sync_token=sync_token, **kwargs
        )
        _policies = kwargs.pop("policies", None)
        if _policies is None:
            _policies = [
                policies.RequestIdPolicy(**kwargs),
                self._config.headers_policy,
                self._config.user_agent_policy,
                self._config.proxy_policy,
                policies.ContentDecodePolicy(**kwargs),
                self._config.redirect_policy,
                self._config.retry_policy,
                self._config.authentication_policy,
                self._config.custom_hook_policy,
                self._config.logging_policy,
                policies.DistributedTracingPolicy(**kwargs),
                policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,
                self._config.http_logging_policy,
            ]
        self._client: PipelineClient = PipelineClient(base_url=_endpoint, policies=_policies, **kwargs)

        client_models = {k: v for k, v in _models.__dict__.items() if isinstance(v, type)}
        self._serialize = Serializer(client_models)
        self._deserialize = Deserializer(client_models)
        self._serialize.client_side_validation = False


class AzureAppConfigurationConfiguration(AzureAppConfigurationConfigurationGenerated):
    """Configuration for AzureAppConfiguration.

    Note that all parameters used to create this instance are saved as instance
    attributes.

    :param credential: Credential needed for the client to connect to Azure. Required.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :param endpoint: The endpoint of the App Configuration instance to send requests to. Required.
    :type endpoint: str
    :param sync_token: Used to guarantee real-time consistency between requests. Default value is
     None.
    :type sync_token: str
    :keyword api_version: Api Version. Default value is "2023-10-01". Note that overriding this
     default value may result in unsupported behavior.
    :paramtype api_version: str
    """

    def __init__(
        self,
        credential: Union[TokenCredential, AzureKeyCredential],
        endpoint: str,
        sync_token: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        api_version: str = kwargs.pop("api_version", "2023-10-01")

        if credential is None:
            raise ValueError("Parameter 'credential' must not be None.")
        if endpoint is None:
            raise ValueError("Parameter 'endpoint' must not be None.")

        self.credential = credential
        self.endpoint = endpoint
        self.sync_token = sync_token
        self.api_version = api_version
        kwargs.setdefault("sdk_moniker", "appconfiguration/{}".format(VERSION))
        self.polling_interval = kwargs.get("polling_interval", 30)
        self._configure(**kwargs)


__all__: List[str] = [
    "AzureAppConfiguration"
]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
