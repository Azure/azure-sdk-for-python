```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.disconnectedoperations

    class azure.mgmt.disconnectedoperations.DisconnectedOperationsMgmtClient: implements ContextManager 
        artifacts: ArtifactsOperations
        disconnected_operations: DisconnectedOperationsOperations
        hardware_settings: HardwareSettingsOperations
        images: ImagesOperations

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


namespace azure.mgmt.disconnectedoperations.aio

    class azure.mgmt.disconnectedoperations.aio.DisconnectedOperationsMgmtClient: implements AsyncContextManager 
        artifacts: ArtifactsOperations
        disconnected_operations: DisconnectedOperationsOperations
        hardware_settings: HardwareSettingsOperations
        images: ImagesOperations

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


namespace azure.mgmt.disconnectedoperations.aio.operations

    class azure.mgmt.disconnectedoperations.aio.operations.ArtifactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> Artifact: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Artifact]: ...

        @distributed_trace_async
        async def list_download_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> ArtifactDownloadResult: ...


    class azure.mgmt.disconnectedoperations.aio.operations.DisconnectedOperationsOperations:

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
                resource: DisconnectedOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DisconnectedOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DisconnectedOperation]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DisconnectedOperation]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DisconnectedOperation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[DisconnectedOperation]: ...

        @distributed_trace_async
        async def list_deployment_manifest(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DisconnectedOperationDeploymentManifest: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: DisconnectedOperationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...


    class azure.mgmt.disconnectedoperations.aio.operations.HardwareSettingsOperations:

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
                hardware_setting_name: str, 
                resource: HardwareSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HardwareSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HardwareSetting]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[HardwareSetting]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'hardware_setting_name']}, api_versions_list=['2026-03-15'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'hardware_setting_name', 'accept']}, api_versions_list=['2026-03-15'])
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                **kwargs: Any
            ) -> HardwareSetting: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'accept']}, api_versions_list=['2026-03-15'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HardwareSetting]: ...


    class azure.mgmt.disconnectedoperations.aio.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_disconnected_operation(
                self, 
                resource_group_name: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Image]: ...

        @distributed_trace_async
        async def list_download_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> ImageDownloadResult: ...


namespace azure.mgmt.disconnectedoperations.models

    class azure.mgmt.disconnectedoperations.models.Artifact(ProxyResource):
        id: str
        name: str
        properties: Optional[ArtifactProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArtifactProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.ArtifactDownloadResult(_Model):
        artifact_order: int
        description: str
        download_link: str
        link_expiry: datetime
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        size: Optional[int]
        title: str


    class azure.mgmt.disconnectedoperations.models.ArtifactProperties(_Model):
        artifact_order: int
        description: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        size: Optional[int]
        title: str


    class azure.mgmt.disconnectedoperations.models.AutoRenew(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.disconnectedoperations.models.BenefitPlanStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.disconnectedoperations.models.BenefitPlans(_Model):
        azure_hybrid_windows_server_benefit: Optional[Union[str, BenefitPlanStatus]]
        windows_server_vm_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                azure_hybrid_windows_server_benefit: Optional[Union[str, BenefitPlanStatus]] = ..., 
                windows_server_vm_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.BillingConfiguration(_Model):
        auto_renew: Union[str, AutoRenew]
        billing_status: Union[str, BillingStatus]
        current: BillingPeriod
        upcoming: Optional[BillingPeriod]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Union[str, AutoRenew], 
                current: BillingPeriod, 
                upcoming: Optional[BillingPeriod] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.BillingModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CAPACITY = "Capacity"


    class azure.mgmt.disconnectedoperations.models.BillingPeriod(_Model):
        cores: int
        end_date: Optional[date]
        pricing_model: Union[str, PricingModel]
        start_date: Optional[date]

        @overload
        def __init__(
                self, 
                *, 
                cores: int, 
                pricing_model: Union[str, PricingModel]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.BillingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        STOPPED = "Stopped"


    class azure.mgmt.disconnectedoperations.models.ConnectionIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.disconnectedoperations.models.ConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.disconnectedoperations.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.disconnectedoperations.models.DisconnectedOperation(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[DisconnectedOperationProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[DisconnectedOperationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.DisconnectedOperationDeploymentManifest(_Model):
        benefit_plans: Optional[BenefitPlans]
        billing_configuration: Optional[BillingConfiguration]
        billing_model: Union[str, BillingModel]
        cloud: Optional[str]
        connection_intent: Union[str, ConnectionIntent]
        location: str
        resource_id: str
        resource_name: str
        stamp_id: str


    class azure.mgmt.disconnectedoperations.models.DisconnectedOperationProperties(_Model):
        benefit_plans: Optional[BenefitPlans]
        billing_configuration: Optional[BillingConfiguration]
        billing_model: Union[str, BillingModel]
        connection_intent: Union[str, ConnectionIntent]
        connection_status: Optional[Union[str, ConnectionStatus]]
        device_version: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        registration_status: Optional[Union[str, RegistrationStatus]]
        stamp_id: str

        @overload
        def __init__(
                self, 
                *, 
                benefit_plans: Optional[BenefitPlans] = ..., 
                billing_configuration: Optional[BillingConfiguration] = ..., 
                connection_intent: Union[str, ConnectionIntent], 
                device_version: Optional[str] = ..., 
                registration_status: Optional[Union[str, RegistrationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.DisconnectedOperationUpdate(_Model):
        properties: Optional[DisconnectedOperationUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DisconnectedOperationUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.DisconnectedOperationUpdateProperties(_Model):
        benefit_plans: Optional[BenefitPlans]
        billing_configuration: Optional[BillingConfiguration]
        connection_intent: Optional[Union[str, ConnectionIntent]]
        device_version: Optional[str]
        registration_status: Optional[Union[str, RegistrationStatus]]

        @overload
        def __init__(
                self, 
                *, 
                benefit_plans: Optional[BenefitPlans] = ..., 
                billing_configuration: Optional[BillingConfiguration] = ..., 
                connection_intent: Optional[Union[str, ConnectionIntent]] = ..., 
                device_version: Optional[str] = ..., 
                registration_status: Optional[Union[str, RegistrationStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.disconnectedoperations.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.disconnectedoperations.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.HardwareSetting(ProxyResource):
        id: str
        name: str
        properties: Optional[HardwareSettingProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HardwareSettingProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.HardwareSettingProperties(_Model):
        device_id: str
        disk_space_in_gb: int
        hardware_sku: str
        memory_in_gb: int
        nodes: int
        oem: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        solution_builder_extension: str
        total_cores: int
        version_at_registration: str

        @overload
        def __init__(
                self, 
                *, 
                device_id: str, 
                disk_space_in_gb: int, 
                hardware_sku: str, 
                memory_in_gb: int, 
                nodes: int, 
                oem: str, 
                solution_builder_extension: str, 
                total_cores: int, 
                version_at_registration: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.Image(ProxyResource):
        id: str
        name: str
        properties: Optional[ImageProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ImageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.disconnectedoperations.models.ImageDownloadResult(_Model):
        compatible_versions: Optional[list[str]]
        download_link: str
        link_expiry: datetime
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        release_date: date
        release_display_name: str
        release_notes: str
        release_type: Union[str, ReleaseType]
        release_version: str
        transaction_id: str
        update_properties: Optional[ImageUpdateProperties]


    class azure.mgmt.disconnectedoperations.models.ImageProperties(_Model):
        compatible_versions: Optional[list[str]]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        release_date: date
        release_display_name: str
        release_notes: str
        release_type: Union[str, ReleaseType]
        release_version: str
        update_properties: Optional[ImageUpdateProperties]


    class azure.mgmt.disconnectedoperations.models.ImageUpdateProperties(_Model):
        agent_version: str
        feature_updates: str
        os_version: str
        security_updates: str
        system_reboot: Union[str, SystemReboot]


    class azure.mgmt.disconnectedoperations.models.PricingModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNUAL = "Annual"
        TRIAL = "Trial"


    class azure.mgmt.disconnectedoperations.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.disconnectedoperations.models.RegistrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGISTERED = "Registered"
        UNREGISTERED = "Unregistered"


    class azure.mgmt.disconnectedoperations.models.ReleaseType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSTALL = "Install"
        UPDATE = "Update"


    class azure.mgmt.disconnectedoperations.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.disconnectedoperations.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.disconnectedoperations.models.SystemData(_Model):
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


    class azure.mgmt.disconnectedoperations.models.SystemReboot(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REQUIRED = "NotRequired"
        REQUIRED = "Required"


    class azure.mgmt.disconnectedoperations.models.TrackedResource(Resource):
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


namespace azure.mgmt.disconnectedoperations.operations

    class azure.mgmt.disconnectedoperations.operations.ArtifactsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> Artifact: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Artifact]: ...

        @distributed_trace
        def list_download_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                artifact_name: str, 
                **kwargs: Any
            ) -> ArtifactDownloadResult: ...


    class azure.mgmt.disconnectedoperations.operations.DisconnectedOperationsOperations:

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
                resource: DisconnectedOperation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DisconnectedOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DisconnectedOperation]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DisconnectedOperation]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DisconnectedOperation]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[DisconnectedOperation]: ...

        @distributed_trace
        def list_deployment_manifest(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> DisconnectedOperationDeploymentManifest: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: DisconnectedOperationUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DisconnectedOperation: ...


    class azure.mgmt.disconnectedoperations.operations.HardwareSettingsOperations:

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
                hardware_setting_name: str, 
                resource: HardwareSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HardwareSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HardwareSetting]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[HardwareSetting]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'hardware_setting_name']}, api_versions_list=['2026-03-15'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'hardware_setting_name', 'accept']}, api_versions_list=['2026-03-15'])
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                hardware_setting_name: str, 
                **kwargs: Any
            ) -> HardwareSetting: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15', params_added_on={'2026-03-15': ['api_version', 'subscription_id', 'resource_group_name', 'name', 'accept']}, api_versions_list=['2026-03-15'])
        def list_by_parent(
                self, 
                resource_group_name: str, 
                name: str, 
                **kwargs: Any
            ) -> ItemPaged[HardwareSetting]: ...


    class azure.mgmt.disconnectedoperations.operations.ImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> Image: ...

        @distributed_trace
        def list_by_disconnected_operation(
                self, 
                resource_group_name: str, 
                name: str, 
                *, 
                filter: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Image]: ...

        @distributed_trace
        def list_download_uri(
                self, 
                resource_group_name: str, 
                name: str, 
                image_name: str, 
                **kwargs: Any
            ) -> ImageDownloadResult: ...


```