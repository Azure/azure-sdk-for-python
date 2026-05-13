```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.workloads

    class azure.mgmt.workloads.WorkloadsMgmtClient(WorkloadsMgmtClientOperationsMixin): implements ContextManager 
        monitors: MonitorsOperations
        operations: Operations
        provider_instances: ProviderInstancesOperations
        sap_application_server_instances: SAPApplicationServerInstancesOperations
        sap_central_instances: SAPCentralInstancesOperations
        sap_database_instances: SAPDatabaseInstancesOperations
        sap_landscape_monitor: SapLandscapeMonitorOperations
        sap_virtual_instances: SAPVirtualInstancesOperations

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

        @overload
        def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[SAPAvailabilityZoneDetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[SAPDiskConfigurationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[SAPSizingRecommendationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[SAPSupportedSkusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...


namespace azure.mgmt.workloads.aio

    class azure.mgmt.workloads.aio.WorkloadsMgmtClient(WorkloadsMgmtClientOperationsMixin): implements AsyncContextManager 
        monitors: MonitorsOperations
        operations: Operations
        provider_instances: ProviderInstancesOperations
        sap_application_server_instances: SAPApplicationServerInstancesOperations
        sap_central_instances: SAPCentralInstancesOperations
        sap_database_instances: SAPDatabaseInstancesOperations
        sap_landscape_monitor: SapLandscapeMonitorOperations
        sap_virtual_instances: SAPVirtualInstancesOperations

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

        @overload
        async def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[SAPAvailabilityZoneDetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[SAPDiskConfigurationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[SAPSizingRecommendationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[SAPSupportedSkusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        async def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...


namespace azure.mgmt.workloads.aio.operations

    class azure.mgmt.workloads.aio.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                monitor_parameter: Monitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Monitor]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Monitor]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Monitor: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Monitor]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Monitor]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: UpdateMonitorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Monitor: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Monitor: ...


    class azure.mgmt.workloads.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Operation]: ...


    class azure.mgmt.workloads.aio.operations.ProviderInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                provider_instance_parameter: ProviderInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                provider_instance_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ProviderInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ProviderInstance]: ...


    class azure.mgmt.workloads.aio.operations.SAPApplicationServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[SAPApplicationServerInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPApplicationServerInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPApplicationServerInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[UpdateSAPApplicationInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPApplicationServerInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPApplicationServerInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SAPApplicationServerInstance]: ...


    class azure.mgmt.workloads.aio.operations.SAPCentralInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[SAPCentralServerInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPCentralServerInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPCentralServerInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[UpdateSAPCentralInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPCentralServerInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPCentralServerInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SAPCentralServerInstance]: ...


    class azure.mgmt.workloads.aio.operations.SAPDatabaseInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[SAPDatabaseInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPDatabaseInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPDatabaseInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[UpdateSAPDatabaseInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPDatabaseInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPDatabaseInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SAPDatabaseInstance]: ...


    class azure.mgmt.workloads.aio.operations.SAPVirtualInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[SAPVirtualInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SAPVirtualInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[SAPVirtualInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[UpdateSAPVirtualInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...


    class azure.mgmt.workloads.aio.operations.SapLandscapeMonitorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: SapLandscapeMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SapLandscapeMonitorListResult: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: SapLandscapeMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...


    class azure.mgmt.workloads.aio.operations.WorkloadsMgmtClientOperationsMixin(WorkloadsMgmtClientMixinABC):

        @overload
        async def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[SAPAvailabilityZoneDetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[SAPDiskConfigurationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[SAPSizingRecommendationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[SAPSupportedSkusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        async def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...


namespace azure.mgmt.workloads.models

    class azure.mgmt.workloads.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.workloads.models.ApplicationServerConfiguration(Model):
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration, 
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


    class azure.mgmt.workloads.models.ApplicationServerFullResourceNames(Model):
        availability_set_name: str
        virtual_machines: list[VirtualMachineResourceNames]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ..., 
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


    class azure.mgmt.workloads.models.ApplicationServerVirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        STANDBY = "Standby"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloads.models.ApplicationServerVmDetails(Model):
        storage_details: list[StorageInformation]
        type: Union[str, ApplicationServerVirtualMachineType]
        virtual_machine_id: str

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


    class azure.mgmt.workloads.models.CentralServerConfiguration(Model):
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration, 
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


    class azure.mgmt.workloads.models.CentralServerFullResourceNames(Model):
        availability_set_name: str
        load_balancer: LoadBalancerResourceNames
        virtual_machines: list[VirtualMachineResourceNames]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                load_balancer: Optional[LoadBalancerResourceNames] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ..., 
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


    class azure.mgmt.workloads.models.CentralServerVirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCS = "ASCS"
        ERS = "ERS"
        ERS_INACTIVE = "ERSInactive"
        PRIMARY = "Primary"
        SECONDARY = "Secondary"
        STANDBY = "Standby"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloads.models.CentralServerVmDetails(Model):
        storage_details: list[StorageInformation]
        type: Union[str, CentralServerVirtualMachineType]
        virtual_machine_id: str

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


    class azure.mgmt.workloads.models.ConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_AND_MOUNT = "CreateAndMount"
        MOUNT = "Mount"
        SKIP = "Skip"


    class azure.mgmt.workloads.models.CreateAndMountFileShareConfiguration(FileShareConfiguration):
        configuration_type: Union[str, ConfigurationType]
        resource_group: str
        storage_account_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_group: Optional[str] = ..., 
                storage_account_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.workloads.models.DB2ProviderInstanceProperties(ProviderSpecificProperties):
        db_name: str
        db_password: str
        db_password_uri: str
        db_port: str
        db_username: str
        hostname: str
        provider_type: str
        sap_sid: str
        ssl_certificate_uri: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                db_name: Optional[str] = ..., 
                db_password: Optional[str] = ..., 
                db_password_uri: Optional[str] = ..., 
                db_port: Optional[str] = ..., 
                db_username: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                sap_sid: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.DatabaseConfiguration(Model):
        database_type: Union[str, SAPDatabaseType]
        disk_configuration: DiskConfiguration
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_type: Optional[Union[str, SAPDatabaseType]] = ..., 
                disk_configuration: Optional[DiskConfiguration] = ..., 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration, 
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


    class azure.mgmt.workloads.models.DatabaseServerFullResourceNames(Model):
        availability_set_name: str
        load_balancer: LoadBalancerResourceNames
        virtual_machines: list[VirtualMachineResourceNames]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                load_balancer: Optional[LoadBalancerResourceNames] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ..., 
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


    class azure.mgmt.workloads.models.DatabaseVmDetails(Model):
        status: Union[str, SAPVirtualInstanceStatus]
        storage_details: list[StorageInformation]
        virtual_machine_id: str

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


    class azure.mgmt.workloads.models.DeployerVmPackages(Model):
        storage_account_id: str
        url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                storage_account_id: Optional[str] = ..., 
                url: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.DeploymentConfiguration(SAPConfiguration):
        app_location: str
        configuration_type: Union[str, SAPConfigurationType]
        infrastructure_configuration: InfrastructureConfiguration
        software_configuration: SoftwareConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: Optional[str] = ..., 
                infrastructure_configuration: Optional[InfrastructureConfiguration] = ..., 
                software_configuration: Optional[SoftwareConfiguration] = ..., 
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


    class azure.mgmt.workloads.models.DeploymentWithOSConfiguration(SAPConfiguration):
        app_location: str
        configuration_type: Union[str, SAPConfigurationType]
        infrastructure_configuration: InfrastructureConfiguration
        os_sap_configuration: OsSapConfiguration
        software_configuration: SoftwareConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: Optional[str] = ..., 
                infrastructure_configuration: Optional[InfrastructureConfiguration] = ..., 
                os_sap_configuration: Optional[OsSapConfiguration] = ..., 
                software_configuration: Optional[SoftwareConfiguration] = ..., 
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


    class azure.mgmt.workloads.models.DiscoveryConfiguration(SAPConfiguration):
        app_location: str
        central_server_vm_id: str
        configuration_type: Union[str, SAPConfigurationType]
        managed_rg_storage_account_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                central_server_vm_id: Optional[str] = ..., 
                managed_rg_storage_account_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.DiskConfiguration(Model):
        disk_volume_configurations: dict[str, DiskVolumeConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_volume_configurations: Optional[Dict[str, DiskVolumeConfiguration]] = ..., 
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


    class azure.mgmt.workloads.models.DiskDetails(Model):
        disk_tier: str
        iops_read_write: int
        maximum_supported_disk_count: int
        mbps_read_write: int
        minimum_supported_disk_count: int
        size_gb: int
        sku: DiskSku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disk_tier: Optional[str] = ..., 
                iops_read_write: Optional[int] = ..., 
                maximum_supported_disk_count: Optional[int] = ..., 
                mbps_read_write: Optional[int] = ..., 
                minimum_supported_disk_count: Optional[int] = ..., 
                size_gb: Optional[int] = ..., 
                sku: Optional[DiskSku] = ..., 
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


    class azure.mgmt.workloads.models.DiskSku(Model):
        name: Union[str, DiskSkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[Union[str, DiskSkuName]] = ..., 
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


    class azure.mgmt.workloads.models.DiskSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.workloads.models.DiskVolumeConfiguration(Model):
        count: int
        size_gb: int
        sku: DiskSku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                size_gb: Optional[int] = ..., 
                sku: Optional[DiskSku] = ..., 
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


    class azure.mgmt.workloads.models.EnqueueReplicationServerProperties(Model):
        ers_version: Union[str, EnqueueReplicationServerType]
        health: Union[str, SAPHealthState]
        hostname: str
        instance_no: str
        ip_address: str
        kernel_patch: str
        kernel_version: str

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


    class azure.mgmt.workloads.models.EnqueueReplicationServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENQUEUE_REPLICATOR1 = "EnqueueReplicator1"
        ENQUEUE_REPLICATOR2 = "EnqueueReplicator2"


    class azure.mgmt.workloads.models.EnqueueServerProperties(Model):
        health: Union[str, SAPHealthState]
        hostname: str
        ip_address: str
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


    class azure.mgmt.workloads.models.Error(Model):
        code: str
        details: list[Error]
        inner_error: ErrorInnerError
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


    class azure.mgmt.workloads.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.workloads.models.ErrorDefinition(Model):
        code: str
        details: list[ErrorDefinition]
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


    class azure.mgmt.workloads.models.ErrorDetail(Model):
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


    class azure.mgmt.workloads.models.ErrorInnerError(Model):
        inner_error: Error

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                inner_error: Optional[Error] = ..., 
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


    class azure.mgmt.workloads.models.ErrorResponse(Model):
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


    class azure.mgmt.workloads.models.ExternalInstallationSoftwareConfiguration(SoftwareConfiguration):
        central_server_vm_id: str
        software_installation_type: Union[str, SAPSoftwareInstallationType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                central_server_vm_id: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.FileShareConfiguration(Model):
        configuration_type: Union[str, ConfigurationType]

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


    class azure.mgmt.workloads.models.GatewayServerProperties(Model):
        health: Union[str, SAPHealthState]
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


    class azure.mgmt.workloads.models.HanaDbProviderInstanceProperties(ProviderSpecificProperties):
        db_name: str
        db_password: str
        db_password_uri: str
        db_username: str
        hostname: str
        instance_number: str
        provider_type: str
        sap_sid: str
        sql_port: str
        ssl_certificate_uri: str
        ssl_host_name_in_certificate: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                db_name: Optional[str] = ..., 
                db_password: Optional[str] = ..., 
                db_password_uri: Optional[str] = ..., 
                db_username: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                instance_number: Optional[str] = ..., 
                sap_sid: Optional[str] = ..., 
                sql_port: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_host_name_in_certificate: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.HighAvailabilityConfiguration(Model):
        high_availability_type: Union[str, SAPHighAvailabilityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                high_availability_type: Union[str, SAPHighAvailabilityType], 
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


    class azure.mgmt.workloads.models.HighAvailabilitySoftwareConfiguration(Model):
        fencing_client_id: str
        fencing_client_password: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fencing_client_id: str, 
                fencing_client_password: str, 
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


    class azure.mgmt.workloads.models.ImageReference(Model):
        offer: str
        publisher: str
        sku: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.InfrastructureConfiguration(Model):
        app_resource_group: str
        deployment_type: Union[str, SAPDeploymentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_resource_group: str, 
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


    class azure.mgmt.workloads.models.LinuxConfiguration(OSConfiguration):
        disable_password_authentication: bool
        os_type: Union[str, OSType]
        ssh: SshConfiguration
        ssh_key_pair: SshKeyPair

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                disable_password_authentication: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ..., 
                ssh_key_pair: Optional[SshKeyPair] = ..., 
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


    class azure.mgmt.workloads.models.LoadBalancerDetails(Model):
        id: str

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


    class azure.mgmt.workloads.models.LoadBalancerResourceNames(Model):
        backend_pool_names: list[str]
        frontend_ip_configuration_names: list[str]
        health_probe_names: list[str]
        load_balancer_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backend_pool_names: Optional[List[str]] = ..., 
                frontend_ip_configuration_names: Optional[List[str]] = ..., 
                health_probe_names: Optional[List[str]] = ..., 
                load_balancer_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.ManagedRGConfiguration(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.workloads.models.MessageServerProperties(Model):
        health: Union[str, SAPHealthState]
        hostname: str
        http_port: int
        https_port: int
        internal_ms_port: int
        ip_address: str
        ms_port: int

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


    class azure.mgmt.workloads.models.Monitor(TrackedResource):
        app_location: str
        errors: MonitorPropertiesErrors
        id: str
        identity: UserAssignedServiceIdentity
        location: str
        log_analytics_workspace_arm_id: str
        managed_resource_group_configuration: ManagedRGConfiguration
        monitor_subnet: str
        msi_arm_id: str
        name: str
        provisioning_state: Union[str, WorkloadMonitorProvisioningState]
        routing_preference: Union[str, RoutingPreference]
        storage_account_arm_id: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zone_redundancy_preference: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: Optional[str] = ..., 
                identity: Optional[UserAssignedServiceIdentity] = ..., 
                location: str, 
                log_analytics_workspace_arm_id: Optional[str] = ..., 
                managed_resource_group_configuration: Optional[ManagedRGConfiguration] = ..., 
                monitor_subnet: Optional[str] = ..., 
                routing_preference: Optional[Union[str, RoutingPreference]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zone_redundancy_preference: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.MonitorListResult(Model):
        next_link: str
        value: list[Monitor]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Monitor]] = ..., 
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


    class azure.mgmt.workloads.models.MonitorPropertiesErrors(Error):
        code: str
        details: list[Error]
        inner_error: ErrorInnerError
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


    class azure.mgmt.workloads.models.MountFileShareConfiguration(FileShareConfiguration):
        configuration_type: Union[str, ConfigurationType]
        id: str
        private_endpoint_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                private_endpoint_id: str, 
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


    class azure.mgmt.workloads.models.MsSqlServerProviderInstanceProperties(ProviderSpecificProperties):
        db_password: str
        db_password_uri: str
        db_port: str
        db_username: str
        hostname: str
        provider_type: str
        sap_sid: str
        ssl_certificate_uri: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                db_password: Optional[str] = ..., 
                db_password_uri: Optional[str] = ..., 
                db_port: Optional[str] = ..., 
                db_username: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                sap_sid: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.NamingPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_RESOURCE_NAME = "FullResourceName"


    class azure.mgmt.workloads.models.NetworkConfiguration(Model):
        is_secondary_ip_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_secondary_ip_enabled: bool = False, 
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


    class azure.mgmt.workloads.models.NetworkInterfaceResourceNames(Model):
        network_interface_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                network_interface_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.OSConfiguration(Model):
        os_type: Union[str, OSType]

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


    class azure.mgmt.workloads.models.OSProfile(Model):
        admin_password: str
        admin_username: str
        os_configuration: OSConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                os_configuration: Optional[OSConfiguration] = ..., 
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


    class azure.mgmt.workloads.models.OSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.workloads.models.Operation(Model):
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


    class azure.mgmt.workloads.models.OperationDisplay(Model):
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


    class azure.mgmt.workloads.models.OperationListResult(Model):
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


    class azure.mgmt.workloads.models.OperationProperties(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.workloads.models.OperationStatusResult(Model):
        end_time: datetime
        error: ErrorDetail
        id: str
        name: str
        operations: list[OperationStatusResult]
        percent_complete: float
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


    class azure.mgmt.workloads.models.OperationsContent(Resource):
        action_type: Union[str, WorkloadMonitorActionType]
        display: OperationsDefinitionDisplay
        id: str
        is_data_action: bool
        name: str
        name_properties_name: str
        origin: Union[str, OperationProperties]
        properties: any
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, WorkloadMonitorActionType]] = ..., 
                display: Optional[OperationsDefinitionDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name_properties_name: Optional[str] = ..., 
                origin: Optional[Union[str, OperationProperties]] = ..., 
                properties: Optional[Any] = ..., 
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


    class azure.mgmt.workloads.models.OperationsDefinition(Model):
        action_type: Union[str, WorkloadMonitorActionType]
        display: OperationsDefinitionDisplay
        is_data_action: bool
        name: str
        origin: Union[str, OperationProperties]
        properties: any

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, WorkloadMonitorActionType]] = ..., 
                display: OperationsDefinitionDisplay, 
                is_data_action: Optional[bool] = ..., 
                name: str, 
                origin: Optional[Union[str, OperationProperties]] = ..., 
                properties: Optional[Any] = ..., 
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


    class azure.mgmt.workloads.models.OperationsDefinitionArrayResponseWithContinuation(Model):
        next_link: str
        value: list[OperationsDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationsDefinition]] = ..., 
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


    class azure.mgmt.workloads.models.OperationsDefinitionDisplay(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str, 
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


    class azure.mgmt.workloads.models.OperationsDisplayDefinition(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str, 
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


    class azure.mgmt.workloads.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.workloads.models.OsSapConfiguration(Model):
        deployer_vm_packages: DeployerVmPackages
        sap_fqdn: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                deployer_vm_packages: Optional[DeployerVmPackages] = ..., 
                sap_fqdn: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.PrometheusHaClusterProviderInstanceProperties(ProviderSpecificProperties):
        cluster_name: str
        hostname: str
        prometheus_url: str
        provider_type: str
        sid: str
        ssl_certificate_uri: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cluster_name: Optional[str] = ..., 
                hostname: Optional[str] = ..., 
                prometheus_url: Optional[str] = ..., 
                sid: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.PrometheusOSProviderInstanceProperties(ProviderSpecificProperties):
        prometheus_url: str
        provider_type: str
        sap_sid: str
        ssl_certificate_uri: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                prometheus_url: Optional[str] = ..., 
                sap_sid: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.ProviderInstance(ProxyResource):
        errors: ProviderInstancePropertiesErrors
        id: str
        identity: UserAssignedServiceIdentity
        name: str
        provider_settings: ProviderSpecificProperties
        provisioning_state: Union[str, WorkloadMonitorProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedServiceIdentity] = ..., 
                provider_settings: Optional[ProviderSpecificProperties] = ..., 
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


    class azure.mgmt.workloads.models.ProviderInstanceListResult(Model):
        next_link: str
        value: list[ProviderInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ProviderInstance]] = ..., 
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


    class azure.mgmt.workloads.models.ProviderInstancePropertiesErrors(Error):
        code: str
        details: list[Error]
        inner_error: ErrorInnerError
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


    class azure.mgmt.workloads.models.ProviderSpecificProperties(Model):
        provider_type: str

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


    class azure.mgmt.workloads.models.ProxyResource(Resource):
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


    class azure.mgmt.workloads.models.Resource(Model):
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


    class azure.mgmt.workloads.models.RoutingPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        ROUTE_ALL = "RouteAll"


    class azure.mgmt.workloads.models.SAPApplicationServerInstance(TrackedResource):
        errors: SAPVirtualInstanceError
        gateway_port: int
        health: Union[str, SAPHealthState]
        hostname: str
        icm_http_port: int
        icm_https_port: int
        id: str
        instance_no: str
        ip_address: str
        kernel_patch: str
        kernel_version: str
        load_balancer_details: LoadBalancerDetails
        location: str
        name: str
        provisioning_state: Union[str, SapVirtualInstanceProvisioningState]
        status: Union[str, SAPVirtualInstanceStatus]
        subnet: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        vm_details: list[ApplicationServerVmDetails]

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


    class azure.mgmt.workloads.models.SAPApplicationServerInstanceList(Model):
        next_link: str
        value: list[SAPApplicationServerInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SAPApplicationServerInstance]] = ..., 
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


    class azure.mgmt.workloads.models.SAPAvailabilityZoneDetailsRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        sap_product: Union[str, SAPProductType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                sap_product: Union[str, SAPProductType], 
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


    class azure.mgmt.workloads.models.SAPAvailabilityZoneDetailsResult(Model):
        availability_zone_pairs: list[SAPAvailabilityZonePair]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                availability_zone_pairs: Optional[List[SAPAvailabilityZonePair]] = ..., 
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


    class azure.mgmt.workloads.models.SAPAvailabilityZonePair(Model):
        zone_a: int
        zone_b: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                zone_a: Optional[int] = ..., 
                zone_b: Optional[int] = ..., 
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


    class azure.mgmt.workloads.models.SAPCentralInstanceList(Model):
        next_link: str
        value: list[SAPCentralServerInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SAPCentralServerInstance]] = ..., 
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


    class azure.mgmt.workloads.models.SAPCentralServerInstance(TrackedResource):
        enqueue_replication_server_properties: EnqueueReplicationServerProperties
        enqueue_server_properties: EnqueueServerProperties
        errors: SAPVirtualInstanceError
        gateway_server_properties: GatewayServerProperties
        health: Union[str, SAPHealthState]
        id: str
        instance_no: str
        kernel_patch: str
        kernel_version: str
        load_balancer_details: LoadBalancerDetails
        location: str
        message_server_properties: MessageServerProperties
        name: str
        provisioning_state: Union[str, SapVirtualInstanceProvisioningState]
        status: Union[str, SAPVirtualInstanceStatus]
        subnet: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        vm_details: list[CentralServerVmDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enqueue_replication_server_properties: Optional[EnqueueReplicationServerProperties] = ..., 
                enqueue_server_properties: Optional[EnqueueServerProperties] = ..., 
                gateway_server_properties: Optional[GatewayServerProperties] = ..., 
                location: str, 
                message_server_properties: Optional[MessageServerProperties] = ..., 
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


    class azure.mgmt.workloads.models.SAPConfiguration(Model):
        configuration_type: Union[str, SAPConfigurationType]

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


    class azure.mgmt.workloads.models.SAPConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOYMENT = "Deployment"
        DEPLOYMENT_WITH_OS_CONFIG = "DeploymentWithOSConfig"
        DISCOVERY = "Discovery"


    class azure.mgmt.workloads.models.SAPDatabaseInstance(TrackedResource):
        database_sid: str
        database_type: str
        errors: SAPVirtualInstanceError
        id: str
        ip_address: str
        load_balancer_details: LoadBalancerDetails
        location: str
        name: str
        provisioning_state: Union[str, SapVirtualInstanceProvisioningState]
        status: Union[str, SAPVirtualInstanceStatus]
        subnet: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        vm_details: list[DatabaseVmDetails]

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


    class azure.mgmt.workloads.models.SAPDatabaseInstanceList(Model):
        next_link: str
        value: list[SAPDatabaseInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SAPDatabaseInstance]] = ..., 
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


    class azure.mgmt.workloads.models.SAPDatabaseScaleMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCALE_UP = "ScaleUp"


    class azure.mgmt.workloads.models.SAPDatabaseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DB2 = "DB2"
        HANA = "HANA"


    class azure.mgmt.workloads.models.SAPDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SINGLE_SERVER = "SingleServer"
        THREE_TIER = "ThreeTier"


    class azure.mgmt.workloads.models.SAPDiskConfiguration(Model):
        recommended_configuration: DiskVolumeConfiguration
        supported_configurations: list[DiskDetails]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                recommended_configuration: Optional[DiskVolumeConfiguration] = ..., 
                supported_configurations: Optional[List[DiskDetails]] = ..., 
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


    class azure.mgmt.workloads.models.SAPDiskConfigurationsRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        db_vm_sku: str
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        sap_product: Union[str, SAPProductType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                db_vm_sku: str, 
                deployment_type: Union[str, SAPDeploymentType], 
                environment: Union[str, SAPEnvironmentType], 
                sap_product: Union[str, SAPProductType], 
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


    class azure.mgmt.workloads.models.SAPDiskConfigurationsResult(Model):
        volume_configurations: dict[str, SAPDiskConfiguration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                volume_configurations: Optional[Dict[str, SAPDiskConfiguration]] = ..., 
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


    class azure.mgmt.workloads.models.SAPEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_PROD = "NonProd"
        PROD = "Prod"


    class azure.mgmt.workloads.models.SAPHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloads.models.SAPHighAvailabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_SET = "AvailabilitySet"
        AVAILABILITY_ZONE = "AvailabilityZone"


    class azure.mgmt.workloads.models.SAPInstallWithoutOSConfigSoftwareConfiguration(SoftwareConfiguration):
        bom_url: str
        high_availability_software_configuration: HighAvailabilitySoftwareConfiguration
        sap_bits_storage_account_id: str
        software_installation_type: Union[str, SAPSoftwareInstallationType]
        software_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bom_url: str, 
                high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration] = ..., 
                sap_bits_storage_account_id: str, 
                software_version: str, 
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


    class azure.mgmt.workloads.models.SAPProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECC = "ECC"
        OTHER = "Other"
        S4_HANA = "S4HANA"


    class azure.mgmt.workloads.models.SAPSizingRecommendationRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        db_memory: int
        db_scale_method: Union[str, SAPDatabaseScaleMethod]
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        high_availability_type: Union[str, SAPHighAvailabilityType]
        sap_product: Union[str, SAPProductType]
        saps: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                db_memory: int, 
                db_scale_method: Optional[Union[str, SAPDatabaseScaleMethod]] = ..., 
                deployment_type: Union[str, SAPDeploymentType], 
                environment: Union[str, SAPEnvironmentType], 
                high_availability_type: Optional[Union[str, SAPHighAvailabilityType]] = ..., 
                sap_product: Union[str, SAPProductType], 
                saps: int, 
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


    class azure.mgmt.workloads.models.SAPSizingRecommendationResult(Model):
        deployment_type: Union[str, SAPDeploymentType]

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


    class azure.mgmt.workloads.models.SAPSoftwareInstallationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        SAP_INSTALL_WITHOUT_OS_CONFIG = "SAPInstallWithoutOSConfig"
        SERVICE_INITIATED = "ServiceInitiated"


    class azure.mgmt.workloads.models.SAPSupportedResourceSkusResult(Model):
        supported_skus: list[SAPSupportedSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                supported_skus: Optional[List[SAPSupportedSku]] = ..., 
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


    class azure.mgmt.workloads.models.SAPSupportedSku(Model):
        is_app_server_certified: bool
        is_database_certified: bool
        vm_sku: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_app_server_certified: Optional[bool] = ..., 
                is_database_certified: Optional[bool] = ..., 
                vm_sku: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.SAPSupportedSkusRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        high_availability_type: Union[str, SAPHighAvailabilityType]
        sap_product: Union[str, SAPProductType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                deployment_type: Union[str, SAPDeploymentType], 
                environment: Union[str, SAPEnvironmentType], 
                high_availability_type: Optional[Union[str, SAPHighAvailabilityType]] = ..., 
                sap_product: Union[str, SAPProductType], 
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


    class azure.mgmt.workloads.models.SAPVirtualInstance(TrackedResource):
        configuration: SAPConfiguration
        environment: Union[str, SAPEnvironmentType]
        errors: SAPVirtualInstanceError
        health: Union[str, SAPHealthState]
        id: str
        identity: UserAssignedServiceIdentity
        location: str
        managed_resource_group_configuration: ManagedRGConfiguration
        name: str
        provisioning_state: Union[str, SapVirtualInstanceProvisioningState]
        sap_product: Union[str, SAPProductType]
        state: Union[str, SAPVirtualInstanceState]
        status: Union[str, SAPVirtualInstanceStatus]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                configuration: SAPConfiguration, 
                environment: Union[str, SAPEnvironmentType], 
                identity: Optional[UserAssignedServiceIdentity] = ..., 
                location: str, 
                managed_resource_group_configuration: Optional[ManagedRGConfiguration] = ..., 
                sap_product: Union[str, SAPProductType], 
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


    class azure.mgmt.workloads.models.SAPVirtualInstanceError(Model):
        properties: ErrorDefinition

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[ErrorDefinition] = ..., 
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


    class azure.mgmt.workloads.models.SAPVirtualInstanceList(Model):
        next_link: str
        value: list[SAPVirtualInstance]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SAPVirtualInstance]] = ..., 
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


    class azure.mgmt.workloads.models.SAPVirtualInstanceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISCOVERY_FAILED = "DiscoveryFailed"
        DISCOVERY_IN_PROGRESS = "DiscoveryInProgress"
        DISCOVERY_PENDING = "DiscoveryPending"
        INFRASTRUCTURE_DEPLOYMENT_FAILED = "InfrastructureDeploymentFailed"
        INFRASTRUCTURE_DEPLOYMENT_IN_PROGRESS = "InfrastructureDeploymentInProgress"
        INFRASTRUCTURE_DEPLOYMENT_PENDING = "InfrastructureDeploymentPending"
        REGISTRATION_COMPLETE = "RegistrationComplete"
        SOFTWARE_DETECTION_FAILED = "SoftwareDetectionFailed"
        SOFTWARE_DETECTION_IN_PROGRESS = "SoftwareDetectionInProgress"
        SOFTWARE_INSTALLATION_FAILED = "SoftwareInstallationFailed"
        SOFTWARE_INSTALLATION_IN_PROGRESS = "SoftwareInstallationInProgress"
        SOFTWARE_INSTALLATION_PENDING = "SoftwareInstallationPending"


    class azure.mgmt.workloads.models.SAPVirtualInstanceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        PARTIALLY_RUNNING = "PartiallyRunning"
        RUNNING = "Running"
        SOFT_SHUTDOWN = "SoftShutdown"
        STARTING = "Starting"
        STOPPING = "Stopping"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.workloads.models.SapLandscapeMonitor(ProxyResource):
        grouping: SapLandscapeMonitorPropertiesGrouping
        id: str
        name: str
        provisioning_state: Union[str, SapLandscapeMonitorProvisioningState]
        system_data: SystemData
        top_metrics_thresholds: list[SapLandscapeMonitorMetricThresholds]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                grouping: Optional[SapLandscapeMonitorPropertiesGrouping] = ..., 
                top_metrics_thresholds: Optional[List[SapLandscapeMonitorMetricThresholds]] = ..., 
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


    class azure.mgmt.workloads.models.SapLandscapeMonitorListResult(Model):
        next_link: str
        value: list[SapLandscapeMonitor]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SapLandscapeMonitor]] = ..., 
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


    class azure.mgmt.workloads.models.SapLandscapeMonitorMetricThresholds(Model):
        green: float
        name: str
        red: float
        yellow: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                green: Optional[float] = ..., 
                name: Optional[str] = ..., 
                red: Optional[float] = ..., 
                yellow: Optional[float] = ..., 
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


    class azure.mgmt.workloads.models.SapLandscapeMonitorPropertiesGrouping(Model):
        landscape: list[SapLandscapeMonitorSidMapping]
        sap_application: list[SapLandscapeMonitorSidMapping]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                landscape: Optional[List[SapLandscapeMonitorSidMapping]] = ..., 
                sap_application: Optional[List[SapLandscapeMonitorSidMapping]] = ..., 
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


    class azure.mgmt.workloads.models.SapLandscapeMonitorProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.workloads.models.SapLandscapeMonitorSidMapping(Model):
        name: str
        top_sid: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                top_sid: Optional[List[str]] = ..., 
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


    class azure.mgmt.workloads.models.SapNetWeaverProviderInstanceProperties(ProviderSpecificProperties):
        provider_type: str
        sap_client_id: str
        sap_host_file_entries: list[str]
        sap_hostname: str
        sap_instance_nr: str
        sap_password: str
        sap_password_uri: str
        sap_port_number: str
        sap_sid: str
        sap_username: str
        ssl_certificate_uri: str
        ssl_preference: Union[str, SslPreference]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sap_client_id: Optional[str] = ..., 
                sap_host_file_entries: Optional[List[str]] = ..., 
                sap_hostname: Optional[str] = ..., 
                sap_instance_nr: Optional[str] = ..., 
                sap_password: Optional[str] = ..., 
                sap_password_uri: Optional[str] = ..., 
                sap_port_number: Optional[str] = ..., 
                sap_sid: Optional[str] = ..., 
                sap_username: Optional[str] = ..., 
                ssl_certificate_uri: Optional[str] = ..., 
                ssl_preference: Optional[Union[str, SslPreference]] = ..., 
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


    class azure.mgmt.workloads.models.SapVirtualInstanceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.workloads.models.ServiceInitiatedSoftwareConfiguration(SoftwareConfiguration):
        bom_url: str
        high_availability_software_configuration: HighAvailabilitySoftwareConfiguration
        sap_bits_storage_account_id: str
        sap_fqdn: str
        software_installation_type: Union[str, SAPSoftwareInstallationType]
        software_version: str
        ssh_private_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bom_url: str, 
                high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration] = ..., 
                sap_bits_storage_account_id: str, 
                sap_fqdn: str, 
                software_version: str, 
                ssh_private_key: str, 
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


    class azure.mgmt.workloads.models.SharedStorageResourceNames(Model):
        shared_storage_account_name: str
        shared_storage_account_private_end_point_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                shared_storage_account_name: Optional[str] = ..., 
                shared_storage_account_private_end_point_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.SingleServerConfiguration(InfrastructureConfiguration):
        app_resource_group: str
        custom_resource_names: SingleServerCustomResourceNames
        database_type: Union[str, SAPDatabaseType]
        db_disk_configuration: DiskConfiguration
        deployment_type: Union[str, SAPDeploymentType]
        network_configuration: NetworkConfiguration
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_resource_group: str, 
                custom_resource_names: Optional[SingleServerCustomResourceNames] = ..., 
                database_type: Optional[Union[str, SAPDatabaseType]] = ..., 
                db_disk_configuration: Optional[DiskConfiguration] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration, 
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


    class azure.mgmt.workloads.models.SingleServerCustomResourceNames(Model):
        naming_pattern_type: Union[str, NamingPatternType]

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


    class azure.mgmt.workloads.models.SingleServerFullResourceNames(SingleServerCustomResourceNames):
        naming_pattern_type: Union[str, NamingPatternType]
        virtual_machine: VirtualMachineResourceNames

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                virtual_machine: Optional[VirtualMachineResourceNames] = ..., 
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


    class azure.mgmt.workloads.models.SingleServerRecommendationResult(SAPSizingRecommendationResult):
        deployment_type: Union[str, SAPDeploymentType]
        vm_sku: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                vm_sku: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.SkipFileShareConfiguration(FileShareConfiguration):
        configuration_type: Union[str, ConfigurationType]

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


    class azure.mgmt.workloads.models.SoftwareConfiguration(Model):
        software_installation_type: Union[str, SAPSoftwareInstallationType]

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


    class azure.mgmt.workloads.models.SshConfiguration(Model):
        public_keys: list[SshPublicKey]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                public_keys: Optional[List[SshPublicKey]] = ..., 
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


    class azure.mgmt.workloads.models.SshKeyPair(Model):
        private_key: str
        public_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_key: Optional[str] = ..., 
                public_key: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.SshPublicKey(Model):
        key_data: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_data: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.SslPreference(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ROOT_CERTIFICATE = "RootCertificate"
        SERVER_CERTIFICATE = "ServerCertificate"


    class azure.mgmt.workloads.models.StopRequest(Model):
        soft_stop_timeout_seconds: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                soft_stop_timeout_seconds: int = 0, 
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


    class azure.mgmt.workloads.models.StorageConfiguration(Model):
        transport_file_share_configuration: FileShareConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                transport_file_share_configuration: Optional[FileShareConfiguration] = ..., 
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


    class azure.mgmt.workloads.models.StorageInformation(Model):
        id: str

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


    class azure.mgmt.workloads.models.SystemData(Model):
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


    class azure.mgmt.workloads.models.Tags(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.workloads.models.ThreeTierConfiguration(InfrastructureConfiguration):
        app_resource_group: str
        application_server: ApplicationServerConfiguration
        central_server: CentralServerConfiguration
        custom_resource_names: ThreeTierCustomResourceNames
        database_server: DatabaseConfiguration
        deployment_type: Union[str, SAPDeploymentType]
        high_availability_config: HighAvailabilityConfiguration
        network_configuration: NetworkConfiguration
        storage_configuration: StorageConfiguration

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_resource_group: str, 
                application_server: ApplicationServerConfiguration, 
                central_server: CentralServerConfiguration, 
                custom_resource_names: Optional[ThreeTierCustomResourceNames] = ..., 
                database_server: DatabaseConfiguration, 
                high_availability_config: Optional[HighAvailabilityConfiguration] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                storage_configuration: Optional[StorageConfiguration] = ..., 
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


    class azure.mgmt.workloads.models.ThreeTierCustomResourceNames(Model):
        naming_pattern_type: Union[str, NamingPatternType]

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


    class azure.mgmt.workloads.models.ThreeTierFullResourceNames(ThreeTierCustomResourceNames):
        application_server: ApplicationServerFullResourceNames
        central_server: CentralServerFullResourceNames
        database_server: DatabaseServerFullResourceNames
        naming_pattern_type: Union[str, NamingPatternType]
        shared_storage: SharedStorageResourceNames

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_server: Optional[ApplicationServerFullResourceNames] = ..., 
                central_server: Optional[CentralServerFullResourceNames] = ..., 
                database_server: Optional[DatabaseServerFullResourceNames] = ..., 
                shared_storage: Optional[SharedStorageResourceNames] = ..., 
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


    class azure.mgmt.workloads.models.ThreeTierRecommendationResult(SAPSizingRecommendationResult):
        application_server_instance_count: int
        application_server_vm_sku: str
        central_server_instance_count: int
        central_server_vm_sku: str
        database_instance_count: int
        db_vm_sku: str
        deployment_type: Union[str, SAPDeploymentType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_server_instance_count: Optional[int] = ..., 
                application_server_vm_sku: Optional[str] = ..., 
                central_server_instance_count: Optional[int] = ..., 
                central_server_vm_sku: Optional[str] = ..., 
                database_instance_count: Optional[int] = ..., 
                db_vm_sku: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.TrackedResource(Resource):
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


    class azure.mgmt.workloads.models.UpdateMonitorRequest(Model):
        identity: UserAssignedServiceIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedServiceIdentity] = ..., 
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


    class azure.mgmt.workloads.models.UpdateSAPApplicationInstanceRequest(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.workloads.models.UpdateSAPCentralInstanceRequest(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.workloads.models.UpdateSAPDatabaseInstanceRequest(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.workloads.models.UpdateSAPVirtualInstanceRequest(Model):
        identity: UserAssignedServiceIdentity
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedServiceIdentity] = ..., 
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


    class azure.mgmt.workloads.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.workloads.models.UserAssignedServiceIdentity(Model):
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


    class azure.mgmt.workloads.models.VirtualMachineConfiguration(Model):
        image_reference: ImageReference
        os_profile: OSProfile
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                image_reference: ImageReference, 
                os_profile: OSProfile, 
                vm_size: str, 
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


    class azure.mgmt.workloads.models.VirtualMachineResourceNames(Model):
        data_disk_names: dict[str, list[str]]
        host_name: str
        network_interfaces: list[NetworkInterfaceResourceNames]
        os_disk_name: str
        vm_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data_disk_names: Optional[Dict[str, List[str]]] = ..., 
                host_name: Optional[str] = ..., 
                network_interfaces: Optional[List[NetworkInterfaceResourceNames]] = ..., 
                os_disk_name: Optional[str] = ..., 
                vm_name: Optional[str] = ..., 
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


    class azure.mgmt.workloads.models.WindowsConfiguration(OSConfiguration):
        os_type: Union[str, OSType]

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


    class azure.mgmt.workloads.models.WorkloadMonitorActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.workloads.models.WorkloadMonitorProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MIGRATING = "Migrating"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


namespace azure.mgmt.workloads.operations

    class azure.mgmt.workloads.operations.MonitorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                monitor_parameter: Monitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Monitor]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Monitor]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Monitor: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Monitor]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Monitor]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: UpdateMonitorRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Monitor: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                body: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Monitor: ...


    class azure.mgmt.workloads.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Operation]: ...


    class azure.mgmt.workloads.operations.ProviderInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                provider_instance_parameter: ProviderInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                provider_instance_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                provider_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ProviderInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ProviderInstance]: ...


    class azure.mgmt.workloads.operations.SAPApplicationServerInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[SAPApplicationServerInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPApplicationServerInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPApplicationServerInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[UpdateSAPApplicationInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPApplicationServerInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPApplicationServerInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SAPApplicationServerInstance]: ...


    class azure.mgmt.workloads.operations.SAPCentralInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[SAPCentralServerInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPCentralServerInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPCentralServerInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[UpdateSAPCentralInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPCentralServerInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPCentralServerInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SAPCentralServerInstance]: ...


    class azure.mgmt.workloads.operations.SAPDatabaseInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[SAPDatabaseInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPDatabaseInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPDatabaseInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop_instance(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[UpdateSAPDatabaseInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPDatabaseInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPDatabaseInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SAPDatabaseInstance]: ...


    class azure.mgmt.workloads.operations.SAPVirtualInstancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[SAPVirtualInstance] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[StopRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SAPVirtualInstance]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[SAPVirtualInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[UpdateSAPVirtualInstanceRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...


    class azure.mgmt.workloads.operations.SapLandscapeMonitorOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: SapLandscapeMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> SapLandscapeMonitorListResult: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: SapLandscapeMonitor, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                monitor_name: str, 
                sap_landscape_monitor_parameter: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SapLandscapeMonitor: ...


    class azure.mgmt.workloads.operations.WorkloadsMgmtClientOperationsMixin(WorkloadsMgmtClientMixinABC):

        @overload
        def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[SAPAvailabilityZoneDetailsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def sap_availability_zone_details(
                self, 
                location: str, 
                sap_availability_zone_details: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[SAPDiskConfigurationsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def sap_disk_configurations(
                self, 
                location: str, 
                sap_disk_configurations: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[SAPSizingRecommendationRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def sap_sizing_recommendations(
                self, 
                location: str, 
                sap_sizing_recommendation: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[SAPSupportedSkusRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        def sap_supported_sku(
                self, 
                location: str, 
                sap_supported_sku: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...


```