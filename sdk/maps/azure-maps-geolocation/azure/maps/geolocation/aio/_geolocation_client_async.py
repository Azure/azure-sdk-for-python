# ---------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ---------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302, too-many-function-args, W0212
from typing import Any, Union
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential

from ._base_client_async import AsyncMapsGeolocationClientBase
from ..models import (
    IpAddressToLocationResult
)

# By default, use the latest supported API version
class MapsGeolocationClient(AsyncMapsGeolocationClientBase):
    """Azure Maps Geolocation REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.AsyncTokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
    """
    def __init__(
        self,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    ) -> None:
        super().__init__(
            credential=credential, **kwargs
        )


    @distributed_trace_async
    async def get_geolocation(
        self,
        ip_address: str,
        **kwargs: Any
    ) -> IpAddressToLocationResult:
        """**Applies to:** see pricing `tiers <https://aka.ms/AzureMapsPricingTier>`_.

        This service will return the ISO country code for the provided IP address. Developers can use
        this information  to block or alter certain content based on geographical locations where the
        application is being viewed from.

        :param ip_address: The IP address. Both IPv4 and IPv6 are allowed. Required.
        :type ip_address: str
        :return: IpAddressToLocationResult
        :rtype: ~azure.maps.geolocation.models.IpAddressToLocationResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        geolocation_result = await self._geolocation_client.get_location(
            format="json",
            ip_address=ip_address,
            **kwargs
        )

        return geolocation_result
