# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import TYPE_CHECKING, Union, Any
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import AzureKeyCredential

from ._base_client import MapsGeolocationClientBase
from .models import (
    IpAddressToLocationResult
)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


# By default, use the latest supported API version
class MapsGeolocationClient(MapsGeolocationClientBase):
    """Azure Maps Geolocation REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
    """

    def __init__(
        self,
        credential, # type: Union[AzureKeyCredential, TokenCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        super().__init__(
            credential=credential, **kwargs
        )

    @distributed_trace
    def get_geolocation(
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
        geolocation_result = self._geolocation_client.get_location(
            format="json",
            ip_address=ip_address,
            **kwargs
        )

        return geolocation_result
