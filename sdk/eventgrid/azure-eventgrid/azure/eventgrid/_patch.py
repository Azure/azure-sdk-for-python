# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
import datetime
from typing import List, TYPE_CHECKING, Any, Union, Optional, Generic, Dict, TypedDict, TypeVar
from ._legacy import (
    EventGridPublisherClient,
    SystemEventNames,
    EventGridEvent,
    generate_sas,
)
from enum import Enum
from azure.core import CaseInsensitiveEnumMeta
from ._client import EventGridClient as InternalEventGridClient

from azure.core import PipelineClient
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import policies
from azure.core.rest import HttpRequest, HttpResponse

from ._configuration import EventGridClientConfiguration
from ._operations import EventGridClientOperationsMixin
from ._serialization import Deserializer, Serializer


if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials import TokenCredential

class ClientLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    STANDARD = "Standard",
    BASIC = "Basic"

class EventGridClient(InternalEventGridClient):
    """Azure Messaging EventGrid Client.

    :param endpoint: The host name of the namespace, e.g.
     namespaceName1.westus-1.eventgrid.azure.net. Required.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure. Is either a
     AzureKeyCredential type or a TokenCredential type. Required.
    :type credential: ~azure.core.credentials.AzureKeyCredential or
     ~azure.core.credentials.TokenCredential
    :keyword api_version: The API version to use for this operation. Default value is
     "2023-10-01-preview". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str
    :keyword level: The level of Client to use. Known values are `Standard` and `Basic`. Default value is `Standard`. 
    :keywordtype level: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[AzureKeyCredential, "TokenCredential"],
        *,
        api_version: str = "2023-10-01-preview",
        level: Union[str, ClientLevel] = "Standard",
        **kwargs: Any
    ) -> None:
        
        _endpoint = '{endpoint}'
        self._config = EventGridClientConfiguration(endpoint=endpoint, credential=credential, api_version=api_version, **kwargs)
        self._config.level = level
        _policies = kwargs.pop('policies', None)
        if _policies is None:
            _policies = [policies.RequestIdPolicy(**kwargs),self._config.headers_policy,self._config.user_agent_policy,self._config.proxy_policy,policies.ContentDecodePolicy(**kwargs),self._config.redirect_policy,self._config.retry_policy,self._config.authentication_policy,self._config.custom_hook_policy,self._config.logging_policy,policies.DistributedTracingPolicy(**kwargs),policies.SensitiveHeaderCleanupPolicy(**kwargs) if self._config.redirect_policy else None,self._config.http_logging_policy]
        
        if level == ClientLevel.BASIC:
            self._client = EventGridPublisherClient(endpoint, credential, **kwargs)
            self._config.level = ClientLevel.BASIC
        elif level == ClientLevel.STANDARD:
            self._client = PipelineClient(base_url=_endpoint, policies=_policies, **kwargs)
            self._config.level = ClientLevel.STANDARD

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
    "EventGridClient",
    "SystemEventNames",
    "EventGridEvent",
    "generate_sas",
    "ClientLevel",
    "EventGridPublisherClient"
]  # Add all objects you want publicly available to users at this package level
