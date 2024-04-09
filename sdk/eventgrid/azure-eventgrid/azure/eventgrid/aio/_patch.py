# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.
Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import List, Union, Any, TYPE_CHECKING, Optional
from azure.core.credentials import AzureKeyCredential, AzureSasCredential


from .._legacy.aio import EventGridPublisherClient
from ._client import EventGridClient as InternalEventGridClient
from .._serialization import Deserializer, Serializer
from .._patch import (
    ClientLevel,
    DEFAULT_BASIC_API_VERSION,
    DEFAULT_STANDARD_API_VERSION,
)

if TYPE_CHECKING:
    # pylint: disable=unused-import,ungrouped-imports
    from azure.core.credentials_async import AsyncTokenCredential


class EventGridClient(InternalEventGridClient):
    """Azure Messaging EventGrid Client.

    :param endpoint: The endpoint to the Event Grid resource.
    :type endpoint: str
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AzureKeyCredential or ~azure.core.credentials.AzureSasCredential or
     ~azure.core.credentials_async.AsyncTokenCredential
    :keyword api_version: The API version to use for this operation. Default value for namespaces is
     "2023-10-01-preview". Default value for basic is "2018-01-01". Note that overriding this default value may result in unsupported
     behavior.
    :paramtype api_version: str or None
    :keyword level: The level of client to use.
     Known values include: "Basic", "Standard". Default value is "Standard".
     `Standard` is used for working with a namespace topic.
     `Basic` is used for working with a basic topic.
    :paramtype level: str
    """

    def __init__(
        self,
        endpoint: str,
        credential: Union[
            AzureKeyCredential, AzureSasCredential, "AsyncTokenCredential"
        ],
        *,
        api_version: Optional[str] = None,
        level: Union[str, ClientLevel] = "Standard",
        **kwargs: Any
    ) -> None:
        _endpoint = "{endpoint}"
        self._level = level

        if level == ClientLevel.BASIC:
            self._client = EventGridPublisherClient(  # type: ignore[assignment]
                endpoint,
                credential,
                api_version=api_version or DEFAULT_BASIC_API_VERSION,
                **kwargs
            )
            self._send = self._client.send  # type: ignore[attr-defined]
        elif level == ClientLevel.STANDARD:
            if isinstance(credential, AzureSasCredential):
                raise TypeError(
                    "SAS token authentication is not supported for the standard client."
                )

            super().__init__(
                endpoint=endpoint,
                credential=credential,
                api_version=api_version or DEFAULT_STANDARD_API_VERSION,
                **kwargs
            )
            self._send = self._publish_cloud_events
        else:
            raise ValueError(
                "Unknown client level. Known values are `Standard` and `Basic`."
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
    "EventGridClient",
    "EventGridPublisherClient",
]  # Add all objects you want publicly available to users at this package level
