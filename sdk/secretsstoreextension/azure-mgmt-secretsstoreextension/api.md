```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> AsyncIterable[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[AzureKeyVaultSecretProviderClass]: ...


    class azure.mgmt.secretsstoreextension.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> AsyncIterable[SecretSync]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[SecretSync]: ...


namespace azure.mgmt.secretsstoreextension.models

    class azure.mgmt.secretsstoreextension.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


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
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassProperties(_Model):
        client_id: str
        keyvault_name: str
        objects: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                keyvault_name: str, 
                objects: Optional[str] = ..., 
                tenant_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassUpdate(_Model):
        properties: Optional[AzureKeyVaultSecretProviderClassUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AzureKeyVaultSecretProviderClassUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.AzureKeyVaultSecretProviderClassUpdateProperties(_Model):
        client_id: Optional[str]
        keyvault_name: Optional[str]
        objects: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
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
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
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
                tags: Optional[Dict[str, str]] = ...
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
        object_secret_mapping: List[KubernetesSecretObjectMapping]
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
                object_secret_mapping: List[KubernetesSecretObjectMapping], 
                secret_provider_class_name: str, 
                service_account_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.SecretSyncStatus(_Model):
        conditions: Optional[List[SecretSyncCondition]]
        last_successful_sync_time: Optional[datetime]


    class azure.mgmt.secretsstoreextension.models.SecretSyncUpdate(_Model):
        properties: Optional[SecretSyncUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecretSyncUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.secretsstoreextension.models.SecretSyncUpdateProperties(_Model):
        force_synchronization: Optional[str]
        kubernetes_secret_type: Optional[Union[str, KubernetesSecretType]]
        object_secret_mapping: Optional[List[KubernetesSecretObjectMapping]]
        secret_provider_class_name: Optional[str]
        service_account_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                force_synchronization: Optional[str] = ..., 
                kubernetes_secret_type: Optional[Union[str, KubernetesSecretType]] = ..., 
                object_secret_mapping: Optional[List[KubernetesSecretObjectMapping]] = ..., 
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


namespace azure.mgmt.secretsstoreextension.operations

    class azure.mgmt.secretsstoreextension.operations.AzureKeyVaultSecretProviderClassesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> Iterable[AzureKeyVaultSecretProviderClass]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[AzureKeyVaultSecretProviderClass]: ...


    class azure.mgmt.secretsstoreextension.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.secretsstoreextension.operations.SecretSyncsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

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
                resource: JSON, 
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
                properties: JSON, 
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
            ) -> Iterable[SecretSync]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[SecretSync]: ...


```