# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, C0302, C0203
from typing import List, NamedTuple
from .._generated.models import (
    CountryRecord,
    TimeTransition,
    TimezoneNames,
    TimezoneId as _TimezoneId,
    ReferenceTime,
)


class LatLon(NamedTuple):
    """Represents coordinate latitude and longitude

    :keyword lat: The coordinate as latitude.
    :paramtype lat: float
    :keyword lon: The coordinate as longitude.
    :paramtype lon: float
    """
    lat: float = 0
    lon: float = 0

class TimezoneId(_TimezoneId):
    """TimezoneId.

    Variables are only populated by the server, and will be ignored when sending a request.

    :ivar id: Id property.
    :vartype id: str
    :ivar aliases: An array of time zone ID aliases. Only returned when [options]=`zoneinfo` or
      `all`. Aliases may be `None`.
    :vartype aliases: list[str]
    :ivar countries: An array of country records. Only returned when [options]=`zoneinfo` or
      `all`.
    :vartype countries: list[~azure.maps.timezone.models.CountryRecord]
    :ivar names: Timezone names object.
    :vartype names: ~azure.maps.timezone.models.TimezoneNames
    :ivar reference_time: Details in effect at the local time.
    :vartype reference_time: ~azure.maps.timezone.models.ReferenceTime
    :ivar representative_point: Representative point property.
    :vartype representative_point: ~azure.maps.timezone.models.LatLon
    :ivar time_transitions: Time zone DST transitions from [transitionsFrom] until timestamp + 1
      year.
    :vartype time_transitions: list[~azure.maps.timezone.models.TimeTransition]
    """

    def __init__(
        self,
        *,
        representative_point: LatLon = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.representative_point = None if not representative_point else LatLon(
            representative_point.lat, representative_point.lon
        )
