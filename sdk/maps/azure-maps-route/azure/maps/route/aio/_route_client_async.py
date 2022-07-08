# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports
from typing import TYPE_CHECKING
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from ._base_client_async import AsyncMapsRouteClientBase
from .._generated.models import BatchRequest

if TYPE_CHECKING:
    from typing import Any, List
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.polling import LROPoller, AsyncLROPoller


# By default, use the latest supported API version
class MapsRouteClient(AsyncMapsRouteClientBase):
    """Azure Maps Route REST APIs.
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AsyncTokenCredential
    :param client_id: Specifies which account is intended for usage in conjunction with the Azure AD security model.
     It represents a unique ID for the Azure Maps account and can be retrieved from the Azure Maps management
     plane Account API. To use Azure AD security in Azure Maps see the following
     `articles <https://aka.ms/amauthdetails>`_ for guidance.
    :type client_id: str
    :param str base_url: Service URL
    :keyword int polling_interval: Default waiting time between two polls for
     LRO operations if no Retry-After header is present.
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.translation.document.MapsRouteApiVersion
    """
    def __init__(
        self,
        credential, # type: Union[AzureKeyCredential, AsyncTokenCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None
        super().__init__(
            credential=credential, **kwargs
        )