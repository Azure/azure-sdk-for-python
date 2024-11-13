# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import Optional


class CountryRegionResult(object):
    """Represents coordinate latitude and longitude

    :keyword ip_address:
        The IP Address of the request.
    :paramtype ip_address: Optional[str]
    :keyword iso_code: iso_code:
        The IP Address's 2-character code of the country or region.
        Please note, IP address in ranges reserved for special purpose will return Null for country/region.
    :paramtype iso_code: Optional[str]
    """

    def __init__(self, ip_address: Optional[str] = None, iso_code: Optional[str] = None):
        self.ip_address = ip_address
        self.iso_code = iso_code
