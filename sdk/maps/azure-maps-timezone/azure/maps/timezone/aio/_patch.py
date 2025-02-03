# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
# pylint: disable=unused-import
import datetime
import sys
from typing import Union, Any, List, Optional, cast
from azure.core.tracing.decorator_async import distributed_trace_async

from azure.core.credentials import AzureKeyCredential, AzureSasCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, AzureSasCredentialPolicy
from ._client import TimezoneClient as TimezoneClientGenerated

if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object

__all__: List[str] = ["MapsTimeZoneClient"]


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


def _authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(name="subscription-key", credential=credential)
    elif isinstance(credential, AzureSasCredential):
        authentication_policy = AzureSasCredentialPolicy(credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )
    return authentication_policy


# pylint: disable=C4748
class MapsTimeZoneClient(TimezoneClientGenerated):
    def __init__(
        self,
        credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential],
        client_id: Optional[str] = None,
        *,
        endpoint: str = "https://atlas.microsoft.com",
        **kwargs: Any
    ) -> None:

        super().__init__(
            credential=credential,  # type: ignore
            client_id=client_id,
            endpoint=endpoint,
            authentication_policy=kwargs.pop("authentication_policy", _authentication_policy(credential)),
            **kwargs
        )

    @distributed_trace_async
    async def get_timezone(
        self,
        *,
        timezone_id: Optional[str] = None,
        coordinates: Optional[List[float]] = None,
        accept_language: Optional[str] = None,
        options: Optional[str] = None,
        time_stamp: Optional[datetime.datetime] = None,
        dst_from: Optional[datetime.datetime] = None,
        dst_lasting_years: Optional[int] = None,
        **kwargs: Any
    ) -> JSON:
        """Unified method to get timezone information by either timezone_id or coordinates.
        Only one of `coordinate` or `timezone_id` will be considered.
        If `timezone_id` is provided, `coordinate` will be ignored.

        :keyword timezone_id: The IANA time zone ID.
        :paramtype timezone_id: str
        :keyword coordinates: Coordinates of the point for which time zone information is requested.
         This parameter is a list of coordinates, containing a pair of coordinate(lat, long). When this
         endpoint is called directly, coordinates are passed in as a single string containing
         coordinates, separated by commas.
        :paramtype coordinates: list[float]
        :keyword accept_language: Specifies the language code in which the timezone names should be
         returned. If no language code is provided, the response will be in "EN". Please refer to
         `Supported Languages <https://learn.microsoft.com/azure/azure-maps/supported-languages>`_ for
         details. Default value is None.
        :paramtype accept_language: str
        :keyword options: Options available for types of information
         returned in the result. Known values are: "none", "zoneInfo", "transitions", and "all". Default
         value is None.
        :paramtype options: str
        :keyword time_stamp: Reference time, if omitted, the
         API will use the machine time serving the request. Default value is None.
        :paramtype time_stamp: ~datetime.datetime
        :keyword dst_from: The start date from which
         daylight savings time (DST) transitions are requested, only applies when "options" = all or
         "options" = transitions. Default value is None.
        :paramtype dst_from: ~datetime.datetime
        :keyword dst_lasting_years: The number of
         years from "transitionsFrom" for which DST transitions are requested, only applies when
         "options" = all or "options" = transitions. Default value is None.
        :paramtype dst_lasting_years: int
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        result = cast(JSON, {})
        if timezone_id:
            # Use the method for getting timezone by ID
            result = await self.get_timezone_by_id(
                format="json",
                timezone_id=timezone_id,
                accept_language=accept_language,
                options=options,
                time_stamp=time_stamp,
                dst_from=dst_from,
                dst_lasting_years=dst_lasting_years,
                **kwargs
            )
        elif coordinates:
            # Use the method for getting timezone by coordinates
            result = await self.get_timezone_by_coordinates(
                format="json",
                coordinates=coordinates,
                accept_language=accept_language,
                options=options,
                time_stamp=time_stamp,
                dst_from=dst_from,
                dst_lasting_years=dst_lasting_years,
                **kwargs
            )
        else:
            raise ValueError("Either 'timezone_id' or 'coordinates' must be provided.")

        return result
