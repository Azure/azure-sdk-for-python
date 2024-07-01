# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
import datetime
from typing import Union, Any, IO, List, Optional, MutableMapping
from azure.core.tracing.decorator_async import distributed_trace_async
from ._base_client_async import AsyncTimezoneClientBase
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


class AzureTimezoneClient(AsyncTimezoneClientBase):

    @distributed_trace_async
    async def get_timezone_by_id(
            self,
            format: str = "json",
            *,
            timezone_id: str,
            accept_language: Optional[str] = None,
            options: Optional[str] = None,
            time_stamp: Optional[datetime.datetime] = None,
            daylight_savings_time_from: Optional[datetime.datetime] = None,
            daylight_savings_time_lasting_years: Optional[int] = None,
            **kwargs: Any
    ) -> JSON:
        """Use to get the current, historical, and future time zone information for the specified IANA
        time zone ID.

        The ``Get Timezone By ID`` API is an HTTP ``GET`` request that returns current, historical, and
        future time zone information for the specified IANA time zone ID.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :keyword timezone_id: The IANA time zone ID. Required.
        :paramtype timezone_id: str
        :keyword accept_language: Specifies the language code in which the timezone names should be
         returned. If no language code is provided, the response will be in "EN". Please refer to
         `Supported Languages <https://docs.microsoft.com/azure/azure-maps/supported-languages>`_ for
         details. Default value is None.
        :paramtype accept_language: str
        :keyword options: Alternatively, use alias "o". Options available for types of information
         returned in the result. Known values are: "none", "zoneInfo", "transitions", and "all". Default
         value is None.
        :paramtype options: str
        :keyword time_stamp: Alternatively, use alias "stamp", or "s". Reference time, if omitted, the
         API will use the machine time serving the request. Default value is None.
        :paramtype time_stamp: ~datetime.datetime
        :keyword daylight_savings_time_from: Alternatively, use alias "tf". The start date from which
         daylight savings time (DST) transitions are requested, only applies when "options" = all or
         "options" = transitions. Default value is None.
        :paramtype daylight_savings_time_from: ~datetime.datetime
        :keyword daylight_savings_time_lasting_years: Alternatively, use alias "ty". The number of
         years from "transitionsFrom" for which DST transitions are requested, only applies when
         "options" = all or "options" = transitions. Default value is None.
        :paramtype daylight_savings_time_lasting_years: int
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.get_timezone_by_id(
            format,
            timezone_id=timezone_id,
            accept_language=accept_language,
            options=options,
            time_stamp=time_stamp,
            daylight_savings_time_from=daylight_savings_time_from,
            daylight_savings_time_lasting_years=daylight_savings_time_lasting_years,
            **kwargs
        )

        return result

    @distributed_trace_async
    async def get_timezone_by_coordinates(
            self,
            format: str = "json",
            *,
            coordinates: List[float],
            accept_language: Optional[str] = None,
            options: Optional[str] = None,
            time_stamp: Optional[datetime.datetime] = None,
            daylight_savings_time_from: Optional[datetime.datetime] = None,
            daylight_savings_time_lasting_years: Optional[int] = None,
            **kwargs: Any
    ) -> JSON:
        """Use to get the current, historical, and future time zone information for the specified
        latitude-longitude pair.

        The ``Get Timezone By Coordinates`` API is an HTTP ``GET`` request that returns current,
        historical, and future time zone information for a specified latitude-longitude pair. In
        addition, the API provides sunset and sunrise times for a given location.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :keyword coordinates: Coordinates of the point for which time zone information is requested.
         This parameter is a list of coordinates, containing a pair of coordinate(lat, long). When this
         endpoint is called directly, coordinates are passed in as a single string containing
         coordinates, separated by commas. Required.
        :paramtype coordinates: list[float]
        :keyword accept_language: Specifies the language code in which the timezone names should be
         returned. If no language code is provided, the response will be in "EN". Please refer to
         `Supported Languages <https://docs.microsoft.com/azure/azure-maps/supported-languages>`_ for
         details. Default value is None.
        :paramtype accept_language: str
        :keyword options: Alternatively, use alias "o". Options available for types of information
         returned in the result. Known values are: "none", "zoneInfo", "transitions", and "all". Default
         value is None.
        :paramtype options: str
        :keyword time_stamp: Alternatively, use alias "stamp", or "s". Reference time, if omitted, the
         API will use the machine time serving the request. Default value is None.
        :paramtype time_stamp: ~datetime.datetime
        :keyword daylight_savings_time_from: Alternatively, use alias "tf". The start date from which
         daylight savings time (DST) transitions are requested, only applies when "options" = all or
         "options" = transitions. Default value is None.
        :paramtype daylight_savings_time_from: ~datetime.datetime
        :keyword daylight_savings_time_lasting_years: Alternatively, use alias "ty". The number of
         years from "transitionsFrom" for which DST transitions are requested, only applies when
         "options" = all or "options" = transitions. Default value is None.
        :paramtype daylight_savings_time_lasting_years: int
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.get_timezone_by_coordinates(
            format,
            coordinates=coordinates,
            accept_language=accept_language,
            options=options,
            time_stamp=time_stamp,
            daylight_savings_time_from=daylight_savings_time_from,
            daylight_savings_time_lasting_years=daylight_savings_time_lasting_years,
            **kwargs
        )

        return result

    @distributed_trace_async
    async def get_windows_timezone_ids(self, format: str = "json", **kwargs: Any) -> List[JSON]:
        """Use to get the list of Windows Time Zone IDs.

        The ``Get Windows Time Zones`` API is an HTTP ``GET`` request that returns a full list of
        Windows Time Zone IDs.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :return: list of JSON object
        :rtype: list[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.get_windows_timezone_ids(
            format,
            **kwargs
        )

        return result

    @distributed_trace_async
    async def get_iana_timezone_ids(self, format: str = "json", **kwargs: Any) -> List[JSON]:
        """Use to get the list of IANA time zone IDs.

        The ``Get IANA Time Zones`` API is an HTTP ``GET`` request that returns a full list of Internet
        Assigned Numbers Authority (IANA) time zone IDs. Updates to the IANA service are reflected in
        the system within one day.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :return: list of JSON object
        :rtype: list[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.get_iana_timezone_ids(
            format,
            **kwargs
        )

        return result

    @distributed_trace_async
    async def get_iana_version(self, format: str = "json", **kwargs: Any) -> JSON:
        """Use to get the current IANA version number.

        The ``Get Time Zone IANA Version`` API is an HTTP ``GET`` request that returns the current
        Internet Assigned Numbers Authority (IANA) version number as Metadata.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.get_iana_version(
            format,
            **kwargs
        )

        return result

    @distributed_trace_async
    async def convert_windows_timezone_to_iana(
            self,
            format: str = "json",
            *,
            windows_timezone_id: str,
            windows_territory_code: Optional[str] = None,
            **kwargs: Any
    ) -> List[JSON]:
        """Use to get the IANA ID.

        The ``Get Windows to IANA Time Zone`` API is an HTTP ``GET`` request that returns a
        corresponding Internet Assigned Numbers Authority (IANA) ID, given a valid Windows Time Zone
        ID. Multiple IANA IDs may be returned for a single Windows ID. It is possible to narrow these
        results by adding an optional territory parameter.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :keyword windows_timezone_id: The Windows time zone ID. Required.
        :paramtype windows_timezone_id: str
        :keyword windows_territory_code: Windows Time Zone territory code. Default value is None.
        :paramtype windows_territory_code: str
        :return: list of JSON object
        :rtype: list[JSON]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = await self._timezone_client.convert_windows_timezone_to_iana(
            format,
            windows_timezone_id=windows_timezone_id,
            windows_territory_code=windows_territory_code,
            **kwargs
        )

        return result
