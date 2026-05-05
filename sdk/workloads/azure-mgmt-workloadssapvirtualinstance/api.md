```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.workloadssapvirtualinstance

    class azure.mgmt.workloadssapvirtualinstance.WorkloadsSapVirtualInstanceMgmtClient: implements ContextManager 
        operations: Operations
        sap_application_server_instances: SAPApplicationServerInstancesOperations
        sap_central_server_instances: SAPCentralServerInstancesOperations
        sap_database_instances: SAPDatabaseInstancesOperations
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.workloadssapvirtualinstance.aio

    class azure.mgmt.workloadssapvirtualinstance.aio.WorkloadsSapVirtualInstanceMgmtClient: implements AsyncContextManager 
        operations: Operations
        sap_application_server_instances: SAPApplicationServerInstancesOperations
        sap_central_server_instances: SAPCentralServerInstancesOperations
        sap_database_instances: SAPDatabaseInstancesOperations
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.workloadssapvirtualinstance.aio.operations

    class azure.mgmt.workloadssapvirtualinstance.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.workloadssapvirtualinstance.aio.operations.SAPApplicationServerInstancesOperations:

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
                resource: SAPApplicationServerInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
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
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SAPApplicationServerInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: UpdateSAPApplicationInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.aio.operations.SAPCentralServerInstancesOperations:

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
                resource: SAPCentralServerInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
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
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SAPCentralServerInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: UpdateSAPCentralInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.aio.operations.SAPDatabaseInstancesOperations:

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
                resource: SAPDatabaseInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
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
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SAPDatabaseInstance]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: UpdateSAPDatabaseInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.aio.operations.SAPVirtualInstancesOperations:

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
                resource: SAPVirtualInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationStatusResult]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: UpdateSAPVirtualInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SAPVirtualInstance]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @overload
        async def get_availability_zone_details(
                self, 
                location: str, 
                body: SAPAvailabilityZoneDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def get_availability_zone_details(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def get_availability_zone_details(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        async def get_disk_configurations(
                self, 
                location: str, 
                body: SAPDiskConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def get_disk_configurations(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def get_disk_configurations(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        async def get_sap_supported_sku(
                self, 
                location: str, 
                body: SAPSupportedSkusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        async def get_sap_supported_sku(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        async def get_sap_supported_sku(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        async def get_sizing_recommendations(
                self, 
                location: str, 
                body: SAPSizingRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def get_sizing_recommendations(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        async def get_sizing_recommendations(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SAPVirtualInstance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[SAPVirtualInstance]: ...


namespace azure.mgmt.workloadssapvirtualinstance.models

    class azure.mgmt.workloadssapvirtualinstance.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.workloadssapvirtualinstance.models.ApplicationServerConfiguration(Model):
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        @overload
        def __init__(
                self, 
                *, 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ApplicationServerFullResourceNames(Model):
        availability_set_name: Optional[str]
        virtual_machines: Optional[List[VirtualMachineResourceNames]]

        @overload
        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ApplicationServerVirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        STANDBY = "Standby"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloadssapvirtualinstance.models.ApplicationServerVmDetails(Model):
        storage_details: Optional[List[StorageInformation]]
        type: Optional[Union[str, ApplicationServerVirtualMachineType]]
        virtual_machine_id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.CentralServerConfiguration(Model):
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        @overload
        def __init__(
                self, 
                *, 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.CentralServerFullResourceNames(Model):
        availability_set_name: Optional[str]
        load_balancer: Optional[LoadBalancerResourceNames]
        virtual_machines: Optional[List[VirtualMachineResourceNames]]

        @overload
        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                load_balancer: Optional[LoadBalancerResourceNames] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.CentralServerVirtualMachineType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASCS = "ASCS"
        ERS = "ERS"
        ERS_INACTIVE = "ERSInactive"
        PRIMARY = "Primary"
        SECONDARY = "Secondary"
        STANDBY = "Standby"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloadssapvirtualinstance.models.CentralServerVmDetails(Model):
        storage_details: Optional[List[StorageInformation]]
        type: Optional[Union[str, CentralServerVirtualMachineType]]
        virtual_machine_id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.CreateAndMountFileShareConfiguration(FileShareConfiguration, discriminator='CreateAndMount'):
        configuration_type: Literal[FileShareConfigurationType.CREATE_AND_MOUNT]
        resource_group: Optional[str]
        storage_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_group: Optional[str] = ..., 
                storage_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.workloadssapvirtualinstance.models.DatabaseConfiguration(Model):
        database_type: Optional[Union[str, SAPDatabaseType]]
        disk_configuration: Optional[DiskConfiguration]
        instance_count: int
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        @overload
        def __init__(
                self, 
                *, 
                database_type: Optional[Union[str, SAPDatabaseType]] = ..., 
                disk_configuration: Optional[DiskConfiguration] = ..., 
                instance_count: int, 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DatabaseServerFullResourceNames(Model):
        availability_set_name: Optional[str]
        load_balancer: Optional[LoadBalancerResourceNames]
        virtual_machines: Optional[List[VirtualMachineResourceNames]]

        @overload
        def __init__(
                self, 
                *, 
                availability_set_name: Optional[str] = ..., 
                load_balancer: Optional[LoadBalancerResourceNames] = ..., 
                virtual_machines: Optional[List[VirtualMachineResourceNames]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DatabaseVmDetails(Model):
        status: Optional[Union[str, SAPVirtualInstanceStatus]]
        storage_details: Optional[List[StorageInformation]]
        virtual_machine_id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.DeployerVmPackages(Model):
        storage_account_id: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                storage_account_id: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DeploymentConfiguration(SAPConfiguration, discriminator='Deployment'):
        app_location: Optional[str]
        configuration_type: Literal[SAPConfigurationType.DEPLOYMENT]
        infrastructure_configuration: Optional[InfrastructureConfiguration]
        software_configuration: Optional[SoftwareConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                app_location: Optional[str] = ..., 
                infrastructure_configuration: Optional[InfrastructureConfiguration] = ..., 
                software_configuration: Optional[SoftwareConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DeploymentWithOSConfiguration(SAPConfiguration, discriminator='DeploymentWithOSConfig'):
        app_location: Optional[str]
        configuration_type: Literal[SAPConfigurationType.DEPLOYMENT_WITH_OS_CONFIG]
        infrastructure_configuration: Optional[InfrastructureConfiguration]
        os_sap_configuration: Optional[OsSapConfiguration]
        software_configuration: Optional[SoftwareConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                app_location: Optional[str] = ..., 
                infrastructure_configuration: Optional[InfrastructureConfiguration] = ..., 
                os_sap_configuration: Optional[OsSapConfiguration] = ..., 
                software_configuration: Optional[SoftwareConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DiscoveryConfiguration(SAPConfiguration, discriminator='Discovery'):
        app_location: Optional[str]
        central_server_vm_id: Optional[str]
        configuration_type: Literal[SAPConfigurationType.DISCOVERY]
        managed_rg_storage_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                central_server_vm_id: Optional[str] = ..., 
                managed_rg_storage_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DiskConfiguration(Model):
        disk_volume_configurations: Optional[Dict[str, DiskVolumeConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                disk_volume_configurations: Optional[Dict[str, DiskVolumeConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DiskDetails(Model):
        disk_tier: Optional[str]
        iops_read_write: Optional[int]
        maximum_supported_disk_count: Optional[int]
        mbps_read_write: Optional[int]
        minimum_supported_disk_count: Optional[int]
        size_gb: Optional[int]
        sku: Optional[DiskSku]

        @overload
        def __init__(
                self, 
                *, 
                disk_tier: Optional[str] = ..., 
                iops_read_write: Optional[int] = ..., 
                maximum_supported_disk_count: Optional[int] = ..., 
                mbps_read_write: Optional[int] = ..., 
                minimum_supported_disk_count: Optional[int] = ..., 
                size_gb: Optional[int] = ..., 
                sku: Optional[DiskSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DiskSku(Model):
        name: Optional[Union[str, DiskSkuName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, DiskSkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.DiskSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_V2_LRS = "PremiumV2_LRS"
        PREMIUM_ZRS = "Premium_ZRS"
        STANDARD_LRS = "Standard_LRS"
        STANDARD_SSD_LRS = "StandardSSD_LRS"
        STANDARD_SSD_ZRS = "StandardSSD_ZRS"
        ULTRA_SSD_LRS = "UltraSSD_LRS"


    class azure.mgmt.workloadssapvirtualinstance.models.DiskVolumeConfiguration(Model):
        count: Optional[int]
        size_gb: Optional[int]
        sku: Optional[DiskSku]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                size_gb: Optional[int] = ..., 
                sku: Optional[DiskSku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.EnqueueReplicationServerProperties(Model):
        ers_version: Optional[Union[str, EnqueueReplicationServerType]]
        health: Optional[Union[str, SAPHealthState]]
        hostname: Optional[str]
        instance_no: Optional[str]
        ip_address: Optional[str]
        kernel_patch: Optional[str]
        kernel_version: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.EnqueueReplicationServerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENQUEUE_REPLICATOR1 = "EnqueueReplicator1"
        ENQUEUE_REPLICATOR2 = "EnqueueReplicator2"


    class azure.mgmt.workloadssapvirtualinstance.models.EnqueueServerProperties(Model):
        health: Optional[Union[str, SAPHealthState]]
        hostname: Optional[str]
        ip_address: Optional[str]
        port: Optional[int]


    class azure.mgmt.workloadssapvirtualinstance.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.ErrorDefinition(Model):
        code: Optional[str]
        details: Optional[List[ErrorDefinition]]
        message: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ExternalInstallationSoftwareConfiguration(SoftwareConfiguration, discriminator='External'):
        central_server_vm_id: Optional[str]
        software_installation_type: Literal[SAPSoftwareInstallationType.EXTERNAL]

        @overload
        def __init__(
                self, 
                *, 
                central_server_vm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.FileShareConfiguration(Model):
        configuration_type: str

        @overload
        def __init__(
                self, 
                *, 
                configuration_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.FileShareConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_AND_MOUNT = "CreateAndMount"
        MOUNT = "Mount"
        SKIP = "Skip"


    class azure.mgmt.workloadssapvirtualinstance.models.GatewayServerProperties(Model):
        health: Optional[Union[str, SAPHealthState]]
        port: Optional[int]


    class azure.mgmt.workloadssapvirtualinstance.models.HighAvailabilityConfiguration(Model):
        high_availability_type: Union[str, SAPHighAvailabilityType]

        @overload
        def __init__(
                self, 
                *, 
                high_availability_type: Union[str, SAPHighAvailabilityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.HighAvailabilitySoftwareConfiguration(Model):
        fencing_client_id: str
        fencing_client_password: str

        @overload
        def __init__(
                self, 
                *, 
                fencing_client_id: str, 
                fencing_client_password: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ImageReference(Model):
        id: Optional[str]
        offer: Optional[str]
        publisher: Optional[str]
        sku: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                offer: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                sku: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.InfrastructureConfiguration(Model):
        app_resource_group: str
        deployment_type: str

        @overload
        def __init__(
                self, 
                *, 
                app_resource_group: str, 
                deployment_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.LinuxConfiguration(OSConfiguration, discriminator='Linux'):
        disable_password_authentication: Optional[bool]
        os_type: Literal[OSType.LINUX]
        ssh: Optional[SshConfiguration]
        ssh_key_pair: Optional[SshKeyPair]

        @overload
        def __init__(
                self, 
                *, 
                disable_password_authentication: Optional[bool] = ..., 
                ssh: Optional[SshConfiguration] = ..., 
                ssh_key_pair: Optional[SshKeyPair] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.LoadBalancerDetails(Model):
        id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.LoadBalancerResourceNames(Model):
        backend_pool_names: Optional[List[str]]
        frontend_ip_configuration_names: Optional[List[str]]
        health_probe_names: Optional[List[str]]
        load_balancer_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                backend_pool_names: Optional[List[str]] = ..., 
                frontend_ip_configuration_names: Optional[List[str]] = ..., 
                health_probe_names: Optional[List[str]] = ..., 
                load_balancer_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ManagedRGConfiguration(Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ManagedResourcesNetworkAccessType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.workloadssapvirtualinstance.models.MessageServerProperties(Model):
        health: Optional[Union[str, SAPHealthState]]
        hostname: Optional[str]
        http_port: Optional[int]
        https_port: Optional[int]
        internal_ms_port: Optional[int]
        ip_address: Optional[str]
        ms_port: Optional[int]


    class azure.mgmt.workloadssapvirtualinstance.models.MountFileShareConfiguration(FileShareConfiguration, discriminator='Mount'):
        configuration_type: Literal[FileShareConfigurationType.MOUNT]
        id: str
        private_endpoint_id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                private_endpoint_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.NamingPatternType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULL_RESOURCE_NAME = "FullResourceName"


    class azure.mgmt.workloadssapvirtualinstance.models.NetworkConfiguration(Model):
        is_secondary_ip_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_secondary_ip_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.NetworkInterfaceResourceNames(Model):
        network_interface_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                network_interface_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.OSConfiguration(Model):
        os_type: str

        @overload
        def __init__(
                self, 
                *, 
                os_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.OSProfile(Model):
        admin_password: Optional[str]
        admin_username: Optional[str]
        os_configuration: Optional[OSConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                admin_password: Optional[str] = ..., 
                admin_username: Optional[str] = ..., 
                os_configuration: Optional[OSConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.OSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.workloadssapvirtualinstance.models.Operation(Model):
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


    class azure.mgmt.workloadssapvirtualinstance.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.OperationStatusResult(Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[List[OperationStatusResult]]
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
                operations: Optional[List[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.workloadssapvirtualinstance.models.OsSapConfiguration(Model):
        deployer_vm_packages: Optional[DeployerVmPackages]
        sap_fqdn: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deployer_vm_packages: Optional[DeployerVmPackages] = ..., 
                sap_fqdn: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.SAPApplicationServerInstance(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SAPApplicationServerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SAPApplicationServerProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPApplicationServerProperties(Model):
        dispatcher_status: Optional[str]
        errors: Optional[SAPVirtualInstanceError]
        gateway_port: Optional[int]
        health: Optional[Union[str, SAPHealthState]]
        hostname: Optional[str]
        icm_http_port: Optional[int]
        icm_https_port: Optional[int]
        instance_no: Optional[str]
        ip_address: Optional[str]
        kernel_patch: Optional[str]
        kernel_version: Optional[str]
        load_balancer_details: Optional[LoadBalancerDetails]
        provisioning_state: Optional[Union[str, SapVirtualInstanceProvisioningState]]
        status: Optional[Union[str, SAPVirtualInstanceStatus]]
        subnet: Optional[str]
        vm_details: Optional[List[ApplicationServerVmDetails]]


    class azure.mgmt.workloadssapvirtualinstance.models.SAPAvailabilityZoneDetailsRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        sap_product: Union[str, SAPProductType]

        @overload
        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                sap_product: Union[str, SAPProductType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPAvailabilityZoneDetailsResult(Model):
        availability_zone_pairs: Optional[List[SAPAvailabilityZonePair]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone_pairs: Optional[List[SAPAvailabilityZonePair]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPAvailabilityZonePair(Model):
        zone_a: Optional[int]
        zone_b: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                zone_a: Optional[int] = ..., 
                zone_b: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPCentralServerInstance(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SAPCentralServerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SAPCentralServerProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPCentralServerProperties(Model):
        enqueue_replication_server_properties: Optional[EnqueueReplicationServerProperties]
        enqueue_server_properties: Optional[EnqueueServerProperties]
        errors: Optional[SAPVirtualInstanceError]
        gateway_server_properties: Optional[GatewayServerProperties]
        health: Optional[Union[str, SAPHealthState]]
        instance_no: Optional[str]
        kernel_patch: Optional[str]
        kernel_version: Optional[str]
        load_balancer_details: Optional[LoadBalancerDetails]
        message_server_properties: Optional[MessageServerProperties]
        provisioning_state: Optional[Union[str, SapVirtualInstanceProvisioningState]]
        status: Optional[Union[str, SAPVirtualInstanceStatus]]
        subnet: Optional[str]
        vm_details: Optional[List[CentralServerVmDetails]]

        @overload
        def __init__(
                self, 
                *, 
                enqueue_replication_server_properties: Optional[EnqueueReplicationServerProperties] = ..., 
                enqueue_server_properties: Optional[EnqueueServerProperties] = ..., 
                gateway_server_properties: Optional[GatewayServerProperties] = ..., 
                message_server_properties: Optional[MessageServerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPConfiguration(Model):
        configuration_type: str

        @overload
        def __init__(
                self, 
                *, 
                configuration_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPConfigurationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOYMENT = "Deployment"
        DEPLOYMENT_WITH_OS_CONFIG = "DeploymentWithOSConfig"
        DISCOVERY = "Discovery"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDatabaseInstance(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[SAPDatabaseProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[SAPDatabaseProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDatabaseProperties(Model):
        database_sid: Optional[str]
        database_type: Optional[str]
        errors: Optional[SAPVirtualInstanceError]
        ip_address: Optional[str]
        load_balancer_details: Optional[LoadBalancerDetails]
        provisioning_state: Optional[Union[str, SapVirtualInstanceProvisioningState]]
        status: Optional[Union[str, SAPVirtualInstanceStatus]]
        subnet: Optional[str]
        vm_details: Optional[List[DatabaseVmDetails]]


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDatabaseScaleMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SCALE_UP = "ScaleUp"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDatabaseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DB2 = "DB2"
        HANA = "HANA"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SINGLE_SERVER = "SingleServer"
        THREE_TIER = "ThreeTier"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDiskConfiguration(Model):
        recommended_configuration: Optional[DiskVolumeConfiguration]
        supported_configurations: Optional[List[DiskDetails]]

        @overload
        def __init__(
                self, 
                *, 
                recommended_configuration: Optional[DiskVolumeConfiguration] = ..., 
                supported_configurations: Optional[List[DiskDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDiskConfigurationsRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        db_vm_sku: str
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        sap_product: Union[str, SAPProductType]

        @overload
        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                db_vm_sku: str, 
                deployment_type: Union[str, SAPDeploymentType], 
                environment: Union[str, SAPEnvironmentType], 
                sap_product: Union[str, SAPProductType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPDiskConfigurationsResult(Model):
        volume_configurations: Optional[Dict[str, SAPDiskConfiguration]]

        @overload
        def __init__(
                self, 
                *, 
                volume_configurations: Optional[Dict[str, SAPDiskConfiguration]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPEnvironmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NON_PROD = "NonProd"
        PROD = "Prod"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPHealthState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        HEALTHY = "Healthy"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPHighAvailabilityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABILITY_SET = "AvailabilitySet"
        AVAILABILITY_ZONE = "AvailabilityZone"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPInstallWithoutOSConfigSoftwareConfiguration(SoftwareConfiguration, discriminator='SAPInstallWithoutOSConfig'):
        bom_url: str
        high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration]
        sap_bits_storage_account_id: str
        software_installation_type: Literal[SAPSoftwareInstallationType.SAP_INSTALL_WITHOUT_OS_CONFIG]
        software_version: str

        @overload
        def __init__(
                self, 
                *, 
                bom_url: str, 
                high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration] = ..., 
                sap_bits_storage_account_id: str, 
                software_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPProductType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECC = "ECC"
        OTHER = "Other"
        S4HANA = "S4HANA"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSizingRecommendationRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        db_memory: int
        db_scale_method: Optional[Union[str, SAPDatabaseScaleMethod]]
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        high_availability_type: Optional[Union[str, SAPHighAvailabilityType]]
        sap_product: Union[str, SAPProductType]
        saps: int

        @overload
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
                saps: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSizingRecommendationResult(Model):
        deployment_type: str

        @overload
        def __init__(
                self, 
                *, 
                deployment_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSoftwareInstallationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        SAP_INSTALL_WITHOUT_OS_CONFIG = "SAPInstallWithoutOSConfig"
        SERVICE_INITIATED = "ServiceInitiated"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSupportedResourceSkusResult(Model):
        supported_skus: Optional[List[SAPSupportedSku]]

        @overload
        def __init__(
                self, 
                *, 
                supported_skus: Optional[List[SAPSupportedSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSupportedSku(Model):
        is_app_server_certified: Optional[bool]
        is_database_certified: Optional[bool]
        vm_sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_app_server_certified: Optional[bool] = ..., 
                is_database_certified: Optional[bool] = ..., 
                vm_sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPSupportedSkusRequest(Model):
        app_location: str
        database_type: Union[str, SAPDatabaseType]
        deployment_type: Union[str, SAPDeploymentType]
        environment: Union[str, SAPEnvironmentType]
        high_availability_type: Optional[Union[str, SAPHighAvailabilityType]]
        sap_product: Union[str, SAPProductType]

        @overload
        def __init__(
                self, 
                *, 
                app_location: str, 
                database_type: Union[str, SAPDatabaseType], 
                deployment_type: Union[str, SAPDeploymentType], 
                environment: Union[str, SAPEnvironmentType], 
                high_availability_type: Optional[Union[str, SAPHighAvailabilityType]] = ..., 
                sap_product: Union[str, SAPProductType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstance(TrackedResource):
        id: str
        identity: Optional[SAPVirtualInstanceIdentity]
        location: str
        name: str
        properties: Optional[SAPVirtualInstanceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SAPVirtualInstanceIdentity] = ..., 
                location: str, 
                properties: Optional[SAPVirtualInstanceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceError(Model):
        properties: Optional[ErrorDefinition]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ErrorDefinition] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceIdentity(Model):
        type: Union[str, SAPVirtualInstanceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SAPVirtualInstanceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceProperties(Model):
        configuration: SAPConfiguration
        environment: Union[str, SAPEnvironmentType]
        errors: Optional[SAPVirtualInstanceError]
        health: Optional[Union[str, SAPHealthState]]
        managed_resource_group_configuration: Optional[ManagedRGConfiguration]
        managed_resources_network_access_type: Optional[Union[str, ManagedResourcesNetworkAccessType]]
        provisioning_state: Optional[Union[str, SapVirtualInstanceProvisioningState]]
        sap_product: Union[str, SAPProductType]
        state: Optional[Union[str, SAPVirtualInstanceState]]
        status: Optional[Union[str, SAPVirtualInstanceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                configuration: SAPConfiguration, 
                environment: Union[str, SAPEnvironmentType], 
                managed_resource_group_configuration: Optional[ManagedRGConfiguration] = ..., 
                managed_resources_network_access_type: Optional[Union[str, ManagedResourcesNetworkAccessType]] = ..., 
                sap_product: Union[str, SAPProductType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACSS_INSTALLATION_BLOCKED = "ACSSInstallationBlocked"
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


    class azure.mgmt.workloadssapvirtualinstance.models.SAPVirtualInstanceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OFFLINE = "Offline"
        PARTIALLY_RUNNING = "PartiallyRunning"
        RUNNING = "Running"
        SOFT_SHUTDOWN = "SoftShutdown"
        STARTING = "Starting"
        STOPPING = "Stopping"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.workloadssapvirtualinstance.models.SapVirtualInstanceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.workloadssapvirtualinstance.models.ServiceInitiatedSoftwareConfiguration(SoftwareConfiguration, discriminator='ServiceInitiated'):
        bom_url: str
        high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration]
        sap_bits_storage_account_id: str
        sap_fqdn: str
        software_installation_type: Literal[SAPSoftwareInstallationType.SERVICE_INITIATED]
        software_version: str
        ssh_private_key: str

        @overload
        def __init__(
                self, 
                *, 
                bom_url: str, 
                high_availability_software_configuration: Optional[HighAvailabilitySoftwareConfiguration] = ..., 
                sap_bits_storage_account_id: str, 
                sap_fqdn: str, 
                software_version: str, 
                ssh_private_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SharedStorageResourceNames(Model):
        shared_storage_account_name: Optional[str]
        shared_storage_account_private_end_point_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                shared_storage_account_name: Optional[str] = ..., 
                shared_storage_account_private_end_point_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SingleServerConfiguration(InfrastructureConfiguration, discriminator='SingleServer'):
        app_resource_group: str
        custom_resource_names: Optional[SingleServerCustomResourceNames]
        database_type: Optional[Union[str, SAPDatabaseType]]
        db_disk_configuration: Optional[DiskConfiguration]
        deployment_type: Literal[SAPDeploymentType.SINGLE_SERVER]
        network_configuration: Optional[NetworkConfiguration]
        subnet_id: str
        virtual_machine_configuration: VirtualMachineConfiguration

        @overload
        def __init__(
                self, 
                *, 
                app_resource_group: str, 
                custom_resource_names: Optional[SingleServerCustomResourceNames] = ..., 
                database_type: Optional[Union[str, SAPDatabaseType]] = ..., 
                db_disk_configuration: Optional[DiskConfiguration] = ..., 
                network_configuration: Optional[NetworkConfiguration] = ..., 
                subnet_id: str, 
                virtual_machine_configuration: VirtualMachineConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SingleServerCustomResourceNames(Model):
        naming_pattern_type: str

        @overload
        def __init__(
                self, 
                *, 
                naming_pattern_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SingleServerFullResourceNames(SingleServerCustomResourceNames, discriminator='FullResourceName'):
        naming_pattern_type: Literal[NamingPatternType.FULL_RESOURCE_NAME]
        virtual_machine: Optional[VirtualMachineResourceNames]

        @overload
        def __init__(
                self, 
                *, 
                virtual_machine: Optional[VirtualMachineResourceNames] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SingleServerRecommendationResult(SAPSizingRecommendationResult, discriminator='SingleServer'):
        deployment_type: Literal[SAPDeploymentType.SINGLE_SERVER]
        vm_sku: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                vm_sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SkipFileShareConfiguration(FileShareConfiguration, discriminator='Skip'):
        configuration_type: Literal[FileShareConfigurationType.SKIP]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SoftwareConfiguration(Model):
        software_installation_type: str

        @overload
        def __init__(
                self, 
                *, 
                software_installation_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SshConfiguration(Model):
        public_keys: Optional[List[SshPublicKey]]

        @overload
        def __init__(
                self, 
                *, 
                public_keys: Optional[List[SshPublicKey]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SshKeyPair(Model):
        private_key: Optional[str]
        public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_key: Optional[str] = ..., 
                public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.SshPublicKey(Model):
        key_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.StartRequest(Model):
        start_vm: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                start_vm: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.StopRequest(Model):
        deallocate_vm: Optional[bool]
        soft_stop_timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deallocate_vm: Optional[bool] = ..., 
                soft_stop_timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.StorageConfiguration(Model):
        transport_file_share_configuration: Optional[FileShareConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                transport_file_share_configuration: Optional[FileShareConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.StorageInformation(Model):
        id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.SystemData(Model):
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


    class azure.mgmt.workloadssapvirtualinstance.models.ThreeTierConfiguration(InfrastructureConfiguration, discriminator='ThreeTier'):
        app_resource_group: str
        application_server: ApplicationServerConfiguration
        central_server: CentralServerConfiguration
        custom_resource_names: Optional[ThreeTierCustomResourceNames]
        database_server: DatabaseConfiguration
        deployment_type: Literal[SAPDeploymentType.THREE_TIER]
        high_availability_config: Optional[HighAvailabilityConfiguration]
        network_configuration: Optional[NetworkConfiguration]
        storage_configuration: Optional[StorageConfiguration]

        @overload
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
                storage_configuration: Optional[StorageConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ThreeTierCustomResourceNames(Model):
        naming_pattern_type: str

        @overload
        def __init__(
                self, 
                *, 
                naming_pattern_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ThreeTierFullResourceNames(ThreeTierCustomResourceNames, discriminator='FullResourceName'):
        application_server: Optional[ApplicationServerFullResourceNames]
        central_server: Optional[CentralServerFullResourceNames]
        database_server: Optional[DatabaseServerFullResourceNames]
        naming_pattern_type: Literal[NamingPatternType.FULL_RESOURCE_NAME]
        shared_storage: Optional[SharedStorageResourceNames]

        @overload
        def __init__(
                self, 
                *, 
                application_server: Optional[ApplicationServerFullResourceNames] = ..., 
                central_server: Optional[CentralServerFullResourceNames] = ..., 
                database_server: Optional[DatabaseServerFullResourceNames] = ..., 
                shared_storage: Optional[SharedStorageResourceNames] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.ThreeTierRecommendationResult(SAPSizingRecommendationResult, discriminator='ThreeTier'):
        application_server_instance_count: Optional[int]
        application_server_vm_sku: Optional[str]
        central_server_instance_count: Optional[int]
        central_server_vm_sku: Optional[str]
        database_instance_count: Optional[int]
        db_vm_sku: Optional[str]
        deployment_type: Literal[SAPDeploymentType.THREE_TIER]

        @overload
        def __init__(
                self, 
                *, 
                application_server_instance_count: Optional[int] = ..., 
                application_server_vm_sku: Optional[str] = ..., 
                central_server_instance_count: Optional[int] = ..., 
                central_server_vm_sku: Optional[str] = ..., 
                database_instance_count: Optional[int] = ..., 
                db_vm_sku: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.TrackedResource(Resource):
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


    class azure.mgmt.workloadssapvirtualinstance.models.UpdateSAPApplicationInstanceRequest(Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.UpdateSAPCentralInstanceRequest(Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.UpdateSAPDatabaseInstanceRequest(Model):
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.UpdateSAPVirtualInstanceProperties(Model):
        managed_resources_network_access_type: Optional[Union[str, ManagedResourcesNetworkAccessType]]

        @overload
        def __init__(
                self, 
                *, 
                managed_resources_network_access_type: Optional[Union[str, ManagedResourcesNetworkAccessType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.UpdateSAPVirtualInstanceRequest(Model):
        identity: Optional[SAPVirtualInstanceIdentity]
        properties: Optional[UpdateSAPVirtualInstanceProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SAPVirtualInstanceIdentity] = ..., 
                properties: Optional[UpdateSAPVirtualInstanceProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.UserAssignedIdentity(Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.workloadssapvirtualinstance.models.VirtualMachineConfiguration(Model):
        image_reference: ImageReference
        os_profile: OSProfile
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                image_reference: ImageReference, 
                os_profile: OSProfile, 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.VirtualMachineResourceNames(Model):
        data_disk_names: Optional[Dict[str, List[str]]]
        host_name: Optional[str]
        network_interfaces: Optional[List[NetworkInterfaceResourceNames]]
        os_disk_name: Optional[str]
        vm_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_disk_names: Optional[Dict[str, List[str]]] = ..., 
                host_name: Optional[str] = ..., 
                network_interfaces: Optional[List[NetworkInterfaceResourceNames]] = ..., 
                os_disk_name: Optional[str] = ..., 
                vm_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.workloadssapvirtualinstance.models.WindowsConfiguration(OSConfiguration, discriminator='Windows'):
        os_type: Literal[OSType.WINDOWS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.workloadssapvirtualinstance.operations

    class azure.mgmt.workloadssapvirtualinstance.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.workloadssapvirtualinstance.operations.SAPApplicationServerInstancesOperations:

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
                resource: SAPApplicationServerInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
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
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> Iterable[SAPApplicationServerInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: UpdateSAPApplicationInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                application_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPApplicationServerInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.operations.SAPCentralServerInstancesOperations:

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
                resource: SAPCentralServerInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
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
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> Iterable[SAPCentralServerInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: UpdateSAPCentralInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                central_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPCentralServerInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.operations.SAPDatabaseInstancesOperations:

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
                resource: SAPDatabaseInstance, 
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
                resource: JSON, 
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
                resource: IO[bytes], 
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
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
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
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> Iterable[SAPDatabaseInstance]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: UpdateSAPDatabaseInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                database_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDatabaseInstance: ...


    class azure.mgmt.workloadssapvirtualinstance.operations.SAPVirtualInstancesOperations:

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
                resource: SAPVirtualInstance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[StartRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_start(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
                body: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_stop(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationStatusResult]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: UpdateSAPVirtualInstanceRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SAPVirtualInstance]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sap_virtual_instance_name: str, 
                **kwargs: Any
            ) -> SAPVirtualInstance: ...

        @overload
        def get_availability_zone_details(
                self, 
                location: str, 
                body: SAPAvailabilityZoneDetailsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def get_availability_zone_details(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def get_availability_zone_details(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPAvailabilityZoneDetailsResult: ...

        @overload
        def get_disk_configurations(
                self, 
                location: str, 
                body: SAPDiskConfigurationsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def get_disk_configurations(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def get_disk_configurations(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPDiskConfigurationsResult: ...

        @overload
        def get_sap_supported_sku(
                self, 
                location: str, 
                body: SAPSupportedSkusRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        def get_sap_supported_sku(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        def get_sap_supported_sku(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSupportedResourceSkusResult: ...

        @overload
        def get_sizing_recommendations(
                self, 
                location: str, 
                body: SAPSizingRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def get_sizing_recommendations(
                self, 
                location: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @overload
        def get_sizing_recommendations(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SAPSizingRecommendationResult: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[SAPVirtualInstance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[SAPVirtualInstance]: ...


```