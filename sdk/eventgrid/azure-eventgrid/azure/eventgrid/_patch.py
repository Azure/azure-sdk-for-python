# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, Union, Optional, Any
from enum import Enum

from azure.core import CaseInsensitiveEnumMeta, PipelineClient
from azure.core.credentials import AzureKeyCredential, TokenCredential, AzureSasCredential
from azure.core.pipeline import policies

from ._legacy import (
    EventGridPublisherClient,
    SystemEventNames,
    EventGridEvent,
    generate_sas,
)
from ._client import EventGridClient as InternalEventGridClient, EventGridClientConfiguration
from ._serialization import Serializer, Deserializer


class ClientLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STANDARD = ("Standard",)
    BASIC = "Basic"

DEFAULT_STANDARD_API_VERSION = "2023-10-01-preview"
DEFAULT_BASIC_API_VERSION = "2018-01-01"

class EventGridClient(InternalEventGridClient):
    """Azure Messaging EventGrid Client.
    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value for namespaces is
     "2023-10-01-preview". Default value for basic is "2018-01-01". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str or None
    :keyword level: The level of Client to use. Known values are `Standard` and `Basic`. Default value is `Standard`.
     `Standard` is used for sending events to a namespace topic. `Basic` is used for sending events to a basic topic.
    :keywordtype level: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, AzureSasCredential, "TokenCredential"],
        *,
        api_version: Optional[str] = None,
        level: Union[str, ClientLevel] = "Standard",
        **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._level = level


        if level == ClientLevel.BASIC:
            self._client = EventGridPublisherClient(endpoint, credential, api_version=api_version or DEFAULT_BASIC_API_VERSION) # type:ignore[assignment]
            self._send = self._client.send # type:ignore[attr-defined]
        elif level == ClientLevel.STANDARD:
            if isinstance(credential, AzureSasCredential):
                raise TypeError("SAS token authentication is not supported for the standard client.")
            self._config = EventGridClientConfiguration(
            endpoint=endpoint, credential=credential, api_version=api_version or DEFAULT_STANDARD_API_VERSION, **kwargs)

            self._send = self._publish_cloud_events
    
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
                    (
                        policies.SensitiveHeaderCleanupPolicy(**kwargs)
                        if self._config.redirect_policy
                        else None
                    ),
                    self._config.http_logging_policy,
                ]

            self._client = PipelineClient(
                base_url=_endpoint, policies=_policies, **kwargs
            )

        self._serialize = Serializer()
        self._deserialize = Deserializer()
        self._serialize.client_side_validation = False



def patch_sdk():
    """Do not remove from this file.
    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


__all__: List[str] = [
    "EventGridPublisherClient",
    "SystemEventNames",
    "EventGridEvent",
    "generate_sas",
    "EventGridClient",
    "ClientLevel",
]  # Add all objects you want publicly available to users at this package level
