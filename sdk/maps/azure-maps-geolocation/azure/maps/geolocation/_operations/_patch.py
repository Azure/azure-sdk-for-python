# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Any
from azure.core.tracing.decorator import distributed_trace
from ._operations import (
    _MapsGeolocationClientOperationsMixin as _MapsGeolocationClientOperationsMixinGenerated
)
from ..models._patch import CountryRegionResult

class _MapsGeolocationClientOperationsMixin(_MapsGeolocationClientOperationsMixinGenerated):
    @distributed_trace
    def get_country_code(  # type: ignore[override]
        self,
        ip_address: str,
        **kwargs: Any
    ) -> CountryRegionResult:
        """Use to get the ISO country/region code for a given IP address.

        The ``Get IP To Location`` API is an HTTP ``GET`` request that returns the
        ISO country/region code for a given IP address. Developers can use this
        information to block or modify content based on the geographical location
        from which the application is accessed.

        :param ip_address: The IP address. Both IPv4 and IPv6 are allowed. Required.
        :type ip_address: str
        :return: CountryRegionResult.
        :rtype: ~azure.maps.geolocation.models.CountryRegionResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        geolocation_result = super().get_country_code(
            format="json", ip_address=ip_address, **kwargs
        )

        return CountryRegionResult(
            ip_address=geolocation_result.ip_address,
            iso_code=(
                geolocation_result.country_region.iso_code
                if geolocation_result.country_region else None
            )
        )


__all__: list[str] = ["_MapsGeolocationClientOperationsMixin"]  # Add all objects you want publicly available to users


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
