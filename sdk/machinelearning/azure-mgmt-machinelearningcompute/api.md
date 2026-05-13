```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.machinelearningcompute

    class azure.mgmt.machinelearningcompute.MachineLearningComputeManagementClient: implements ContextManager 
        machine_learning_compute: MachineLearningComputeOperations
        operationalization_clusters: OperationalizationClustersOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.machinelearningcompute.aio

    class azure.mgmt.machinelearningcompute.aio.MachineLearningComputeManagementClient: implements AsyncContextManager 
        machine_learning_compute: MachineLearningComputeOperations
        operationalization_clusters: OperationalizationClustersOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.machinelearningcompute.aio.operations

    class azure.mgmt.machinelearningcompute.aio.operations.MachineLearningComputeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_available_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AvailableOperations: ...


    class azure.mgmt.machinelearningcompute.aio.operations.OperationalizationClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: OperationalizationCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationalizationCluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OperationalizationCluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                delete_all: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_update_system_services(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, AsyncPollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[UpdateSystemServicesResponse]: ...

        @distributed_trace_async
        async def check_system_services_updates_available(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CheckSystemServicesUpdatesAvailableResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationalizationCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationalizationCluster]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AsyncIterable[OperationalizationCluster]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationalizationClusterCredentials: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: OperationalizationClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationalizationCluster: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationalizationCluster: ...


namespace azure.mgmt.machinelearningcompute.models

    class azure.mgmt.machinelearningcompute.models.AcsClusterProperties(Model):
        agent_count: int
        agent_vm_size: Union[str, AgentVMSizeTypes]
        cluster_fqdn: str
        master_count: int
        orchestrator_properties: KubernetesClusterProperties
        orchestrator_type: Union[str, OrchestratorType]
        system_services: list[SystemService]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                agent_count: int = 2, 
                agent_vm_size: Union[str, AgentVMSizeTypes] = "Standard_D3_v2", 
                master_count: int = 1, 
                orchestrator_properties: Optional[KubernetesClusterProperties] = ..., 
                orchestrator_type: Union[str, OrchestratorType], 
                system_services: Optional[List[SystemService]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.AgentVMSizeTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        STANDARD_A0 = "Standard_A0"
        STANDARD_A1 = "Standard_A1"
        STANDARD_A10 = "Standard_A10"
        STANDARD_A11 = "Standard_A11"
        STANDARD_A2 = "Standard_A2"
        STANDARD_A3 = "Standard_A3"
        STANDARD_A4 = "Standard_A4"
        STANDARD_A5 = "Standard_A5"
        STANDARD_A6 = "Standard_A6"
        STANDARD_A7 = "Standard_A7"
        STANDARD_A8 = "Standard_A8"
        STANDARD_A9 = "Standard_A9"
        STANDARD_D1 = "Standard_D1"
        STANDARD_D11 = "Standard_D11"
        STANDARD_D11_V2 = "Standard_D11_v2"
        STANDARD_D12 = "Standard_D12"
        STANDARD_D12_V2 = "Standard_D12_v2"
        STANDARD_D13 = "Standard_D13"
        STANDARD_D13_V2 = "Standard_D13_v2"
        STANDARD_D14 = "Standard_D14"
        STANDARD_D14_V2 = "Standard_D14_v2"
        STANDARD_D1_V2 = "Standard_D1_v2"
        STANDARD_D2 = "Standard_D2"
        STANDARD_D2_V2 = "Standard_D2_v2"
        STANDARD_D3 = "Standard_D3"
        STANDARD_D3_V2 = "Standard_D3_v2"
        STANDARD_D4 = "Standard_D4"
        STANDARD_D4_V2 = "Standard_D4_v2"
        STANDARD_D5_V2 = "Standard_D5_v2"
        STANDARD_DS1 = "Standard_DS1"
        STANDARD_DS11 = "Standard_DS11"
        STANDARD_DS12 = "Standard_DS12"
        STANDARD_DS13 = "Standard_DS13"
        STANDARD_DS14 = "Standard_DS14"
        STANDARD_DS2 = "Standard_DS2"
        STANDARD_DS3 = "Standard_DS3"
        STANDARD_DS4 = "Standard_DS4"
        STANDARD_G1 = "Standard_G1"
        STANDARD_G2 = "Standard_G2"
        STANDARD_G3 = "Standard_G3"
        STANDARD_G4 = "Standard_G4"
        STANDARD_G5 = "Standard_G5"
        STANDARD_GS1 = "Standard_GS1"
        STANDARD_GS2 = "Standard_GS2"
        STANDARD_GS3 = "Standard_GS3"
        STANDARD_GS4 = "Standard_GS4"
        STANDARD_GS5 = "Standard_GS5"


    class azure.mgmt.machinelearningcompute.models.AppInsightsCredentials(Model):
        app_id: str
        instrumentation_key: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                instrumentation_key: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.AppInsightsProperties(Model):
        resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.AutoScaleConfiguration(Model):
        max_replicas: int
        min_replicas: int
        refresh_period_in_seconds: int
        status: Union[str, Status]
        target_utilization: float

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                max_replicas: int = 100, 
                min_replicas: int = 1, 
                refresh_period_in_seconds: Optional[int] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                target_utilization: Optional[float] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.AvailableOperations(Model):
        value: list[ResourceOperation]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ResourceOperation]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.CheckSystemServicesUpdatesAvailableResponse(Model):
        updates_available: Union[str, UpdatesAvailable]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACS = "ACS"
        LOCAL = "Local"


    class azure.mgmt.machinelearningcompute.models.ContainerRegistryCredentials(Model):
        login_server: str
        password: str
        password2: str
        username: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ContainerRegistryProperties(Model):
        resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ContainerServiceCredentials(Model):
        acs_kube_config: str
        image_pull_secret_name: str
        service_principal_configuration: ServicePrincipalProperties

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ErrorDetail(Model):
        code: str
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                message: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ErrorResponse(Model):
        code: str
        details: list[ErrorDetail]
        message: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                code: str, 
                details: Optional[List[ErrorDetail]] = ..., 
                message: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ErrorResponseWrapper(Model):
        error: ErrorResponse

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponse] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.GlobalServiceConfiguration(Model):
        additional_properties: dict[str, JSON]
        auto_scale: AutoScaleConfiguration
        etag: str
        service_auth: ServiceAuthConfiguration
        ssl: SslConfiguration

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                additional_properties: Optional[Dict[str, JSON]] = ..., 
                auto_scale: Optional[AutoScaleConfiguration] = ..., 
                etag: Optional[str] = ..., 
                service_auth: Optional[ServiceAuthConfiguration] = ..., 
                ssl: Optional[SslConfiguration] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.KubernetesClusterProperties(Model):
        service_principal: ServicePrincipalProperties

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                service_principal: Optional[ServicePrincipalProperties] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.OperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.machinelearningcompute.models.OperationalizationCluster(Resource):
        app_insights: AppInsightsProperties
        cluster_type: Union[str, ClusterType]
        container_registry: ContainerRegistryProperties
        container_service: AcsClusterProperties
        created_on: datetime
        description: str
        global_service_configuration: GlobalServiceConfiguration
        id: str
        location: str
        modified_on: datetime
        name: str
        provisioning_errors: list[ErrorResponseWrapper]
        provisioning_state: Union[str, OperationStatus]
        storage_account: StorageAccountProperties
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                app_insights: Optional[AppInsightsProperties] = ..., 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                container_registry: Optional[ContainerRegistryProperties] = ..., 
                container_service: Optional[AcsClusterProperties] = ..., 
                description: Optional[str] = ..., 
                global_service_configuration: Optional[GlobalServiceConfiguration] = ..., 
                location: str, 
                storage_account: Optional[StorageAccountProperties] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.OperationalizationClusterCredentials(Model):
        app_insights: AppInsightsCredentials
        container_registry: ContainerRegistryCredentials
        container_service: ContainerServiceCredentials
        service_auth_configuration: ServiceAuthConfiguration
        ssl_configuration: SslConfiguration
        storage_account: StorageAccountCredentials

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                app_insights: Optional[AppInsightsCredentials] = ..., 
                container_registry: Optional[ContainerRegistryCredentials] = ..., 
                container_service: Optional[ContainerServiceCredentials] = ..., 
                service_auth_configuration: Optional[ServiceAuthConfiguration] = ..., 
                ssl_configuration: Optional[SslConfiguration] = ..., 
                storage_account: Optional[StorageAccountCredentials] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.OperationalizationClusterUpdateParameters(Model):
        tags: dict[str, str]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.OrchestratorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KUBERNETES = "Kubernetes"
        NONE = "None"


    class azure.mgmt.machinelearningcompute.models.PaginatedOperationalizationClustersList(Model):
        next_link: str
        value: list[OperationalizationCluster]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[OperationalizationCluster]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.Resource(Model):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ResourceOperation(Model):
        display: ResourceOperationDisplay
        name: str
        origin: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                display: Optional[ResourceOperationDisplay] = ..., 
                name: Optional[str] = ..., 
                origin: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ResourceOperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ServiceAuthConfiguration(Model):
        primary_auth_key_hash: str
        secondary_auth_key_hash: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                primary_auth_key_hash: str, 
                secondary_auth_key_hash: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.ServicePrincipalProperties(Model):
        client_id: str
        secret: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                client_id: str, 
                secret: str, 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.SslConfiguration(Model):
        cert: str
        cname: str
        key: str
        status: Union[str, Status]

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                cert: Optional[str] = ..., 
                cname: Optional[str] = ..., 
                key: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.machinelearningcompute.models.StorageAccountCredentials(Model):
        primary_key: str
        resource_id: str
        secondary_key: str

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.StorageAccountProperties(Model):
        resource_id: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ..., 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.SystemService(Model):
        public_ip_address: str
        system_service_type: Union[str, SystemServiceType]
        version: str

        def __eq__(self, other): ...

        def __init__(
                self, 
                *, 
                system_service_type: Union[str, SystemServiceType], 
                **kwargs
            ): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.SystemServiceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BATCH_FRONT_END = "BatchFrontEnd"
        NONE = "None"
        SCORING_FRONT_END = "ScoringFrontEnd"


    class azure.mgmt.machinelearningcompute.models.UpdateSystemServicesResponse(Model):
        update_completed_on: datetime
        update_started_on: datetime
        update_status: Union[str, OperationStatus]

        def __eq__(self, other): ...

        def __init__(self, **kwargs): ...

        def __ne__(self, other): ...

        def __str__(self): ...

        @classmethod
        def deserialize(
                cls, 
                data: str, 
                content_type: str = None
            ): ...

        @classmethod
        def enable_additional_properties_sending(cls): ...

        @classmethod
        def from_dict(
                cls, 
                data: dict, 
                key_extractors = None, 
                content_type: str = None
            ): ...

        @classmethod
        def is_xml_model(cls): ...

        def as_dict(
                self, 
                keep_readonly = True, 
                key_transformer: function = attribute_transformer, 
                **kwargs
            ) -> dict: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs
            ) -> dict: ...


    class azure.mgmt.machinelearningcompute.models.UpdatesAvailable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO = "No"
        YES = "Yes"


namespace azure.mgmt.machinelearningcompute.operations

    class azure.mgmt.machinelearningcompute.operations.MachineLearningComputeOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_available_operations(
                self, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> AvailableOperations: ...


    class azure.mgmt.machinelearningcompute.operations.OperationalizationClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: OperationalizationCluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationalizationCluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OperationalizationCluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                delete_all: Optional[bool] = None, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_update_system_services(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                continuation_token: Optional[str] = ..., 
                polling: Union[bool, PollingMethod] = ..., 
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> LROPoller[UpdateSystemServicesResponse]: ...

        @distributed_trace
        def check_system_services_updates_available(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> CheckSystemServicesUpdatesAvailableResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationalizationCluster: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OperationalizationCluster]: ...

        @distributed_trace
        def list_by_subscription_id(
                self, 
                skiptoken: Optional[str] = None, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> Iterable[OperationalizationCluster]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                *, 
                cls: Optional[callable] = ..., 
                **kwargs: Any
            ) -> OperationalizationClusterCredentials: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: OperationalizationClusterUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationalizationCluster: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationalizationCluster: ...


```