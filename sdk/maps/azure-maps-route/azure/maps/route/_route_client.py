# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302
from typing import TYPE_CHECKING, overload, Union, Any, List, Optional
from azure.core.tracing.decorator import distributed_trace
from azure.core.exceptions import HttpResponseError
from azure.core.credentials import AzureKeyCredential

from ._base_client import MapsRouteClientBase
from ._generated.models import (
    RouteDirectionsResponse,
    RouteRangeBudget,
    GetRouteRangeResponse,
    RouteDirectionsRequest,
    RouteDirectionsBatchResponse,
    RouteMatrixQuery,
    RouteMatrixResponse,
    AlternativeRouteType
)

from .models import (
    LatLon
)

if TYPE_CHECKING:
    from typing import Any, List, Optional, Object
    from azure.core.credentials import TokenCredential
    from azure.core.polling import LROPoller

def latlon_to_string(route_point_list):
    for route_point in route_point_list:
        query_items = ":".join(f"{route_point.lat},{route_point.lon}")
    return query_items

# By default, use the latest supported API version
class MapsRouteClient(MapsRouteClientBase):
    """Azure Maps Route REST APIs.

    :param credential: Credential needed for the client to connect to Azure.
    :type credential: ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword api_version:
            The API version of the service to use for requests. It defaults to the latest service version.
            Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
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

    # cSpell:disable
    @distributed_trace
    def get_route_directions(
        self,
        route_points,  # type: List[LatLon]
        **kwargs  # type: Any
    ):
         # type: (...) -> "RouteDirectionsResponse"
        """
        Returns a route between an origin and a destination, passing through waypoints if they are
        specified. The route will take into account factors such as current traffic and the typical
        road speeds on the requested day of the week and time of day.

        Information returned includes the distance, estimated travel time, and a representation of the
        route geometry. Additional routing information such as optimized waypoint order or turn by turn
        instructions is also available, depending on the options selected.

        :param route_points: The Coordinate from which the range calculation should start.
        :type route_points: List[~azure.maps.route._models.LatLon]
        :param max_alternatives: Number of desired alternative routes to be calculated.
        :type max_alternatives: int
        :param alternative_type: Controls the optimality, with respect to the given planning criteria,
         of the calculated alternatives compared to the reference route.
        :type alternative_type: str or ~azure.maps.route.models.AlternativeRouteType
        :param min_deviation_distance: All alternative routes returned will follow the reference route
         (see section POST Requests) from the origin point of the calculateRoute request for at least
         this number of meters
        :type min_deviation_distance: int
        :param arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime.
        :type arrive_at: ~datetime.datetime
        :param depart_at: The date and time of departure from the origin point.
        :type depart_at: ~datetime.datetime
        :param min_deviation_time: All alternative routes
        :type min_deviation_time: int
        :param instructions_type: If specified, guidance instructions will be returned.
        :type instructions_type: str or ~azure.maps.route.models.RouteInstructionsType
        :param language: The language parameter determines the language of the guidance messages.
        :type language: str
        :param compute_best_order: Re-order the route waypoints using a fast heuristic algorithm to
         reduce the route length.
        :type compute_best_order: bool
        :param route_representation: Specifies the representation of the set of routes provided as
         response.
        :type route_representation: str or ~azure.maps.route.models.RouteRepresentation
        :param compute_travel_time_for: Specifies whether to return additional travel times using
         different types of traffic information (none, historic, live) as well as the default
         best-estimate travel time.
        :type compute_travel_time_for: str or ~azure.maps.route.models.ComputeTravelTimeFor
        :param vehicle_heading: The directional heading of the vehicle in degrees starting at true
         North and continuing in clockwise direction.
        :type vehicle_heading: int
        :param report: Specifies which data should be reported for diagnosis purposes.
        :type report: str
        :param section_type: Specifies which of the section types is reported in the route response.
        :type section_type: str or ~azure.maps.route.models.SectionType
        :param vehicle_axle_weight: Weight per axle of the vehicle in kg.
        :type vehicle_axle_weight: int
        :param vehicle_width: Width of the vehicle in meters.
        :type vehicle_width: float
        :param vehicle_height: Height of the vehicle in meters.
        :type vehicle_height: float
        :param vehicle_length: Length of the vehicle in meters.
        :type vehicle_length: float
        :param vehicle_max_speed: Maximum speed of the vehicle in km/hour.
        :type vehicle_max_speed: int
        :param vehicle_weight: Weight of the vehicle in kilograms.
        :type vehicle_weight: int
        :param vehicle_commercial: Vehicle is used for commercial purposes and thus may not be allowed
         to drive  on some roads.
        :type vehicle_commercial: bool
        :param windingness: Level of turns for thrilling route.
        :type windingness: str or ~azure.maps.route.models.WindingnessLevel
        :param hilliness: Degree of hilliness for thrilling route.
        :type hilliness: str or ~azure.maps.route.models.HillinessDegree
        :param travel_mode: The mode of travel for the requested route.
        :type travel_mode: str or ~azure.maps.route.models.TravelMode
        :param avoid: Specifies something that the route calculation should try to avoid when
         determining the route.
        :type avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :param traffic: Input values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing. Note that although the current traffic
         data is ignored during routing, the effect of historic traffic on effective road speeds is still
         incorporated.
        :type traffic: bool
        :param route_type: The type of route requested.
        :type route_type: str or ~azure.maps.route.models.RouteType
        :param vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads.
        :type vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :param vehicle_engine_type: Engine type of the vehicle.
        :type vehicle_engine_type: str or ~azure.maps.route.models.VehicleEngineType
        :param constant_speed_consumption_in_liters_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :type constant_speed_consumption_in_liters_per_hundred_km: float
        :param current_fuel_in_liters: Specifies the current supply of fuel in liters.
        :type current_fuel_in_liters: float
        :param auxiliary_power_in_liters_per_hour: Specifies the amount of fuel consumed for sustaining
         auxiliary systems of the vehicle, in liters per hour.
        :type auxiliary_power_in_liters_per_hour: float
        :param fuel_energy_density_in_m_joules_per_liter: Specifies the amount of chemical energy
         stored in one liter of fuel in megajoules (MJ).
        :type fuel_energy_density_in_m_joules_per_liter: float
        :param acceleration_efficiency: Specifies the efficiency of converting chemical energy stored
         in fuel to kinetic energy when the vehicle accelerates.
        :type acceleration_efficiency: float
        :param deceleration_efficiency: Specifies the efficiency of converting kinetic energy to saved
         (not consumed) fuel when the vehicle decelerates.
        :type deceleration_efficiency: float
        :param uphill_efficiency: Specifies the efficiency of converting chemical energy stored in fuel
         to potential energy when the vehicle gains elevation.
        :type uphill_efficiency: float
        :param downhill_efficiency: Specifies the efficiency of converting potential energy to saved
         (not consumed) fuel when the vehicle loses elevation.
        :type downhill_efficiency: float
        :param constant_speed_consumption_in_kwh_per_hundred_km: Specifies the speed-dependent component
         of consumption.
        :type constant_speed_consumption_in_kwh_per_hundred_km: str
        :param current_charge_ink_wh: Specifies the current electric energy supply in kilowatt hours
         (kWh).
        :type current_charge_ink_wh: str
        :param max_charge_ink_wh: Specifies the maximum electric energy supply in kilowatt hours (kWh)
         that may be stored in the vehicle's battery.
        :type max_charge_ink_wh: str
        :keyword str auxiliary_power_in_kw: Specifies the amount of power consumed for sustaining auxiliary
         systems, in kilowatts (kW).
        :return: RouteDirectionsResponse
        :rtype: ~azure.maps.route.models.RouteDirectionsResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """

        query_items = ""
        if route_points:
            query_items = latlon_to_string(route_points)

        return self._route_client.get_route_directions(
            query=query_items,
            constant_speed_consumption_in_liters_per_hundredkm=kwargs.get(
                'constant_speed_consumption_in_liters_per_hundred_km', None
            ),
            constant_speed_consumption_ink_wh_per_hundredkm=kwargs.get(
                'constant_speed_consumption_in_kwh_per_hundred_km', None
            ),
            auxiliary_power_ink_w=kwargs.get('auxiliary_power_in_kw', None),
            **kwargs
        )

    # cSpell:disable
    @distributed_trace
    def get_route_range(
        self,
        coordinates,  # type: LatLon
        **kwargs  # type: Any
    ):
         # type: (...) -> "GetRouteRangeResponse"
        """**Route Range (Isochrone) API**

        This service will calculate a set of locations that can be reached from the origin point based
        on fuel, energy,  time or distance budget that is specified. A polygon boundary (or Isochrone)
        is returned in a counterclockwise  orientation as well as the precise polygon center which was
        the result of the origin point.

        :param coordinates: The Coordinate from which the range calculation should start.
        :type coordinates: ~azure.maps.route._models.LatLon
        :param fuel_budget_in_liters: Fuel budget in liters that determines maximal range which can be
         travelled using the specified Combustion Consumption Model.
         Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec, or
         distanceBudgetInMeters) must be used.
        :type fuel_budget_in_liters: float
        :param energy_budget_in_kwh: Electric energy budget in kilowatt hours (kWh) that determines
         maximal range which can be travelled using the specified Electric Consumption
         Model.
        :type energy_budget_in_kwh: float
        :param time_budget_in_sec: Time budget in seconds that determines maximal range which can be
         travelled using driving time. The Consumption Model will only affect the range when routeType
         is eco. Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec,
         or distanceBudgetInMeters) must be used.
        :type time_budget_in_sec: float
        :param distance_budget_in_meters: Distance budget in meters that determines maximal range which
         can be travelled using driving distance.
        :type distance_budget_in_meters: float
        :param depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00).
        :type depart_at: ~datetime.datetime
        :param route_type: The type of route requested.
        :type route_type: str or ~azure.maps.route.models.RouteType
        :type traffic: bool
        :param avoid: Specifies something that the route calculation should try to avoid when
         determining the route.
        :type avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :param travel_mode: The mode of travel for the requested route.
        :type travel_mode: str or ~azure.maps.route.models.TravelMode
        :param hilliness: Degree of hilliness for thrilling route.
        :type hilliness: str or ~azure.maps.route.models.HillinessDegree
        :param windingness: Level of turns for thrilling route.
        :type windingness: str or ~azure.maps.route.models.WindingnessLevel
        :param vehicle_axle_weight: Weight per axle of the vehicle in kg. A value of 0 means that
         weight restrictions per axle are not considered.
        :type vehicle_axle_weight: int
        :param vehicle_width: Width of the vehicle in meters. A value of 0 means that width
         restrictions are not considered.
        :type vehicle_width: float
        :param vehicle_height: Height of the vehicle in meters. A value of 0 means that height
         restrictions are not considered.
        :type vehicle_height: float
        :param vehicle_length: Length of the vehicle in meters. A value of 0 means that length
         restrictions are not considered.
        :type vehicle_length: float
        :param vehicle_max_speed: Maximum speed of the vehicle in km/hour.
        :type vehicle_max_speed: int
        :param vehicle_weight: Weight of the vehicle in kilograms.
        :type vehicle_weight: int
        :param vehicle_commercial: Vehicle is used for commercial purposes and thus may not be allowed
         to drive on some roads.
        :type vehicle_commercial: bool
        :param vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads.
        :type vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :param vehicle_engine_type: Engine type of the vehicle.
        :type vehicle_engine_type: str or ~azure.maps.route.models.VehicleEngineType
        :param constant_speed_consumption_in_liters_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :type constant_speed_consumption_in_liters_per_hundred_km: float
        :param current_fuel_in_liters: Specifies the current supply of fuel in liters.
        :type current_fuel_in_liters: float
        :param auxiliary_power_in_liters_per_hour: Specifies the amount of fuel consumed for sustaining
         auxiliary systems of the vehicle, in liters per hour.
        :type auxiliary_power_in_liters_per_hour: float
        :param fuel_energy_density_in_m_joules_per_liter: Specifies the amount of chemical energy
         stored in one liter of fuel in megajoules (MJ).
        :type fuel_energy_density_in_m_joules_per_liter: float
        :param acceleration_efficiency: Specifies the efficiency of converting chemical energy stored
         in fuel to kinetic energy when the vehicle accelerates
        :type acceleration_efficiency: float
        :param deceleration_efficiency: Specifies the efficiency of converting kinetic energy to saved
         (not consumed) fuel when the vehicle decelerates.
        :type deceleration_efficiency: float
        :param uphill_efficiency: Specifies the efficiency of converting chemical energy stored in fuel
         to potential energy when the vehicle gains elevation
        :type uphill_efficiency: float
        :param downhill_efficiency: Specifies the efficiency of converting potential energy to saved
         (not consumed) fuel when the vehicle loses elevation
        :type downhill_efficiency: float
        :param constant_speed_consumption_in_kwh_per_hundred_km: Specifies the speed-dependent component
         of consumption.
        :type constant_speed_consumption_in_kwh_per_hundred_km: str
        :param current_charge_in_kwh: Specifies the current electric energy supply in kilowatt hours
         (kWh).
        :type current_charge_in_kwh: str
        :param max_charge_in_kwh: Specifies the maximum electric energy supply in kilowatt hours (kWh)
         that may be stored in the vehicle's battery.
        :type max_charge_in_kwh: str
        :param auxiliary_power_in_kw: Specifies the amount of power consumed for sustaining auxiliary
         systems, in kilowatts (kW).
        :type auxiliary_power_in_kw: str
        :return: GetRouteRangeResponse
        :rtype: ~azure.maps.route.models.GetRouteRangeResponse
        :raises: ~azure.core.exceptions.HttpResponseError
        """
        coordinates = LatLon() if not coordinates else coordinates

        return self._route_client.get_route_range(
            query=f"{coordinates.lat, coordinates.lon}",
            energy_budget_ink_wh=kwargs.get('energy_budget_in_kwh', None),
            constant_speed_consumption_in_liters_per_hundredkm=kwargs.get(
                'constant_speed_consumption_in_liters_per_hundred_km', None
            ),
            constant_speed_consumption_ink_wh_per_hundredkm=kwargs.get(
                'constant_speed_consumption_in_kwh_per_hundred_km', None
            ),
            current_charge_ink_wh=kwargs.get('current_charge_in_kwh', None),
            max_charge_ink_wh=kwargs.get('max_charge_in_kwh', None),
            auxiliary_power_ink_w=kwargs.get('auxiliary_power_in_kw', None),
            **kwargs
        )


    @distributed_trace
    def request_route_directions_batch(
        self,
        route_points_batch, #type: BatchRequestBody
        **kwargs  # type: Any
    ):
        # type: (...) -> RouteDirectionsBatchResponse
        """Sends batches of route directions requests.
        The method return the result directly.

        :param route_points_batch: A list of the Coordinate list from which the range calculation should start.
        :type route_points_batch: BatchRequestBody
        :param max_alternatives: Number of desired alternative routes to be calculated.
        :type max_alternatives: int
        :param alternative_type: Controls the optimality, with respect to the given planning criteria,
         of the calculated alternatives compared to the reference route.
        :type alternative_type: str or ~azure.maps.route.models.AlternativeRouteType
        :param min_deviation_distance: All alternative routes returned will follow the reference route
         (see section POST Requests) from the origin point of the calculateRoute request for at least
         this number of meters
        :type min_deviation_distance: int
        :param arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime.
        :type arrive_at: ~datetime.datetime
        :param depart_at: The date and time of departure from the origin point.
        :type depart_at: ~datetime.datetime
        :param min_deviation_time: All alternative routes
        :type min_deviation_time: int
        :param instructions_type: If specified, guidance instructions will be returned.
        :type instructions_type: str or ~azure.maps.route.models.RouteInstructionsType
        :param language: The language parameter determines the language of the guidance messages.
        :type language: str
        :param compute_best_order: Re-order the route waypoints using a fast heuristic algorithm to
         reduce the route length.
        :type compute_best_order: bool
        :param route_representation: Specifies the representation of the set of routes provided as
         response.
        :type route_representation: str or ~azure.maps.route.models.RouteRepresentation
        :param compute_travel_time_for: Specifies whether to return additional travel times using
         different types of traffic information (none, historic, live) as well as the default
         best-estimate travel time.
        :type compute_travel_time_for: str or ~azure.maps.route.models.ComputeTravelTimeFor
        :param vehicle_heading: The directional heading of the vehicle in degrees starting at true
         North and continuing in clockwise direction.
        :type vehicle_heading: int
        :param report: Specifies which data should be reported for diagnosis purposes.
        :type report: str
        :param section_type: Specifies which of the section types is reported in the route response.
        :type section_type: str or ~azure.maps.route.models.SectionType
        :param vehicle_axle_weight: Weight per axle of the vehicle in kg.
        :type vehicle_axle_weight: int
        :param vehicle_width: Width of the vehicle in meters.
        :type vehicle_width: float
        :param vehicle_height: Height of the vehicle in meters.
        :type vehicle_height: float
        :param vehicle_length: Length of the vehicle in meters.
        :type vehicle_length: float
        :param vehicle_max_speed: Maximum speed of the vehicle in km/hour.
        :type vehicle_max_speed: int
        :param vehicle_weight: Weight of the vehicle in kilograms.
        :type vehicle_weight: int
        :param vehicle_commercial: Vehicle is used for commercial purposes and thus may not be allowed
         to drive  on some roads.
        :type vehicle_commercial: bool
        :param windingness: Level of turns for thrilling route.
        :type windingness: str or ~azure.maps.route.models.WindingnessLevel
        :param hilliness: Degree of hilliness for thrilling route.
        :type hilliness: str or ~azure.maps.route.models.HillinessDegree
        :param travel_mode: The mode of travel for the requested route.
        :type travel_mode: str or ~azure.maps.route.models.TravelMode
        :param avoid: Specifies something that the route calculation should try to avoid when
         determining the route.
        :type avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :param traffic: Input values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing. Note that although the current traffic
         data is ignored during routing, the effect of historic traffic on effective road speeds is still
         incorporated.
        :type traffic: bool
        :param route_type: The type of route requested.
        :type route_type: str or ~azure.maps.route.models.RouteType
        :param vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads.
        :type vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :param vehicle_engine_type: Engine type of the vehicle.
        :type vehicle_engine_type: str or ~azure.maps.route.models.VehicleEngineType
        :param constant_speed_consumption_in_liters_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :type constant_speed_consumption_in_liters_per_hundred_km: float
        :param current_fuel_in_liters: Specifies the current supply of fuel in liters.
        :type current_fuel_in_liters: float
        :param auxiliary_power_in_liters_per_hour: Specifies the amount of fuel consumed for sustaining
         auxiliary systems of the vehicle, in liters per hour.
        :type auxiliary_power_in_liters_per_hour: float
        :param fuel_energy_density_in_m_joules_per_liter: Specifies the amount of chemical energy
         stored in one liter of fuel in megajoules (MJ).
        :type fuel_energy_density_in_m_joules_per_liter: float
        :param acceleration_efficiency: Specifies the efficiency of converting chemical energy stored
         in fuel to kinetic energy when the vehicle accelerates.
        :type acceleration_efficiency: float
        :param deceleration_efficiency: Specifies the efficiency of converting kinetic energy to saved
         (not consumed) fuel when the vehicle decelerates.
        :type deceleration_efficiency: float
        :param uphill_efficiency: Specifies the efficiency of converting chemical energy stored in fuel
         to potential energy when the vehicle gains elevation.
        :type uphill_efficiency: float
        :param downhill_efficiency: Specifies the efficiency of converting potential energy to saved
         (not consumed) fuel when the vehicle loses elevation.
        :type downhill_efficiency: float
        :param constant_speed_consumption_in_kwh_per_hundred_km: Specifies the speed-dependent component
         of consumption.
        :type constant_speed_consumption_in_kwh_per_hundred_km: str
        :param current_charge_ink_wh: Specifies the current electric energy supply in kilowatt hours
         (kWh).
        :type current_charge_ink_wh: str
        :param max_charge_ink_wh: Specifies the maximum electric energy supply in kilowatt hours (kWh)
         that may be stored in the vehicle's battery.
        :type max_charge_ink_wh: str
        :keyword str auxiliary_power_in_kw: Specifies the amount of power consumed for sustaining auxiliary
         systems, in kilowatts (kW).
        :return: RouteDirectionsResponse
        :rtype: ~azure.maps.route.models.RouteDirectionsResponse
        :raises: ~azure.core.exceptions.HttpResponseError

        To send the *route directions* queries you will use a ``POST`` request where the request body
        will contain the ``batchItems`` array in ``json`` format and the ``Content-Type`` header will
        be set to ``application/json``. Here's a sample request body containing 3 *route directions*
        queries:
                   {
               "batchItems": [
                   { "query":
        "?query=47.620659,-122.348934:47.610101,-122.342015&travelMode=bicycle&routeType=eco&traffic=false"
        },
                   { "query":
        "?query=40.759856,-73.985108:40.771136,-73.973506&travelMode=pedestrian&routeType=shortest" },
                   { "query": "?query=48.923159,-122.557362:32.621279,-116.840362" }
               ]
           }
        """
        return self._route_client.post_route_directions_batch_sync(
            post_route_directions_batch_request_body=route_points_batch,
            **kwargs
        )


    @distributed_trace
    def begin_request_route_directions_batch(
        self,
        requests, #type: List[RouteDirectionsRequest]
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["RouteDirectionsBatchResponse"]
        """Sends batches of route direction queries.
        The method returns a poller for retrieving the result later.
        """
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
        batch_id, #type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["RouteDirectionsBatchResponse"]
        """Retrieves the result of a previous route direction batch request.
        The method returns a poller for retrieving the result.

        :param batch_id: Batch id for querying the operation.
        :type batch_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between
         two polls for LRO operations if no Retry-After header is present.
        :return: An instance of LROPoller that returns RouteDirectionsBatchResponse
        :rtype: ~azure.core.polling.LROPoller[~azure.maps.route.models.RouteDirectionsBatchResponse]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        poller = self._route_client.begin_get_route_directions_batch(
            format=batch_id,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace
    def request_route_matrix(
        self,
        route_matrix_query, #type: RouteMatrixQuery
        **kwargs  # type: Any
    ):
        # type: (...) -> "RouteMatrixResponse"
        """
        Calculates a matrix of route summaries for a set of routes defined by origin and destination locations.
        The method return the result directly.

        The maximum size of a matrix for this method is 100.
        """
        return self._route_client.post_route_matrix_sync(
            query=route_matrix_query,
            **kwargs
        )


    @distributed_trace
    def begin_request_route_matrix(
        self,
        route_matrix_query, #type: RouteMatrixQuery
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["RouteMatrixResponse"]
        """
        Calculates a matrix of route summaries for a set of routes defined by origin and destination locations.
        The method returns a poller for retrieving the result later.

        The maximum size of a matrix for this method is 700.
        """

        poller = self._route_client.begin_post_route_matrix(
            requests=route_matrix_query,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller


    @distributed_trace
    def begin_get_route_matrix_result(
        self,
        matrix_id, #type: str
        **kwargs  # type: Any
    ):
        # type: (...) -> LROPoller["RouteMatrixResponse"]
        """If the Matrix Route request was accepted successfully, the Location header in the response
        contains the URL to download the results of the request.

        Retrieves the result of a previous route matrix request.
        The method returns a poller for retrieving the result.

        :param matrix_id: Matrix id received after the Matrix Route request was accepted successfully.
        :type matrix_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling.
        :paramtype polling: bool or ~azure.core.polling.PollingMethod
        :keyword int polling_interval: Default waiting time between two polls for
         LRO operations if no Retry-After header is present.
        :return: An instance of LROPoller that returns RouteMatrixResponse
        :rtype: ~azure.core.polling.LROPoller[~azure.maps.route.models.RouteMatrixResponse]
        :raises ~azure.core.exceptions.HttpResponseError:
        """

        poller = self._route_client.begin_get_route_matrix(
            format=matrix_id,
            **kwargs
        )
        result_properties = poller.result().additional_properties
        if 'status' in result_properties and result_properties['status'].lower() == 'failed':
            raise HttpResponseError(message=result_properties['error']['message'])

        return poller
