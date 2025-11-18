# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""

from typing import Optional

class CountryRegionResult(object):
    """Represents coordinate latitude and longitude

    :param ip_address:
        The IP Address of the request.
    :type ip_address: Optional[str]
    :param iso_code:
        The IP Address's 2-character code of the country or region.
        Please note, IP address in ranges reserved for special purpose will return Null for country/region.
    :type iso_code: Optional[str]
    """

    def __init__(self, ip_address: Optional[str] = None, iso_code: Optional[str] = None):
        self.ip_address = ip_address
        self.iso_code = iso_code


__all__: list[str] = ["CountryRegionResult"]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
