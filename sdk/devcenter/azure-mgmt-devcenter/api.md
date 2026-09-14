```py
namespace azure.mgmt.devcenter

    class azure.mgmt.devcenter.DevCenterMgmtClient: implements ContextManager 
        attached_networks: AttachedNetworksOperations
        catalogs: CatalogsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_scoped_name_availability: CheckScopedNameAvailabilityOperations
        customization_tasks: CustomizationTasksOperations
        dev_box_definitions: DevBoxDefinitionsOperations
        dev_center_catalog_image_definition_build: DevCenterCatalogImageDefinitionBuildOperations
        dev_center_catalog_image_definition_builds: DevCenterCatalogImageDefinitionBuildsOperations
        dev_center_catalog_image_definitions: DevCenterCatalogImageDefinitionsOperations
        dev_centers: DevCentersOperations
        encryption_sets: EncryptionSetsOperations
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
        project_catalog_image_definition_build: ProjectCatalogImageDefinitionBuildOperations
        project_catalog_image_definition_builds: ProjectCatalogImageDefinitionBuildsOperations
        project_catalog_image_definitions: ProjectCatalogImageDefinitionsOperations
        project_catalogs: ProjectCatalogsOperations
        project_environment_types: ProjectEnvironmentTypesOperations
        project_policies: ProjectPoliciesOperations
        projects: ProjectsOperations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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


namespace azure.mgmt.devcenter.aio

    class azure.mgmt.devcenter.aio.DevCenterMgmtClient: implements AsyncContextManager 
        attached_networks: AttachedNetworksOperations
        catalogs: CatalogsOperations
        check_name_availability: CheckNameAvailabilityOperations
        check_scoped_name_availability: CheckScopedNameAvailabilityOperations
        customization_tasks: CustomizationTasksOperations
        dev_box_definitions: DevBoxDefinitionsOperations
        dev_center_catalog_image_definition_build: DevCenterCatalogImageDefinitionBuildOperations
        dev_center_catalog_image_definition_builds: DevCenterCatalogImageDefinitionBuildsOperations
        dev_center_catalog_image_definitions: DevCenterCatalogImageDefinitionsOperations
        dev_centers: DevCentersOperations
        encryption_sets: EncryptionSetsOperations
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
        project_catalog_image_definition_build: ProjectCatalogImageDefinitionBuildOperations
        project_catalog_image_definition_builds: ProjectCatalogImageDefinitionBuildsOperations
        project_catalog_image_definitions: ProjectCatalogImageDefinitionsOperations
        project_catalogs: ProjectCatalogsOperations
        project_environment_types: ProjectEnvironmentTypesOperations
        project_policies: ProjectPoliciesOperations
        projects: ProjectsOperations
        schedules: SchedulesOperations
        skus: SkusOperations
        usages: UsagesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AttachedNetworkConnection]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AttachedNetworkConnection]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Catalog]: ...


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


    class azure.mgmt.devcenter.aio.operations.CustomizationTasksOperations:

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
                task_name: str, 
                **kwargs: Any
            ) -> CustomizationTask: ...

        @distributed_trace_async
        async def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomizationTask]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevBoxDefinition]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevBoxDefinition]: ...


    class azure.mgmt.devcenter.aio.operations.DevCenterCatalogImageDefinitionBuildOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuild: ...

        @distributed_trace_async
        async def get_build_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuildDetails: ...


    class azure.mgmt.devcenter.aio.operations.DevCenterCatalogImageDefinitionBuildsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image_definition(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageDefinitionBuild]: ...


    class azure.mgmt.devcenter.aio.operations.DevCenterCatalogImageDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_build_image(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_by_dev_center_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ImageDefinition: ...

        @distributed_trace_async
        async def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_dev_center_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageDefinition]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevCenter]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevCenter]: ...


    class azure.mgmt.devcenter.aio.operations.EncryptionSetsOperations:

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
                encryption_set_name: str, 
                body: DevCenterEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: DevCenterEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: EncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: EncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DevCenterEncryptionSet]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                **kwargs: Any
            ) -> DevCenterEncryptionSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevCenterEncryptionSet]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EnvironmentDefinition]: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnvironmentDefinition]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EnvironmentType]: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Gallery]: ...


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

        @distributed_trace_async
        async def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
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
            ) -> AsyncItemPaged[ImageVersion]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageVersion]: ...


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

        @distributed_trace_async
        async def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkConnection]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkConnection]: ...

        @distributed_trace
        def list_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[HealthCheckStatusDetails]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundEnvironmentEndpoint]: ...


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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Pool]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AllowedEnvironmentType]: ...


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


    class azure.mgmt.devcenter.aio.operations.ProjectCatalogImageDefinitionBuildOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuild: ...

        @distributed_trace_async
        async def get_build_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuildDetails: ...


    class azure.mgmt.devcenter.aio.operations.ProjectCatalogImageDefinitionBuildsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image_definition(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageDefinitionBuild]: ...


    class azure.mgmt.devcenter.aio.operations.ProjectCatalogImageDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_build_image(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ImageDefinition: ...

        @distributed_trace_async
        async def get_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ImageDefinition]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Catalog]: ...


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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectEnvironmentType]: ...

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


    class azure.mgmt.devcenter.aio.operations.ProjectPoliciesOperations:

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
                project_policy_name: str, 
                body: ProjectPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                **kwargs: Any
            ) -> ProjectPolicy: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectPolicy]: ...


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

        @distributed_trace_async
        async def get_inherited_settings(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> InheritedSettingsForProject: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...


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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                *, 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[Schedule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Schedule]: ...


    class azure.mgmt.devcenter.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DevCenterSku]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DevCenterSku]: ...


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
            ) -> AsyncItemPaged[Usage]: ...


namespace azure.mgmt.devcenter.models

    class azure.mgmt.devcenter.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.devcenter.models.ActiveHoursConfiguration(_Model):
        auto_start_enable_status: Optional[Union[str, AutoStartEnableStatus]]
        days_of_week_limit: Optional[int]
        default_days_of_week: Optional[list[Union[str, DayOfWeek]]]
        default_end_time_hour: Optional[int]
        default_start_time_hour: Optional[int]
        default_time_zone: Optional[str]
        keep_awake_enable_status: Optional[Union[str, KeepAwakeEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                auto_start_enable_status: Optional[Union[str, AutoStartEnableStatus]] = ..., 
                days_of_week_limit: Optional[int] = ..., 
                default_days_of_week: Optional[list[Union[str, DayOfWeek]]] = ..., 
                default_end_time_hour: Optional[int] = ..., 
                default_start_time_hour: Optional[int] = ..., 
                default_time_zone: Optional[str] = ..., 
                keep_awake_enable_status: Optional[Union[str, KeepAwakeEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.AllowedEnvironmentType(ProxyResource):
        id: str
        name: str
        properties: Optional[AllowedEnvironmentTypeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AllowedEnvironmentTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.AllowedEnvironmentTypeProperties(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.devcenter.models.ArchitectureType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARM64 = "Arm64"
        X64 = "x64"


    class azure.mgmt.devcenter.models.AssignedGroup(_Model):
        object_id: Optional[str]
        scope: Optional[Union[str, AssignedGroupScope]]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ..., 
                scope: Optional[Union[str, AssignedGroupScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.AssignedGroupScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEV_BOX = "DevBox"


    class azure.mgmt.devcenter.models.AttachedNetworkConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[AttachedNetworkConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AttachedNetworkConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.AttachedNetworkConnectionProperties(_Model):
        domain_join_type: Optional[Union[str, DomainJoinType]]
        health_check_status: Optional[Union[str, HealthCheckStatus]]
        network_connection_id: Optional[str]
        network_connection_location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                network_connection_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.AutoImageBuildStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.AutoStartEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.AzureAiServicesMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_DEPLOY = "AutoDeploy"
        DISABLED = "Disabled"


    class azure.mgmt.devcenter.models.AzureAiServicesSettings(_Model):
        azure_ai_services_mode: Optional[Union[str, AzureAiServicesMode]]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_services_mode: Optional[Union[str, AzureAiServicesMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CancelOnConnectEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.Capability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.devcenter.models.Catalog(ProxyResource):
        id: str
        name: str
        properties: Optional[CatalogProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CatalogProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CatalogAutoImageBuildEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.CatalogConflictError(_Model):
        name: Optional[str]
        path: Optional[str]


    class azure.mgmt.devcenter.models.CatalogConnectionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.devcenter.models.CatalogErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CatalogItemSyncEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.CatalogItemType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENVIRONMENT_DEFINITION = "EnvironmentDefinition"
        IMAGE_DEFINITION = "ImageDefinition"


    class azure.mgmt.devcenter.models.CatalogProperties(CatalogUpdateProperties):
        ado_git: GitCatalog
        auto_image_build_enable_status: Union[str, CatalogAutoImageBuildEnableStatus]
        connection_state: Optional[Union[str, CatalogConnectionState]]
        git_hub: GitCatalog
        last_connection_time: Optional[datetime]
        last_sync_stats: Optional[SyncStats]
        last_sync_time: Optional[datetime]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sync_state: Optional[Union[str, CatalogSyncState]]
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                auto_image_build_enable_status: Optional[Union[str, CatalogAutoImageBuildEnableStatus]] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CatalogResourceValidationErrorDetails(_Model):
        errors: Optional[list[CatalogErrorDetails]]


    class azure.mgmt.devcenter.models.CatalogResourceValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.devcenter.models.CatalogSyncError(_Model):
        error_details: Optional[list[CatalogErrorDetails]]
        path: Optional[str]


    class azure.mgmt.devcenter.models.CatalogSyncState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.devcenter.models.CatalogSyncType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        SCHEDULED = "Scheduled"


    class azure.mgmt.devcenter.models.CatalogUpdate(_Model):
        properties: Optional[CatalogUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CatalogUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.CatalogUpdateProperties(_Model):
        ado_git: Optional[GitCatalog]
        auto_image_build_enable_status: Optional[Union[str, CatalogAutoImageBuildEnableStatus]]
        git_hub: Optional[GitCatalog]
        sync_type: Optional[Union[str, CatalogSyncType]]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                ado_git: Optional[GitCatalog] = ..., 
                auto_image_build_enable_status: Optional[Union[str, CatalogAutoImageBuildEnableStatus]] = ..., 
                git_hub: Optional[GitCatalog] = ..., 
                sync_type: Optional[Union[str, CatalogSyncType]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.devcenter.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CheckScopedNameAvailabilityRequest(_Model):
        name: Optional[str]
        scope: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CmkIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.devcenter.models.ConfigurationPolicies(_Model):
        azure_ai_services_feature_status: Optional[FeatureState]
        dev_box_limits_feature_status: Optional[FeatureState]
        dev_box_schedule_delete_feature_status: Optional[FeatureState]
        dev_box_tunnel_feature_status: Optional[FeatureState]
        display_name_feature_status: Optional[FeatureState]
        project_catalog_feature_status: Optional[FeatureState]
        serverless_gpu_sessions_feature_status: Optional[FeatureState]
        user_customizations_feature_status: Optional[FeatureState]
        workspace_storage_feature_status: Optional[FeatureState]

        @overload
        def __init__(
                self, 
                *, 
                azure_ai_services_feature_status: Optional[FeatureState] = ..., 
                dev_box_limits_feature_status: Optional[FeatureState] = ..., 
                dev_box_schedule_delete_feature_status: Optional[FeatureState] = ..., 
                dev_box_tunnel_feature_status: Optional[FeatureState] = ..., 
                display_name_feature_status: Optional[FeatureState] = ..., 
                project_catalog_feature_status: Optional[FeatureState] = ..., 
                serverless_gpu_sessions_feature_status: Optional[FeatureState] = ..., 
                user_customizations_feature_status: Optional[FeatureState] = ..., 
                workspace_storage_feature_status: Optional[FeatureState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.devcenter.models.CustomerManagedKeyEncryption(_Model):
        key_encryption_key_identity: Optional[CustomerManagedKeyEncryptionKeyIdentity]
        key_encryption_key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[CustomerManagedKeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CustomerManagedKeyEncryptionKeyIdentity(_Model):
        delegated_identity_client_id: Optional[str]
        federated_client_id: Optional[str]
        identity_type: Optional[Union[str, IdentityType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delegated_identity_client_id: Optional[str] = ..., 
                federated_client_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, IdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CustomizationTask(ProxyResource):
        id: str
        name: str
        properties: Optional[CustomizationTaskProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomizationTaskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CustomizationTaskInput(_Model):
        description: Optional[str]
        required: Optional[bool]
        type: Optional[Union[str, CustomizationTaskInputType]]


    class azure.mgmt.devcenter.models.CustomizationTaskInputType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOLEAN = "boolean"
        NUMBER = "number"
        STRING = "string"


    class azure.mgmt.devcenter.models.CustomizationTaskInstance(_Model):
        condition: Optional[str]
        display_name: Optional[str]
        name: str
        parameters: Optional[list[DefinitionParametersItem]]
        timeout_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: str, 
                parameters: Optional[list[DefinitionParametersItem]] = ..., 
                timeout_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.CustomizationTaskProperties(_Model):
        inputs: Optional[dict[str, CustomizationTaskInput]]
        timeout: Optional[int]
        validation_status: Optional[Union[str, CatalogResourceValidationStatus]]


    class azure.mgmt.devcenter.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.devcenter.models.DefaultValue(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DefinitionParametersItem(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxDefinition(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DevBoxDefinitionProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DevBoxDefinitionProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxDefinitionProperties(DevBoxDefinitionUpdateProperties):
        active_image_reference: Optional[ImageReference]
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        image_validation_error_details: Optional[ImageValidationErrorDetails]
        image_validation_status: Optional[Union[str, ImageValidationStatus]]
        os_storage_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sku: Sku
        validation_status: Optional[Union[str, CatalogResourceValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxDefinitionUpdate(_Model):
        location: Optional[str]
        properties: Optional[DevBoxDefinitionUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[DevBoxDefinitionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxDefinitionUpdateProperties(_Model):
        hibernate_support: Optional[Union[str, HibernateSupport]]
        image_reference: Optional[ImageReference]
        os_storage_type: Optional[str]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                hibernate_support: Optional[Union[str, HibernateSupport]] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                os_storage_type: Optional[str] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxDeleteMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO = "Auto"
        MANUAL = "Manual"


    class azure.mgmt.devcenter.models.DevBoxProvisioningSettings(_Model):
        install_azure_monitor_agent_enable_status: Optional[Union[str, InstallAzureMonitorAgentEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                install_azure_monitor_agent_enable_status: Optional[Union[str, InstallAzureMonitorAgentEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxScheduleDeleteSettings(_Model):
        cancel_on_connect_enable_status: Optional[Union[str, CancelOnConnectEnableStatus]]
        delete_mode: Optional[Union[str, DevBoxDeleteMode]]
        grace_period: Optional[timedelta]
        inactive_threshold: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                cancel_on_connect_enable_status: Optional[Union[str, CancelOnConnectEnableStatus]] = ..., 
                delete_mode: Optional[Union[str, DevBoxDeleteMode]] = ..., 
                grace_period: Optional[timedelta] = ..., 
                inactive_threshold: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevBoxTunnelEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.DevCenter(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[DevCenterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[DevCenterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterEncryptionSet(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[DevCenterEncryptionSetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[DevCenterEncryptionSetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterEncryptionSetProperties(DevCenterEncryptionSetUpdateProperties):
        devbox_disks_encryption_enable_status: Union[str, DevboxDisksEncryptionEnableStatus]
        key_encryption_key_identity: KeyEncryptionKeyIdentityUpdate
        key_encryption_key_url: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                devbox_disks_encryption_enable_status: Optional[Union[str, DevboxDisksEncryptionEnableStatus]] = ..., 
                key_encryption_key_identity: Optional[KeyEncryptionKeyIdentityUpdate] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterEncryptionSetUpdateProperties(_Model):
        devbox_disks_encryption_enable_status: Optional[Union[str, DevboxDisksEncryptionEnableStatus]]
        key_encryption_key_identity: Optional[KeyEncryptionKeyIdentityUpdate]
        key_encryption_key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                devbox_disks_encryption_enable_status: Optional[Union[str, DevboxDisksEncryptionEnableStatus]] = ..., 
                key_encryption_key_identity: Optional[KeyEncryptionKeyIdentityUpdate] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterNetworkSettings(_Model):
        microsoft_hosted_network_enable_status: Optional[Union[str, MicrosoftHostedNetworkEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                microsoft_hosted_network_enable_status: Optional[Union[str, MicrosoftHostedNetworkEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterProjectCatalogSettings(_Model):
        catalog_item_sync_enable_status: Optional[Union[str, CatalogItemSyncEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                catalog_item_sync_enable_status: Optional[Union[str, CatalogItemSyncEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterProperties(DevCenterUpdateProperties):
        dev_box_provisioning_settings: DevBoxProvisioningSettings
        dev_center_uri: Optional[str]
        display_name: str
        encryption: Encryption
        network_settings: DevCenterNetworkSettings
        project_catalog_settings: DevCenterProjectCatalogSettings
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                dev_box_provisioning_settings: Optional[DevBoxProvisioningSettings] = ..., 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                network_settings: Optional[DevCenterNetworkSettings] = ..., 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACHED_NETWORKS = "AttachedNetworks"
        IMAGES = "Images"
        SKUS = "Skus"


    class azure.mgmt.devcenter.models.DevCenterSku(Sku):
        capabilities: Optional[list[Capability]]
        capacity: int
        family: str
        locations: Optional[list[str]]
        name: str
        resource_type: Optional[str]
        size: str
        tier: Union[str, SkuTier]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        properties: Optional[DevCenterUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DevCenterUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.DevCenterUpdateProperties(_Model):
        dev_box_provisioning_settings: Optional[DevBoxProvisioningSettings]
        display_name: Optional[str]
        encryption: Optional[Encryption]
        network_settings: Optional[DevCenterNetworkSettings]
        project_catalog_settings: Optional[DevCenterProjectCatalogSettings]

        @overload
        def __init__(
                self, 
                *, 
                dev_box_provisioning_settings: Optional[DevBoxProvisioningSettings] = ..., 
                display_name: Optional[str] = ..., 
                encryption: Optional[Encryption] = ..., 
                network_settings: Optional[DevCenterNetworkSettings] = ..., 
                project_catalog_settings: Optional[DevCenterProjectCatalogSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.DevboxDisksEncryptionEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.DomainJoinType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_AD_JOIN = "AzureADJoin"
        HYBRID_AZURE_AD_JOIN = "HybridAzureADJoin"
        NONE = "None"


    class azure.mgmt.devcenter.models.Encryption(_Model):
        customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.EncryptionSetUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        properties: Optional[DevCenterEncryptionSetUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[DevCenterEncryptionSetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.EndpointDependency(_Model):
        description: Optional[str]
        domain_name: Optional[str]
        endpoint_details: Optional[list[EndpointDetail]]


    class azure.mgmt.devcenter.models.EndpointDetail(_Model):
        port: Optional[int]


    class azure.mgmt.devcenter.models.EnvironmentDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[EnvironmentDefinitionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnvironmentDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.EnvironmentDefinitionParameter(_Model):
        description: Optional[str]
        id: Optional[str]
        name: Optional[str]
        read_only: Optional[bool]
        required: Optional[bool]
        type: Optional[Union[str, ParameterType]]


    class azure.mgmt.devcenter.models.EnvironmentDefinitionProperties(_Model):
        description: Optional[str]
        parameters: Optional[list[EnvironmentDefinitionParameter]]
        template_path: Optional[str]
        validation_status: Optional[Union[str, CatalogResourceValidationStatus]]


    class azure.mgmt.devcenter.models.EnvironmentRole(_Model):
        description: Optional[str]
        role_name: Optional[str]


    class azure.mgmt.devcenter.models.EnvironmentType(ProxyResource):
        id: str
        name: str
        properties: Optional[EnvironmentTypeProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnvironmentTypeProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.EnvironmentTypeEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.EnvironmentTypeProperties(EnvironmentTypeUpdateProperties):
        display_name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.EnvironmentTypeUpdate(_Model):
        properties: Optional[EnvironmentTypeUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EnvironmentTypeUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.EnvironmentTypeUpdateProperties(_Model):
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.devcenter.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.devcenter.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.FeatureState(_Model):
        default_status: Optional[Union[str, FeatureStatus]]
        default_values: Optional[list[DefaultValue]]
        status_modifiable: Optional[Union[str, FeatureStateModifiable]]
        values_modifiable: Optional[Union[str, FeatureStateModifiable]]

        @overload
        def __init__(
                self, 
                *, 
                default_status: Optional[Union[str, FeatureStatus]] = ..., 
                default_values: Optional[list[DefaultValue]] = ..., 
                status_modifiable: Optional[Union[str, FeatureStateModifiable]] = ..., 
                values_modifiable: Optional[Union[str, FeatureStateModifiable]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.FeatureStateModifiable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MODIFIABLE = "Modifiable"
        NOT_MODIFIABLE = "NotModifiable"


    class azure.mgmt.devcenter.models.FeatureStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_DEPLOY = "AutoDeploy"
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.Gallery(ProxyResource):
        id: str
        name: str
        properties: Optional[GalleryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GalleryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.GalleryProperties(_Model):
        gallery_resource_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                gallery_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.GitCatalog(_Model):
        branch: Optional[str]
        path: Optional[str]
        secret_identifier: Optional[str]
        uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                branch: Optional[str] = ..., 
                path: Optional[str] = ..., 
                secret_identifier: Optional[str] = ..., 
                uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.HealthCheck(_Model):
        additional_details: Optional[str]
        display_name: Optional[str]
        end_date_time: Optional[datetime]
        error_type: Optional[str]
        recommended_action: Optional[str]
        start_date_time: Optional[datetime]
        status: Optional[Union[str, HealthCheckStatus]]


    class azure.mgmt.devcenter.models.HealthCheckStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INFORMATIONAL = "Informational"
        PASSED = "Passed"
        PENDING = "Pending"
        RUNNING = "Running"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.devcenter.models.HealthCheckStatusDetails(ProxyResource):
        id: str
        name: str
        properties: Optional[HealthCheckStatusDetailsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HealthCheckStatusDetailsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.HealthCheckStatusDetailsProperties(_Model):
        end_date_time: Optional[datetime]
        health_checks: Optional[list[HealthCheck]]
        start_date_time: Optional[datetime]


    class azure.mgmt.devcenter.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        PENDING = "Pending"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"
        WARNING = "Warning"


    class azure.mgmt.devcenter.models.HealthStatusDetail(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.devcenter.models.HibernateSupport(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELEGATED_RESOURCE_IDENTITY = "delegatedResourceIdentity"
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.devcenter.models.Image(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageCreationErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinition(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageDefinitionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageDefinitionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinitionBuild(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageDefinitionBuildProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageDefinitionBuildProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinitionBuildDetails(ProxyResource):
        end_time: Optional[datetime]
        error_details: Optional[ImageCreationErrorDetails]
        id: str
        image_reference: Optional[ImageReference]
        name: str
        start_time: Optional[datetime]
        status: Optional[Union[str, ImageDefinitionBuildStatus]]
        system_data: SystemData
        task_groups: Optional[list[ImageDefinitionBuildTaskGroup]]
        type: str


    class azure.mgmt.devcenter.models.ImageDefinitionBuildProperties(_Model):
        end_time: Optional[datetime]
        error_details: Optional[ImageCreationErrorDetails]
        image_reference: Optional[ImageReference]
        start_time: Optional[datetime]
        status: Optional[Union[str, ImageDefinitionBuildStatus]]


    class azure.mgmt.devcenter.models.ImageDefinitionBuildStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        VALIDATION_FAILED = "ValidationFailed"


    class azure.mgmt.devcenter.models.ImageDefinitionBuildTask(_Model):
        display_name: Optional[str]
        end_time: Optional[datetime]
        id: Optional[str]
        log_uri: Optional[str]
        name: Optional[str]
        parameters: Optional[list[ImageDefinitionBuildTaskParametersItem]]
        start_time: Optional[datetime]
        status: Optional[Union[str, ImageDefinitionBuildStatus]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                parameters: Optional[list[ImageDefinitionBuildTaskParametersItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinitionBuildTaskGroup(_Model):
        end_time: Optional[datetime]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, ImageDefinitionBuildStatus]]
        tasks: Optional[list[ImageDefinitionBuildTask]]


    class azure.mgmt.devcenter.models.ImageDefinitionBuildTaskParametersItem(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinitionProperties(_Model):
        active_image_reference: Optional[ImageReference]
        auto_image_build: Optional[Union[str, AutoImageBuildStatus]]
        extends: Optional[ImageDefinitionReference]
        file_url: Optional[str]
        image_reference: Optional[ImageReference]
        image_validation_error_details: Optional[ImageValidationErrorDetails]
        image_validation_status: Optional[Union[str, ImageValidationStatus]]
        latest_build: Optional[LatestImageBuild]
        tasks: Optional[list[CustomizationTaskInstance]]
        user_tasks: Optional[list[CustomizationTaskInstance]]
        validation_status: Optional[Union[str, CatalogResourceValidationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                extends: Optional[ImageDefinitionReference] = ..., 
                image_reference: Optional[ImageReference] = ..., 
                latest_build: Optional[LatestImageBuild] = ..., 
                tasks: Optional[list[CustomizationTaskInstance]] = ..., 
                user_tasks: Optional[list[CustomizationTaskInstance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageDefinitionReference(_Model):
        image_definition: str
        parameters: Optional[list[DefinitionParametersItem]]

        @overload
        def __init__(
                self, 
                *, 
                image_definition: str, 
                parameters: Optional[list[DefinitionParametersItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageProperties(_Model):
        architecture: Optional[Union[str, ArchitectureType]]
        description: Optional[str]
        hibernate_support: Optional[Union[str, HibernateSupport]]
        offer: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        publisher: Optional[str]
        recommended_machine_configuration: Optional[RecommendedMachineConfiguration]
        sku: Optional[str]


    class azure.mgmt.devcenter.models.ImageReference(_Model):
        exact_version: Optional[str]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageValidationErrorDetails(_Model):
        code: Optional[str]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.devcenter.models.ImageVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ImageVersionProperties(_Model):
        exclude_from_latest: Optional[bool]
        name: Optional[str]
        os_disk_image_size_in_gb: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        published_date: Optional[datetime]


    class azure.mgmt.devcenter.models.InheritedProjectCatalogSettings(_Model):
        catalog_item_sync_enable_status: Optional[Union[str, CatalogItemSyncEnableStatus]]
        default_status: Optional[Union[str, FeatureStatus]]
        default_values: Optional[list[DefaultValue]]
        status_modifiable: Optional[Union[str, FeatureStateModifiable]]
        values_modifiable: Optional[Union[str, FeatureStateModifiable]]

        @overload
        def __init__(
                self, 
                *, 
                catalog_item_sync_enable_status: Optional[Union[str, CatalogItemSyncEnableStatus]] = ..., 
                default_status: Optional[Union[str, FeatureStatus]] = ..., 
                default_values: Optional[list[DefaultValue]] = ..., 
                status_modifiable: Optional[Union[str, FeatureStateModifiable]] = ..., 
                values_modifiable: Optional[Union[str, FeatureStateModifiable]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.InheritedSettingsForProject(_Model):
        azure_ai_services_settings: Optional[FeatureState]
        dev_box_limits_settings: Optional[FeatureState]
        dev_box_schedule_delete_settings: Optional[FeatureState]
        dev_box_tunnel_settings: Optional[FeatureState]
        display_name_settings: Optional[FeatureState]
        network_settings: Optional[ProjectNetworkSettings]
        project_catalog_settings: Optional[InheritedProjectCatalogSettings]
        serverless_gpu_sessions_settings: Optional[FeatureState]
        user_customizations_settings: Optional[FeatureState]
        workspace_storage_settings: Optional[FeatureState]


    class azure.mgmt.devcenter.models.InstallAzureMonitorAgentEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.KeepAwakeEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.KeyEncryptionKeyIdentityUpdate(_Model):
        type: Optional[Union[str, CmkIdentityType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CmkIdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.LatestImageBuild(_Model):
        end_time: Optional[datetime]
        name: Optional[str]
        start_time: Optional[datetime]
        status: Optional[Union[str, ImageDefinitionBuildStatus]]


    class azure.mgmt.devcenter.models.LicenseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WINDOWS_CLIENT = "Windows_Client"


    class azure.mgmt.devcenter.models.LocalAdminStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.devcenter.models.MicrosoftHostedNetworkEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.NetworkConnection(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[NetworkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[NetworkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.NetworkConnectionUpdate(_Model):
        location: Optional[str]
        properties: Optional[NetworkConnectionUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[NetworkConnectionUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.NetworkConnectionUpdateProperties(_Model):
        domain_name: Optional[str]
        domain_password: Optional[str]
        domain_username: Optional[str]
        organization_unit: Optional[str]
        subnet_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.NetworkProperties(NetworkConnectionUpdateProperties):
        domain_join_type: Union[str, DomainJoinType]
        domain_name: str
        domain_password: str
        domain_username: str
        health_check_status: Optional[Union[str, HealthCheckStatus]]
        networking_resource_group_name: Optional[str]
        organization_unit: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        subnet_id: str

        @overload
        def __init__(
                self, 
                *, 
                domain_join_type: Union[str, DomainJoinType], 
                domain_name: Optional[str] = ..., 
                domain_password: Optional[str] = ..., 
                domain_username: Optional[str] = ..., 
                networking_resource_group_name: Optional[str] = ..., 
                organization_unit: Optional[str] = ..., 
                subnet_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.Operation(_Model):
        action_type: Optional[Union[str, ActionType]]
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[Union[str, Origin]]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.devcenter.models.OperationStatus(OperationStatusResult):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
        properties: Optional[dict[str, Any]]
        resource_id: str
        start_time: datetime
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.devcenter.models.OutboundEnvironmentEndpoint(_Model):
        category: Optional[str]
        endpoints: Optional[list[EndpointDependency]]


    class azure.mgmt.devcenter.models.ParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRAY = "array"
        BOOLEAN = "boolean"
        INTEGER = "integer"
        NUMBER = "number"
        OBJECT = "object"
        STRING = "string"


    class azure.mgmt.devcenter.models.PolicyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.devcenter.models.Pool(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[PoolProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[PoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.PoolDevBoxDefinition(_Model):
        active_image_reference: Optional[ImageReference]
        image_reference: Optional[ImageReference]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                image_reference: Optional[ImageReference] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.PoolDevBoxDefinitionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REFERENCE = "Reference"
        VALUE = "Value"


    class azure.mgmt.devcenter.models.PoolProperties(PoolUpdateProperties):
        active_hours_configuration: ActiveHoursConfiguration
        dev_box_count: Optional[int]
        dev_box_definition: PoolDevBoxDefinition
        dev_box_definition_name: str
        dev_box_definition_type: Union[str, PoolDevBoxDefinitionType]
        dev_box_tunnel_enable_status: Union[str, DevBoxTunnelEnableStatus]
        display_name: str
        health_status: Optional[Union[str, HealthStatus]]
        health_status_details: Optional[list[HealthStatusDetail]]
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        stop_on_no_connect: StopOnNoConnectConfiguration
        virtual_network_type: Union[str, VirtualNetworkType]

        @overload
        def __init__(
                self, 
                *, 
                active_hours_configuration: Optional[ActiveHoursConfiguration] = ..., 
                dev_box_definition: Optional[PoolDevBoxDefinition] = ..., 
                dev_box_definition_name: Optional[str] = ..., 
                dev_box_definition_type: Optional[Union[str, PoolDevBoxDefinitionType]] = ..., 
                dev_box_tunnel_enable_status: Optional[Union[str, DevBoxTunnelEnableStatus]] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                managed_virtual_network_regions: Optional[list[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                stop_on_no_connect: Optional[StopOnNoConnectConfiguration] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.PoolUpdate(_Model):
        location: Optional[str]
        properties: Optional[PoolUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PoolUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.PoolUpdateProperties(_Model):
        active_hours_configuration: Optional[ActiveHoursConfiguration]
        dev_box_definition: Optional[PoolDevBoxDefinition]
        dev_box_definition_name: Optional[str]
        dev_box_definition_type: Optional[Union[str, PoolDevBoxDefinitionType]]
        dev_box_tunnel_enable_status: Optional[Union[str, DevBoxTunnelEnableStatus]]
        display_name: Optional[str]
        license_type: Optional[Union[str, LicenseType]]
        local_administrator: Optional[Union[str, LocalAdminStatus]]
        managed_virtual_network_regions: Optional[list[str]]
        network_connection_name: Optional[str]
        single_sign_on_status: Optional[Union[str, SingleSignOnStatus]]
        stop_on_disconnect: Optional[StopOnDisconnectConfiguration]
        stop_on_no_connect: Optional[StopOnNoConnectConfiguration]
        virtual_network_type: Optional[Union[str, VirtualNetworkType]]

        @overload
        def __init__(
                self, 
                *, 
                active_hours_configuration: Optional[ActiveHoursConfiguration] = ..., 
                dev_box_definition: Optional[PoolDevBoxDefinition] = ..., 
                dev_box_definition_name: Optional[str] = ..., 
                dev_box_definition_type: Optional[Union[str, PoolDevBoxDefinitionType]] = ..., 
                dev_box_tunnel_enable_status: Optional[Union[str, DevBoxTunnelEnableStatus]] = ..., 
                display_name: Optional[str] = ..., 
                license_type: Optional[Union[str, LicenseType]] = ..., 
                local_administrator: Optional[Union[str, LocalAdminStatus]] = ..., 
                managed_virtual_network_regions: Optional[list[str]] = ..., 
                network_connection_name: Optional[str] = ..., 
                single_sign_on_status: Optional[Union[str, SingleSignOnStatus]] = ..., 
                stop_on_disconnect: Optional[StopOnDisconnectConfiguration] = ..., 
                stop_on_no_connect: Optional[StopOnNoConnectConfiguration] = ..., 
                virtual_network_type: Optional[Union[str, VirtualNetworkType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.Project(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ProjectProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectCatalogSettings(_Model):
        catalog_item_sync_types: Optional[list[Union[str, CatalogItemType]]]

        @overload
        def __init__(
                self, 
                *, 
                catalog_item_sync_types: Optional[list[Union[str, CatalogItemType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectCustomizationIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.devcenter.models.ProjectCustomizationManagedIdentity(_Model):
        identity_resource_id: Optional[str]
        identity_type: Optional[Union[str, ProjectCustomizationIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, ProjectCustomizationIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectCustomizationSettings(_Model):
        identities: Optional[list[ProjectCustomizationManagedIdentity]]
        user_customizations_enable_status: Optional[Union[str, UserCustomizationsEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                identities: Optional[list[ProjectCustomizationManagedIdentity]] = ..., 
                user_customizations_enable_status: Optional[Union[str, UserCustomizationsEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectEnvironmentType(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ProjectEnvironmentTypeProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ProjectEnvironmentTypeProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeProperties(ProjectEnvironmentTypeUpdateProperties):
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        environment_count: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Union[str, EnvironmentTypeEnableStatus]
        user_role_assignments: dict[str, UserRoleAssignmentValue]

        @overload
        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                user_role_assignments: Optional[dict[str, UserRoleAssignmentValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ProjectEnvironmentTypeUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ProjectEnvironmentTypeUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdateProperties(_Model):
        creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment]
        deployment_target_id: Optional[str]
        display_name: Optional[str]
        status: Optional[Union[str, EnvironmentTypeEnableStatus]]
        user_role_assignments: Optional[dict[str, UserRoleAssignmentValue]]

        @overload
        def __init__(
                self, 
                *, 
                creator_role_assignment: Optional[ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment] = ..., 
                deployment_target_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                status: Optional[Union[str, EnvironmentTypeEnableStatus]] = ..., 
                user_role_assignments: Optional[dict[str, UserRoleAssignmentValue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment(_Model):
        roles: Optional[dict[str, EnvironmentRole]]

        @overload
        def __init__(
                self, 
                *, 
                roles: Optional[dict[str, EnvironmentRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectNetworkSettings(_Model):
        microsoft_hosted_network_enable_status: Optional[Union[str, MicrosoftHostedNetworkEnableStatus]]


    class azure.mgmt.devcenter.models.ProjectPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[ProjectPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectPolicyProperties(ProjectPolicyUpdateProperties):
        configuration_policies: ConfigurationPolicies
        provisioning_state: Optional[Union[str, ProvisioningState]]
        resource_policies: list[ResourcePolicy]
        scopes: list[str]

        @overload
        def __init__(
                self, 
                *, 
                configuration_policies: Optional[ConfigurationPolicies] = ..., 
                resource_policies: Optional[list[ResourcePolicy]] = ..., 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectPolicyUpdate(_Model):
        properties: Optional[ProjectPolicyUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProjectPolicyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.ProjectPolicyUpdateProperties(_Model):
        configuration_policies: Optional[ConfigurationPolicies]
        resource_policies: Optional[list[ResourcePolicy]]
        scopes: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                configuration_policies: Optional[ConfigurationPolicies] = ..., 
                resource_policies: Optional[list[ResourcePolicy]] = ..., 
                scopes: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectProperties(ProjectUpdateProperties):
        assigned_groups: list[AssignedGroup]
        azure_ai_services_settings: AzureAiServicesSettings
        catalog_settings: ProjectCatalogSettings
        customization_settings: ProjectCustomizationSettings
        description: str
        dev_box_schedule_delete_settings: DevBoxScheduleDeleteSettings
        dev_center_id: str
        dev_center_uri: Optional[str]
        display_name: str
        max_dev_boxes_per_user: int
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serverless_gpu_sessions_settings: ServerlessGpuSessionsSettings
        workspace_storage_settings: WorkspaceStorageSettings

        @overload
        def __init__(
                self, 
                *, 
                assigned_groups: Optional[list[AssignedGroup]] = ..., 
                azure_ai_services_settings: Optional[AzureAiServicesSettings] = ..., 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                customization_settings: Optional[ProjectCustomizationSettings] = ..., 
                description: Optional[str] = ..., 
                dev_box_schedule_delete_settings: Optional[DevBoxScheduleDeleteSettings] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ..., 
                serverless_gpu_sessions_settings: Optional[ServerlessGpuSessionsSettings] = ..., 
                workspace_storage_settings: Optional[WorkspaceStorageSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ProjectUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        properties: Optional[ProjectUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProjectUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.ProjectUpdateProperties(_Model):
        assigned_groups: Optional[list[AssignedGroup]]
        azure_ai_services_settings: Optional[AzureAiServicesSettings]
        catalog_settings: Optional[ProjectCatalogSettings]
        customization_settings: Optional[ProjectCustomizationSettings]
        description: Optional[str]
        dev_box_schedule_delete_settings: Optional[DevBoxScheduleDeleteSettings]
        dev_center_id: Optional[str]
        display_name: Optional[str]
        max_dev_boxes_per_user: Optional[int]
        serverless_gpu_sessions_settings: Optional[ServerlessGpuSessionsSettings]
        workspace_storage_settings: Optional[WorkspaceStorageSettings]

        @overload
        def __init__(
                self, 
                *, 
                assigned_groups: Optional[list[AssignedGroup]] = ..., 
                azure_ai_services_settings: Optional[AzureAiServicesSettings] = ..., 
                catalog_settings: Optional[ProjectCatalogSettings] = ..., 
                customization_settings: Optional[ProjectCustomizationSettings] = ..., 
                description: Optional[str] = ..., 
                dev_box_schedule_delete_settings: Optional[DevBoxScheduleDeleteSettings] = ..., 
                dev_center_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                max_dev_boxes_per_user: Optional[int] = ..., 
                serverless_gpu_sessions_settings: Optional[ServerlessGpuSessionsSettings] = ..., 
                workspace_storage_settings: Optional[WorkspaceStorageSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.devcenter.models.RecommendedMachineConfiguration(_Model):
        memory: Optional[ResourceRange]
        v_cp_us: Optional[ResourceRange]


    class azure.mgmt.devcenter.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.devcenter.models.ResourcePolicy(_Model):
        action: Optional[Union[str, PolicyAction]]
        filter: Optional[str]
        resource_type: Optional[Union[str, DevCenterResourceType]]
        resources: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, PolicyAction]] = ..., 
                filter: Optional[str] = ..., 
                resource_type: Optional[Union[str, DevCenterResourceType]] = ..., 
                resources: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ResourceRange(_Model):
        max: Optional[int]
        min: Optional[int]


    class azure.mgmt.devcenter.models.Schedule(ProxyResource):
        id: str
        name: str
        properties: Optional[ScheduleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ScheduleEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.ScheduleProperties(ScheduleUpdateProperties):
        frequency: Union[str, ScheduledFrequency]
        location: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]

        @overload
        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, ScheduledType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ScheduleUpdate(_Model):
        properties: Optional[ScheduleUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScheduleUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.devcenter.models.ScheduleUpdateProperties(_Model):
        frequency: Optional[Union[str, ScheduledFrequency]]
        location: Optional[str]
        state: Optional[Union[str, ScheduleEnableStatus]]
        tags: Optional[dict[str, str]]
        time: Optional[str]
        time_zone: Optional[str]
        type: Optional[Union[str, ScheduledType]]

        @overload
        def __init__(
                self, 
                *, 
                frequency: Optional[Union[str, ScheduledFrequency]] = ..., 
                location: Optional[str] = ..., 
                state: Optional[Union[str, ScheduleEnableStatus]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                time: Optional[str] = ..., 
                time_zone: Optional[str] = ..., 
                type: Optional[Union[str, ScheduledType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.ScheduledFrequency(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DAILY = "Daily"


    class azure.mgmt.devcenter.models.ScheduledType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STOP_DEV_BOX = "StopDevBox"


    class azure.mgmt.devcenter.models.ServerlessGpuSessionsMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_DEPLOY = "AutoDeploy"
        DISABLED = "Disabled"


    class azure.mgmt.devcenter.models.ServerlessGpuSessionsSettings(_Model):
        max_concurrent_sessions_per_project: Optional[int]
        serverless_gpu_sessions_mode: Optional[Union[str, ServerlessGpuSessionsMode]]

        @overload
        def __init__(
                self, 
                *, 
                max_concurrent_sessions_per_project: Optional[int] = ..., 
                serverless_gpu_sessions_mode: Optional[Union[str, ServerlessGpuSessionsMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.SingleSignOnStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.devcenter.models.StopOnDisconnectConfiguration(_Model):
        grace_period_minutes: Optional[int]
        status: Optional[Union[str, StopOnDisconnectEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                grace_period_minutes: Optional[int] = ..., 
                status: Optional[Union[str, StopOnDisconnectEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.StopOnDisconnectEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.StopOnNoConnectConfiguration(_Model):
        grace_period_minutes: Optional[int]
        status: Optional[Union[str, StopOnNoConnectEnableStatus]]

        @overload
        def __init__(
                self, 
                *, 
                grace_period_minutes: Optional[int] = ..., 
                status: Optional[Union[str, StopOnNoConnectEnableStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.StopOnNoConnectEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.SyncErrorDetails(_Model):
        conflicts: Optional[list[CatalogConflictError]]
        errors: Optional[list[CatalogSyncError]]
        operation_error: Optional[CatalogErrorDetails]


    class azure.mgmt.devcenter.models.SyncStats(_Model):
        added: Optional[int]
        removed: Optional[int]
        synced_catalog_item_types: Optional[list[Union[str, CatalogItemType]]]
        synchronization_errors: Optional[int]
        unchanged: Optional[int]
        updated: Optional[int]
        validation_errors: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                synced_catalog_item_types: Optional[list[Union[str, CatalogItemType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, CreatedByType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, CreatedByType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.Usage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[UsageName]
        unit: Optional[Union[str, UsageUnit]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[int] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[int] = ..., 
                name: Optional[UsageName] = ..., 
                unit: Optional[Union[str, UsageUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.UsageName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.devcenter.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.devcenter.models.UserCustomizationsEnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.devcenter.models.UserRoleAssignmentValue(_Model):
        roles: Optional[dict[str, EnvironmentRole]]

        @overload
        def __init__(
                self, 
                *, 
                roles: Optional[dict[str, EnvironmentRole]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.devcenter.models.VirtualNetworkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED = "Managed"
        UNMANAGED = "Unmanaged"


    class azure.mgmt.devcenter.models.WorkspaceStorageMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_DEPLOY = "AutoDeploy"
        DISABLED = "Disabled"


    class azure.mgmt.devcenter.models.WorkspaceStorageSettings(_Model):
        workspace_storage_mode: Optional[Union[str, WorkspaceStorageMode]]

        @overload
        def __init__(
                self, 
                *, 
                workspace_storage_mode: Optional[Union[str, WorkspaceStorageMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.devcenter.operations

    class azure.mgmt.devcenter.operations.AttachedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AttachedNetworkConnection]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AttachedNetworkConnection]: ...


    class azure.mgmt.devcenter.operations.CatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Catalog]: ...


    class azure.mgmt.devcenter.operations.CheckNameAvailabilityOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

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


    class azure.mgmt.devcenter.operations.CustomizationTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> CustomizationTask: ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[CustomizationTask]: ...


    class azure.mgmt.devcenter.operations.DevBoxDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevBoxDefinition]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevBoxDefinition]: ...


    class azure.mgmt.devcenter.operations.DevCenterCatalogImageDefinitionBuildOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuild: ...

        @distributed_trace
        def get_build_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuildDetails: ...


    class azure.mgmt.devcenter.operations.DevCenterCatalogImageDefinitionBuildsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image_definition(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImageDefinitionBuild]: ...


    class azure.mgmt.devcenter.operations.DevCenterCatalogImageDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_build_image(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_by_dev_center_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ImageDefinition: ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_dev_center_catalog(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ImageDefinition]: ...


    class azure.mgmt.devcenter.operations.DevCentersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevCenter]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevCenter]: ...


    class azure.mgmt.devcenter.operations.EncryptionSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: DevCenterEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: DevCenterEncryptionSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: EncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: EncryptionSetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DevCenterEncryptionSet]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                encryption_set_name: str, 
                **kwargs: Any
            ) -> DevCenterEncryptionSet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevCenterEncryptionSet]: ...


    class azure.mgmt.devcenter.operations.EnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EnvironmentDefinition]: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnvironmentDefinition]: ...


    class azure.mgmt.devcenter.operations.EnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EnvironmentType]: ...

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
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Gallery]: ...


    class azure.mgmt.devcenter.operations.ImageVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
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
            ) -> ItemPaged[ImageVersion]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImageVersion]: ...


    class azure.mgmt.devcenter.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def get_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...

        @distributed_trace
        def list_by_gallery(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                gallery_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...


    class azure.mgmt.devcenter.operations.NetworkConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NetworkConnection]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[NetworkConnection]: ...

        @distributed_trace
        def list_health_details(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[HealthCheckStatusDetails]: ...

        @distributed_trace
        def list_outbound_network_dependencies_endpoints(
                self, 
                resource_group_name: str, 
                network_connection_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[OutboundEnvironmentEndpoint]: ...


    class azure.mgmt.devcenter.operations.OperationStatusesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.devcenter.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Pool]: ...


    class azure.mgmt.devcenter.operations.ProjectAllowedEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AllowedEnvironmentType]: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogEnvironmentDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                environment_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogImageDefinitionBuildOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_cancel(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuild: ...

        @distributed_trace
        def get_build_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                build_name: str, 
                **kwargs: Any
            ) -> ImageDefinitionBuildDetails: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogImageDefinitionBuildsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_image_definition(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ImageDefinitionBuild]: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogImageDefinitionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_build_image(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> ImageDefinition: ...

        @distributed_trace
        def get_error_details(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                image_definition_name: str, 
                **kwargs: Any
            ) -> CatalogResourceValidationErrorDetails: ...

        @distributed_trace
        def list_by_project_catalog(
                self, 
                resource_group_name: str, 
                project_name: str, 
                catalog_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ImageDefinition]: ...


    class azure.mgmt.devcenter.operations.ProjectCatalogsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Catalog]: ...


    class azure.mgmt.devcenter.operations.ProjectEnvironmentTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectEnvironmentType]: ...

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


    class azure.mgmt.devcenter.operations.ProjectPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: ProjectPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                project_policy_name: str, 
                **kwargs: Any
            ) -> ProjectPolicy: ...

        @distributed_trace
        def list_by_dev_center(
                self, 
                resource_group_name: str, 
                dev_center_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ProjectPolicy]: ...


    class azure.mgmt.devcenter.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
        def get_inherited_settings(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> InheritedSettingsForProject: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...


    class azure.mgmt.devcenter.operations.SchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: Schedule, 
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                *, 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                body: ScheduleUpdate, 
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
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
                *, 
                content_type: str = "application/json", 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[Schedule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                schedule_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> Schedule: ...

        @distributed_trace
        def list_by_pool(
                self, 
                resource_group_name: str, 
                project_name: str, 
                pool_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Schedule]: ...


    class azure.mgmt.devcenter.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_project(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DevCenterSku]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DevCenterSku]: ...


    class azure.mgmt.devcenter.operations.UsagesOperations:

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
            ) -> ItemPaged[Usage]: ...


namespace azure.mgmt.devcenter.types

    class azure.mgmt.devcenter.types.ActiveHoursConfiguration(TypedDict, total=False):
        key "autoStartEnableStatus": Union[str, AutoStartEnableStatus]
        key "daysOfWeekLimit": int
        key "defaultEndTimeHour": int
        key "defaultStartTimeHour": int
        key "defaultTimeZone": str
        key "keepAwakeEnableStatus": Union[str, KeepAwakeEnableStatus]
        auto_start_enable_status: Union[str, AutoStartEnableStatus]
        days_of_week_limit: int
        defaultDaysOfWeek: list[Union[str, DayOfWeek]]
        default_days_of_week: list[Union[str, DayOfWeek]]
        default_end_time_hour: int
        default_start_time_hour: int
        default_time_zone: str
        keep_awake_enable_status: Union[str, KeepAwakeEnableStatus]


    class azure.mgmt.devcenter.types.AssignedGroup(TypedDict, total=False):
        key "objectId": str
        key "scope": Union[str, AssignedGroupScope]
        object_id: str
        scope: Union[str, AssignedGroupScope]


    class azure.mgmt.devcenter.types.AttachedNetworkConnection(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AttachedNetworkConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AttachedNetworkConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.AttachedNetworkConnectionProperties(TypedDict, total=False):
        key "domainJoinType": Union[str, DomainJoinType]
        key "healthCheckStatus": Union[str, HealthCheckStatus]
        key "networkConnectionId": str
        key "networkConnectionLocation": str
        key "provisioningState": Union[str, ProvisioningState]
        domain_join_type: Union[str, DomainJoinType]
        health_check_status: Union[str, HealthCheckStatus]
        network_connection_id: str
        network_connection_location: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.devcenter.types.AzureAiServicesSettings(TypedDict, total=False):
        key "azureAiServicesMode": Union[str, AzureAiServicesMode]
        azure_ai_services_mode: Union[str, AzureAiServicesMode]


    class azure.mgmt.devcenter.types.Catalog(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('CatalogProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CatalogProperties
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.CatalogProperties(CatalogUpdateProperties):
        key "adoGit": ForwardRef('GitCatalog', module='types')
        key "autoImageBuildEnableStatus": Union[str, CatalogAutoImageBuildEnableStatus]
        key "connectionState": Union[str, CatalogConnectionState]
        key "gitHub": ForwardRef('GitCatalog', module='types')
        key "lastConnectionTime": str
        key "lastSyncStats": ForwardRef('SyncStats', module='types')
        key "lastSyncTime": str
        key "provisioningState": Union[str, ProvisioningState]
        key "syncState": Union[str, CatalogSyncState]
        key "syncType": Union[str, CatalogSyncType]
        ado_git: GitCatalog
        auto_image_build_enable_status: Union[str, CatalogAutoImageBuildEnableStatus]
        connection_state: Union[str, CatalogConnectionState]
        git_hub: GitCatalog
        last_connection_time: str
        last_sync_stats: SyncStats
        last_sync_time: str
        provisioning_state: Union[str, ProvisioningState]
        sync_state: Union[str, CatalogSyncState]
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.CatalogUpdate(TypedDict, total=False):
        key "properties": ForwardRef('CatalogUpdateProperties', module='types')
        properties: CatalogUpdateProperties


    class azure.mgmt.devcenter.types.CatalogUpdateProperties(TypedDict, total=False):
        key "adoGit": ForwardRef('GitCatalog', module='types')
        key "autoImageBuildEnableStatus": Union[str, CatalogAutoImageBuildEnableStatus]
        key "gitHub": ForwardRef('GitCatalog', module='types')
        key "syncType": Union[str, CatalogSyncType]
        ado_git: GitCatalog
        auto_image_build_enable_status: Union[str, CatalogAutoImageBuildEnableStatus]
        git_hub: GitCatalog
        sync_type: Union[str, CatalogSyncType]
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.devcenter.types.CheckScopedNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "scope": str
        key "type": str
        name: str
        scope: str
        type: str


    class azure.mgmt.devcenter.types.ConfigurationPolicies(TypedDict, total=False):
        key "azureAiServicesFeatureStatus": ForwardRef('FeatureState', module='types')
        key "devBoxLimitsFeatureStatus": ForwardRef('FeatureState', module='types')
        key "devBoxScheduleDeleteFeatureStatus": ForwardRef('FeatureState', module='types')
        key "devBoxTunnelFeatureStatus": ForwardRef('FeatureState', module='types')
        key "displayNameFeatureStatus": ForwardRef('FeatureState', module='types')
        key "projectCatalogFeatureStatus": ForwardRef('FeatureState', module='types')
        key "serverlessGpuSessionsFeatureStatus": ForwardRef('FeatureState', module='types')
        key "userCustomizationsFeatureStatus": ForwardRef('FeatureState', module='types')
        key "workspaceStorageFeatureStatus": ForwardRef('FeatureState', module='types')
        azure_ai_services_feature_status: FeatureState
        dev_box_limits_feature_status: FeatureState
        dev_box_schedule_delete_feature_status: FeatureState
        dev_box_tunnel_feature_status: FeatureState
        display_name_feature_status: FeatureState
        project_catalog_feature_status: FeatureState
        serverless_gpu_sessions_feature_status: FeatureState
        user_customizations_feature_status: FeatureState
        workspace_storage_feature_status: FeatureState


    class azure.mgmt.devcenter.types.CustomerManagedKeyEncryption(TypedDict, total=False):
        key "keyEncryptionKeyIdentity": ForwardRef('CustomerManagedKeyEncryptionKeyIdentity', module='types')
        key "keyEncryptionKeyUrl": str
        key_encryption_key_identity: CustomerManagedKeyEncryptionKeyIdentity
        key_encryption_key_url: str


    class azure.mgmt.devcenter.types.CustomerManagedKeyEncryptionKeyIdentity(TypedDict, total=False):
        key "delegatedIdentityClientId": str
        key "federatedClientId": str
        key "identityType": Union[str, IdentityType]
        key "userAssignedIdentityResourceId": str
        delegated_identity_client_id: str
        federated_client_id: str
        identity_type: Union[str, IdentityType]
        user_assigned_identity_resource_id: str


    class azure.mgmt.devcenter.types.DefaultValue(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.devcenter.types.DevBoxDefinition(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DevBoxDefinitionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: DevBoxDefinitionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.DevBoxDefinitionProperties(DevBoxDefinitionUpdateProperties):
        key "activeImageReference": ForwardRef('ImageReference', module='types')
        key "hibernateSupport": Union[str, HibernateSupport]
        key "imageReference": ForwardRef('ImageReference', module='types')
        key "imageValidationErrorDetails": ForwardRef('ImageValidationErrorDetails', module='types')
        key "imageValidationStatus": Union[str, ImageValidationStatus]
        key "osStorageType": str
        key "provisioningState": Union[str, ProvisioningState]
        key "sku": ForwardRef('Sku', module='types')
        key "validationStatus": Union[str, CatalogResourceValidationStatus]
        active_image_reference: ImageReference
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        image_validation_error_details: ImageValidationErrorDetails
        image_validation_status: Union[str, ImageValidationStatus]
        os_storage_type: str
        provisioning_state: Union[str, ProvisioningState]
        sku: Sku
        validation_status: Union[str, CatalogResourceValidationStatus]


    class azure.mgmt.devcenter.types.DevBoxDefinitionUpdate(TypedDict, total=False):
        key "location": str
        key "properties": ForwardRef('DevBoxDefinitionUpdateProperties', module='types')
        location: str
        properties: DevBoxDefinitionUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.DevBoxDefinitionUpdateProperties(TypedDict, total=False):
        key "hibernateSupport": Union[str, HibernateSupport]
        key "imageReference": ForwardRef('ImageReference', module='types')
        key "osStorageType": str
        key "sku": ForwardRef('Sku', module='types')
        hibernate_support: Union[str, HibernateSupport]
        image_reference: ImageReference
        os_storage_type: str
        sku: Sku


    class azure.mgmt.devcenter.types.DevBoxProvisioningSettings(TypedDict, total=False):
        key "installAzureMonitorAgentEnableStatus": Union[str, InstallAzureMonitorAgentEnableStatus]
        install_azure_monitor_agent_enable_status: Union[str, InstallAzureMonitorAgentEnableStatus]


    class azure.mgmt.devcenter.types.DevBoxScheduleDeleteSettings(TypedDict, total=False):
        key "cancelOnConnectEnableStatus": Union[str, CancelOnConnectEnableStatus]
        key "deleteMode": Union[str, DevBoxDeleteMode]
        key "gracePeriod": str
        key "inactiveThreshold": str
        cancel_on_connect_enable_status: Union[str, CancelOnConnectEnableStatus]
        delete_mode: Union[str, DevBoxDeleteMode]
        grace_period: str
        inactive_threshold: str


    class azure.mgmt.devcenter.types.DevCenter(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DevCenterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: DevCenterProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.DevCenterEncryptionSet(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('DevCenterEncryptionSetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: DevCenterEncryptionSetProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.DevCenterEncryptionSetProperties(DevCenterEncryptionSetUpdateProperties):
        key "devboxDisksEncryptionEnableStatus": Union[str, DevboxDisksEncryptionEnableStatus]
        key "keyEncryptionKeyIdentity": ForwardRef('KeyEncryptionKeyIdentityUpdate', module='types')
        key "keyEncryptionKeyUrl": str
        key "provisioningState": Union[str, ProvisioningState]
        devbox_disks_encryption_enable_status: Union[str, DevboxDisksEncryptionEnableStatus]
        key_encryption_key_identity: KeyEncryptionKeyIdentityUpdate
        key_encryption_key_url: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.devcenter.types.DevCenterEncryptionSetUpdateProperties(TypedDict, total=False):
        key "devboxDisksEncryptionEnableStatus": Union[str, DevboxDisksEncryptionEnableStatus]
        key "keyEncryptionKeyIdentity": ForwardRef('KeyEncryptionKeyIdentityUpdate', module='types')
        key "keyEncryptionKeyUrl": str
        devbox_disks_encryption_enable_status: Union[str, DevboxDisksEncryptionEnableStatus]
        key_encryption_key_identity: KeyEncryptionKeyIdentityUpdate
        key_encryption_key_url: str


    class azure.mgmt.devcenter.types.DevCenterNetworkSettings(TypedDict, total=False):
        key "microsoftHostedNetworkEnableStatus": Union[str, MicrosoftHostedNetworkEnableStatus]
        microsoft_hosted_network_enable_status: Union[str, MicrosoftHostedNetworkEnableStatus]


    class azure.mgmt.devcenter.types.DevCenterProjectCatalogSettings(TypedDict, total=False):
        key "catalogItemSyncEnableStatus": Union[str, CatalogItemSyncEnableStatus]
        catalog_item_sync_enable_status: Union[str, CatalogItemSyncEnableStatus]


    class azure.mgmt.devcenter.types.DevCenterProperties(DevCenterUpdateProperties):
        key "devBoxProvisioningSettings": ForwardRef('DevBoxProvisioningSettings', module='types')
        key "devCenterUri": str
        key "displayName": str
        key "encryption": ForwardRef('Encryption', module='types')
        key "networkSettings": ForwardRef('DevCenterNetworkSettings', module='types')
        key "projectCatalogSettings": ForwardRef('DevCenterProjectCatalogSettings', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        dev_box_provisioning_settings: DevBoxProvisioningSettings
        dev_center_uri: str
        display_name: str
        encryption: Encryption
        network_settings: DevCenterNetworkSettings
        project_catalog_settings: DevCenterProjectCatalogSettings
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.devcenter.types.DevCenterUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "properties": ForwardRef('DevCenterUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        location: str
        properties: DevCenterUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.DevCenterUpdateProperties(TypedDict, total=False):
        key "devBoxProvisioningSettings": ForwardRef('DevBoxProvisioningSettings', module='types')
        key "displayName": str
        key "encryption": ForwardRef('Encryption', module='types')
        key "networkSettings": ForwardRef('DevCenterNetworkSettings', module='types')
        key "projectCatalogSettings": ForwardRef('DevCenterProjectCatalogSettings', module='types')
        dev_box_provisioning_settings: DevBoxProvisioningSettings
        display_name: str
        encryption: Encryption
        network_settings: DevCenterNetworkSettings
        project_catalog_settings: DevCenterProjectCatalogSettings


    class azure.mgmt.devcenter.types.Encryption(TypedDict, total=False):
        key "customerManagedKeyEncryption": ForwardRef('CustomerManagedKeyEncryption', module='types')
        customer_managed_key_encryption: CustomerManagedKeyEncryption


    class azure.mgmt.devcenter.types.EncryptionSetUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "properties": ForwardRef('DevCenterEncryptionSetUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        location: str
        properties: DevCenterEncryptionSetUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.EnvironmentRole(TypedDict, total=False):
        key "description": str
        key "roleName": str
        description: str
        role_name: str


    class azure.mgmt.devcenter.types.EnvironmentType(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('EnvironmentTypeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: EnvironmentTypeProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.EnvironmentTypeProperties(EnvironmentTypeUpdateProperties):
        key "displayName": str
        key "provisioningState": Union[str, ProvisioningState]
        display_name: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.devcenter.types.EnvironmentTypeUpdate(TypedDict, total=False):
        key "properties": ForwardRef('EnvironmentTypeUpdateProperties', module='types')
        properties: EnvironmentTypeUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.EnvironmentTypeUpdateProperties(TypedDict, total=False):
        key "displayName": str
        display_name: str


    class azure.mgmt.devcenter.types.FeatureState(TypedDict, total=False):
        key "defaultStatus": Union[str, FeatureStatus]
        key "statusModifiable": Union[str, FeatureStateModifiable]
        key "valuesModifiable": Union[str, FeatureStateModifiable]
        defaultValues: list[DefaultValue]
        default_status: Union[str, FeatureStatus]
        default_values: list[DefaultValue]
        status_modifiable: Union[str, FeatureStateModifiable]
        values_modifiable: Union[str, FeatureStateModifiable]


    class azure.mgmt.devcenter.types.Gallery(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('GalleryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: GalleryProperties
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.GalleryProperties(TypedDict, total=False):
        key "galleryResourceId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        gallery_resource_id: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.devcenter.types.GitCatalog(TypedDict, total=False):
        key "branch": str
        key "path": str
        key "secretIdentifier": str
        key "uri": str
        branch: str
        path: str
        secret_identifier: str
        uri: str


    class azure.mgmt.devcenter.types.HealthStatusDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.devcenter.types.ImageReference(TypedDict, total=False):
        key "exactVersion": str
        key "id": str
        exact_version: str
        id: str


    class azure.mgmt.devcenter.types.ImageValidationErrorDetails(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.devcenter.types.KeyEncryptionKeyIdentityUpdate(TypedDict, total=False):
        key "type": Union[str, CmkIdentityType]
        key "userAssignedIdentityResourceId": str
        type: Union[str, CmkIdentityType]
        user_assigned_identity_resource_id: str


    class azure.mgmt.devcenter.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.devcenter.types.NetworkConnection(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NetworkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NetworkProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.NetworkConnectionUpdate(TypedDict, total=False):
        key "location": str
        key "properties": ForwardRef('NetworkConnectionUpdateProperties', module='types')
        location: str
        properties: NetworkConnectionUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.NetworkConnectionUpdateProperties(TypedDict, total=False):
        key "domainName": str
        key "domainPassword": str
        key "domainUsername": str
        key "organizationUnit": str
        key "subnetId": str
        domain_name: str
        domain_password: str
        domain_username: str
        organization_unit: str
        subnet_id: str


    class azure.mgmt.devcenter.types.NetworkProperties(NetworkConnectionUpdateProperties):
        key "domainJoinType": Required[Union[str, DomainJoinType]]
        key "domainName": str
        key "domainPassword": str
        key "domainUsername": str
        key "healthCheckStatus": Union[str, HealthCheckStatus]
        key "networkingResourceGroupName": str
        key "organizationUnit": str
        key "provisioningState": Union[str, ProvisioningState]
        key "subnetId": str
        domain_join_type: Union[str, DomainJoinType]
        domain_name: str
        domain_password: str
        domain_username: str
        health_check_status: Union[str, HealthCheckStatus]
        networking_resource_group_name: str
        organization_unit: str
        provisioning_state: Union[str, ProvisioningState]
        subnet_id: str


    class azure.mgmt.devcenter.types.Pool(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('PoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PoolProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.PoolDevBoxDefinition(TypedDict, total=False):
        key "activeImageReference": ForwardRef('ImageReference', module='types')
        key "imageReference": ForwardRef('ImageReference', module='types')
        key "sku": ForwardRef('Sku', module='types')
        active_image_reference: ImageReference
        image_reference: ImageReference
        sku: Sku


    class azure.mgmt.devcenter.types.PoolProperties(PoolUpdateProperties):
        key "activeHoursConfiguration": ForwardRef('ActiveHoursConfiguration', module='types')
        key "devBoxCount": int
        key "devBoxDefinition": ForwardRef('PoolDevBoxDefinition', module='types')
        key "devBoxDefinitionName": str
        key "devBoxDefinitionType": Union[str, PoolDevBoxDefinitionType]
        key "devBoxTunnelEnableStatus": Union[str, DevBoxTunnelEnableStatus]
        key "displayName": str
        key "healthStatus": Union[str, HealthStatus]
        key "licenseType": Union[str, LicenseType]
        key "localAdministrator": Union[str, LocalAdminStatus]
        key "networkConnectionName": str
        key "provisioningState": Union[str, ProvisioningState]
        key "singleSignOnStatus": Union[str, SingleSignOnStatus]
        key "stopOnDisconnect": ForwardRef('StopOnDisconnectConfiguration', module='types')
        key "stopOnNoConnect": ForwardRef('StopOnNoConnectConfiguration', module='types')
        key "virtualNetworkType": Union[str, VirtualNetworkType]
        active_hours_configuration: ActiveHoursConfiguration
        dev_box_count: int
        dev_box_definition: PoolDevBoxDefinition
        dev_box_definition_name: str
        dev_box_definition_type: Union[str, PoolDevBoxDefinitionType]
        dev_box_tunnel_enable_status: Union[str, DevBoxTunnelEnableStatus]
        display_name: str
        healthStatusDetails: list[HealthStatusDetail]
        health_status: Union[str, HealthStatus]
        health_status_details: list[HealthStatusDetail]
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        managedVirtualNetworkRegions: list[str]
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        provisioning_state: Union[str, ProvisioningState]
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        stop_on_no_connect: StopOnNoConnectConfiguration
        virtual_network_type: Union[str, VirtualNetworkType]


    class azure.mgmt.devcenter.types.PoolUpdate(TypedDict, total=False):
        key "location": str
        key "properties": ForwardRef('PoolUpdateProperties', module='types')
        location: str
        properties: PoolUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.PoolUpdateProperties(TypedDict, total=False):
        key "activeHoursConfiguration": ForwardRef('ActiveHoursConfiguration', module='types')
        key "devBoxDefinition": ForwardRef('PoolDevBoxDefinition', module='types')
        key "devBoxDefinitionName": str
        key "devBoxDefinitionType": Union[str, PoolDevBoxDefinitionType]
        key "devBoxTunnelEnableStatus": Union[str, DevBoxTunnelEnableStatus]
        key "displayName": str
        key "licenseType": Union[str, LicenseType]
        key "localAdministrator": Union[str, LocalAdminStatus]
        key "networkConnectionName": str
        key "singleSignOnStatus": Union[str, SingleSignOnStatus]
        key "stopOnDisconnect": ForwardRef('StopOnDisconnectConfiguration', module='types')
        key "stopOnNoConnect": ForwardRef('StopOnNoConnectConfiguration', module='types')
        key "virtualNetworkType": Union[str, VirtualNetworkType]
        active_hours_configuration: ActiveHoursConfiguration
        dev_box_definition: PoolDevBoxDefinition
        dev_box_definition_name: str
        dev_box_definition_type: Union[str, PoolDevBoxDefinitionType]
        dev_box_tunnel_enable_status: Union[str, DevBoxTunnelEnableStatus]
        display_name: str
        license_type: Union[str, LicenseType]
        local_administrator: Union[str, LocalAdminStatus]
        managedVirtualNetworkRegions: list[str]
        managed_virtual_network_regions: list[str]
        network_connection_name: str
        single_sign_on_status: Union[str, SingleSignOnStatus]
        stop_on_disconnect: StopOnDisconnectConfiguration
        stop_on_no_connect: StopOnNoConnectConfiguration
        virtual_network_type: Union[str, VirtualNetworkType]


    class azure.mgmt.devcenter.types.Project(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ProjectProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.ProjectCatalogSettings(TypedDict, total=False):
        catalogItemSyncTypes: list[Union[str, CatalogItemType]]
        catalog_item_sync_types: list[Union[str, CatalogItemType]]


    class azure.mgmt.devcenter.types.ProjectCustomizationManagedIdentity(TypedDict, total=False):
        key "identityResourceId": str
        key "identityType": Union[str, ProjectCustomizationIdentityType]
        identity_resource_id: str
        identity_type: Union[str, ProjectCustomizationIdentityType]


    class azure.mgmt.devcenter.types.ProjectCustomizationSettings(TypedDict, total=False):
        key "userCustomizationsEnableStatus": Union[str, UserCustomizationsEnableStatus]
        identities: list[ProjectCustomizationManagedIdentity]
        user_customizations_enable_status: Union[str, UserCustomizationsEnableStatus]


    class azure.mgmt.devcenter.types.ProjectEnvironmentType(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProjectEnvironmentTypeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ProjectEnvironmentTypeProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.ProjectEnvironmentTypeProperties(ProjectEnvironmentTypeUpdateProperties):
        key "creatorRoleAssignment": ForwardRef('ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment', module='types')
        key "deploymentTargetId": str
        key "displayName": str
        key "environmentCount": int
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Union[str, EnvironmentTypeEnableStatus]
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        environment_count: int
        provisioning_state: Union[str, ProvisioningState]
        status: Union[str, EnvironmentTypeEnableStatus]
        userRoleAssignments: dict[str, UserRoleAssignmentValue]
        user_role_assignments: dict[str, UserRoleAssignmentValue]


    class azure.mgmt.devcenter.types.ProjectEnvironmentTypeUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ProjectEnvironmentTypeUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: ProjectEnvironmentTypeUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.ProjectEnvironmentTypeUpdateProperties(TypedDict, total=False):
        key "creatorRoleAssignment": ForwardRef('ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment', module='types')
        key "deploymentTargetId": str
        key "displayName": str
        key "status": Union[str, EnvironmentTypeEnableStatus]
        creator_role_assignment: ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment
        deployment_target_id: str
        display_name: str
        status: Union[str, EnvironmentTypeEnableStatus]
        userRoleAssignments: dict[str, UserRoleAssignmentValue]
        user_role_assignments: dict[str, UserRoleAssignmentValue]


    class azure.mgmt.devcenter.types.ProjectEnvironmentTypeUpdatePropertiesCreatorRoleAssignment(TypedDict, total=False):
        roles: dict[str, EnvironmentRole]


    class azure.mgmt.devcenter.types.ProjectPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ProjectPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProjectPolicyProperties
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.ProjectPolicyProperties(ProjectPolicyUpdateProperties):
        key "configurationPolicies": ForwardRef('ConfigurationPolicies', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        configuration_policies: ConfigurationPolicies
        provisioning_state: Union[str, ProvisioningState]
        resourcePolicies: list[ResourcePolicy]
        resource_policies: list[ResourcePolicy]
        scopes: list[str]


    class azure.mgmt.devcenter.types.ProjectPolicyUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ProjectPolicyUpdateProperties', module='types')
        properties: ProjectPolicyUpdateProperties


    class azure.mgmt.devcenter.types.ProjectPolicyUpdateProperties(TypedDict, total=False):
        key "configurationPolicies": ForwardRef('ConfigurationPolicies', module='types')
        configuration_policies: ConfigurationPolicies
        resourcePolicies: list[ResourcePolicy]
        resource_policies: list[ResourcePolicy]
        scopes: list[str]


    class azure.mgmt.devcenter.types.ProjectProperties(ProjectUpdateProperties):
        key "azureAiServicesSettings": ForwardRef('AzureAiServicesSettings', module='types')
        key "catalogSettings": ForwardRef('ProjectCatalogSettings', module='types')
        key "customizationSettings": ForwardRef('ProjectCustomizationSettings', module='types')
        key "description": str
        key "devBoxScheduleDeleteSettings": ForwardRef('DevBoxScheduleDeleteSettings', module='types')
        key "devCenterId": str
        key "devCenterUri": str
        key "displayName": str
        key "maxDevBoxesPerUser": int
        key "provisioningState": Union[str, ProvisioningState]
        key "serverlessGpuSessionsSettings": ForwardRef('ServerlessGpuSessionsSettings', module='types')
        key "workspaceStorageSettings": ForwardRef('WorkspaceStorageSettings', module='types')
        assignedGroups: list[AssignedGroup]
        assigned_groups: list[AssignedGroup]
        azure_ai_services_settings: AzureAiServicesSettings
        catalog_settings: ProjectCatalogSettings
        customization_settings: ProjectCustomizationSettings
        description: str
        dev_box_schedule_delete_settings: DevBoxScheduleDeleteSettings
        dev_center_id: str
        dev_center_uri: str
        display_name: str
        max_dev_boxes_per_user: int
        provisioning_state: Union[str, ProvisioningState]
        serverless_gpu_sessions_settings: ServerlessGpuSessionsSettings
        workspace_storage_settings: WorkspaceStorageSettings


    class azure.mgmt.devcenter.types.ProjectUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "properties": ForwardRef('ProjectUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        location: str
        properties: ProjectUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.devcenter.types.ProjectUpdateProperties(TypedDict, total=False):
        key "azureAiServicesSettings": ForwardRef('AzureAiServicesSettings', module='types')
        key "catalogSettings": ForwardRef('ProjectCatalogSettings', module='types')
        key "customizationSettings": ForwardRef('ProjectCustomizationSettings', module='types')
        key "description": str
        key "devBoxScheduleDeleteSettings": ForwardRef('DevBoxScheduleDeleteSettings', module='types')
        key "devCenterId": str
        key "displayName": str
        key "maxDevBoxesPerUser": int
        key "serverlessGpuSessionsSettings": ForwardRef('ServerlessGpuSessionsSettings', module='types')
        key "workspaceStorageSettings": ForwardRef('WorkspaceStorageSettings', module='types')
        assignedGroups: list[AssignedGroup]
        assigned_groups: list[AssignedGroup]
        azure_ai_services_settings: AzureAiServicesSettings
        catalog_settings: ProjectCatalogSettings
        customization_settings: ProjectCustomizationSettings
        description: str
        dev_box_schedule_delete_settings: DevBoxScheduleDeleteSettings
        dev_center_id: str
        display_name: str
        max_dev_boxes_per_user: int
        serverless_gpu_sessions_settings: ServerlessGpuSessionsSettings
        workspace_storage_settings: WorkspaceStorageSettings


    class azure.mgmt.devcenter.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.ResourcePolicy(TypedDict, total=False):
        key "action": Union[str, PolicyAction]
        key "filter": str
        key "resourceType": Union[str, DevCenterResourceType]
        key "resources": str
        action: Union[str, PolicyAction]
        filter: str
        resource_type: Union[str, DevCenterResourceType]
        resources: str


    class azure.mgmt.devcenter.types.Schedule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ScheduleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ScheduleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.devcenter.types.ScheduleProperties(ScheduleUpdateProperties):
        key "frequency": Union[str, ScheduledFrequency]
        key "location": str
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Union[str, ScheduleEnableStatus]
        key "time": str
        key "timeZone": str
        key "type": Union[str, ScheduledType]
        frequency: Union[str, ScheduledFrequency]
        location: str
        provisioning_state: Union[str, ProvisioningState]
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]


    class azure.mgmt.devcenter.types.ScheduleUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ScheduleUpdateProperties', module='types')
        properties: ScheduleUpdateProperties


    class azure.mgmt.devcenter.types.ScheduleUpdateProperties(TypedDict, total=False):
        key "frequency": Union[str, ScheduledFrequency]
        key "location": str
        key "state": Union[str, ScheduleEnableStatus]
        key "time": str
        key "timeZone": str
        key "type": Union[str, ScheduledType]
        frequency: Union[str, ScheduledFrequency]
        location: str
        state: Union[str, ScheduleEnableStatus]
        tags: dict[str, str]
        time: str
        time_zone: str
        type: Union[str, ScheduledType]


    class azure.mgmt.devcenter.types.ServerlessGpuSessionsSettings(TypedDict, total=False):
        key "maxConcurrentSessionsPerProject": int
        key "serverlessGpuSessionsMode": Union[str, ServerlessGpuSessionsMode]
        max_concurrent_sessions_per_project: int
        serverless_gpu_sessions_mode: Union[str, ServerlessGpuSessionsMode]


    class azure.mgmt.devcenter.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.devcenter.types.StopOnDisconnectConfiguration(TypedDict, total=False):
        key "gracePeriodMinutes": int
        key "status": Union[str, StopOnDisconnectEnableStatus]
        grace_period_minutes: int
        status: Union[str, StopOnDisconnectEnableStatus]


    class azure.mgmt.devcenter.types.StopOnNoConnectConfiguration(TypedDict, total=False):
        key "gracePeriodMinutes": int
        key "status": Union[str, StopOnNoConnectEnableStatus]
        grace_period_minutes: int
        status: Union[str, StopOnNoConnectEnableStatus]


    class azure.mgmt.devcenter.types.SyncStats(TypedDict, total=False):
        key "added": int
        key "removed": int
        key "synchronizationErrors": int
        key "unchanged": int
        key "updated": int
        key "validationErrors": int
        added: int
        removed: int
        syncedCatalogItemTypes: list[Union[str, CatalogItemType]]
        synced_catalog_item_types: list[Union[str, CatalogItemType]]
        synchronization_errors: int
        unchanged: int
        updated: int
        validation_errors: int


    class azure.mgmt.devcenter.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.devcenter.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.devcenter.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.devcenter.types.UserRoleAssignmentValue(TypedDict, total=False):
        roles: dict[str, EnvironmentRole]


    class azure.mgmt.devcenter.types.WorkspaceStorageSettings(TypedDict, total=False):
        key "workspaceStorageMode": Union[str, WorkspaceStorageMode]
        workspace_storage_mode: Union[str, WorkspaceStorageMode]


```