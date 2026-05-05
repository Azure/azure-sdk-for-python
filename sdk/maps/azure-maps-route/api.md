```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.maps.route

    class azure.maps.route.MapsRouteClient(MapsRouteClientGenerated): implements ContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, TokenCredential], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_get_route_directions_batch(
                self, 
                *, 
                batch_id: str = ..., 
                continuation_token: Optional[str] = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                queries: List[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @distributed_trace
        def begin_get_route_matrix(
                self, 
                matrix_id: str, 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @distributed_trace
        def begin_get_route_matrix_batch(
                self, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                continuation_token: Optional[str] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                matrix_id: str = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                query: RouteMatrixQuery = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @overload
        def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @overload
        def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @overload
        def begin_request_route_matrix(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @overload
        def begin_request_route_matrix(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_route_directions(
                self, 
                route_points: Union[List[LatLongPair], List[Tuple]], 
                *, 
                acceleration_efficiency: float = ..., 
                allow_vignette: list[str] = ..., 
                alternative_type: Union[str, AlternativeRouteType] = ..., 
                arrive_at: datetime = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                avoid_areas: GeoJsonMultiPolygon = ..., 
                avoid_vignette: list[str] = ..., 
                compute_best_waypoint_order: bool = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                downhill_efficiency: float = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                instructions_type: Union[str, RouteInstructionsType] = ..., 
                is_commercial_vehicle: bool = ..., 
                language: str = ..., 
                max_alternatives: int = ..., 
                max_charge_in_kw_h: float = ..., 
                min_deviation_distance: int = ..., 
                min_deviation_time: int = ..., 
                report: Union[str, Report] = ..., 
                route_representation_for_best_order: Union[str, RouteRepresentationForBestOrder] = ..., 
                route_type: Union[str, RouteType] = ..., 
                supporting_points: GeoJsonGeometryCollection = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_heading: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace
        def get_route_directions_batch_sync(
                self, 
                queries: List[str], 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: RouteDirectionParameters, 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @overload
        def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: IO[bytes], 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace
        def get_route_matrix(
                self, 
                query: RouteMatrixQuery, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @distributed_trace
        def get_route_range(
                self, 
                coordinates: Union[LatLongPair, Tuple], 
                *, 
                acceleration_efficiency: float = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                distance_budget_in_meters: float = ..., 
                downhill_efficiency: float = ..., 
                energy_budget_in_kw_h: float = ..., 
                fuel_budget_in_liters: float = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                is_commercial_vehicle: bool = ..., 
                max_charge_in_kw_h: float = ..., 
                route_type: Union[str, RouteType] = ..., 
                time_budget_in_sec: float = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteRangeResult: ...

        @overload
        def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def request_route_matrix_sync(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @overload
        def request_route_matrix_sync(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.maps.route.aio

    class azure.maps.route.aio.MapsRouteClient(MapsRouteClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_get_route_directions_batch(
                self, 
                *, 
                batch_id: str = ..., 
                continuation_token: Optional[str] = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                queries: List[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @distributed_trace_async
        async def begin_get_route_matrix(
                self, 
                matrix_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @distributed_trace_async
        async def begin_get_route_matrix_batch(
                self, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                continuation_token: Optional[str] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                matrix_id: str = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                query: RouteMatrixQuery = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @overload
        async def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @overload
        async def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @overload
        async def begin_request_route_matrix(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @overload
        async def begin_request_route_matrix(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_route_directions(
                self, 
                route_points: Union[List[LatLongPair], List[Tuple]], 
                *, 
                acceleration_efficiency: float = ..., 
                allow_vignette: list[str] = ..., 
                alternative_type: Union[str, AlternativeRouteType] = ..., 
                arrive_at: datetime = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                avoid_areas: GeoJsonMultiPolygon = ..., 
                avoid_vignette: list[str] = ..., 
                compute_best_waypoint_order: bool = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                downhill_efficiency: float = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                instructions_type: Union[str, RouteInstructionsType] = ..., 
                is_commercial_vehicle: bool = ..., 
                language: str = ..., 
                max_alternatives: int = ..., 
                max_charge_in_kw_h: float = ..., 
                min_deviation_distance: int = ..., 
                min_deviation_time: int = ..., 
                report: Union[str, Report] = ..., 
                route_representation_for_best_order: Union[str, RouteRepresentationForBestOrder] = ..., 
                route_type: Union[str, RouteType] = ..., 
                supporting_points: GeoJsonGeometryCollection = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_heading: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace_async
        async def get_route_directions_batch_sync(
                self, 
                queries: List[str], 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: RouteDirectionParameters, 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @overload
        async def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: IO[bytes], 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace_async
        async def get_route_matrix(
                self, 
                query: RouteMatrixQuery, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @distributed_trace_async
        async def get_route_range(
                self, 
                coordinates: Union[LatLongPair, Tuple[float, float]], 
                *, 
                acceleration_efficiency: float = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                distance_budget_in_meters: float = ..., 
                downhill_efficiency: float = ..., 
                energy_budget_in_kw_h: float = ..., 
                fuel_budget_in_liters: float = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                is_commercial_vehicle: bool = ..., 
                max_charge_in_kw_h: float = ..., 
                route_type: Union[str, RouteType] = ..., 
                time_budget_in_sec: float = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteRangeResult: ...

        @overload
        async def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def request_route_matrix_sync(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @overload
        async def request_route_matrix_sync(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.maps.route.aio.operations

    class azure.maps.route.aio.operations.RouteOperations(RouteOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get_route_directions_batch(
                self, 
                *, 
                batch_id: str = ..., 
                continuation_token: Optional[str] = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                queries: List[str] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @distributed_trace_async
        async def begin_get_route_matrix(
                self, 
                matrix_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @distributed_trace_async
        async def begin_get_route_matrix_batch(
                self, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                continuation_token: Optional[str] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                matrix_id: str = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                query: RouteMatrixQuery = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @overload
        async def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @overload
        async def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteDirectionsBatchResult]: ...

        @overload
        async def begin_request_route_matrix(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @overload
        async def begin_request_route_matrix(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[RouteMatrixResult]: ...

        @distributed_trace_async
        async def get_route_directions(
                self, 
                route_points: Union[List[LatLongPair], List[Tuple]], 
                *, 
                acceleration_efficiency: float = ..., 
                allow_vignette: list[str] = ..., 
                alternative_type: Union[str, AlternativeRouteType] = ..., 
                arrive_at: datetime = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                avoid_areas: GeoJsonMultiPolygon = ..., 
                avoid_vignette: list[str] = ..., 
                compute_best_waypoint_order: bool = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                downhill_efficiency: float = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                instructions_type: Union[str, RouteInstructionsType] = ..., 
                is_commercial_vehicle: bool = ..., 
                language: str = ..., 
                max_alternatives: int = ..., 
                max_charge_in_kw_h: float = ..., 
                min_deviation_distance: int = ..., 
                min_deviation_time: int = ..., 
                report: Union[str, Report] = ..., 
                route_representation_for_best_order: Union[str, RouteRepresentationForBestOrder] = ..., 
                route_type: Union[str, RouteType] = ..., 
                supporting_points: GeoJsonGeometryCollection = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_heading: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace_async
        async def get_route_directions_batch_sync(
                self, 
                queries: List[str], 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: RouteDirectionParameters, 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @overload
        async def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: IO[bytes], 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace_async
        async def get_route_matrix(
                self, 
                query: RouteMatrixQuery, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @distributed_trace_async
        async def get_route_range(
                self, 
                coordinates: Union[LatLongPair, Tuple[float, float]], 
                *, 
                acceleration_efficiency: float = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                distance_budget_in_meters: float = ..., 
                downhill_efficiency: float = ..., 
                energy_budget_in_kw_h: float = ..., 
                fuel_budget_in_liters: float = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                is_commercial_vehicle: bool = ..., 
                max_charge_in_kw_h: float = ..., 
                route_type: Union[str, RouteType] = ..., 
                time_budget_in_sec: float = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteRangeResult: ...

        @overload
        async def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        async def request_route_matrix_sync(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @overload
        async def request_route_matrix_sync(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...


namespace azure.maps.route.models

    class azure.maps.route.models.AlternativeRouteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY_ROUTE = "anyRoute"
        BETTER_ROUTE = "betterRoute"


    class azure.maps.route.models.BatchRequest(Model):
        batch_items: list[BatchRequestItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                batch_items: Optional[List[BatchRequestItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.BatchRequestItem(Model):
        query: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.BatchResult(Model):
        batch_summary: BatchResultSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.BatchResultItem(Model):
        status_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.BatchResultSummary(Model):
        successful_requests: int
        total_requests: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.ComputeTravelTime(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        NONE = "none"


    class azure.maps.route.models.DelayMagnitude(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAJOR = "3"
        MINOR = "1"
        MODERATE = "2"
        UNDEFINED = "4"
        UNKNOWN = "0"


    class azure.maps.route.models.DrivingSide(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LEFT = "LEFT"
        RIGHT = "RIGHT"


    class azure.maps.route.models.EffectiveSetting(Model):
        key: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonFeature(GeoJsonObject, GeoJsonFeatureData):
        feature_type: str
        geometry: GeoJsonGeometry
        id: str
        properties: JSON
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                feature_type: Optional[str] = ..., 
                geometry: GeoJsonGeometry, 
                id: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonFeatureCollection(GeoJsonObject, GeoJsonFeatureCollectionData):
        features: list[GeoJsonFeature]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                features: List[GeoJsonFeature], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonFeatureCollectionData(Model):
        features: list[GeoJsonFeature]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                features: List[GeoJsonFeature], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonFeatureData(Model):
        feature_type: str
        geometry: GeoJsonGeometry
        id: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                feature_type: Optional[str] = ..., 
                geometry: GeoJsonGeometry, 
                id: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonGeometry(GeoJsonObject):
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonGeometryCollection(GeoJsonGeometry, GeoJsonGeometryCollectionData):
        geometries: list[GeoJsonGeometry]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                geometries: List[GeoJsonGeometry], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonGeometryCollectionData(Model):
        geometries: list[GeoJsonGeometry]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                geometries: List[GeoJsonGeometry], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonLineString(GeoJsonGeometry, GeoJsonLineStringData):
        coordinates: list[list[float]]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[float]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonLineStringData(Model):
        coordinates: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[float]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiLineString(GeoJsonGeometry, GeoJsonMultiLineStringData):
        coordinates: list[list[list[float]]]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[float]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiLineStringData(Model):
        coordinates: list[list[list[float]]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[float]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiPoint(GeoJsonGeometry, GeoJsonMultiPointData):
        coordinates: list[list[float]]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[float]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiPointData(Model):
        coordinates: list[list[float]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[float]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiPolygon(GeoJsonGeometry, GeoJsonMultiPolygonData):
        coordinates: list[list[list[list[float]]]]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[List[float]]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonMultiPolygonData(Model):
        coordinates: list[list[list[list[float]]]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[List[float]]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonObject(Model):
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_JSON_FEATURE = "Feature"
        GEO_JSON_FEATURE_COLLECTION = "FeatureCollection"
        GEO_JSON_GEOMETRY_COLLECTION = "GeometryCollection"
        GEO_JSON_LINE_STRING = "LineString"
        GEO_JSON_MULTI_LINE_STRING = "MultiLineString"
        GEO_JSON_MULTI_POINT = "MultiPoint"
        GEO_JSON_MULTI_POLYGON = "MultiPolygon"
        GEO_JSON_POINT = "Point"
        GEO_JSON_POLYGON = "Polygon"


    class azure.maps.route.models.GeoJsonPoint(GeoJsonGeometry, GeoJsonPointData):
        coordinates: list[float]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[float], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonPointData(Model):
        coordinates: list[float]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[float], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonPolygon(GeoJsonGeometry, GeoJsonPolygonData):
        coordinates: list[list[list[float]]]
        type: Union[str, GeoJsonObjectType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[float]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GeoJsonPolygonData(Model):
        coordinates: list[list[list[float]]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                coordinates: List[List[List[float]]], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.GuidanceInstructionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECTION_INFO = "DIRECTION_INFO"
        LOCATION_ARRIVAL = "LOCATION_ARRIVAL"
        LOCATION_DEPARTURE = "LOCATION_DEPARTURE"
        LOCATION_WAYPOINT = "LOCATION_WAYPOINT"
        ROAD_CHANGE = "ROAD_CHANGE"
        TURN = "TURN"


    class azure.maps.route.models.GuidanceManeuver(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRIVE = "ARRIVE"
        ARRIVE_LEFT = "ARRIVE_LEFT"
        ARRIVE_RIGHT = "ARRIVE_RIGHT"
        BEAR_LEFT = "BEAR_LEFT"
        BEAR_RIGHT = "BEAR_RIGHT"
        DEPART = "DEPART"
        ENTER_FREEWAY = "ENTER_FREEWAY"
        ENTER_HIGHWAY = "ENTER_HIGHWAY"
        ENTER_MOTORWAY = "ENTER_MOTORWAY"
        ENTRANCE_RAMP = "ENTRANCE_RAMP"
        FOLLOW = "FOLLOW"
        KEEP_LEFT = "KEEP_LEFT"
        KEEP_RIGHT = "KEEP_RIGHT"
        MAKE_U_TURN = "MAKE_UTURN"
        MOTORWAY_EXIT_LEFT = "MOTORWAY_EXIT_LEFT"
        MOTORWAY_EXIT_RIGHT = "MOTORWAY_EXIT_RIGHT"
        ROUNDABOUT_BACK = "ROUNDABOUT_BACK"
        ROUNDABOUT_CROSS = "ROUNDABOUT_CROSS"
        ROUNDABOUT_LEFT = "ROUNDABOUT_LEFT"
        ROUNDABOUT_RIGHT = "ROUNDABOUT_RIGHT"
        SHARP_LEFT = "SHARP_LEFT"
        SHARP_RIGHT = "SHARP_RIGHT"
        STRAIGHT = "STRAIGHT"
        SWITCH_MAIN_ROAD = "SWITCH_MAIN_ROAD"
        SWITCH_PARALLEL_ROAD = "SWITCH_PARALLEL_ROAD"
        TAKE_EXIT = "TAKE_EXIT"
        TAKE_FERRY = "TAKE_FERRY"
        TRY_MAKE_U_TURN = "TRY_MAKE_UTURN"
        TURN_LEFT = "TURN_LEFT"
        TURN_RIGHT = "TURN_RIGHT"
        WAYPOINT_LEFT = "WAYPOINT_LEFT"
        WAYPOINT_REACHED = "WAYPOINT_REACHED"
        WAYPOINT_RIGHT = "WAYPOINT_RIGHT"


    class azure.maps.route.models.InclineLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        NORMAL = "normal"


    class azure.maps.route.models.JsonFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json"


    class azure.maps.route.models.JunctionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIFURCATION = "BIFURCATION"
        REGULAR = "REGULAR"
        ROUNDABOUT = "ROUNDABOUT"


    class azure.maps.route.models.LatLongPair(Model):
        latitude: float
        longitude: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                latitude: Optional[float] = ..., 
                longitude: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.Report(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EFFECTIVE_SETTINGS = "effectiveSettings"


    class azure.maps.route.models.ResponseFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json"
        XML = "xml"


    class azure.maps.route.models.ResponseSectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CARPOOL = "CARPOOL"
        CAR_OR_TRAIN = "CAR_TRAIN"
        COUNTRY = "COUNTRY"
        FERRY = "FERRY"
        MOTORWAY = "MOTORWAY"
        PEDESTRIAN = "PEDESTRIAN"
        TOLL_ROAD = "TOLL_ROAD"
        TOLL_VIGNETTE = "TOLL_VIGNETTE"
        TRAFFIC = "TRAFFIC"
        TRAVEL_MODE = "TRAVEL_MODE"
        TUNNEL = "TUNNEL"
        URBAN = "URBAN"


    class azure.maps.route.models.ResponseTravelMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BICYCLE = "bicycle"
        BUS = "bus"
        CAR = "car"
        MOTORCYCLE = "motorcycle"
        OTHER = "other"
        PEDESTRIAN = "pedestrian"
        TAXI = "taxi"
        TRUCK = "truck"
        VAN = "van"


    class azure.maps.route.models.Route(Model):
        guidance: RouteGuidance
        legs: list[RouteLeg]
        sections: list[RouteSection]
        summary: RouteSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteAvoidType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_USED_ROADS = "alreadyUsedRoads"
        BORDER_CROSSINGS = "borderCrossings"
        CARPOOLS = "carpools"
        FERRIES = "ferries"
        MOTORWAYS = "motorways"
        TOLL_ROADS = "tollRoads"
        UNPAVED_ROADS = "unpavedRoads"


    class azure.maps.route.models.RouteDirectionParameters(Model):
        allow_vignette: list[str]
        avoid_areas: GeoJsonMultiPolygon
        avoid_vignette: list[str]
        supporting_points: GeoJsonGeometryCollection

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_vignette: Optional[List[str]] = ..., 
                avoid_areas: Optional[GeoJsonMultiPolygon] = ..., 
                avoid_vignette: Optional[List[str]] = ..., 
                supporting_points: Optional[GeoJsonGeometryCollection] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteDirections(Model):
        format_version: str
        optimized_waypoints: list[RouteOptimizedWaypoint]
        report: RouteReport
        routes: list[Route]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                report: Optional[RouteReport] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteDirectionsBatchItem(BatchResultItem):
        response: RouteDirectionsBatchItemResponse
        status_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteDirectionsBatchItemResponse(RouteDirections, ErrorResponse):
        error: ErrorDetail
        format_version: str
        optimized_waypoints: list[RouteOptimizedWaypoint]
        report: RouteReport
        routes: list[Route]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                report: Optional[RouteReport] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteDirectionsBatchResult(BatchResult):
        batch_items: list[RouteDirectionsBatchItem]
        batch_summary: BatchResultSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteGuidance(Model):
        instruction_groups: list[RouteInstructionGroup]
        instructions: list[RouteInstruction]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteInstruction(Model):
        combined_message: str
        country_code: str
        driving_side: Union[str, DrivingSide]
        exit_number: str
        instruction_type: Union[str, GuidanceInstructionType]
        junction_type: Union[str, JunctionType]
        maneuver: Union[str, GuidanceManeuver]
        message: str
        point: LatLongPair
        point_index: int
        possible_combine_with_next: bool
        road_numbers: list[str]
        roundabout_exit_number: str
        route_offset_in_meters: int
        signpost_text: str
        state_code: str
        street: str
        travel_time_in_seconds: int
        turn_angle_in_degrees: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instruction_type: Optional[Union[str, GuidanceInstructionType]] = ..., 
                point: Optional[LatLongPair] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteInstructionGroup(Model):
        first_instruction_index: int
        group_length_in_meters: int
        group_message: str
        last_instruction_index: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteInstructionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CODED = "coded"
        TAGGED = "tagged"
        TEXT = "text"


    class azure.maps.route.models.RouteLeg(Model):
        points: list[LatLongPair]
        summary: RouteLegSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteLegSummary(Model):
        arrival_time: datetime
        battery_consumption_in_kw_h: float
        departure_time: datetime
        fuel_consumption_in_liters: float
        historic_traffic_travel_time_in_seconds: int
        length_in_meters: int
        live_traffic_incidents_travel_time_in_seconds: int
        no_traffic_travel_time_in_seconds: int
        traffic_delay_in_seconds: int
        travel_time_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteMatrix(Model):
        response: RouteMatrixResultResponse
        status_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteMatrixQuery(Model):
        destinations: GeoJsonMultiPoint
        origins: GeoJsonMultiPoint

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destinations: Optional[GeoJsonMultiPoint] = ..., 
                origins: Optional[GeoJsonMultiPoint] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteMatrixResult(Model):
        format_version: str
        matrix: list[list[RouteMatrix]]
        summary: RouteMatrixSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteMatrixResultResponse(Model):
        summary: RouteLegSummary

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteMatrixSummary(Model):
        successful_routes: int
        total_routes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteOptimizedWaypoint(Model):
        optimized_index: int
        provided_index: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteRange(Model):
        boundary: list[LatLongPair]
        center: LatLongPair

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                center: Optional[LatLongPair] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteRangeResult(Model):
        format_version: str
        reachable_range: RouteRange
        report: RouteReport

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                reachable_range: Optional[RouteRange] = ..., 
                report: Optional[RouteReport] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteReport(Model):
        effective_settings: list[EffectiveSetting]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteRepresentationForBestOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "none"
        POLYLINE = "polyline"
        SUMMARY_ONLY = "summaryOnly"


    class azure.maps.route.models.RouteSection(Model):
        delay_in_seconds: int
        delay_magnitude: Union[str, DelayMagnitude]
        effective_speed_in_kmh: int
        end_point_index: int
        section_type: Union[str, ResponseSectionType]
        simple_category: Union[str, SimpleCategory]
        start_point_index: int
        tec: RouteSectionTec
        travel_mode: Union[str, ResponseTravelMode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tec: Optional[RouteSectionTec] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteSectionTec(Model):
        causes: list[RouteSectionTecCause]
        effect_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                causes: Optional[List[RouteSectionTecCause]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteSectionTecCause(Model):
        main_cause_code: int
        sub_cause_code: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteSummary(Model):
        arrival_time: datetime
        departure_time: datetime
        length_in_meters: int
        traffic_delay_in_seconds: int
        travel_time_in_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.maps.route.models.RouteType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECONOMY = "eco"
        FASTEST = "fastest"
        SHORTEST = "shortest"
        THRILLING = "thrilling"


    class azure.maps.route.models.SectionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CARPOOL = "carpool"
        CAR_OR_TRAIN = "carTrain"
        COUNTRY = "country"
        FERRY = "ferry"
        MOTORWAY = "motorway"
        PEDESTRIAN = "pedestrian"
        TOLL_ROAD = "tollRoad"
        TOLL_VIGNETTE = "tollVignette"
        TRAFFIC = "traffic"
        TRAVEL_MODE = "travelMode"
        TUNNEL = "tunnel"
        URBAN = "urban"


    class azure.maps.route.models.SimpleCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JAM = "JAM"
        OTHER = "OTHER"
        ROAD_CLOSURE = "ROAD_CLOSURE"
        ROAD_WORK = "ROAD_WORK"


    class azure.maps.route.models.TravelMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BICYCLE = "bicycle"
        BUS = "bus"
        CAR = "car"
        MOTORCYCLE = "motorcycle"
        PEDESTRIAN = "pedestrian"
        TAXI = "taxi"
        TRUCK = "truck"
        VAN = "van"


    class azure.maps.route.models.VehicleEngineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMBUSTION = "combustion"
        ELECTRIC = "electric"


    class azure.maps.route.models.VehicleLoadType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OTHER_HAZMAT_EXPLOSIVE = "otherHazmatExplosive"
        OTHER_HAZMAT_GENERAL = "otherHazmatGeneral"
        OTHER_HAZMAT_HARMFUL_TO_WATER = "otherHazmatHarmfulToWater"
        US_HAZMAT_CLASS1 = "USHazmatClass1"
        US_HAZMAT_CLASS2 = "USHazmatClass2"
        US_HAZMAT_CLASS3 = "USHazmatClass3"
        US_HAZMAT_CLASS4 = "USHazmatClass4"
        US_HAZMAT_CLASS5 = "USHazmatClass5"
        US_HAZMAT_CLASS6 = "USHazmatClass6"
        US_HAZMAT_CLASS7 = "USHazmatClass7"
        US_HAZMAT_CLASS8 = "USHazmatClass8"
        US_HAZMAT_CLASS9 = "USHazmatClass9"


    class azure.maps.route.models.WindingnessLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "high"
        LOW = "low"
        NORMAL = "normal"


namespace azure.maps.route.operations

    class azure.maps.route.operations.RouteOperations(RouteOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_get_route_directions_batch(
                self, 
                *, 
                batch_id: str = ..., 
                continuation_token: Optional[str] = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                queries: List[str] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @distributed_trace
        def begin_get_route_matrix(
                self, 
                matrix_id: str, 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @distributed_trace
        def begin_get_route_matrix_batch(
                self, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                continuation_token: Optional[str] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                matrix_id: str = ..., 
                polling: bool = ..., 
                polling_interval: Optional[int] = ..., 
                query: RouteMatrixQuery = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @overload
        def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @overload
        def begin_request_route_directions_batch(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RouteDirectionsBatchResult]: ...

        @overload
        def begin_request_route_matrix(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @overload
        def begin_request_route_matrix(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> LROPoller[RouteMatrixResult]: ...

        @distributed_trace
        def get_route_directions(
                self, 
                route_points: Union[List[LatLongPair], List[Tuple]], 
                *, 
                acceleration_efficiency: float = ..., 
                allow_vignette: list[str] = ..., 
                alternative_type: Union[str, AlternativeRouteType] = ..., 
                arrive_at: datetime = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                avoid_areas: GeoJsonMultiPolygon = ..., 
                avoid_vignette: list[str] = ..., 
                compute_best_waypoint_order: bool = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                downhill_efficiency: float = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                instructions_type: Union[str, RouteInstructionsType] = ..., 
                is_commercial_vehicle: bool = ..., 
                language: str = ..., 
                max_alternatives: int = ..., 
                max_charge_in_kw_h: float = ..., 
                min_deviation_distance: int = ..., 
                min_deviation_time: int = ..., 
                report: Union[str, Report] = ..., 
                route_representation_for_best_order: Union[str, RouteRepresentationForBestOrder] = ..., 
                route_type: Union[str, RouteType] = ..., 
                supporting_points: GeoJsonGeometryCollection = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_heading: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace
        def get_route_directions_batch_sync(
                self, 
                queries: List[str], 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: RouteDirectionParameters, 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @overload
        def get_route_directions_with_additional_parameters(
                self, 
                route_direction_parameters: IO[bytes], 
                format: Union[str, ResponseFormat] = "json", 
                *, 
                acceleration_efficiency: Optional[float] = ..., 
                alternative_type: Optional[Union[str, AlternativeRouteType]] = ..., 
                arrive_at: Optional[datetime] = ..., 
                auxiliary_power_in_kw: Optional[float] = ..., 
                auxiliary_power_in_liters_per_hour: Optional[float] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_best_waypoint_order: Optional[bool] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: Optional[str] = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: Optional[str] = ..., 
                content_type: str = "application/json", 
                current_charge_in_kw_h: Optional[float] = ..., 
                current_fuel_in_liters: Optional[float] = ..., 
                deceleration_efficiency: Optional[float] = ..., 
                depart_at: Optional[datetime] = ..., 
                downhill_efficiency: Optional[float] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                fuel_energy_density_in_megajoules_per_liter: Optional[float] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                instructions_type: Optional[Union[str, RouteInstructionsType]] = ..., 
                is_commercial_vehicle: bool = False, 
                language: Optional[str] = ..., 
                max_alternatives: Optional[int] = ..., 
                max_charge_in_kw_h: Optional[float] = ..., 
                min_deviation_distance: Optional[int] = ..., 
                min_deviation_time: Optional[int] = ..., 
                report: Optional[Union[str, Report]] = ..., 
                route_points: str, 
                route_representation_for_best_order: Optional[Union[str, RouteRepresentationForBestOrder]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                uphill_efficiency: Optional[float] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_engine_type: Optional[Union[str, VehicleEngineType]] = ..., 
                vehicle_heading: Optional[int] = ..., 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteDirections: ...

        @distributed_trace
        def get_route_matrix(
                self, 
                query: RouteMatrixQuery, 
                *, 
                arrive_at: datetime = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                compute_travel_time: Union[str, ComputeTravelTime] = ..., 
                depart_at: datetime = ..., 
                filter_section_type: Union[str, SectionType] = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                route_type: Union[str, RouteType] = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                wait_for_results: bool = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @distributed_trace
        def get_route_range(
                self, 
                coordinates: Union[LatLongPair, Tuple], 
                *, 
                acceleration_efficiency: float = ..., 
                auxiliary_power_in_kw: float = ..., 
                auxiliary_power_in_liters_per_hour: float = ..., 
                avoid: Union[list[str, RouteAvoidType]] = ..., 
                constant_speed_consumption_in_kw_h_per_hundred_km: str = ..., 
                constant_speed_consumption_in_liters_per_hundred_km: str = ..., 
                current_charge_in_kw_h: float = ..., 
                current_fuel_in_liters: float = ..., 
                deceleration_efficiency: float = ..., 
                depart_at: datetime = ..., 
                distance_budget_in_meters: float = ..., 
                downhill_efficiency: float = ..., 
                energy_budget_in_kw_h: float = ..., 
                fuel_budget_in_liters: float = ..., 
                fuel_energy_density_in_megajoules_per_liter: float = ..., 
                incline_level: Union[str, InclineLevel] = ..., 
                is_commercial_vehicle: bool = ..., 
                max_charge_in_kw_h: float = ..., 
                route_type: Union[str, RouteType] = ..., 
                time_budget_in_sec: float = ..., 
                travel_mode: Union[str, TravelMode] = ..., 
                uphill_efficiency: float = ..., 
                use_traffic_data: bool = ..., 
                vehicle_axle_weight: int = ..., 
                vehicle_engine_type: Union[str, VehicleEngineType] = ..., 
                vehicle_height: float = ..., 
                vehicle_length: float = ..., 
                vehicle_load_type: Union[str, VehicleLoadType] = ..., 
                vehicle_max_speed: int = ..., 
                vehicle_weight: int = ..., 
                vehicle_width: float = ..., 
                windingness: Union[str, WindingnessLevel] = ..., 
                **kwargs: Any
            ) -> RouteRangeResult: ...

        @overload
        def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: BatchRequest, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def request_route_directions_batch_sync(
                self, 
                route_directions_batch_queries: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RouteDirectionsBatchResult: ...

        @overload
        def request_route_matrix_sync(
                self, 
                route_matrix_query: RouteMatrixQuery, 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...

        @overload
        def request_route_matrix_sync(
                self, 
                route_matrix_query: IO[bytes], 
                format: Union[str, JsonFormat] = "json", 
                *, 
                arrive_at: Optional[datetime] = ..., 
                avoid: Optional[List[Union[str, RouteAvoidType]]] = ..., 
                compute_travel_time: Optional[Union[str, ComputeTravelTime]] = ..., 
                content_type: str = "application/json", 
                depart_at: Optional[datetime] = ..., 
                filter_section_type: Optional[Union[str, SectionType]] = ..., 
                incline_level: Optional[Union[str, InclineLevel]] = ..., 
                route_type: Optional[Union[str, RouteType]] = ..., 
                travel_mode: Optional[Union[str, TravelMode]] = ..., 
                use_traffic_data: Optional[bool] = ..., 
                vehicle_axle_weight: int = 0, 
                vehicle_height: float = 0, 
                vehicle_length: float = 0, 
                vehicle_load_type: Optional[Union[str, VehicleLoadType]] = ..., 
                vehicle_max_speed: int = 0, 
                vehicle_weight: int = 0, 
                vehicle_width: float = 0, 
                wait_for_results: Optional[bool] = ..., 
                windingness: Optional[Union[str, WindingnessLevel]] = ..., 
                **kwargs: Any
            ) -> RouteMatrixResult: ...


```