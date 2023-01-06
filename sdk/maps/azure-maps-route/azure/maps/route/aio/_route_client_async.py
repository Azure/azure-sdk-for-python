# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-import,ungrouped-imports, R0904, C0302, W0212
from typing import Any, List, Union, Tuple, overload
from azure.core.polling import AsyncLROPoller
from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials import AzureKeyCredential
from azure.core.credentials_async import AsyncTokenCredential
from ._base_client_async import AsyncMapsRouteClientBase

from ..models import (
    RouteDirectionsBatchResult,
    RouteDirections,
    RouteRangeResult,
    RouteMatrixResult,
    RouteMatrixQuery,
    LatLon
)

from .._generated.models import (
    ResponseFormat
)

def get_batch_id_from_poller(polling_method):
    if hasattr(polling_method, "_operation"):
        operation=polling_method._operation
        return operation._location_url.split('/')[-1].split('?')[0]
    return None

# By default, use the latest supported API version
class MapsRouteClient(AsyncMapsRouteClientBase):
    """Azure Maps Route REST APIs.
    :param credential:
        Credential needed for the client to connect to Azure.
    :type credential:
        ~azure.core.credentials.TokenCredential or ~azure.core.credentials.AzureKeyCredential
    :keyword str base_url:
        Supported Maps Services or Language resource base_url
        (protocol and hostname, for example: 'https://us.atlas.microsoft.com').
    :keyword str client_id:
        Specifies which account is intended for usage with the Azure AD security model.
        It represents a unique ID for the Azure Maps account.
    :keyword api_version:
        The API version of the service to use for requests. It defaults to the latest service version.
        Setting to an older version may result in reduced feature compatibility.
    :paramtype api_version: str
    """

    def __init__(
        self,
        credential: Union[AzureKeyCredential, AsyncTokenCredential],
        **kwargs: Any
    )-> None:

        super().__init__(
            credential=credential, **kwargs
        )

    # cSpell:disable
    @distributed_trace_async
    async def get_route_directions(
        self,
        route_points: Union[List[LatLon], List[Tuple]],
        **kwargs: Any
    ) -> RouteDirections:
        """
        Returns a route between an origin and a destination, passing through waypoints if they are
        specified. The route will take into account factors such as current traffic and the typical
        road speeds on the requested day of the week and time of day.

        Information returned includes the distance, estimated travel time, and a representation of the
        route geometry. Additional routing information such as optimized waypoint order or turn by turn
        instructions is also available, depending on the options selected.

        :param route_points: The Coordinate from which the range calculation should start, coordinates as (lat, lon)
        :type route_points: List[LatLon] or List[Tuple]
        :keyword supporting_points: A GeoJSON Geometry collection representing sequence of coordinates
         used as input for route reconstruction and for calculating zero or more alternative routes to
         this reference route.
        :paramtype supporting_points: ~azure.maps.route.models.GeoJsonGeometryCollection
        :keyword avoid_vignette: This is a list of 3-character, ISO 3166-1, alpha-3 country codes of
         countries in which all toll roads with vignettes are to be avoided, e.g. "AUS,CHE". Toll roads
         with vignettes in countries not in the list are unaffected.
        :paramtype avoid_vignette: list[str]
        :keyword allow_vignette: This is a list of 3-character, ISO 3166-1, alpha-3 country codes of
         countries in which toll roads with vignettes are allowed, e.g. "AUS,CHE". Specifying
         **allowVignette** with some countries X is equivalent to specifying **avoidVignette** with all
         countries but X. Specifying **allowVignette** with an empty list is the same as avoiding all
         toll roads with vignettes.
        :paramtype allow_vignette: list[str]
        :keyword avoid_areas: A GeoJSON MultiPolygon representing list of areas to avoid. Only rectangle
         polygons are supported. The maximum size of a rectangle is about 160x160 km. Maximum number of
         avoided areas is **10**.
        :paramtype avoid_areas: ~azure.maps.route.models.GeoJsonMultiPolygon
        :keyword max_alternatives: Number of desired alternative routes to be calculated. Default: 0,
         minimum: 0 and maximum: 5. Default value is None.
        :paramtype max_alternatives: int
        :keyword alternative_type: Controls the optimality, with respect to the given planning
         criteria, of the calculated alternatives compared to the reference route. Known values are:
         "anyRoute" and "betterRoute". Default value is None.
        :paramtype alternative_type: str or ~azure.maps.route.models.AlternativeRouteType
        :keyword min_deviation_distance: All alternative routes returned will follow the reference
         route (see section POST Requests) from the origin point of the calculateRoute request for at
         least this number of meters. Can only be used when reconstructing a route. The
         minDeviationDistance parameter cannot be used in conjunction with arriveAt. Default value is
         None.
        :paramtype min_deviation_distance: int
        :keyword min_deviation_time: All alternative routes returned will follow the reference route
         (see section POST Requests) from the origin point of the calculateRoute request for at least
         this number of seconds. Can only be used when reconstructing a route. The minDeviationTime
         parameter cannot be used in conjunction with arriveAt. Default value is 0.
        :paramtype min_deviation_time: int
        :keyword instructions_type: If specified, guidance instructions will be returned. Note that the
         instructionsType parameter cannot be used in conjunction with routeRepresentation=none. Known
         values are: "coded", "text", and "tagged". Default value is None.
        :paramtype instructions_type: str or ~azure.maps.route.models.RouteInstructionsType
        :keyword language: The language parameter determines the language of the guidance messages. It
         does not affect proper nouns (the names of streets, plazas, etc.) It has no effect when
         instructionsType=coded. Allowed values are (a subset of) the IETF language tags described.
         Default value is None.
        :paramtype language: str
        :keyword compute_best_waypoint_order: Re-order the route waypoints using a fast heuristic
         algorithm to reduce the route length. Yields best results when used in conjunction with
         routeType *shortest*. Notice that origin and destination are excluded from the optimized
         waypoint indices. To include origin and destination in the response, please increase all the
         indices by 1 to account for the origin, and then add the destination as the final index.
         Possible values are true or false. True computes a better order if possible, but is not allowed
         to be used in conjunction with maxAlternatives value greater than 0 or in conjunction with
         circle waypoints. False will use the locations in the given order and not allowed to be used in
         conjunction with routeRepresentation *none*. Default value is None.
        :paramtype compute_best_waypoint_order: bool
        :keyword route_representation_for_best_order: Specifies the representation of the set of routes
         provided as response. This parameter value can only be used in conjunction with
         computeBestOrder=true. Known values are: "polyline", "summaryOnly", and "none". Default value
         is None.
        :paramtype route_representation_for_best_order: str or
         ~azure.maps.route.models.RouteRepresentationForBestOrder
        :keyword compute_travel_time: Specifies whether to return additional travel times using
         different types of traffic information (none, historic, live) as well as the default
         best-estimate travel time. Known values are: "none" and "all". Default value is None.
        :paramtype compute_travel_time: str or ~azure.maps.route.models.ComputeTravelTime
        :keyword vehicle_heading: The directional heading of the vehicle in degrees starting at true
         North and continuing in clockwise direction. North is 0 degrees, east is 90 degrees, south is
         180 degrees, west is 270 degrees. Possible values 0-359. Default value is None.
        :paramtype vehicle_heading: int
        :keyword report: Specifies which data should be reported for diagnosis purposes. The only
         possible value is *effectiveSettings*. Reports the effective parameters or data used when
         calling the API. In the case of defaulted parameters the default will be reflected where the
         parameter was not specified by the caller. "effectiveSettings" Default value is None.
        :paramtype report: str or ~azure.maps.route.models.Report
        :keyword filter_section_type: Specifies which of the section types is reported in the route
         response. :code:`<br>`:code:`<br>`For example if sectionType = pedestrian the sections which
         are suited for pedestrians only are returned. Multiple types can be used. The default
         sectionType refers to the travelMode input. By default travelMode is set to car. Known values
         are: "carTrain", "country", "ferry", "motorway", "pedestrian", "tollRoad", "tollVignette",
         "traffic", "travelMode", "tunnel", "carpool", and "urban". Default value is None.
        :paramtype filter_section_type: str or ~azure.maps.route.models.SectionType
        :keyword arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime. When a time zone offset is not specified it will be assumed to be that of the
         destination point. The arriveAt value must be in the future. The arriveAt parameter cannot be
         used in conjunction with departAt, minDeviationDistance or minDeviationTime. Default value is
         None.
        :paramtype arrive_at: ~datetime.datetime
        :keyword depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00). Default value is None.
        :paramtype depart_at: ~datetime.datetime
        :keyword vehicle_axle_weight: Weight per axle of the vehicle in kg. A value of 0 means that
         weight restrictions per axle are not considered. Default value is 0.
        :paramtype vehicle_axle_weight: int
        :keyword vehicle_length: Length of the vehicle in meters. A value of 0 means that length
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_length: float
        :keyword vehicle_height: Height of the vehicle in meters. A value of 0 means that height
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_height: float
        :keyword vehicle_width: Width of the vehicle in meters. A value of 0 means that width
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_width: float
        :keyword vehicle_max_speed: Maximum speed of the vehicle in km/hour. The max speed in the
         vehicle profile is used to check whether a vehicle is allowed on motorways.
        :paramtype vehicle_max_speed: int
        :keyword vehicle_weight: Weight of the vehicle in kilograms.
        :paramtype vehicle_weight: int
        :keyword is_commercial_vehicle: Whether the vehicle is used for commercial purposes. Commercial
         vehicles may not be allowed to drive on some roads. Default value is False.
        :paramtype is_commercial_vehicle: bool
        :keyword windingness: Level of turns for thrilling route. This parameter can only be used in
         conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and "high".
         Default value is None.
        :paramtype windingness: str or ~azure.maps.route.models.WindingnessLevel
        :keyword incline_level: Degree of hilliness for thrilling route. This parameter can only be
         used in conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and
         "high". Default value is None.
        :paramtype incline_level: str or ~azure.maps.route.models.InclineLevel
        :keyword travel_mode: The mode of travel for the requested route. If not defined, default is
         'car'. Note that the requested travelMode may not be available for the entire route. Where the
         requested travelMode is not available for a particular section, the travelMode element of the
         response for that section will be "other". Note that travel modes bus, motorcycle, taxi and van
         are BETA functionality. Full restriction data is not available in all areas. In
         **calculateReachableRange** requests, the values bicycle and pedestrian must not be used. Known
         values are: "car", "truck", "taxi", "bus", "van", "motorcycle", "bicycle", and "pedestrian".
         Default value is None.
        :paramtype travel_mode: str or ~azure.maps.route.models.TravelMode
        :keyword avoid: Specifies something that the route calculation should try to avoid when
         determining the route. Can be specified multiple times in one request, for example,
         '&avoid=motorways&avoid=tollRoads&avoid=ferries'. In calculateReachableRange requests, the
         value alreadyUsedRoads must not be used. Default value is None.
        :paramtype avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :keyword use_traffic_data: Possible values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing.
        :paramtype use_traffic_data: bool
        :keyword route_type: The type of route requested. Known values are: "fastest", "shortest",
         "eco", and "thrilling". Default value is None.
        :paramtype route_type: str or ~azure.maps.route.models.RouteType
        :keyword vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads. Available vehicleLoadType values are US Hazmat classes 1 through 9,
         plus generic classifications for use in other countries. Values beginning with USHazmat are for
         US routing while otherHazmat should be used for all other countries. vehicleLoadType can be
         specified multiple times. This parameter is currently only considered for travelMode=truck.
         Known values are: "USHazmatClass1", "USHazmatClass2", "USHazmatClass3", "USHazmatClass4",
         "USHazmatClass5", "USHazmatClass6", "USHazmatClass7", "USHazmatClass8", "USHazmatClass9",
         "otherHazmatExplosive", "otherHazmatGeneral", and "otherHazmatHarmfulToWater". Default value is
         None.
        :paramtype vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :keyword vehicle_engine_type: Engine type of the vehicle. When a detailed Consumption Model is
         specified, it must be consistent with the value of **vehicleEngineType**. Known values are:
         "combustion" and "electric". Default value is None.
        :paramtype vehicle_engine_type: str or ~azure.maps.route.models.VehicleEngineType
        :keyword constant_speed_consumption_in_liters_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :paramtype constant_speed_consumption_in_liters_per_hundred_km: str
        :keyword current_fuel_in_liters: Specifies the current supply of fuel in liters.
        :paramtype current_fuel_in_liters: float
        :keyword auxiliary_power_in_liters_per_hour: Specifies the amount of fuel consumed for
         sustaining auxiliary systems of the vehicle, in liters per hour.
        :paramtype auxiliary_power_in_liters_per_hour: float
        :keyword fuel_energy_density_in_megajoules_per_liter: Specifies the amount of chemical energy
         stored in one liter of fuel in megajoules (MJ).
        :paramtype fuel_energy_density_in_megajoules_per_liter: float
        :keyword acceleration_efficiency: Specifies the efficiency of converting chemical energy stored
         in fuel to kinetic energy when the vehicle accelerates *(i.e.
         KineticEnergyGained/ChemicalEnergyConsumed). ChemicalEnergyConsumed* is obtained by converting
         consumed fuel to chemical energy using **fuelEnergyDensityInMJoulesPerLiter**.
        :paramtype acceleration_efficiency: float
        :keyword deceleration_efficiency: Specifies the efficiency of converting kinetic energy to
         saved (not consumed) fuel when the vehicle decelerates *(i.e.
         ChemicalEnergySaved/KineticEnergyLost). ChemicalEnergySaved* is obtained by converting saved
         (not consumed) fuel to energy using **fuelEnergyDensityInMJoulesPerLiter**.
        :paramtype deceleration_efficiency: float
        :keyword uphill_efficiency: Specifies the efficiency of converting chemical energy stored in
         fuel to potential energy when the vehicle gains elevation *(i.e.
         PotentialEnergyGained/ChemicalEnergyConsumed). ChemicalEnergyConsumed* is obtained by
         converting consumed fuel to chemical energy using **fuelEnergyDensityInMJoulesPerLiter**.
        :paramtype uphill_efficiency: float
        :keyword downhill_efficiency: Specifies the efficiency of converting potential energy to saved
         (not consumed) fuel when the vehicle loses elevation *(i.e.
         ChemicalEnergySaved/PotentialEnergyLost). ChemicalEnergySaved* is obtained by converting saved
         (not consumed) fuel to energy using **fuelEnergyDensityInMJoulesPerLiter**.
        :paramtype downhill_efficiency: float
        :keyword constant_speed_consumption_in_kw_h_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :paramtype constant_speed_consumption_in_kw_h_per_hundred_km: str
        :keyword current_charge_in_kw_h: Specifies the current electric energy supply in kilowatt hours
         (kWh).
        :paramtype current_charge_in_kw_h: float
        :keyword max_charge_in_kw_h: Specifies the maximum electric energy supply in kilowatt hours
         (kWh) that may be stored in the vehicle's battery.
        :paramtype max_charge_in_kw_h: float
        :keyword auxiliary_power_in_kw: Specifies the amount of power consumed for sustaining auxiliary
         systems, in kilowatts (kW).
        :paramtype auxiliary_power_in_kw: float
        :return: RouteDirections
        :rtype: ~azure.maps.route.models.RouteDirections
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        query_items=""
        route_directions_body={}
        if route_points:
            query_items = ":".join([(str(route_point[0])+","+str(route_point[1])) for route_point in route_points])

        supporting_points = kwargs.pop('supporting_points', None)
        avoid_vignette = kwargs.pop('avoid_vignette', None)
        allow_vignette = kwargs.pop('allow_vignette', None)
        avoid_areas = kwargs.pop('avoid_areas', None)
        if supporting_points or avoid_vignette or allow_vignette or avoid_areas is not None:
            route_directions_body['supporting_points'] = supporting_points
            route_directions_body['avoid_vignette'] = avoid_vignette
            route_directions_body['allow_vignette'] = allow_vignette
            route_directions_body['avoid_areas'] = avoid_areas

        if route_directions_body:
            # import pdb; pdb.set_trace()
            return await self._route_client.get_route_directions_with_additional_parameters(
                format=ResponseFormat.JSON,
                route_direction_parameters=route_directions_body,
                route_points=query_items,
                **kwargs
            )
        return await self._route_client.get_route_directions(
            format=ResponseFormat.JSON,
            route_points=query_items,
            **kwargs
        )

    # cSpell:disable
    @distributed_trace_async
    async def get_route_range(
        self,
        coordinates: Union[LatLon, Tuple],
        **kwargs: Any
    ) -> RouteRangeResult:

        """**Route Range (Isochrone) API**

        This service will calculate a set of locations that can be reached from the origin point based
        on fuel, energy,  time or distance budget that is specified. A polygon boundary (or Isochrone)
        is returned in a counterclockwise  orientation as well as the precise polygon center which was
        the result of the origin point.

        :param coordinates: The Coordinate from which the range calculation should start, coordinates as (lat, lon)
        :type coordinates: LatLon or Tuple
        :keyword fuel_budget_in_liters: Fuel budget in liters that determines maximal range which can
         be travelled using the specified Combustion Consumption Model.:code:`<br>` When
         fuelBudgetInLiters is used, it is mandatory to specify a detailed  Combustion Consumption
         Model.:code:`<br>` Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec,
         or distanceBudgetInMeters) must be used. Default value is None.
        :paramtype fuel_budget_in_liters: float
        :keyword energy_budget_in_kw_h: Electric energy budget in kilowatt hours (kWh) that determines
         maximal range which can be travelled using the specified Electric Consumption
         Model.:code:`<br>` When energyBudgetInkWh is used, it is mandatory to specify a detailed
         Electric Consumption Model.:code:`<br>` Exactly one budget (fuelBudgetInLiters,
         energyBudgetInkWh, timeBudgetInSec, or distanceBudgetInMeters) must be used. Default value is
         None.
        :paramtype energy_budget_in_kw_h: float
        :keyword time_budget_in_sec: Time budget in seconds that determines maximal range which can be
         travelled using driving time. The Consumption Model will only affect the range when routeType
         is eco.:code:`<br>` Exactly one budget (fuelBudgetInLiters, energyBudgetInkWh, timeBudgetInSec,
         or distanceBudgetInMeters) must be used. Default value is None.
        :paramtype time_budget_in_sec: float
        :keyword distance_budget_in_meters: Distance budget in meters that determines maximal range
         which can be travelled using driving distance.  The Consumption Model will only affect the
         range when routeType is eco.:code:`<br>` Exactly one budget (fuelBudgetInLiters,
         energyBudgetInkWh, timeBudgetInSec, or distanceBudgetInMeters) must be used. Default value is
         None.
        :paramtype distance_budget_in_meters: float
        :keyword depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00). Default value is None.
        :paramtype depart_at: ~datetime.datetime
        :keyword route_type: The type of route requested. Known values are: "fastest", "shortest",
         "eco", and "thrilling". Default value is None.
        :paramtype route_type: str or ~azure.maps.route.models.RouteType
        :keyword use_traffic_data: Possible values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing.
        :paramtype use_traffic_data: bool
        :keyword avoid: Specifies something that the route calculation should try to avoid when
         determining the route. Can be specified multiple times in one request, for example,
         '&avoid=motorways&avoid=tollRoads&avoid=ferries'. In calculateReachableRange requests, the
         value alreadyUsedRoads must not be used. Default value is None.
        :paramtype avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :keyword travel_mode: The mode of travel for the requested route. If not defined, default is
         'car'. Note that the requested travelMode may not be available for the entire route. Where the
         requested travelMode is not available for a particular section, the travelMode element of the
         response for that section will be "other". Note that travel modes bus, motorcycle, taxi and van
         are BETA functionality. Full restriction data is not available in all areas. In
         **calculateReachableRange** requests, the values bicycle and pedestrian must not be used. Known
         values are: "car", "truck", "taxi", "bus", "van", "motorcycle", "bicycle", and "pedestrian".
         Default value is None.
        :paramtype travel_mode: str or ~azure.maps.route.models.TravelMode
        :keyword incline_level: Degree of hilliness for thrilling route. This parameter can only be
         used in conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and
         "high". Default value is None.
        :paramtype incline_level: str or ~azure.maps.route.models.InclineLevel
        :keyword windingness: Level of turns for thrilling route. This parameter can only be used in
         conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and "high".
         Default value is None.
        :paramtype windingness: str or ~azure.maps.route.models.WindingnessLevel
        :keyword vehicle_axle_weight: Weight per axle of the vehicle in kg. A value of 0 means that
         weight restrictions per axle are not considered. Default value is 0.
        :paramtype vehicle_axle_weight: int
        :keyword vehicle_width: Width of the vehicle in meters. A value of 0 means that width
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_width: float
        :keyword vehicle_height: Height of the vehicle in meters. A value of 0 means that height
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_height: float
        :keyword vehicle_length: Length of the vehicle in meters. A value of 0 means that length
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_length: float
        :keyword vehicle_max_speed: Maximum speed of the vehicle in km/hour. The max speed in the
         vehicle profile is used to check whether a vehicle is allowed on motorways.
         Default value is 0.
        :paramtype vehicle_max_speed: int
        :keyword vehicle_weight: Weight of the vehicle in kilograms. Default
         value is 0.
        :paramtype vehicle_weight: int
        :keyword is_commercial_vehicle: Whether the vehicle is used for commercial purposes. Commercial
         vehicles may not be allowed to drive on some roads. Default value is False.
        :paramtype is_commercial_vehicle: bool
        :keyword vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads. Available vehicleLoadType values are US Hazmat classes 1 through 9,
         plus generic classifications for use in other countries. Values beginning with USHazmat are for
         US routing while otherHazmat should be used for all other countries. vehicleLoadType can be
         specified multiple times. This parameter is currently only considered for travelMode=truck.
         Known values are: "USHazmatClass1", "USHazmatClass2", "USHazmatClass3", "USHazmatClass4",
         "USHazmatClass5", "USHazmatClass6", "USHazmatClass7", "USHazmatClass8", "USHazmatClass9",
         "otherHazmatExplosive", "otherHazmatGeneral", and "otherHazmatHarmfulToWater". Default value is
         None.
        :paramtype vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :keyword vehicle_engine_type: Engine type of the vehicle. When a detailed Consumption Model is
         specified, it must be consistent with the value of **vehicleEngineType**. Known values are:
         "combustion" and "electric". Default value is None.
        :paramtype vehicle_engine_type: str or ~azure.maps.route.models.VehicleEngineType
        :keyword constant_speed_consumption_in_liters_per_hundred_km: Specifies the speed-dependent
         component of consumption.
        :paramtype constant_speed_consumption_in_liters_per_hundred_km: str
        :keyword current_fuel_in_liters: Specifies the current supply of fuel in liters.
        :paramtype current_fuel_in_liters: float
        :keyword auxiliary_power_in_liters_per_hour: Specifies the amount of fuel consumed for
         sustaining auxiliary systems of the vehicle, in liters per hour.
        :paramtype auxiliary_power_in_liters_per_hour: float
        :keyword fuel_energy_density_in_megajoules_per_liter: Specifies the amount of chemical energy
         stored in one liter of fuel in megajoules (MJ). It is used in conjunction with the
         ***Efficiency** parameters for conversions between saved or consumed energy and fuel.
        :paramtype fuel_energy_density_in_megajoules_per_liter: float
        :keyword acceleration_efficiency: Specifies the efficiency of converting chemical energy stored
         in fuel to kinetic energy when the vehicle accelerates *(i.e.
         KineticEnergyGained/ChemicalEnergyConsumed). ChemicalEnergyConsumed* is obtained by converting
         consumed fuel to chemical energy using **fuelEnergyDensityInMJoulesPerLiter**.
        :paramtype acceleration_efficiency: float
        :keyword deceleration_efficiency: Specifies the efficiency of converting kinetic energy to
         saved (not consumed) fuel when the vehicle decelerates *(i.e.
         ChemicalEnergySaved/KineticEnergyLost). ChemicalEnergySaved* is obtained by converting saved
         (not consumed) fuel to energy using **fuelEnergyDensityInMJoulesPerLiter**. Default
         value is None.
        :paramtype deceleration_efficiency: float
        :keyword uphill_efficiency: Specifies the efficiency of converting chemical energy stored in
         fuel to potential energy when the vehicle gains elevation *(i.e.
         PotentialEnergyGained/ChemicalEnergyConsumed). ChemicalEnergyConsumed* is obtained by
         converting consumed fuel to chemical energy using **fuelEnergyDensityInMJoulesPerLiter**.
         Default value is None.
        :paramtype uphill_efficiency: float
        :keyword downhill_efficiency: Specifies the efficiency of converting potential energy to saved
         (not consumed) fuel when the vehicle loses elevation *(i.e.
         ChemicalEnergySaved/PotentialEnergyLost). ChemicalEnergySaved* is obtained by converting saved
         (not consumed) fuel to energy using **fuelEnergyDensityInMJoulesPerLiter**. Default
         value is None.
        :paramtype downhill_efficiency: float
        :keyword constant_speed_consumption_in_kw_h_per_hundred_km: Specifies the speed-dependent
         component of consumption. Default value is None.
        :paramtype constant_speed_consumption_in_kw_h_per_hundred_km: str
        :keyword current_charge_in_kw_h: Specifies the current electric energy supply in kilowatt hours
         (kWh). Default value is None.
        :paramtype current_charge_in_kw_h: float
        :keyword max_charge_in_kw_h: Specifies the maximum electric energy supply in kilowatt hours
         (kWh) that may be stored in the vehicle's battery. Default value is None.
        :paramtype max_charge_in_kw_h: float
        :keyword auxiliary_power_in_kw: Specifies the amount of power consumed for sustaining auxiliary
         systems, in kilowatts (kW). Default value is None.
        :paramtype auxiliary_power_in_kw: float
        :return: RouteRangeResult
        :rtype: ~azure.maps.route.models.RouteRangeResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        query = [coordinates[0], coordinates[1]]

        return await self._route_client.get_route_range(
            format=ResponseFormat.JSON,
            query=query,
            **kwargs
        )


    @distributed_trace_async
    async def get_route_directions_batch_sync(
        self,
        queries: List[str],
        **kwargs: Any
    ) -> RouteDirectionsBatchResult:

        """Sends batches of route directions requests.
        The method return the result directly.

        :param queries: The list of route directions queries/requests to
         process. The list can contain  a max of 700 queries for async and 100 queries for sync version
         and must contain at least 1 query. Required.
        :type queries: List[str]
        :return: RouteDirectionsBatchResult
        :rtype: RouteDirectionsBatchResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        batch_items = [{"query": f"?query={query}"} for query
                       in queries] if queries else []
        result = await self._route_client.request_route_directions_batch_sync(
            format=ResponseFormat.JSON,
            route_directions_batch_queries={"batch_items": batch_items},
            **kwargs
        )
        return RouteDirectionsBatchResult(summary=result.batch_summary, items=result.batch_items)

    @overload
    def begin_get_route_directions_batch(
        self,
        batch_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[RouteDirectionsBatchResult]:
        pass

    @overload
    def begin_get_route_directions_batch(
        self,
        queries: List[str],
        **kwargs: Any
    ) -> AsyncLROPoller[RouteDirectionsBatchResult]:
        pass

    @distributed_trace_async
    async def begin_get_route_directions_batch(
        self,
        **kwargs: Any
    ) -> AsyncLROPoller[RouteDirectionsBatchResult]:

        """Sends batches of route direction queries.
        The method returns a poller for retrieving the result later.

        :keyword queries: The list of route directions queries/requests to
         process. The list can contain a max of 700 queries for async and 100 queries for sync version
         and must contain at least 1 query. Required.
        :paramtype queries: List[str]
        :keyword batch_id: Batch id for querying the operation. Required.
        :paramtype batch_id: str
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns RouteDirectionsBatchResult
        :rtype: ~azure.core.polling.AsyncLROPoller[RouteDirectionsBatchResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        queries=kwargs.pop('queries', None)
        batch_id=kwargs.pop('batch_id', None)

        if batch_id:
            poller = await self._route_client.begin_get_route_directions_batch(
                format=ResponseFormat.JSON,
                batch_id=batch_id,
                **kwargs
            )
            return poller

        batch_items = [{"query": f"?query={query}"} for query
                       in queries] if queries else []
        batch_poller = await self._route_client.begin_request_route_directions_batch(
            format=ResponseFormat.JSON,
            route_directions_batch_queries={"batch_items": batch_items},
            **kwargs
        )
        batch_poller.batch_id = get_batch_id_from_poller(batch_poller.polling_method())
        return batch_poller

    @distributed_trace_async
    async def get_route_matrix(
        self,
        query: RouteMatrixQuery,
        **kwargs: Any
    ) -> RouteMatrixResult:

        """
        Calculates a matrix of route summaries for a set of routes defined by origin and destination locations.
        The method return the result directly.

        The maximum size of a matrix for this method is 100
         (the number of origins multiplied by the number of destinations)

        :param query: The matrix of origin and destination coordinates to compute the
         route distance, travel time and other summary for each cell of the matrix based on the input
         parameters. The minimum and the maximum cell count supported are 1 and **700** for async and
         **100** for sync respectively. For example, it can be 35 origins and 20 destinations or 25
         origins and 25 destinations for async API. Is either a model type or a IO type. Required.
        :type query: ~azure.maps.route.models.RouteMatrixQuery or IO
        :keyword wait_for_results: Boolean to indicate whether to execute the request synchronously. If
         set to true, user will get a 200 response if the request is finished under 120 seconds.
         Otherwise, user will get a 202 response right away. Please refer to the API description for
         more details on 202 response. **Supported only for async request**. Default value is None.
        :paramtype wait_for_results: bool
        :keyword compute_travel_time: Specifies whether to return additional travel times using
         different types of traffic information (none, historic, live) as well as the default
         best-estimate travel time. Known values are: "none" and "all". Default value is None.
        :paramtype compute_travel_time: str or ~azure.maps.route.models.ComputeTravelTime
        :keyword filter_section_type: Specifies which of the section types is reported in the route
         response. :code:`<br>`:code:`<br>`For example if sectionType = pedestrian the sections which
         are suited for pedestrians only are returned. Multiple types can be used. The default
         sectionType refers to the travelMode input. By default travelMode is set to car. Known values
         are: "carTrain", "country", "ferry", "motorway", "pedestrian", "tollRoad", "tollVignette",
         "traffic", "travelMode", "tunnel", "carpool", and "urban". Default value is None.
        :paramtype filter_section_type: str or ~azure.maps.route.models.SectionType
        :keyword arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime. When a time zone offset is not specified it will be assumed to be that of the
         destination point. The arriveAt value must be in the future. The arriveAt parameter cannot be
         used in conjunction with departAt, minDeviationDistance or minDeviationTime. Default value is
         None.
        :paramtype arrive_at: ~datetime.datetime
        :keyword depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00). Default value is None.
        :paramtype depart_at: ~datetime.datetime
        :keyword vehicle_axle_weight: Weight per axle of the vehicle in kg. A value of 0 means that
         weight restrictions per axle are not considered. Default value is 0.
        :paramtype vehicle_axle_weight: int
        :keyword vehicle_length: Length of the vehicle in meters. A value of 0 means that length
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_length: float
        :keyword vehicle_height: Height of the vehicle in meters. A value of 0 means that height
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_height: float
        :keyword vehicle_width: Width of the vehicle in meters. A value of 0 means that width
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_width: float
        :keyword vehicle_max_speed: Maximum speed of the vehicle in km/hour. Default value is 0.
        :paramtype vehicle_max_speed: int
        :keyword vehicle_weight: Weight of the vehicle in kilograms. Default value is 0.
        :paramtype vehicle_weight: int
        :keyword windingness: Level of turns for thrilling route. This parameter can only be used in
         conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and "high".
         Default value is None.
        :paramtype windingness: str or ~azure.maps.route.models.WindingnessLevel
        :keyword incline_level: Degree of hilliness for thrilling route. This parameter can only be
         used in conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and
         "high". Default value is None.
        :paramtype incline_level: str or ~azure.maps.route.models.InclineLevel
        :keyword travel_mode: The mode of travel for the requested route. If not defined, default is
         'car'. Note that the requested travelMode may not be available for the entire route. Where the
         requested travelMode is not available for a particular section, the travelMode element of the
         response for that section will be "other". Note that travel modes bus, motorcycle, taxi and van
         are BETA functionality. Full restriction data is not available in all areas. In
         **calculateReachableRange** requests, the values bicycle and pedestrian must not be used. Known
         values are: "car", "truck", "taxi", "bus", "van", "motorcycle", "bicycle", and "pedestrian".
         Default value is None.
        :paramtype travel_mode: str or ~azure.maps.route.models.TravelMode
        :keyword avoid: Specifies something that the route calculation should try to avoid when
         determining the route. Can be specified multiple times in one request, for example,
         '&avoid=motorways&avoid=tollRoads&avoid=ferries'. In calculateReachableRange requests, the
         value alreadyUsedRoads must not be used. Default value is None.
        :paramtype avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :keyword use_traffic_data: Possible values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing. Note that although the current traffic
         data is ignored during routing,
         the effect of historic traffic on effective road speeds is still
         incorporated. Default value is None.
        :paramtype use_traffic_data: bool
        :keyword route_type: The type of route requested. Known values are: "fastest", "shortest",
         "eco", and "thrilling". Default value is None.
        :paramtype route_type: str or ~azure.maps.route.models.RouteType
        :keyword vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads. Available vehicleLoadType values are US Hazmat classes 1 through 9,
         plus generic classifications for use in other countries. Values beginning with USHazmat are for
         US routing while otherHazmat should be used for all other countries. vehicleLoadType can be
         specified multiple times. This parameter is currently only considered for travelMode=truck.
         Known values are: "USHazmatClass1", "USHazmatClass2", "USHazmatClass3", "USHazmatClass4",
         "USHazmatClass5", "USHazmatClass6", "USHazmatClass7", "USHazmatClass8", "USHazmatClass9",
         "otherHazmatExplosive", "otherHazmatGeneral", and "otherHazmatHarmfulToWater". Default value is
         None.
        :paramtype vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :return: RouteMatrixResult
        :rtype: ~azure.maps.route.models.RouteMatrixResult
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        return await self._route_client.request_route_matrix_sync(
            format=ResponseFormat.JSON,
            route_matrix_query=query,
            **kwargs
        )

    @overload
    async def begin_get_route_matrix_batch(
        self,
        query: RouteMatrixQuery,
        **kwargs: Any
    ) -> AsyncLROPoller[RouteMatrixResult]:
        pass

    @overload
    async def begin_get_route_matrix_batch(
        self,
        matrix_id: str,
        **kwargs: Any
    ) -> AsyncLROPoller[RouteMatrixResult]:
        pass

    @distributed_trace_async
    async def begin_get_route_matrix_batch(
        self,
        **kwargs: Any
    ) -> AsyncLROPoller[RouteMatrixResult]:

        """
        Calculates a matrix of route summaries for a set of routes defined by origin and destination locations.
        The method returns a poller for retrieving the result later.

        The maximum size of a matrix for this method is 700
         (the number of origins multiplied by the number of destinations)

        :keyword query: The matrix of origin and destination coordinates to compute the
         route distance, travel time and other summary for each cell of the matrix based on the input
         parameters. The minimum and the maximum cell count supported are 1 and **700** for async and
         **100** for sync respectively. For example, it can be 35 origins and 20 destinations or 25
         origins and 25 destinations for async API. Required.
        :paramtype query: ~azure.maps.route.models.RouteMatrixQuery
        :keyword matrix_id: Matrix id received after the Matrix Route request was accepted successfully.
         Required.
        :paramtype matrix_id: str
        :keyword wait_for_results: Boolean to indicate whether to execute the request synchronously. If
         set to true, user will get a 200 response if the request is finished under 120 seconds.
         Otherwise, user will get a 202 response right away. Please refer to the API description for
         more details on 202 response. **Supported only for async request**. Default value is None.
        :paramtype wait_for_results: bool
        :keyword compute_travel_time: Specifies whether to return additional travel times using
         different types of traffic information (none, historic, live) as well as the default
         best-estimate travel time. Known values are: "none" and "all". Default value is None.
        :paramtype compute_travel_time: str or ~azure.maps.route.models.ComputeTravelTime
        :keyword filter_section_type: Specifies which of the section types is reported in the route
         response. :code:`<br>`:code:`<br>`For example if sectionType = pedestrian the sections which
         are suited for pedestrians only are returned. Multiple types can be used. The default
         sectionType refers to the travelMode input. By default travelMode is set to car. Known values
         are: "carTrain", "country", "ferry", "motorway", "pedestrian", "tollRoad", "tollVignette",
         "traffic", "travelMode", "tunnel", "carpool", and "urban". Default value is None.
        :paramtype filter_section_type: str or ~azure.maps.route.models.SectionType
        :keyword arrive_at: The date and time of arrival at the destination point. It must be specified
         as a dateTime. When a time zone offset is not specified it will be assumed to be that of the
         destination point. The arriveAt value must be in the future. The arriveAt parameter cannot be
         used in conjunction with departAt, minDeviationDistance or minDeviationTime. Default value is
         None.
        :paramtype arrive_at: ~datetime.datetime
        :keyword depart_at: The date and time of departure from the origin point. Departure times apart
         from now must be specified as a dateTime. When a time zone offset is not specified, it will be
         assumed to be that of the origin point. The departAt value must be in the future in the
         date-time format (1996-12-19T16:39:57-08:00). Default value is None.
        :paramtype depart_at: ~datetime.datetime
        :keyword vehicle_axle_weight: Weight per axle of the vehicle in kg. A value of 0 means that
         weight restrictions per axle are not considered. Default value is 0.
        :paramtype vehicle_axle_weight: int
        :keyword vehicle_length: Length of the vehicle in meters. A value of 0 means that length
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_length: float
        :keyword vehicle_height: Height of the vehicle in meters. A value of 0 means that height
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_height: float
        :keyword vehicle_width: Width of the vehicle in meters. A value of 0 means that width
         restrictions are not considered. Default value is 0.
        :paramtype vehicle_width: float
        :keyword vehicle_max_speed: Maximum speed of the vehicle in km/hour. Default value is 0.
        :paramtype vehicle_max_speed: int
        :keyword vehicle_weight: Weight of the vehicle in kilograms. Default value is 0.
        :paramtype vehicle_weight: int
        :keyword windingness: Level of turns for thrilling route. This parameter can only be used in
         conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and "high".
         Default value is None.
        :paramtype windingness: str or ~azure.maps.route.models.WindingnessLevel
        :keyword incline_level: Degree of hilliness for thrilling route. This parameter can only be
         used in conjunction with ``routeType``=thrilling. Known values are: "low", "normal", and
         "high". Default value is None.
        :paramtype incline_level: str or ~azure.maps.route.models.InclineLevel
        :keyword travel_mode: The mode of travel for the requested route. If not defined, default is
         'car'. Note that the requested travelMode may not be available for the entire route. Where the
         requested travelMode is not available for a particular section, the travelMode element of the
         response for that section will be "other". Note that travel modes bus, motorcycle, taxi and van
         are BETA functionality. Full restriction data is not available in all areas. In
         **calculateReachableRange** requests, the values bicycle and pedestrian must not be used. Known
         values are: "car", "truck", "taxi", "bus", "van", "motorcycle", "bicycle", and "pedestrian".
         Default value is None.
        :paramtype travel_mode: str or ~azure.maps.route.models.TravelMode
        :keyword avoid: Specifies something that the route calculation should try to avoid when
         determining the route. Can be specified multiple times in one request, for example,
         '&avoid=motorways&avoid=tollRoads&avoid=ferries'. In calculateReachableRange requests, the
         value alreadyUsedRoads must not be used. Default value is None.
        :paramtype avoid: list[str or ~azure.maps.route.models.RouteAvoidType]
        :keyword use_traffic_data: Possible values:
         * true - Do consider all available traffic information during routing
         * false - Ignore current traffic data during routing. Note that although the current traffic
         data is ignored during routing,
         the effect of historic traffic on effective road speeds is still
         incorporated. Default value is None.
        :paramtype use_traffic_data: bool
        :keyword route_type: The type of route requested. Known values are: "fastest", "shortest",
         "eco", and "thrilling". Default value is None.
        :paramtype route_type: str or ~azure.maps.route.models.RouteType
        :keyword vehicle_load_type: Types of cargo that may be classified as hazardous materials and
         restricted from some roads. Available vehicleLoadType values are US Hazmat classes 1 through 9,
         plus generic classifications for use in other countries. Values beginning with USHazmat are for
         US routing while otherHazmat should be used for all other countries. vehicleLoadType can be
         specified multiple times. This parameter is currently only considered for travelMode=truck.
         Known values are: "USHazmatClass1", "USHazmatClass2", "USHazmatClass3", "USHazmatClass4",
         "USHazmatClass5", "USHazmatClass6", "USHazmatClass7", "USHazmatClass8", "USHazmatClass9",
         "otherHazmatExplosive", "otherHazmatGeneral", and "otherHazmatHarmfulToWater". Default value is
         None.
        :paramtype vehicle_load_type: str or ~azure.maps.route.models.VehicleLoadType
        :keyword str continuation_token: A continuation token to restart a poller from a saved state.
        :keyword polling: By default, your polling method will be LROBasePolling. Pass in False for
         this operation to not poll, or pass in your own initialized polling object for a personal
         polling strategy.
        :paramtype polling: bool
        :keyword int polling_interval: Default waiting time between two polls for LRO operations if no
         Retry-After header is present.
        :return: An instance of AsyncLROPoller that returns RouteMatrixResult
        :rtype: ~azure.core.polling.AsyncLROPoller[~azure.maps.route.models.RouteMatrixResult]
        :raises ~azure.core.exceptions.HttpResponseError:
        """
        query=kwargs.pop('query', None)
        matrix_id = kwargs.pop('matrix_id', None)

        if matrix_id:
            return await self._route_client.begin_get_route_matrix(
                matrix_id=matrix_id,
                **kwargs
            )

        poller = await self._route_client.begin_request_route_matrix(
            format=ResponseFormat.JSON,
            route_matrix_query=query,
            **kwargs
        )
        return poller
