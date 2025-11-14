# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from ._operations import _MapsGeolocationClientOperationsMixin as _MapsGeolocationClientOperationsMixinGenerated
from azure.core.tracing.decorator_async import distributed_trace_async
from typing import Any
from ..models._patch import CountryRegionResult

class _MapsGeolocationClientOperationsMixin(_MapsGeolocationClientOperationsMixinGenerated):
    @distributed_trace_async
    async def get_country_code(self, ip_address: str, **kwargs: Any) -> CountryRegionResult:  # type: ignore[override]
        """
        This service will return the ISO country code for the provided IP address. Developers can use
        this information  to block or alter certain content based on geographical locations where the
        application is being viewed from.

        :param ip_address:
            The IP address. Both IPv4 and IPv6 are allowed. Required.
        :type ip_address: str
        :return:
            CountryRegionResult
        :rtype:
            ~azure.maps.geolocation.models.CountryRegionResult
        :raises ~azure.core.exceptions.HttpResponseError:

        .. admonition:: Example:

            .. literalinclude:: ../samples/async_samples/sample_get_country_code_async.py
                :start-after: [START get_country_code_async]
                :end-before: [END get_country_code_async]
                :language: python
                :dedent: 4
                :caption:  Return the ISO country code for the provided IP address.
        """
        geolocation_result = await super().get_country_code(
            format="json", ip_address=ip_address, **kwargs
        )

        return CountryRegionResult(
            ip_address=geolocation_result.ip_address,
            iso_code=(
                geolocation_result.country_region.iso_code
                if geolocation_result.country_region else None
            )
        )


__all__: list[str] = ["_MapsGeolocationClientOperationsMixin"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
