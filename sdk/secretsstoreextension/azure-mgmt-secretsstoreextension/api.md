```py
namespace azure.mgmt.secretsstoreextension

    class azure.mgmt.secretsstoreextension.SecretsStoreExtensionMgmtClient: implements ContextManager 
        azure_key_vault_secret_provider_classes: AzureKeyVaultSecretProviderClassesOperations
        operations: Operations
        secret_syncs: SecretSyncsOperations

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


namespace azure.mgmt.secretsstoreextension.aio

    class azure.mgmt.secretsstoreextension.aio.SecretsStoreExtensionMgmtClient: implements AsyncContextManager 
        azure_key_vault_secret_provider_classes: AzureKeyVaultSecretProviderClassesOperations
        operations: Operations
        secret_syncs: SecretSyncsOperations

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


namespace azure.mgmt.secretsstoreextension.aio.operations

    class azure.mgmt.secretsstoreextension.aio.operations.AzureKeyVaultSecretProviderClassesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: AzureKeyVaultSecretProviderClass, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: AzureKeyVaultSecretProviderClass, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: AzureKeyVaultSecretProviderClassUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: AzureKeyVaultSecretProviderClassUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                **kwargs: Any
            ) -> AzureKeyVaultSecretProviderClass: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AzureKeyVaultSecretProviderClass]: ...


    class azure.mgmt.secretsstoreextension.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.secretsstoreextension.aio.operations.SecretSyncsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: SecretSync, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: SecretSync, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: SecretSyncUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: SecretSyncUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecretSync]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                **kwargs: Any
            ) -> SecretSync: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SecretSync]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SecretSync]: ...


namespace azure.mgmt.secretsstoreextension.models

    class azure.mgmt.secretsstoreextension.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.secretsstoreextension.models.AzureCloudName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_CHINA_CLOUD = "AzureChinaCloud"
        AZURE_GERMAN_CLOUD = "AzureGermanCloud"
        AZURE_PUBLIC_CLOUD = "AzurePublicCloud"
        AZURE_STACK_CLOUD = "AzureStackCloud"
        AZURE_US_GOVERNMENT_CLOUD = "AzureUSGovernmentCloud"


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClass(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[AzureKeyVaultSecretProviderClassProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[AzureKeyVaultSecretProviderClassProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassProperties(_Model):
        client_id: str
        cloud_name: Optional[Union[str, AzureCloudName]]
        keyvault_name: str
        objects: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                cloud_name: Optional[Union[str, AzureCloudName]] = ..., 
                keyvault_name: str, 
                objects: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassUpdate(_Model):
        properties: Optional[AzureKeyVaultSecretProviderClassUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureKeyVaultSecretProviderClassUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassUpdateProperties(_Model):
        client_id: Optional[str]
        cloud_name: Optional[Union[str, AzureCloudName]]
        keyvault_name: Optional[str]
        objects: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                cloud_name: Optional[Union[str, AzureCloudName]] = ..., 
                keyvault_name: Optional[str] = ..., 
                objects: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.secretsstoreextension.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.secretsstoreextension.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.secretsstoreextension.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.ExtendedLocation(_Model):
        name: str
        type: Union[str, ExtendedLocationType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ExtendedLocationType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_LOCATION = "CustomLocation"
        EDGE_ZONE = "EdgeZone"


    class azure.mgmt.secretsstoreextension.models.KubernetesSecretObjectMapping(_Model):
        source_path: str
        target_key: str

        @overload
        def __init__(
                self, 
                *, 
                source_path: str, 
                target_key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.KubernetesSecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPAQUE = "Opaque"
        TLS = "kubernetes.io/tls"


    class azure.mgmt.secretsstoreextension.models.Operation(_Model):
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


    class azure.mgmt.secretsstoreextension.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.secretsstoreextension.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.secretsstoreextension.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.secretsstoreextension.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.secretsstoreextension.models.SecretSync(TrackedResource):
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[SecretSyncProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[SecretSyncProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.SecretSyncCondition(_Model):
        last_transition_time: Optional[datetime]
        message: str
        observed_generation: Optional[int]
        reason: str
        status: Union[str, StatusConditionType]
        type: str


    class azure.mgmt.secretsstoreextension.models.SecretSyncProperties(_Model):
        force_synchronization: Optional[str]
        kubernetes_secret_type: Union[str, KubernetesSecretType]
        object_secret_mapping: list[KubernetesSecretObjectMapping]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        secret_provider_class_name: str
        service_account_name: str
        status: Optional[SecretSyncStatus]

        @overload
        def __init__(
                self, 
                *, 
                force_synchronization: Optional[str] = ..., 
                kubernetes_secret_type: Union[str, KubernetesSecretType], 
                object_secret_mapping: list[KubernetesSecretObjectMapping], 
                secret_provider_class_name: str, 
                service_account_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.SecretSyncStatus(_Model):
        conditions: Optional[list[SecretSyncCondition]]
        last_successful_sync_time: Optional[datetime]


    class azure.mgmt.secretsstoreextension.models.SecretSyncUpdate(_Model):
        properties: Optional[SecretSyncUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecretSyncUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.SecretSyncUpdateProperties(_Model):
        force_synchronization: Optional[str]
        object_secret_mapping: Optional[list[KubernetesSecretObjectMapping]]
        secret_provider_class_name: Optional[str]
        service_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                force_synchronization: Optional[str] = ..., 
                object_secret_mapping: Optional[list[KubernetesSecretObjectMapping]] = ..., 
                secret_provider_class_name: Optional[str] = ..., 
                service_account_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.StatusConditionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "False"
        TRUE = "True"
        UNKNOWN = "Unknown"


    class azure.mgmt.secretsstoreextension.models.SystemData(_Model):
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


    class azure.mgmt.secretsstoreextension.models.TrackedResource(Resource):
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


namespace azure.mgmt.secretsstoreextension.operations

    class azure.mgmt.secretsstoreextension.operations.AzureKeyVaultSecretProviderClassesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: AzureKeyVaultSecretProviderClass, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: AzureKeyVaultSecretProviderClass, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: AzureKeyVaultSecretProviderClassUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: AzureKeyVaultSecretProviderClassUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                azure_key_vault_secret_provider_class_name: str, 
                **kwargs: Any
            ) -> AzureKeyVaultSecretProviderClass: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AzureKeyVaultSecretProviderClass]: ...


    class azure.mgmt.secretsstoreextension.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.secretsstoreextension.operations.SecretSyncsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: SecretSync, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: SecretSync, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: SecretSyncUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: SecretSyncUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecretSync]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                secret_sync_name: str, 
                **kwargs: Any
            ) -> SecretSync: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SecretSync]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SecretSync]: ...


namespace azure.mgmt.secretsstoreextension.types

    class azure.mgmt.secretsstoreextension.types.AzureKeyVaultSecretProviderClass(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AzureKeyVaultSecretProviderClassProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: AzureKeyVaultSecretProviderClassProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.secretsstoreextension.types.AzureKeyVaultSecretProviderClassProperties(TypedDict, total=False):
        key "clientId": Required[str]
        key "cloudName": Union[str, AzureCloudName]
        key "keyvaultName": Required[str]
        key "objects": str
        key "provisioningState": Union[str, ProvisioningState]
        key "tenantId": Required[str]
        clientId: str
        cloudName: Union[str, AzureCloudName]
        keyvaultName: str
        objects: str
        provisioningState: Union[str, ProvisioningState]
        tenantId: str


    class azure.mgmt.secretsstoreextension.types.AzureKeyVaultSecretProviderClassUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AzureKeyVaultSecretProviderClassUpdateProperties', module='types')
        properties: AzureKeyVaultSecretProviderClassUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.secretsstoreextension.types.AzureKeyVaultSecretProviderClassUpdateProperties(TypedDict, total=False):
        key "clientId": str
        key "cloudName": Union[str, AzureCloudName]
        key "keyvaultName": str
        key "objects": str
        key "tenantId": str
        clientId: str
        cloudName: Union[str, AzureCloudName]
        keyvaultName: str
        objects: str
        tenantId: str


    class azure.mgmt.secretsstoreextension.types.ExtendedLocation(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ExtendedLocationType]]
        name: str
        type: Union[str, ExtendedLocationType]


    class azure.mgmt.secretsstoreextension.types.KubernetesSecretObjectMapping(TypedDict, total=False):
        key "sourcePath": Required[str]
        key "targetKey": Required[str]
        sourcePath: str
        targetKey: str


    class azure.mgmt.secretsstoreextension.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.secretsstoreextension.types.SecretSync(TrackedResource):
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SecretSyncProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: SecretSyncProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.secretsstoreextension.types.SecretSyncCondition(TypedDict, total=False):
        key "lastTransitionTime": str
        key "message": Required[str]
        key "observedGeneration": int
        key "reason": Required[str]
        key "status": Required[Union[str, StatusConditionType]]
        key "type": Required[str]
        lastTransitionTime: str
        message: str
        observedGeneration: int
        reason: str
        status: Union[str, StatusConditionType]
        type: str


    class azure.mgmt.secretsstoreextension.types.SecretSyncProperties(TypedDict, total=False):
        key "forceSynchronization": str
        key "kubernetesSecretType": Required[Union[str, KubernetesSecretType]]
        key "objectSecretMapping": Required[list[KubernetesSecretObjectMapping]]
        key "provisioningState": Union[str, ProvisioningState]
        key "secretProviderClassName": Required[str]
        key "serviceAccountName": Required[str]
        key "status": ForwardRef('SecretSyncStatus', module='types')
        forceSynchronization: str
        kubernetesSecretType: Union[str, KubernetesSecretType]
        objectSecretMapping: list[KubernetesSecretObjectMapping]
        provisioningState: Union[str, ProvisioningState]
        secretProviderClassName: str
        serviceAccountName: str
        status: SecretSyncStatus


    class azure.mgmt.secretsstoreextension.types.SecretSyncStatus(TypedDict, total=False):
        key "lastSuccessfulSyncTime": str
        conditions: list[SecretSyncCondition]
        lastSuccessfulSyncTime: str


    class azure.mgmt.secretsstoreextension.types.SecretSyncUpdate(TypedDict, total=False):
        key "properties": ForwardRef('SecretSyncUpdateProperties', module='types')
        properties: SecretSyncUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.secretsstoreextension.types.SecretSyncUpdateProperties(TypedDict, total=False):
        key "forceSynchronization": str
        key "secretProviderClassName": str
        key "serviceAccountName": str
        forceSynchronization: str
        objectSecretMapping: list[KubernetesSecretObjectMapping]
        secretProviderClassName: str
        serviceAccountName: str


    class azure.mgmt.secretsstoreextension.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        createdAt: str
        createdBy: str
        createdByType: Union[str, CreatedByType]
        lastModifiedAt: str
        lastModifiedBy: str
        lastModifiedByType: Union[str, CreatedByType]


    class azure.mgmt.secretsstoreextension.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


```