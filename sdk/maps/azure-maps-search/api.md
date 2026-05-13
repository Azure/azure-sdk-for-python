```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.maps.search

    class azure.maps.search.BoundaryResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADMIN_DISTRICT = "adminDistrict"
        ADMIN_DISTRICT2 = "adminDistrict2"
        COUNTRY_REGION = "countryRegion"
        LOCALITY = "locality"
        NEIGHBORHOOD = "neighborhood"
        POSTAL_CODE = "postalCode"
        POSTAL_CODE2 = "postalCode2"
        POSTAL_CODE3 = "postalCode3"
        POSTAL_CODE4 = "postalCode4"


    class azure.maps.search.CalculationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERPOLATION = "Interpolation"
        INTERPOLATION_OFFSET = "InterpolationOffset"
        PARCEL = "Parcel"
        ROOFTOP = "Rooftop"


    class azure.maps.search.Confidence(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.maps.search.FeatureCollection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEATURE_COLLECTION = "FeatureCollection"


    class azure.maps.search.FeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEATURE = "Feature"


    class azure.maps.search.GeoJsonObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEO_JSON_FEATURE = "Feature"
        GEO_JSON_FEATURE_COLLECTION = "FeatureCollection"
        GEO_JSON_GEOMETRY_COLLECTION = "GeometryCollection"
        GEO_JSON_LINE_STRING = "LineString"
        GEO_JSON_MULTI_LINE_STRING = "MultiLineString"
        GEO_JSON_MULTI_POINT = "MultiPoint"
        GEO_JSON_MULTI_POLYGON = "MultiPolygon"
        GEO_JSON_POINT = "Point"
        GEO_JSON_POLYGON = "Polygon"


    class azure.maps.search.LocalizedMapView(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AE = "AE"
        AR = "AR"
        AUTO = "Auto"
        BH = "BH"
        IN = "IN"
        IQ = "IQ"
        JO = "JO"
        KW = "KW"
        LB = "LB"
        MA = "MA"
        OM = "OM"
        PK = "PK"
        PS = "PS"
        QA = "QA"
        SA = "SA"
        SY = "SY"
        UNIFIED = "Unified"
        YE = "YE"


    class azure.maps.search.MapsSearchClient(MapsSearchClientGenerated): implements ContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, TokenCredential], 
                *, 
                client_id: Optional[str] = ..., 
                endpoint: str = "https://atlas.microsoft.com", 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_geocoding(
                self, 
                *, 
                address_line: Optional[str] = ..., 
                admin_district: Optional[str] = ..., 
                admin_district2: Optional[str] = ..., 
                admin_district3: Optional[str] = ..., 
                bbox: Optional[List[float]] = ..., 
                coordinates: Optional[List[float]] = ..., 
                country_region: Optional[str] = ..., 
                locality: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                query: Optional[str] = ..., 
                top: int = 5, 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_polygon(
                self, 
                *, 
                coordinates: List[float], 
                resolution: str = "medium", 
                result_type: str = "countryRegion", 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_reverse_geocoding(
                self, 
                *, 
                coordinates: List[float], 
                result_types: Optional[List[str]] = ..., 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_reverse_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_reverse_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.maps.search.MatchCodes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMBIGUOUS = "Ambiguous"
        GOOD = "Good"
        UP_HIERARCHY = "UpHierarchy"


    class azure.maps.search.Resolution(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUGE = "huge"
        LARGE = "large"
        MEDIUM = "medium"
        SMALL = "small"


    class azure.maps.search.ResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS = "Address"
        ADMIN_DIVISION1 = "AdminDivision1"
        ADMIN_DIVISION2 = "AdminDivision2"
        COUNTRY_REGION = "CountryRegion"
        NEIGHBORHOOD = "Neighborhood"
        POPULATED_PLACE = "PopulatedPlace"
        POSTCODE1 = "Postcode1"


    class azure.maps.search.ReverseGeocodingResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS = "Address"
        ADMIN_DIVISION1 = "AdminDivision1"
        ADMIN_DIVISION2 = "AdminDivision2"
        COUNTRY_REGION = "CountryRegion"
        NEIGHBORHOOD = "Neighborhood"
        POPULATED_PLACE = "PopulatedPlace"
        POSTCODE1 = "Postcode1"


    class azure.maps.search.UsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISPLAY = "Display"
        ROUTE = "Route"


namespace azure.maps.search.aio

    class azure.maps.search.aio.MapsSearchClient(MapsSearchClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                *, 
                client_id: Optional[str] = ..., 
                endpoint: str = "https://atlas.microsoft.com", 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_geocoding(
                self, 
                *, 
                address_line: Optional[str] = ..., 
                admin_district: Optional[str] = ..., 
                admin_district2: Optional[str] = ..., 
                admin_district3: Optional[str] = ..., 
                bbox: Optional[List[float]] = ..., 
                coordinates: Optional[List[float]] = ..., 
                country_region: Optional[str] = ..., 
                locality: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                query: Optional[str] = ..., 
                top: int = 5, 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_polygon(
                self, 
                *, 
                coordinates: List[float], 
                resolution: str = "medium", 
                result_type: str = "countryRegion", 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_reverse_geocoding(
                self, 
                *, 
                coordinates: List[float], 
                result_types: Optional[List[str]] = ..., 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_reverse_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_reverse_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.maps.search.aio.operations

    class azure.maps.search.aio.operations.SearchOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_geocoding(
                self, 
                *, 
                address_line: Optional[str] = ..., 
                admin_district: Optional[str] = ..., 
                admin_district2: Optional[str] = ..., 
                admin_district3: Optional[str] = ..., 
                bbox: Optional[List[float]] = ..., 
                coordinates: Optional[List[float]] = ..., 
                country_region: Optional[str] = ..., 
                locality: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                query: Optional[str] = ..., 
                top: int = 5, 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_polygon(
                self, 
                *, 
                coordinates: List[float], 
                resolution: str = "medium", 
                result_type: str = "countryRegion", 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_reverse_geocoding(
                self, 
                *, 
                coordinates: List[float], 
                result_types: Optional[List[str]] = ..., 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_reverse_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        async def get_reverse_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.maps.search.operations

    class azure.maps.search.operations.SearchOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_geocoding(
                self, 
                *, 
                address_line: Optional[str] = ..., 
                admin_district: Optional[str] = ..., 
                admin_district2: Optional[str] = ..., 
                admin_district3: Optional[str] = ..., 
                bbox: Optional[List[float]] = ..., 
                coordinates: Optional[List[float]] = ..., 
                country_region: Optional[str] = ..., 
                locality: Optional[str] = ..., 
                postal_code: Optional[str] = ..., 
                query: Optional[str] = ..., 
                top: int = 5, 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_polygon(
                self, 
                *, 
                coordinates: List[float], 
                resolution: str = "medium", 
                result_type: str = "countryRegion", 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_reverse_geocoding(
                self, 
                *, 
                coordinates: List[float], 
                result_types: Optional[List[str]] = ..., 
                view: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_reverse_geocoding_batch(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...

        @overload
        def get_reverse_geocoding_batch(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> JSON: ...


```