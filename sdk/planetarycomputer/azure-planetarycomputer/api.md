```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.planetarycomputer

    class azure.planetarycomputer.PlanetaryComputerProClient: implements ContextManager 
        data: DataOperations
        ingestion: IngestionOperations
        shared_access_signature: SharedAccessSignatureOperations
        stac: StacOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: TokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.planetarycomputer.aio

    class azure.planetarycomputer.aio.PlanetaryComputerProClient: implements AsyncContextManager 
        data: DataOperations
        ingestion: IngestionOperations
        shared_access_signature: SharedAccessSignatureOperations
        stac: StacOperations

        def __init__(
                self, 
                endpoint: str, 
                credential: AsyncTokenCredential, 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.planetarycomputer.aio.operations

    class azure.planetarycomputer.aio.operations.DataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_static_image(
                self, 
                collection_id: str, 
                body: ImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        async def create_static_image(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        async def create_static_image(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        async def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: Feature, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: JSON, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: IO[bytes], 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: Feature, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: JSON, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @overload
        async def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: IO[bytes], 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_asset_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AssetStatisticsResponse: ...

        @distributed_trace_async
        async def get_bounds(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> StacItemBounds: ...

        @distributed_trace_async
        async def get_class_map_legend(
                self, 
                classmap_name: str, 
                *, 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                **kwargs: Any
            ) -> ClassMapLegendResponse: ...

        @overload
        async def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: Feature, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @overload
        async def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @overload
        async def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @distributed_trace_async
        async def get_info_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                assets: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> TilerInfoGeoJsonFeature: ...

        @distributed_trace_async
        async def get_interval_legend(
                self, 
                classmap_name: str, 
                *, 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[List[List[int]]]: ...

        @distributed_trace_async
        async def get_item_asset_details(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                assets: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> TilerInfoMapResponse: ...

        @distributed_trace_async
        async def get_legend(
                self, 
                color_map_name: str, 
                *, 
                height: Optional[float] = ..., 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                width: Optional[float] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_mosaics_assets_for_point(
                self, 
                search_id: str, 
                longitude: float, 
                latitude: float, 
                *, 
                coordinate_reference_system: Optional[str] = ..., 
                exit_when_full: Optional[bool] = ..., 
                items_limit: Optional[int] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[StacItemPointAsset]: ...

        @distributed_trace_async
        async def get_mosaics_assets_for_tile(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                *, 
                collection_id: str, 
                exit_when_full: Optional[bool] = ..., 
                items_limit: Optional[int] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[TilerAssetGeoJson]: ...

        @distributed_trace_async
        async def get_mosaics_search_info(
                self, 
                search_id: str, 
                **kwargs: Any
            ) -> TilerStacSearchRegistration: ...

        @distributed_trace_async
        async def get_mosaics_tile(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                scale: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                collection: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                exit_when_full: Optional[bool] = ..., 
                expression: Optional[str] = ..., 
                items_limit: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                pixel_selection: Optional[Union[str, PixelSelection]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_mosaics_tile_json(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                collection: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                exit_when_full: Optional[bool] = ..., 
                expression: Optional[str] = ..., 
                items_limit: Optional[int] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                pixel_selection: Optional[Union[str, PixelSelection]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                time_limit: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TileJsonMetadata: ...

        @distributed_trace_async
        async def get_mosaics_wmts_capabilities(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_part(
                self, 
                collection_id: str, 
                item_id: str, 
                minx: float, 
                miny: float, 
                maxx: float, 
                maxy: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_part_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                minx: float, 
                miny: float, 
                maxx: float, 
                maxy: float, 
                width: int, 
                height: int, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_point(
                self, 
                collection_id: str, 
                item_id: str, 
                longitude: float, 
                latitude: float, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TilerCoreModelsResponsesPoint: ...

        @distributed_trace_async
        async def get_preview(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                format: Optional[Union[str, TilerImageFormat]] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_preview_with_format(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_static_image(
                self, 
                collection_id: str, 
                id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_tile(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                scale: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                subdataset_bands: Optional[List[str]] = ..., 
                subdataset_name: Optional[str] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_tile_json(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TileJsonMetadata: ...

        @distributed_trace_async
        async def get_tile_matrix_definitions(
                self, 
                tile_matrix_set_id: str, 
                **kwargs: Any
            ) -> TileMatrixSet: ...

        @distributed_trace_async
        async def get_wmts_capabilities(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def list_available_assets(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace_async
        async def list_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TilerStacItemStatistics: ...

        @distributed_trace_async
        async def list_tile_matrices(self, **kwargs: Any) -> List[str]: ...

        @overload
        async def register_mosaics_search(
                self, 
                *, 
                bounding_box: Optional[float] = ..., 
                collections: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                datetime: Optional[str] = ..., 
                filter: Optional[dict[str, Any]] = ..., 
                filter_language: Optional[Union[str, FilterLanguage]] = ..., 
                ids: Optional[List[str]] = ..., 
                intersects: Optional[Geometry] = ..., 
                metadata: Optional[MosaicMetadata] = ..., 
                query: Optional[dict[str, Any]] = ..., 
                sort_by: Optional[List[StacSortExtension]] = ..., 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...

        @overload
        async def register_mosaics_search(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...

        @overload
        async def register_mosaics_search(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...


    class azure.planetarycomputer.aio.operations.IngestionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def cancel_all_operations(self, **kwargs: Any) -> None: ...

        @distributed_trace_async
        async def cancel_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def create(
                self, 
                collection_id: str, 
                body: IngestionDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        async def create(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        async def create(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @distributed_trace_async
        async def create_run(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> IngestionRun: ...

        @overload
        async def create_source(
                self, 
                body: IngestionSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        async def create_source(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        async def create_source(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @distributed_trace_async
        async def delete_source(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @distributed_trace_async
        async def get_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> Operation: ...

        @distributed_trace_async
        async def get_run(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> IngestionRun: ...

        @distributed_trace_async
        async def get_source(
                self, 
                id: str, 
                **kwargs: Any
            ) -> IngestionSource: ...

        @distributed_trace
        def list(
                self, 
                collection_id: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IngestionDefinition]: ...

        @distributed_trace
        def list_managed_identities(self, **kwargs: Any) -> AsyncItemPaged[ManagedIdentityMetadata]: ...

        @distributed_trace
        def list_operations(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Operation]: ...

        @distributed_trace
        def list_runs(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IngestionRun]: ...

        @distributed_trace
        def list_sources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[IngestionSourceSummary]: ...

        @overload
        async def replace_source(
                self, 
                id: str, 
                body: IngestionSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        async def replace_source(
                self, 
                id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        async def replace_source(
                self, 
                id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        async def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: IngestionDefinition, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        async def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        async def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...


    class azure.planetarycomputer.aio.operations.SharedAccessSignatureOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_sign(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                href: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureSignedLink: ...

        @distributed_trace_async
        async def get_token(
                self, 
                collection_id: str, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> SharedAccessSignatureToken: ...

        @distributed_trace_async
        async def revoke_token(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.planetarycomputer.aio.operations.StacOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_mosaic(
                self, 
                collection_id: str, 
                body: StacMosaic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def add_mosaic(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def add_mosaic(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def begin_create_collection(
                self, 
                body: StacCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_collection(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_collection(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_item(
                self, 
                collection_id: str, 
                body: StacItemOrStacItemCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_item(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_item(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: StacItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_collection(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_item(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: StacItem, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_collection_asset(
                self, 
                collection_id: str, 
                body: StacAssetData, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def create_collection_asset(
                self, 
                collection_id: str, 
                body: JSON, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: StacCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def create_queryables(
                self, 
                collection_id: str, 
                body: List[StacQueryable], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        async def create_queryables(
                self, 
                collection_id: str, 
                body: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        async def create_queryables(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        async def create_render_option(
                self, 
                collection_id: str, 
                body: RenderOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        async def create_render_option(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        async def create_render_option(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @distributed_trace_async
        async def delete_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                **kwargs: Any
            ) -> StacCollection: ...

        @distributed_trace_async
        async def delete_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_collection(
                self, 
                collection_id: str, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacCollection: ...

        @distributed_trace_async
        async def get_collection_configuration(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> UserCollectionSettings: ...

        @distributed_trace_async
        async def get_collection_queryables(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> QueryableDefinitionsResponse: ...

        @distributed_trace_async
        async def get_collection_thumbnail(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> AsyncIterator[bytes]: ...

        @distributed_trace_async
        async def get_collections(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacCatalogCollections: ...

        @distributed_trace_async
        async def get_conformance_class(self, **kwargs: Any) -> StacConformanceClasses: ...

        @distributed_trace_async
        async def get_item(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> StacItem: ...

        @distributed_trace_async
        async def get_item_collection(
                self, 
                collection_id: str, 
                *, 
                bounding_box: Optional[List[str]] = ..., 
                datetime: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @distributed_trace_async
        async def get_landing_page(self, **kwargs: Any) -> StacLandingPage: ...

        @distributed_trace_async
        async def get_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                **kwargs: Any
            ) -> StacMosaic: ...

        @distributed_trace_async
        async def get_partition_type(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> PartitionType: ...

        @distributed_trace_async
        async def get_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                **kwargs: Any
            ) -> RenderOption: ...

        @distributed_trace_async
        async def get_tile_settings(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> TileSettings: ...

        @distributed_trace_async
        async def list_mosaics(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> List[StacMosaic]: ...

        @distributed_trace_async
        async def list_queryables(self, **kwargs: Any) -> QueryableDefinitionsResponse: ...

        @distributed_trace_async
        async def list_render_options(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> List[RenderOption]: ...

        @overload
        async def replace_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                body: StacAssetData, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def replace_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                body: JSON, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        async def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: StacMosaic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        async def replace_partition_type(
                self, 
                collection_id: str, 
                body: PartitionType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def replace_partition_type(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def replace_partition_type(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: StacQueryable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        async def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        async def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        async def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: RenderOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        async def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        async def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        async def replace_tile_settings(
                self, 
                collection_id: str, 
                body: TileSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        async def replace_tile_settings(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        async def replace_tile_settings(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        async def search(
                self, 
                body: StacSearchParameters, 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @overload
        async def search(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @overload
        async def search(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...


namespace azure.planetarycomputer.models

    class azure.planetarycomputer.models.AssetMetadata(_Model):
        description: str
        key: str
        roles: list[str]
        title: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                key: str, 
                roles: list[str], 
                title: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.AssetStatisticsResponse(_Model):


    class azure.planetarycomputer.models.BandStatistics(_Model):
        count: float
        histogram: list[list[float]]
        majority: float
        masked_pixels: float
        maximum: float
        mean: float
        median: float
        minimum: float
        minority: float
        percentile2: float
        percentile98: float
        std: float
        sum: float
        unique: float
        valid_percent: float
        valid_pixels: float

        @overload
        def __init__(
                self, 
                *, 
                count: float, 
                histogram: list[list[float]], 
                majority: float, 
                masked_pixels: float, 
                maximum: float, 
                mean: float, 
                median: float, 
                minimum: float, 
                minority: float, 
                percentile2: float, 
                percentile98: float, 
                std: float, 
                sum: float, 
                unique: float, 
                valid_percent: float, 
                valid_pixels: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.BandStatisticsMap(_Model):


    class azure.planetarycomputer.models.ClassMapLegendResponse(_Model):


    class azure.planetarycomputer.models.ColorMapNames(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCENT = "accent"
        ACCENT_R = "accent_r"
        AFMHOT = "afmhot"
        AFMHOT_R = "afmhot_r"
        AI4_G_LULC = "ai4g-lulc"
        ALOS_FNF = "alos-fnf"
        ALOS_PALSAR_MASK = "alos-palsar-mask"
        AUTUMN = "autumn"
        AUTUMN_R = "autumn_r"
        BINARY = "binary"
        BINARY_R = "binary_r"
        BLUES = "blues"
        BLUES_R = "blues_r"
        BONE = "bone"
        BONE_R = "bone_r"
        BRBG = "brbg"
        BRBG_R = "brbg_r"
        BRG = "brg"
        BRG_R = "brg_r"
        BUGN = "bugn"
        BUGN_R = "bugn_r"
        BUPU = "bupu"
        BUPU_R = "bupu_r"
        BWR = "bwr"
        BWR_R = "bwr_r"
        CFASTIE = "cfastie"
        CHESAPEAKE_LC13 = "chesapeake-lc-13"
        CHESAPEAKE_LC7 = "chesapeake-lc-7"
        CHESAPEAKE_LU = "chesapeake-lu"
        CHLORIS_BIOMASS = "chloris-biomass"
        CIVIDIS = "cividis"
        CIVIDIS_R = "cividis_r"
        CMRMAP = "cmrmap"
        CMRMAP_R = "cmrmap_r"
        COOL = "cool"
        COOLWARM = "coolwarm"
        COOLWARM_R = "coolwarm_r"
        COOL_R = "cool_r"
        COPPER = "copper"
        COPPER_R = "copper_r"
        CUBEHELIX = "cubehelix"
        CUBEHELIX_R = "cubehelix_r"
        C_CAP = "c-cap"
        DARK2 = "dark2"
        DARK2_R = "dark2_r"
        DRCOG_LULC = "drcog-lulc"
        ESA_CCI_LC = "esa-cci-lc"
        ESA_WORLDCOVER = "esa-worldcover"
        FLAG = "flag"
        FLAG_R = "flag_r"
        GAP_LULC = "gap-lulc"
        GIST_EARTH = "gist_earth"
        GIST_EARTH_R = "gist_earth_r"
        GIST_GRAY = "gist_gray"
        GIST_GRAY_R = "gist_gray_r"
        GIST_HEAT = "gist_heat"
        GIST_HEAT_R = "gist_heat_r"
        GIST_NCAR = "gist_ncar"
        GIST_NCAR_R = "gist_ncar_r"
        GIST_RAINBOW = "gist_rainbow"
        GIST_RAINBOW_R = "gist_rainbow_r"
        GIST_STERN = "gist_stern"
        GIST_STERN_R = "gist_stern_r"
        GIST_YARG = "gist_yarg"
        GIST_YARG_R = "gist_yarg_r"
        GNBU = "gnbu"
        GNBU_R = "gnbu_r"
        GNUPLOT = "gnuplot"
        GNUPLOT2 = "gnuplot2"
        GNUPLOT2_R = "gnuplot2_r"
        GNUPLOT_R = "gnuplot_r"
        GRAY = "gray"
        GRAY_R = "gray_r"
        GREENS = "greens"
        GREENS_R = "greens_r"
        GREYS = "greys"
        GREYS_R = "greys_r"
        HOT = "hot"
        HOT_R = "hot_r"
        HSV = "hsv"
        HSV_R = "hsv_r"
        INFERNO = "inferno"
        INFERNO_R = "inferno_r"
        IO_BII = "io-bii"
        IO_LULC = "io-lulc"
        IO_LULC9_CLASS = "io-lulc-9-class"
        JET = "jet"
        JET_R = "jet_r"
        JRC_CHANGE = "jrc-change"
        JRC_EXTENT = "jrc-extent"
        JRC_OCCURRENCE = "jrc-occurrence"
        JRC_RECURRENCE = "jrc-recurrence"
        JRC_SEASONALITY = "jrc-seasonality"
        JRC_TRANSITIONS = "jrc-transitions"
        LIDAR_CLASSIFICATION = "lidar-classification"
        LIDAR_HAG = "lidar-hag"
        LIDAR_HAG_ALTERNATIVE = "lidar-hag-alternative"
        LIDAR_INTENSITY = "lidar-intensity"
        LIDAR_RETURNS = "lidar-returns"
        MAGMA = "magma"
        MAGMA_R = "magma_r"
        MODIS10_A1 = "modis-10A1"
        MODIS10_A2 = "modis-10A2"
        MODIS13_A1_Q1 = "modis-13A1|Q1"
        MODIS14_A1_A2 = "modis-14A1|A2"
        MODIS15_A2_H_A3_H = "modis-15A2H|A3H"
        MODIS16_A3_GF_ET = "modis-16A3GF-ET"
        MODIS16_A3_GF_PET = "modis-16A3GF-PET"
        MODIS17_A2_H_A2_HGF = "modis-17A2H|A2HGF"
        MODIS17_A3_HGF = "modis-17A3HGF"
        MODIS64_A1 = "modis-64A1"
        MTBS_SEVERITY = "mtbs-severity"
        NIPY_SPECTRAL = "nipy_spectral"
        NIPY_SPECTRAL_R = "nipy_spectral_r"
        NRCAN_LULC = "nrcan-lulc"
        OCEAN = "ocean"
        OCEAN_R = "ocean_r"
        ORANGES = "oranges"
        ORANGES_R = "oranges_r"
        ORRD = "orrd"
        ORRD_R = "orrd_r"
        PAIRED = "paired"
        PAIRED_R = "paired_r"
        PASTEL1 = "pastel1"
        PASTEL1_R = "pastel1_r"
        PASTEL2 = "pastel2"
        PASTEL2_R = "pastel2_r"
        PINK = "pink"
        PINK_R = "pink_r"
        PIYG = "piyg"
        PIYG_R = "piyg_r"
        PLASMA = "plasma"
        PLASMA_R = "plasma_r"
        PRGN = "prgn"
        PRGN_R = "prgn_r"
        PRISM = "prism"
        PRISM_R = "prism_r"
        PUBU = "pubu"
        PUBUGN = "pubugn"
        PUBUGN_R = "pubugn_r"
        PUBU_R = "pubu_r"
        PUOR = "puor"
        PUOR_R = "puor_r"
        PURD = "purd"
        PURD_R = "purd_r"
        PURPLES = "purples"
        PURPLES_R = "purples_r"
        QPE = "qpe"
        RAINBOW = "rainbow"
        RAINBOW_R = "rainbow_r"
        RDBU = "rdbu"
        RDBU_R = "rdbu_r"
        RDGY = "rdgy"
        RDGY_R = "rdgy_r"
        RDPU = "rdpu"
        RDPU_R = "rdpu_r"
        RDYLBU = "rdylbu"
        RDYLBU_R = "rdylbu_r"
        RDYLGN = "rdylgn"
        RDYLGN_R = "rdylgn_r"
        REDS = "reds"
        REDS_R = "reds_r"
        RPLUMBO = "rplumbo"
        SCHWARZWALD = "schwarzwald"
        SEISMIC = "seismic"
        SEISMIC_R = "seismic_r"
        SET1 = "set1"
        SET1_R = "set1_r"
        SET2 = "set2"
        SET2_R = "set2_r"
        SET3 = "set3"
        SET3_R = "set3_r"
        SPECTRAL = "spectral"
        SPECTRAL_R = "spectral_r"
        SPRING = "spring"
        SPRING_R = "spring_r"
        SUMMER = "summer"
        SUMMER_R = "summer_r"
        TAB10 = "tab10"
        TAB10_R = "tab10_r"
        TAB20 = "tab20"
        TAB20_B = "tab20b"
        TAB20_B_R = "tab20b_r"
        TAB20_C = "tab20c"
        TAB20_C_R = "tab20c_r"
        TAB20_R = "tab20_r"
        TERRAIN = "terrain"
        TERRAIN_R = "terrain_r"
        TWILIGHT = "twilight"
        TWILIGHT_R = "twilight_r"
        TWILIGHT_SHIFTED = "twilight_shifted"
        TWILIGHT_SHIFTED_R = "twilight_shifted_r"
        USDA_CDL = "usda-cdl"
        USDA_CDL_CORN = "usda-cdl-corn"
        USDA_CDL_COTTON = "usda-cdl-cotton"
        USDA_CDL_SOYBEANS = "usda-cdl-soybeans"
        USDA_CDL_WHEAT = "usda-cdl-wheat"
        USGS_LCMAP = "usgs-lcmap"
        VIIRS10_A1 = "viirs-10a1"
        VIIRS13_A1 = "viirs-13a1"
        VIIRS14_A1 = "viirs-14a1"
        VIIRS15_A2_H = "viirs-15a2H"
        VIRIDIS = "viridis"
        VIRIDIS_R = "viridis_r"
        WINTER = "winter"
        WINTER_R = "winter_r"
        WISTIA = "wistia"
        WISTIA_R = "wistia_r"
        YLGN = "ylgn"
        YLGNBU = "ylgnbu"
        YLGNBU_R = "ylgnbu_r"
        YLGN_R = "ylgn_r"
        YLORBR = "ylorbr"
        YLORBR_R = "ylorbr_r"
        YLORRD = "ylorrd"
        YLORRD_R = "ylorrd_r"


    class azure.planetarycomputer.models.DefaultLocation(_Model):
        coordinates: list[float]
        zoom: int

        @overload
        def __init__(
                self, 
                *, 
                coordinates: list[float], 
                zoom: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.ErrorInfo(_Model):
        error: ODataV4Format

        @overload
        def __init__(
                self, 
                *, 
                error: ODataV4Format
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.Feature(_Model):
        geometry: Geometry
        properties: Optional[dict[str, Any]]
        type: Union[str, FeatureType]

        @overload
        def __init__(
                self, 
                *, 
                geometry: Geometry, 
                properties: Optional[dict[str, Any]] = ..., 
                type: Union[str, FeatureType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.FeatureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEATURE = "Feature"


    class azure.planetarycomputer.models.FilterLanguage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CQL2_JSON = "cql2-json"
        CQL2_TEXT = "cql2-text"
        CQL_JSON = "cql-json"


    class azure.planetarycomputer.models.Geometry(_Model):
        bounding_box: Optional[list[float]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.GeometryType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINE_STRING = "LineString"
        MULTI_LINE_STRING = "MultiLineString"
        MULTI_POINT = "MultiPoint"
        MULTI_POLYGON = "MultiPolygon"
        POINT = "Point"
        POLYGON = "Polygon"


    class azure.planetarycomputer.models.ImageParameters(_Model):
        columns: int
        cql: dict[str, Any]
        geometry: Optional[Geometry]
        image_size: Optional[str]
        render_parameters: str
        rows: int
        show_branding: Optional[bool]
        zoom: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                columns: int, 
                cql: dict[str, Any], 
                geometry: Optional[Geometry] = ..., 
                image_size: Optional[str] = ..., 
                render_parameters: str, 
                rows: int, 
                show_branding: Optional[bool] = ..., 
                zoom: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.ImageResponse(_Model):
        url: str

        @overload
        def __init__(
                self, 
                *, 
                url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionDefinition(_Model):
        creation_time: datetime
        display_name: Optional[str]
        id: str
        import_type: Union[str, IngestionType]
        keep_original_assets: Optional[bool]
        skip_existing_items: Optional[bool]
        source_catalog_url: Optional[str]
        status: Union[str, IngestionStatus]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                import_type: Union[str, IngestionType], 
                keep_original_assets: Optional[bool] = ..., 
                skip_existing_items: Optional[bool] = ..., 
                source_catalog_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionRun(_Model):
        creation_time: datetime
        id: str
        keep_original_assets: Optional[bool]
        operation: IngestionRunOperation
        parent_run_id: Optional[str]
        skip_existing_items: Optional[bool]
        source_catalog_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_time: datetime, 
                id: str, 
                keep_original_assets: Optional[bool] = ..., 
                operation: IngestionRunOperation, 
                parent_run_id: Optional[str] = ..., 
                skip_existing_items: Optional[bool] = ..., 
                source_catalog_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionRunOperation(_Model):
        creation_time: datetime
        finish_time: Optional[datetime]
        id: str
        start_time: Optional[datetime]
        status: Union[str, OperationStatus]
        status_history: list[OperationStatusHistoryItem]
        total_failed_items: int
        total_items: int
        total_pending_items: int
        total_successful_items: int

        @overload
        def __init__(
                self, 
                *, 
                creation_time: datetime, 
                finish_time: Optional[datetime] = ..., 
                id: str, 
                start_time: Optional[datetime] = ..., 
                status: Union[str, OperationStatus], 
                status_history: list[OperationStatusHistoryItem], 
                total_failed_items: int, 
                total_items: int, 
                total_pending_items: int, 
                total_successful_items: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionSource(_Model):
        created: Optional[datetime]
        id: str
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionSourceSummary(_Model):
        created: Optional[datetime]
        id: str
        kind: Union[str, IngestionSourceType]

        @overload
        def __init__(
                self, 
                *, 
                created: Optional[datetime] = ..., 
                id: str, 
                kind: Union[str, IngestionSourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.IngestionSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_MANAGED_IDENTITY = "BlobManagedIdentity"
        SHARED_ACCESS_SIGNATURE_TOKEN = "SasToken"


    class azure.planetarycomputer.models.IngestionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        READY = "Ready"


    class azure.planetarycomputer.models.IngestionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STATIC_CATALOG = "StaticCatalog"


    class azure.planetarycomputer.models.LegendConfigType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSMAP = "classmap"
        CONTINUOUS = "continuous"
        INTERVAL = "interval"
        NONE = "none"


    class azure.planetarycomputer.models.LineString(Geometry, discriminator='LineString'):
        bounding_box: list[float]
        coordinates: list[list[float]]
        type: Literal[GeometryType.LINE_STRING]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[list[float]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.ManagedIdentityConnection(_Model):
        container_uri: str
        object_id: str

        @overload
        def __init__(
                self, 
                *, 
                container_uri: str, 
                object_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.ManagedIdentityIngestionSource(IngestionSource, discriminator='BlobManagedIdentity'):
        connection_info: ManagedIdentityConnection
        created: datetime
        id: str
        kind: Literal[IngestionSourceType.BLOB_MANAGED_IDENTITY]

        @overload
        def __init__(
                self, 
                *, 
                connection_info: ManagedIdentityConnection, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.ManagedIdentityMetadata(_Model):
        object_id: str
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                object_id: str, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.MosaicMetadata(_Model):
        assets: Optional[list[str]]
        bounds: Optional[str]
        defaults: Optional[dict[str, str]]
        max_zoom: Optional[int]
        min_zoom: Optional[int]
        name: Optional[str]
        type: Optional[Union[str, MosaicMetadataType]]

        @overload
        def __init__(
                self, 
                *, 
                assets: Optional[list[str]] = ..., 
                bounds: Optional[str] = ..., 
                defaults: Optional[dict[str, str]] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                name: Optional[str] = ..., 
                type: Optional[Union[str, MosaicMetadataType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.MosaicMetadataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MOSAIC = "mosaic"
        SEARCH = "search"


    class azure.planetarycomputer.models.MultiLineString(Geometry, discriminator='MultiLineString'):
        bounding_box: list[float]
        coordinates: list[list[list[float]]]
        type: Literal[GeometryType.MULTI_LINE_STRING]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[list[list[float]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.MultiPoint(Geometry, discriminator='MultiPoint'):
        bounding_box: list[float]
        coordinates: list[list[float]]
        type: Literal[GeometryType.MULTI_POINT]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[list[float]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.MultiPolygon(Geometry, discriminator='MultiPolygon'):
        bounding_box: list[float]
        coordinates: list[list[list[list[float]]]]
        type: Literal[GeometryType.MULTI_POLYGON]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[list[list[list[float]]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.NoDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALPHA = "Alpha"
        INTERNAL = "Internal"
        MASK = "Mask"
        NODATA = "Nodata"
        NONE = "None"


    class azure.planetarycomputer.models.Operation(_Model):
        additional_information: Optional[dict[str, str]]
        collection_id: Optional[str]
        creation_time: datetime
        error: Optional[ErrorInfo]
        finish_time: Optional[datetime]
        id: str
        start_time: Optional[datetime]
        status: Union[str, OperationStatus]
        status_history: list[OperationStatusHistoryItem]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                additional_information: Optional[dict[str, str]] = ..., 
                collection_id: Optional[str] = ..., 
                creation_time: datetime, 
                error: Optional[ErrorInfo] = ..., 
                finish_time: Optional[datetime] = ..., 
                id: str, 
                start_time: Optional[datetime] = ..., 
                status: Union[str, OperationStatus], 
                status_history: list[OperationStatusHistoryItem], 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELING = "Canceling"
        FAILED = "Failed"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.planetarycomputer.models.OperationStatusHistoryItem(_Model):
        error_code: Optional[str]
        error_message: Optional[str]
        status: Union[str, OperationStatus]
        timestamp: datetime

        @overload
        def __init__(
                self, 
                *, 
                error_code: Optional[str] = ..., 
                error_message: Optional[str] = ..., 
                status: Union[str, OperationStatus], 
                timestamp: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.PartitionType(_Model):
        scheme: Optional[Union[str, PartitionTypeScheme]]

        @overload
        def __init__(
                self, 
                *, 
                scheme: Optional[Union[str, PartitionTypeScheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.PartitionTypeScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTH = "month"
        NONE = "none"
        YEAR = "year"


    class azure.planetarycomputer.models.PixelSelection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIRST = "first"
        HIGHEST = "highest"
        LAST_BAND_HIGH = "lastbandhigh"
        LAST_BAND_LOW = "lastbandlow"
        LOWEST = "lowest"
        MEAN = "mean"
        MEDIAN = "median"
        STANDARD_DEVIATION = "stdev"


    class azure.planetarycomputer.models.Point(Geometry, discriminator='Point'):
        bounding_box: list[float]
        coordinates: list[float]
        type: Literal[GeometryType.POINT]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[float]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.Polygon(Geometry, discriminator='Polygon'):
        bounding_box: list[float]
        coordinates: list[list[list[float]]]
        type: Literal[GeometryType.POLYGON]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                coordinates: list[list[list[float]]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.QueryableDefinitionsResponse(_Model):


    class azure.planetarycomputer.models.RenderOption(_Model):
        conditions: Optional[list[RenderOptionCondition]]
        description: Optional[str]
        id: str
        legend: Optional[RenderOptionLegend]
        min_zoom: Optional[int]
        name: str
        options: Optional[str]
        type: Optional[Union[str, RenderOptionType]]
        vector_options: Optional[RenderOptionVectorOptions]

        @overload
        def __init__(
                self, 
                *, 
                conditions: Optional[list[RenderOptionCondition]] = ..., 
                description: Optional[str] = ..., 
                id: str, 
                legend: Optional[RenderOptionLegend] = ..., 
                min_zoom: Optional[int] = ..., 
                name: str, 
                options: Optional[str] = ..., 
                type: Optional[Union[str, RenderOptionType]] = ..., 
                vector_options: Optional[RenderOptionVectorOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.RenderOptionCondition(_Model):
        property: str
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                property: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.RenderOptionLegend(_Model):
        labels: Optional[list[str]]
        scale_factor: Optional[float]
        trim_end: Optional[int]
        trim_start: Optional[int]
        type: Optional[Union[str, LegendConfigType]]

        @overload
        def __init__(
                self, 
                *, 
                labels: Optional[list[str]] = ..., 
                scale_factor: Optional[float] = ..., 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                type: Optional[Union[str, LegendConfigType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.RenderOptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RASTER_TILE = "raster-tile"
        VT_LINE = "vt-line"
        VT_POLYGON = "vt-polygon"


    class azure.planetarycomputer.models.RenderOptionVectorOptions(_Model):
        fill_color: Optional[str]
        filter: Optional[list[str]]
        source_layer: str
        stroke_color: Optional[str]
        stroke_width: Optional[int]
        tilejson_key: str

        @overload
        def __init__(
                self, 
                *, 
                fill_color: Optional[str] = ..., 
                filter: Optional[list[str]] = ..., 
                source_layer: str, 
                stroke_color: Optional[str] = ..., 
                stroke_width: Optional[int] = ..., 
                tilejson_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.Resampling(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVERAGE = "average"
        BILINEAR = "bilinear"
        CUBIC = "cubic"
        CUBIC_SPLINE = "cubic_spline"
        GAUSS = "gauss"
        LANCZOS = "lanczos"
        MODE = "mode"
        NEAREST = "nearest"
        RMS = "rms"


    class azure.planetarycomputer.models.SearchOptionsFields(_Model):
        exclude: Optional[list[str]]
        include: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                exclude: Optional[list[str]] = ..., 
                include: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.SharedAccessSignatureSignedLink(_Model):
        expires_on: Optional[datetime]
        href: str

        @overload
        def __init__(
                self, 
                *, 
                expires_on: Optional[datetime] = ..., 
                href: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.SharedAccessSignatureToken(_Model):
        expires_on: datetime
        token: str

        @overload
        def __init__(
                self, 
                *, 
                expires_on: datetime, 
                token: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.SharedAccessSignatureTokenConnection(_Model):
        container_uri: str
        expiration: Optional[datetime]
        shared_access_signature_token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                container_uri: str, 
                shared_access_signature_token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.SharedAccessSignatureTokenIngestionSource(IngestionSource, discriminator='SasToken'):
        connection_info: SharedAccessSignatureTokenConnection
        created: datetime
        id: str
        kind: Literal[IngestionSourceType.SHARED_ACCESS_SIGNATURE_TOKEN]

        @overload
        def __init__(
                self, 
                *, 
                connection_info: SharedAccessSignatureTokenConnection, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacAsset(_Model):
        constellation: Optional[str]
        created: Optional[datetime]
        description: Optional[str]
        gsd: Optional[float]
        href: str
        instruments: Optional[list[str]]
        mission: Optional[str]
        platform: Optional[str]
        providers: Optional[list[StacProvider]]
        roles: Optional[list[str]]
        title: Optional[str]
        type: Optional[str]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                constellation: Optional[str] = ..., 
                created: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                gsd: Optional[float] = ..., 
                href: str, 
                instruments: Optional[list[str]] = ..., 
                mission: Optional[str] = ..., 
                platform: Optional[str] = ..., 
                providers: Optional[list[StacProvider]] = ..., 
                roles: Optional[list[str]] = ..., 
                title: Optional[str] = ..., 
                type: Optional[str] = ..., 
                updated: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacAssetData(_Model):
        data: AssetMetadata
        file: Union[str, bytes, IO[str], IO[bytes], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]]], tuple[Optional[str], Union[str, bytes, IO[str], IO[bytes]], Optional[str]]]

        @overload
        def __init__(
                self, 
                *, 
                data: AssetMetadata, 
                file: FileType
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacAssetUrlSigningMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.planetarycomputer.models.StacCatalogCollections(_Model):
        collections: list[StacCollection]
        links: list[StacLink]

        @overload
        def __init__(
                self, 
                *, 
                collections: list[StacCollection], 
                links: list[StacLink]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacCollection(_Model):
        assets: Optional[dict[str, StacAsset]]
        created_on: Optional[datetime]
        description: str
        extent: StacExtensionExtent
        id: str
        item_assets: Optional[dict[str, StacItemAsset]]
        keywords: Optional[list[str]]
        license: str
        links: list[StacLink]
        providers: Optional[list[StacProvider]]
        short_description: Optional[str]
        stac_extensions: Optional[list[str]]
        stac_version: Optional[str]
        summaries: Optional[dict[str, Any]]
        title: Optional[str]
        type: Optional[str]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                assets: Optional[dict[str, StacAsset]] = ..., 
                created_on: Optional[datetime] = ..., 
                description: str, 
                extent: StacExtensionExtent, 
                id: str, 
                item_assets: Optional[dict[str, StacItemAsset]] = ..., 
                keywords: Optional[list[str]] = ..., 
                license: str, 
                links: list[StacLink], 
                providers: Optional[list[StacProvider]] = ..., 
                short_description: Optional[str] = ..., 
                stac_extensions: Optional[list[str]] = ..., 
                stac_version: Optional[str] = ..., 
                summaries: Optional[dict[str, Any]] = ..., 
                title: Optional[str] = ..., 
                type: Optional[str] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacCollectionTemporalExtent(_Model):
        interval: list[list[datetime]]

        @overload
        def __init__(
                self, 
                *, 
                interval: list[list[datetime]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacConformanceClasses(_Model):
        conforms_to: list[str]

        @overload
        def __init__(
                self, 
                *, 
                conforms_to: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacContextExtension(_Model):
        limit: Optional[int]
        matched: Optional[int]
        returned: int

        @overload
        def __init__(
                self, 
                *, 
                limit: Optional[int] = ..., 
                matched: Optional[int] = ..., 
                returned: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacExtensionExtent(_Model):
        spatial: StacExtensionSpatialExtent
        temporal: StacCollectionTemporalExtent

        @overload
        def __init__(
                self, 
                *, 
                spatial: StacExtensionSpatialExtent, 
                temporal: StacCollectionTemporalExtent
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacExtensionSpatialExtent(_Model):
        bounding_box: Optional[list[list[float]]]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[list[float]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItem(StacItemOrStacItemCollection, discriminator='Feature'):
        assets: dict[str, StacAsset]
        bounding_box: list[float]
        collection: Optional[str]
        created_on: datetime
        e_tag: Optional[str]
        geometry: Geometry
        id: str
        links: list[StacLink]
        properties: StacItemProperties
        short_description: str
        stac_extensions: list[str]
        stac_version: str
        timestamp: Optional[datetime]
        type: Literal[StacModelType.FEATURE]
        updated_on: datetime

        @overload
        def __init__(
                self, 
                *, 
                assets: dict[str, StacAsset], 
                bounding_box: list[float], 
                collection: Optional[str] = ..., 
                created_on: Optional[datetime] = ..., 
                e_tag: Optional[str] = ..., 
                geometry: Geometry, 
                id: str, 
                links: Optional[list[StacLink]] = ..., 
                properties: StacItemProperties, 
                short_description: Optional[str] = ..., 
                stac_extensions: Optional[list[str]] = ..., 
                stac_version: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemAsset(_Model):
        constellation: Optional[str]
        created: Optional[datetime]
        description: Optional[str]
        gsd: Optional[float]
        href: Optional[str]
        instruments: Optional[list[str]]
        mission: Optional[str]
        platform: Optional[str]
        providers: Optional[list[StacProvider]]
        roles: Optional[list[str]]
        title: str
        type: str
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                constellation: Optional[str] = ..., 
                created: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                gsd: Optional[float] = ..., 
                href: Optional[str] = ..., 
                instruments: Optional[list[str]] = ..., 
                mission: Optional[str] = ..., 
                platform: Optional[str] = ..., 
                providers: Optional[list[StacProvider]] = ..., 
                roles: Optional[list[str]] = ..., 
                title: str, 
                type: str, 
                updated: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemBounds(_Model):
        bounds: list[float]

        @overload
        def __init__(
                self, 
                *, 
                bounds: list[float]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemCollection(StacItemOrStacItemCollection, discriminator='FeatureCollection'):
        bounding_box: Optional[list[float]]
        context: Optional[StacContextExtension]
        created_on: datetime
        features: list[StacItem]
        links: list[StacLink]
        short_description: str
        stac_extensions: list[str]
        stac_version: str
        type: Literal[StacModelType.FEATURE_COLLECTION]
        updated_on: datetime

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                context: Optional[StacContextExtension] = ..., 
                created_on: Optional[datetime] = ..., 
                features: list[StacItem], 
                links: Optional[list[StacLink]] = ..., 
                short_description: Optional[str] = ..., 
                stac_extensions: Optional[list[str]] = ..., 
                stac_version: Optional[str] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemOrStacItemCollection(_Model):
        created_on: Optional[datetime]
        links: Optional[list[StacLink]]
        short_description: Optional[str]
        stac_extensions: Optional[list[str]]
        stac_version: Optional[str]
        type: str
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                created_on: Optional[datetime] = ..., 
                links: Optional[list[StacLink]] = ..., 
                short_description: Optional[str] = ..., 
                stac_extensions: Optional[list[str]] = ..., 
                stac_version: Optional[str] = ..., 
                type: str, 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemPointAsset(_Model):
        assets: dict[str, StacAsset]
        bounding_box: list[float]
        collection_id: str
        id: str

        @overload
        def __init__(
                self, 
                *, 
                assets: dict[str, StacAsset], 
                bounding_box: list[float], 
                collection_id: str, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemProperties(_Model):
        constellation: Optional[str]
        created: Optional[datetime]
        date_time: str
        description: Optional[str]
        end_datetime: Optional[datetime]
        gsd: Optional[float]
        instruments: Optional[list[str]]
        mission: Optional[str]
        platform: Optional[str]
        providers: Optional[list[StacProvider]]
        start_datetime: Optional[datetime]
        title: Optional[str]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                constellation: Optional[str] = ..., 
                created: Optional[datetime] = ..., 
                date_time: str, 
                description: Optional[str] = ..., 
                end_datetime: Optional[datetime] = ..., 
                gsd: Optional[float] = ..., 
                instruments: Optional[list[str]] = ..., 
                mission: Optional[str] = ..., 
                platform: Optional[str] = ..., 
                providers: Optional[list[StacProvider]] = ..., 
                start_datetime: Optional[datetime] = ..., 
                title: Optional[str] = ..., 
                updated: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemStatisticsGeoJson(_Model):
        geometry: Geometry
        properties: Optional[StacItemStatisticsGeoJsonProperties]
        type: Union[str, FeatureType]

        @overload
        def __init__(
                self, 
                *, 
                geometry: Geometry, 
                properties: Optional[StacItemStatisticsGeoJsonProperties] = ..., 
                type: Union[str, FeatureType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacItemStatisticsGeoJsonProperties(_Model):
        statistics: dict[str, BandStatistics]

        @overload
        def __init__(
                self, 
                *, 
                statistics: dict[str, BandStatistics]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacLandingPage(_Model):
        conforms_to: list[str]
        created_on: Optional[datetime]
        description: str
        id: str
        links: list[StacLink]
        short_description: Optional[str]
        stac_extensions: Optional[list[str]]
        stac_version: Optional[str]
        title: Optional[str]
        type: Optional[str]
        updated_on: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                conforms_to: list[str], 
                created_on: Optional[datetime] = ..., 
                description: str, 
                id: str, 
                links: list[StacLink], 
                short_description: Optional[str] = ..., 
                stac_extensions: Optional[list[str]] = ..., 
                stac_version: Optional[str] = ..., 
                title: Optional[str] = ..., 
                type: Optional[str] = ..., 
                updated_on: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacLink(_Model):
        body: Optional[dict[str, Any]]
        headers: Optional[dict[str, str]]
        href: str
        hreflang: Optional[str]
        length: Optional[int]
        merge: Optional[bool]
        method: Optional[Union[Literal["GET"], Literal["POST"], str]]
        rel: Optional[str]
        title: Optional[str]
        type: Optional[Union[str, StacLinkType]]

        @overload
        def __init__(
                self, 
                *, 
                body: Optional[dict[str, Any]] = ..., 
                headers: Optional[dict[str, str]] = ..., 
                href: str, 
                hreflang: Optional[str] = ..., 
                length: Optional[int] = ..., 
                merge: Optional[bool] = ..., 
                method: Optional[Union[Literal[GET], Literal[POST], str]] = ..., 
                rel: Optional[str] = ..., 
                title: Optional[str] = ..., 
                type: Optional[Union[str, StacLinkType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacLinkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION_GEO_JSON = "application/geo+json"
        APPLICATION_JSON = "application/json"
        APPLICATION_XML = "application/xml"
        APPLICATION_X_BINARY = "application/x-binary"
        APPLICATION_X_PROTOBUF = "application/x-protobuf"
        IMAGE_JP2 = "image/jp2"
        IMAGE_JPEG = "image/jpeg"
        IMAGE_JPG = "image/jpg"
        IMAGE_PNG = "image/png"
        IMAGE_TIFF_APPLICATION_GEOTIFF = "image/tiff; application=geotiff"
        IMAGE_WEBP = "image/webp"
        TEXT_HTML = "text/html"
        TEXT_PLAIN = "text/plain"


    class azure.planetarycomputer.models.StacModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEATURE = "Feature"
        FEATURE_COLLECTION = "FeatureCollection"


    class azure.planetarycomputer.models.StacMosaic(_Model):
        cql: list[dict[str, Any]]
        description: Optional[str]
        id: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                cql: list[dict[str, Any]], 
                description: Optional[str] = ..., 
                id: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacMosaicConfiguration(_Model):
        default_custom_query: Optional[dict[str, Any]]
        default_location: Optional[DefaultLocation]
        mosaics: list[StacMosaic]
        render_options: list[RenderOption]

        @overload
        def __init__(
                self, 
                *, 
                default_custom_query: Optional[dict[str, Any]] = ..., 
                default_location: Optional[DefaultLocation] = ..., 
                mosaics: list[StacMosaic], 
                render_options: list[RenderOption]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacProvider(_Model):
        description: Optional[str]
        name: str
        roles: Optional[list[str]]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str, 
                roles: Optional[list[str]] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacQueryable(_Model):
        create_index: Optional[bool]
        data_type: Optional[Union[str, StacQueryableDefinitionDataType]]
        definition: dict[str, Any]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                create_index: Optional[bool] = ..., 
                data_type: Optional[Union[str, StacQueryableDefinitionDataType]] = ..., 
                definition: dict[str, Any], 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacQueryableDefinitionDataType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        DATE = "date"
        NUMBER = "number"
        STRING = "string"
        TIMESTAMP = "timestamp"


    class azure.planetarycomputer.models.StacSearchParameters(_Model):
        bounding_box: Optional[list[float]]
        collections: Optional[list[str]]
        conformance_class: Optional[dict[str, Any]]
        date_time: Optional[str]
        fields: Optional[list[SearchOptionsFields]]
        filter: Optional[dict[str, Any]]
        filter_coordinate_reference_system: Optional[str]
        filter_lang: Optional[Union[str, FilterLanguage]]
        ids: Optional[list[str]]
        intersects: Optional[Geometry]
        limit: Optional[int]
        query: Optional[dict[str, Any]]
        sort_by: Optional[list[StacSortExtension]]
        token: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[list[float]] = ..., 
                collections: Optional[list[str]] = ..., 
                conformance_class: Optional[dict[str, Any]] = ..., 
                date_time: Optional[str] = ..., 
                fields: Optional[list[SearchOptionsFields]] = ..., 
                filter: Optional[dict[str, Any]] = ..., 
                filter_coordinate_reference_system: Optional[str] = ..., 
                filter_lang: Optional[Union[str, FilterLanguage]] = ..., 
                ids: Optional[list[str]] = ..., 
                intersects: Optional[Geometry] = ..., 
                limit: Optional[int] = ..., 
                query: Optional[dict[str, Any]] = ..., 
                sort_by: Optional[list[StacSortExtension]] = ..., 
                token: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.StacSearchSortingDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASC = "asc"
        DESC = "desc"


    class azure.planetarycomputer.models.StacSortExtension(_Model):
        direction: Union[str, StacSearchSortingDirection]
        field: str

        @overload
        def __init__(
                self, 
                *, 
                direction: Union[str, StacSearchSortingDirection], 
                field: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TerrainAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTOURS = "contours"
        HILLSHADE = "hillshade"
        NORMALIZED_INDEX = "normalizedIndex"
        TERRAINRGB = "terrainrgb"
        TERRARIUM = "terrarium"


    class azure.planetarycomputer.models.TileAddressingScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TMS = "tms"
        XYZ = "xyz"


    class azure.planetarycomputer.models.TileJsonMetadata(_Model):
        attribution: Optional[str]
        bounds: Optional[list[float]]
        center: Optional[list[float]]
        data: Optional[list[str]]
        description: Optional[str]
        grids: Optional[list[str]]
        legend: Optional[str]
        max_zoom: Optional[int]
        min_zoom: Optional[int]
        name: Optional[str]
        scheme: Optional[Union[str, TileAddressingScheme]]
        template: Optional[str]
        tile_json: Optional[str]
        tiles: list[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attribution: Optional[str] = ..., 
                bounds: Optional[list[float]] = ..., 
                center: Optional[list[float]] = ..., 
                data: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                grids: Optional[list[str]] = ..., 
                legend: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                name: Optional[str] = ..., 
                scheme: Optional[Union[str, TileAddressingScheme]] = ..., 
                template: Optional[str] = ..., 
                tile_json: Optional[str] = ..., 
                tiles: list[str], 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TileMatrix(_Model):
        cell_size: float
        corner_of_origin: Optional[Union[str, TileMatrixCornerOfOrigin]]
        description: Optional[str]
        id: str
        keywords: Optional[list[str]]
        matrix_height: int
        matrix_width: int
        point_of_origin: list[float]
        scale_denominator: float
        tile_height: int
        tile_width: int
        title: Optional[str]
        variable_matrix_widths: Optional[list[VariableMatrixWidth]]

        @overload
        def __init__(
                self, 
                *, 
                cell_size: float, 
                corner_of_origin: Optional[Union[str, TileMatrixCornerOfOrigin]] = ..., 
                description: Optional[str] = ..., 
                id: str, 
                keywords: Optional[list[str]] = ..., 
                matrix_height: int, 
                matrix_width: int, 
                point_of_origin: list[float], 
                scale_denominator: float, 
                tile_height: int, 
                tile_width: int, 
                title: Optional[str] = ..., 
                variable_matrix_widths: Optional[list[VariableMatrixWidth]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TileMatrixCornerOfOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOTTOM_LEFT = "bottomLeft"
        TOP_LEFT = "topLeft"


    class azure.planetarycomputer.models.TileMatrixSet(_Model):
        bounding_box: Optional[TileMatrixSetBoundingBox]
        crs: str
        description: Optional[str]
        id: Optional[str]
        keywords: Optional[list[str]]
        ordered_axes: Optional[list[str]]
        tile_matrices: list[TileMatrix]
        title: Optional[str]
        uri: Optional[str]
        well_known_scale_set: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[TileMatrixSetBoundingBox] = ..., 
                crs: str, 
                description: Optional[str] = ..., 
                id: Optional[str] = ..., 
                keywords: Optional[list[str]] = ..., 
                ordered_axes: Optional[list[str]] = ..., 
                tile_matrices: list[TileMatrix], 
                title: Optional[str] = ..., 
                uri: Optional[str] = ..., 
                well_known_scale_set: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TileMatrixSetBoundingBox(_Model):
        crs: Optional[str]
        lower_left: list[str]
        ordered_axes: Optional[list[str]]
        upper_right: list[str]

        @overload
        def __init__(
                self, 
                *, 
                crs: Optional[str] = ..., 
                lower_left: list[str], 
                ordered_axes: Optional[list[str]] = ..., 
                upper_right: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TileSettings(_Model):
        default_location: Optional[DefaultLocation]
        max_items_per_tile: int
        min_zoom: int

        @overload
        def __init__(
                self, 
                *, 
                default_location: Optional[DefaultLocation] = ..., 
                max_items_per_tile: int, 
                min_zoom: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerAssetGeoJson(_Model):
        assets: dict[str, StacAsset]
        bounding_box: list[float]
        collection: Optional[str]
        id: str

        @overload
        def __init__(
                self, 
                *, 
                assets: dict[str, StacAsset], 
                bounding_box: list[float], 
                collection: Optional[str] = ..., 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerCoreModelsResponsesPoint(_Model):
        band_names: list[str]
        coordinates: list[float]
        values_property: list[float]

        @overload
        def __init__(
                self, 
                *, 
                band_names: list[str], 
                coordinates: list[float], 
                values_property: list[float]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerImageFormat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        JP2 = "jp2"
        JPEG = "jpeg"
        JPG = "jpg"
        NPY = "npy"
        PNG = "png"
        PNGRAW = "pngraw"
        TIF = "tif"
        WEBP = "webp"


    class azure.planetarycomputer.models.TilerInfo(_Model):
        band_descriptions: Optional[list[list[str]]]
        band_metadata: Optional[list[list[BandMetadataElement]]]
        bounds: list[float]
        color_interpretation: Optional[list[str]]
        colormap: Optional[dict[str, list[str]]]
        coordinate_reference_system: Optional[str]
        count: Optional[int]
        driver: Optional[str]
        dtype: str
        height: Optional[int]
        max_zoom: Optional[int]
        min_zoom: Optional[int]
        no_data_type: Optional[Union[str, NoDataType]]
        offsets: Optional[list[int]]
        overviews: Optional[list[int]]
        scales: Optional[list[int]]
        width: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                band_descriptions: Optional[list[list[str]]] = ..., 
                band_metadata: Optional[list[list[BandMetadataElement]]] = ..., 
                bounds: list[float], 
                color_interpretation: Optional[list[str]] = ..., 
                colormap: Optional[dict[str, list[str]]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                count: Optional[int] = ..., 
                driver: Optional[str] = ..., 
                dtype: str, 
                height: Optional[int] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data_type: Optional[Union[str, NoDataType]] = ..., 
                offsets: Optional[list[int]] = ..., 
                overviews: Optional[list[int]] = ..., 
                scales: Optional[list[int]] = ..., 
                width: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerInfoGeoJsonFeature(_Model):
        bounding_box: Optional[float]
        geometry: Geometry
        id: Optional[str]
        properties: dict[str, TilerInfo]
        type: Union[str, FeatureType]

        @overload
        def __init__(
                self, 
                *, 
                bounding_box: Optional[float] = ..., 
                geometry: Geometry, 
                id: Optional[str] = ..., 
                properties: dict[str, TilerInfo], 
                type: Union[str, FeatureType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerInfoMapResponse(_Model):


    class azure.planetarycomputer.models.TilerMosaicSearchRegistrationResponse(_Model):
        links: Optional[list[StacLink]]
        search_id: str

        @overload
        def __init__(
                self, 
                *, 
                links: Optional[list[StacLink]] = ..., 
                search_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerStacItemStatistics(_Model):


    class azure.planetarycomputer.models.TilerStacSearchDefinition(_Model):
        hash: str
        last_used: datetime
        metadata: MosaicMetadata
        order_by: str
        search: dict[str, Any]
        use_count: int
        where: str

        @overload
        def __init__(
                self, 
                *, 
                hash: str, 
                last_used: datetime, 
                metadata: MosaicMetadata, 
                order_by: str, 
                search: dict[str, Any], 
                use_count: int, 
                where: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.TilerStacSearchRegistration(_Model):
        links: Optional[list[StacLink]]
        search: TilerStacSearchDefinition

        @overload
        def __init__(
                self, 
                *, 
                links: Optional[list[StacLink]] = ..., 
                search: TilerStacSearchDefinition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.UserCollectionSettings(_Model):
        mosaic_configuration: StacMosaicConfiguration
        tile_settings: TileSettings

        @overload
        def __init__(
                self, 
                *, 
                mosaic_configuration: StacMosaicConfiguration, 
                tile_settings: TileSettings
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.planetarycomputer.models.VariableMatrixWidth(_Model):
        coalesce: int
        max_tile_row: int
        min_tile_row: int

        @overload
        def __init__(
                self, 
                *, 
                coalesce: int, 
                max_tile_row: int, 
                min_tile_row: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.planetarycomputer.operations

    class azure.planetarycomputer.operations.DataOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_static_image(
                self, 
                collection_id: str, 
                body: ImageParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        def create_static_image(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        def create_static_image(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ImageResponse: ...

        @overload
        def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: Feature, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: JSON, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def crop_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                body: IO[bytes], 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: Feature, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: JSON, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @overload
        def crop_geo_json_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                width: int, 
                height: int, 
                format: str, 
                body: IO[bytes], 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_asset_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AssetStatisticsResponse: ...

        @distributed_trace
        def get_bounds(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> StacItemBounds: ...

        @distributed_trace
        def get_class_map_legend(
                self, 
                classmap_name: str, 
                *, 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                **kwargs: Any
            ) -> ClassMapLegendResponse: ...

        @overload
        def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: Feature, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @overload
        def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @overload
        def get_geo_json_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> StacItemStatisticsGeoJson: ...

        @distributed_trace
        def get_info_geo_json(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                assets: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> TilerInfoGeoJsonFeature: ...

        @distributed_trace
        def get_interval_legend(
                self, 
                classmap_name: str, 
                *, 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[List[List[int]]]: ...

        @distributed_trace
        def get_item_asset_details(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                assets: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> TilerInfoMapResponse: ...

        @distributed_trace
        def get_legend(
                self, 
                color_map_name: str, 
                *, 
                height: Optional[float] = ..., 
                trim_end: Optional[int] = ..., 
                trim_start: Optional[int] = ..., 
                width: Optional[float] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_mosaics_assets_for_point(
                self, 
                search_id: str, 
                longitude: float, 
                latitude: float, 
                *, 
                coordinate_reference_system: Optional[str] = ..., 
                exit_when_full: Optional[bool] = ..., 
                items_limit: Optional[int] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[StacItemPointAsset]: ...

        @distributed_trace
        def get_mosaics_assets_for_tile(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                *, 
                collection_id: str, 
                exit_when_full: Optional[bool] = ..., 
                items_limit: Optional[int] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> List[TilerAssetGeoJson]: ...

        @distributed_trace
        def get_mosaics_search_info(
                self, 
                search_id: str, 
                **kwargs: Any
            ) -> TilerStacSearchRegistration: ...

        @distributed_trace
        def get_mosaics_tile(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                scale: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                collection: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                exit_when_full: Optional[bool] = ..., 
                expression: Optional[str] = ..., 
                items_limit: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                pixel_selection: Optional[Union[str, PixelSelection]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                time_limit: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_mosaics_tile_json(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                collection: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                exit_when_full: Optional[bool] = ..., 
                expression: Optional[str] = ..., 
                items_limit: Optional[int] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                pixel_selection: Optional[Union[str, PixelSelection]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                scan_limit: Optional[int] = ..., 
                skip_covered: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                time_limit: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TileJsonMetadata: ...

        @distributed_trace
        def get_mosaics_wmts_capabilities(
                self, 
                search_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_part(
                self, 
                collection_id: str, 
                item_id: str, 
                minx: float, 
                miny: float, 
                maxx: float, 
                maxy: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_part_with_dimensions(
                self, 
                collection_id: str, 
                item_id: str, 
                minx: float, 
                miny: float, 
                maxx: float, 
                maxy: float, 
                width: int, 
                height: int, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_point(
                self, 
                collection_id: str, 
                item_id: str, 
                longitude: float, 
                latitude: float, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                coordinate_reference_system: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TilerCoreModelsResponsesPoint: ...

        @distributed_trace
        def get_preview(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                format: Optional[Union[str, TilerImageFormat]] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_preview_with_format(
                self, 
                collection_id: str, 
                item_id: str, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                dst_crs: Optional[str] = ..., 
                expression: Optional[str] = ..., 
                height: Optional[int] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                unscale: Optional[bool] = ..., 
                width: Optional[int] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_static_image(
                self, 
                collection_id: str, 
                id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_tile(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                z: float, 
                x: float, 
                y: float, 
                scale: float, 
                format: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                subdataset_bands: Optional[List[str]] = ..., 
                subdataset_name: Optional[str] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_tile_json(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TileJsonMetadata: ...

        @distributed_trace
        def get_tile_matrix_definitions(
                self, 
                tile_matrix_set_id: str, 
                **kwargs: Any
            ) -> TileMatrixSet: ...

        @distributed_trace
        def get_wmts_capabilities(
                self, 
                collection_id: str, 
                item_id: str, 
                tile_matrix_set_id: str, 
                *, 
                algorithm: Optional[Union[str, TerrainAlgorithm]] = ..., 
                algorithm_params: Optional[str] = ..., 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                buffer: Optional[str] = ..., 
                color_formula: Optional[str] = ..., 
                color_map: Optional[str] = ..., 
                color_map_name: Optional[Union[str, ColorMapNames]] = ..., 
                expression: Optional[str] = ..., 
                max_zoom: Optional[int] = ..., 
                min_zoom: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                rescale: Optional[List[str]] = ..., 
                return_mask: Optional[bool] = ..., 
                tile_format: Optional[Union[str, TilerImageFormat]] = ..., 
                tile_scale: Optional[int] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def list_available_assets(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> List[str]: ...

        @distributed_trace
        def list_statistics(
                self, 
                collection_id: str, 
                item_id: str, 
                *, 
                asset_as_band: Optional[bool] = ..., 
                asset_band_indices: Optional[str] = ..., 
                assets: Optional[List[str]] = ..., 
                categorical: Optional[bool] = ..., 
                categories_pixels: Optional[List[str]] = ..., 
                expression: Optional[str] = ..., 
                histogram_bins: Optional[str] = ..., 
                histogram_range: Optional[str] = ..., 
                max_size: Optional[int] = ..., 
                no_data: Optional[float] = ..., 
                percentiles: Optional[List[int]] = ..., 
                resampling: Optional[Union[str, Resampling]] = ..., 
                unscale: Optional[bool] = ..., 
                **kwargs: Any
            ) -> TilerStacItemStatistics: ...

        @distributed_trace
        def list_tile_matrices(self, **kwargs: Any) -> List[str]: ...

        @overload
        def register_mosaics_search(
                self, 
                *, 
                bounding_box: Optional[float] = ..., 
                collections: Optional[List[str]] = ..., 
                content_type: str = "application/json", 
                datetime: Optional[str] = ..., 
                filter: Optional[dict[str, Any]] = ..., 
                filter_language: Optional[Union[str, FilterLanguage]] = ..., 
                ids: Optional[List[str]] = ..., 
                intersects: Optional[Geometry] = ..., 
                metadata: Optional[MosaicMetadata] = ..., 
                query: Optional[dict[str, Any]] = ..., 
                sort_by: Optional[List[StacSortExtension]] = ..., 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...

        @overload
        def register_mosaics_search(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...

        @overload
        def register_mosaics_search(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TilerMosaicSearchRegistrationResponse: ...


    class azure.planetarycomputer.operations.IngestionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def cancel_all_operations(self, **kwargs: Any) -> None: ...

        @distributed_trace
        def cancel_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def create(
                self, 
                collection_id: str, 
                body: IngestionDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        def create(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        def create(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @distributed_trace
        def create_run(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> IngestionRun: ...

        @overload
        def create_source(
                self, 
                body: IngestionSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        def create_source(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        def create_source(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @distributed_trace
        def delete_source(
                self, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @distributed_trace
        def get_operation(
                self, 
                operation_id: str, 
                **kwargs: Any
            ) -> Operation: ...

        @distributed_trace
        def get_run(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                run_id: str, 
                **kwargs: Any
            ) -> IngestionRun: ...

        @distributed_trace
        def get_source(
                self, 
                id: str, 
                **kwargs: Any
            ) -> IngestionSource: ...

        @distributed_trace
        def list(
                self, 
                collection_id: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IngestionDefinition]: ...

        @distributed_trace
        def list_managed_identities(self, **kwargs: Any) -> ItemPaged[ManagedIdentityMetadata]: ...

        @distributed_trace
        def list_operations(
                self, 
                *, 
                collection_id: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                status: Optional[Union[str, OperationStatus]] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Operation]: ...

        @distributed_trace
        def list_runs(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IngestionRun]: ...

        @distributed_trace
        def list_sources(
                self, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[IngestionSourceSummary]: ...

        @overload
        def replace_source(
                self, 
                id: str, 
                body: IngestionSource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        def replace_source(
                self, 
                id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        def replace_source(
                self, 
                id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IngestionSource: ...

        @overload
        def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: IngestionDefinition, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...

        @overload
        def update(
                self, 
                collection_id: str, 
                ingestion_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> IngestionDefinition: ...


    class azure.planetarycomputer.operations.SharedAccessSignatureOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_sign(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                href: str, 
                **kwargs: Any
            ) -> SharedAccessSignatureSignedLink: ...

        @distributed_trace
        def get_token(
                self, 
                collection_id: str, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> SharedAccessSignatureToken: ...

        @distributed_trace
        def revoke_token(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...


    class azure.planetarycomputer.operations.StacOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add_mosaic(
                self, 
                collection_id: str, 
                body: StacMosaic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def add_mosaic(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def add_mosaic(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def begin_create_collection(
                self, 
                body: StacCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_collection(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_collection(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_item(
                self, 
                collection_id: str, 
                body: StacItemOrStacItemCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_item(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_item(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: StacItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_replace_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_collection(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_item(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: StacItem, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_item(
                self, 
                collection_id: str, 
                item_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/merge-patch+json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_collection_asset(
                self, 
                collection_id: str, 
                body: StacAssetData, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def create_collection_asset(
                self, 
                collection_id: str, 
                body: JSON, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: StacCollection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def create_or_replace_collection(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def create_queryables(
                self, 
                collection_id: str, 
                body: List[StacQueryable], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        def create_queryables(
                self, 
                collection_id: str, 
                body: List[JSON], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        def create_queryables(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> List[StacQueryable]: ...

        @overload
        def create_render_option(
                self, 
                collection_id: str, 
                body: RenderOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        def create_render_option(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        def create_render_option(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @distributed_trace
        def delete_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                **kwargs: Any
            ) -> StacCollection: ...

        @distributed_trace
        def delete_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_collection(
                self, 
                collection_id: str, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacCollection: ...

        @distributed_trace
        def get_collection_configuration(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> UserCollectionSettings: ...

        @distributed_trace
        def get_collection_queryables(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> QueryableDefinitionsResponse: ...

        @distributed_trace
        def get_collection_thumbnail(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> Iterator[bytes]: ...

        @distributed_trace
        def get_collections(
                self, 
                *, 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacCatalogCollections: ...

        @distributed_trace
        def get_conformance_class(self, **kwargs: Any) -> StacConformanceClasses: ...

        @distributed_trace
        def get_item(
                self, 
                collection_id: str, 
                item_id: str, 
                **kwargs: Any
            ) -> StacItem: ...

        @distributed_trace
        def get_item_collection(
                self, 
                collection_id: str, 
                *, 
                bounding_box: Optional[List[str]] = ..., 
                datetime: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @distributed_trace
        def get_landing_page(self, **kwargs: Any) -> StacLandingPage: ...

        @distributed_trace
        def get_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                **kwargs: Any
            ) -> StacMosaic: ...

        @distributed_trace
        def get_partition_type(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> PartitionType: ...

        @distributed_trace
        def get_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                **kwargs: Any
            ) -> RenderOption: ...

        @distributed_trace
        def get_tile_settings(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> TileSettings: ...

        @distributed_trace
        def list_mosaics(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> List[StacMosaic]: ...

        @distributed_trace
        def list_queryables(self, **kwargs: Any) -> QueryableDefinitionsResponse: ...

        @distributed_trace
        def list_render_options(
                self, 
                collection_id: str, 
                **kwargs: Any
            ) -> List[RenderOption]: ...

        @overload
        def replace_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                body: StacAssetData, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def replace_collection_asset(
                self, 
                collection_id: str, 
                asset_id: str, 
                body: JSON, 
                **kwargs: Any
            ) -> StacCollection: ...

        @overload
        def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: StacMosaic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def replace_mosaic(
                self, 
                collection_id: str, 
                mosaic_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacMosaic: ...

        @overload
        def replace_partition_type(
                self, 
                collection_id: str, 
                body: PartitionType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def replace_partition_type(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def replace_partition_type(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: StacQueryable, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        def replace_queryable(
                self, 
                collection_id: str, 
                queryable_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StacQueryable: ...

        @overload
        def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: RenderOption, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        def replace_render_option(
                self, 
                collection_id: str, 
                render_option_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RenderOption: ...

        @overload
        def replace_tile_settings(
                self, 
                collection_id: str, 
                body: TileSettings, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        def replace_tile_settings(
                self, 
                collection_id: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        def replace_tile_settings(
                self, 
                collection_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TileSettings: ...

        @overload
        def search(
                self, 
                body: StacSearchParameters, 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @overload
        def search(
                self, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...

        @overload
        def search(
                self, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                duration_in_minutes: Optional[int] = ..., 
                sign: Optional[Union[str, StacAssetUrlSigningMode]] = ..., 
                **kwargs: Any
            ) -> StacItemCollection: ...


```