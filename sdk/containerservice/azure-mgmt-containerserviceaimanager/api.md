```py
namespace azure.mgmt.containerserviceaimanager

    class azure.mgmt.containerserviceaimanager.ContainerServiceAIManagerClient: implements ContextManager 
        ai_manager_namespaces: AIManagerNamespacesOperations
        ai_managers: AIManagersOperations
        ai_models: AIModelsOperations
        model_deployments: ModelDeploymentsOperations
        model_sources: ModelSourcesOperations
        operations: Operations

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


namespace azure.mgmt.containerserviceaimanager.aio

    class azure.mgmt.containerserviceaimanager.aio.ContainerServiceAIManagerClient: implements AsyncContextManager 
        ai_manager_namespaces: AIManagerNamespacesOperations
        ai_managers: AIManagersOperations
        ai_models: AIModelsOperations
        model_deployments: ModelDeploymentsOperations
        model_sources: ModelSourcesOperations
        operations: Operations

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


namespace azure.mgmt.containerserviceaimanager.aio.operations

    class azure.mgmt.containerserviceaimanager.aio.operations.AIManagerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: AIManagerNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManagerNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: AIManagerNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManagerNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManagerNamespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AIManagerNamespace: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def list_access_keys(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceAccessInfo: ...

        @distributed_trace
        def list_by_ai_manager(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AIManagerNamespace]: ...

        @distributed_trace_async
        async def list_credential(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def rotate_keys(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceAccessInfo: ...


    class azure.mgmt.containerserviceaimanager.aio.operations.AIManagersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: AIManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManager]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: AIManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManager]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[AIManager]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> AIManager: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AIManager]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AIManager]: ...

        @distributed_trace_async
        async def list_credential(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: AIManagerPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: AIManagerPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...


    class azure.mgmt.containerserviceaimanager.aio.operations.AIModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: CalculateCostRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @overload
        async def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: CalculateCostRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @overload
        async def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'location', 'ai_model_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                location: str, 
                ai_model_name: str, 
                **kwargs: Any
            ) -> AIModel: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AIModel]: ...


    class azure.mgmt.containerserviceaimanager.aio.operations.ModelDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: ModelDeployment, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: ModelDeployment, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'model_deployment_name', 'etag', 'match_condition']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'model_deployment_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                **kwargs: Any
            ) -> ModelDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_ai_manager_namespace(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelDeployment]: ...


    class azure.mgmt.containerserviceaimanager.aio.operations.ModelSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: ModelSource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelSource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: ModelSource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelSource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[ModelSource]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'model_source_name', 'etag', 'match_condition']}, api_versions_list=['2026-05-02-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'model_source_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                **kwargs: Any
            ) -> ModelSource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelSource]: ...


    class azure.mgmt.containerserviceaimanager.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.containerserviceaimanager.models

    class azure.mgmt.containerserviceaimanager.models.AIManager(TrackedResource):
        e_tag: Optional[str]
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AIManagerProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AIManagerProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIManagerNamespace(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[AIManagerNamespaceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AIManagerNamespaceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIManagerNamespaceProperties(_Model):
        annotations: Optional[dict[str, str]]
        labels: Optional[dict[str, str]]
        provisioning_state: Optional[Union[str, AIManagerNamespaceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                annotations: Optional[dict[str, str]] = ..., 
                labels: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIManagerNamespaceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerserviceaimanager.models.AIManagerPatch(_Model):
        identity: Optional[ManagedServiceIdentity]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIManagerProperties(_Model):
        delete_policy: Optional[Union[str, DeletePolicy]]
        managed_resource_group_name: Optional[str]
        provisioning_state: Optional[Union[str, AIManagerProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                delete_policy: Optional[Union[str, DeletePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIManagerProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerserviceaimanager.models.AIModel(ProxyResource):
        id: str
        name: str
        properties: Optional[AIModelProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AIModelProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.AIModelProperties(_Model):
        description: Optional[str]
        model_id: str
        spec: ModelSpec


    class azure.mgmt.containerserviceaimanager.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.containerserviceaimanager.models.AutoscaleProfile(_Model):
        max_replicas: Optional[int]
        min_replicas: int

        @overload
        def __init__(
                self, 
                *, 
                max_replicas: Optional[int] = ..., 
                min_replicas: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.CalculateCostPlan(_Model):
        feasible: bool
        infeasibility_reason: Optional[InfeasibilityReason]
        max_available_replicas: int
        price_as_of: Optional[datetime]
        quantization: Optional[str]
        serving_performance_estimation: Optional[ServingPerformanceEstimation]
        total_hourly_price: Optional[float]
        vm_hourly_price: float
        vm_size: str
        vms_per_replica: int


    class azure.mgmt.containerserviceaimanager.models.CalculateCostRequest(_Model):


    class azure.mgmt.containerserviceaimanager.models.CalculateCostResponse(_Model):
        currency: str
        plans: list[CalculateCostPlan]


    class azure.mgmt.containerserviceaimanager.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.containerserviceaimanager.models.CredentialResult(_Model):
        name: Optional[str]
        value: Optional[bytes]


    class azure.mgmt.containerserviceaimanager.models.CredentialResults(_Model):
        kubeconfigs: Optional[list[CredentialResult]]


    class azure.mgmt.containerserviceaimanager.models.CredentialValue(_Model):
        inline: Optional[InlineCredential]

        @overload
        def __init__(
                self, 
                *, 
                inline: Optional[InlineCredential] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.DeletePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        KEEP = "Keep"


    class azure.mgmt.containerserviceaimanager.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.containerserviceaimanager.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.containerserviceaimanager.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.InfeasibilityReason(_Model):
        code: Union[str, InfeasibleCode]
        message: str


    class azure.mgmt.containerserviceaimanager.models.InfeasibleCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INEFFICIENT_DEPLOYMENT = "InefficientDeployment"
        INSUFFICIENT_QUOTA = "InsufficientQuota"
        REGION_UNAVAILABLE = "RegionUnavailable"


    class azure.mgmt.containerserviceaimanager.models.InlineCredential(_Model):
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.containerserviceaimanager.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.containerserviceaimanager.models.ManualScalingProfile(_Model):
        replicas: int

        @overload
        def __init__(
                self, 
                *, 
                replicas: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelDeployment(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ModelDeploymentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ModelDeploymentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelDeploymentOverrides(_Model):
        values_property: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                values_property: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelDeploymentPerformanceMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED = "Balanced"
        LATENCY = "Latency"
        THROUGHPUT = "Throughput"


    class azure.mgmt.containerserviceaimanager.models.ModelDeploymentProperties(_Model):
        model_resource_id: str
        model_source_resource_id: Optional[str]
        overrides: Optional[ModelDeploymentOverrides]
        performance_mode: Optional[Union[str, ModelDeploymentPerformanceMode]]
        provisioning_state: Optional[Union[str, ModelDeploymentProvisioningState]]
        scale: Optional[ScalingProfile]
        status: Optional[ModelDeploymentStatus]
        vm_size: str

        @overload
        def __init__(
                self, 
                *, 
                model_resource_id: str, 
                model_source_resource_id: Optional[str] = ..., 
                overrides: Optional[ModelDeploymentOverrides] = ..., 
                performance_mode: Optional[Union[str, ModelDeploymentPerformanceMode]] = ..., 
                scale: Optional[ScalingProfile] = ..., 
                vm_size: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelDeploymentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.containerserviceaimanager.models.ModelDeploymentStatus(_Model):
        current_replicas: Optional[int]
        desired_replicas: Optional[int]
        endpoint: Optional[str]
        engine: Optional[str]
        engine_version: Optional[str]
        estimated_provision_time_seconds: Optional[int]
        max_model_len: Optional[int]
        peak_tokens_per_minute: Optional[int]
        quantization: Optional[str]


    class azure.mgmt.containerserviceaimanager.models.ModelSource(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ModelSourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ModelSourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelSourceProperties(_Model):
        credential: Optional[CredentialValue]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        source_type: Union[str, ModelSourceType]

        @overload
        def __init__(
                self, 
                *, 
                credential: Optional[CredentialValue] = ..., 
                description: Optional[str] = ..., 
                source_type: Union[str, ModelSourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ModelSourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HUGGING_FACE = "HuggingFace"


    class azure.mgmt.containerserviceaimanager.models.ModelSpec(_Model):
        is_restricted: bool
        license: Optional[str]
        max_context_length: int


    class azure.mgmt.containerserviceaimanager.models.NamespaceAccessInfo(_Model):
        endpoint: str
        last_rotated_at: Optional[datetime]
        primary_key: str
        secondary_key: str


    class azure.mgmt.containerserviceaimanager.models.Operation(_Model):
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


    class azure.mgmt.containerserviceaimanager.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.containerserviceaimanager.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.containerserviceaimanager.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.containerserviceaimanager.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.containerserviceaimanager.models.ScalingProfile(_Model):
        autoscale: Optional[AutoscaleProfile]
        manual: Optional[ManualScalingProfile]

        @overload
        def __init__(
                self, 
                *, 
                autoscale: Optional[AutoscaleProfile] = ..., 
                manual: Optional[ManualScalingProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.containerserviceaimanager.models.ServingPerformanceEstimation(_Model):
        relative_latency_score: float
        relative_throughput_score: float


    class azure.mgmt.containerserviceaimanager.models.SystemData(_Model):
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


    class azure.mgmt.containerserviceaimanager.models.TrackedResource(Resource):
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


    class azure.mgmt.containerserviceaimanager.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.containerserviceaimanager.operations

    class azure.mgmt.containerserviceaimanager.operations.AIManagerNamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: AIManagerNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManagerNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: AIManagerNamespace, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManagerNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManagerNamespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AIManagerNamespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_access_keys(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceAccessInfo: ...

        @distributed_trace
        def list_by_ai_manager(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AIManagerNamespace]: ...

        @distributed_trace
        def list_credential(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def rotate_keys(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NamespaceAccessInfo: ...


    class azure.mgmt.containerserviceaimanager.operations.AIManagersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: AIManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManager]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: AIManager, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManager]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[AIManager]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> AIManager: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AIManager]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AIManager]: ...

        @distributed_trace
        def list_credential(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> CredentialResults: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: AIManagerPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: AIManagerPatch, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> AIManager: ...


    class azure.mgmt.containerserviceaimanager.operations.AIModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: CalculateCostRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @overload
        def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: CalculateCostRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @overload
        def calculate_cost(
                self, 
                location: str, 
                ai_model_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateCostResponse: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'location', 'ai_model_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                location: str, 
                ai_model_name: str, 
                **kwargs: Any
            ) -> AIModel: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[AIModel]: ...


    class azure.mgmt.containerserviceaimanager.operations.ModelDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: ModelDeployment, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: ModelDeployment, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'model_deployment_name', 'etag', 'match_condition']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'model_deployment_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                model_deployment_name: str, 
                **kwargs: Any
            ) -> ModelDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'namespace_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list_by_ai_manager_namespace(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelDeployment]: ...


    class azure.mgmt.containerserviceaimanager.operations.ModelSourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: ModelSource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelSource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: ModelSource, 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelSource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[ModelSource]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'model_source_name', 'etag', 'match_condition']}, api_versions_list=['2026-05-02-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                *, 
                etag: Optional[str] = ..., 
                match_condition: Optional[MatchConditions] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'model_source_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def get(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                model_source_name: str, 
                **kwargs: Any
            ) -> ModelSource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-02-preview', params_added_on={'2026-05-02-preview': ['api_version', 'subscription_id', 'resource_group_name', 'ai_manager_name', 'accept']}, api_versions_list=['2026-05-02-preview'])
        def list(
                self, 
                resource_group_name: str, 
                ai_manager_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelSource]: ...


    class azure.mgmt.containerserviceaimanager.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.containerserviceaimanager.types

    class azure.mgmt.containerserviceaimanager.types.AIManager(TrackedResource):
        key "eTag": str
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AIManagerProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AIManagerProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerserviceaimanager.types.AIManagerNamespace(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('AIManagerNamespaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: AIManagerNamespaceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.types.AIManagerNamespaceProperties(TypedDict, total=False):
        key "provisioningState": Union[str, AIManagerNamespaceProvisioningState]
        annotations: dict[str, str]
        labels: dict[str, str]
        provisioning_state: Union[str, AIManagerNamespaceProvisioningState]


    class azure.mgmt.containerserviceaimanager.types.AIManagerPatch(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        identity: ManagedServiceIdentity
        tags: dict[str, str]


    class azure.mgmt.containerserviceaimanager.types.AIManagerProperties(TypedDict, total=False):
        key "deletePolicy": Union[str, DeletePolicy]
        key "managedResourceGroupName": str
        key "provisioningState": Union[str, AIManagerProvisioningState]
        delete_policy: Union[str, DeletePolicy]
        managed_resource_group_name: str
        provisioning_state: Union[str, AIManagerProvisioningState]


    class azure.mgmt.containerserviceaimanager.types.AutoscaleProfile(TypedDict, total=False):
        key "maxReplicas": int
        key "minReplicas": Required[int]
        max_replicas: int
        min_replicas: int


    class azure.mgmt.containerserviceaimanager.types.CalculateCostRequest(TypedDict, total=False):


    class azure.mgmt.containerserviceaimanager.types.CredentialValue(TypedDict, total=False):
        key "inline": ForwardRef('InlineCredential', module='types')
        inline: InlineCredential


    class azure.mgmt.containerserviceaimanager.types.InlineCredential(TypedDict, total=False):
        key "value": Required[str]
        value: str


    class azure.mgmt.containerserviceaimanager.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.containerserviceaimanager.types.ManualScalingProfile(TypedDict, total=False):
        key "replicas": Required[int]
        replicas: int


    class azure.mgmt.containerserviceaimanager.types.ModelDeployment(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ModelDeploymentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: ModelDeploymentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.types.ModelDeploymentOverrides(TypedDict, total=False):
        values: dict[str, str]
        values_property: dict[str, str]


    class azure.mgmt.containerserviceaimanager.types.ModelDeploymentProperties(TypedDict, total=False):
        key "modelResourceId": Required[str]
        key "modelSourceResourceId": str
        key "overrides": ForwardRef('ModelDeploymentOverrides', module='types')
        key "performanceMode": Union[str, ModelDeploymentPerformanceMode]
        key "provisioningState": Union[str, ModelDeploymentProvisioningState]
        key "scale": ForwardRef('ScalingProfile', module='types')
        key "status": ForwardRef('ModelDeploymentStatus', module='types')
        key "vmSize": Required[str]
        model_resource_id: str
        model_source_resource_id: str
        overrides: ModelDeploymentOverrides
        performance_mode: Union[str, ModelDeploymentPerformanceMode]
        provisioning_state: Union[str, ModelDeploymentProvisioningState]
        scale: ScalingProfile
        status: ModelDeploymentStatus
        vm_size: str


    class azure.mgmt.containerserviceaimanager.types.ModelDeploymentStatus(TypedDict, total=False):
        key "currentReplicas": int
        key "desiredReplicas": int
        key "endpoint": str
        key "engine": str
        key "engineVersion": str
        key "estimatedProvisionTimeSeconds": int
        key "maxModelLen": int
        key "peakTokensPerMinute": int
        key "quantization": str
        current_replicas: int
        desired_replicas: int
        endpoint: str
        engine: str
        engine_version: str
        estimated_provision_time_seconds: int
        max_model_len: int
        peak_tokens_per_minute: int
        quantization: str


    class azure.mgmt.containerserviceaimanager.types.ModelSource(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ModelSourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        e_tag: str
        id: str
        name: str
        properties: ModelSourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.types.ModelSourceProperties(TypedDict, total=False):
        key "credential": ForwardRef('CredentialValue', module='types')
        key "description": str
        key "provisioningState": Union[str, ResourceProvisioningState]
        key "sourceType": Required[Union[str, ModelSourceType]]
        credential: CredentialValue
        description: str
        provisioning_state: Union[str, ResourceProvisioningState]
        source_type: Union[str, ModelSourceType]


    class azure.mgmt.containerserviceaimanager.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.containerserviceaimanager.types.ScalingProfile(TypedDict, total=False):
        key "autoscale": ForwardRef('AutoscaleProfile', module='types')
        key "manual": ForwardRef('ManualScalingProfile', module='types')
        autoscale: AutoscaleProfile
        manual: ManualScalingProfile


    class azure.mgmt.containerserviceaimanager.types.SystemData(TypedDict, total=False):
        key "createdAt": str
        key "createdBy": str
        key "createdByType": Union[str, CreatedByType]
        key "lastModifiedAt": str
        key "lastModifiedBy": str
        key "lastModifiedByType": Union[str, CreatedByType]
        created_at: str
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: str
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]


    class azure.mgmt.containerserviceaimanager.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.containerserviceaimanager.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


```