```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.maps.timezone

    class azure.maps.timezone.MapsTimeZoneClient(TimezoneClientGenerated): implements ContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, TokenCredential], 
                client_id: Optional[str] = None, 
                *, 
                endpoint: str = "https://atlas.microsoft.com", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def convert_windows_timezone_to_iana(
                self, 
                format: str = "json", 
                *, 
                windows_territory_code: Optional[str] = ..., 
                windows_timezone_id: str, 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace
        def get_iana_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace
        def get_iana_version(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_timezone(
                self, 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: Optional[List[float]] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_timezone_by_coordinates(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: List[float], 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_timezone_by_id(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_windows_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.maps.timezone.aio

    class azure.maps.timezone.aio.MapsTimeZoneClient(TimezoneClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                client_id: Optional[str] = None, 
                *, 
                endpoint: str = "https://atlas.microsoft.com", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def convert_windows_timezone_to_iana(
                self, 
                format: str = "json", 
                *, 
                windows_territory_code: Optional[str] = ..., 
                windows_timezone_id: str, 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace_async
        async def get_iana_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace_async
        async def get_iana_version(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_timezone(
                self, 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: Optional[List[float]] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_timezone_by_coordinates(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: List[float], 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_timezone_by_id(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_windows_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.maps.timezone.aio.operations

    class azure.maps.timezone.aio.operations.TimezoneOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def convert_windows_timezone_to_iana(
                self, 
                format: str = "json", 
                *, 
                windows_territory_code: Optional[str] = ..., 
                windows_timezone_id: str, 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace_async
        async def get_iana_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace_async
        async def get_iana_version(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_timezone_by_coordinates(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: List[float], 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_timezone_by_id(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_windows_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...


namespace azure.maps.timezone.operations

    class azure.maps.timezone.operations.TimezoneOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def convert_windows_timezone_to_iana(
                self, 
                format: str = "json", 
                *, 
                windows_territory_code: Optional[str] = ..., 
                windows_timezone_id: str, 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace
        def get_iana_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...

        @distributed_trace
        def get_iana_version(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_timezone_by_coordinates(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                coordinates: List[float], 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_timezone_by_id(
                self, 
                format: str = "json", 
                *, 
                accept_language: Optional[str] = ..., 
                dst_from: Optional[datetime] = ..., 
                dst_lasting_years: Optional[int] = ..., 
                options: Optional[str] = ..., 
                time_stamp: Optional[datetime] = ..., 
                timezone_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_windows_timezone_ids(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> List[JSON]: ...


```