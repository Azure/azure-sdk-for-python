```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.purview

    class azure.mgmt.purview.PurviewManagementClient: implements ContextManager 
        accounts: AccountsOperations
        default_accounts: DefaultAccountsOperations
        features: FeaturesOperations
        ingestion_private_endpoint_connections: IngestionPrivateEndpointConnectionsOperations
        kafka_configurations: KafkaConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
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


namespace azure.mgmt.purview.aio

    class azure.mgmt.purview.aio.PurviewManagementClient: implements AsyncContextManager 
        accounts: AccountsOperations
        default_accounts: DefaultAccountsOperations
        features: FeaturesOperations
        ingestion_private_endpoint_connections: IngestionPrivateEndpointConnectionsOperations
        kafka_configurations: KafkaConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
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


namespace azure.mgmt.purview.aio.operations

    class azure.mgmt.purview.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: CollectionAdminUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: AccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Account]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Account]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.purview.aio.operations.DefaultAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                *, 
                scope: Optional[str] = ..., 
                scope_tenant_id: str, 
                scope_type: Union[str, ScopeType], 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @distributed_trace_async
        async def remove(
                self, 
                *, 
                scope: Optional[str] = ..., 
                scope_tenant_id: str, 
                scope_type: Union[str, ScopeType], 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def set(
                self, 
                default_account_payload: DefaultAccountPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @overload
        async def set(
                self, 
                default_account_payload: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @overload
        async def set(
                self, 
                default_account_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...


    class azure.mgmt.purview.aio.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: BatchFeatureRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        async def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        async def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        async def subscription_get(
                self, 
                locations: str, 
                feature_request: BatchFeatureRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        async def subscription_get(
                self, 
                locations: str, 
                feature_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        async def subscription_get(
                self, 
                locations: str, 
                feature_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...


    class azure.mgmt.purview.aio.operations.IngestionPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: PrivateEndpointConnectionStatusUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...

        @overload
        async def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...


    class azure.mgmt.purview.aio.operations.KafkaConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: KafkaConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[KafkaConfiguration]: ...


    class azure.mgmt.purview.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.purview.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.purview.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_by_group_id(
                self, 
                resource_group_name: str, 
                account_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.purview.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> UsageList: ...


namespace azure.mgmt.purview.models

    class azure.mgmt.purview.models.AccessKeys(_Model):
        atlas_kafka_primary_endpoint: Optional[str]
        atlas_kafka_secondary_endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                atlas_kafka_primary_endpoint: Optional[str] = ..., 
                atlas_kafka_secondary_endpoint: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.Account(ProxyResource):
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[AccountProperties]
        sku: Optional[AccountSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AccountProperties] = ..., 
                sku: Optional[AccountSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.AccountEndpoints(_Model):
        catalog: Optional[str]
        scan: Optional[str]


    class azure.mgmt.purview.models.AccountMergeInfo(_Model):
        account_location: Optional[str]
        account_name: Optional[str]
        account_resource_group_name: Optional[str]
        account_subscription_id: Optional[str]
        deprovisioned: Optional[bool]
        merge_status: Optional[Union[str, MergeStatus]]
        type_of_account: Optional[Union[str, MergeAccountType]]


    class azure.mgmt.purview.models.AccountProperties(_Model):
        account_status: Optional[AccountPropertiesAccountStatus]
        cloud_connectors: Optional[CloudConnectors]
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_object_id: Optional[str]
        default_domain: Optional[str]
        endpoints: Optional[AccountPropertiesEndpoints]
        friendly_name: Optional[str]
        ingestion_storage: Optional[IngestionStorage]
        managed_event_hub_state: Optional[Union[str, ManagedEventHubState]]
        managed_resource_group_name: Optional[str]
        managed_resources: Optional[AccountPropertiesManagedResources]
        managed_resources_public_network_access: Optional[Union[str, PublicNetworkAccess]]
        merge_info: Optional[AccountMergeInfo]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        tenant_endpoint_state: Optional[Union[str, TenantEndpointState]]

        @overload
        def __init__(
                self, 
                *, 
                cloud_connectors: Optional[CloudConnectors] = ..., 
                ingestion_storage: Optional[IngestionStorage] = ..., 
                managed_event_hub_state: Optional[Union[str, ManagedEventHubState]] = ..., 
                managed_resource_group_name: Optional[str] = ..., 
                managed_resources_public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                merge_info: Optional[AccountMergeInfo] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                tenant_endpoint_state: Optional[Union[str, TenantEndpointState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.AccountPropertiesAccountStatus(AccountStatus):
        account_provisioning_state: Union[str, AccountProvisioningState]
        error_details: AccountStatusErrorDetails


    class azure.mgmt.purview.models.AccountPropertiesEndpoints(AccountEndpoints):
        catalog: str
        scan: str


    class azure.mgmt.purview.models.AccountPropertiesManagedResources(ManagedResources):
        event_hub_namespace: str
        resource_group: str
        storage_account: str


    class azure.mgmt.purview.models.AccountProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        SOFT_DELETED = "SoftDeleted"
        SOFT_DELETING = "SoftDeleting"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.purview.models.AccountSku(_Model):
        capacity: Optional[int]
        name: Optional[Union[str, AccountSkuName]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Optional[Union[str, AccountSkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.AccountSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE = "Free"
        STANDARD = "Standard"


    class azure.mgmt.purview.models.AccountStatus(_Model):
        account_provisioning_state: Optional[Union[str, AccountProvisioningState]]
        error_details: Optional[AccountStatusErrorDetails]


    class azure.mgmt.purview.models.AccountStatusErrorDetails(ErrorModel):
        code: str
        details: list[ErrorModel]
        message: str
        target: str


    class azure.mgmt.purview.models.AccountUpdateParameters(_Model):
        identity: Optional[Identity]
        properties: Optional[AccountProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[AccountProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.BatchFeatureRequest(_Model):
        features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.BatchFeatureStatus(_Model):
        features: Optional[dict[str, bool]]


    class azure.mgmt.purview.models.CheckNameAvailabilityRequest(_Model):
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


    class azure.mgmt.purview.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, Reason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.CloudConnectors(_Model):
        aws_external_id: Optional[str]


    class azure.mgmt.purview.models.CollectionAdminUpdate(_Model):
        object_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                object_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.purview.models.Credentials(_Model):
        identity_id: Optional[str]
        type: Optional[Union[str, KafkaConfigurationIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                identity_id: Optional[str] = ..., 
                type: Optional[Union[str, KafkaConfigurationIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.DefaultAccountPayload(_Model):
        account_name: Optional[str]
        resource_group_name: Optional[str]
        scope: Optional[str]
        scope_tenant_id: Optional[str]
        scope_type: Optional[Union[str, ScopeType]]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                resource_group_name: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                scope_tenant_id: Optional[str] = ..., 
                scope_type: Optional[Union[str, ScopeType]] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.DimensionProperties(_Model):
        display_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_customer: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_customer: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.ErrorModel(_Model):
        code: Optional[str]
        details: Optional[list[ErrorModel]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.purview.models.ErrorResponseModel(_Model):
        error: Optional[ErrorResponseModelError]


    class azure.mgmt.purview.models.ErrorResponseModelError(ErrorModel):
        code: str
        details: list[ErrorModel]
        message: str
        target: str


    class azure.mgmt.purview.models.EventHubType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOOK = "Hook"
        NOTIFICATION = "Notification"


    class azure.mgmt.purview.models.EventStreamingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.purview.models.EventStreamingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        MANAGED = "Managed"
        NONE = "None"


    class azure.mgmt.purview.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.IngestionStorage(_Model):
        id: Optional[str]
        primary_endpoint: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.KafkaConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[KafkaConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[KafkaConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.KafkaConfigurationIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.purview.models.KafkaConfigurationProperties(_Model):
        consumer_group: Optional[str]
        credentials: Optional[Credentials]
        event_hub_partition_id: Optional[str]
        event_hub_resource_id: Optional[str]
        event_hub_type: Optional[Union[str, EventHubType]]
        event_streaming_state: Optional[Union[str, EventStreamingState]]
        event_streaming_type: Optional[Union[str, EventStreamingType]]

        @overload
        def __init__(
                self, 
                *, 
                consumer_group: Optional[str] = ..., 
                credentials: Optional[Credentials] = ..., 
                event_hub_partition_id: Optional[str] = ..., 
                event_hub_resource_id: Optional[str] = ..., 
                event_hub_type: Optional[Union[str, EventHubType]] = ..., 
                event_streaming_state: Optional[Union[str, EventStreamingState]] = ..., 
                event_streaming_type: Optional[Union[str, EventStreamingType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.ManagedEventHubState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.purview.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.purview.models.ManagedResources(_Model):
        event_hub_namespace: Optional[str]
        resource_group: Optional[str]
        storage_account: Optional[str]


    class azure.mgmt.purview.models.MergeAccountType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.purview.models.MergeStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.purview.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[OperationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.OperationDisplay(_Model):
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


    class azure.mgmt.purview.models.OperationMetaLogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.OperationMetaMetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[DimensionProperties]]
        display_description: Optional[str]
        display_name: Optional[str]
        enable_regional_mdm_account: Optional[str]
        internal_metric_name: Optional[str]
        name: Optional[str]
        resource_id_dimension_name_override: Optional[str]
        source_mdm_namespace: Optional[str]
        supported_aggregation_types: Optional[list[str]]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                dimensions: Optional[list[DimensionProperties]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                enable_regional_mdm_account: Optional[str] = ..., 
                internal_metric_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                resource_id_dimension_name_override: Optional[str] = ..., 
                source_mdm_namespace: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.OperationMetaServiceSpecification(_Model):
        log_specifications: Optional[list[OperationMetaLogSpecification]]
        metric_specifications: Optional[list[OperationMetaMetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[OperationMetaLogSpecification]] = ..., 
                metric_specifications: Optional[list[OperationMetaMetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.OperationProperties(_Model):
        service_specification: Optional[OperationMetaServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[OperationMetaServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.PrivateEndpointConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        UNKNOWN = "Unknown"


    class azure.mgmt.purview.models.PrivateEndpointConnectionStatusUpdateRequest(_Model):
        private_endpoint_id: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint_id: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.PrivateEndpointConnectionStatusUpdateResponse(_Model):
        private_endpoint_id: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint_id: Optional[str] = ..., 
                status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.purview.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.purview.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        SOFT_DELETED = "SoftDeleted"
        SOFT_DELETING = "SoftDeleting"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.purview.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.purview.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.purview.models.QuotaName(_Model):
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


    class azure.mgmt.purview.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.purview.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.purview.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUBSCRIPTION = "Subscription"
        TENANT = "Tenant"


    class azure.mgmt.purview.models.SystemData(_Model):
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


    class azure.mgmt.purview.models.TenantEndpointState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.purview.models.Usage(_Model):
        current_value: Optional[int]
        id: Optional[str]
        limit: Optional[int]
        name: Optional[UsageName]
        unit: Optional[str]


    class azure.mgmt.purview.models.UsageList(_Model):
        next_link: Optional[str]
        value: list[Usage]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Usage]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.UsageName(QuotaName):
        localized_value: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.purview.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.purview.operations

    class azure.mgmt.purview.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: CollectionAdminUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def add_root_collection_admin(
                self, 
                resource_group_name: str, 
                account_name: str, 
                collection_admin_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: AccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Account]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Account]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.purview.operations.DefaultAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                *, 
                scope: Optional[str] = ..., 
                scope_tenant_id: str, 
                scope_type: Union[str, ScopeType], 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @distributed_trace
        def remove(
                self, 
                *, 
                scope: Optional[str] = ..., 
                scope_tenant_id: str, 
                scope_type: Union[str, ScopeType], 
                **kwargs: Any
            ) -> None: ...

        @overload
        def set(
                self, 
                default_account_payload: DefaultAccountPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @overload
        def set(
                self, 
                default_account_payload: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...

        @overload
        def set(
                self, 
                default_account_payload: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultAccountPayload: ...


    class azure.mgmt.purview.operations.FeaturesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: BatchFeatureRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        def account_get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                feature_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        def subscription_get(
                self, 
                locations: str, 
                feature_request: BatchFeatureRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        def subscription_get(
                self, 
                locations: str, 
                feature_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...

        @overload
        def subscription_get(
                self, 
                locations: str, 
                feature_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> BatchFeatureStatus: ...


    class azure.mgmt.purview.operations.IngestionPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: PrivateEndpointConnectionStatusUpdateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...

        @overload
        def update_status(
                self, 
                resource_group_name: str, 
                account_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionStatusUpdateResponse: ...


    class azure.mgmt.purview.operations.KafkaConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: KafkaConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                kafka_configuration: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                kafka_configuration_name: str, 
                **kwargs: Any
            ) -> KafkaConfiguration: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[KafkaConfiguration]: ...


    class azure.mgmt.purview.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.purview.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.purview.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_by_group_id(
                self, 
                resource_group_name: str, 
                account_name: str, 
                group_id: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


    class azure.mgmt.purview.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> UsageList: ...


```