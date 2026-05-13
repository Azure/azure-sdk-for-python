```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.kubernetesconfiguration.extensions

    class azure.mgmt.kubernetesconfiguration.extensions.KubernetesConfigurationExtensionsMgmtClient: implements ContextManager 
        extensions: ExtensionsOperations
        operation_status: OperationStatusOperations

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


namespace azure.mgmt.kubernetesconfiguration.extensions.aio

    class azure.mgmt.kubernetesconfiguration.extensions.aio.KubernetesConfigurationExtensionsMgmtClient: implements AsyncContextManager 
        extensions: ExtensionsOperations
        operation_status: OperationStatusOperations

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


namespace azure.mgmt.kubernetesconfiguration.extensions.aio.operations

    class azure.mgmt.kubernetesconfiguration.extensions.aio.operations.ExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: PatchExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Extension]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> Extension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Extension]: ...


    class azure.mgmt.kubernetesconfiguration.extensions.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


namespace azure.mgmt.kubernetesconfiguration.extensions.models

    class azure.mgmt.kubernetesconfiguration.extensions.models.AKSIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"
        WORKLOAD = "Workload"


    class azure.mgmt.kubernetesconfiguration.extensions.models.AccessDetail(_Model):
        allowed_actions: Optional[list[str]]
        description: Optional[str]
        entity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_actions: Optional[list[str]] = ..., 
                description: Optional[str] = ..., 
                entity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.AdditionalDetails(_Model):
        docs: Optional[str]
        release_notes: Optional[str]
        troubleshooting_guide: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                docs: Optional[str] = ..., 
                release_notes: Optional[str] = ..., 
                troubleshooting_guide: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.AutoUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPATIBLE = "compatible"
        NONE = "none"
        PATCH = "patch"


    class azure.mgmt.kubernetesconfiguration.extensions.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kubernetesconfiguration.extensions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensions.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.Extension(ProxyResource):
        id: str
        identity: Optional[Identity]
        managed_by: Optional[str]
        name: str
        plan: Optional[Plan]
        properties: Optional[ExtensionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                managed_by: Optional[str] = ..., 
                plan: Optional[Plan] = ..., 
                properties: Optional[ExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ExtensionProperties(_Model):
        additional_details: Optional[AdditionalDetails]
        aks_assigned_identity: Optional[ExtensionPropertiesAksAssignedIdentity]
        auto_upgrade_minor_version: Optional[bool]
        auto_upgrade_mode: Optional[Union[str, AutoUpgradeMode]]
        configuration_protected_settings: Optional[dict[str, str]]
        configuration_settings: Optional[dict[str, str]]
        current_version: Optional[str]
        custom_location_settings: Optional[dict[str, str]]
        error_info: Optional[ErrorDetail]
        extension_state: Optional[str]
        extension_type: Optional[str]
        is_system_extension: Optional[bool]
        management_details: Optional[ManagementDetails]
        package_uri: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        release_train: Optional[str]
        scope: Optional[Scope]
        statuses: Optional[list[ExtensionStatus]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_details: Optional[AdditionalDetails] = ..., 
                aks_assigned_identity: Optional[ExtensionPropertiesAksAssignedIdentity] = ..., 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                auto_upgrade_mode: Optional[Union[str, AutoUpgradeMode]] = ..., 
                configuration_protected_settings: Optional[dict[str, str]] = ..., 
                configuration_settings: Optional[dict[str, str]] = ..., 
                extension_type: Optional[str] = ..., 
                management_details: Optional[ManagementDetails] = ..., 
                release_train: Optional[str] = ..., 
                scope: Optional[Scope] = ..., 
                statuses: Optional[list[ExtensionStatus]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ExtensionPropertiesAksAssignedIdentity(_Model):
        client_id: Optional[str]
        object_id: Optional[str]
        principal_id: Optional[str]
        resource_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, AKSIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                object_id: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                type: Optional[Union[str, AKSIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ExtensionStatus(_Model):
        code: Optional[str]
        display_status: Optional[str]
        level: Optional[Union[str, LevelType]]
        message: Optional[str]
        time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                display_status: Optional[str] = ..., 
                level: Optional[Union[str, LevelType]] = ..., 
                message: Optional[str] = ..., 
                time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.Identity(_Model):
        principal_id: Optional[str]
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


    class azure.mgmt.kubernetesconfiguration.extensions.models.LevelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        WARNING = "Warning"


    class azure.mgmt.kubernetesconfiguration.extensions.models.ManagementDetails(_Model):
        access_details: Optional[list[AccessDetail]]
        category: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_details: Optional[list[AccessDetail]] = ..., 
                category: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.OperationStatusResult(_Model):
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        properties: Optional[dict[str, str]]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.PatchExtension(_Model):
        properties: Optional[PatchExtensionProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PatchExtensionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.PatchExtensionProperties(_Model):
        auto_upgrade_minor_version: Optional[bool]
        auto_upgrade_mode: Optional[Union[str, AutoUpgradeMode]]
        configuration_protected_settings: Optional[dict[str, str]]
        configuration_settings: Optional[dict[str, str]]
        release_train: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_minor_version: Optional[bool] = ..., 
                auto_upgrade_mode: Optional[Union[str, AutoUpgradeMode]] = ..., 
                configuration_protected_settings: Optional[dict[str, str]] = ..., 
                configuration_settings: Optional[dict[str, str]] = ..., 
                release_train: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.Plan(_Model):
        name: str
        product: str
        promotion_code: Optional[str]
        publisher: str
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.kubernetesconfiguration.extensions.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.kubernetesconfiguration.extensions.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensions.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.kubernetesconfiguration.extensions.models.Scope(_Model):
        cluster: Optional[ScopeCluster]
        namespace: Optional[ScopeNamespace]

        @overload
        def __init__(
                self, 
                *, 
                cluster: Optional[ScopeCluster] = ..., 
                namespace: Optional[ScopeNamespace] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ScopeCluster(_Model):
        release_namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                release_namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.ScopeNamespace(_Model):
        target_namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensions.models.SystemData(_Model):
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


namespace azure.mgmt.kubernetesconfiguration.extensions.operations

    class azure.mgmt.kubernetesconfiguration.extensions.operations.ExtensionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: Extension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                *, 
                force_delete: Optional[bool] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: PatchExtension, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                patch_extension: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Extension]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                **kwargs: Any
            ) -> Extension: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Extension]: ...


    class azure.mgmt.kubernetesconfiguration.extensions.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_name: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


```