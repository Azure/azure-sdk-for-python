```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.networkfunction

    class azure.mgmt.networkfunction.TrafficCollectorMgmtClient: implements ContextManager 
        azure_traffic_collectors: AzureTrafficCollectorsOperations
        azure_traffic_collectors_by_resource_group: AzureTrafficCollectorsByResourceGroupOperations
        azure_traffic_collectors_by_subscription: AzureTrafficCollectorsBySubscriptionOperations
        collector_policies: CollectorPoliciesOperations
        network_function: NetworkFunctionOperations

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


namespace azure.mgmt.networkfunction.aio

    class azure.mgmt.networkfunction.aio.TrafficCollectorMgmtClient: implements AsyncContextManager 
        azure_traffic_collectors: AzureTrafficCollectorsOperations
        azure_traffic_collectors_by_resource_group: AzureTrafficCollectorsByResourceGroupOperations
        azure_traffic_collectors_by_subscription: AzureTrafficCollectorsBySubscriptionOperations
        collector_policies: CollectorPoliciesOperations
        network_function: NetworkFunctionOperations

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


namespace azure.mgmt.networkfunction.aio.operations

    class azure.mgmt.networkfunction.aio.operations.AzureTrafficCollectorsByResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureTrafficCollector]: ...


    class azure.mgmt.networkfunction.aio.operations.AzureTrafficCollectorsBySubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[AzureTrafficCollector]: ...


    class azure.mgmt.networkfunction.aio.operations.AzureTrafficCollectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: AzureTrafficCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureTrafficCollector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureTrafficCollector]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureTrafficCollector]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...


    class azure.mgmt.networkfunction.aio.operations.CollectorPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: CollectorPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CollectorPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CollectorPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CollectorPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CollectorPolicy]: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @overload
        async def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...


    class azure.mgmt.networkfunction.aio.operations.NetworkFunctionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.networkfunction.models

    class azure.mgmt.networkfunction.models.AzureTrafficCollector(ProxyResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[AzureTrafficCollectorPropertiesFormat]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AzureTrafficCollectorPropertiesFormat] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkfunction.models.AzureTrafficCollectorPropertiesFormat(_Model):
        collector_policies: Optional[list[ResourceReference]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        virtual_hub: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                virtual_hub: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.CloudErrorBody(_Model):
        code: Optional[str]
        details: Optional[list[CloudErrorBody]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[list[CloudErrorBody]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.CollectorPolicy(ProxyResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[CollectorPolicyPropertiesFormat]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CollectorPolicyPropertiesFormat] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.networkfunction.models.CollectorPolicyPropertiesFormat(_Model):
        emission_policies: Optional[list[EmissionPoliciesPropertiesFormat]]
        ingestion_policy: Optional[IngestionPolicyPropertiesFormat]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                emission_policies: Optional[list[EmissionPoliciesPropertiesFormat]] = ..., 
                ingestion_policy: Optional[IngestionPolicyPropertiesFormat] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.networkfunction.models.DestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_MONITOR = "AzureMonitor"


    class azure.mgmt.networkfunction.models.EmissionPoliciesPropertiesFormat(_Model):
        emission_destinations: Optional[list[EmissionPolicyDestination]]
        emission_type: Optional[Union[str, EmissionType]]

        @overload
        def __init__(
                self, 
                *, 
                emission_destinations: Optional[list[EmissionPolicyDestination]] = ..., 
                emission_type: Optional[Union[str, EmissionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.EmissionPolicyDestination(_Model):
        destination_type: Optional[Union[str, DestinationType]]

        @overload
        def __init__(
                self, 
                *, 
                destination_type: Optional[Union[str, DestinationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.EmissionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IPFIX = "IPFIX"


    class azure.mgmt.networkfunction.models.IngestionPolicyPropertiesFormat(_Model):
        ingestion_sources: Optional[list[IngestionSourcesPropertiesFormat]]
        ingestion_type: Optional[Union[str, IngestionType]]

        @overload
        def __init__(
                self, 
                *, 
                ingestion_sources: Optional[list[IngestionSourcesPropertiesFormat]] = ..., 
                ingestion_type: Optional[Union[str, IngestionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.IngestionSourcesPropertiesFormat(_Model):
        resource_id: Optional[str]
        source_type: Optional[Union[str, SourceType]]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                source_type: Optional[Union[str, SourceType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.IngestionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IPFIX = "IPFIX"


    class azure.mgmt.networkfunction.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.networkfunction.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.networkfunction.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.networkfunction.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.networkfunction.models.ResourceReference(_Model):
        id: Optional[str]


    class azure.mgmt.networkfunction.models.SourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCE = "Resource"


    class azure.mgmt.networkfunction.models.SystemData(_Model):
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


    class azure.mgmt.networkfunction.models.TagsObject(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.networkfunction.operations

    class azure.mgmt.networkfunction.operations.AzureTrafficCollectorsByResourceGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureTrafficCollector]: ...


    class azure.mgmt.networkfunction.operations.AzureTrafficCollectorsBySubscriptionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[AzureTrafficCollector]: ...


    class azure.mgmt.networkfunction.operations.AzureTrafficCollectorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: AzureTrafficCollector, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureTrafficCollector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureTrafficCollector]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureTrafficCollector]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AzureTrafficCollector: ...


    class azure.mgmt.networkfunction.operations.CollectorPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: CollectorPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CollectorPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CollectorPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CollectorPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CollectorPolicy]: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: TagsObject, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...

        @overload
        def update_tags(
                self, 
                resource_group_name: str, 
                azure_traffic_collector_name: str, 
                collector_policy_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CollectorPolicy: ...


    class azure.mgmt.networkfunction.operations.NetworkFunctionOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```