# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Any, Optional
import sys

from ._operations import WeatherOperations as WeatherOperationsGenerated

__all__: List[str] = ["WeatherOperations"]  # Add all objects you want publicly available to users at this package level


if sys.version_info >= (3, 9):
    from collections.abc import MutableMapping
else:
    from typing import MutableMapping  # type: ignore  # pylint: disable=ungrouped-imports
JSON = MutableMapping[str, Any]  # pylint: disable=unsubscriptable-object


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """


class WeatherOperations(WeatherOperationsGenerated):
    def get_tropical_storm_search(
        self,
        format: str = "json",
        *,
        year: int,
        basin_id: Optional[str] = None,
        government_storm_id: Optional[int] = None,
        **kwargs: Any
    ) -> JSON:
        """Use to get a list of storms issued by national weather forecasting agencies.

        The ``Get Tropical Storm Search`` API is an HTTP ``GET`` request that returns a list of
        government-issued tropical storms by year, basin ID, and government ID. Information about the
        tropical storms includes, government ID, basin ID, status, year, name and if it is subtropical.

        :param format: Desired format of the response. Only ``json`` format is supported. "json"
         Default value is "json".
        :type format: str
        :keyword year: Year of the cyclone(s). Required.
        :paramtype year: int
        :keyword basin_id: Basin identifier. Known values are: "AL", "EP", "SI", "NI", "CP", "NP", and
         "SP". Default value is None.
        :paramtype basin_id: str
        :keyword government_storm_id: Government storm Id. Default value is None.
        :paramtype government_storm_id: int
        :return: JSON object
        :rtype: JSON
        :raises ~azure.core.exceptions.HttpResponseError:

        Example:
            .. code-block:: python

                # response body for status code(s): 200
                response == {
                    "nextLink": "str",
                    "results": [
                        {
                            "basinId": "str",
                            "govId": 0,
                            "isActive": bool,
                            "isRetired": bool,
                            "isSubtropical": bool,
                            "name": "str",
                            "year": "str"
                        }
                    ]
                }
        """
        return super().search_tropical_storm(
            format=format, year=year, basin_id=basin_id, government_storm_id=government_storm_id, **kwargs
        )
