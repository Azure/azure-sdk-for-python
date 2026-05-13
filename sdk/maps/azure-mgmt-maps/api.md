```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.maps

    class azure.mgmt.maps.AzureMapsManagementClient: implements ContextManager 
        accounts: AccountsOperations
        creators: CreatorsOperations
        maps: MapsOperations
        operation_result: OperationResultOperations
        operation_status: OperationStatusOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.maps.aio

    class azure.mgmt.maps.aio.AzureMapsManagementClient: implements AsyncContextManager 
        accounts: AccountsOperations
        creators: CreatorsOperations
        maps: MapsOperations
        operation_result: OperationResultOperations
        operation_status: OperationStatusOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.maps.aio.operations

    class azure.mgmt.maps.aio.operations.AccountsOperations:

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
                maps_account: MapsAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MapsAccount: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MapsAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[MapsAccount]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        async def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        async def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        async def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: MapsKeySpecification, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: MapsAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...


    class azure.mgmt.maps.aio.operations.CreatorsOperations:

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
                creator_name: str, 
                creator_resource: Creator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                **kwargs: Any
            ) -> Creator: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Creator]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: CreatorUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...


    class azure.mgmt.maps.aio.operations.MapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.maps.aio.operations.OperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.maps.aio.operations.OperationStatusOperations:

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
            ) -> OperationStatusResult: ...


    class azure.mgmt.maps.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
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
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.maps.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.maps.models

    class azure.mgmt.maps.models.AccountSasParameters(_Model):
        expiry: str
        max_rate_per_second: int
        principal_id: str
        regions: Optional[list[str]]
        signing_key: Union[str, SigningKey]
        start: str

        @overload
        def __init__(
                self, 
                *, 
                expiry: str, 
                max_rate_per_second: int, 
                principal_id: str, 
                regions: Optional[list[str]] = ..., 
                signing_key: Union[str, SigningKey], 
                start: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.maps.models.CorsRule(_Model):
        allowed_origins: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_origins: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.CorsRules(_Model):
        cors_rules: Optional[list[CorsRule]]

        @overload
        def __init__(
                self, 
                *, 
                cors_rules: Optional[list[CorsRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.maps.models.Creator(TrackedResource):
        id: str
        location: str
        name: str
        properties: CreatorProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: CreatorProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.CreatorProperties(_Model):
        consumed_storage_unit_size_in_bytes: Optional[int]
        provisioning_state: Optional[str]
        storage_units: int
        total_storage_unit_size_in_bytes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                consumed_storage_unit_size_in_bytes: Optional[int] = ..., 
                storage_units: int, 
                total_storage_unit_size_in_bytes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.CreatorUpdateParameters(_Model):
        properties: Optional[CreatorProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreatorProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maps.models.CustomerManagedKeyEncryption(_Model):
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


    class azure.mgmt.maps.models.CustomerManagedKeyEncryptionKeyIdentity(_Model):
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


    class azure.mgmt.maps.models.Encryption(_Model):
        customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption]
        infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption] = ..., 
                infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.maps.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.maps.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELEGATED_RESOURCE_IDENTITY = "delegatedResourceIdentity"
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.maps.models.InfrastructureEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.maps.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "primary"
        SECONDARY = "secondary"


    class azure.mgmt.maps.models.Kind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GEN2 = "Gen2"


    class azure.mgmt.maps.models.LinkedResource(_Model):
        id: str
        unique_name: str

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                unique_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.LocationsItem(_Model):
        location_name: str

        @overload
        def __init__(
                self, 
                *, 
                location_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.maps.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.maps.models.MapsAccount(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[Union[str, Kind]]
        location: str
        name: str
        properties: Optional[MapsAccountProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                location: str, 
                properties: Optional[MapsAccountProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.MapsAccountKeys(_Model):
        primary_key: Optional[str]
        primary_key_last_updated: Optional[str]
        secondary_key: Optional[str]
        secondary_key_last_updated: Optional[str]


    class azure.mgmt.maps.models.MapsAccountProperties(_Model):
        cors: Optional[CorsRules]
        disable_local_auth: Optional[bool]
        encryption: Optional[Encryption]
        linked_resources: Optional[list[LinkedResource]]
        locations: Optional[list[LocationsItem]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        unique_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cors: Optional[CorsRules] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                linked_resources: Optional[list[LinkedResource]] = ..., 
                locations: Optional[list[LocationsItem]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.MapsAccountSasToken(_Model):
        account_sas_token: Optional[str]


    class azure.mgmt.maps.models.MapsAccountUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[Union[str, Kind]]
        properties: Optional[MapsAccountProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                kind: Optional[Union[str, Kind]] = ..., 
                properties: Optional[MapsAccountProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.maps.models.MapsKeySpecification(_Model):
        key_type: Union[str, KeyType]

        @overload
        def __init__(
                self, 
                *, 
                key_type: Union[str, KeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.Name(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        G2 = "G2"


    class azure.mgmt.maps.models.Operation(_Model):
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


    class azure.mgmt.maps.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.maps.models.OperationStatusResult(_Model):
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


    class azure.mgmt.maps.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.maps.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.maps.models.PrivateEndpointConnection(Resource):
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


    class azure.mgmt.maps.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.maps.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.maps.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.maps.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.maps.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.maps.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.maps.models.SigningKey(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_IDENTITY = "managedIdentity"
        PRIMARY_KEY = "primaryKey"
        SECONDARY_KEY = "secondaryKey"


    class azure.mgmt.maps.models.Sku(_Model):
        name: Union[str, Name]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, Name]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.maps.models.SystemData(_Model):
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


    class azure.mgmt.maps.models.TrackedResource(Resource):
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


    class azure.mgmt.maps.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.maps.operations

    class azure.mgmt.maps.operations.AccountsOperations:

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
                maps_account: MapsAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MapsAccount: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MapsAccount]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[MapsAccount]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: AccountSasParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        def list_sas(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_sas_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountSasToken: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: MapsKeySpecification, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                key_specification: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccountKeys: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: MapsAccountUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                maps_account_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MapsAccount: ...


    class azure.mgmt.maps.operations.CreatorsOperations:

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
                creator_name: str, 
                creator_resource: Creator, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                **kwargs: Any
            ) -> Creator: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Creator]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: CreatorUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                creator_name: str, 
                creator_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Creator: ...


    class azure.mgmt.maps.operations.MapsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.maps.operations.OperationResultOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.maps.operations.OperationStatusOperations:

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
            ) -> OperationStatusResult: ...


    class azure.mgmt.maps.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
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
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.maps.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_account(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


```