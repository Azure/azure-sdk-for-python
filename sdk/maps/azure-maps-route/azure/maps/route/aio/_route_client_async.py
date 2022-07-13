# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import TYPE_CHECKING
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential
from ._base_client_async import AsyncMapsRouteClientBase
from .._generated.models import BatchRequest

if TYPE_CHECKING:
    from typing import Any, List, Union
    from azure.core.credentials_async import AsyncTokenCredential
    from azure.core.polling import LROPoller, AsyncLROPoller


# By default, use the latest supported API version
class MapsRouteClient(AsyncMapsRouteClientBase):
    """Azure Maps Route REST APIs.
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
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