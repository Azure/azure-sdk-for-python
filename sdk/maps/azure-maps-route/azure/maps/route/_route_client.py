# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from typing import TYPE_CHECKING, overload, Union, Any, List, Optional
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential

from ._base_client import RouteClientBase
from ._generated._route_client import RouteClient as RouteClientGen
from ._generated.models import *
from .models import (
    LatLon
)

if TYPE_CHECKING:
    from typing import Any, List, Optional, Object
    from azure.core.credentials import TokenCredential

class RouteClient(RouteClientBase):
    """Azure Maps Route REST APIs.
    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str or ~azure.ai.translation.document.MapsRouteApiVersion
    """

    def __init__(
        self,
        credential, # type: Union[AzureKeyCredential, TokenCredential]
        **kwargs  # type: Any
    ):
        # type: (...) -> None

        super().__init__(
            credential=credential, **kwargs
        )


    @distributed_trace
    def get_route_directions(
        self,
        routePoints,  # type: List[LatLon]
        **kwargs  # type: Any
    ):
         # type: (...) -> "_models.RouteDirectionsResponse"
        """**Applies to**\ : S0 and S1 pricing tiers.

        Returns  a route between an origin and a destination, passing through waypoints if they are
        specified. The route will take into account factors such as current traffic and the typical
        road speeds on the requested day of the week and time of day.

        Information returned includes the distance, estimated travel time, and a representation of the
        route geometry. Additional routing information such as optimized waypoint order or turn by turn
        instructions is also available, depending on the options selected.
        :param format: Desired format of the response. Value can be either *json* or *xml*.
        :type format: str or ~azure.maps.route.models.TextFormat
        :param query: The Coordinates through which the route is calculated, delimited by a colon.  A
         minimum of two coordinates is required.  The first one is the origin and the last is the
         destination of the route. Optional coordinates in-between act as WayPoints in the route.  You
         can pass up to 150 WayPoints.
        :type query: str
        :param max_alternatives: Number of desired alternative routes to be calculated. Default: 0,
         minimum: 0 and maximum: 5.
        :type max_alternatives: int
        :param alternative_type: Controls the optimality, with respect to the given planning criteria,
         of the calculated alternatives compared to the reference route.
        :type alternative_type: str or ~azure.maps.route.models.AlternativeRouteType
        :param min_deviation_distance: All alternative routes returned will follow the reference route
         (see section POST Requests) from the origin point of the calculateRoute request for at least
         this number of meters. Can only be used when reconstructing a route. The minDeviationDistance
         parameter cannot be used in conjunction with arriveAt.
        :type min_deviation_distance: int
        :param arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime. When a time zone offset is not specified it will be assumed to be that of the
         destination point. The arriveAt value must be in the future. The arriveAt parameter cannot be
         used in conjunction with departAt, minDeviationDistance or minDeviationTime.
        :type arrive_at: ~datetime.datetime
        :param depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00).
        :type depart_at: ~datetime.datetime
        :param min_deviation_time: All alternative routes 
        :type min_deviation_time: int
        :param instructions_type: If specified, guidance instructions will be returned. Note that the
         instructionsType parameter cannot be used in conjunction with routeRepresentation=none.
        :type instructions_type: str or ~azure.maps.route.models.RouteInstructionsType
        :param language: The language parameter determines the language of the guidance messages.
         Proper nouns (the names of streets, plazas, etc.) are returned in the specified  language, or
         if that is not available, they are returned in an available language  that is close to it.
         Allowed values are (a subset of) the IETF language tags. The currently supported  languages are
         listed in the `Supported languages  section
         <https://docs.microsoft.com/azure/azure-maps/supported-languages>`_.

         Default value: en-GB.
        :type language: str
        :type auxiliary_power_ink_w: str
        :keyword callable cls: A custom type or function that will be passed the direct response
        :return: RouteDirectionsResponse, or the result of cls(response)
        :rtype: ~azure.maps.route.models.RouteDirectionsResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        routePoints = LatLon() if not routePoints else routePoints

        return self._route_client.get_route_directions(
            query=routePoints,
            **kwargs
        )


    @distributed_trace
    def get_route_range(
        self,
        coordinates,  # type: LatLon
        budget, # type: RouteRangeBudget
        **kwargs  # type: Any
    ):
         # type: (...) -> "_models.GetRouteRangeResponse"
        """**Route Range (Isochrone) API**

        **Applies to**\ : S1 pricing tier.

        This service will calculate a set of locations that can be reached from the origin point based
        on fuel, energy,  time or distance budget that is specified. A polygon boundary (or Isochrone)
        is returned in a counterclockwise  orientation as well as the precise polygon center which was
        the result of the origin point.

        The returned polygon can be used for further processing such as  `Route Inside Geometry
        <https://docs.microsoft.com/rest/api/maps/search/postsearchinsidegeometry>`_ to  search for
        POIs within the provided Isochrone.

        :param format: Desired format of the response. Value can be either *json* or *xml*.
        :type format: str or ~azure.maps.route.models.TextFormat
        :param query: The Coordinate from which the range calculation should start.
        :type query: str
        :param fuel_budget_in_liters: Fuel budget in liters that determines maximal range which can be
         travelled using the specified Combustion Consumption Model.:code:`<br>` When fuelBudgetInLiters
         is used, it is mandatory to specify a detailed  Combustion Consumption Model.:code:`<br>`
         Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec, or
         distanceBudgetInMeters) must be used.
        :type fuel_budget_in_liters: float
        :param energy_budget_ink_wh: Electric energy budget in kilowatt hours (kWh) that determines
         maximal range which can be travelled using the specified Electric Consumption
         Model.:code:`<br>` When energyBudgetInkWh is used, it is mandatory to specify a detailed
         Electric Consumption Model.:code:`<br>` Exactly one budget (fuelBudgetInLiters,
         energyBudgetInkWh, timeBudgetInSec, or distanceBudgetInMeters) must be used.
        :type energy_budget_ink_wh: float
        :param time_budget_in_sec: Time budget in seconds that determines maximal range which can be
         travelled using driving time. The Consumption Model will only affect the range when routeType
         is eco.:code:`<br>` Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec,
         or distanceBudgetInMeters) must be used.
        :type time_budget_in_sec: float
        :param distance_budget_in_meters: Distance budget in meters that determines maximal range which
         can be travelled using driving distance.  The Consumption Model will only affect the range when
         routeType is eco.:code:`<br>` Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh,
         timeBudgetInSec, or distanceBudgetInMeters) must be used.
        :type distance_budget_in_meters: float
        :param depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00).
        :type depart_at: ~datetime.datetime
        :param route_type: The type of route requested.
        :type route_type: str or ~azure.maps.route.models.RouteType
        """
        coordinates = LatLon() if not coordinates else coordinates
        budget = RouteRangeBudget if not budget else budget
        
        return self._route_client.get_route_range(
            query=coordinates+budget,
            **kwargs
        )


    @distributed_trace
    def request_route_directions_batch(
        self,
        requests, #type: RouteDirectionsRequest[]
        **kwargs  # type: Any
    ):
        # type: (...) -> Optional["_models.RouteDirectionsBatchResponse"]
          
        poller = self._route_client.post_route_directions_batch_sync(
            requests,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace
    def begin_request_route_directions_batch(
        self,
        requests, #type: RouteDirectionsRequest[]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["_models.RouteDirectionsBatchResponse"]
          
        poller = self._route_client.begin_post_route_directions_batch(
            requests=requests,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace
    def begin_get_route_directions_batch_result(
        self,
        batchId, #type: string
        **kwargs  # type: Any
    ):
        # type: (...) -> Optional["_models.RouteDirectionsBatchResponse"]
        poller = self._route_client.begin_get_route_directions_batch(
            requests=batchId,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller

        
    @distributed_trace
    def request_route_matrix(
        self,
        routeMatrixQuery, #type: RouteMatrixQuery
        **kwargs  # type: Any
    ):
        # type: (...) -> "_models.RouteMatrixResponse"
        """**Applies to**\ : S1 pricing tier.

        The Matrix Routing service allows calculation of a matrix of route summaries for a set of
        routes defined by origin and destination locations by using an asynchronous (async) or
        synchronous (sync) POST request. For every given origin, the service calculates the cost of
        routing from that origin to every given destination. The set of origins and the set of
        destinations can be thought of as the column and row headers of a table and each cell in the
        table contains the costs of routing from the origin to the destination for that cell. As an
        example, let's say a food delivery company has 20 drivers and they need to find the closest
        driver to pick up the delivery from the restaurant. To solve this use case, they can call
        Matrix Route API.
        """
        return self._route_client.post_route_matrix_sync(
            query=routeMatrixQuery,
            **kwargs
        )


    @distributed_trace
    def begin_request_route_matrix(
        self,
        routeMatrixQuery, #type: RouteMatrixQuery
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["_models.RouteMatrixResponse"]
        """**Applies to**\ : S1 pricing tier.

        The Matrix Routing service allows calculation of a matrix of route summaries for a set of
        routes defined by origin and destination locations by using an asynchronous (async) or
        synchronous (sync) POST request. For every given origin, the service calculates the cost of
        routing from that origin to every given destination. The set of origins and the set of
        destinations can be thought of as the column and row headers of a table and each cell in the
        table contains the costs of routing from the origin to the destination for that cell. As an
        example, let's say a food delivery company has 20 drivers and they need to find the closest
        driver to pick up the delivery from the restaurant. To solve this use case, they can call
        Matrix Route API.
        """

        poller = self._route_client.begin_post_route_matrix(
            requests=routeMatrixQuery,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller
        

    @distributed_trace
    def begin_get_route_matrix_result(
        self,
        matrixId, #type: string
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["_models.RouteMatrixResponse"]
        """If the Matrix Route request was accepted successfully, the Location header in the response
        contains the URL to download the results of the request.
        """
        
        poller = self._route_client.begin_get_route_matrix(
            requests=matrixId,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller