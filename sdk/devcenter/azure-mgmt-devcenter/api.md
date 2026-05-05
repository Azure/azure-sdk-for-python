```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.devcenter

    class azure.mgmt.devcenter.DevCenterMgmtClient: implements ContextManager 
        attached_networks: AttachedNetworksOperations
        catalogs: CatalogsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_scoped_name_availability: CheckScopedNameAvailabilityOperations
        dev_box_definitions: DevBoxDefinitionsOperations
        dev_centers: DevCentersOperations
        environment_definitions: EnvironmentDefinitionsOperations
        environment_types: EnvironmentTypesOperations
        galleries: GalleriesOperations
        image_versions: ImageVersionsOperations
        images: ImagesOperations
        network_connections: NetworkConnectionsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        pools: PoolsOperations
        project_allowed_environment_types: ProjectAllowedEnvironmentTypesOperations
        project_catalog_environment_definitions: ProjectCatalogEnvironmentDefinitionsOperations
        project_catalogs: ProjectCatalogsOperations
        project_environment_types: ProjectEnvironmentTypesOperations
        projects: ProjectsOperations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.devcenter.aio

    class azure.mgmt.devcenter.aio.DevCenterMgmtClient: implements AsyncContextManager 
        attached_networks: AttachedNetworksOperations
        catalogs: CatalogsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_scoped_name_availability: CheckScopedNameAvailabilityOperations
        dev_box_definitions: DevBoxDefinitionsOperations
        dev_centers: DevCentersOperations
        environment_definitions: EnvironmentDefinitionsOperations
        environment_types: EnvironmentTypesOperations
        galleries: GalleriesOperations
        image_versions: ImageVersionsOperations
        images: ImagesOperations
        network_connections: NetworkConnectionsOperations
        operation_statuses: OperationStatusesOperations
        operations: Operations
        pools: PoolsOperations
        project_allowed_environment_types: ProjectAllowedEnvironmentTypesOperations
        project_catalog_environment_definitions: ProjectCatalogEnvironmentDefinitionsOperations
        project_catalogs: ProjectCatalogsOperations
        project_environment_types: ProjectEnvironmentTypesOperations
        projects: ProjectsOperations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.devcenter.aio.operations

    class azure.mgmt.devcenter.aio.operations.AttachedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                body: AttachedNetworkConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedNetworkConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AttachedNetworkConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> AttachedNetworkConnection: ...

        @distributed_trace_async
        async def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> AttachedNetworkConnection: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AttachedNetworkConnection]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AttachedNetworkConnection]: ...


    class azure.mgmt.devcenter.aio.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_connect(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_sync(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace_async
        async def get_sync_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> SyncErrorDetails: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...


    class azure.mgmt.devcenter.aio.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def execute(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.devcenter.aio.operations.CheckScopedNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def execute(
                self, 
                name_availability_request: CheckScopedNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.devcenter.aio.operations.DevBoxDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: DevBoxDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBoxDefinition]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBoxDefinition]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: DevBoxDefinitionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBoxDefinition]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevBoxDefinition]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> DevBoxDefinition: ...

        @distributed_trace_async
        async def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> DevBoxDefinition: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DevBoxDefinition]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DevBoxDefinition]: ...


    class azure.mgmt.devcenter.aio.operations.DevCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: DevCenter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenter]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenter]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: DevCenterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenter]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenter]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                **kwargs: Any
            ) -> DevCenter: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DevCenter]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DevCenter]: ...


    class azure.mgmt.devcenter.aio.operations.EnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace_async
        async def get_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace_async
        async def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentDefinition]: ...


    class azure.mgmt.devcenter.aio.operations.EnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: EnvironmentType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[EnvironmentType]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: EnvironmentTypeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...


    class azure.mgmt.devcenter.aio.operations.GalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                body: Gallery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Gallery]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> Gallery: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Gallery]: ...


    class azure.mgmt.devcenter.aio.operations.ImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ImageVersion: ...

        @distributed_trace
        def list_by_image(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ImageVersion]: ...


    class azure.mgmt.devcenter.aio.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Image]: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Image]: ...


    class azure.mgmt.devcenter.aio.operations.NetworkConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: NetworkConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_run_health_checks(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: NetworkConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkConnection]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> NetworkConnection: ...

        @distributed_trace_async
        async def get_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> HealthCheckStatusDetails: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[NetworkConnection]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[NetworkConnection]: ...

        @distributed_trace
        def list_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[HealthCheckStatusDetails]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.devcenter.aio.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.devcenter.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.devcenter.aio.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_run_health_checks(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Pool]: ...


    class azure.mgmt.devcenter.aio.operations.ProjectAllowedEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> AllowedEnvironmentType: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AllowedEnvironmentType]: ...


    class azure.mgmt.devcenter.aio.operations.ProjectCatalogEnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...


    class azure.mgmt.devcenter.aio.operations.ProjectCatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_connect(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Catalog]: ...

        @distributed_trace_async
        async def begin_sync(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace_async
        async def get_sync_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> SyncErrorDetails: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Catalog]: ...


    class azure.mgmt.devcenter.aio.operations.ProjectEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: ProjectEnvironmentType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ProjectEnvironmentType]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: ProjectEnvironmentTypeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...


    class azure.mgmt.devcenter.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ProjectUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Project]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Project]: ...


    class azure.mgmt.devcenter.aio.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: Schedule, 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: IO[bytes], 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: IO[bytes], 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Schedule]: ...


    class azure.mgmt.devcenter.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[DevCenterSku]: ...


    class azure.mgmt.devcenter.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


namespace azure.mgmt.devcenter.models

    class azure.mgmt.devcenter.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.devcenter.models.AllowedEnvironmentType(Resource):
        display_name: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.AllowedEnvironmentTypeListResult(Model):
        next_link: str
        value: list[AllowedEnvironmentType]

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


    class azure.mgmt.devcenter.models.AttachedNetworkConnection(Resource):
        domain_join_type: Union[str, DomainJoinType]
        health_check_status: Union[str, HealthCheckStatus]
        id: str
        name: str
        network_connection_id: str
        network_connection_location: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_connection_id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.AttachedNetworkListResult(Model):
        next_link: str
        value: list[AttachedNetworkConnection]

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


    class azure.mgmt.devcenter.models.Capability(Model):
        name: str
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


    class azure.mgmt.devcenter.models.Catalog(Resource):
        ado_git: GitCatalog
        connection_state: Union[str, CatalogConnectionState]
        git_hub: GitCatalog
        id: str
        last_connection_time: datetime
        last_sync_stats: SyncStats
        last_sync_time: datetime
        name: str
        provisioning_state: Union[str, ProvisioningState]
        sync_state: Union[str, CatalogSyncState]
        sync_type: Union[str, CatalogSyncType]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.CatalogConflictError(Model):
        name: str
        path: str

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


    class azure.mgmt.devcenter.models.CatalogConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.devcenter.models.CatalogErrorDetails(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.CatalogItemSyncEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.CatalogItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENVIRONMENT_DEFINITION = "EnvironmentDefinition"


    class azure.mgmt.devcenter.models.CatalogListResult(Model):
        next_link: str
        value: list[Catalog]

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


    class azure.mgmt.devcenter.models.CatalogProperties(CatalogUpdateProperties):
        ado_git: GitCatalog
        connection_state: Union[str, CatalogConnectionState]
        git_hub: GitCatalog
        last_connection_time: datetime
        last_sync_stats: SyncStats
        last_sync_time: datetime
        provisioning_state: Union[str, ProvisioningState]
        sync_state: Union[str, CatalogSyncState]
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.CatalogResourceValidationErrorDetails(Model):
        errors: list[CatalogErrorDetails]

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


    class azure.mgmt.devcenter.models.CatalogResourceValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.devcenter.models.CatalogSyncError(Model):
        error_details: list[CatalogErrorDetails]
        path: str

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


    class azure.mgmt.devcenter.models.CatalogSyncState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.devcenter.models.CatalogSyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        SCHEDULED = "Scheduled"


    class azure.mgmt.devcenter.models.CatalogUpdate(Model):
        ado_git: GitCatalog
        git_hub: GitCatalog
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.CatalogUpdateProperties(Model):
        ado_git: GitCatalog
        git_hub: GitCatalog
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.devcenter.models.CheckNameAvailabilityRequest(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.CheckNameAvailabilityResponse(Model):
        message: str
        name_available: bool
        reason: Union[str, CheckNameAvailabilityReason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ..., 
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


    class azure.mgmt.devcenter.models.CheckScopedNameAvailabilityRequest(Model):
        name: str
        scope: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                type: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.devcenter.models.CustomerManagedKeyEncryption(Model):
        key_encryption_key_identity: CustomerManagedKeyEncryptionKeyIdentity
        key_encryption_key_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[CustomerManagedKeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.CustomerManagedKeyEncryptionKeyIdentity(Model):
        delegated_identity_client_id: str
        identity_type: Union[str, IdentityType]
        user_assigned_identity_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delegated_identity_client_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.DevBoxDefinition(TrackedResource):
        active_image_reference: ImageReference
        hibernate_support: Union[str, HibernateSupport]
        id: str
        image_reference: ImageReference
        image_validation_error_details: ImageValidationErrorDetails
        image_validation_status: Union[str, ImageValidationStatus]
        location: str
        name: str
        os_storage_type: str
        provisioning_state: Union[str, ProvisioningState]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        validation_status: Union[str, CatalogResourceValidationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                location: str, 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.DevBoxDefinitionListResult(Model):
        next_link: str
        value: list[DevBoxDefinition]

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


    class azure.mgmt.devcenter.models.DevBoxDefinitionProperties(DevBoxDefinitionUpdateProperties):
        active_image_reference: ImageReference
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        image_validation_error_details: ImageValidationErrorDetails
        image_validation_status: Union[str, ImageValidationStatus]
        os_storage_type: str
        provisioning_state: Union[str, ProvisioningState]
        sku: Sku
        validation_status: Union[str, CatalogResourceValidationStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.devcenter.models.DevBoxDefinitionUpdate(TrackedResourceUpdate):
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        location: str
        os_storage_type: str
        sku: Sku
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                location: Optional[str] = ..., 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.DevBoxDefinitionUpdateProperties(Model):
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        os_storage_type: str
        sku: Sku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenter(TrackedResource):
        dev_center_uri: str
        display_name: str
        encryption: Encryption
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        project_catalog_settings: DevCenterProjectCatalogSettings
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenterListResult(Model):
        next_link: str
        value: list[DevCenter]

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


    class azure.mgmt.devcenter.models.DevCenterProjectCatalogSettings(Model):
        catalog_item_sync_enable_status: Union[str, CatalogItemSyncEnableStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_item_sync_enable_status: Optional[Union[str, CatalogItemSyncEnableStatus]] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenterProperties(DevCenterUpdateProperties):
        dev_center_uri: str
        display_name: str
        encryption: Encryption
        project_catalog_settings: DevCenterProjectCatalogSettings
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenterSku(Sku):
        capabilities: list[Capability]
        capacity: int
        family: str
        locations: list[str]
        name: str
        resource_type: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenterUpdate(TrackedResourceUpdate):
        display_name: str
        encryption: Encryption
        identity: ManagedServiceIdentity
        location: str
        project_catalog_settings: DevCenterProjectCatalogSettings
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.DevCenterUpdateProperties(Model):
        display_name: str
        encryption: Encryption
        project_catalog_settings: DevCenterProjectCatalogSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ..., 
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


    class azure.mgmt.devcenter.models.DomainJoinType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AD_JOIN = "AzureADJoin"
        HYBRID_AZURE_AD_JOIN = "HybridAzureADJoin"


    class azure.mgmt.devcenter.models.Encryption(Model):
        customer_managed_key_encryption: CustomerManagedKeyEncryption

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption] = ..., 
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


    class azure.mgmt.devcenter.models.EndpointDependency(Model):
        description: str
        domain_name: str
        endpoint_details: list[EndpointDetail]

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


    class azure.mgmt.devcenter.models.EndpointDetail(Model):
        port: int

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


    class azure.mgmt.devcenter.models.EnvironmentDefinition(ProxyResource):
        description: str
        id: str
        name: str
        parameters: list[EnvironmentDefinitionParameter]
        system_data: SystemData
        template_path: str
        type: str
        validation_status: Union[str, CatalogResourceValidationStatus]

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


    class azure.mgmt.devcenter.models.EnvironmentDefinitionListResult(Model):
        next_link: str
        value: list[EnvironmentDefinition]

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


    class azure.mgmt.devcenter.models.EnvironmentDefinitionParameter(Model):
        description: str
        id: str
        name: str
        read_only: bool
        required: bool
        type: Union[str, ParameterType]

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


    class azure.mgmt.devcenter.models.EnvironmentRole(Model):
        description: str
        role_name: str

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


    class azure.mgmt.devcenter.models.EnvironmentType(Resource):
        display_name: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.EnvironmentTypeEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.EnvironmentTypeListResult(Model):
        next_link: str
        value: list[EnvironmentType]

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


    class azure.mgmt.devcenter.models.EnvironmentTypeProperties(EnvironmentTypeUpdateProperties):
        display_name: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.EnvironmentTypeUpdate(Model):
        display_name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.EnvironmentTypeUpdateProperties(Model):
        display_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.devcenter.models.ErrorDetail(Model):
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


    class azure.mgmt.devcenter.models.ErrorResponse(Model):
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


    class azure.mgmt.devcenter.models.Gallery(Resource):
        gallery_resource_id: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                gallery_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.GalleryListResult(Model):
        next_link: str
        value: list[Gallery]

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


    class azure.mgmt.devcenter.models.GitCatalog(Model):
        branch: str
        path: str
        secret_identifier: str
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                path: Optional[str] = ..., 
                secret_identifier: Optional[str] = ..., 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.HealthCheck(Model):
        additional_details: str
        display_name: str
        end_date_time: datetime
        error_type: str
        recommended_action: str
        start_date_time: datetime
        status: Union[str, HealthCheckStatus]

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


    class azure.mgmt.devcenter.models.HealthCheckStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PASSED = "Passed"
        PENDING = "Pending"
        RUNNING = "Running"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.devcenter.models.HealthCheckStatusDetails(Resource):
        end_date_time: datetime
        health_checks: list[HealthCheck]
        id: str
        name: str
        start_date_time: datetime
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.HealthCheckStatusDetailsListResult(Model):
        next_link: str
        value: list[HealthCheckStatusDetails]

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


    class azure.mgmt.devcenter.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        PENDING = "Pending"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.devcenter.models.HealthStatusDetail(Model):
        code: str
        message: str

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


    class azure.mgmt.devcenter.models.HibernateSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELEGATED_RESOURCE_IDENTITY = "delegatedResourceIdentity"
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.devcenter.models.Image(ProxyResource):
        description: str
        hibernate_support: Union[str, HibernateSupport]
        id: str
        name: str
        offer: str
        provisioning_state: Union[str, ProvisioningState]
        publisher: str
        recommended_machine_configuration: RecommendedMachineConfiguration
        sku: str
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.ImageListResult(Model):
        next_link: str
        value: list[Image]

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


    class azure.mgmt.devcenter.models.ImageReference(Model):
        exact_version: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.ImageValidationErrorDetails(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.ImageValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.devcenter.models.ImageVersion(ProxyResource):
        exclude_from_latest: bool
        id: str
        name: str
        name_properties_name: str
        os_disk_image_size_in_gb: int
        provisioning_state: Union[str, ProvisioningState]
        published_date: datetime
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.ImageVersionListResult(Model):
        next_link: str
        value: list[ImageVersion]

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


    class azure.mgmt.devcenter.models.LicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS_CLIENT = "Windows_Client"


    class azure.mgmt.devcenter.models.ListUsagesResult(Model):
        next_link: str
        value: list[Usage]

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


    class azure.mgmt.devcenter.models.LocalAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
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


    class azure.mgmt.devcenter.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.devcenter.models.NetworkConnection(TrackedResource):
        domain_join_type: Union[str, DomainJoinType]
        domain_name: str
        domain_password: str
        domain_username: str
        health_check_status: Union[str, HealthCheckStatus]
        id: str
        location: str
        name: str
        networking_resource_group_name: str
        organization_unit: str
        provisioning_state: Union[str, ProvisioningState]
        subnet_id: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_join_type: Optional[Union[str, DomainJoinType]] = ..., 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                location: str, 
                networking_resource_group_name: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.NetworkConnectionListResult(Model):
        next_link: str
        value: list[NetworkConnection]

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


    class azure.mgmt.devcenter.models.NetworkConnectionUpdate(TrackedResourceUpdate):
        domain_name: str
        domain_password: str
        domain_username: str
        location: str
        organization_unit: str
        subnet_id: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                location: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.NetworkConnectionUpdateProperties(Model):
        domain_name: str
        domain_password: str
        domain_username: str
        organization_unit: str
        subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.NetworkProperties(NetworkConnectionUpdateProperties):
        domain_join_type: Union[str, DomainJoinType]
        domain_name: str
        domain_password: str
        domain_username: str
        health_check_status: Union[str, HealthCheckStatus]
        networking_resource_group_name: str
        organization_unit: str
        provisioning_state: Union[str, ProvisioningState]
        subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domain_join_type: Union[str, DomainJoinType], 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                networking_resource_group_name: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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


    class azure.mgmt.devcenter.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

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


    class azure.mgmt.devcenter.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

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


    class azure.mgmt.devcenter.models.OperationStatus(OperationStatusResult):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        properties: JSON
        resource_id: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[List[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
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


    class azure.mgmt.devcenter.models.OperationStatusResult(Model):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        resource_id: str
        start_time: datetime
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[List[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str, 
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


    class azure.mgmt.devcenter.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.devcenter.models.OutboundEnvironmentEndpoint(Model):
        category: str
        endpoints: list[EndpointDependency]

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


    class azure.mgmt.devcenter.models.OutboundEnvironmentEndpointCollection(Model):
        next_link: str
        value: list[OutboundEnvironmentEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        INTEGER = "integer"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


    class azure.mgmt.devcenter.models.Pool(TrackedResource):
        dev_box_count: int
        dev_box_definition_name: str
        display_name: str
        health_status: Union[str, HealthStatus]
        health_status_details: list[HealthStatusDetail]
        id: str
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        location: str
        managed_virtual_network_regions: list[str]
        name: str
        network_connection_name: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        system_data: SystemData
        tags: dict[str, str]
        type: str
        virtual_network_type: Union[str, VirtualNetworkType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dev_box_definition_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                location: str, 
                managed_virtual_network_regions: Optional[List[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ..., 
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


    class azure.mgmt.devcenter.models.PoolListResult(Model):
        next_link: str
        value: list[Pool]

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


    class azure.mgmt.devcenter.models.PoolProperties(PoolUpdateProperties):
        dev_box_count: int
        dev_box_definition_name: str
        display_name: str
        health_status: Union[str, HealthStatus]
        health_status_details: list[HealthStatusDetail]
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        virtual_network_type: Union[str, VirtualNetworkType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dev_box_definition_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                managed_virtual_network_regions: Optional[List[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ..., 
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


    class azure.mgmt.devcenter.models.PoolUpdate(TrackedResourceUpdate):
        dev_box_definition_name: str
        display_name: str
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        location: str
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        tags: dict[str, str]
        virtual_network_type: Union[str, VirtualNetworkType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dev_box_definition_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                location: Optional[str] = ..., 
                managed_virtual_network_regions: Optional[List[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ..., 
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


    class azure.mgmt.devcenter.models.PoolUpdateProperties(Model):
        dev_box_definition_name: str
        display_name: str
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        virtual_network_type: Union[str, VirtualNetworkType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dev_box_definition_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                managed_virtual_network_regions: Optional[List[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ..., 
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


    class azure.mgmt.devcenter.models.Project(TrackedResource):
        catalog_settings: ProjectCatalogSettings
        description: str
        dev_center_id: str
        dev_center_uri: str
        display_name: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        max_dev_boxes_per_user: int
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                description: Optional[str] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                max_dev_boxes_per_user: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectCatalogSettings(Model):
        catalog_item_sync_types: Union[list[str, CatalogItemType]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_item_sync_types: Optional[List[Union[str, CatalogItemType]]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectEnvironmentType(Resource):
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        environment_count: int
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, EnvironmentTypeEnableStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        user_role_assignments: dict[str, UserRoleAssignmentValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                user_role_assignments: Optional[Dict[str, UserRoleAssignmentValue]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeListResult(Model):
        next_link: str
        value: list[ProjectEnvironmentType]

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


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeProperties(ProjectEnvironmentTypeUpdateProperties):
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        environment_count: int
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, EnvironmentTypeEnableStatus]
        user_role_assignments: dict[str, UserRoleAssignmentValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                user_role_assignments: Optional[Dict[str, UserRoleAssignmentValue]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdate(Model):
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        identity: ManagedServiceIdentity
        status: Union[str, EnvironmentTypeEnableStatus]
        tags: dict[str, str]
        user_role_assignments: dict[str, UserRoleAssignmentValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                user_role_assignments: Optional[Dict[str, UserRoleAssignmentValue]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdateProperties(Model):
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        status: Union[str, EnvironmentTypeEnableStatus]
        user_role_assignments: dict[str, UserRoleAssignmentValue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                user_role_assignments: Optional[Dict[str, UserRoleAssignmentValue]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment(Model):
        roles: dict[str, EnvironmentRole]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                roles: Optional[Dict[str, EnvironmentRole]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectListResult(Model):
        next_link: str
        value: list[Project]

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


    class azure.mgmt.devcenter.models.ProjectProperties(ProjectUpdateProperties):
        catalog_settings: ProjectCatalogSettings
        description: str
        dev_center_id: str
        dev_center_uri: str
        display_name: str
        max_dev_boxes_per_user: int
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                description: Optional[str] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectUpdate(TrackedResourceUpdate):
        catalog_settings: ProjectCatalogSettings
        description: str
        dev_center_id: str
        display_name: str
        identity: ManagedServiceIdentity
        location: str
        max_dev_boxes_per_user: int
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                description: Optional[str] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.ProjectUpdateProperties(Model):
        catalog_settings: ProjectCatalogSettings
        description: str
        dev_center_id: str
        display_name: str
        max_dev_boxes_per_user: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                description: Optional[str] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ..., 
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


    class azure.mgmt.devcenter.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING_RESOURCES = "MovingResources"
        NOT_SPECIFIED = "NotSpecified"
        ROLLOUT_IN_PROGRESS = "RolloutInProgress"
        RUNNING = "Running"
        STORAGE_PROVISIONING_FAILED = "StorageProvisioningFailed"
        SUCCEEDED = "Succeeded"
        TRANSIENT_FAILURE = "TransientFailure"
        UPDATED = "Updated"
        UPDATING = "Updating"


    class azure.mgmt.devcenter.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.RecommendedMachineConfiguration(Model):
        memory: ResourceRange
        v_cp_us: ResourceRange

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


    class azure.mgmt.devcenter.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
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


    class azure.mgmt.devcenter.models.ResourceRange(Model):
        max: int
        min: int

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


    class azure.mgmt.devcenter.models.Schedule(Resource):
        frequency: Union[str, ScheduledFrequency]
        id: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, ScheduleEnableStatus]
        system_data: SystemData
        tags: dict[str, str]
        time: str
        time_zone: str
        type: str
        type_properties_type: Union[str, ScheduledType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type_properties_type: Optional[Union[str, ScheduledType]] = ..., 
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


    class azure.mgmt.devcenter.models.ScheduleEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.ScheduleListResult(Model):
        next_link: str
        value: list[Schedule]

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


    class azure.mgmt.devcenter.models.ScheduleProperties(ScheduleUpdateProperties):
        frequency: Union[str, ScheduledFrequency]
        location: str
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, ScheduledType]] = ..., 
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


    class azure.mgmt.devcenter.models.ScheduleUpdate(Model):
        frequency: Union[str, ScheduledFrequency]
        location: str
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, ScheduledType]] = ..., 
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


    class azure.mgmt.devcenter.models.ScheduleUpdateProperties(TrackedResourceUpdate):
        frequency: Union[str, ScheduledFrequency]
        location: str
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, ScheduledType]] = ..., 
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


    class azure.mgmt.devcenter.models.ScheduledFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"


    class azure.mgmt.devcenter.models.ScheduledType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STOP_DEV_BOX = "StopDevBox"


    class azure.mgmt.devcenter.models.SingleSignOnStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.Sku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.devcenter.models.SkuListResult(Model):
        next_link: str
        value: list[DevCenterSku]

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


    class azure.mgmt.devcenter.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.devcenter.models.StopOnDisconnectConfiguration(Model):
        grace_period_minutes: int
        status: Union[str, StopOnDisconnectEnableStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                grace_period_minutes: Optional[int] = ..., 
                status: Optional[Union[str, StopOnDisconnectEnableStatus]] = ..., 
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


    class azure.mgmt.devcenter.models.StopOnDisconnectEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.SyncErrorDetails(Model):
        conflicts: list[CatalogConflictError]
        errors: list[CatalogSyncError]
        operation_error: CatalogErrorDetails

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


    class azure.mgmt.devcenter.models.SyncStats(Model):
        added: int
        removed: int
        synced_catalog_item_types: Union[list[str, CatalogItemType]]
        synchronization_errors: int
        unchanged: int
        updated: int
        validation_errors: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                synced_catalog_item_types: Optional[List[Union[str, CatalogItemType]]] = ..., 
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


    class azure.mgmt.devcenter.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
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


    class azure.mgmt.devcenter.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.TrackedResourceUpdate(Model):
        location: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.devcenter.models.Usage(Model):
        current_value: int
        id: str
        limit: int
        name: UsageName
        unit: Union[str, UsageUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[UsageName] = ..., 
                unit: Optional[Union[str, UsageUnit]] = ..., 
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


    class azure.mgmt.devcenter.models.UsageName(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
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


    class azure.mgmt.devcenter.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.devcenter.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

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


    class azure.mgmt.devcenter.models.UserRoleAssignmentValue(Model):
        roles: dict[str, EnvironmentRole]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                roles: Optional[Dict[str, EnvironmentRole]] = ..., 
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


    class azure.mgmt.devcenter.models.VirtualNetworkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        UNMANAGED = "Unmanaged"


namespace azure.mgmt.devcenter.operations

    class azure.mgmt.devcenter.operations.AttachedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                body: AttachedNetworkConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedNetworkConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AttachedNetworkConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> AttachedNetworkConnection: ...

        @distributed_trace
        def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                attached_network_connection_name: str, 
                **kwargs: Any
            ) -> AttachedNetworkConnection: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AttachedNetworkConnection]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AttachedNetworkConnection]: ...


    class azure.mgmt.devcenter.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_connect(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_sync(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace
        def get_sync_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> SyncErrorDetails: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...


    class azure.mgmt.devcenter.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def execute(
                self, 
                name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.devcenter.operations.CheckScopedNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def execute(
                self, 
                name_availability_request: CheckScopedNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def execute(
                self, 
                name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...


    class azure.mgmt.devcenter.operations.DevBoxDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: DevBoxDefinition, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBoxDefinition]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBoxDefinition]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: DevBoxDefinitionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBoxDefinition]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevBoxDefinition]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> DevBoxDefinition: ...

        @distributed_trace
        def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                dev_box_definition_name: str, 
                **kwargs: Any
            ) -> DevBoxDefinition: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DevBoxDefinition]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DevBoxDefinition]: ...


    class azure.mgmt.devcenter.operations.DevCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: DevCenter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenter]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenter]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: DevCenterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenter]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenter]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                **kwargs: Any
            ) -> DevCenter: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DevCenter]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DevCenter]: ...


    class azure.mgmt.devcenter.operations.EnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace
        def get_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> EnvironmentDefinition: ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[EnvironmentDefinition]: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Iterable[EnvironmentDefinition]: ...


    class azure.mgmt.devcenter.operations.EnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: EnvironmentType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[EnvironmentType]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: EnvironmentTypeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnvironmentType: ...


    class azure.mgmt.devcenter.operations.GalleriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                body: Gallery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Gallery]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                **kwargs: Any
            ) -> Gallery: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Gallery]: ...


    class azure.mgmt.devcenter.operations.ImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                version_name: str, 
                **kwargs: Any
            ) -> ImageVersion: ...

        @distributed_trace
        def list_by_image(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Iterable[ImageVersion]: ...


    class azure.mgmt.devcenter.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Image]: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Image]: ...


    class azure.mgmt.devcenter.operations.NetworkConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: NetworkConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_run_health_checks(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: NetworkConnectionUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkConnection]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NetworkConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> NetworkConnection: ...

        @distributed_trace
        def get_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                **kwargs: Any
            ) -> HealthCheckStatusDetails: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[NetworkConnection]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[NetworkConnection]: ...

        @distributed_trace
        def list_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[HealthCheckStatusDetails]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.devcenter.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatus: ...


    class azure.mgmt.devcenter.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.devcenter.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_run_health_checks(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: PoolUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Pool]: ...


    class azure.mgmt.devcenter.operations.ProjectAllowedEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> AllowedEnvironmentType: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[AllowedEnvironmentType]: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogEnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_connect(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: Catalog, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: CatalogUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Catalog]: ...

        @distributed_trace
        def begin_sync(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> Catalog: ...

        @distributed_trace
        def get_sync_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> SyncErrorDetails: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Catalog]: ...


    class azure.mgmt.devcenter.operations.ProjectEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: ProjectEnvironmentType, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                project_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ProjectEnvironmentType]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: ProjectEnvironmentTypeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                environment_type_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectEnvironmentType: ...


    class azure.mgmt.devcenter.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ProjectUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Project]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Project]: ...


    class azure.mgmt.devcenter.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: Schedule, 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: IO[bytes], 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: IO[bytes], 
                top: Optional[int] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Schedule]: ...


    class azure.mgmt.devcenter.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_subscription(
                self, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[DevCenterSku]: ...


    class azure.mgmt.devcenter.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


```