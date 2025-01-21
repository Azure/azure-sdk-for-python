# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import Union, Any
from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import AzureKeyCredential, TokenCredential

from ._base_client import MapsGeolocationClientBase
from .models import CountryRegionResult


# By default, use the latest supported API version
class MapsGeolocationClient(MapsGeolocationClientBase):
    """Azure Maps Geolocation REST APIs.

    :param credential:
        Credential needed for the client to connect to Azure.
    :type credential:
        ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword str client_id:
        Specifies which account is intended for usage with the Azure AD security model.
        It represents a unique ID for the Azure Maps account.
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str

    .. admonition:: Example:

        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_maps_geolocation_service_client_with_key]
            :end-before: [END create_maps_geolocation_service_client_with_key]
            :language: python
            :dedent: 4
            :caption: Creating the MapsGeolocationClient with an subscription key.
        .. literalinclude:: ../samples/sample_authentication.py
            :start-after: [START create_maps_geolocation_service_client_with_aad]
            :end-before: [END create_maps_geolocation_service_client_with_aad]
            :language: python
            :dedent: 4
            :caption: Creating the MapsGeolocationClient with a token credential.
    """

    def __init__(self, credential: Union[AzureKeyCredential, TokenCredential], **kwargs: Any) -> None:

        super().__init__(credential=credential, **kwargs)

    @distributed_trace
    def get_country_code(self, ip_address: str, **kwargs: Any) -> CountryRegionResult:
        """
        This service will return the ISO country code for the provided IP address. Developers can use
        this information  to block or alter certain content based on geographical locations where the
        application is being viewed from.

        :param ip_address:
            The IP address. Both IPv4 and IPv6 are allowed. Required.
        :type ip_address:
            str
        :return:
            CountryRegionResult
        :rtype:
            ~azure.maps.geolocation.models.CountryRegionResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/sample_get_country_code.py
                :start-after: [START get_country_code]
                :end-before: [END get_country_code]
                :language: python
                :dedent: 4
                :caption:  Return the ISO country code for the provided IP address.
        """

        geolocation_result = self._geolocation_client.get_location(format="json", ip_address=ip_address, **kwargs)

        return CountryRegionResult(
            ip_address=geolocation_result.ip_address, iso_code=geolocation_result.country_region.iso_code
        )
