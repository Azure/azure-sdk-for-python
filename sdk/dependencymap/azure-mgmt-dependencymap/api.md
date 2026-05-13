```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.dependencymap

    class azure.mgmt.dependencymap.DependencyMapMgmtClient: implements ContextManager 
        discovery_sources: DiscoverySourcesOperations
        maps: MapsOperations
        operations: Operations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.dependencymap.aio

    class azure.mgmt.dependencymap.aio.DependencyMapMgmtClient: implements AsyncContextManager 
        discovery_sources: DiscoverySourcesOperations
        maps: MapsOperations
        operations: Operations

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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.dependencymap.aio.operations

    class azure.mgmt.dependencymap.aio.operations.DiscoverySourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: DiscoverySourceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: DiscoverySourceResourceTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DiscoverySourceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> DiscoverySourceResource: ...

        @distributed_trace
        def list_by_maps_resource(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[DiscoverySourceResource]: ...


    class azure.mgmt.dependencymap.aio.operations.MapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: MapsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: ExportDependenciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetConnectionsForProcessOnFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetConnectionsWithConnectedMachineForFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetDependencyViewForFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: MapsResourceTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MapsResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> MapsResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[MapsResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[MapsResource]: ...


    class azure.mgmt.dependencymap.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


namespace azure.mgmt.dependencymap.models

    class azure.mgmt.dependencymap.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.dependencymap.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dependencymap.models.DateTimeFilter(Model):
        end_date_time_utc: Optional[datetime]
        start_date_time_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                end_date_time_utc: Optional[datetime] = ..., 
                start_date_time_utc: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.DependencyMapVisualizationFilter(Model):
        date_time: Optional[DateTimeFilter]
        process_name_filter: Optional[ProcessNameFilter]

        @overload
        def __init__(
                self, 
                *, 
                date_time: Optional[DateTimeFilter] = ..., 
                process_name_filter: Optional[ProcessNameFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.DiscoverySourceResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DiscoverySourceResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DiscoverySourceResourceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.DiscoverySourceResourceProperties(Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_id: str
        source_type: str

        @overload
        def __init__(
                self, 
                *, 
                source_id: str, 
                source_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.DiscoverySourceResourceTagsUpdate(Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dependencymap.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dependencymap.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.ExportDependenciesRequest(Model):
        filters: Optional[DependencyMapVisualizationFilter]
        focused_machine_id: str

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[DependencyMapVisualizationFilter] = ..., 
                focused_machine_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.GetConnectionsForProcessOnFocusedMachineRequest(Model):
        filters: Optional[DependencyMapVisualizationFilter]
        focused_machine_id: str
        process_id_on_focused_machine: str

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[DependencyMapVisualizationFilter] = ..., 
                focused_machine_id: str, 
                process_id_on_focused_machine: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.GetConnectionsWithConnectedMachineForFocusedMachineRequest(Model):
        connected_machine_id: str
        filters: Optional[DependencyMapVisualizationFilter]
        focused_machine_id: str

        @overload
        def __init__(
                self, 
                *, 
                connected_machine_id: str, 
                filters: Optional[DependencyMapVisualizationFilter] = ..., 
                focused_machine_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.GetDependencyViewForFocusedMachineRequest(Model):
        filters: Optional[DependencyMapVisualizationFilter]
        focused_machine_id: str

        @overload
        def __init__(
                self, 
                *, 
                filters: Optional[DependencyMapVisualizationFilter] = ..., 
                focused_machine_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.MapsResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MapsResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MapsResourceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.MapsResourceProperties(Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.dependencymap.models.MapsResourceTagsUpdate(Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.OffAzureDiscoverySourceResourceProperties(DiscoverySourceResourceProperties, discriminator='OffAzure'):
        provisioning_state: Union[str, ProvisioningState]
        source_id: str
        source_type: Literal[SourceType.OFF_AZURE]

        @overload
        def __init__(
                self, 
                *, 
                source_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.Operation(Model):
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


    class azure.mgmt.dependencymap.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.dependencymap.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.dependencymap.models.ProcessNameFilter(Model):
        operator: Union[str, ProcessNameFilterOperator]
        process_names: List[str]

        @overload
        def __init__(
                self, 
                *, 
                operator: Union[str, ProcessNameFilterOperator], 
                process_names: List[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dependencymap.models.ProcessNameFilterOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTAINS = "contains"
        NOT_CONTAINS = "notContains"


    class azure.mgmt.dependencymap.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.dependencymap.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dependencymap.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFF_AZURE = "OffAzure"


    class azure.mgmt.dependencymap.models.SystemData(Model):
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


    class azure.mgmt.dependencymap.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.dependencymap.operations

    class azure.mgmt.dependencymap.operations.DiscoverySourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: DiscoverySourceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: DiscoverySourceResourceTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DiscoverySourceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                map_name: str, 
                source_name: str, 
                **kwargs: Any
            ) -> DiscoverySourceResource: ...

        @distributed_trace
        def list_by_maps_resource(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> Iterable[DiscoverySourceResource]: ...


    class azure.mgmt.dependencymap.operations.MapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: MapsResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: ExportDependenciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_export_dependencies(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetConnectionsForProcessOnFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_for_process_on_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetConnectionsWithConnectedMachineForFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_connections_with_connected_machine_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: GetDependencyViewForFocusedMachineRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_get_dependency_view_for_focused_machine(
                self, 
                resource_group_name: str, 
                map_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: MapsResourceTagsUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                map_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MapsResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                map_name: str, 
                **kwargs: Any
            ) -> MapsResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[MapsResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[MapsResource]: ...


    class azure.mgmt.dependencymap.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


```