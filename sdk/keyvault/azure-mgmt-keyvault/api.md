```py
namespace azure.mgmt.keyvault

    class azure.mgmt.keyvault.KeyVaultManagementClient: implements ContextManager 
        keys: KeysOperations
        managed_hsm_keys: ManagedHsmKeysOperations
        managed_hsms: ManagedHsmsOperations
        mhsm_private_endpoint_connections: MHSMPrivateEndpointConnectionsOperations
        mhsm_private_link_resources: MHSMPrivateLinkResourcesOperations
        mhsm_regions: MHSMRegionsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        secrets: SecretsOperations
        vaults: VaultsOperations

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


namespace azure.mgmt.keyvault.aio

    class azure.mgmt.keyvault.aio.KeyVaultManagementClient: implements AsyncContextManager 
        keys: KeysOperations
        managed_hsm_keys: ManagedHsmKeysOperations
        managed_hsms: ManagedHsmsOperations
        mhsm_private_endpoint_connections: MHSMPrivateEndpointConnectionsOperations
        mhsm_private_link_resources: MHSMPrivateLinkResourcesOperations
        mhsm_regions: MHSMRegionsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        secrets: SecretsOperations
        vaults: VaultsOperations

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


namespace azure.mgmt.keyvault.aio.operations

    class azure.mgmt.keyvault.aio.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: KeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: KeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace_async
        async def get_version(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                key_version: str, 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Key]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Key]: ...


    class azure.mgmt.keyvault.aio.operations.MHSMPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[MHSMPrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MHSMPrivateEndpointConnection]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: MHSMPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: MHSMPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...


    class azure.mgmt.keyvault.aio.operations.MHSMPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_mhsm_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> MHSMPrivateLinkResourceListResult: ...


    class azure.mgmt.keyvault.aio.operations.MHSMRegionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MHSMGeoReplicatedRegion]: ...


    class azure.mgmt.keyvault.aio.operations.ManagedHsmKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: ManagedHsmKeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: ManagedHsmKeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @overload
        async def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace_async
        async def get_version(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                key_version: str, 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedHsmKey]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedHsmKey]: ...


    class azure.mgmt.keyvault.aio.operations.ManagedHsmsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_purge_deleted(
                self, 
                name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedHsm]: ...

        @overload
        async def check_mhsm_name_availability(
                self, 
                mhsm_name: CheckMhsmNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @overload
        async def check_mhsm_name_availability(
                self, 
                mhsm_name: CheckMhsmNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @overload
        async def check_mhsm_name_availability(
                self, 
                mhsm_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Optional[ManagedHsm]: ...

        @distributed_trace_async
        async def get_deleted(
                self, 
                name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedManagedHsm: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedHsm]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedHsm]: ...

        @distributed_trace
        def list_deleted(self, **kwargs: Any) -> AsyncItemPaged[DeletedManagedHsm]: ...


    class azure.mgmt.keyvault.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.keyvault.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> Optional[PrivateEndpointConnection]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.keyvault.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_vault(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.keyvault.aio.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Secret]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...


    class azure.mgmt.keyvault.aio.operations.VaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Vault]: ...

        @distributed_trace_async
        async def begin_purge_deleted(
                self, 
                vault_name: str, 
                location: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def check_name_availability(
                self, 
                vault_name: VaultCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                vault_name: VaultCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                vault_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> Vault: ...

        @distributed_trace_async
        async def get_deleted(
                self, 
                vault_name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[TrackedResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Vault]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Vault]: ...

        @distributed_trace
        def list_deleted(self, **kwargs: Any) -> AsyncItemPaged[DeletedVault]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        async def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: VaultAccessPolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...

        @overload
        async def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: VaultAccessPolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...

        @overload
        async def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...


namespace azure.mgmt.keyvault.models

    class azure.mgmt.keyvault.models.AccessPolicyEntry(_Model):
        application_id: Optional[str]
        object_id: str
        permissions: Permissions
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                object_id: str, 
                permissions: Permissions, 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.AccessPolicyUpdateKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD = "add"
        REMOVE = "remove"
        REPLACE = "replace"


    class azure.mgmt.keyvault.models.Action(_Model):
        type: Optional[Union[str, KeyRotationPolicyActionType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, KeyRotationPolicyActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ActionsRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"


    class azure.mgmt.keyvault.models.ActivationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        FAILED = "Failed"
        NOT_ACTIVATED = "NotActivated"
        UNKNOWN = "Unknown"


    class azure.mgmt.keyvault.models.Attributes(_Model):
        created: Optional[datetime]
        enabled: Optional[bool]
        expires: Optional[datetime]
        not_before: Optional[datetime]
        updated: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expires: Optional[datetime] = ..., 
                not_before: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.CertificatePermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        BACKUP = "backup"
        CREATE = "create"
        DELETE = "delete"
        DELETEISSUERS = "deleteissuers"
        GET = "get"
        GETISSUERS = "getissuers"
        IMPORT = "import"
        LIST = "list"
        LISTISSUERS = "listissuers"
        MANAGECONTACTS = "managecontacts"
        MANAGEISSUERS = "manageissuers"
        PURGE = "purge"
        RECOVER = "recover"
        RESTORE = "restore"
        SETISSUERS = "setissuers"
        UPDATE = "update"


    class azure.mgmt.keyvault.models.CheckMhsmNameAvailabilityParameters(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.CheckMhsmNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]


    class azure.mgmt.keyvault.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]


    class azure.mgmt.keyvault.models.CloudError(_Model):
        error: Optional[CloudErrorBody]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[CloudErrorBody] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.CloudErrorBody(_Model):
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


    class azure.mgmt.keyvault.models.CreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "default"
        RECOVER = "recover"


    class azure.mgmt.keyvault.models.DeletedManagedHsm(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedManagedHsmProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedManagedHsmProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.DeletedManagedHsmProperties(_Model):
        deletion_date: Optional[datetime]
        location: Optional[str]
        mhsm_id: Optional[str]
        purge_protection_enabled: Optional[bool]
        scheduled_purge_date: Optional[datetime]
        tags: Optional[dict[str, str]]


    class azure.mgmt.keyvault.models.DeletedVault(ProxyResource):
        id: str
        name: str
        properties: Optional[DeletedVaultProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeletedVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.DeletedVaultProperties(_Model):
        deletion_date: Optional[datetime]
        location: Optional[str]
        purge_protection_enabled: Optional[bool]
        scheduled_purge_date: Optional[datetime]
        tags: Optional[dict[str, str]]
        vault_id: Optional[str]


    class azure.mgmt.keyvault.models.DeletionRecoveryLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PURGEABLE = "Purgeable"
        RECOVERABLE = "Recoverable"
        RECOVERABLE_PROTECTED_SUBSCRIPTION = "Recoverable+ProtectedSubscription"
        RECOVERABLE_PURGEABLE = "Recoverable+Purgeable"


    class azure.mgmt.keyvault.models.DimensionProperties(_Model):
        display_name: Optional[str]
        name: Optional[str]
        to_be_exported_for_shoebox: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                to_be_exported_for_shoebox: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.Error(_Model):
        code: Optional[str]
        inner_error: Optional[Error]
        message: Optional[str]


    class azure.mgmt.keyvault.models.GeoReplicationRegionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLEANUP = "Cleanup"
        DELETING = "Deleting"
        FAILED = "Failed"
        PREPROVISIONING = "Preprovisioning"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.keyvault.models.IPRule(_Model):
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.keyvault.models.JsonWebKeyCurveName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P256 = "P-256"
        P256_K = "P-256K"
        P384 = "P-384"
        P521 = "P-521"


    class azure.mgmt.keyvault.models.JsonWebKeyOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DECRYPT = "decrypt"
        ENCRYPT = "encrypt"
        IMPORT = "import"
        RELEASE = "release"
        SIGN = "sign"
        UNWRAP_KEY = "unwrapKey"
        VERIFY = "verify"
        WRAP_KEY = "wrapKey"


    class azure.mgmt.keyvault.models.JsonWebKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EC = "EC"
        EC_HSM = "EC-HSM"
        OCT_HSM = "oct-HSM"
        RSA = "RSA"
        RSA_HSM = "RSA-HSM"


    class azure.mgmt.keyvault.models.Key(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: KeyProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: KeyProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.KeyAttributes(_Model):
        created: Optional[int]
        enabled: Optional[bool]
        expires: Optional[int]
        exportable: Optional[bool]
        not_before: Optional[int]
        recovery_level: Optional[Union[str, DeletionRecoveryLevel]]
        updated: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expires: Optional[int] = ..., 
                exportable: Optional[bool] = ..., 
                not_before: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.KeyCreateParameters(_Model):
        properties: KeyProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: KeyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.KeyPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        BACKUP = "backup"
        CREATE = "create"
        DECRYPT = "decrypt"
        DELETE = "delete"
        ENCRYPT = "encrypt"
        GET = "get"
        GETROTATIONPOLICY = "getrotationpolicy"
        IMPORT = "import"
        LIST = "list"
        PURGE = "purge"
        RECOVER = "recover"
        RELEASE = "release"
        RESTORE = "restore"
        ROTATE = "rotate"
        SETROTATIONPOLICY = "setrotationpolicy"
        SIGN = "sign"
        UNWRAP_KEY = "unwrapKey"
        UPDATE = "update"
        VERIFY = "verify"
        WRAP_KEY = "wrapKey"


    class azure.mgmt.keyvault.models.KeyProperties(_Model):
        attributes: Optional[KeyAttributes]
        curve_name: Optional[Union[str, JsonWebKeyCurveName]]
        key_ops: Optional[list[Union[str, JsonWebKeyOperation]]]
        key_size: Optional[int]
        key_uri: Optional[str]
        key_uri_with_version: Optional[str]
        kty: Optional[Union[str, JsonWebKeyType]]
        release_policy: Optional[KeyReleasePolicy]
        rotation_policy: Optional[RotationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[KeyAttributes] = ..., 
                curve_name: Optional[Union[str, JsonWebKeyCurveName]] = ..., 
                key_ops: Optional[list[Union[str, JsonWebKeyOperation]]] = ..., 
                key_size: Optional[int] = ..., 
                kty: Optional[Union[str, JsonWebKeyType]] = ..., 
                release_policy: Optional[KeyReleasePolicy] = ..., 
                rotation_policy: Optional[RotationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.KeyReleasePolicy(_Model):
        content_type: Optional[str]
        data: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                data: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.KeyRotationPolicyActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOTIFY = "notify"
        ROTATE = "rotate"


    class azure.mgmt.keyvault.models.KeyRotationPolicyAttributes(_Model):
        created: Optional[int]
        expiry_time: Optional[str]
        updated: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.LifetimeAction(_Model):
        action: Optional[Action]
        trigger: Optional[Trigger]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Action] = ..., 
                trigger: Optional[Trigger] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.LogSpecification(_Model):
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


    class azure.mgmt.keyvault.models.MHSMGeoReplicatedRegion(_Model):
        is_primary: Optional[bool]
        name: Optional[str]
        provisioning_state: Optional[Union[str, GeoReplicationRegionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                is_primary: Optional[bool] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMIPRule(_Model):
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMNetworkRuleSet(_Model):
        bypass: Optional[Union[str, NetworkRuleBypassOptions]]
        default_action: Optional[Union[str, NetworkRuleAction]]
        ip_rules: Optional[list[MHSMIPRule]]
        service_tags: Optional[list[MHSMServiceTagRule]]
        virtual_network_rules: Optional[list[MHSMVirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                bypass: Optional[Union[str, NetworkRuleBypassOptions]] = ..., 
                default_action: Optional[Union[str, NetworkRuleAction]] = ..., 
                ip_rules: Optional[list[MHSMIPRule]] = ..., 
                service_tags: Optional[list[MHSMServiceTagRule]] = ..., 
                virtual_network_rules: Optional[list[MHSMVirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.keyvault.models.MHSMPrivateEndpointConnection(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[MHSMPrivateEndpointConnectionProperties]
        sku: Optional[ManagedHsmSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[MHSMPrivateEndpointConnectionProperties] = ..., 
                sku: Optional[ManagedHsmSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateEndpointConnectionItem(_Model):
        etag: Optional[str]
        id: Optional[str]
        properties: Optional[MHSMPrivateEndpointConnectionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                id: Optional[str] = ..., 
                properties: Optional[MHSMPrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[MHSMPrivateEndpoint]
        private_link_service_connection_state: Optional[MHSMPrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[MHSMPrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[MHSMPrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateLinkResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[MHSMPrivateLinkResourceProperties]
        sku: Optional[ManagedHsmSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[MHSMPrivateLinkResourceProperties] = ..., 
                sku: Optional[ManagedHsmSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateLinkResourceListResult(_Model):
        value: Optional[list[MHSMPrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[MHSMPrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMPrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.keyvault.models.MHSMPrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[Union[str, ActionsRequired]]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[Union[str, ActionsRequired]] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMServiceTagRule(_Model):
        tag: str

        @overload
        def __init__(
                self, 
                *, 
                tag: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.MHSMVirtualNetworkRule(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHSMSecurityDomainProperties(_Model):
        activation_status: Optional[Union[str, ActivationStatus]]
        activation_status_message: Optional[str]


    class azure.mgmt.keyvault.models.ManagedHsm(ProxyResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: Optional[str]
        name: str
        properties: Optional[ManagedHsmProperties]
        sku: Optional[ManagedHsmSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ManagedHsmProperties] = ..., 
                sku: Optional[ManagedHsmSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmAction(_Model):
        type: Optional[Union[str, KeyRotationPolicyActionType]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, KeyRotationPolicyActionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmError(_Model):
        error: Optional[Error]


    class azure.mgmt.keyvault.models.ManagedHsmKey(ProxyResource):
        id: str
        name: str
        properties: ManagedHsmKeyProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: ManagedHsmKeyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmKeyAttributes(_Model):
        created: Optional[int]
        enabled: Optional[bool]
        expires: Optional[int]
        exportable: Optional[bool]
        not_before: Optional[int]
        recovery_level: Optional[Union[str, DeletionRecoveryLevel]]
        updated: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expires: Optional[int] = ..., 
                exportable: Optional[bool] = ..., 
                not_before: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmKeyCreateParameters(_Model):
        properties: ManagedHsmKeyProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: ManagedHsmKeyProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmKeyProperties(_Model):
        attributes: Optional[ManagedHsmKeyAttributes]
        curve_name: Optional[Union[str, JsonWebKeyCurveName]]
        key_ops: Optional[list[Union[str, JsonWebKeyOperation]]]
        key_size: Optional[int]
        key_uri: Optional[str]
        key_uri_with_version: Optional[str]
        kty: Optional[Union[str, JsonWebKeyType]]
        release_policy: Optional[ManagedHsmKeyReleasePolicy]
        rotation_policy: Optional[ManagedHsmRotationPolicy]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[ManagedHsmKeyAttributes] = ..., 
                curve_name: Optional[Union[str, JsonWebKeyCurveName]] = ..., 
                key_ops: Optional[list[Union[str, JsonWebKeyOperation]]] = ..., 
                key_size: Optional[int] = ..., 
                kty: Optional[Union[str, JsonWebKeyType]] = ..., 
                release_policy: Optional[ManagedHsmKeyReleasePolicy] = ..., 
                rotation_policy: Optional[ManagedHsmRotationPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmKeyReleasePolicy(_Model):
        content_type: Optional[str]
        data: Optional[bytes]

        @overload
        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                data: Optional[bytes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmKeyRotationPolicyAttributes(_Model):
        created: Optional[int]
        expiry_time: Optional[str]
        updated: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                expiry_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmLifetimeAction(_Model):
        action: Optional[ManagedHsmAction]
        trigger: Optional[ManagedHsmTrigger]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[ManagedHsmAction] = ..., 
                trigger: Optional[ManagedHsmTrigger] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmProperties(_Model):
        create_mode: Optional[Union[str, CreateMode]]
        enable_purge_protection: Optional[bool]
        enable_soft_delete: Optional[bool]
        hsm_uri: Optional[str]
        initial_admin_object_ids: Optional[list[str]]
        network_acls: Optional[MHSMNetworkRuleSet]
        private_endpoint_connections: Optional[list[MHSMPrivateEndpointConnectionItem]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        regions: Optional[list[MHSMGeoReplicatedRegion]]
        scheduled_purge_date: Optional[datetime]
        security_domain_properties: Optional[ManagedHSMSecurityDomainProperties]
        soft_delete_retention_in_days: Optional[int]
        status_message: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                enable_purge_protection: Optional[bool] = ..., 
                enable_soft_delete: Optional[bool] = ..., 
                initial_admin_object_ids: Optional[list[str]] = ..., 
                network_acls: Optional[MHSMNetworkRuleSet] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                regions: Optional[list[MHSMGeoReplicatedRegion]] = ..., 
                soft_delete_retention_in_days: Optional[int] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmRotationPolicy(_Model):
        attributes: Optional[ManagedHsmKeyRotationPolicyAttributes]
        lifetime_actions: Optional[list[ManagedHsmLifetimeAction]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[ManagedHsmKeyRotationPolicyAttributes] = ..., 
                lifetime_actions: Optional[list[ManagedHsmLifetimeAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmSku(_Model):
        family: Union[str, ManagedHsmSkuFamily]
        name: Union[str, ManagedHsmSkuNameV2]

        @overload
        def __init__(
                self, 
                *, 
                family: Union[str, ManagedHsmSkuFamily], 
                name: Union[str, ManagedHsmSkuNameV2]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedHsmSkuFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        B = "B"
        C = "C"


    class azure.mgmt.keyvault.models.ManagedHsmSkuNameV2(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_B32 = "Custom_B32"
        CUSTOM_B6 = "Custom_B6"
        CUSTOM_C10 = "Custom_C10"
        CUSTOM_C42 = "Custom_C42"
        STANDARD_B1 = "Standard_B1"


    class azure.mgmt.keyvault.models.ManagedHsmTrigger(_Model):
        time_after_create: Optional[str]
        time_before_expiry: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                time_after_create: Optional[str] = ..., 
                time_before_expiry: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.keyvault.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.keyvault.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        dimensions: Optional[list[DimensionProperties]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        internal_metric_name: Optional[str]
        lock_aggregation_type: Optional[str]
        name: Optional[str]
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
                fill_gap_with_zero: Optional[bool] = ..., 
                internal_metric_name: Optional[str] = ..., 
                lock_aggregation_type: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_aggregation_types: Optional[list[str]] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.NetworkRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.keyvault.models.NetworkRuleBypassOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.keyvault.models.NetworkRuleSet(_Model):
        bypass: Optional[Union[str, NetworkRuleBypassOptions]]
        default_action: Optional[Union[str, NetworkRuleAction]]
        ip_rules: Optional[list[IPRule]]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                bypass: Optional[Union[str, NetworkRuleBypassOptions]] = ..., 
                default_action: Optional[Union[str, NetworkRuleAction]] = ..., 
                ip_rules: Optional[list[IPRule]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        operation_properties: Optional[OperationProperties]
        origin: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                operation_properties: Optional[OperationProperties] = ..., 
                origin: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.OperationDisplay(_Model):
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


    class azure.mgmt.keyvault.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.Permissions(_Model):
        certificates: Optional[list[Union[str, CertificatePermissions]]]
        keys_property: Optional[list[Union[str, KeyPermissions]]]
        secrets: Optional[list[Union[str, SecretPermissions]]]
        storage: Optional[list[Union[str, StoragePermissions]]]

        @overload
        def __init__(
                self, 
                *, 
                certificates: Optional[list[Union[str, CertificatePermissions]]] = ..., 
                keys_property: Optional[list[Union[str, KeyPermissions]]] = ..., 
                secrets: Optional[list[Union[str, SecretPermissions]]] = ..., 
                storage: Optional[list[Union[str, StoragePermissions]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.keyvault.models.PrivateEndpointConnection(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.PrivateEndpointConnectionItem(_Model):
        etag: Optional[str]
        id: Optional[str]
        properties: Optional[PrivateEndpointConnectionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                id: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.keyvault.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState]
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        DISCONNECTED = "Disconnected"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.keyvault.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.keyvault.models.PrivateLinkResource(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
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


    class azure.mgmt.keyvault.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.keyvault.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[Union[str, ActionsRequired]]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[Union[str, ActionsRequired]] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATED = "Activated"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        RESTORING = "Restoring"
        SECURITY_DOMAIN_RESTORE = "SecurityDomainRestore"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.keyvault.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.keyvault.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.keyvault.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_NAME_INVALID = "AccountNameInvalid"
        ALREADY_EXISTS = "AlreadyExists"


    class azure.mgmt.keyvault.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.keyvault.models.RotationPolicy(_Model):
        attributes: Optional[KeyRotationPolicyAttributes]
        lifetime_actions: Optional[list[LifetimeAction]]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[KeyRotationPolicyAttributes] = ..., 
                lifetime_actions: Optional[list[LifetimeAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.Secret(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: SecretProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: SecretProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SecretAttributes(Attributes):
        created: datetime
        enabled: bool
        expires: datetime
        not_before: datetime
        updated: datetime

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expires: Optional[datetime] = ..., 
                not_before: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SecretCreateOrUpdateParameters(_Model):
        properties: SecretProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: SecretProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SecretPatchParameters(_Model):
        properties: Optional[SecretPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecretPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SecretPatchProperties(_Model):
        attributes: Optional[SecretAttributes]
        content_type: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[SecretAttributes] = ..., 
                content_type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SecretPermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        BACKUP = "backup"
        DELETE = "delete"
        GET = "get"
        LIST = "list"
        PURGE = "purge"
        RECOVER = "recover"
        RESTORE = "restore"
        SET = "set"


    class azure.mgmt.keyvault.models.SecretProperties(_Model):
        attributes: Optional[SecretAttributes]
        content_type: Optional[str]
        secret_uri: Optional[str]
        secret_uri_with_version: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[SecretAttributes] = ..., 
                content_type: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.Sku(_Model):
        family: Union[str, SkuFamily]
        name: Union[str, SkuName]

        @overload
        def __init__(
                self, 
                *, 
                family: Union[str, SkuFamily], 
                name: Union[str, SkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.SkuFamily(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A = "A"


    class azure.mgmt.keyvault.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "premium"
        STANDARD = "standard"


    class azure.mgmt.keyvault.models.StoragePermissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "all"
        BACKUP = "backup"
        DELETE = "delete"
        DELETESAS = "deletesas"
        GET = "get"
        GETSAS = "getsas"
        LIST = "list"
        LISTSAS = "listsas"
        PURGE = "purge"
        RECOVER = "recover"
        REGENERATEKEY = "regeneratekey"
        RESTORE = "restore"
        SET = "set"
        SETSAS = "setsas"
        UPDATE = "update"


    class azure.mgmt.keyvault.models.SystemData(_Model):
        created_at: Optional[datetime]
        created_by: Optional[str]
        created_by_type: Optional[Union[str, IdentityType]]
        last_modified_at: Optional[datetime]
        last_modified_by: Optional[str]
        last_modified_by_type: Optional[Union[str, IdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, IdentityType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, IdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.TokenBindingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENFORCED = "Enforced"
        NOT_ENFORCED = "NotEnforced"


    class azure.mgmt.keyvault.models.TokenBindingParameters(_Model):
        minimum_token_binding_strength: Optional[Union[str, TokenBindingStrength]]
        mode: Optional[Union[str, TokenBindingMode]]

        @overload
        def __init__(
                self, 
                *, 
                minimum_token_binding_strength: Optional[Union[str, TokenBindingStrength]] = ..., 
                mode: Optional[Union[str, TokenBindingMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.TokenBindingStrength(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTESTED_CONFIDENTIAL = "AttestedConfidential"
        ATTESTED_TRUSTED_LAUNCH = "AttestedTrustedLaunch"
        NO_VALIDATION = "NoValidation"
        UNATTESTED = "Unattested"


    class azure.mgmt.keyvault.models.TrackedResource(Resource):
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


    class azure.mgmt.keyvault.models.Trigger(_Model):
        time_after_create: Optional[str]
        time_before_expiry: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                time_after_create: Optional[str] = ..., 
                time_before_expiry: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.keyvault.models.Vault(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: VaultProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: VaultProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultAccessPolicyParameters(_Model):
        id: Optional[str]
        location: Optional[str]
        name: Optional[str]
        properties: VaultAccessPolicyProperties
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                properties: VaultAccessPolicyProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultAccessPolicyProperties(_Model):
        access_policies: list[AccessPolicyEntry]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: list[AccessPolicyEntry]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultCheckNameAvailabilityParameters(_Model):
        name: str
        type: Literal["KeyVault/vaults"]

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultCreateOrUpdateParameters(_Model):
        location: str
        properties: VaultProperties
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: VaultProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultPatchParameters(_Model):
        properties: Optional[VaultPatchProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VaultPatchProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultPatchProperties(_Model):
        access_policies: Optional[list[AccessPolicyEntry]]
        create_mode: Optional[Union[str, CreateMode]]
        enable_purge_protection: Optional[bool]
        enable_rbac_authorization: Optional[bool]
        enable_soft_delete: Optional[bool]
        enabled_for_deployment: Optional[bool]
        enabled_for_disk_encryption: Optional[bool]
        enabled_for_template_deployment: Optional[bool]
        network_acls: Optional[NetworkRuleSet]
        public_network_access: Optional[str]
        sku: Optional[Sku]
        soft_delete_retention_in_days: Optional[int]
        tenant_id: Optional[str]
        token_binding_parameters: Optional[TokenBindingParameters]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: Optional[list[AccessPolicyEntry]] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                enable_purge_protection: Optional[bool] = ..., 
                enable_rbac_authorization: Optional[bool] = ..., 
                enable_soft_delete: Optional[bool] = ..., 
                enabled_for_deployment: Optional[bool] = ..., 
                enabled_for_disk_encryption: Optional[bool] = ..., 
                enabled_for_template_deployment: Optional[bool] = ..., 
                network_acls: Optional[NetworkRuleSet] = ..., 
                public_network_access: Optional[str] = ..., 
                sku: Optional[Sku] = ..., 
                soft_delete_retention_in_days: Optional[int] = ..., 
                tenant_id: Optional[str] = ..., 
                token_binding_parameters: Optional[TokenBindingParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultProperties(_Model):
        access_policies: Optional[list[AccessPolicyEntry]]
        create_mode: Optional[Union[str, CreateMode]]
        enable_purge_protection: Optional[bool]
        enable_rbac_authorization: Optional[bool]
        enable_soft_delete: Optional[bool]
        enabled_for_deployment: Optional[bool]
        enabled_for_disk_encryption: Optional[bool]
        enabled_for_template_deployment: Optional[bool]
        hsm_pool_resource_id: Optional[str]
        network_acls: Optional[NetworkRuleSet]
        private_endpoint_connections: Optional[list[PrivateEndpointConnectionItem]]
        provisioning_state: Optional[Union[str, VaultProvisioningState]]
        public_network_access: Optional[str]
        sku: Sku
        soft_delete_retention_in_days: Optional[int]
        tenant_id: str
        token_binding_parameters: Optional[TokenBindingParameters]
        vault_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_policies: Optional[list[AccessPolicyEntry]] = ..., 
                create_mode: Optional[Union[str, CreateMode]] = ..., 
                enable_purge_protection: Optional[bool] = ..., 
                enable_rbac_authorization: Optional[bool] = ..., 
                enable_soft_delete: Optional[bool] = ..., 
                enabled_for_deployment: Optional[bool] = ..., 
                enabled_for_disk_encryption: Optional[bool] = ..., 
                enabled_for_template_deployment: Optional[bool] = ..., 
                network_acls: Optional[NetworkRuleSet] = ..., 
                provisioning_state: Optional[Union[str, VaultProvisioningState]] = ..., 
                public_network_access: Optional[str] = ..., 
                sku: Sku, 
                soft_delete_retention_in_days: Optional[int] = ..., 
                tenant_id: str, 
                token_binding_parameters: Optional[TokenBindingParameters] = ..., 
                vault_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.keyvault.models.VaultProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGISTERING_DNS = "RegisteringDns"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.keyvault.models.VirtualNetworkRule(_Model):
        id: str
        ignore_missing_vnet_service_endpoint: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                ignore_missing_vnet_service_endpoint: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.keyvault.operations

    class azure.mgmt.keyvault.operations.KeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: KeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: KeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def get_version(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                key_version: str, 
                **kwargs: Any
            ) -> Key: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Key]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Key]: ...


    class azure.mgmt.keyvault.operations.MHSMPrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[MHSMPrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[MHSMPrivateEndpointConnection]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: MHSMPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: MHSMPrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MHSMPrivateEndpointConnection: ...


    class azure.mgmt.keyvault.operations.MHSMPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_mhsm_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> MHSMPrivateLinkResourceListResult: ...


    class azure.mgmt.keyvault.operations.MHSMRegionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[MHSMGeoReplicatedRegion]: ...


    class azure.mgmt.keyvault.operations.ManagedHsmKeysOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: ManagedHsmKeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: ManagedHsmKeyCreateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @overload
        def create_if_not_exist(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace
        def get_version(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                key_version: str, 
                **kwargs: Any
            ) -> ManagedHsmKey: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedHsmKey]: ...

        @distributed_trace
        def list_versions(
                self, 
                resource_group_name: str, 
                name: str, 
                key_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedHsmKey]: ...


    class azure.mgmt.keyvault.operations.ManagedHsmsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_purge_deleted(
                self, 
                name: str, 
                location: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: ManagedHsm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedHsm]: ...

        @overload
        def check_mhsm_name_availability(
                self, 
                mhsm_name: CheckMhsmNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @overload
        def check_mhsm_name_availability(
                self, 
                mhsm_name: CheckMhsmNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @overload
        def check_mhsm_name_availability(
                self, 
                mhsm_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckMhsmNameAvailabilityResult: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> Optional[ManagedHsm]: ...

        @distributed_trace
        def get_deleted(
                self, 
                name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedManagedHsm: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ManagedHsm]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ManagedHsm]: ...

        @distributed_trace
        def list_deleted(self, **kwargs: Any) -> ItemPaged[DeletedManagedHsm]: ...


    class azure.mgmt.keyvault.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.keyvault.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> Optional[PrivateEndpointConnection]: ...

        @distributed_trace
        def list_by_resource(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def put(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...


    class azure.mgmt.keyvault.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_vault(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.keyvault.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Secret]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: SecretPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                secret_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Secret: ...


    class azure.mgmt.keyvault.operations.VaultsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultCreateOrUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Vault]: ...

        @distributed_trace
        def begin_purge_deleted(
                self, 
                vault_name: str, 
                location: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def check_name_availability(
                self, 
                vault_name: VaultCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                vault_name: VaultCheckNameAvailabilityParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                vault_name: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                **kwargs: Any
            ) -> Vault: ...

        @distributed_trace
        def get_deleted(
                self, 
                vault_name: str, 
                location: str, 
                **kwargs: Any
            ) -> DeletedVault: ...

        @distributed_trace
        def list(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[TrackedResource]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Vault]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                *, 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Vault]: ...

        @distributed_trace
        def list_deleted(self, **kwargs: Any) -> ItemPaged[DeletedVault]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: VaultPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Vault: ...

        @overload
        def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: VaultAccessPolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...

        @overload
        def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: VaultAccessPolicyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...

        @overload
        def update_access_policy(
                self, 
                resource_group_name: str, 
                vault_name: str, 
                operation_kind: Union[str, AccessPolicyUpdateKind], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> VaultAccessPolicyParameters: ...


namespace azure.mgmt.keyvault.types

    class azure.mgmt.keyvault.types.AccessPolicyEntry(TypedDict, total=False):
        key "applicationId": str
        key "objectId": Required[str]
        key "permissions": Required[Permissions]
        key "tenantId": Required[str]
        application_id: str
        object_id: str
        permissions: Permissions
        tenant_id: str


    class azure.mgmt.keyvault.types.Action(TypedDict, total=False):
        key "type": Union[str, KeyRotationPolicyActionType]
        type: Union[str, KeyRotationPolicyActionType]


    class azure.mgmt.keyvault.types.Attributes(TypedDict, total=False):
        key "created": int
        key "enabled": bool
        key "exp": int
        key "nbf": int
        key "updated": int
        created: int
        enabled: bool
        expires: int
        not_before: int
        updated: int


    class azure.mgmt.keyvault.types.CheckMhsmNameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.keyvault.types.IPRule(TypedDict, total=False):
        key "value": Required[str]
        value: str


    class azure.mgmt.keyvault.types.KeyAttributes(TypedDict, total=False):
        key "created": int
        key "enabled": bool
        key "exp": int
        key "exportable": bool
        key "nbf": int
        key "recoveryLevel": Union[str, DeletionRecoveryLevel]
        key "updated": int
        created: int
        enabled: bool
        expires: int
        exportable: bool
        not_before: int
        recovery_level: Union[str, DeletionRecoveryLevel]
        updated: int


    class azure.mgmt.keyvault.types.KeyCreateParameters(TypedDict, total=False):
        key "properties": Required[KeyProperties]
        properties: KeyProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.KeyProperties(TypedDict, total=False):
        key "attributes": ForwardRef('KeyAttributes', module='types')
        key "curveName": Union[str, JsonWebKeyCurveName]
        key "keySize": int
        key "keyUri": str
        key "keyUriWithVersion": str
        key "kty": Union[str, JsonWebKeyType]
        key "release_policy": ForwardRef('KeyReleasePolicy', module='types')
        key "rotationPolicy": ForwardRef('RotationPolicy', module='types')
        attributes: KeyAttributes
        curve_name: Union[str, JsonWebKeyCurveName]
        keyOps: list[Union[str, JsonWebKeyOperation]]
        key_ops: list[Union[str, JsonWebKeyOperation]]
        key_size: int
        key_uri: str
        key_uri_with_version: str
        kty: Union[str, JsonWebKeyType]
        release_policy: KeyReleasePolicy
        rotation_policy: RotationPolicy


    class azure.mgmt.keyvault.types.KeyReleasePolicy(TypedDict, total=False):
        key "contentType": str
        key "data": str
        content_type: str
        data: str


    class azure.mgmt.keyvault.types.KeyRotationPolicyAttributes(TypedDict, total=False):
        key "created": int
        key "expiryTime": str
        key "updated": int
        created: int
        expiry_time: str
        updated: int


    class azure.mgmt.keyvault.types.LifetimeAction(TypedDict, total=False):
        key "action": ForwardRef('Action', module='types')
        key "trigger": ForwardRef('Trigger', module='types')
        action: Action
        trigger: Trigger


    class azure.mgmt.keyvault.types.MHSMGeoReplicatedRegion(TypedDict, total=False):
        key "isPrimary": bool
        key "name": str
        key "provisioningState": Union[str, GeoReplicationRegionProvisioningState]
        is_primary: bool
        name: str
        provisioning_state: Union[str, GeoReplicationRegionProvisioningState]


    class azure.mgmt.keyvault.types.MHSMIPRule(TypedDict, total=False):
        key "value": Required[str]
        value: str


    class azure.mgmt.keyvault.types.MHSMNetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[str, NetworkRuleBypassOptions]
        key "defaultAction": Union[str, NetworkRuleAction]
        bypass: Union[str, NetworkRuleBypassOptions]
        default_action: Union[str, NetworkRuleAction]
        ipRules: list[MHSMIPRule]
        ip_rules: list[MHSMIPRule]
        serviceTags: list[MHSMServiceTagRule]
        service_tags: list[MHSMServiceTagRule]
        virtualNetworkRules: list[MHSMVirtualNetworkRule]
        virtual_network_rules: list[MHSMVirtualNetworkRule]


    class azure.mgmt.keyvault.types.MHSMPrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.keyvault.types.MHSMPrivateEndpointConnection(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('MHSMPrivateEndpointConnectionProperties', module='types')
        key "sku": ForwardRef('ManagedHsmSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: MHSMPrivateEndpointConnectionProperties
        sku: ManagedHsmSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.keyvault.types.MHSMPrivateEndpointConnectionItem(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "properties": ForwardRef('MHSMPrivateEndpointConnectionProperties', module='types')
        etag: str
        id: str
        properties: MHSMPrivateEndpointConnectionProperties


    class azure.mgmt.keyvault.types.MHSMPrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('MHSMPrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('MHSMPrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        private_endpoint: MHSMPrivateEndpoint
        private_link_service_connection_state: MHSMPrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.keyvault.types.MHSMPrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": Union[str, ActionsRequired]
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: Union[str, ActionsRequired]
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.keyvault.types.MHSMServiceTagRule(TypedDict, total=False):
        key "tag": Required[str]
        tag: str


    class azure.mgmt.keyvault.types.MHSMVirtualNetworkRule(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.keyvault.types.ManagedHSMSecurityDomainProperties(TypedDict, total=False):
        key "activationStatus": Union[str, ActivationStatus]
        key "activationStatusMessage": str
        activation_status: Union[str, ActivationStatus]
        activation_status_message: str


    class azure.mgmt.keyvault.types.ManagedHsm(ProxyResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ManagedHsmProperties', module='types')
        key "sku": ForwardRef('ManagedHsmSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: ManagedHsmProperties
        sku: ManagedHsmSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.keyvault.types.ManagedHsmAction(TypedDict, total=False):
        key "type": Union[str, KeyRotationPolicyActionType]
        type: Union[str, KeyRotationPolicyActionType]


    class azure.mgmt.keyvault.types.ManagedHsmKeyAttributes(TypedDict, total=False):
        key "created": int
        key "enabled": bool
        key "exp": int
        key "exportable": bool
        key "nbf": int
        key "recoveryLevel": Union[str, DeletionRecoveryLevel]
        key "updated": int
        created: int
        enabled: bool
        expires: int
        exportable: bool
        not_before: int
        recovery_level: Union[str, DeletionRecoveryLevel]
        updated: int


    class azure.mgmt.keyvault.types.ManagedHsmKeyCreateParameters(TypedDict, total=False):
        key "properties": Required[ManagedHsmKeyProperties]
        properties: ManagedHsmKeyProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.ManagedHsmKeyProperties(TypedDict, total=False):
        key "attributes": ForwardRef('ManagedHsmKeyAttributes', module='types')
        key "curveName": Union[str, JsonWebKeyCurveName]
        key "keySize": int
        key "keyUri": str
        key "keyUriWithVersion": str
        key "kty": Union[str, JsonWebKeyType]
        key "release_policy": ForwardRef('ManagedHsmKeyReleasePolicy', module='types')
        key "rotationPolicy": ForwardRef('ManagedHsmRotationPolicy', module='types')
        attributes: ManagedHsmKeyAttributes
        curve_name: Union[str, JsonWebKeyCurveName]
        keyOps: list[Union[str, JsonWebKeyOperation]]
        key_ops: list[Union[str, JsonWebKeyOperation]]
        key_size: int
        key_uri: str
        key_uri_with_version: str
        kty: Union[str, JsonWebKeyType]
        release_policy: ManagedHsmKeyReleasePolicy
        rotation_policy: ManagedHsmRotationPolicy


    class azure.mgmt.keyvault.types.ManagedHsmKeyReleasePolicy(TypedDict, total=False):
        key "contentType": str
        key "data": str
        content_type: str
        data: str


    class azure.mgmt.keyvault.types.ManagedHsmKeyRotationPolicyAttributes(TypedDict, total=False):
        key "created": int
        key "expiryTime": str
        key "updated": int
        created: int
        expiry_time: str
        updated: int


    class azure.mgmt.keyvault.types.ManagedHsmLifetimeAction(TypedDict, total=False):
        key "action": ForwardRef('ManagedHsmAction', module='types')
        key "trigger": ForwardRef('ManagedHsmTrigger', module='types')
        action: ManagedHsmAction
        trigger: ManagedHsmTrigger


    class azure.mgmt.keyvault.types.ManagedHsmProperties(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "enablePurgeProtection": bool
        key "enableSoftDelete": bool
        key "hsmUri": str
        key "networkAcls": ForwardRef('MHSMNetworkRuleSet', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "scheduledPurgeDate": str
        key "securityDomainProperties": ForwardRef('ManagedHSMSecurityDomainProperties', module='types')
        key "softDeleteRetentionInDays": int
        key "statusMessage": str
        key "tenantId": str
        create_mode: Union[str, CreateMode]
        enable_purge_protection: bool
        enable_soft_delete: bool
        hsm_uri: str
        initialAdminObjectIds: list[str]
        initial_admin_object_ids: list[str]
        network_acls: MHSMNetworkRuleSet
        privateEndpointConnections: list[MHSMPrivateEndpointConnectionItem]
        private_endpoint_connections: list[MHSMPrivateEndpointConnectionItem]
        provisioning_state: Union[str, ProvisioningState]
        public_network_access: Union[str, PublicNetworkAccess]
        regions: list[MHSMGeoReplicatedRegion]
        scheduled_purge_date: str
        security_domain_properties: ManagedHSMSecurityDomainProperties
        soft_delete_retention_in_days: int
        status_message: str
        tenant_id: str


    class azure.mgmt.keyvault.types.ManagedHsmRotationPolicy(TypedDict, total=False):
        key "attributes": ForwardRef('ManagedHsmKeyRotationPolicyAttributes', module='types')
        attributes: ManagedHsmKeyRotationPolicyAttributes
        lifetimeActions: list[ManagedHsmLifetimeAction]
        lifetime_actions: list[ManagedHsmLifetimeAction]


    class azure.mgmt.keyvault.types.ManagedHsmSku(TypedDict, total=False):
        key "family": Required[Union[str, ManagedHsmSkuFamily]]
        key "name": Required[Union[str, ManagedHsmSkuNameV2]]
        family: Union[str, ManagedHsmSkuFamily]
        name: Union[str, ManagedHsmSkuNameV2]


    class azure.mgmt.keyvault.types.ManagedHsmTrigger(TypedDict, total=False):
        key "timeAfterCreate": str
        key "timeBeforeExpiry": str
        time_after_create: str
        time_before_expiry: str


    class azure.mgmt.keyvault.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.keyvault.types.NetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[str, NetworkRuleBypassOptions]
        key "defaultAction": Union[str, NetworkRuleAction]
        bypass: Union[str, NetworkRuleBypassOptions]
        default_action: Union[str, NetworkRuleAction]
        ipRules: list[IPRule]
        ip_rules: list[IPRule]
        virtualNetworkRules: list[VirtualNetworkRule]
        virtual_network_rules: list[VirtualNetworkRule]


    class azure.mgmt.keyvault.types.Permissions(TypedDict, total=False):
        certificates: list[Union[str, CertificatePermissions]]
        keys: list[Union[str, KeyPermissions]]
        keys_property: list[Union[str, KeyPermissions]]
        secrets: list[Union[str, SecretPermissions]]
        storage: list[Union[str, StoragePermissions]]


    class azure.mgmt.keyvault.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.keyvault.types.PrivateEndpointConnection(ProxyResource):
        key "etag": str
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.keyvault.types.PrivateEndpointConnectionItem(TypedDict, total=False):
        key "etag": str
        key "id": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        etag: str
        id: str
        properties: PrivateEndpointConnectionProperties


    class azure.mgmt.keyvault.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('PrivateLinkServiceConnectionState', module='types')
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.keyvault.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": Union[str, ActionsRequired]
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actions_required: Union[str, ActionsRequired]
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.keyvault.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.keyvault.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.keyvault.types.RotationPolicy(TypedDict, total=False):
        key "attributes": ForwardRef('KeyRotationPolicyAttributes', module='types')
        attributes: KeyRotationPolicyAttributes
        lifetimeActions: list[LifetimeAction]
        lifetime_actions: list[LifetimeAction]


    class azure.mgmt.keyvault.types.SecretAttributes(Attributes):
        key "created": int
        key "enabled": bool
        key "exp": int
        key "nbf": int
        key "updated": int
        created: int
        enabled: bool
        expires: int
        not_before: int
        updated: int


    class azure.mgmt.keyvault.types.SecretCreateOrUpdateParameters(TypedDict, total=False):
        key "properties": Required[SecretProperties]
        properties: SecretProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.SecretPatchParameters(TypedDict, total=False):
        key "properties": ForwardRef('SecretPatchProperties', module='types')
        properties: SecretPatchProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.SecretPatchProperties(TypedDict, total=False):
        key "attributes": ForwardRef('SecretAttributes', module='types')
        key "contentType": str
        key "value": str
        attributes: SecretAttributes
        content_type: str
        value: str


    class azure.mgmt.keyvault.types.SecretProperties(TypedDict, total=False):
        key "attributes": ForwardRef('SecretAttributes', module='types')
        key "contentType": str
        key "secretUri": str
        key "secretUriWithVersion": str
        key "value": str
        attributes: SecretAttributes
        content_type: str
        secret_uri: str
        secret_uri_with_version: str
        value: str


    class azure.mgmt.keyvault.types.Sku(TypedDict, total=False):
        key "family": Required[Union[str, SkuFamily]]
        key "name": Required[Union[str, SkuName]]
        family: Union[str, SkuFamily]
        name: Union[str, SkuName]


    class azure.mgmt.keyvault.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, IdentityType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, IdentityType]
        created_at: str
        created_by: str
        created_by_type: Union[str, IdentityType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, IdentityType]


    class azure.mgmt.keyvault.types.TokenBindingParameters(TypedDict, total=False):
        key "minimumTokenBindingStrength": Union[str, TokenBindingStrength]
        key "mode": Union[str, TokenBindingMode]
        minimum_token_binding_strength: Union[str, TokenBindingStrength]
        mode: Union[str, TokenBindingMode]


    class azure.mgmt.keyvault.types.Trigger(TypedDict, total=False):
        key "timeAfterCreate": str
        key "timeBeforeExpiry": str
        time_after_create: str
        time_before_expiry: str


    class azure.mgmt.keyvault.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.keyvault.types.VaultAccessPolicyParameters(TypedDict, total=False):
        key "id": str
        key "location": str
        key "name": str
        key "properties": Required[VaultAccessPolicyProperties]
        key "type": str
        id: str
        location: str
        name: str
        properties: VaultAccessPolicyProperties
        type: str


    class azure.mgmt.keyvault.types.VaultAccessPolicyProperties(TypedDict, total=False):
        key "accessPolicies": Required[list[AccessPolicyEntry]]
        access_policies: list[AccessPolicyEntry]


    class azure.mgmt.keyvault.types.VaultCheckNameAvailabilityParameters(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Literal["KeyVault/vaults"]]
        name: str
        type: Literal[KeyVault/vaults]


    class azure.mgmt.keyvault.types.VaultCreateOrUpdateParameters(TypedDict, total=False):
        key "location": Required[str]
        key "properties": Required[VaultProperties]
        location: str
        properties: VaultProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.VaultPatchParameters(TypedDict, total=False):
        key "properties": ForwardRef('VaultPatchProperties', module='types')
        properties: VaultPatchProperties
        tags: dict[str, str]


    class azure.mgmt.keyvault.types.VaultPatchProperties(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "enablePurgeProtection": bool
        key "enableRbacAuthorization": bool
        key "enableSoftDelete": bool
        key "enabledForDeployment": bool
        key "enabledForDiskEncryption": bool
        key "enabledForTemplateDeployment": bool
        key "networkAcls": ForwardRef('NetworkRuleSet', module='types')
        key "publicNetworkAccess": str
        key "sku": ForwardRef('Sku', module='types')
        key "softDeleteRetentionInDays": int
        key "tenantId": str
        key "tokenBindingParameters": ForwardRef('TokenBindingParameters', module='types')
        accessPolicies: list[AccessPolicyEntry]
        access_policies: list[AccessPolicyEntry]
        create_mode: Union[str, CreateMode]
        enable_purge_protection: bool
        enable_rbac_authorization: bool
        enable_soft_delete: bool
        enabled_for_deployment: bool
        enabled_for_disk_encryption: bool
        enabled_for_template_deployment: bool
        network_acls: NetworkRuleSet
        public_network_access: str
        sku: Sku
        soft_delete_retention_in_days: int
        tenant_id: str
        token_binding_parameters: TokenBindingParameters


    class azure.mgmt.keyvault.types.VaultProperties(TypedDict, total=False):
        key "createMode": Union[str, CreateMode]
        key "enablePurgeProtection": bool
        key "enableRbacAuthorization": bool
        key "enableSoftDelete": bool
        key "enabledForDeployment": bool
        key "enabledForDiskEncryption": bool
        key "enabledForTemplateDeployment": bool
        key "hsmPoolResourceId": str
        key "networkAcls": ForwardRef('NetworkRuleSet', module='types')
        key "provisioningState": Union[str, VaultProvisioningState]
        key "publicNetworkAccess": str
        key "sku": Required[Sku]
        key "softDeleteRetentionInDays": int
        key "tenantId": Required[str]
        key "tokenBindingParameters": ForwardRef('TokenBindingParameters', module='types')
        key "vaultUri": str
        accessPolicies: list[AccessPolicyEntry]
        access_policies: list[AccessPolicyEntry]
        create_mode: Union[str, CreateMode]
        enable_purge_protection: bool
        enable_rbac_authorization: bool
        enable_soft_delete: bool
        enabled_for_deployment: bool
        enabled_for_disk_encryption: bool
        enabled_for_template_deployment: bool
        hsm_pool_resource_id: str
        network_acls: NetworkRuleSet
        privateEndpointConnections: list[PrivateEndpointConnectionItem]
        private_endpoint_connections: list[PrivateEndpointConnectionItem]
        provisioning_state: Union[str, VaultProvisioningState]
        public_network_access: str
        sku: Sku
        soft_delete_retention_in_days: int
        tenant_id: str
        token_binding_parameters: TokenBindingParameters
        vault_uri: str


    class azure.mgmt.keyvault.types.VirtualNetworkRule(TypedDict, total=False):
        key "id": Required[str]
        key "ignoreMissingVnetServiceEndpoint": bool
        id: str
        ignore_missing_vnet_service_endpoint: bool


```