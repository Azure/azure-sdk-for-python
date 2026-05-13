```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.maps.render

    class azure.maps.render.IncludeText(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "no"
        YES = "yes"


    class azure.maps.render.LocalizedMapView(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.maps.render.MapImageStyle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DARK = "dark"
        MAIN = "main"


    class azure.maps.render.MapTileSize(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SIZE256 = "256"
        SIZE512 = "512"


    class azure.maps.render.MapsRenderClient(MapsRenderClientGenerated): implements ContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, TokenCredential], 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        @distributed_trace
        def get_copyright_caption(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_for_tile(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_for_world(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_from_bounding_box(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                north_east: List[float], 
                south_west: List[float], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_map_attribution(
                self, 
                *, 
                bounds: List[float], 
                tileset_id: str, 
                zoom: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_map_state_tile(
                self, 
                *, 
                stateset_id: str, 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_static_image(
                self, 
                *, 
                bounding_box_private: Optional[List[float]] = ..., 
                center: Optional[List[float]] = ..., 
                height: Optional[int] = ..., 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                path: Optional[List[str]] = ..., 
                pins: Optional[List[str]] = ..., 
                tileset_id: Optional[str] = ..., 
                traffic_layer: Optional[str] = ..., 
                width: Optional[int] = ..., 
                zoom: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_tile(
                self, 
                *, 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                tile_size: Optional[str] = ..., 
                tileset_id: str, 
                time_stamp: Optional[datetime] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_tileset(
                self, 
                *, 
                tileset_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


    class azure.maps.render.RasterTileFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PNG = "png"


    class azure.maps.render.ResponseFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JSON = "json"
        XML = "xml"


    class azure.maps.render.StaticMapLayer(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "basic"
        HYBRID = "hybrid"
        LABELS = "labels"


    class azure.maps.render.TilesetID(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_BASE = "microsoft.base"
        MICROSOFT_BASE_DARKGREY = "microsoft.base.darkgrey"
        MICROSOFT_BASE_HYBRID = "microsoft.base.hybrid"
        MICROSOFT_BASE_HYBRID_DARKGREY = "microsoft.base.hybrid.darkgrey"
        MICROSOFT_BASE_HYBRID_ROAD = "microsoft.base.hybrid.road"
        MICROSOFT_BASE_LABELS = "microsoft.base.labels"
        MICROSOFT_BASE_LABELS_DARKGREY = "microsoft.base.labels.darkgrey"
        MICROSOFT_BASE_LABELS_ROAD = "microsoft.base.labels.road"
        MICROSOFT_BASE_ROAD = "microsoft.base.road"
        MICROSOFT_IMAGERY = "microsoft.imagery"
        MICROSOFT_TERRA_MAIN = "microsoft.terra.main"
        MICROSOFT_TRAFFIC_ABSOLUTE = "microsoft.traffic.absolute"
        MICROSOFT_TRAFFIC_ABSOLUTE_MAIN = "microsoft.traffic.absolute.main"
        MICROSOFT_TRAFFIC_DELAY = "microsoft.traffic.delay"
        MICROSOFT_TRAFFIC_DELAY_MAIN = "microsoft.traffic.delay.main"
        MICROSOFT_TRAFFIC_INCIDENT = "microsoft.traffic.incident"
        MICROSOFT_TRAFFIC_REDUCED_MAIN = "microsoft.traffic.reduced.main"
        MICROSOFT_TRAFFIC_RELATIVE = "microsoft.traffic.relative"
        MICROSOFT_TRAFFIC_RELATIVE_DARK = "microsoft.traffic.relative.dark"
        MICROSOFT_TRAFFIC_RELATIVE_MAIN = "microsoft.traffic.relative.main"
        MICROSOFT_WEATHER_INFRARED_MAIN = "microsoft.weather.infrared.main"
        MICROSOFT_WEATHER_RADAR_MAIN = "microsoft.weather.radar.main"


namespace azure.maps.render.aio

    class azure.maps.render.aio.MapsRenderClient(MapsRenderClientGenerated): implements AsyncContextManager 

        def __init__(
                self, 
                credential: Union[AzureKeyCredential, AzureSasCredential, AsyncTokenCredential], 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def get_copyright_caption(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_for_tile(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_for_world(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_from_bounding_box(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                north_east: List[float], 
                south_west: List[float], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_map_attribution(
                self, 
                *, 
                bounds: List[float], 
                tileset_id: str, 
                zoom: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_map_state_tile(
                self, 
                *, 
                stateset_id: str, 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_static_image(
                self, 
                *, 
                bounding_box_private: Optional[List[float]] = ..., 
                center: Optional[List[float]] = ..., 
                height: Optional[int] = ..., 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                path: Optional[List[str]] = ..., 
                pins: Optional[List[str]] = ..., 
                tileset_id: Optional[str] = ..., 
                traffic_layer: Optional[str] = ..., 
                width: Optional[int] = ..., 
                zoom: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_tile(
                self, 
                *, 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                tile_size: Optional[str] = ..., 
                tileset_id: str, 
                time_stamp: Optional[datetime] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_tileset(
                self, 
                *, 
                tileset_id: str, 
                **kwargs: Any
            ) -> JSON: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.maps.render.aio.operations

    class azure.maps.render.aio.operations.RenderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_copyright_caption(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_for_tile(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_for_world(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_copyright_from_bounding_box(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                north_east: List[float], 
                south_west: List[float], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_map_attribution(
                self, 
                *, 
                bounds: List[float], 
                tileset_id: str, 
                zoom: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace_async
        async def get_map_state_tile(
                self, 
                *, 
                stateset_id: str, 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_static_image(
                self, 
                *, 
                bounding_box_private: Optional[List[float]] = ..., 
                center: Optional[List[float]] = ..., 
                height: Optional[int] = ..., 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                path: Optional[List[str]] = ..., 
                pins: Optional[List[str]] = ..., 
                tileset_id: Optional[str] = ..., 
                traffic_layer: Optional[str] = ..., 
                width: Optional[int] = ..., 
                zoom: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_tile(
                self, 
                *, 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                tile_size: Optional[str] = ..., 
                tileset_id: str, 
                time_stamp: Optional[datetime] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_map_tileset(
                self, 
                *, 
                tileset_id: str, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.maps.render.operations

    class azure.maps.render.operations.RenderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_copyright_caption(
                self, 
                format: str = "json", 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_for_tile(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_for_world(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_copyright_from_bounding_box(
                self, 
                format: str = "json", 
                *, 
                include_text: Optional[str] = ..., 
                north_east: List[float], 
                south_west: List[float], 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_map_attribution(
                self, 
                *, 
                bounds: List[float], 
                tileset_id: str, 
                zoom: int, 
                **kwargs: Any
            ) -> JSON: ...

        @distributed_trace
        def get_map_state_tile(
                self, 
                *, 
                stateset_id: str, 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_static_image(
                self, 
                *, 
                bounding_box_private: Optional[List[float]] = ..., 
                center: Optional[List[float]] = ..., 
                height: Optional[int] = ..., 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                path: Optional[List[str]] = ..., 
                pins: Optional[List[str]] = ..., 
                tileset_id: Optional[str] = ..., 
                traffic_layer: Optional[str] = ..., 
                width: Optional[int] = ..., 
                zoom: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_tile(
                self, 
                *, 
                language: Optional[str] = ..., 
                localized_map_view: Optional[str] = ..., 
                tile_size: Optional[str] = ..., 
                tileset_id: str, 
                time_stamp: Optional[datetime] = ..., 
                x: int, 
                y: int, 
                z: int, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_map_tileset(
                self, 
                *, 
                tileset_id: str, 
                **kwargs: Any
            ) -> JSON: ...


```