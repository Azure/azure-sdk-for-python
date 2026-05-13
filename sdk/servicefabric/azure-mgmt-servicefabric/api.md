```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.servicefabric

    class azure.mgmt.servicefabric.ServiceFabricManagementClient: implements ContextManager 
        application_type_versions: ApplicationTypeVersionsOperations
        application_types: ApplicationTypesOperations
        applications: ApplicationsOperations
        cluster_versions: ClusterVersionsOperations
        clusters: ClustersOperations
        operations: Operations
        services: ServicesOperations
        unsupported_vm_sizes: UnsupportedVmSizesOperations

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


namespace azure.mgmt.servicefabric.aio

    class azure.mgmt.servicefabric.aio.ServiceFabricManagementClient: implements AsyncContextManager 
        application_type_versions: ApplicationTypeVersionsOperations
        application_types: ApplicationTypesOperations
        applications: ApplicationsOperations
        cluster_versions: ClusterVersionsOperations
        clusters: ClustersOperations
        operations: Operations
        services: ServicesOperations
        unsupported_vm_sizes: UnsupportedVmSizesOperations

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


namespace azure.mgmt.servicefabric.aio.operations

    class azure.mgmt.servicefabric.aio.operations.ApplicationTypeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationTypeVersionResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationTypeVersionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ApplicationTypeVersionResource]: ...


    class azure.mgmt.servicefabric.aio.operations.ApplicationTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ApplicationTypeResource]: ...


    class azure.mgmt.servicefabric.aio.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ApplicationResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ApplicationResource]: ...


    class azure.mgmt.servicefabric.aio.operations.ClusterVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                cluster_version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace_async
        async def get_by_environment(
                self, 
                location: str, 
                environment: Union[str, ClusterVersionsEnvironment], 
                cluster_version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace_async
        async def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace_async
        async def list_by_environment(
                self, 
                location: str, 
                environment: Union[str, ClusterVersionsEnvironment], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...


    class azure.mgmt.servicefabric.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[Cluster]: ...

        @overload
        async def list_upgradable_versions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                versions_description: Optional[UpgradableVersionsDescription] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpgradableVersionPathResult: ...

        @overload
        async def list_upgradable_versions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                versions_description: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpgradableVersionPathResult: ...


    class azure.mgmt.servicefabric.aio.operations.Operations:

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
            ) -> AsyncIterable[OperationResult]: ...


    class azure.mgmt.servicefabric.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[ServiceResource]: ...


    class azure.mgmt.servicefabric.aio.operations.UnsupportedVmSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                vm_size: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VMSizeResource: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[VMSizeResource]: ...


namespace azure.mgmt.servicefabric.models

    class azure.mgmt.servicefabric.models.AddOnFeatures(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_RESTORE_SERVICE = "BackupRestoreService"
        DNS_SERVICE = "DnsService"
        REPAIR_MANAGER = "RepairManager"
        RESOURCE_MONITOR_SERVICE = "ResourceMonitorService"


    class azure.mgmt.servicefabric.models.ApplicationDeltaHealthPolicy(Model):
        default_service_type_delta_health_policy: ServiceTypeDeltaHealthPolicy
        service_type_delta_health_policies: dict[str, ServiceTypeDeltaHealthPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_service_type_delta_health_policy: Optional[ServiceTypeDeltaHealthPolicy] = ..., 
                service_type_delta_health_policies: Optional[Dict[str, ServiceTypeDeltaHealthPolicy]] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationHealthPolicy(Model):
        default_service_type_health_policy: ServiceTypeHealthPolicy
        service_type_health_policies: dict[str, ServiceTypeHealthPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_service_type_health_policy: Optional[ServiceTypeHealthPolicy] = ..., 
                service_type_health_policies: Optional[Dict[str, ServiceTypeHealthPolicy]] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationMetricDescription(Model):
        maximum_capacity: int
        name: str
        reservation_capacity: int
        total_application_capacity: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                maximum_capacity: Optional[int] = ..., 
                name: Optional[str] = ..., 
                reservation_capacity: Optional[int] = ..., 
                total_application_capacity: Optional[int] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationResource(ProxyResource):
        etag: str
        id: str
        identity: ManagedIdentity
        location: str
        managed_identities: list[ApplicationUserAssignedIdentity]
        maximum_nodes: int
        metrics: list[ApplicationMetricDescription]
        minimum_nodes: int
        name: str
        parameters: dict[str, str]
        provisioning_state: str
        remove_application_capacity: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str
        type_name: str
        type_version: str
        upgrade_policy: ApplicationUpgradePolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedIdentity] = ..., 
                location: Optional[str] = ..., 
                managed_identities: Optional[List[ApplicationUserAssignedIdentity]] = ..., 
                maximum_nodes: int = 0, 
                metrics: Optional[List[ApplicationMetricDescription]] = ..., 
                minimum_nodes: Optional[int] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                remove_application_capacity: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                type_name: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                upgrade_policy: Optional[ApplicationUpgradePolicy] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationResourceList(Model):
        next_link: str
        value: list[ApplicationResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ApplicationResource]] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationResourceProperties(ApplicationResourceUpdateProperties):
        managed_identities: list[ApplicationUserAssignedIdentity]
        maximum_nodes: int
        metrics: list[ApplicationMetricDescription]
        minimum_nodes: int
        parameters: dict[str, str]
        provisioning_state: str
        remove_application_capacity: bool
        type_name: str
        type_version: str
        upgrade_policy: ApplicationUpgradePolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_identities: Optional[List[ApplicationUserAssignedIdentity]] = ..., 
                maximum_nodes: int = 0, 
                metrics: Optional[List[ApplicationMetricDescription]] = ..., 
                minimum_nodes: Optional[int] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                remove_application_capacity: Optional[bool] = ..., 
                type_name: Optional[str] = ..., 
                type_version: Optional[str] = ..., 
                upgrade_policy: Optional[ApplicationUpgradePolicy] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationResourceUpdate(ProxyResource):
        etag: str
        id: str
        location: str
        managed_identities: list[ApplicationUserAssignedIdentity]
        maximum_nodes: int
        metrics: list[ApplicationMetricDescription]
        minimum_nodes: int
        name: str
        parameters: dict[str, str]
        remove_application_capacity: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str
        type_version: str
        upgrade_policy: ApplicationUpgradePolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                managed_identities: Optional[List[ApplicationUserAssignedIdentity]] = ..., 
                maximum_nodes: int = 0, 
                metrics: Optional[List[ApplicationMetricDescription]] = ..., 
                minimum_nodes: Optional[int] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                remove_application_capacity: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                type_version: Optional[str] = ..., 
                upgrade_policy: Optional[ApplicationUpgradePolicy] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationResourceUpdateProperties(Model):
        managed_identities: list[ApplicationUserAssignedIdentity]
        maximum_nodes: int
        metrics: list[ApplicationMetricDescription]
        minimum_nodes: int
        parameters: dict[str, str]
        remove_application_capacity: bool
        type_version: str
        upgrade_policy: ApplicationUpgradePolicy

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_identities: Optional[List[ApplicationUserAssignedIdentity]] = ..., 
                maximum_nodes: int = 0, 
                metrics: Optional[List[ApplicationMetricDescription]] = ..., 
                minimum_nodes: Optional[int] = ..., 
                parameters: Optional[Dict[str, str]] = ..., 
                remove_application_capacity: Optional[bool] = ..., 
                type_version: Optional[str] = ..., 
                upgrade_policy: Optional[ApplicationUpgradePolicy] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationTypeResource(ProxyResource):
        etag: str
        id: str
        location: str
        name: str
        provisioning_state: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

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


    class azure.mgmt.servicefabric.models.ApplicationTypeResourceList(Model):
        next_link: str
        value: list[ApplicationTypeResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ApplicationTypeResource]] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationTypeVersionResource(ProxyResource):
        app_package_url: str
        default_parameter_list: dict[str, str]
        etag: str
        id: str
        location: str
        name: str
        provisioning_state: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_package_url: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationTypeVersionResourceList(Model):
        next_link: str
        value: list[ApplicationTypeVersionResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ApplicationTypeVersionResource]] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationTypeVersionsCleanupPolicy(Model):
        max_unused_versions_to_keep: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_unused_versions_to_keep: int, 
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


    class azure.mgmt.servicefabric.models.ApplicationUpgradePolicy(Model):
        application_health_policy: ArmApplicationHealthPolicy
        force_restart: bool
        recreate_application: bool
        rolling_upgrade_monitoring_policy: ArmRollingUpgradeMonitoringPolicy
        upgrade_mode: Union[str, RollingUpgradeMode]
        upgrade_replica_set_check_timeout: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_health_policy: Optional[ArmApplicationHealthPolicy] = ..., 
                force_restart: bool = False, 
                recreate_application: Optional[bool] = ..., 
                rolling_upgrade_monitoring_policy: Optional[ArmRollingUpgradeMonitoringPolicy] = ..., 
                upgrade_mode: Union[str, RollingUpgradeMode] = "Monitored", 
                upgrade_replica_set_check_timeout: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ApplicationUserAssignedIdentity(Model):
        name: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                principal_id: str, 
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


    class azure.mgmt.servicefabric.models.ArmApplicationHealthPolicy(Model):
        consider_warning_as_error: bool
        default_service_type_health_policy: ArmServiceTypeHealthPolicy
        max_percent_unhealthy_deployed_applications: int
        service_type_health_policy_map: dict[str, ArmServiceTypeHealthPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                consider_warning_as_error: bool = False, 
                default_service_type_health_policy: Optional[ArmServiceTypeHealthPolicy] = ..., 
                max_percent_unhealthy_deployed_applications: int = 0, 
                service_type_health_policy_map: Optional[Dict[str, ArmServiceTypeHealthPolicy]] = ..., 
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


    class azure.mgmt.servicefabric.models.ArmRollingUpgradeMonitoringPolicy(Model):
        failure_action: Union[str, ArmUpgradeFailureAction]
        health_check_retry_timeout: str
        health_check_stable_duration: str
        health_check_wait_duration: str
        upgrade_domain_timeout: str
        upgrade_timeout: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failure_action: Optional[Union[str, ArmUpgradeFailureAction]] = ..., 
                health_check_retry_timeout: str = "PT0H10M0S", 
                health_check_stable_duration: str = "PT0H2M0S", 
                health_check_wait_duration: str = "0", 
                upgrade_domain_timeout: str = "P10675199DT02H48M05.4775807S", 
                upgrade_timeout: str = "P10675199DT02H48M05.4775807S", 
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


    class azure.mgmt.servicefabric.models.ArmServicePackageActivationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUSIVE_PROCESS = "ExclusiveProcess"
        SHARED_PROCESS = "SharedProcess"


    class azure.mgmt.servicefabric.models.ArmServiceTypeHealthPolicy(Model):
        max_percent_unhealthy_partitions_per_service: int
        max_percent_unhealthy_replicas_per_partition: int
        max_percent_unhealthy_services: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_percent_unhealthy_partitions_per_service: int = 0, 
                max_percent_unhealthy_replicas_per_partition: int = 0, 
                max_percent_unhealthy_services: int = 0, 
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


    class azure.mgmt.servicefabric.models.ArmUpgradeFailureAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        ROLLBACK = "Rollback"


    class azure.mgmt.servicefabric.models.AvailableOperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.AzureActiveDirectory(Model):
        client_application: str
        cluster_application: str
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_application: Optional[str] = ..., 
                cluster_application: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.CertificateDescription(Model):
        thumbprint: str
        thumbprint_secondary: str
        x509_store_name: Union[str, StoreName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                thumbprint: str, 
                thumbprint_secondary: Optional[str] = ..., 
                x509_store_name: Optional[Union[str, StoreName]] = ..., 
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


    class azure.mgmt.servicefabric.models.ClientCertificateCommonName(Model):
        certificate_common_name: str
        certificate_issuer_thumbprint: str
        is_admin: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_common_name: str, 
                certificate_issuer_thumbprint: str, 
                is_admin: bool, 
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


    class azure.mgmt.servicefabric.models.ClientCertificateThumbprint(Model):
        certificate_thumbprint: str
        is_admin: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_thumbprint: str, 
                is_admin: bool, 
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


    class azure.mgmt.servicefabric.models.Cluster(Resource):
        add_on_features: Union[list[str, AddOnFeatures]]
        application_type_versions_cleanup_policy: ApplicationTypeVersionsCleanupPolicy
        available_cluster_versions: list[ClusterVersionDetails]
        azure_active_directory: AzureActiveDirectory
        certificate: CertificateDescription
        certificate_common_names: ServerCertificateCommonNames
        client_certificate_common_names: list[ClientCertificateCommonName]
        client_certificate_thumbprints: list[ClientCertificateThumbprint]
        cluster_code_version: str
        cluster_endpoint: str
        cluster_id: str
        cluster_state: Union[str, ClusterState]
        diagnostics_storage_account_config: DiagnosticsStorageAccountConfig
        enable_http_gateway_exclusive_auth_mode: bool
        etag: str
        event_store_service_enabled: bool
        fabric_settings: list[SettingsSectionDescription]
        id: str
        infrastructure_service_manager: bool
        location: str
        management_endpoint: str
        name: str
        node_types: list[NodeTypeDescription]
        notifications: list[Notification]
        provisioning_state: Union[str, ProvisioningState]
        reliability_level: Union[str, ReliabilityLevel]
        reverse_proxy_certificate: CertificateDescription
        reverse_proxy_certificate_common_names: ServerCertificateCommonNames
        sf_zonal_upgrade_mode: Union[str, SfZonalUpgradeMode]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        upgrade_description: ClusterUpgradePolicy
        upgrade_mode: Union[str, UpgradeMode]
        upgrade_pause_end_timestamp_utc: datetime
        upgrade_pause_start_timestamp_utc: datetime
        upgrade_wave: Union[str, ClusterUpgradeCadence]
        vm_image: str
        vmss_zonal_upgrade_mode: Union[str, VmssZonalUpgradeMode]
        wave_upgrade_paused: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add_on_features: Optional[List[Union[str, AddOnFeatures]]] = ..., 
                application_type_versions_cleanup_policy: Optional[ApplicationTypeVersionsCleanupPolicy] = ..., 
                azure_active_directory: Optional[AzureActiveDirectory] = ..., 
                certificate: Optional[CertificateDescription] = ..., 
                certificate_common_names: Optional[ServerCertificateCommonNames] = ..., 
                client_certificate_common_names: Optional[List[ClientCertificateCommonName]] = ..., 
                client_certificate_thumbprints: Optional[List[ClientCertificateThumbprint]] = ..., 
                cluster_code_version: Optional[str] = ..., 
                diagnostics_storage_account_config: Optional[DiagnosticsStorageAccountConfig] = ..., 
                enable_http_gateway_exclusive_auth_mode: Optional[bool] = ..., 
                event_store_service_enabled: Optional[bool] = ..., 
                fabric_settings: Optional[List[SettingsSectionDescription]] = ..., 
                infrastructure_service_manager: Optional[bool] = ..., 
                location: str, 
                management_endpoint: Optional[str] = ..., 
                node_types: Optional[List[NodeTypeDescription]] = ..., 
                notifications: Optional[List[Notification]] = ..., 
                reliability_level: Optional[Union[str, ReliabilityLevel]] = ..., 
                reverse_proxy_certificate: Optional[CertificateDescription] = ..., 
                reverse_proxy_certificate_common_names: Optional[ServerCertificateCommonNames] = ..., 
                sf_zonal_upgrade_mode: Optional[Union[str, SfZonalUpgradeMode]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                upgrade_description: Optional[ClusterUpgradePolicy] = ..., 
                upgrade_mode: Union[str, UpgradeMode] = "Automatic", 
                upgrade_pause_end_timestamp_utc: Optional[datetime] = ..., 
                upgrade_pause_start_timestamp_utc: Optional[datetime] = ..., 
                upgrade_wave: Optional[Union[str, ClusterUpgradeCadence]] = ..., 
                vm_image: Optional[str] = ..., 
                vmss_zonal_upgrade_mode: Optional[Union[str, VmssZonalUpgradeMode]] = ..., 
                wave_upgrade_paused: Optional[bool] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterCodeVersionsListResult(Model):
        next_link: str
        value: list[ClusterCodeVersionsResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ClusterCodeVersionsResult]] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterCodeVersionsResult(Model):
        code_version: str
        environment: Union[str, ClusterEnvironment]
        id: str
        name: str
        support_expiry_utc: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_version: Optional[str] = ..., 
                environment: Optional[Union[str, ClusterEnvironment]] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                support_expiry_utc: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.servicefabric.models.ClusterHealthPolicy(Model):
        application_health_policies: dict[str, ApplicationHealthPolicy]
        max_percent_unhealthy_applications: int
        max_percent_unhealthy_nodes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_health_policies: Optional[Dict[str, ApplicationHealthPolicy]] = ..., 
                max_percent_unhealthy_applications: int = 0, 
                max_percent_unhealthy_nodes: int = 0, 
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


    class azure.mgmt.servicefabric.models.ClusterListResult(Model):
        next_link: str
        value: list[Cluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Cluster]] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_SCALE = "AutoScale"
        BASELINE_UPGRADE = "BaselineUpgrade"
        DEPLOYING = "Deploying"
        ENFORCING_CLUSTER_VERSION = "EnforcingClusterVersion"
        READY = "Ready"
        UPDATING_INFRASTRUCTURE = "UpdatingInfrastructure"
        UPDATING_USER_CERTIFICATE = "UpdatingUserCertificate"
        UPDATING_USER_CONFIGURATION = "UpdatingUserConfiguration"
        UPGRADE_SERVICE_UNREACHABLE = "UpgradeServiceUnreachable"
        WAITING_FOR_NODES = "WaitingForNodes"


    class azure.mgmt.servicefabric.models.ClusterUpdateParameters(Model):
        add_on_features: Union[list[str, AddOnFeatures]]
        application_type_versions_cleanup_policy: ApplicationTypeVersionsCleanupPolicy
        certificate: CertificateDescription
        certificate_common_names: ServerCertificateCommonNames
        client_certificate_common_names: list[ClientCertificateCommonName]
        client_certificate_thumbprints: list[ClientCertificateThumbprint]
        cluster_code_version: str
        enable_http_gateway_exclusive_auth_mode: bool
        event_store_service_enabled: bool
        fabric_settings: list[SettingsSectionDescription]
        infrastructure_service_manager: bool
        node_types: list[NodeTypeDescription]
        notifications: list[Notification]
        reliability_level: Union[str, ReliabilityLevel]
        reverse_proxy_certificate: CertificateDescription
        sf_zonal_upgrade_mode: Union[str, SfZonalUpgradeMode]
        tags: dict[str, str]
        upgrade_description: ClusterUpgradePolicy
        upgrade_mode: Union[str, UpgradeMode]
        upgrade_pause_end_timestamp_utc: datetime
        upgrade_pause_start_timestamp_utc: datetime
        upgrade_wave: Union[str, ClusterUpgradeCadence]
        vmss_zonal_upgrade_mode: Union[str, VmssZonalUpgradeMode]
        wave_upgrade_paused: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                add_on_features: Optional[List[Union[str, AddOnFeatures]]] = ..., 
                application_type_versions_cleanup_policy: Optional[ApplicationTypeVersionsCleanupPolicy] = ..., 
                certificate: Optional[CertificateDescription] = ..., 
                certificate_common_names: Optional[ServerCertificateCommonNames] = ..., 
                client_certificate_common_names: Optional[List[ClientCertificateCommonName]] = ..., 
                client_certificate_thumbprints: Optional[List[ClientCertificateThumbprint]] = ..., 
                cluster_code_version: Optional[str] = ..., 
                enable_http_gateway_exclusive_auth_mode: Optional[bool] = ..., 
                event_store_service_enabled: Optional[bool] = ..., 
                fabric_settings: Optional[List[SettingsSectionDescription]] = ..., 
                infrastructure_service_manager: Optional[bool] = ..., 
                node_types: Optional[List[NodeTypeDescription]] = ..., 
                notifications: Optional[List[Notification]] = ..., 
                reliability_level: Optional[Union[str, ReliabilityLevel]] = ..., 
                reverse_proxy_certificate: Optional[CertificateDescription] = ..., 
                sf_zonal_upgrade_mode: Optional[Union[str, SfZonalUpgradeMode]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                upgrade_description: Optional[ClusterUpgradePolicy] = ..., 
                upgrade_mode: Union[str, UpgradeMode] = "Automatic", 
                upgrade_pause_end_timestamp_utc: Optional[datetime] = ..., 
                upgrade_pause_start_timestamp_utc: Optional[datetime] = ..., 
                upgrade_wave: Optional[Union[str, ClusterUpgradeCadence]] = ..., 
                vmss_zonal_upgrade_mode: Optional[Union[str, VmssZonalUpgradeMode]] = ..., 
                wave_upgrade_paused: Optional[bool] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterUpgradeCadence(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAVE0 = "Wave0"
        WAVE1 = "Wave1"
        WAVE2 = "Wave2"


    class azure.mgmt.servicefabric.models.ClusterUpgradeDeltaHealthPolicy(Model):
        application_delta_health_policies: dict[str, ApplicationDeltaHealthPolicy]
        max_percent_delta_unhealthy_applications: int
        max_percent_delta_unhealthy_nodes: int
        max_percent_upgrade_domain_delta_unhealthy_nodes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_delta_health_policies: Optional[Dict[str, ApplicationDeltaHealthPolicy]] = ..., 
                max_percent_delta_unhealthy_applications: int, 
                max_percent_delta_unhealthy_nodes: int, 
                max_percent_upgrade_domain_delta_unhealthy_nodes: int, 
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


    class azure.mgmt.servicefabric.models.ClusterUpgradePolicy(Model):
        delta_health_policy: ClusterUpgradeDeltaHealthPolicy
        force_restart: bool
        health_check_retry_timeout: str
        health_check_stable_duration: str
        health_check_wait_duration: str
        health_policy: ClusterHealthPolicy
        upgrade_domain_timeout: str
        upgrade_replica_set_check_timeout: str
        upgrade_timeout: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delta_health_policy: Optional[ClusterUpgradeDeltaHealthPolicy] = ..., 
                force_restart: Optional[bool] = ..., 
                health_check_retry_timeout: str, 
                health_check_stable_duration: str, 
                health_check_wait_duration: str, 
                health_policy: ClusterHealthPolicy, 
                upgrade_domain_timeout: str, 
                upgrade_replica_set_check_timeout: str, 
                upgrade_timeout: str, 
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


    class azure.mgmt.servicefabric.models.ClusterVersionDetails(Model):
        code_version: str
        environment: Union[str, ClusterEnvironment]
        support_expiry_utc: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code_version: Optional[str] = ..., 
                environment: Optional[Union[str, ClusterEnvironment]] = ..., 
                support_expiry_utc: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ClusterVersionsEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.servicefabric.models.DiagnosticsStorageAccountConfig(Model):
        blob_endpoint: str
        protected_account_key_name: str
        protected_account_key_name2: str
        queue_endpoint: str
        storage_account_name: str
        table_endpoint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_endpoint: str, 
                protected_account_key_name: str, 
                protected_account_key_name2: Optional[str] = ..., 
                queue_endpoint: str, 
                storage_account_name: str, 
                table_endpoint: str, 
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


    class azure.mgmt.servicefabric.models.DurabilityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRONZE = "Bronze"
        GOLD = "Gold"
        SILVER = "Silver"


    class azure.mgmt.servicefabric.models.EndpointRangeDescription(Model):
        end_port: int
        start_port: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                end_port: int, 
                start_port: int, 
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


    class azure.mgmt.servicefabric.models.ErrorModel(Model):
        error: ErrorModelError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorModelError] = ..., 
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


    class azure.mgmt.servicefabric.models.ErrorModelError(Model):
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


    class azure.mgmt.servicefabric.models.ManagedIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityType]] = ..., 
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


    class azure.mgmt.servicefabric.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.servicefabric.models.MoveCost(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        ZERO = "Zero"


    class azure.mgmt.servicefabric.models.NamedPartitionSchemeDescription(PartitionSchemeDescription):
        count: int
        names: list[str]
        partition_scheme: Union[str, PartitionScheme]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: int, 
                names: List[str], 
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


    class azure.mgmt.servicefabric.models.NodeTypeDescription(Model):
        application_ports: EndpointRangeDescription
        capacities: dict[str, str]
        client_connection_endpoint_port: int
        durability_level: Union[str, DurabilityLevel]
        ephemeral_ports: EndpointRangeDescription
        http_gateway_endpoint_port: int
        http_gateway_token_auth_endpoint_port: int
        is_primary: bool
        is_stateless: bool
        multiple_availability_zones: bool
        name: str
        placement_properties: dict[str, str]
        reverse_proxy_endpoint_port: int
        vm_instance_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_ports: Optional[EndpointRangeDescription] = ..., 
                capacities: Optional[Dict[str, str]] = ..., 
                client_connection_endpoint_port: int, 
                durability_level: Optional[Union[str, DurabilityLevel]] = ..., 
                ephemeral_ports: Optional[EndpointRangeDescription] = ..., 
                http_gateway_endpoint_port: int, 
                http_gateway_token_auth_endpoint_port: Optional[int] = ..., 
                is_primary: bool, 
                is_stateless: Optional[bool] = ..., 
                multiple_availability_zones: Optional[bool] = ..., 
                name: str, 
                placement_properties: Optional[Dict[str, str]] = ..., 
                reverse_proxy_endpoint_port: Optional[int] = ..., 
                vm_instance_count: int, 
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


    class azure.mgmt.servicefabric.models.Notification(Model):
        is_enabled: bool
        notification_category: Union[str, NotificationCategory]
        notification_level: Union[str, NotificationLevel]
        notification_targets: list[NotificationTarget]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_enabled: bool, 
                notification_category: Union[str, NotificationCategory], 
                notification_level: Union[str, NotificationLevel], 
                notification_targets: List[NotificationTarget], 
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


    class azure.mgmt.servicefabric.models.NotificationCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WAVE_PROGRESS = "WaveProgress"


    class azure.mgmt.servicefabric.models.NotificationChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMAIL_SUBSCRIPTION = "EmailSubscription"
        EMAIL_USER = "EmailUser"


    class azure.mgmt.servicefabric.models.NotificationLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CRITICAL = "Critical"


    class azure.mgmt.servicefabric.models.NotificationTarget(Model):
        notification_channel: Union[str, NotificationChannel]
        receivers: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                notification_channel: Union[str, NotificationChannel], 
                receivers: List[str], 
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


    class azure.mgmt.servicefabric.models.OperationListResult(Model):
        next_link: str
        value: list[OperationResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[OperationResult]] = ..., 
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


    class azure.mgmt.servicefabric.models.OperationResult(Model):
        display: AvailableOperationDisplay
        is_data_action: bool
        name: str
        next_link: str
        origin: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[AvailableOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                next_link: Optional[str] = ..., 
                origin: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.PartitionScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        NAMED = "Named"
        SINGLETON = "Singleton"
        UNIFORM_INT64_RANGE = "UniformInt64Range"


    class azure.mgmt.servicefabric.models.PartitionSchemeDescription(Model):
        partition_scheme: Union[str, PartitionScheme]

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


    class azure.mgmt.servicefabric.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.servicefabric.models.ProxyResource(Model):
        etag: str
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


    class azure.mgmt.servicefabric.models.ReliabilityLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BRONZE = "Bronze"
        GOLD = "Gold"
        NONE = "None"
        PLATINUM = "Platinum"
        SILVER = "Silver"


    class azure.mgmt.servicefabric.models.Resource(Model):
        etag: str
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


    class azure.mgmt.servicefabric.models.RollingUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        MONITORED = "Monitored"
        UNMONITORED_AUTO = "UnmonitoredAuto"
        UNMONITORED_MANUAL = "UnmonitoredManual"


    class azure.mgmt.servicefabric.models.ServerCertificateCommonName(Model):
        certificate_common_name: str
        certificate_issuer_thumbprint: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_common_name: str, 
                certificate_issuer_thumbprint: str, 
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


    class azure.mgmt.servicefabric.models.ServerCertificateCommonNames(Model):
        common_names: list[ServerCertificateCommonName]
        x509_store_name: Union[str, StoreName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                common_names: Optional[List[ServerCertificateCommonName]] = ..., 
                x509_store_name: Optional[Union[str, StoreName]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceCorrelationDescription(Model):
        scheme: Union[str, ServiceCorrelationScheme]
        service_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scheme: Union[str, ServiceCorrelationScheme], 
                service_name: str, 
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


    class azure.mgmt.servicefabric.models.ServiceCorrelationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFFINITY = "Affinity"
        ALIGNED_AFFINITY = "AlignedAffinity"
        INVALID = "Invalid"
        NON_ALIGNED_AFFINITY = "NonAlignedAffinity"


    class azure.mgmt.servicefabric.models.ServiceKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        STATEFUL = "Stateful"
        STATELESS = "Stateless"


    class azure.mgmt.servicefabric.models.ServiceLoadMetricDescription(Model):
        default_load: int
        name: str
        primary_default_load: int
        secondary_default_load: int
        weight: Union[str, ServiceLoadMetricWeight]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_load: Optional[int] = ..., 
                name: str, 
                primary_default_load: Optional[int] = ..., 
                secondary_default_load: Optional[int] = ..., 
                weight: Optional[Union[str, ServiceLoadMetricWeight]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceLoadMetricWeight(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"
        ZERO = "Zero"


    class azure.mgmt.servicefabric.models.ServicePlacementPolicyDescription(Model):
        type: Union[str, ServicePlacementPolicyType]

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


    class azure.mgmt.servicefabric.models.ServicePlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        INVALID_DOMAIN = "InvalidDomain"
        NON_PARTIALLY_PLACE_SERVICE = "NonPartiallyPlaceService"
        PREFERRED_PRIMARY_DOMAIN = "PreferredPrimaryDomain"
        REQUIRED_DOMAIN = "RequiredDomain"
        REQUIRED_DOMAIN_DISTRIBUTION = "RequiredDomainDistribution"


    class azure.mgmt.servicefabric.models.ServiceResource(ProxyResource):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        etag: str
        id: str
        location: str
        name: str
        partition_description: PartitionSchemeDescription
        placement_constraints: str
        provisioning_state: str
        service_dns_name: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_package_activation_mode: Union[str, ArmServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        service_type_name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                location: Optional[str] = ..., 
                partition_description: Optional[PartitionSchemeDescription] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_package_activation_mode: Optional[Union[str, ArmServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
                service_type_name: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceResourceList(Model):
        next_link: str
        value: list[ServiceResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ServiceResource]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceResourceProperties(ServiceResourcePropertiesBase):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        partition_description: PartitionSchemeDescription
        placement_constraints: str
        provisioning_state: str
        service_dns_name: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_package_activation_mode: Union[str, ArmServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        service_type_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                partition_description: Optional[PartitionSchemeDescription] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_package_activation_mode: Optional[Union[str, ArmServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
                service_type_name: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceResourcePropertiesBase(Model):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        placement_constraints: str
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_placement_policies: list[ServicePlacementPolicyDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceResourceUpdate(ProxyResource):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        etag: str
        id: str
        location: str
        name: str
        placement_constraints: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                location: Optional[str] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceResourceUpdateProperties(ServiceResourcePropertiesBase):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        placement_constraints: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_placement_policies: list[ServicePlacementPolicyDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
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


    class azure.mgmt.servicefabric.models.ServiceTypeDeltaHealthPolicy(Model):
        max_percent_delta_unhealthy_services: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_percent_delta_unhealthy_services: int = 0, 
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


    class azure.mgmt.servicefabric.models.ServiceTypeHealthPolicy(Model):
        max_percent_unhealthy_services: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_percent_unhealthy_services: int = 0, 
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


    class azure.mgmt.servicefabric.models.SettingsParameterDescription(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                value: str, 
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


    class azure.mgmt.servicefabric.models.SettingsSectionDescription(Model):
        name: str
        parameters: list[SettingsParameterDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                parameters: List[SettingsParameterDescription], 
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


    class azure.mgmt.servicefabric.models.SfZonalUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIERARCHICAL = "Hierarchical"
        PARALLEL = "Parallel"


    class azure.mgmt.servicefabric.models.SingletonPartitionSchemeDescription(PartitionSchemeDescription):
        partition_scheme: Union[str, PartitionScheme]

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


    class azure.mgmt.servicefabric.models.StatefulServiceProperties(ServiceResourceProperties):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        has_persisted_state: bool
        min_replica_set_size: int
        partition_description: PartitionSchemeDescription
        placement_constraints: str
        provisioning_state: str
        quorum_loss_wait_duration: datetime
        replica_restart_wait_duration: datetime
        service_dns_name: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_package_activation_mode: Union[str, ArmServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        service_type_name: str
        stand_by_replica_keep_duration: datetime
        target_replica_set_size: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                has_persisted_state: Optional[bool] = ..., 
                min_replica_set_size: Optional[int] = ..., 
                partition_description: Optional[PartitionSchemeDescription] = ..., 
                placement_constraints: Optional[str] = ..., 
                quorum_loss_wait_duration: Optional[datetime] = ..., 
                replica_restart_wait_duration: Optional[datetime] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_package_activation_mode: Optional[Union[str, ArmServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
                service_type_name: Optional[str] = ..., 
                stand_by_replica_keep_duration: Optional[datetime] = ..., 
                target_replica_set_size: Optional[int] = ..., 
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


    class azure.mgmt.servicefabric.models.StatefulServiceUpdateProperties(ServiceResourceUpdateProperties):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        min_replica_set_size: int
        placement_constraints: str
        quorum_loss_wait_duration: datetime
        replica_restart_wait_duration: datetime
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        stand_by_replica_keep_duration: datetime
        target_replica_set_size: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                min_replica_set_size: Optional[int] = ..., 
                placement_constraints: Optional[str] = ..., 
                quorum_loss_wait_duration: Optional[datetime] = ..., 
                replica_restart_wait_duration: Optional[datetime] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
                stand_by_replica_keep_duration: Optional[datetime] = ..., 
                target_replica_set_size: Optional[int] = ..., 
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


    class azure.mgmt.servicefabric.models.StatelessServiceProperties(ServiceResourceProperties):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        instance_close_delay_duration: str
        instance_count: int
        min_instance_count: int
        min_instance_percentage: bytes
        partition_description: PartitionSchemeDescription
        placement_constraints: str
        provisioning_state: str
        service_dns_name: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_package_activation_mode: Union[str, ArmServicePackageActivationMode]
        service_placement_policies: list[ServicePlacementPolicyDescription]
        service_type_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                instance_close_delay_duration: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                min_instance_count: Optional[int] = ..., 
                min_instance_percentage: Optional[bytes] = ..., 
                partition_description: Optional[PartitionSchemeDescription] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_dns_name: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_package_activation_mode: Optional[Union[str, ArmServicePackageActivationMode]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
                service_type_name: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.StatelessServiceUpdateProperties(ServiceResourceUpdateProperties):
        correlation_scheme: list[ServiceCorrelationDescription]
        default_move_cost: Union[str, MoveCost]
        instance_close_delay_duration: str
        instance_count: int
        placement_constraints: str
        service_kind: Union[str, ServiceKind]
        service_load_metrics: list[ServiceLoadMetricDescription]
        service_placement_policies: list[ServicePlacementPolicyDescription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                correlation_scheme: Optional[List[ServiceCorrelationDescription]] = ..., 
                default_move_cost: Optional[Union[str, MoveCost]] = ..., 
                instance_close_delay_duration: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                placement_constraints: Optional[str] = ..., 
                service_load_metrics: Optional[List[ServiceLoadMetricDescription]] = ..., 
                service_placement_policies: Optional[List[ServicePlacementPolicyDescription]] = ..., 
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


    class azure.mgmt.servicefabric.models.StoreName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDRESS_BOOK = "AddressBook"
        AUTH_ROOT = "AuthRoot"
        CERTIFICATE_AUTHORITY = "CertificateAuthority"
        DISALLOWED = "Disallowed"
        MY = "My"
        ROOT = "Root"
        TRUSTED_PEOPLE = "TrustedPeople"
        TRUSTED_PUBLISHER = "TrustedPublisher"


    class azure.mgmt.servicefabric.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: str
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[str] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[str] = ..., 
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


    class azure.mgmt.servicefabric.models.UniformInt64RangePartitionSchemeDescription(PartitionSchemeDescription):
        count: int
        high_key: str
        low_key: str
        partition_scheme: Union[str, PartitionScheme]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                count: int, 
                high_key: str, 
                low_key: str, 
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


    class azure.mgmt.servicefabric.models.UpgradableVersionPathResult(Model):
        supported_path: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                supported_path: Optional[List[str]] = ..., 
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


    class azure.mgmt.servicefabric.models.UpgradableVersionsDescription(Model):
        target_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_version: str, 
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


    class azure.mgmt.servicefabric.models.UpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"


    class azure.mgmt.servicefabric.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.servicefabric.models.VMSize(Model):
        size: str

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


    class azure.mgmt.servicefabric.models.VMSizeResource(Model):
        id: str
        name: str
        properties: VMSize
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


    class azure.mgmt.servicefabric.models.VMSizesResult(Model):
        next_link: str
        value: list[VMSizeResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[VMSizeResource]] = ..., 
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


    class azure.mgmt.servicefabric.models.VmssZonalUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIERARCHICAL = "Hierarchical"
        PARALLEL = "Parallel"


namespace azure.mgmt.servicefabric.operations

    class azure.mgmt.servicefabric.operations.ApplicationTypeVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: ApplicationTypeVersionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationTypeVersionResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationTypeVersionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationTypeVersionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ApplicationTypeVersionResource]: ...


    class azure.mgmt.servicefabric.operations.ApplicationTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: ApplicationTypeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_type_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationTypeResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ApplicationTypeResource]: ...


    class azure.mgmt.servicefabric.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: ApplicationResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ApplicationResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ApplicationResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ApplicationResource]: ...


    class azure.mgmt.servicefabric.operations.ClusterVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                cluster_version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace
        def get_by_environment(
                self, 
                location: str, 
                environment: Union[str, ClusterVersionsEnvironment], 
                cluster_version: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...

        @distributed_trace
        def list_by_environment(
                self, 
                location: str, 
                environment: Union[str, ClusterVersionsEnvironment], 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ClusterCodeVersionsListResult: ...


    class azure.mgmt.servicefabric.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Cluster]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[Cluster]: ...

        @overload
        def list_upgradable_versions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                versions_description: Optional[UpgradableVersionsDescription] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpgradableVersionPathResult: ...

        @overload
        def list_upgradable_versions(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                versions_description: Optional[IO] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> UpgradableVersionPathResult: ...


    class azure.mgmt.servicefabric.operations.Operations:

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
            ) -> Iterable[OperationResult]: ...


    class azure.mgmt.servicefabric.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: ServiceResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                service_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> ServiceResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                application_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[ServiceResource]: ...


    class azure.mgmt.servicefabric.operations.UnsupportedVmSizesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                vm_size: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> VMSizeResource: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[VMSizeResource]: ...


```