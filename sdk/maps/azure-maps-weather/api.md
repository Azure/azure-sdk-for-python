```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.maps.weather

    class azure.maps.weather.MapsWeatherClient(MapsWeatherClientGenerated): implements ContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, TokenCredential], 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_air_quality_daily_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_air_quality_hourly_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_current_air_quality(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_current_conditions(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_actuals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_normals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_records(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_indices(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                index_group_id: Optional[int] = ..., 
                index_id: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_hourly_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_minute_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                interval: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_quarter_day_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_severe_weather_alerts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_active(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_forecast(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                include_window_geometry: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_locations(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_current_storm: bool = False, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        def get_tropical_storm_search(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_weather_along_route(
                self, 
                format: str = "json", 
                *, 
                language: Optional[str] = ..., 
                query: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def search_tropical_storm(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.maps.weather.aio

    class azure.maps.weather.aio.MapsWeatherClient(MapsWeatherClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AsyncTokenCredential], 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_air_quality_daily_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_air_quality_hourly_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_current_air_quality(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_current_conditions(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_actuals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_normals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_records(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_indices(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                index_group_id: Optional[int] = ..., 
                index_id: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_hourly_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_minute_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                interval: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_quarter_day_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_severe_weather_alerts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_active(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_forecast(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                include_window_geometry: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_locations(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_current_storm: bool = False, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        async def get_tropical_storm_search(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_weather_along_route(
                self, 
                format: str = "json", 
                *, 
                language: Optional[str] = ..., 
                query: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def search_tropical_storm(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.maps.weather.aio.operations

    class azure.maps.weather.aio.operations.WeatherOperations(WeatherOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_air_quality_daily_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_air_quality_hourly_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_current_air_quality(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_current_conditions(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_actuals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_normals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_historical_records(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_daily_indices(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                index_group_id: Optional[int] = ..., 
                index_id: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_hourly_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_minute_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                interval: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_quarter_day_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_severe_weather_alerts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_active(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_forecast(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                include_window_geometry: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_tropical_storm_locations(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_current_storm: bool = False, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        async def get_tropical_storm_search(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_weather_along_route(
                self, 
                format: str = "json", 
                *, 
                language: Optional[str] = ..., 
                query: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def search_tropical_storm(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.maps.weather.operations

    class azure.maps.weather.operations.WeatherOperations(WeatherOperationsGenerated):

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_air_quality_daily_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_air_quality_hourly_forecasts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: int = 1, 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_current_air_quality(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                include_pollutant_details: Optional[bool] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_current_conditions(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_actuals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_normals(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_historical_records(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                end_date: date, 
                start_date: date, 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_daily_indices(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                index_group_id: Optional[int] = ..., 
                index_id: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_hourly_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_minute_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                interval: Optional[int] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_quarter_day_forecast(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                duration: Optional[int] = ..., 
                language: Optional[str] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_severe_weather_alerts(
                self, 
                format: str = "json", 
                *, 
                coordinates: List[float], 
                details: Optional[str] = ..., 
                language: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_active(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_forecast(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                include_window_geometry: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_tropical_storm_locations(
                self, 
                format: str = "json", 
                *, 
                basin_id: str, 
                government_storm_id: int, 
                include_current_storm: bool = False, 
                include_details: bool = False, 
                include_geometric_details: bool = False, 
                unit: Optional[str] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        def get_tropical_storm_search(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_weather_along_route(
                self, 
                format: str = "json", 
                *, 
                language: Optional[str] = ..., 
                query: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def search_tropical_storm(
                self, 
                format: str = "json", 
                *, 
                basin_id: Optional[str] = ..., 
                government_storm_id: Optional[int] = ..., 
                year: int, 
                **kwargs: Any
            ) -> JSON: ...


```