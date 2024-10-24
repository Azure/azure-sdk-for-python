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

from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy
from azure.core.tracing.decorator_async import distributed_trace_async

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
        authentication_policy = AzureKeyCredentialPolicy(
            name="subscription-key", credential=credential
        )
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
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
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
        format: str = "json",
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

        :param format: Desired format of the response, default is 'json'
        :param timezone_id: IANA time zone ID (optional)
        :param coordinates: Coordinates (latitude, longitude) as a list (optional)
        :param accept_language: Preferred language for the response (optional)
        :param options: Options for the type of information returned (optional)
        :param time_stamp: Reference timestamp (optional)
        :param dst_from: Start date for daylight savings time transitions (optional)
        :param dst_lasting_years: Number of years for DST transitions (optional)
        :return: JSON response with timezone information
        """
        result = cast(JSON, {})
        if timezone_id:
            # Use the method for getting timezone by ID
            result = await self.get_timezone_by_id(
                format=format,
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
                format=format,
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
