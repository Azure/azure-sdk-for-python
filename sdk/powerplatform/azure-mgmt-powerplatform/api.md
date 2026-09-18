```py
namespace azure.mgmt.powerplatform

    class azure.mgmt.powerplatform.PowerPlatformMgmtClient: implements ContextManager 
        accounts: AccountsOperations
        enterprise_policies: EnterprisePoliciesOperations
        operations: Operations
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


namespace azure.mgmt.powerplatform.aio

    class azure.mgmt.powerplatform.aio.PowerPlatformMgmtClient: implements AsyncContextManager 
        accounts: AccountsOperations
        enterprise_policies: EnterprisePoliciesOperations
        operations: Operations
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


namespace azure.mgmt.powerplatform.aio.operations

    class azure.mgmt.powerplatform.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        async def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        async def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace_async
        async def delete(
                self, 
                account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Account]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Account]: ...

        @overload
        async def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: PatchAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        async def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        async def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...


    class azure.mgmt.powerplatform.aio.operations.EnterprisePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: EnterprisePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        async def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        async def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnterprisePolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EnterprisePolicy]: ...

        @overload
        async def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: PatchEnterprisePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        async def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        async def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...


    class azure.mgmt.powerplatform.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.powerplatform.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_enterprise_policy(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.powerplatform.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_enterprise_policy(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.powerplatform.models

    class azure.mgmt.powerplatform.models.Account(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
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


    class azure.mgmt.powerplatform.models.AccountProperties(_Model):
        description: Optional[str]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.powerplatform.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.powerplatform.models.EnterprisePolicy(TrackedResource):
        id: str
        identity: Optional[EnterprisePolicyIdentity]
        kind: Union[str, EnterprisePolicyKind]
        location: str
        name: str
        properties: Optional[Properties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EnterprisePolicyIdentity] = ..., 
                kind: Union[str, EnterprisePolicyKind], 
                location: str, 
                properties: Optional[Properties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerplatform.models.EnterprisePolicyIdentity(_Model):
        system_assigned_identity_principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.EnterprisePolicyKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTION = "Encryption"
        IDENTITY = "Identity"
        LOCKBOX = "Lockbox"
        NETWORK_INJECTION = "NetworkInjection"
        PRIVATE_ENDPOINT = "PrivateEndpoint"


    class azure.mgmt.powerplatform.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.powerplatform.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.powerplatform.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        UNDETERMINED = "Undetermined"
        UNHEALTHY = "Unhealthy"
        WARNING = "Warning"


    class azure.mgmt.powerplatform.models.KeyProperties(_Model):
        name: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.KeyVaultProperties(_Model):
        id: Optional[str]
        key: Optional[KeyProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                key: Optional[KeyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.Operation(_Model):
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


    class azure.mgmt.powerplatform.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.powerplatform.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.powerplatform.models.PatchAccount(PatchTrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AccountProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.powerplatform.models.PatchEnterprisePolicy(PatchTrackedResource):
        id: str
        identity: Optional[EnterprisePolicyIdentity]
        kind: Optional[Union[str, EnterprisePolicyKind]]
        location: str
        name: str
        properties: Optional[Properties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[EnterprisePolicyIdentity] = ..., 
                kind: Optional[Union[str, EnterprisePolicyKind]] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[Properties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.powerplatform.models.PatchTrackedResource(Resource):
        id: str
        location: Optional[str]
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.powerplatform.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.powerplatform.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.powerplatform.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.powerplatform.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.powerplatform.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.powerplatform.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.powerplatform.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.powerplatform.models.Properties(_Model):
        encryption: Optional[PropertiesEncryption]
        health_status: Optional[Union[str, HealthStatus]]
        lockbox: Optional[PropertiesLockbox]
        network_injection: Optional[PropertiesNetworkInjection]
        system_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[PropertiesEncryption] = ..., 
                health_status: Optional[Union[str, HealthStatus]] = ..., 
                lockbox: Optional[PropertiesLockbox] = ..., 
                network_injection: Optional[PropertiesNetworkInjection] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.PropertiesEncryption(_Model):
        key_vault: Optional[KeyVaultProperties]
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault: Optional[KeyVaultProperties] = ..., 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.PropertiesLockbox(_Model):
        state: Optional[Union[str, State]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, State]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.PropertiesNetworkInjection(_Model):
        virtual_networks: Optional[list[VirtualNetworkProperties]]

        @overload
        def __init__(
                self, 
                *, 
                virtual_networks: Optional[list[VirtualNetworkProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.powerplatform.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.powerplatform.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.powerplatform.models.State(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_CONFIGURED = "NotConfigured"


    class azure.mgmt.powerplatform.models.SubnetProperties(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.powerplatform.models.SystemData(_Model):
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


    class azure.mgmt.powerplatform.models.TrackedResource(Resource):
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


    class azure.mgmt.powerplatform.models.VirtualNetworkProperties(_Model):
        id: Optional[str]
        subnet: Optional[SubnetProperties]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                subnet: Optional[SubnetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.powerplatform.operations

    class azure.mgmt.powerplatform.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        def create_or_update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def delete(
                self, 
                account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                account_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Account]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Account]: ...

        @overload
        def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: PatchAccount, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...

        @overload
        def update(
                self, 
                account_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Account: ...


    class azure.mgmt.powerplatform.operations.EnterprisePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: EnterprisePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        def create_or_update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnterprisePolicy]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EnterprisePolicy]: ...

        @overload
        def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: PatchEnterprisePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...

        @overload
        def update(
                self, 
                enterprise_policy_name: str, 
                resource_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterprisePolicy: ...


    class azure.mgmt.powerplatform.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.powerplatform.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list_by_enterprise_policy(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.powerplatform.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list_by_enterprise_policy(
                self, 
                resource_group_name: str, 
                enterprise_policy_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


```