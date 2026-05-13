```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.kubernetesconfiguration.extensiontypes

    class azure.mgmt.kubernetesconfiguration.extensiontypes.KubernetesConfigurationExtensionTypesMgmtClient: implements ContextManager 
        extension_types: ExtensionTypesOperations

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


namespace azure.mgmt.kubernetesconfiguration.extensiontypes.aio

    class azure.mgmt.kubernetesconfiguration.extensiontypes.aio.KubernetesConfigurationExtensionTypesMgmtClient: implements AsyncContextManager 
        extension_types: ExtensionTypesOperations

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


namespace azure.mgmt.kubernetesconfiguration.extensiontypes.aio.operations

    class azure.mgmt.kubernetesconfiguration.extensiontypes.aio.operations.ExtensionTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cluster_get_version(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                version_number: str, 
                **kwargs: Any
            ) -> ExtensionTypeVersionForReleaseTrain: ...

        @distributed_trace
        def cluster_list_versions(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                *, 
                major_version: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                show_latest: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionTypeVersionForReleaseTrain]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                **kwargs: Any
            ) -> ExtensionType: ...

        @distributed_trace_async
        async def get_version(
                self, 
                location: str, 
                extension_type_name: str, 
                version_number: str, 
                **kwargs: Any
            ) -> ExtensionTypeVersionForReleaseTrain: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionType]: ...

        @distributed_trace
        def list_versions(
                self, 
                location: str, 
                extension_type_name: str, 
                *, 
                cluster_type: Optional[str] = ..., 
                major_version: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                show_latest: Optional[bool] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionTypeVersionForReleaseTrain]: ...

        @distributed_trace_async
        async def location_get(
                self, 
                location: str, 
                extension_type_name: str, 
                **kwargs: Any
            ) -> ExtensionType: ...

        @distributed_trace
        def location_list(
                self, 
                location: str, 
                *, 
                cluster_type: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ExtensionType]: ...


namespace azure.mgmt.kubernetesconfiguration.extensiontypes.models

    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ClusterScopeSettings(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterScopeSettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterScopeSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ClusterScopeSettingsProperties(_Model):
        allow_multiple_instances: Optional[bool]
        default_release_namespace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allow_multiple_instances: Optional[bool] = ..., 
                default_release_namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionType(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtensionTypeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionTypeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypeProperties(_Model):
        description: Optional[str]
        is_managed_identity_required: Optional[bool]
        is_system_extension: Optional[bool]
        plan_info: Optional[ExtensionTypePropertiesPlanInfo]
        publisher: Optional[str]
        supported_cluster_types: Optional[list[str]]
        supported_scopes: Optional[ExtensionTypePropertiesSupportedScopes]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                is_managed_identity_required: Optional[bool] = ..., 
                is_system_extension: Optional[bool] = ..., 
                plan_info: Optional[ExtensionTypePropertiesPlanInfo] = ..., 
                publisher: Optional[str] = ..., 
                supported_cluster_types: Optional[list[str]] = ..., 
                supported_scopes: Optional[ExtensionTypePropertiesSupportedScopes] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypePropertiesPlanInfo(_Model):
        offer_id: Optional[str]
        plan_id: Optional[str]
        publisher_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypePropertiesSupportedScopes(_Model):
        cluster_scope_settings: Optional[ClusterScopeSettings]
        default_scope: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_scope_settings: Optional[ClusterScopeSettings] = ..., 
                default_scope: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypeVersionForReleaseTrain(ProxyResource):
        id: str
        name: str
        properties: Optional[ExtensionTypeVersionForReleaseTrainProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExtensionTypeVersionForReleaseTrainProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypeVersionForReleaseTrainProperties(_Model):
        supported_cluster_types: Optional[list[str]]
        unsupported_kubernetes_versions: Optional[ExtensionTypeVersionForReleaseTrainPropertiesUnsupportedKubernetesVersions]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                supported_cluster_types: Optional[list[str]] = ..., 
                unsupported_kubernetes_versions: Optional[ExtensionTypeVersionForReleaseTrainPropertiesUnsupportedKubernetesVersions] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypeVersionForReleaseTrainPropertiesUnsupportedKubernetesVersions(_Model):
        appliances: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]]
        connected_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]]
        managed_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]]
        provisioned_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]]

        @overload
        def __init__(
                self, 
                *, 
                appliances: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]] = ..., 
                connected_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]] = ..., 
                managed_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]] = ..., 
                provisioned_cluster: Optional[list[ExtensionTypeVersionUnsupportedKubernetesMatrixItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ExtensionTypeVersionUnsupportedKubernetesMatrixItem(_Model):
        distributions: Optional[list[str]]
        unsupported_versions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                distributions: Optional[list[str]] = ..., 
                unsupported_versions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.kubernetesconfiguration.extensiontypes.models.SystemData(_Model):
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


namespace azure.mgmt.kubernetesconfiguration.extensiontypes.operations

    class azure.mgmt.kubernetesconfiguration.extensiontypes.operations.ExtensionTypesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cluster_get_version(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                version_number: str, 
                **kwargs: Any
            ) -> ExtensionTypeVersionForReleaseTrain: ...

        @distributed_trace
        def cluster_list_versions(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                *, 
                major_version: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                show_latest: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExtensionTypeVersionForReleaseTrain]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                extension_type_name: str, 
                **kwargs: Any
            ) -> ExtensionType: ...

        @distributed_trace
        def get_version(
                self, 
                location: str, 
                extension_type_name: str, 
                version_number: str, 
                **kwargs: Any
            ) -> ExtensionTypeVersionForReleaseTrain: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_rp: str, 
                cluster_resource_name: str, 
                cluster_name: str, 
                *, 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExtensionType]: ...

        @distributed_trace
        def list_versions(
                self, 
                location: str, 
                extension_type_name: str, 
                *, 
                cluster_type: Optional[str] = ..., 
                major_version: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                show_latest: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExtensionTypeVersionForReleaseTrain]: ...

        @distributed_trace
        def location_get(
                self, 
                location: str, 
                extension_type_name: str, 
                **kwargs: Any
            ) -> ExtensionType: ...

        @distributed_trace
        def location_list(
                self, 
                location: str, 
                *, 
                cluster_type: Optional[str] = ..., 
                offer_id: Optional[str] = ..., 
                plan_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                release_train: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ExtensionType]: ...


```