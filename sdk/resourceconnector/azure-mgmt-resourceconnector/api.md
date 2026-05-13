```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.resourceconnector

    class azure.mgmt.resourceconnector.ResourceConnectorMgmtClient: implements ContextManager 
        appliances: AppliancesOperations

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


namespace azure.mgmt.resourceconnector.aio

    class azure.mgmt.resourceconnector.aio.ResourceConnectorMgmtClient: implements AsyncContextManager 
        appliances: AppliancesOperations

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


namespace azure.mgmt.resourceconnector.aio.operations

    class azure.mgmt.resourceconnector.aio.operations.AppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Appliance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Appliance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Appliance]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Appliance]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Appliance: ...

        @distributed_trace_async
        async def get_telemetry_config(self, **kwargs: Any) -> ApplianceGetTelemetryConfigResult: ...

        @distributed_trace_async
        async def get_upgrade_graph(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                upgrade_graph: str, 
                **kwargs: Any
            ) -> UpgradeGraph: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Appliance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Appliance]: ...

        @distributed_trace_async
        async def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplianceListCredentialResults: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                artifact_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ApplianceListKeysResults: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> AsyncItemPaged[ApplianceOperation]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                content_type: str = "application/json", 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> Appliance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Appliance: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Appliance: ...


namespace azure.mgmt.resourceconnector.models

    class azure.mgmt.resourceconnector.models.AccessProfileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER_CUSTOMER_USER = "clusterCustomerUser"
        CLUSTER_USER = "clusterUser"


    class azure.mgmt.resourceconnector.models.Appliance(TrackedResource):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[ApplianceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: str, 
                properties: Optional[ApplianceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourceconnector.models.ApplianceCredentialKubeconfig(_Model):
        name: Optional[Union[str, AccessProfileType]]
        value: Optional[str]


    class azure.mgmt.resourceconnector.models.ApplianceGetTelemetryConfigResult(_Model):
        telemetry_instrumentation_key: Optional[str]


    class azure.mgmt.resourceconnector.models.ApplianceListCredentialResults(_Model):
        hybrid_connection_config: Optional[HybridConnectionConfig]
        kubeconfigs: Optional[list[ApplianceCredentialKubeconfig]]


    class azure.mgmt.resourceconnector.models.ApplianceListKeysResults(_Model):
        artifact_profiles: Optional[dict[str, ArtifactProfile]]
        kubeconfigs: Optional[list[ApplianceCredentialKubeconfig]]
        ssh_keys: Optional[dict[str, SSHKey]]


    class azure.mgmt.resourceconnector.models.ApplianceOperation(_Model):
        display: Optional[ApplianceOperationValueDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[ApplianceOperationValueDisplay] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.resourceconnector.models.ApplianceOperationValueDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.resourceconnector.models.ApplianceProperties(_Model):
        distro: Optional[Union[str, Distro]]
        events: Optional[list[Event]]
        infrastructure_config: Optional[AppliancePropertiesInfrastructureConfig]
        network_profile: Optional[NetworkProfile]
        provisioning_state: Optional[str]
        public_key: Optional[str]
        status: Optional[Union[str, Status]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                distro: Optional[Union[str, Distro]] = ..., 
                infrastructure_config: Optional[AppliancePropertiesInfrastructureConfig] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                public_key: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.AppliancePropertiesInfrastructureConfig(_Model):
        provider: Optional[Union[str, Provider]]

        @overload
        def __init__(
                self, 
                *, 
                provider: Optional[Union[str, Provider]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.ArtifactProfile(_Model):
        endpoint: Optional[str]


    class azure.mgmt.resourceconnector.models.ArtifactType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGS_ARTIFACT_TYPE = "LogsArtifactType"


    class azure.mgmt.resourceconnector.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.resourceconnector.models.Distro(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS_EDGE = "AKSEdge"


    class azure.mgmt.resourceconnector.models.DnsConfiguration(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.resourceconnector.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.resourceconnector.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.Event(_Model):
        code: Optional[str]
        message: Optional[str]
        severity: Optional[str]
        status: Optional[str]
        timestamp: Optional[datetime]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
                severity: Optional[str] = ..., 
                status: Optional[str] = ..., 
                timestamp: Optional[datetime] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.GatewayConfiguration(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.HybridConnectionConfig(_Model):
        expiration_time: Optional[int]
        hybrid_connection_name: Optional[str]
        relay: Optional[str]
        token: Optional[str]


    class azure.mgmt.resourceconnector.models.Identity(_Model):
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


    class azure.mgmt.resourceconnector.models.NetworkProfile(_Model):
        dns_configuration: Optional[DnsConfiguration]
        gateway_configuration: Optional[GatewayConfiguration]
        proxy_configuration: Optional[ProxyConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                dns_configuration: Optional[DnsConfiguration] = ..., 
                gateway_configuration: Optional[GatewayConfiguration] = ..., 
                proxy_configuration: Optional[ProxyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.PatchableAppliance(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.Provider(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HCI = "HCI"
        SCVMM = "SCVMM"
        VM_WARE = "VMWare"


    class azure.mgmt.resourceconnector.models.ProxyConfiguration(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.resourceconnector.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.resourceconnector.models.SSHKey(_Model):
        certificate: Optional[str]
        creation_time_stamp: Optional[int]
        expiration_time_stamp: Optional[int]
        private_key: Optional[str]
        public_key: Optional[str]


    class azure.mgmt.resourceconnector.models.SSHKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOGS_KEY = "LogsKey"
        MANAGEMENT_CA_KEY = "ManagementCAKey"
        SCOPED_ACCESS_KEY = "ScopedAccessKey"
        SSH_CUSTOMER_USER = "SSHCustomerUser"
        USER_MANAGEMENT_KEY = "UserManagementKey"


    class azure.mgmt.resourceconnector.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC_GATEWAY_UPDATE_COMPLETE = "ArcGatewayUpdateComplete"
        ARC_GATEWAY_UPDATE_FAILED = "ArcGatewayUpdateFailed"
        ARC_GATEWAY_UPDATE_PREPARING = "ArcGatewayUpdatePreparing"
        ARC_GATEWAY_UPDATING = "ArcGatewayUpdating"
        CONNECTED = "Connected"
        CONNECTING = "Connecting"
        ETCD_SNAPSHOT_FAILED = "ETCDSnapshotFailed"
        IMAGE_DEPROVISIONING = "ImageDeprovisioning"
        IMAGE_DOWNLOADED = "ImageDownloaded"
        IMAGE_DOWNLOADING = "ImageDownloading"
        IMAGE_PENDING = "ImagePending"
        IMAGE_PROVISIONED = "ImageProvisioned"
        IMAGE_PROVISIONING = "ImageProvisioning"
        IMAGE_UNKNOWN = "ImageUnknown"
        NETWORK_DNS_UPDATE_COMPLETE = "NetworkDNSUpdateComplete"
        NETWORK_DNS_UPDATE_FAILED = "NetworkDNSUpdateFailed"
        NETWORK_DNS_UPDATE_PREPARING = "NetworkDNSUpdatePreparing"
        NETWORK_DNS_UPDATING = "NetworkDNSUpdating"
        NETWORK_PROXY_UPDATE_COMPLETE = "NetworkProxyUpdateComplete"
        NETWORK_PROXY_UPDATE_FAILED = "NetworkProxyUpdateFailed"
        NETWORK_PROXY_UPDATE_PREPARING = "NetworkProxyUpdatePreparing"
        NETWORK_PROXY_UPDATING = "NetworkProxyUpdating"
        NONE = "None"
        OFFLINE = "Offline"
        POST_UPGRADE = "PostUpgrade"
        PREPARING_FOR_UPGRADE = "PreparingForUpgrade"
        PRE_UPGRADE = "PreUpgrade"
        RUNNING = "Running"
        UPDATING_CAPI = "UpdatingCAPI"
        UPDATING_CLOUD_OPERATOR = "UpdatingCloudOperator"
        UPDATING_CLUSTER = "UpdatingCluster"
        UPGRADE_CLUSTER_EXTENSION_FAILED_TO_DELETE = "UpgradeClusterExtensionFailedToDelete"
        UPGRADE_COMPLETE = "UpgradeComplete"
        UPGRADE_FAILED = "UpgradeFailed"
        UPGRADE_PREREQUISITES_COMPLETED = "UpgradePrerequisitesCompleted"
        UPGRADING_KVAIO = "UpgradingKVAIO"
        VALIDATING = "Validating"
        VALIDATING_ETCD_HEALTH = "ValidatingETCDHealth"
        VALIDATING_IMAGE_DOWNLOAD = "ValidatingImageDownload"
        VALIDATING_IMAGE_UPLOAD = "ValidatingImageUpload"
        VALIDATING_SFS_CONNECTIVITY = "ValidatingSFSConnectivity"
        WAITING_FOR_CLOUD_OPERATOR = "WaitingForCloudOperator"
        WAITING_FOR_HEARTBEAT = "WaitingForHeartbeat"
        WAITING_FOR_KVAIO = "WaitingForKVAIO"


    class azure.mgmt.resourceconnector.models.SupportedVersion(_Model):
        metadata: Optional[SupportedVersionMetadata]
        version: Optional[str]


    class azure.mgmt.resourceconnector.models.SupportedVersionCatalogVersion(_Model):
        data: Optional[SupportedVersionCatalogVersionData]
        name: Optional[str]
        namespace: Optional[str]


    class azure.mgmt.resourceconnector.models.SupportedVersionCatalogVersionData(_Model):
        audience: Optional[str]
        catalog: Optional[str]
        offer: Optional[str]
        version: Optional[str]


    class azure.mgmt.resourceconnector.models.SupportedVersionMetadata(_Model):
        catalog_version: Optional[SupportedVersionCatalogVersion]


    class azure.mgmt.resourceconnector.models.SystemData(_Model):
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


    class azure.mgmt.resourceconnector.models.TrackedResource(Resource):
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


    class azure.mgmt.resourceconnector.models.UpgradeGraph(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[UpgradeGraphProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpgradeGraphProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.resourceconnector.models.UpgradeGraphProperties(_Model):
        appliance_version: Optional[str]
        supported_versions: Optional[list[SupportedVersion]]


namespace azure.mgmt.resourceconnector.operations

    class azure.mgmt.resourceconnector.operations.AppliancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: Appliance, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Appliance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Appliance]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Appliance]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> Appliance: ...

        @distributed_trace
        def get_telemetry_config(self, **kwargs: Any) -> ApplianceGetTelemetryConfigResult: ...

        @distributed_trace
        def get_upgrade_graph(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                upgrade_graph: str, 
                **kwargs: Any
            ) -> UpgradeGraph: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Appliance]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Appliance]: ...

        @distributed_trace
        def list_cluster_user_credential(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ApplianceListCredentialResults: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                artifact_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> ApplianceListKeysResults: ...

        @distributed_trace
        def list_operations(self, **kwargs: Any) -> ItemPaged[ApplianceOperation]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                *, 
                content_type: str = "application/json", 
                tags: Optional[dict[str, str]] = ..., 
                **kwargs: Any
            ) -> Appliance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Appliance: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Appliance: ...


```