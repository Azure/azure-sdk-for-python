```py
namespace azure.mgmt.cognitiveservices

    class azure.mgmt.cognitiveservices.CognitiveServicesManagementClient(_CognitiveServicesManagementClientOperationsMixin): implements ContextManager 
        account_capability_hosts: AccountCapabilityHostsOperations
        account_connections: AccountConnectionsOperations
        accounts: AccountsOperations
        agent_applications: AgentApplicationsOperations
        agent_deployments: AgentDeploymentsOperations
        arc_deployments: ArcDeploymentsOperations
        commitment_plans: CommitmentPlansOperations
        commitment_tiers: CommitmentTiersOperations
        compute_operations: ComputeOperationsOperations
        computes: ComputesOperations
        defender_for_ai_settings: DefenderForAISettingsOperations
        deleted_accounts: DeletedAccountsOperations
        deployments: DeploymentsOperations
        encryption_scopes: EncryptionScopesOperations
        location_based_model_capacities: LocationBasedModelCapacitiesOperations
        managed_compute_capacities: ManagedComputeCapacitiesOperations
        managed_compute_deployments: ManagedComputeDeploymentsOperations
        managed_compute_usages_operation_group: ManagedComputeUsagesOperationGroupOperations
        managed_network_provisions: ManagedNetworkProvisionsOperations
        managed_network_settings: ManagedNetworkSettingsOperations
        model_capacities: ModelCapacitiesOperations
        models: ModelsOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        outbound_rule: OutboundRuleOperations
        outbound_rules: OutboundRulesOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        project_capability_hosts: ProjectCapabilityHostsOperations
        project_connections: ProjectConnectionsOperations
        projects: ProjectsOperations
        quota_tiers: QuotaTiersOperations
        rai_blocklist_items: RaiBlocklistItemsOperations
        rai_blocklists: RaiBlocklistsOperations
        rai_content_filters: RaiContentFiltersOperations
        rai_external_safety_provider: RaiExternalSafetyProviderOperations
        rai_external_safety_providers: RaiExternalSafetyProvidersOperations
        rai_policies: RaiPoliciesOperations
        rai_tool_labels: RaiToolLabelsOperations
        rai_topics: RaiTopicsOperations
        resource_skus: ResourceSkusOperations
        subscription_rai_policy: SubscriptionRaiPolicyOperations
        test_rai_external_safety_provider: TestRaiExternalSafetyProviderOperations
        usages: UsagesOperations
        workbenches: WorkbenchesOperations

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

        @overload
        def calculate_model_capacity(
                self, 
                parameters: CalculateModelCapacityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        def calculate_model_capacity(
                self, 
                parameters: CalculateModelCapacityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        def calculate_model_capacity(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        def check_domain_availability(
                self, 
                parameters: CheckDomainAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        def check_domain_availability(
                self, 
                parameters: CheckDomainAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        def check_domain_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        def check_sku_availability(
                self, 
                location: str, 
                parameters: CheckSkuAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        @overload
        def check_sku_availability(
                self, 
                location: str, 
                parameters: CheckSkuAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        @overload
        def check_sku_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.cognitiveservices.aio

    class azure.mgmt.cognitiveservices.aio.CognitiveServicesManagementClient(_CognitiveServicesManagementClientOperationsMixin): implements AsyncContextManager 
        account_capability_hosts: AccountCapabilityHostsOperations
        account_connections: AccountConnectionsOperations
        accounts: AccountsOperations
        agent_applications: AgentApplicationsOperations
        agent_deployments: AgentDeploymentsOperations
        arc_deployments: ArcDeploymentsOperations
        commitment_plans: CommitmentPlansOperations
        commitment_tiers: CommitmentTiersOperations
        compute_operations: ComputeOperationsOperations
        computes: ComputesOperations
        defender_for_ai_settings: DefenderForAISettingsOperations
        deleted_accounts: DeletedAccountsOperations
        deployments: DeploymentsOperations
        encryption_scopes: EncryptionScopesOperations
        location_based_model_capacities: LocationBasedModelCapacitiesOperations
        managed_compute_capacities: ManagedComputeCapacitiesOperations
        managed_compute_deployments: ManagedComputeDeploymentsOperations
        managed_compute_usages_operation_group: ManagedComputeUsagesOperationGroupOperations
        managed_network_provisions: ManagedNetworkProvisionsOperations
        managed_network_settings: ManagedNetworkSettingsOperations
        model_capacities: ModelCapacitiesOperations
        models: ModelsOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        outbound_rule: OutboundRuleOperations
        outbound_rules: OutboundRulesOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        project_capability_hosts: ProjectCapabilityHostsOperations
        project_connections: ProjectConnectionsOperations
        projects: ProjectsOperations
        quota_tiers: QuotaTiersOperations
        rai_blocklist_items: RaiBlocklistItemsOperations
        rai_blocklists: RaiBlocklistsOperations
        rai_content_filters: RaiContentFiltersOperations
        rai_external_safety_provider: RaiExternalSafetyProviderOperations
        rai_external_safety_providers: RaiExternalSafetyProvidersOperations
        rai_policies: RaiPoliciesOperations
        rai_tool_labels: RaiToolLabelsOperations
        rai_topics: RaiTopicsOperations
        resource_skus: ResourceSkusOperations
        subscription_rai_policy: SubscriptionRaiPolicyOperations
        test_rai_external_safety_provider: TestRaiExternalSafetyProviderOperations
        usages: UsagesOperations
        workbenches: WorkbenchesOperations

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

        @overload
        async def calculate_model_capacity(
                self, 
                parameters: CalculateModelCapacityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        async def calculate_model_capacity(
                self, 
                parameters: CalculateModelCapacityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        async def calculate_model_capacity(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CalculateModelCapacityResult: ...

        @overload
        async def check_domain_availability(
                self, 
                parameters: CheckDomainAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        async def check_domain_availability(
                self, 
                parameters: CheckDomainAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        async def check_domain_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DomainAvailability: ...

        @overload
        async def check_sku_availability(
                self, 
                location: str, 
                parameters: CheckSkuAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        @overload
        async def check_sku_availability(
                self, 
                location: str, 
                parameters: CheckSkuAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        @overload
        async def check_sku_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuAvailabilityListResult: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.cognitiveservices.aio.operations

    class azure.mgmt.cognitiveservices.aio.operations.AccountCapabilityHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: CapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapabilityHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: CapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapabilityHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CapabilityHost]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> CapabilityHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CapabilityHost]: ...


    class azure.mgmt.cognitiveservices.aio.operations.AccountConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                category: Optional[str] = ..., 
                include_all: bool = False, 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectionPropertiesV2BasicResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...


    class azure.mgmt.cognitiveservices.aio.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Account]: ...

        @overload
        async def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: EvaluateDeploymentPoliciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @overload
        async def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: EvaluateDeploymentPoliciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @overload
        async def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Account]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Account]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ApiKeys: ...

        @distributed_trace
        def list_models(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AccountModel]: ...

        @distributed_trace_async
        async def list_skus(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AccountSkuListResult: ...

        @distributed_trace_async
        async def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> UsageListResult: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...

        @overload
        async def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...


    class azure.mgmt.cognitiveservices.aio.operations.AgentApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: AgentApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: AgentApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentApplication]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def enable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AgentApplication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                *, 
                count: int = 30, 
                names: Optional[List[str]] = ..., 
                order_by: Optional[str] = ..., 
                order_by_asc: bool = False, 
                search_text: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentApplication]: ...

        @distributed_trace_async
        async def list_agents(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AgentReferenceResourceArmPaginatedResult: ...


    class azure.mgmt.cognitiveservices.aio.operations.AgentDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: AgentDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: AgentDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AgentDeployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AgentDeployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                *, 
                count: int = 30, 
                names: Optional[List[str]] = ..., 
                order_by: Optional[str] = ..., 
                order_by_asc: bool = False, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AgentDeployment]: ...

        @distributed_trace_async
        async def start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.cognitiveservices.aio.operations.ArcDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ArcDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ArcDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name']}, api_versions_list=['2026-07-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: ArcDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: ArcDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ArcDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name', 'accept']}, api_versions_list=['2026-07-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ArcDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ArcDeployment]: ...


    class azure.mgmt.cognitiveservices.aio.operations.CommitmentPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: CommitmentPlanAccountAssociation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        async def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: CommitmentPlanAccountAssociation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        async def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        async def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @overload
        async def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @overload
        async def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @overload
        async def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @overload
        async def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CommitmentPlan]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace_async
        async def get_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                **kwargs: Any
            ) -> CommitmentPlanAccountAssociation: ...

        @distributed_trace_async
        async def get_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommitmentPlan]: ...

        @distributed_trace
        def list_associations(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommitmentPlanAccountAssociation]: ...

        @distributed_trace
        def list_plans_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommitmentPlan]: ...

        @distributed_trace
        def list_plans_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[CommitmentPlan]: ...


    class azure.mgmt.cognitiveservices.aio.operations.CommitmentTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CommitmentTier]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ComputeOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-01-15-preview', '2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ComputeOperationStatus: ...


    class azure.mgmt.cognitiveservices.aio.operations.ComputesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: Compute, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Compute]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: Compute, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Compute]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Compute]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_restart(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> Compute: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Compute]: ...


    class azure.mgmt.cognitiveservices.aio.operations.DefenderForAISettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DefenderForAISetting]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...


    class azure.mgmt.cognitiveservices.aio.operations.DeletedAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_purge(
                self, 
                location: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Account]: ...


    class azure.mgmt.cognitiveservices.aio.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Deployment]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Deployment]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuResource]: ...

        @distributed_trace_async
        async def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace_async
        async def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...


    class azure.mgmt.cognitiveservices.aio.operations.EncryptionScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EncryptionScope]: ...


    class azure.mgmt.cognitiveservices.aio.operations.LocationBasedModelCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                model_format: str, 
                model_name: str, 
                model_version: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelCapacityListResultValueItem]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ManagedComputeCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'offer', 'accelerator_type', 'deployment_id', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                *, 
                accelerator_type: Optional[str] = ..., 
                deployment_id: Optional[str] = ..., 
                offer: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedComputeCapacity]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ManagedComputeDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ManagedComputeDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ManagedComputeDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: PatchResourceSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: PatchResourceSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedComputeDeployment]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ManagedComputeDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedComputeDeployment]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ManagedComputeUsagesOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedComputeUsage]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ManagedNetworkProvisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkProvisionOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkProvisionStatus]: ...

        @overload
        async def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkProvisionOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkProvisionStatus]: ...

        @overload
        async def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkProvisionStatus]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ManagedNetworkSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'managed_network_name']}, api_versions_list=['2026-01-15-preview', '2026-03-01', '2026-03-15-preview', '2026-05-01', '2026-05-15-preview', '2026-07-01', '2026-07-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkSettingsPropertiesBasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkSettingsPropertiesBasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsPropertiesBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsPropertiesBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        async def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> ManagedNetworkSettingsPropertiesBasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagedNetworkSettingsPropertiesBasicResource]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ModelCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                model_format: str, 
                model_name: str, 
                model_version: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ModelCapacityListResultValueItem]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Model]: ...


    class azure.mgmt.cognitiveservices.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                nsp_configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                nsp_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.cognitiveservices.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.cognitiveservices.aio.operations.OutboundRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: OutboundRuleBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundRuleBasicResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: OutboundRuleBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundRuleBasicResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundRuleBasicResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> OutboundRuleBasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[OutboundRuleBasicResource]: ...


    class azure.mgmt.cognitiveservices.aio.operations.OutboundRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[OutboundRuleBasicResource]]: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[OutboundRuleBasicResource]]: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AsyncItemPaged[OutboundRuleBasicResource]]: ...


    class azure.mgmt.cognitiveservices.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.cognitiveservices.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.cognitiveservices.aio.operations.ProjectCapabilityHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: ProjectCapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectCapabilityHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: ProjectCapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectCapabilityHost]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProjectCapabilityHost]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> ProjectCapabilityHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectCapabilityHost]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ProjectConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                *, 
                category: Optional[str] = ..., 
                include_all: bool = False, 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConnectionPropertiesV2BasicResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...


    class azure.mgmt.cognitiveservices.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Project]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...


    class azure.mgmt.cognitiveservices.aio.operations.QuotaTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        async def create_or_update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        async def create_or_update(
                self, 
                default: str, 
                tier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @distributed_trace_async
        async def get(
                self, 
                default: str, 
                **kwargs: Any
            ) -> QuotaTier: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[QuotaTier]: ...

        @overload
        async def update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        async def update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        async def update(
                self, 
                default: str, 
                tier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiBlocklistItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: List[RaiBlocklistItemBulkRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        async def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: List[RaiBlocklistItemBulkRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        async def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        async def batch_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items_names: List[str], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def batch_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items_names: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: RaiBlocklistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: RaiBlocklistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiBlocklistItem]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiBlocklistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: RaiBlocklist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: RaiBlocklist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiBlocklist]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiContentFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                filter_name: str, 
                **kwargs: Any
            ) -> RaiContentFilter: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiContentFilter]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiExternalSafetyProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                safety_provider_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        async def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        async def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @distributed_trace_async
        async def get(
                self, 
                safety_provider_name: str, 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiExternalSafetyProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[RaiExternalSafetyProviderSchema]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiPolicy]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiToolLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: RaiToolLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: RaiToolLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiToolLabel]: ...


    class azure.mgmt.cognitiveservices.aio.operations.RaiTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: RaiTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: RaiTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                **kwargs: Any
            ) -> RaiTopic: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RaiTopic]: ...


    class azure.mgmt.cognitiveservices.aio.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.cognitiveservices.aio.operations.SubscriptionRaiPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        async def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        async def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace_async
        async def get(
                self, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> RaiPolicy: ...


    class azure.mgmt.cognitiveservices.aio.operations.TestRaiExternalSafetyProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...


    class azure.mgmt.cognitiveservices.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


    class azure.mgmt.cognitiveservices.aio.operations.WorkbenchesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_restart(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def begin_stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Workbench]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> Workbench: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Workbench]: ...


namespace azure.mgmt.cognitiveservices.models

    class azure.mgmt.cognitiveservices.models.AADAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='AAD'):
        auth_type: Literal[ConnectionAuthType.AAD]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AbusePenalty(_Model):
        action: Optional[Union[str, AbusePenaltyAction]]
        expiration: Optional[datetime]
        rate_limit_percentage: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, AbusePenaltyAction]] = ..., 
                expiration: Optional[datetime] = ..., 
                rate_limit_percentage: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AbusePenaltyAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCK = "Block"
        THROTTLE = "Throttle"


    class azure.mgmt.cognitiveservices.models.AccessKeyAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='AccessKey'):
        auth_type: Literal[ConnectionAuthType.ACCESS_KEY]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionAccessKey]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionAccessKey] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Account(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[AccountProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[AccountProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AccountKeyAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='AccountKey'):
        auth_type: Literal[ConnectionAuthType.ACCOUNT_KEY]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionAccountKey]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionAccountKey] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AccountModel(DeploymentModel):
        base_model: Optional[DeploymentModel]
        call_rate_limit: CallRateLimit
        capabilities: Optional[dict[str, str]]
        deprecation: Optional[ModelDeprecationInfo]
        finetune_capabilities: Optional[dict[str, str]]
        format: str
        is_default_version: Optional[bool]
        lifecycle_status: Optional[Union[str, ModelLifecycleStatus]]
        max_capacity: Optional[int]
        model_catalog_asset_id: Optional[str]
        name: str
        publisher: str
        replacement_config: Optional[ReplacementConfig]
        skus: Optional[list[ModelSku]]
        source: str
        source_account: str
        system_data: Optional[SystemData]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                base_model: Optional[DeploymentModel] = ..., 
                capabilities: Optional[dict[str, str]] = ..., 
                deprecation: Optional[ModelDeprecationInfo] = ..., 
                finetune_capabilities: Optional[dict[str, str]] = ..., 
                format: Optional[str] = ..., 
                is_default_version: Optional[bool] = ..., 
                lifecycle_status: Optional[Union[str, ModelLifecycleStatus]] = ..., 
                max_capacity: Optional[int] = ..., 
                model_catalog_asset_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                replacement_config: Optional[ReplacementConfig] = ..., 
                skus: Optional[list[ModelSku]] = ..., 
                source: Optional[str] = ..., 
                source_account: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AccountProperties(_Model):
        a365_logging_enabled: Optional[bool]
        abuse_penalty: Optional[AbusePenalty]
        agent_hosting_configurations: Optional[list[AgentHostingConfiguration]]
        allow_project_management: Optional[bool]
        allowed_fqdn_list: Optional[list[str]]
        aml_workspace: Optional[UserOwnedAmlWorkspace]
        api_properties: Optional[ApiProperties]
        associated_projects: Optional[list[str]]
        call_rate_limit: Optional[CallRateLimit]
        capabilities: Optional[list[SkuCapability]]
        capability_settings: Optional[CapabilitySettings]
        commitment_plan_associations: Optional[list[CommitmentPlanAssociation]]
        custom_sub_domain_name: Optional[str]
        date_created: Optional[str]
        default_project: Optional[str]
        deletion_date: Optional[str]
        disable_local_auth: Optional[bool]
        dynamic_throttling_enabled: Optional[bool]
        encryption: Optional[Encryption]
        endpoint: Optional[str]
        endpoints: Optional[dict[str, str]]
        foundry_auto_upgrade: Optional[FoundryAutoUpgrade]
        internal_id: Optional[str]
        is_migrated: Optional[bool]
        locations: Optional[MultiRegionSettings]
        migration_token: Optional[str]
        network_acls: Optional[NetworkRuleSet]
        network_injections: Optional[list[NetworkInjection]]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        quota_limit: Optional[QuotaLimit]
        rai_monitor_config: Optional[RaiMonitorConfig]
        restore: Optional[bool]
        restrict_outbound_network_access: Optional[bool]
        scheduled_purge_date: Optional[str]
        sku_change_info: Optional[SkuChangeInfo]
        stored_completions_disabled: Optional[bool]
        user_owned_storage: Optional[list[UserOwnedStorage]]

        @overload
        def __init__(
                self, 
                *, 
                a365_logging_enabled: Optional[bool] = ..., 
                agent_hosting_configurations: Optional[list[AgentHostingConfiguration]] = ..., 
                allow_project_management: Optional[bool] = ..., 
                allowed_fqdn_list: Optional[list[str]] = ..., 
                aml_workspace: Optional[UserOwnedAmlWorkspace] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                associated_projects: Optional[list[str]] = ..., 
                capability_settings: Optional[CapabilitySettings] = ..., 
                custom_sub_domain_name: Optional[str] = ..., 
                default_project: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                dynamic_throttling_enabled: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                foundry_auto_upgrade: Optional[FoundryAutoUpgrade] = ..., 
                locations: Optional[MultiRegionSettings] = ..., 
                migration_token: Optional[str] = ..., 
                network_acls: Optional[NetworkRuleSet] = ..., 
                network_injections: Optional[list[NetworkInjection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                rai_monitor_config: Optional[RaiMonitorConfig] = ..., 
                restore: Optional[bool] = ..., 
                restrict_outbound_network_access: Optional[bool] = ..., 
                stored_completions_disabled: Optional[bool] = ..., 
                user_owned_storage: Optional[list[UserOwnedStorage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AccountSku(_Model):
        resource_type: Optional[str]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                resource_type: Optional[str] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AccountSkuListResult(_Model):
        value: Optional[list[AccountSku]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[AccountSku]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.cognitiveservices.models.AgentApplication(ProxyResource):
        id: str
        name: str
        properties: AgenticApplicationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: AgenticApplicationProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentDeployment(ProxyResource):
        id: str
        name: str
        properties: AgentDeploymentProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: AgentDeploymentProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentDeploymentProperties(ResourceBase):
        agents: Optional[list[VersionedAgentReference]]
        deployment_id: Optional[str]
        deployment_type: str
        description: str
        display_name: Optional[str]
        protocols: Optional[list[AgentProtocolVersion]]
        provisioning_state: Optional[Union[str, AgentDeploymentProvisioningState]]
        state: Optional[Union[str, AgentDeploymentState]]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                agents: Optional[list[VersionedAgentReference]] = ..., 
                deployment_id: Optional[str] = ..., 
                deployment_type: str, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                protocols: Optional[list[AgentProtocolVersion]] = ..., 
                state: Optional[Union[str, AgentDeploymentState]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentDeploymentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.AgentDeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.AgentDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        HOSTED = "Hosted"
        MANAGED = "Managed"


    class azure.mgmt.cognitiveservices.models.AgentHostingConfiguration(_Model):
        hosting_type: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                hosting_type: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentHostingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_CLUSTER = "ManagedCluster"


    class azure.mgmt.cognitiveservices.models.AgentProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        A2_A = "A2A"
        AGENT = "Agent"
        RESPONSES = "Responses"


    class azure.mgmt.cognitiveservices.models.AgentProtocolVersion(_Model):
        protocol: Optional[Union[str, AgentProtocol]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                protocol: Optional[Union[str, AgentProtocol]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentReference(ProxyResource):
        id: str
        name: str
        properties: AgentReferenceProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: AgentReferenceProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentReferenceProperties(_Model):
        agent_id: Optional[str]
        agent_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgentReferenceResourceArmPaginatedResult(_Model):
        next_link: Optional[str]
        value: Optional[list[AgentReference]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[AgentReference]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgenticApplicationProperties(ResourceBase):
        agent_identity_blueprint: Optional[AssignedIdentity]
        agents: Optional[list[AgentReferenceProperties]]
        authorization_policy: Optional[ApplicationAuthorizationPolicy]
        base_url: Optional[str]
        default_instance_identity: Optional[AssignedIdentity]
        description: str
        display_name: Optional[str]
        is_enabled: Optional[bool]
        provisioning_state: Optional[Union[str, AgenticApplicationProvisioningState]]
        tags: dict[str, str]
        traffic_routing_policy: Optional[ApplicationTrafficRoutingPolicy]

        @overload
        def __init__(
                self, 
                *, 
                agent_identity_blueprint: Optional[AssignedIdentity] = ..., 
                agents: Optional[list[AgentReferenceProperties]] = ..., 
                authorization_policy: Optional[ApplicationAuthorizationPolicy] = ..., 
                base_url: Optional[str] = ..., 
                default_instance_identity: Optional[AssignedIdentity] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                traffic_routing_policy: Optional[ApplicationTrafficRoutingPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AgenticApplicationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.ApiKeyAuthConnectionProperties(ConnectionPropertiesV2, discriminator='ApiKey'):
        auth_type: Literal[ConnectionAuthType.API_KEY]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionApiKey]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionApiKey] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ApiKeys(_Model):
        key1: Optional[str]
        key2: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key1: Optional[str] = ..., 
                key2: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ApiProperties(_Model):
        aad_client_id: Optional[str]
        aad_tenant_id: Optional[str]
        event_hub_connection_string: Optional[str]
        qna_azure_search_endpoint_id: Optional[str]
        qna_azure_search_endpoint_key: Optional[str]
        qna_runtime_endpoint: Optional[str]
        statistics_enabled: Optional[bool]
        storage_account_connection_string: Optional[str]
        super_user: Optional[str]
        website_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aad_client_id: Optional[str] = ..., 
                aad_tenant_id: Optional[str] = ..., 
                event_hub_connection_string: Optional[str] = ..., 
                qna_azure_search_endpoint_id: Optional[str] = ..., 
                qna_azure_search_endpoint_key: Optional[str] = ..., 
                qna_runtime_endpoint: Optional[str] = ..., 
                statistics_enabled: Optional[bool] = ..., 
                storage_account_connection_string: Optional[str] = ..., 
                super_user: Optional[str] = ..., 
                website_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ApplicationAuthorizationPolicy(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ApplicationTrafficRoutingPolicy(_Model):
        protocol: Optional[Union[str, TrafficRoutingProtocol]]
        rules: Optional[list[TrafficRoutingRule]]

        @overload
        def __init__(
                self, 
                *, 
                protocol: Optional[Union[str, TrafficRoutingProtocol]] = ..., 
                rules: Optional[list[TrafficRoutingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeployment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: ArcDeploymentProperties
        sku: ArcDeploymentSku
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ArcDeploymentProperties, 
                sku: ArcDeploymentSku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CPU = "cpu"
        GPU = "gpu"


    class azure.mgmt.cognitiveservices.models.ArcDeploymentCpuMemoryResourceRequirements(_Model):
        cpu: str
        memory: str

        @overload
        def __init__(
                self, 
                *, 
                cpu: str, 
                memory: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentKubernetesResources(_Model):
        limits: Optional[ArcDeploymentResourceRequirements]
        requests: Optional[ArcDeploymentCpuMemoryResourceRequirements]

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[ArcDeploymentResourceRequirements] = ..., 
                requests: Optional[ArcDeploymentCpuMemoryResourceRequirements] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentModel(_Model):
        format: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                format: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentPatchCpuMemoryResourceRequirements(_Model):
        cpu: Optional[str]
        memory: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[str] = ..., 
                memory: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentPatchKubernetesResources(_Model):
        limits: Optional[ArcDeploymentResourceRequirements]
        requests: Optional[ArcDeploymentPatchCpuMemoryResourceRequirements]

        @overload
        def __init__(
                self, 
                *, 
                limits: Optional[ArcDeploymentResourceRequirements] = ..., 
                requests: Optional[ArcDeploymentPatchCpuMemoryResourceRequirements] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentProperties(_Model):
        capabilities: Optional[dict[str, str]]
        compute: Union[str, ArcDeploymentComputeType]
        deployment_state: Optional[Union[str, DeploymentState]]
        deployment_template: Optional[str]
        extension_id: str
        inference_endpoint: Optional[str]
        model: ArcDeploymentModel
        node_selector: Optional[dict[str, str]]
        provisioning_details: Optional[ArcDeploymentProvisioningDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rai_policy_name: Optional[str]
        replicas: int
        resources: ArcDeploymentKubernetesResources
        runtime: Union[str, ArcDeploymentRuntime]
        vllm_parameters: Optional[ArcDeploymentVllmParameters]

        @overload
        def __init__(
                self, 
                *, 
                compute: Union[str, ArcDeploymentComputeType], 
                deployment_state: Optional[Union[str, DeploymentState]] = ..., 
                deployment_template: Optional[str] = ..., 
                extension_id: str, 
                model: ArcDeploymentModel, 
                node_selector: Optional[dict[str, str]] = ..., 
                rai_policy_name: Optional[str] = ..., 
                replicas: int, 
                resources: ArcDeploymentKubernetesResources, 
                runtime: Union[str, ArcDeploymentRuntime]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentProvisioningDetails(_Model):
        last_operation_timestamp: Optional[datetime]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_operation_timestamp: Optional[datetime] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentResourceRequirements(_Model):
        cpu: Optional[str]
        gpu: Optional[int]
        memory: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cpu: Optional[str] = ..., 
                gpu: Optional[int] = ..., 
                memory: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentRuntime(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONNX = "onnx-genai"
        VLLM = "vllm"


    class azure.mgmt.cognitiveservices.models.ArcDeploymentSku(_Model):
        name: Union[str, ArcDeploymentSkuName]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, ArcDeploymentSkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC = "Arc"


    class azure.mgmt.cognitiveservices.models.ArcDeploymentUpdate(_Model):
        properties: Optional[ArcDeploymentUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArcDeploymentUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentUpdateProperties(_Model):
        node_selector: Optional[dict[str, str]]
        replicas: Optional[int]
        resources: Optional[ArcDeploymentPatchKubernetesResources]

        @overload
        def __init__(
                self, 
                *, 
                node_selector: Optional[dict[str, str]] = ..., 
                replicas: Optional[int] = ..., 
                resources: Optional[ArcDeploymentPatchKubernetesResources] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ArcDeploymentVllmParameters(_Model):
        enforce_eager: Optional[bool]
        gpu_memory_utilization: Optional[float]
        max_model_len: Optional[int]
        tensor_parallel_size: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enforce_eager: Optional[bool] = ..., 
                gpu_memory_utilization: Optional[float] = ..., 
                max_model_len: Optional[int] = ..., 
                tensor_parallel_size: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.AssignedIdentity(_Model):
        client_id: str
        kind: Union[str, IdentityKind]
        principal_id: str
        provisioning_state: Optional[Union[str, IdentityProvisioningState]]
        subject: Optional[str]
        tenant_id: str
        type: Union[str, IdentityManagementType]

        @overload
        def __init__(
                self, 
                *, 
                client_id: str, 
                kind: Union[str, IdentityKind], 
                principal_id: str, 
                subject: Optional[str] = ..., 
                tenant_id: str, 
                type: Union[str, IdentityManagementType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.BillingMeterInfo(_Model):
        meter_id: Optional[str]
        name: Optional[str]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                meter_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.BuiltInAuthorizationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANNELS = "Channels"
        CUSTOM = "Custom"
        DEFAULT = "Default"
        ORGANIZATION_SCOPE = "OrganizationScope"


    class azure.mgmt.cognitiveservices.models.ByPassSelection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_SERVICES = "AzureServices"
        NONE = "None"


    class azure.mgmt.cognitiveservices.models.CalculateModelCapacityParameter(_Model):
        model: Optional[DeploymentModel]
        sku_name: Optional[str]
        workloads: Optional[list[ModelCapacityCalculatorWorkload]]

        @overload
        def __init__(
                self, 
                *, 
                model: Optional[DeploymentModel] = ..., 
                sku_name: Optional[str] = ..., 
                workloads: Optional[list[ModelCapacityCalculatorWorkload]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CalculateModelCapacityResult(_Model):
        estimated_capacity: Optional[CalculateModelCapacityResultEstimatedCapacity]
        model: Optional[DeploymentModel]
        sku_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                estimated_capacity: Optional[CalculateModelCapacityResultEstimatedCapacity] = ..., 
                model: Optional[DeploymentModel] = ..., 
                sku_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CalculateModelCapacityResultEstimatedCapacity(_Model):
        deployable_value: Optional[int]
        value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deployable_value: Optional[int] = ..., 
                value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CallRateLimit(_Model):
        count: Optional[float]
        renewal_period: Optional[float]
        rules: Optional[list[ThrottlingRule]]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[float] = ..., 
                renewal_period: Optional[float] = ..., 
                rules: Optional[list[ThrottlingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CapabilityHost(ProxyResource):
        id: str
        name: str
        properties: CapabilityHostProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: CapabilityHostProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CapabilityHostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTS = "Agents"


    class azure.mgmt.cognitiveservices.models.CapabilityHostProperties(ResourceBase):
        ai_services_connections: Optional[list[str]]
        capability_host_kind: Optional[Union[str, CapabilityHostKind]]
        customer_subnet: Optional[str]
        description: str
        enable_public_hosting_environment: Optional[bool]
        provisioning_state: Optional[Union[str, CapabilityHostProvisioningState]]
        storage_connections: Optional[list[str]]
        tags: dict[str, str]
        thread_storage_connections: Optional[list[str]]
        vector_store_connections: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ai_services_connections: Optional[list[str]] = ..., 
                capability_host_kind: Optional[Union[str, CapabilityHostKind]] = ..., 
                customer_subnet: Optional[str] = ..., 
                description: Optional[str] = ..., 
                enable_public_hosting_environment: Optional[bool] = ..., 
                storage_connections: Optional[list[str]] = ..., 
                tags: Optional[dict[str, str]] = ..., 
                thread_storage_connections: Optional[list[str]] = ..., 
                vector_store_connections: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CapabilityHostProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.CapabilitySettings(_Model):
        blob_store: Optional[str]
        document_store: Optional[str]
        vector_store: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_store: Optional[str] = ..., 
                document_store: Optional[str] = ..., 
                vector_store: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CapacityConfig(_Model):
        allowed_values: Optional[list[int]]
        default: Optional[int]
        maximum: Optional[int]
        minimum: Optional[int]
        step: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                allowed_values: Optional[list[int]] = ..., 
                default: Optional[int] = ..., 
                maximum: Optional[int] = ..., 
                minimum: Optional[int] = ..., 
                step: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ChannelsBuiltInAuthorizationPolicy(ApplicationAuthorizationPolicy, discriminator='Channels'):
        type: Literal[BuiltInAuthorizationScheme.CHANNELS]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CheckDomainAvailabilityParameter(_Model):
        kind: Optional[str]
        subdomain_name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                subdomain_name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CheckSkuAvailabilityParameter(_Model):
        kind: str
        skus: list[str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str, 
                skus: list[str], 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ClusterComputeProperties(ComputeProperties, discriminator='Cluster'):
        compute_type: Literal[ComputeType.CLUSTER]
        creation_time: datetime
        errors: list[ErrorDetail]
        location: str
        pools: list[Pool]
        provisioning_state: Union[str, ComputeProvisioningState]
        subnet_arm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                pools: list[Pool], 
                subnet_arm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentCost(_Model):
        commitment_meter_id: Optional[str]
        overage_meter_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commitment_meter_id: Optional[str] = ..., 
                overage_meter_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPeriod(_Model):
        count: Optional[int]
        end_date: Optional[str]
        quota: Optional[CommitmentQuota]
        start_date: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[int] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlan(ProxyResource):
        etag: Optional[str]
        id: str
        kind: Optional[str]
        location: Optional[str]
        name: str
        properties: Optional[CommitmentPlanProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[CommitmentPlanProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlanAccountAssociation(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[CommitmentPlanAccountAssociationProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CommitmentPlanAccountAssociationProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlanAccountAssociationProperties(_Model):
        account_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlanAssociation(_Model):
        commitment_plan_id: Optional[str]
        commitment_plan_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                commitment_plan_id: Optional[str] = ..., 
                commitment_plan_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlanProperties(_Model):
        auto_renew: Optional[bool]
        commitment_plan_guid: Optional[str]
        current: Optional[CommitmentPeriod]
        hosting_model: Optional[Union[str, HostingModel]]
        last: Optional[CommitmentPeriod]
        next: Optional[CommitmentPeriod]
        plan_type: Optional[str]
        provisioning_issues: Optional[list[str]]
        provisioning_state: Optional[Union[str, CommitmentPlanProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                auto_renew: Optional[bool] = ..., 
                commitment_plan_guid: Optional[str] = ..., 
                current: Optional[CommitmentPeriod] = ..., 
                hosting_model: Optional[Union[str, HostingModel]] = ..., 
                next: Optional[CommitmentPeriod] = ..., 
                plan_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentPlanProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.CommitmentQuota(_Model):
        quantity: Optional[int]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                quantity: Optional[int] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CommitmentTier(_Model):
        cost: Optional[CommitmentCost]
        hosting_model: Optional[Union[str, HostingModel]]
        kind: Optional[str]
        max_count: Optional[int]
        plan_type: Optional[str]
        quota: Optional[CommitmentQuota]
        sku_name: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cost: Optional[CommitmentCost] = ..., 
                hosting_model: Optional[Union[str, HostingModel]] = ..., 
                kind: Optional[str] = ..., 
                max_count: Optional[int] = ..., 
                plan_type: Optional[str] = ..., 
                quota: Optional[CommitmentQuota] = ..., 
                sku_name: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Compute(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        kind: Optional[str]
        name: str
        properties: ComputeProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                kind: Optional[str] = ..., 
                properties: ComputeProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ComputeOperationStatus(ProxyResource):
        id: str
        name: str
        properties: Optional[ComputeOperationStatusProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ComputeOperationStatusProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ComputeOperationStatusProperties(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        start_time: Optional[datetime]
        status: Optional[Union[str, ComputeOperationStatusType]]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                status: Optional[Union[str, ComputeOperationStatusType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ComputeOperationStatusType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.ComputeProperties(_Model):
        compute_type: str
        creation_time: Optional[datetime]
        errors: Optional[list[ErrorDetail]]
        location: str
        provisioning_state: Optional[Union[str, ComputeProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                compute_type: str, 
                location: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ComputeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        FAILED = "Failed"
        RESTARTING = "Restarting"
        SCALING = "Scaling"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.ComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        CONTAINER_INSTANCE = "ContainerInstance"


    class azure.mgmt.cognitiveservices.models.ConnectionAccessKey(_Model):
        access_key_id: Optional[str]
        secret_access_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_key_id: Optional[str] = ..., 
                secret_access_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionAccountKey(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionApiKey(_Model):
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ACCESS_KEY = "AccessKey"
        ACCOUNT_KEY = "AccountKey"
        ACCOUNT_MANAGED_IDENTITY = "AccountManagedIdentity"
        AGENTIC_IDENTITY_TOKEN = "AgenticIdentityToken"
        AGENTIC_USER = "AgenticUser"
        AGENT_USER_IMPERSONATION = "AgentUserImpersonation"
        API_KEY = "ApiKey"
        CUSTOM_KEYS = "CustomKeys"
        DELEGATED_SAS = "DelegatedSAS"
        MANAGED_IDENTITY = "ManagedIdentity"
        NONE = "None"
        O_AUTH2 = "OAuth2"
        PAT = "PAT"
        PROJECT_MANAGED_IDENTITY = "ProjectManagedIdentity"
        SAS = "SAS"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        USERNAME_PASSWORD = "UsernamePassword"
        USER_ENTRA_TOKEN = "UserEntraToken"


    class azure.mgmt.cognitiveservices.models.ConnectionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADLS_GEN2 = "ADLSGen2"
        AI_SERVICES = "AIServices"
        AMAZON_MWS = "AmazonMws"
        AMAZON_RDS_FOR_ORACLE = "AmazonRdsForOracle"
        AMAZON_RDS_FOR_SQL_SERVER = "AmazonRdsForSqlServer"
        AMAZON_REDSHIFT = "AmazonRedshift"
        AMAZON_S3_COMPATIBLE = "AmazonS3Compatible"
        API_KEY = "ApiKey"
        API_MANAGEMENT = "ApiManagement"
        APP_CONFIG = "AppConfig"
        APP_INSIGHTS = "AppInsights"
        AZURE_BLOB = "AzureBlob"
        AZURE_CONTAINER_APP_ENVIRONMENT = "AzureContainerAppEnvironment"
        AZURE_DATABRICKS_DELTA_LAKE = "AzureDatabricksDeltaLake"
        AZURE_DATA_EXPLORER = "AzureDataExplorer"
        AZURE_KEY_VAULT = "AzureKeyVault"
        AZURE_MARIA_DB = "AzureMariaDb"
        AZURE_MY_SQL_DB = "AzureMySqlDb"
        AZURE_ONE_LAKE = "AzureOneLake"
        AZURE_OPEN_AI = "AzureOpenAI"
        AZURE_POSTGRES_DB = "AzurePostgresDb"
        AZURE_SQL_DB = "AzureSqlDb"
        AZURE_SQL_MI = "AzureSqlMi"
        AZURE_STORAGE_ACCOUNT = "AzureStorageAccount"
        AZURE_SYNAPSE_ANALYTICS = "AzureSynapseAnalytics"
        AZURE_TABLE_STORAGE = "AzureTableStorage"
        BING_LLM_SEARCH = "BingLLMSearch"
        CASSANDRA = "Cassandra"
        COGNITIVE_SEARCH = "CognitiveSearch"
        COGNITIVE_SERVICE = "CognitiveService"
        CONCUR = "Concur"
        CONTAINER_REGISTRY = "ContainerRegistry"
        COSMOS_DB = "CosmosDb"
        COSMOS_DB_MONGO_DB_API = "CosmosDbMongoDbApi"
        COUCHBASE = "Couchbase"
        CUSTOM_KEYS = "CustomKeys"
        DATABRICKS = "Databricks"
        DB2 = "Db2"
        DRILL = "Drill"
        DYNAMICS = "Dynamics"
        DYNAMICS_AX = "DynamicsAx"
        DYNAMICS_CRM = "DynamicsCrm"
        ELASTICSEARCH = "Elasticsearch"
        ELOQUA = "Eloqua"
        FILE_SERVER = "FileServer"
        FTP_SERVER = "FtpServer"
        GENERIC_CONTAINER_REGISTRY = "GenericContainerRegistry"
        GENERIC_HTTP = "GenericHttp"
        GENERIC_REST = "GenericRest"
        GIT = "Git"
        GOOGLE_AD_WORDS = "GoogleAdWords"
        GOOGLE_BIG_QUERY = "GoogleBigQuery"
        GOOGLE_CLOUD_STORAGE = "GoogleCloudStorage"
        GREENPLUM = "Greenplum"
        GROUNDING_WITH_BING_SEARCH = "GroundingWithBingSearch"
        GROUNDING_WITH_CUSTOM_SEARCH = "GroundingWithCustomSearch"
        HBASE = "Hbase"
        HDFS = "Hdfs"
        HIVE = "Hive"
        HUBSPOT = "Hubspot"
        IMPALA = "Impala"
        INFORMIX = "Informix"
        JIRA = "Jira"
        MAGENTO = "Magento"
        MANAGED_ONLINE_ENDPOINT = "ManagedOnlineEndpoint"
        MARIA_DB = "MariaDb"
        MARKETO = "Marketo"
        MICROSOFT_ACCESS = "MicrosoftAccess"
        MICROSOFT_FABRIC = "MicrosoftFabric"
        MODEL_GATEWAY = "ModelGateway"
        MONGO_DB_ATLAS = "MongoDbAtlas"
        MONGO_DB_V2 = "MongoDbV2"
        MY_SQL = "MySql"
        NETEZZA = "Netezza"
        ODBC = "Odbc"
        OFFICE365 = "Office365"
        OPEN_AI = "OpenAI"
        ORACLE = "Oracle"
        ORACLE_CLOUD_STORAGE = "OracleCloudStorage"
        ORACLE_SERVICE_CLOUD = "OracleServiceCloud"
        O_DATA_REST = "ODataRest"
        PAY_PAL = "PayPal"
        PHOENIX = "Phoenix"
        PINECONE = "Pinecone"
        POSTGRE_SQL = "PostgreSql"
        POWER_PLATFORM_ENVIRONMENT = "PowerPlatformEnvironment"
        PRESTO = "Presto"
        PYTHON_FEED = "PythonFeed"
        QUICK_BOOKS = "QuickBooks"
        REDIS = "Redis"
        REMOTE_A2_A = "RemoteA2A"
        REMOTE_TOOL = "RemoteTool"
        RESPONSYS = "Responsys"
        S3 = "S3"
        SALESFORCE = "Salesforce"
        SALESFORCE_MARKETING_CLOUD = "SalesforceMarketingCloud"
        SALESFORCE_SERVICE_CLOUD = "SalesforceServiceCloud"
        SAP_BW = "SapBw"
        SAP_CLOUD_FOR_CUSTOMER = "SapCloudForCustomer"
        SAP_ECC = "SapEcc"
        SAP_HANA = "SapHana"
        SAP_OPEN_HUB = "SapOpenHub"
        SAP_TABLE = "SapTable"
        SERP = "Serp"
        SERVERLESS = "Serverless"
        SERVICE_NOW = "ServiceNow"
        SFTP = "Sftp"
        SHAREPOINT = "Sharepoint"
        SHARE_POINT_ONLINE_LIST = "SharePointOnlineList"
        SHOPIFY = "Shopify"
        SNOWFLAKE = "Snowflake"
        SPARK = "Spark"
        SQL_SERVER = "SqlServer"
        SQUARE = "Square"
        SYBASE = "Sybase"
        TERADATA = "Teradata"
        VERTICA = "Vertica"
        WEB_TABLE = "WebTable"
        XERO = "Xero"
        ZOHO = "Zoho"


    class azure.mgmt.cognitiveservices.models.ConnectionGroup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "Azure"
        AZURE_AI = "AzureAI"
        DATABASE = "Database"
        FILE = "File"
        GENERIC_PROTOCOL = "GenericProtocol"
        NO_SQL = "NoSQL"
        SERVICES_AND_APPS = "ServicesAndApps"


    class azure.mgmt.cognitiveservices.models.ConnectionManagedIdentity(_Model):
        client_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionOAuth2(_Model):
        auth_url: Optional[str]
        client_id: Optional[str]
        client_secret: Optional[str]
        developer_token: Optional[str]
        password: Optional[str]
        refresh_token: Optional[str]
        tenant_id: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auth_url: Optional[str] = ..., 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                developer_token: Optional[str] = ..., 
                password: Optional[str] = ..., 
                refresh_token: Optional[str] = ..., 
                tenant_id: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionPersonalAccessToken(_Model):
        pat: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                pat: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionPropertiesV2(_Model):
        auth_type: str
        category: Optional[Union[str, ConnectionCategory]]
        created_by_workspace_arm_id: Optional[str]
        error: Optional[str]
        expiry_time: Optional[datetime]
        group: Optional[Union[str, ConnectionGroup]]
        is_shared_to_all: Optional[bool]
        metadata: Optional[dict[str, str]]
        pe_requirement: Optional[Union[str, ManagedPERequirement]]
        pe_status: Optional[Union[str, ManagedPEStatus]]
        shared_user_list: Optional[list[str]]
        target: Optional[str]
        use_workspace_managed_identity: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auth_type: str, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionPropertiesV2BasicResource(ProxyResource):
        id: str
        name: str
        properties: ConnectionPropertiesV2
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ConnectionPropertiesV2
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionServicePrincipal(_Model):
        client_id: Optional[str]
        client_secret: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                client_secret: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionSharedAccessSignature(_Model):
        sas: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                sas: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionUpdateContent(_Model):
        properties: Optional[ConnectionPropertiesV2]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConnectionPropertiesV2] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectionUsernamePassword(_Model):
        password: Optional[str]
        security_token: Optional[str]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                security_token: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ConnectivityEndpoints(_Model):
        public_ip_address: Optional[str]
        ssh_port: Optional[int]


    class azure.mgmt.cognitiveservices.models.ContainerInstanceComputeProperties(ComputeProperties, discriminator='ContainerInstance'):
        compute_type: Literal[ComputeType.CONTAINER_INSTANCE]
        connectivity_endpoints: Optional[ConnectivityEndpoints]
        creation_time: datetime
        errors: list[ErrorDetail]
        idle_time_before_shutdown: Optional[str]
        image_link: str
        location: str
        provisioning_state: Union[str, ComputeProvisioningState]
        ssh_settings: Optional[SshSettings]
        target_cluster_id: str

        @overload
        def __init__(
                self, 
                *, 
                idle_time_before_shutdown: Optional[str] = ..., 
                image_link: str, 
                location: str, 
                ssh_settings: Optional[SshSettings] = ..., 
                target_cluster_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ContentLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIGH = "High"
        LOW = "Low"
        MEDIUM = "Medium"


    class azure.mgmt.cognitiveservices.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cognitiveservices.models.CustomBlocklistConfig(RaiBlocklistConfig):
        blocking: bool
        blocklist_name: str
        source: Optional[Union[str, RaiPolicyContentSource]]

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                blocklist_name: Optional[str] = ..., 
                source: Optional[Union[str, RaiPolicyContentSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CustomKeys(_Model):
        keys_property: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                keys_property: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.CustomKeysConnectionProperties(ConnectionPropertiesV2, discriminator='CustomKeys'):
        auth_type: Literal[ConnectionAuthType.CUSTOM_KEYS]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[CustomKeys]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[CustomKeys] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DefenderForAISetting(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[DefenderForAISettingProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DefenderForAISettingProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cognitiveservices.models.DefenderForAISettingProperties(_Model):
        state: Optional[Union[str, DefenderForAISettingState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, DefenderForAISettingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DefenderForAISettingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cognitiveservices.models.Deployment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[DeploymentProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DeploymentProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentCapacitySettings(_Model):
        designated_capacity: Optional[int]
        priority: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                designated_capacity: Optional[int] = ..., 
                priority: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentModel(_Model):
        call_rate_limit: Optional[CallRateLimit]
        format: Optional[str]
        name: Optional[str]
        publisher: Optional[str]
        source: Optional[str]
        source_account: Optional[str]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[str] = ..., 
                name: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
                source: Optional[str] = ..., 
                source_account: Optional[str] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentModelVersionUpgradeOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_AUTO_UPGRADE = "NoAutoUpgrade"
        ONCE_CURRENT_VERSION_EXPIRED = "OnceCurrentVersionExpired"
        ONCE_NEW_DEFAULT_VERSION_AVAILABLE = "OnceNewDefaultVersionAvailable"


    class azure.mgmt.cognitiveservices.models.DeploymentPolicyEvaluationResult(_Model):
        error_message: Optional[str]
        evaluation_outcome: Optional[Union[str, PolicyEvaluationOutcome]]
        non_compliant_assignments: Optional[list[PolicyAssignmentEvaluationDetails]]

        @overload
        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                evaluation_outcome: Optional[Union[str, PolicyEvaluationOutcome]] = ..., 
                non_compliant_assignments: Optional[list[PolicyAssignmentEvaluationDetails]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentProperties(_Model):
        call_rate_limit: Optional[CallRateLimit]
        capabilities: Optional[dict[str, str]]
        capacity_settings: Optional[DeploymentCapacitySettings]
        context_cache_container_id: Optional[str]
        current_capacity: Optional[int]
        deployment_state: Optional[Union[str, DeploymentState]]
        dynamic_throttling_enabled: Optional[bool]
        model: Optional[DeploymentModel]
        parent_deployment_name: Optional[str]
        provisioning_state: Optional[Union[str, DeploymentProvisioningState]]
        rai_policy_name: Optional[str]
        rate_limits: Optional[list[ThrottlingRule]]
        routing: Optional[DeploymentRouting]
        scale_settings: Optional[DeploymentScaleSettings]
        service_tier: Optional[Union[str, ServiceTier]]
        speculative_decoding: Optional[DeploymentSpeculativeDecoding]
        spillover_deployment_name: Optional[str]
        version_upgrade_option: Optional[Union[str, DeploymentModelVersionUpgradeOption]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_settings: Optional[DeploymentCapacitySettings] = ..., 
                context_cache_container_id: Optional[str] = ..., 
                current_capacity: Optional[int] = ..., 
                deployment_state: Optional[Union[str, DeploymentState]] = ..., 
                model: Optional[DeploymentModel] = ..., 
                parent_deployment_name: Optional[str] = ..., 
                rai_policy_name: Optional[str] = ..., 
                routing: Optional[DeploymentRouting] = ..., 
                scale_settings: Optional[DeploymentScaleSettings] = ..., 
                service_tier: Optional[Union[str, ServiceTier]] = ..., 
                speculative_decoding: Optional[DeploymentSpeculativeDecoding] = ..., 
                spillover_deployment_name: Optional[str] = ..., 
                version_upgrade_option: Optional[Union[str, DeploymentModelVersionUpgradeOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        FAILED = "Failed"
        MOVING = "Moving"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.DeploymentRouting(_Model):
        mode: Optional[Union[str, RoutingMode]]
        models: Optional[list[DeploymentModel]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, RoutingMode]] = ..., 
                models: Optional[list[DeploymentModel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentScaleSettings(_Model):
        active_capacity: Optional[int]
        capacity: Optional[int]
        scale_type: Optional[Union[str, DeploymentScaleType]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                scale_type: Optional[Union[str, DeploymentScaleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANUAL = "Manual"
        STANDARD = "Standard"


    class azure.mgmt.cognitiveservices.models.DeploymentSizeCapacity(_Model):
        largest_deployment_capacity: Optional[int]
        model_instance_accelerator_count: Optional[int]
        total_available_capacity: Optional[int]


    class azure.mgmt.cognitiveservices.models.DeploymentSpeculativeDecoding(_Model):
        draft_model: DeploymentModel
        draft_token_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                draft_model: DeploymentModel, 
                draft_token_count: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.DeploymentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PAUSED = "Paused"
        RUNNING = "Running"


    class azure.mgmt.cognitiveservices.models.DeprecationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLANNED = "Planned"
        TENTATIVE = "Tentative"


    class azure.mgmt.cognitiveservices.models.DomainAvailability(_Model):
        is_subdomain_available: Optional[bool]
        kind: Optional[str]
        reason: Optional[str]
        subdomain_name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_subdomain_available: Optional[bool] = ..., 
                kind: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                subdomain_name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Encryption(_Model):
        key_source: Optional[Union[str, KeySource]]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EncryptionScope(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[EncryptionScopeProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EncryptionScopeProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EncryptionScopeProperties(Encryption):
        key_source: Union[str, KeySource]
        key_vault_properties: KeyVaultProperties
        provisioning_state: Optional[Union[str, EncryptionScopeProvisioningState]]
        state: Optional[Union[str, EncryptionScopeState]]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Optional[Union[str, KeySource]] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ..., 
                state: Optional[Union[str, EncryptionScopeState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EncryptionScopeProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING = "Moving"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.EncryptionScopeState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cognitiveservices.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.cognitiveservices.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.cognitiveservices.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EvaluateDeploymentPoliciesDeployment(_Model):
        name: str
        properties: EvaluateDeploymentPoliciesDeploymentProperties

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: EvaluateDeploymentPoliciesDeploymentProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EvaluateDeploymentPoliciesDeploymentProperties(_Model):
        model: DeploymentModel
        rai_policy_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                model: DeploymentModel, 
                rai_policy_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EvaluateDeploymentPoliciesRequest(_Model):
        deployments: list[EvaluateDeploymentPoliciesDeployment]

        @overload
        def __init__(
                self, 
                *, 
                deployments: list[EvaluateDeploymentPoliciesDeployment]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.EvaluateDeploymentPoliciesResponse(_Model):
        results: Optional[dict[str, DeploymentPolicyEvaluationResult]]

        @overload
        def __init__(
                self, 
                *, 
                results: Optional[dict[str, DeploymentPolicyEvaluationResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.FirewallSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        STANDARD = "Standard"


    class azure.mgmt.cognitiveservices.models.FoundryAutoUpgrade(_Model):
        mode: Optional[Union[str, FoundryAutoUpgradeMode]]
        planned_by_microsoft: Optional[bool]
        scheduled_at: Optional[datetime]
        status_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, FoundryAutoUpgradeMode]] = ..., 
                planned_by_microsoft: Optional[bool] = ..., 
                scheduled_at: Optional[datetime] = ..., 
                status_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.FoundryAutoUpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cognitiveservices.models.FqdnOutboundRule(OutboundRule, discriminator='FQDN'):
        category: Union[str, RuleCategory]
        destination: Optional[str]
        error_information: str
        parent_rule_names: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.FQDN]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                destination: Optional[str] = ..., 
                status: Optional[Union[str, RuleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.HostedAgentDeployment(AgentDeploymentProperties, discriminator='Hosted'):
        agents: list[VersionedAgentReference]
        deployment_id: str
        deployment_type: Literal[AgentDeploymentType.HOSTED]
        description: str
        display_name: str
        max_replicas: Optional[int]
        min_replicas: Optional[int]
        protocols: list[AgentProtocolVersion]
        provisioning_state: Union[str, AgentDeploymentProvisioningState]
        state: Union[str, AgentDeploymentState]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                agents: Optional[list[VersionedAgentReference]] = ..., 
                deployment_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                max_replicas: Optional[int] = ..., 
                min_replicas: Optional[int] = ..., 
                protocols: Optional[list[AgentProtocolVersion]] = ..., 
                state: Optional[Union[str, AgentDeploymentState]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.HostingModel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED_CONTAINER = "ConnectedContainer"
        DISCONNECTED_CONTAINER = "DisconnectedContainer"
        PROVISIONED_WEB = "ProvisionedWeb"
        WEB = "Web"


    class azure.mgmt.cognitiveservices.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ResourceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ResourceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.IdentityKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENTIC_USER = "AgenticUser"
        AGENT_BLUEPRINT = "AgentBlueprint"
        AGENT_INSTANCE = "AgentInstance"
        MANAGED = "Managed"
        NONE = "None"


    class azure.mgmt.cognitiveservices.models.IdentityManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.cognitiveservices.models.IdentityProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.IpRule(_Model):
        value: str

        @overload
        def __init__(
                self, 
                *, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.IsolationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW_INTERNET_OUTBOUND = "AllowInternetOutbound"
        ALLOW_ONLY_APPROVED_OUTBOUND = "AllowOnlyApprovedOutbound"
        DISABLED = "Disabled"


    class azure.mgmt.cognitiveservices.models.KeyName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY1 = "Key1"
        KEY2 = "Key2"


    class azure.mgmt.cognitiveservices.models.KeySource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_COGNITIVE_SERVICES = "Microsoft.CognitiveServices"
        MICROSOFT_KEY_VAULT = "Microsoft.KeyVault"


    class azure.mgmt.cognitiveservices.models.KeyVaultProperties(_Model):
        identity_client_id: Optional[str]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_client_id: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedAgentDeployment(AgentDeploymentProperties, discriminator='Managed'):
        agents: list[VersionedAgentReference]
        deployment_id: str
        deployment_type: Literal[AgentDeploymentType.MANAGED]
        description: str
        display_name: str
        protocols: list[AgentProtocolVersion]
        provisioning_state: Union[str, AgentDeploymentProvisioningState]
        state: Union[str, AgentDeploymentState]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                agents: Optional[list[VersionedAgentReference]] = ..., 
                deployment_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                protocols: Optional[list[AgentProtocolVersion]] = ..., 
                state: Optional[Union[str, AgentDeploymentState]] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedClusterAgentHostingConfiguration(AgentHostingConfiguration, discriminator='ManagedCluster'):
        cluster_resource_id: str
        hosting_management_identity_resource_id: str
        hosting_type: Literal[AgentHostingType.MANAGED_CLUSTER]
        name: str
        storage_account_resource_id: str
        workload_identity_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                cluster_resource_id: str, 
                hosting_management_identity_resource_id: str, 
                name: str, 
                storage_account_resource_id: str, 
                workload_identity_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeCapacity(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagedComputeCapacityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedComputeCapacityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeCapacityProperties(_Model):
        accelerator_type: Optional[str]
        available_accelerators: Optional[int]
        deployment_size_capacities: Optional[list[DeploymentSizeCapacity]]


    class azure.mgmt.cognitiveservices.models.ManagedComputeDeployment(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[ManagedComputeDeploymentProperties]
        sku: Optional[Sku]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedComputeDeploymentProperties] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeDeploymentInfo(_Model):
        accelerator_count: Optional[int]
        deployment_id: Optional[str]
        instance_count: Optional[int]
        model_id: Optional[str]
        project_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                accelerator_count: Optional[int] = ..., 
                deployment_id: Optional[str] = ..., 
                instance_count: Optional[int] = ..., 
                model_id: Optional[str] = ..., 
                project_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeDeploymentProperties(_Model):
        accelerator_type: Optional[str]
        accelerators_per_instance: Optional[int]
        capabilities: Optional[dict[str, str]]
        compute_id: Optional[str]
        deployment_template: Optional[str]
        model: str
        priority: Optional[str]
        provisioning_details: Optional[ManagedComputeDeploymentProvisioningDetails]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        routes: Optional[ManagedComputeDeploymentRoutes]
        total_accelerators: Optional[int]
        version_upgrade_option: Optional[Union[str, DeploymentModelVersionUpgradeOption]]

        @overload
        def __init__(
                self, 
                *, 
                accelerator_type: Optional[str] = ..., 
                compute_id: Optional[str] = ..., 
                deployment_template: Optional[str] = ..., 
                model: str, 
                priority: Optional[str] = ..., 
                version_upgrade_option: Optional[Union[str, DeploymentModelVersionUpgradeOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeDeploymentProvisioningDetails(_Model):
        last_operation_timestamp: Optional[datetime]
        message: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                last_operation_timestamp: Optional[datetime] = ..., 
                message: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeDeploymentRoutes(_Model):
        chat_completions_scoring_path: Optional[str]
        messages_api_scoring_path: Optional[str]
        swagger: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                chat_completions_scoring_path: Optional[str] = ..., 
                messages_api_scoring_path: Optional[str] = ..., 
                swagger: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedComputeUsage(_Model):
        current_value: Optional[float]
        deployments: Optional[list[ManagedComputeDeploymentInfo]]
        id: Optional[str]
        limit: Optional[float]
        name: Optional[MetricName]
        offer_scope: Optional[str]
        type: Optional[str]
        unit: Optional[Union[str, UnitType]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                deployments: Optional[list[ManagedComputeDeploymentInfo]] = ..., 
                limit: Optional[float] = ..., 
                offer_scope: Optional[str] = ..., 
                unit: Optional[Union[str, UnitType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedIdentityAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='ManagedIdentity'):
        auth_type: Literal[ConnectionAuthType.MANAGED_IDENTITY]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionManagedIdentity]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionManagedIdentity] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V1 = "V1"
        V2 = "V2"


    class azure.mgmt.cognitiveservices.models.ManagedNetworkProvisionOptions(_Model):


    class azure.mgmt.cognitiveservices.models.ManagedNetworkProvisionStatus(_Model):
        status: Optional[Union[str, ManagedNetworkStatus]]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, ManagedNetworkStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFERRED = "Deferred"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cognitiveservices.models.ManagedNetworkSettings(_Model):
        firewall_public_ip_address: Optional[str]
        firewall_sku: Optional[Union[str, FirewallSku]]
        isolation_mode: Optional[Union[str, IsolationMode]]
        managed_network_kind: Optional[Union[str, ManagedNetworkKind]]
        network_id: Optional[str]
        outbound_rules: Optional[dict[str, OutboundRule]]
        provisioning_state: Optional[Union[str, ManagedNetworkProvisioningState]]
        status: Optional[ManagedNetworkProvisionStatus]

        @overload
        def __init__(
                self, 
                *, 
                firewall_sku: Optional[Union[str, FirewallSku]] = ..., 
                isolation_mode: Optional[Union[str, IsolationMode]] = ..., 
                managed_network_kind: Optional[Union[str, ManagedNetworkKind]] = ..., 
                outbound_rules: Optional[dict[str, OutboundRule]] = ..., 
                status: Optional[ManagedNetworkProvisionStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkSettingsBasicResource(Resource):
        id: str
        name: str
        properties: Optional[ManagedNetworkSettings]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedNetworkSettings] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkSettingsEx(ManagedNetworkSettings):
        changeable_isolation_modes: Optional[list[Union[str, IsolationMode]]]
        firewall_public_ip_address: str
        firewall_sku: Union[str, FirewallSku]
        isolation_mode: Union[str, IsolationMode]
        managed_network_kind: Union[str, ManagedNetworkKind]
        network_id: str
        outbound_rules: dict[str, OutboundRule]
        provisioning_state: Union[str, ManagedNetworkProvisioningState]
        status: ManagedNetworkProvisionStatus

        @overload
        def __init__(
                self, 
                *, 
                firewall_sku: Optional[Union[str, FirewallSku]] = ..., 
                isolation_mode: Optional[Union[str, IsolationMode]] = ..., 
                managed_network_kind: Optional[Union[str, ManagedNetworkKind]] = ..., 
                outbound_rules: Optional[dict[str, OutboundRule]] = ..., 
                status: Optional[ManagedNetworkProvisionStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkSettingsProperties(_Model):
        managed_network: Optional[ManagedNetworkSettingsEx]
        provisioning_state: Optional[Union[str, ManagedNetworkProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                managed_network: Optional[ManagedNetworkSettingsEx] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkSettingsPropertiesBasicResource(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagedNetworkSettingsProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedNetworkSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ManagedNetworkStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.cognitiveservices.models.ManagedPERequirement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_APPLICABLE = "NotApplicable"
        NOT_REQUIRED = "NotRequired"
        REQUIRED = "Required"


    class azure.mgmt.cognitiveservices.models.ManagedPEStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.cognitiveservices.models.MetricName(_Model):
        localized_value: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Model(_Model):
        description: Optional[str]
        kind: Optional[str]
        model: Optional[AccountModel]
        sku_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                model: Optional[AccountModel] = ..., 
                sku_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelCapacityCalculatorWorkload(_Model):
        request_parameters: Optional[ModelCapacityCalculatorWorkloadRequestParam]
        request_per_minute: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                request_parameters: Optional[ModelCapacityCalculatorWorkloadRequestParam] = ..., 
                request_per_minute: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelCapacityCalculatorWorkloadRequestParam(_Model):
        avg_generated_tokens: Optional[int]
        avg_prompt_tokens: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                avg_generated_tokens: Optional[int] = ..., 
                avg_prompt_tokens: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelCapacityListResultValueItem(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ModelSkuCapacityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ModelSkuCapacityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelDeprecationInfo(_Model):
        deprecation_status: Optional[Union[str, DeprecationStatus]]
        fine_tune: Optional[str]
        inference: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                deprecation_status: Optional[Union[str, DeprecationStatus]] = ..., 
                fine_tune: Optional[str] = ..., 
                inference: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelLifecycleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPRECATED = "Deprecated"
        DEPRECATING = "Deprecating"
        GENERALLY_AVAILABLE = "GenerallyAvailable"
        LEGACY = "Legacy"
        PREVIEW = "Preview"
        STABLE = "Stable"


    class azure.mgmt.cognitiveservices.models.ModelSku(_Model):
        capacity: Optional[CapacityConfig]
        cost: Optional[list[BillingMeterInfo]]
        deprecation_date: Optional[datetime]
        name: Optional[str]
        rate_limits: Optional[list[CallRateLimit]]
        usage_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[CapacityConfig] = ..., 
                cost: Optional[list[BillingMeterInfo]] = ..., 
                deprecation_date: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                rate_limits: Optional[list[CallRateLimit]] = ..., 
                usage_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ModelSkuCapacityProperties(_Model):
        available_capacity: Optional[float]
        available_finetune_capacity: Optional[float]
        model: Optional[DeploymentModel]
        scope_id: Optional[str]
        scope_type: Optional[Union[str, QuotaScopeType]]
        sku_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                available_capacity: Optional[float] = ..., 
                available_finetune_capacity: Optional[float] = ..., 
                model: Optional[DeploymentModel] = ..., 
                scope_id: Optional[str] = ..., 
                scope_type: Optional[Union[str, QuotaScopeType]] = ..., 
                sku_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.MultiRegionSettings(_Model):
        regions: Optional[list[RegionSetting]]
        routing_method: Optional[Union[str, RoutingMethods]]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[RegionSetting]] = ..., 
                routing_method: Optional[Union[str, RoutingMethods]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkInjection(_Model):
        scenario: Optional[Union[str, ScenarioType]]
        subnet_arm_id: Optional[str]
        use_microsoft_managed_network: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                scenario: Optional[Union[str, ScenarioType]] = ..., 
                subnet_arm_id: Optional[str] = ..., 
                use_microsoft_managed_network: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkRuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.cognitiveservices.models.NetworkRuleSet(_Model):
        bypass: Optional[Union[str, ByPassSelection]]
        default_action: Optional[Union[str, NetworkRuleAction]]
        ip_rules: Optional[list[IpRule]]
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                bypass: Optional[Union[str, ByPassSelection]] = ..., 
                default_action: Optional[Union[str, NetworkRuleAction]] = ..., 
                ip_rules: Optional[list[IpRule]] = ..., 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeter(_Model):
        id: Optional[str]
        location: Optional[str]
        perimeter_guid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterAccessRule(_Model):
        name: Optional[str]
        properties: Optional[NetworkSecurityPerimeterAccessRuleProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[NetworkSecurityPerimeterAccessRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterAccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, NspAccessRuleDirection]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        subscriptions: Optional[list[NetworkSecurityPerimeterAccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                fully_qualified_domain_names: Optional[list[str]] = ..., 
                network_security_perimeters: Optional[list[NetworkSecurityPerimeter]] = ..., 
                subscriptions: Optional[list[NetworkSecurityPerimeterAccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterAccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterConfigurationAssociationInfo(_Model):
        access_mode: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        profile: Optional[NetworkSecurityPerimeterProfileInfo]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[str]
        resource_association: Optional[NetworkSecurityPerimeterConfigurationAssociationInfo]

        @overload
        def __init__(
                self, 
                *, 
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                profile: Optional[NetworkSecurityPerimeterProfileInfo] = ..., 
                provisioning_issues: Optional[list[ProvisioningIssue]] = ..., 
                resource_association: Optional[NetworkSecurityPerimeterConfigurationAssociationInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NetworkSecurityPerimeterProfileInfo(_Model):
        access_rules: Optional[list[NetworkSecurityPerimeterAccessRule]]
        access_rules_version: Optional[int]
        diagnostic_settings_version: Optional[int]
        enabled_log_categories: Optional[list[str]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NetworkSecurityPerimeterAccessRule]] = ..., 
                access_rules_version: Optional[int] = ..., 
                diagnostic_settings_version: Optional[int] = ..., 
                enabled_log_categories: Optional[list[str]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NoneAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='None'):
        auth_type: Literal[ConnectionAuthType.NONE]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.cognitiveservices.models.OAuth2AuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='OAuth2'):
        auth_type: Literal[ConnectionAuthType.O_AUTH2]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionOAuth2]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionOAuth2] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Operation(_Model):
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


    class azure.mgmt.cognitiveservices.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.cognitiveservices.models.OrganizationSharedBuiltInAuthorizationPolicy(ApplicationAuthorizationPolicy, discriminator='OrganizationScope'):
        type: Literal[BuiltInAuthorizationScheme.ORGANIZATION_SCOPE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.cognitiveservices.models.OutboundRule(_Model):
        category: Optional[Union[str, RuleCategory]]
        error_information: Optional[str]
        parent_rule_names: Optional[list[str]]
        status: Optional[Union[str, RuleStatus]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                status: Optional[Union[str, RuleStatus]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.OutboundRuleBasicResource(ProxyResource):
        id: str
        name: str
        properties: OutboundRule
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: OutboundRule
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PATAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='PAT'):
        auth_type: Literal[ConnectionAuthType.PAT]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionPersonalAccessToken]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionPersonalAccessToken] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PatchResourceSku(_Model):
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PatchResourceTags(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PatchResourceTagsAndSku(PatchResourceTags):
        sku: Optional[Sku]
        tags: dict[str, str]

        @overload
        def __init__(
                self, 
                *, 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PolicyAssignmentEvaluationDetails(_Model):
        assignment_id: Optional[str]
        effect: Optional[str]
        evaluation_outcome: Optional[Union[str, PolicyEvaluationOutcome]]
        expression_evaluations: Optional[list[PolicyExpressionEvaluationDetails]]
        non_compliance_reason: Optional[str]
        policy_definition_id: Optional[str]
        policy_set_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assignment_id: Optional[str] = ..., 
                effect: Optional[str] = ..., 
                evaluation_outcome: Optional[Union[str, PolicyEvaluationOutcome]] = ..., 
                expression_evaluations: Optional[list[PolicyExpressionEvaluationDetails]] = ..., 
                non_compliance_reason: Optional[str] = ..., 
                policy_definition_id: Optional[str] = ..., 
                policy_set_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PolicyEvaluationOutcome(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLIANT = "Compliant"
        ERROR = "Error"
        NON_COMPLIANT = "NonCompliant"


    class azure.mgmt.cognitiveservices.models.PolicyExpressionEvaluationDetails(_Model):
        expression: Optional[str]
        expression_kind: Optional[str]
        expression_value: Optional[str]
        operator: Optional[str]
        result: Optional[str]
        target_value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                expression: Optional[str] = ..., 
                expression_kind: Optional[str] = ..., 
                expression_value: Optional[str] = ..., 
                operator: Optional[str] = ..., 
                result: Optional[str] = ..., 
                target_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Pool(_Model):
        instance_type: str
        name: str
        node_count: int
        vm_priority: Optional[Union[str, VmPriority]]

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str, 
                name: str, 
                node_count: int, 
                vm_priority: Optional[Union[str, VmPriority]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.cognitiveservices.models.PrivateEndpointConnection(ProxyResource):
        etag: Optional[str]
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpointConnectionListResult(_Model):
        value: Optional[list[PrivateEndpointConnection]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateEndpointConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.PrivateEndpointOutboundRule(OutboundRule, discriminator='PrivateEndpoint'):
        category: Union[str, RuleCategory]
        destination: Optional[PrivateEndpointOutboundRuleDestination]
        error_information: str
        fqdns: Optional[list[str]]
        parent_rule_names: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.PRIVATE_ENDPOINT]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                destination: Optional[PrivateEndpointOutboundRuleDestination] = ..., 
                fqdns: Optional[list[str]] = ..., 
                status: Optional[Union[str, RuleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpointOutboundRuleDestination(_Model):
        service_resource_id: Optional[str]
        subresource_target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                service_resource_id: Optional[str] = ..., 
                subresource_target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.cognitiveservices.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateLinkResourceListResult(_Model):
        value: Optional[list[PrivateLinkResource]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[PrivateLinkResource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.PrivateLinkResourceProperties(_Model):
        display_name: Optional[str]
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


    class azure.mgmt.cognitiveservices.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.cognitiveservices.models.Project(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[ProjectProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[ProjectProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProjectCapabilityHost(ProxyResource):
        id: str
        name: str
        properties: ProjectCapabilityHostProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: ProjectCapabilityHostProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProjectCapabilityHostProperties(_Model):
        ai_services_connections: Optional[list[str]]
        provisioning_state: Optional[Union[str, CapabilityHostProvisioningState]]
        storage_connections: Optional[list[str]]
        thread_storage_connections: Optional[list[str]]
        vector_store_connections: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                ai_services_connections: Optional[list[str]] = ..., 
                storage_connections: Optional[list[str]] = ..., 
                thread_storage_connections: Optional[list[str]] = ..., 
                vector_store_connections: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProjectProperties(_Model):
        capability_settings: Optional[CapabilitySettings]
        description: Optional[str]
        display_name: Optional[str]
        endpoints: Optional[dict[str, str]]
        is_default: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                capability_settings: Optional[CapabilitySettings] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[ProvisioningIssueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[str]
        severity: Optional[str]
        suggested_access_rules: Optional[list[NetworkSecurityPerimeterAccessRule]]
        suggested_resource_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[str] = ..., 
                severity: Optional[str] = ..., 
                suggested_access_rules: Optional[list[NetworkSecurityPerimeterAccessRule]] = ..., 
                suggested_resource_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        EXTENSION_UNREACHABLE = "ExtensionUnreachable"
        FAILED = "Failed"
        MOVING = "Moving"
        RESOLVING_DNS = "ResolvingDNS"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cognitiveservices.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cognitiveservices.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cognitiveservices.models.QuotaLimit(_Model):
        count: Optional[float]
        renewal_period: Optional[float]
        rules: Optional[list[ThrottlingRule]]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[float] = ..., 
                renewal_period: Optional[float] = ..., 
                rules: Optional[list[ThrottlingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.QuotaScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLASSIC = "Classic"
        DATA_ZONE = "DataZone"
        GLOBAL = "Global"
        REGIONAL = "Regional"


    class azure.mgmt.cognitiveservices.models.QuotaTier(ProxyResource):
        id: str
        name: str
        properties: Optional[QuotaTierProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[QuotaTierProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.QuotaTierProperties(_Model):
        assignment_date: Optional[datetime]
        current_tier_name: Optional[str]
        tier_upgrade_eligibility_info: Optional[QuotaTierUpgradeEligibilityInfo]
        tier_upgrade_policy: Optional[Union[str, TierUpgradePolicy]]

        @overload
        def __init__(
                self, 
                *, 
                tier_upgrade_policy: Optional[Union[str, TierUpgradePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.QuotaTierUpgradeEligibilityInfo(_Model):
        next_tier_name: Optional[str]
        upgrade_applicable_date: Optional[datetime]
        upgrade_availability_status: Optional[Union[str, UpgradeAvailabilityStatus]]
        upgrade_unavailability_reason: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                next_tier_name: Optional[str] = ..., 
                upgrade_applicable_date: Optional[datetime] = ..., 
                upgrade_availability_status: Optional[Union[str, UpgradeAvailabilityStatus]] = ..., 
                upgrade_unavailability_reason: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.QuotaUsageStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        INCLUDED = "Included"
        IN_OVERAGE = "InOverage"
        UNKNOWN = "Unknown"


    class azure.mgmt.cognitiveservices.models.RaiActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANNOTATING = "ANNOTATING"
        BLOCKING = "BLOCKING"
        HITL = "HITL"
        NONE = "None"
        RETRY = "RETRY"


    class azure.mgmt.cognitiveservices.models.RaiBlocklist(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiBlocklistProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiBlocklistProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiBlocklistConfig(_Model):
        blocking: Optional[bool]
        blocklist_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                blocklist_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiBlocklistItem(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiBlocklistItemProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiBlocklistItemProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiBlocklistItemBulkRequest(_Model):
        name: Optional[str]
        properties: Optional[RaiBlocklistItemProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[RaiBlocklistItemProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiBlocklistItemProperties(_Model):
        is_regex: Optional[bool]
        pattern: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                is_regex: Optional[bool] = ..., 
                pattern: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiBlocklistProperties(_Model):
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiContentFilter(ProxyResource):
        id: str
        name: str
        properties: Optional[RaiContentFilterProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiContentFilterProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiContentFilterProperties(_Model):
        is_multi_level_filter: Optional[bool]
        name: Optional[str]
        source: Optional[Union[str, RaiPolicyContentSource]]

        @overload
        def __init__(
                self, 
                *, 
                is_multi_level_filter: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                source: Optional[Union[str, RaiPolicyContentSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressDefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.cognitiveservices.models.RaiEgressHeaderOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INSERT = "Insert"
        REMOVE = "Remove"
        SET = "Set"


    class azure.mgmt.cognitiveservices.models.RaiEgressHeaderTransform(_Model):
        name: str
        operation: Union[str, RaiEgressHeaderOperation]
        value: Optional[str]
        value_ref: Optional[RaiEgressHeaderValueRef]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                operation: Union[str, RaiEgressHeaderOperation], 
                value: Optional[str] = ..., 
                value_ref: Optional[RaiEgressHeaderValueRef] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressHeaderValueRef(_Model):
        managed_identity_ref: Optional[RaiEgressManagedIdentityRef]
        secret_ref: Optional[RaiEgressSecretRef]

        @overload
        def __init__(
                self, 
                *, 
                managed_identity_ref: Optional[RaiEgressManagedIdentityRef] = ..., 
                secret_ref: Optional[RaiEgressSecretRef] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressManagedIdentityRef(_Model):
        format: Optional[str]
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[str] = ..., 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        ENFORCED = "Enforced"


    class azure.mgmt.cognitiveservices.models.RaiEgressPolicyConfig(_Model):
        default_action: Optional[Union[str, RaiEgressDefaultAction]]
        description: Optional[str]
        mode: Optional[Union[str, RaiEgressMode]]
        rules: Optional[list[RaiEgressRule]]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, RaiEgressDefaultAction]] = ..., 
                description: Optional[str] = ..., 
                mode: Optional[Union[str, RaiEgressMode]] = ..., 
                rules: Optional[list[RaiEgressRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressRewriteTarget(_Model):
        host: Optional[str]
        path: Optional[str]
        scheme: Optional[Union[str, RaiEgressScheme]]

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                path: Optional[str] = ..., 
                scheme: Optional[Union[str, RaiEgressScheme]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressRule(_Model):
        action: RaiEgressRuleAction
        description: Optional[str]
        match: Optional[RaiEgressRuleMatch]
        name: str
        rule_type: Union[str, RaiEgressRuleType]

        @overload
        def __init__(
                self, 
                *, 
                action: RaiEgressRuleAction, 
                description: Optional[str] = ..., 
                match: Optional[RaiEgressRuleMatch] = ..., 
                name: str, 
                rule_type: Union[str, RaiEgressRuleType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressRuleAction(_Model):
        action_type: Union[str, RaiEgressRuleActionType]
        headers: Optional[list[RaiEgressHeaderTransform]]
        rewrite: Optional[RaiEgressRewriteTarget]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Union[str, RaiEgressRuleActionType], 
                headers: Optional[list[RaiEgressHeaderTransform]] = ..., 
                rewrite: Optional[RaiEgressRewriteTarget] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressRuleActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"
        REWRITE = "Rewrite"
        TRANSFORM = "Transform"


    class azure.mgmt.cognitiveservices.models.RaiEgressRuleMatch(_Model):
        host: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                host: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiEgressRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "Fqdn"


    class azure.mgmt.cognitiveservices.models.RaiEgressScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "http"
        HTTPS = "https"


    class azure.mgmt.cognitiveservices.models.RaiEgressSecretRef(_Model):
        format: Optional[str]
        secret_id: str
        secret_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                format: Optional[str] = ..., 
                secret_id: str, 
                secret_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiExternalSafetyProviderSchema(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiExternalSafetyProviderSchemaProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiExternalSafetyProviderSchemaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiExternalSafetyProviderSchemaProperties(_Model):
        created_at: Optional[datetime]
        key_vault_uri: Optional[str]
        last_modified_at: Optional[datetime]
        managed_identity: Optional[str]
        mode: Optional[str]
        provider_id: Optional[str]
        provider_name: Optional[str]
        secret_name: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_uri: Optional[str] = ..., 
                managed_identity: Optional[str] = ..., 
                mode: Optional[str] = ..., 
                provider_id: Optional[str] = ..., 
                provider_name: Optional[str] = ..., 
                secret_name: Optional[str] = ..., 
                url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiMonitorConfig(_Model):
        adx_storage_resource_id: Optional[str]
        identity_client_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                adx_storage_resource_id: Optional[str] = ..., 
                identity_client_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiPolicy(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiPolicyProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiPolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiPolicyContentFilter(_Model):
        action: Optional[Union[str, RaiActionType]]
        blocking: Optional[bool]
        enabled: Optional[bool]
        name: Optional[str]
        severity_threshold: Optional[Union[str, ContentLevel]]
        source: Optional[Union[str, RaiPolicyContentSource]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, RaiActionType]] = ..., 
                blocking: Optional[bool] = ..., 
                enabled: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                severity_threshold: Optional[Union[str, ContentLevel]] = ..., 
                source: Optional[Union[str, RaiPolicyContentSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiPolicyContentSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETION = "Completion"
        POST_RUN = "PostRun"
        POST_TOOL_CALL = "PostToolCall"
        PRE_RUN = "PreRun"
        PRE_TOOL_CALL = "PreToolCall"
        PROMPT = "Prompt"


    class azure.mgmt.cognitiveservices.models.RaiPolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNCHRONOUS_FILTER = "Asynchronous_filter"
        BLOCKING = "Blocking"
        DEFAULT = "Default"
        DEFERRED = "Deferred"


    class azure.mgmt.cognitiveservices.models.RaiPolicyProperties(_Model):
        base_policy_name: Optional[str]
        content_filters: Optional[list[RaiPolicyContentFilter]]
        custom_blocklists: Optional[list[CustomBlocklistConfig]]
        egress_policy: Optional[RaiEgressPolicyConfig]
        mode: Optional[Union[str, RaiPolicyMode]]
        safety_providers: Optional[list[SafetyProviderConfig]]
        type: Optional[Union[str, RaiPolicyType]]

        @overload
        def __init__(
                self, 
                *, 
                base_policy_name: Optional[str] = ..., 
                content_filters: Optional[list[RaiPolicyContentFilter]] = ..., 
                custom_blocklists: Optional[list[CustomBlocklistConfig]] = ..., 
                egress_policy: Optional[RaiEgressPolicyConfig] = ..., 
                mode: Optional[Union[str, RaiPolicyMode]] = ..., 
                safety_providers: Optional[list[SafetyProviderConfig]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_MANAGED = "SystemManaged"
        USER_MANAGED = "UserManaged"


    class azure.mgmt.cognitiveservices.models.RaiSafetyProviderConfig(_Model):
        blocking: Optional[bool]
        safety_provider_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                safety_provider_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiToolLabel(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiToolLabelProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiToolLabelProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiToolLabelProperties(_Model):
        account_scope: Optional[RaiToolLabelPropertiesAccountScope]
        project_scopes: Optional[list[RaiToolLabelPropertiesProjectScopesItem]]
        tool_connection_name: str

        @overload
        def __init__(
                self, 
                *, 
                account_scope: Optional[RaiToolLabelPropertiesAccountScope] = ..., 
                project_scopes: Optional[list[RaiToolLabelPropertiesProjectScopesItem]] = ..., 
                tool_connection_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiToolLabelPropertiesAccountScope(_Model):
        label_values: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                label_values: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiToolLabelPropertiesProjectScopesItem(_Model):
        label_values: dict[str, str]
        project: str

        @overload
        def __init__(
                self, 
                *, 
                label_values: dict[str, str], 
                project: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiTopic(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiTopicProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiTopicProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiTopicProperties(_Model):
        created_at: Optional[datetime]
        description: Optional[str]
        failed_reason: Optional[str]
        last_modified_at: Optional[datetime]
        sample_blob_url: Optional[str]
        status: Optional[str]
        topic_id: Optional[str]
        topic_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                description: Optional[str] = ..., 
                failed_reason: Optional[str] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                sample_blob_url: Optional[str] = ..., 
                status: Optional[str] = ..., 
                topic_id: Optional[str] = ..., 
                topic_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RegenerateKeyParameters(_Model):
        key_name: Union[str, KeyName]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Union[str, KeyName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RegionSetting(_Model):
        customsubdomain: Optional[str]
        name: Optional[str]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                customsubdomain: Optional[str] = ..., 
                name: Optional[str] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ReplacementConfig(_Model):
        auto_upgrade_start_date: Optional[datetime]
        target_model_name: Optional[str]
        target_model_version: Optional[str]
        upgrade_on_expiry_lead_time_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_start_date: Optional[datetime] = ..., 
                target_model_name: Optional[str] = ..., 
                target_model_version: Optional[str] = ..., 
                upgrade_on_expiry_lead_time_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RequestMatchPattern(_Model):
        method: Optional[str]
        path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                method: Optional[str] = ..., 
                path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.cognitiveservices.models.ResourceBase(_Model):
        description: Optional[str]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cognitiveservices.models.ResourceSku(_Model):
        kind: Optional[str]
        locations: Optional[list[str]]
        name: Optional[str]
        resource_type: Optional[str]
        restrictions: Optional[list[ResourceSkuRestrictions]]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                locations: Optional[list[str]] = ..., 
                name: Optional[str] = ..., 
                resource_type: Optional[str] = ..., 
                restrictions: Optional[list[ResourceSkuRestrictions]] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ResourceSkuRestrictionInfo(_Model):
        locations: Optional[list[str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ResourceSkuRestrictions(_Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: Optional[ResourceSkuRestrictionInfo]
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]] = ..., 
                restriction_info: Optional[ResourceSkuRestrictionInfo] = ..., 
                type: Optional[Union[str, ResourceSkuRestrictionsType]] = ..., 
                values_property: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.cognitiveservices.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.cognitiveservices.models.RoleBasedBuiltInAuthorizationPolicy(ApplicationAuthorizationPolicy, discriminator='Default'):
        type: Literal[BuiltInAuthorizationScheme.DEFAULT]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RoutingMethods(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PERFORMANCE = "Performance"
        PRIORITY = "Priority"
        WEIGHTED = "Weighted"


    class azure.mgmt.cognitiveservices.models.RoutingMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BALANCED = "balanced"
        COST = "cost"
        QUALITY = "quality"


    class azure.mgmt.cognitiveservices.models.RuleAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.cognitiveservices.models.RuleCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPENDENCY = "Dependency"
        RECOMMENDED = "Recommended"
        REQUIRED = "Required"
        USER_DEFINED = "UserDefined"


    class azure.mgmt.cognitiveservices.models.RuleStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DELETING = "Deleting"
        FAILED = "Failed"
        INACTIVE = "Inactive"
        PROVISIONING = "Provisioning"


    class azure.mgmt.cognitiveservices.models.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "FQDN"
        PRIVATE_ENDPOINT = "PrivateEndpoint"
        SERVICE_TAG = "ServiceTag"


    class azure.mgmt.cognitiveservices.models.SASAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='SAS'):
        auth_type: Literal[ConnectionAuthType.SAS]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionSharedAccessSignature]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionSharedAccessSignature] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SafetyProviderConfig(RaiSafetyProviderConfig):
        blocking: bool
        safety_provider_name: str
        source: Optional[Union[str, RaiPolicyContentSource]]

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                safety_provider_name: Optional[str] = ..., 
                source: Optional[Union[str, RaiPolicyContentSource]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ScenarioType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AGENT = "agent"
        NONE = "none"


    class azure.mgmt.cognitiveservices.models.ServicePrincipalAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='ServicePrincipal'):
        auth_type: Literal[ConnectionAuthType.SERVICE_PRINCIPAL]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionServicePrincipal]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionServicePrincipal] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ServiceTagOutboundRule(OutboundRule, discriminator='ServiceTag'):
        category: Union[str, RuleCategory]
        destination: Optional[ServiceTagOutboundRuleDestination]
        error_information: str
        parent_rule_names: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.SERVICE_TAG]

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, RuleCategory]] = ..., 
                destination: Optional[ServiceTagOutboundRuleDestination] = ..., 
                status: Optional[Union[str, RuleStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ServiceTagOutboundRuleDestination(_Model):
        action: Optional[Union[str, RuleAction]]
        address_prefixes: Optional[list[str]]
        port_ranges: Optional[str]
        protocol: Optional[str]
        service_tag: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, RuleAction]] = ..., 
                address_prefixes: Optional[list[str]] = ..., 
                port_ranges: Optional[str] = ..., 
                protocol: Optional[str] = ..., 
                service_tag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.ServiceTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        PRIORITY = "Priority"


    class azure.mgmt.cognitiveservices.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuAvailability(_Model):
        kind: Optional[str]
        message: Optional[str]
        reason: Optional[str]
        sku_available: Optional[bool]
        sku_name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[str] = ..., 
                message: Optional[str] = ..., 
                reason: Optional[str] = ..., 
                sku_available: Optional[bool] = ..., 
                sku_name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuAvailabilityListResult(_Model):
        value: Optional[list[SkuAvailability]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[SkuAvailability]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuCapability(_Model):
        name: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuChangeInfo(_Model):
        count_of_downgrades: Optional[float]
        count_of_upgrades_after_downgrades: Optional[float]
        last_change_date: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                count_of_downgrades: Optional[float] = ..., 
                count_of_upgrades_after_downgrades: Optional[float] = ..., 
                last_change_date: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuResource(_Model):
        capacity: Optional[CapacityConfig]
        resource_type: Optional[str]
        sku: Optional[Sku]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[CapacityConfig] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        ENTERPRISE = "Enterprise"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.cognitiveservices.models.SshSettings(_Model):
        admin_enabled: Optional[bool]
        ssh_public_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                admin_enabled: Optional[bool] = ..., 
                ssh_public_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.SystemData(_Model):
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


    class azure.mgmt.cognitiveservices.models.ThrottlingRule(_Model):
        count: Optional[float]
        dynamic_throttling_enabled: Optional[bool]
        key: Optional[str]
        match_patterns: Optional[list[RequestMatchPattern]]
        min_count: Optional[float]
        renewal_period: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                count: Optional[float] = ..., 
                dynamic_throttling_enabled: Optional[bool] = ..., 
                key: Optional[str] = ..., 
                match_patterns: Optional[list[RequestMatchPattern]] = ..., 
                min_count: Optional[float] = ..., 
                renewal_period: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.TierUpgradePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_AUTO_UPGRADE = "NoAutoUpgrade"
        ONCE_UPGRADE_IS_AVAILABLE = "OnceUpgradeIsAvailable"


    class azure.mgmt.cognitiveservices.models.TrafficRoutingProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIXED_RATIO = "FixedRatio"


    class azure.mgmt.cognitiveservices.models.TrafficRoutingRule(_Model):
        deployment_id: Optional[str]
        description: Optional[str]
        rule_id: Optional[str]
        traffic_percentage: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                deployment_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                rule_id: Optional[str] = ..., 
                traffic_percentage: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.UnitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYTES = "Bytes"
        BYTES_PER_SECOND = "BytesPerSecond"
        COUNT = "Count"
        COUNT_PER_SECOND = "CountPerSecond"
        MILLISECONDS = "Milliseconds"
        PERCENT = "Percent"
        SECONDS = "Seconds"


    class azure.mgmt.cognitiveservices.models.UpgradeAvailabilityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        NOT_AVAILABLE = "NotAvailable"


    class azure.mgmt.cognitiveservices.models.Usage(_Model):
        current_value: Optional[float]
        limit: Optional[float]
        name: Optional[MetricName]
        next_reset_time: Optional[str]
        quota_period: Optional[str]
        scope_id: Optional[str]
        scope_type: Optional[Union[str, QuotaScopeType]]
        status: Optional[Union[str, QuotaUsageStatus]]
        unit: Optional[Union[str, UnitType]]

        @overload
        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                limit: Optional[float] = ..., 
                name: Optional[MetricName] = ..., 
                next_reset_time: Optional[str] = ..., 
                quota_period: Optional[str] = ..., 
                scope_id: Optional[str] = ..., 
                scope_type: Optional[Union[str, QuotaScopeType]] = ..., 
                status: Optional[Union[str, QuotaUsageStatus]] = ..., 
                unit: Optional[Union[str, UnitType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.UsageListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[Usage]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[Usage]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.cognitiveservices.models.UserOwnedAmlWorkspace(_Model):
        identity_client_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_client_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.UserOwnedStorage(_Model):
        identity_client_id: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity_client_id: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.UsernamePasswordAuthTypeConnectionProperties(ConnectionPropertiesV2, discriminator='UsernamePassword'):
        auth_type: Literal[ConnectionAuthType.USERNAME_PASSWORD]
        category: Union[str, ConnectionCategory]
        created_by_workspace_arm_id: str
        credentials: Optional[ConnectionUsernamePassword]
        error: str
        expiry_time: datetime
        group: Union[str, ConnectionGroup]
        is_shared_to_all: bool
        metadata: dict[str, str]
        pe_requirement: Union[str, ManagedPERequirement]
        pe_status: Union[str, ManagedPEStatus]
        shared_user_list: list[str]
        target: str
        use_workspace_managed_identity: bool

        @overload
        def __init__(
                self, 
                *, 
                category: Optional[Union[str, ConnectionCategory]] = ..., 
                credentials: Optional[ConnectionUsernamePassword] = ..., 
                error: Optional[str] = ..., 
                expiry_time: Optional[datetime] = ..., 
                is_shared_to_all: Optional[bool] = ..., 
                metadata: Optional[dict[str, str]] = ..., 
                pe_requirement: Optional[Union[str, ManagedPERequirement]] = ..., 
                pe_status: Optional[Union[str, ManagedPEStatus]] = ..., 
                shared_user_list: Optional[list[str]] = ..., 
                target: Optional[str] = ..., 
                use_workspace_managed_identity: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.VersionedAgentReference(AgentReferenceProperties):
        agent_id: str
        agent_name: str
        agent_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                agent_id: Optional[str] = ..., 
                agent_name: Optional[str] = ..., 
                agent_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.VirtualNetworkRule(_Model):
        id: str
        ignore_missing_vnet_service_endpoint: Optional[bool]
        state: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: str, 
                ignore_missing_vnet_service_endpoint: Optional[bool] = ..., 
                state: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.VmPriority(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REGULAR = "Regular"
        SPOT = "Spot"


    class azure.mgmt.cognitiveservices.models.Workbench(ProxyResource):
        etag: Optional[str]
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: WorkbenchProperties
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: WorkbenchProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.WorkbenchProperties(_Model):
        connectivity_endpoints: Optional[ConnectivityEndpoints]
        creation_time: Optional[datetime]
        dataset_id: Optional[str]
        errors: Optional[list[ErrorDetail]]
        idle_time_before_shutdown: Optional[str]
        image_link: str
        provisioning_state: Optional[Union[str, ComputeProvisioningState]]
        ssh_settings: Optional[SshSettings]
        target_cluster_id: str
        web_endpoint: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dataset_id: Optional[str] = ..., 
                idle_time_before_shutdown: Optional[str] = ..., 
                image_link: str, 
                ssh_settings: Optional[SshSettings] = ..., 
                target_cluster_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.cognitiveservices.operations

    class azure.mgmt.cognitiveservices.operations.AccountCapabilityHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: CapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapabilityHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: CapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapabilityHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                capability_host: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CapabilityHost]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> CapabilityHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CapabilityHost]: ...


    class azure.mgmt.cognitiveservices.operations.AccountConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                category: Optional[str] = ..., 
                include_all: bool = False, 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConnectionPropertiesV2BasicResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...


    class azure.mgmt.cognitiveservices.operations.AccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: Account, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                account: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Account]: ...

        @overload
        def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: EvaluateDeploymentPoliciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @overload
        def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: EvaluateDeploymentPoliciesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @overload
        def evaluate_deployment_policies(
                self, 
                resource_group_name: str, 
                account_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EvaluateDeploymentPoliciesResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Account]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Account]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ApiKeys: ...

        @distributed_trace
        def list_models(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AccountModel]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> AccountSkuListResult: ...

        @distributed_trace
        def list_usages(
                self, 
                resource_group_name: str, 
                account_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> UsageListResult: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: RegenerateKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...

        @overload
        def regenerate_key(
                self, 
                resource_group_name: str, 
                account_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApiKeys: ...


    class azure.mgmt.cognitiveservices.operations.AgentApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: AgentApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: AgentApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentApplication]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def disable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def enable(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AgentApplication: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                *, 
                count: int = 30, 
                names: Optional[List[str]] = ..., 
                order_by: Optional[str] = ..., 
                order_by_asc: bool = False, 
                search_text: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentApplication]: ...

        @distributed_trace
        def list_agents(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AgentReferenceResourceArmPaginatedResult: ...


    class azure.mgmt.cognitiveservices.operations.AgentDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: AgentDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: AgentDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AgentDeployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> AgentDeployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                *, 
                count: int = 30, 
                names: Optional[List[str]] = ..., 
                order_by: Optional[str] = ..., 
                order_by_asc: bool = False, 
                skip_token: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AgentDeployment]: ...

        @distributed_trace
        def start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                app_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.cognitiveservices.operations.ArcDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ArcDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ArcDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name']}, api_versions_list=['2026-07-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: ArcDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: ArcDeploymentUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ArcDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name', 'accept']}, api_versions_list=['2026-07-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ArcDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-07-15-preview', params_added_on={'2026-07-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ArcDeployment]: ...


    class azure.mgmt.cognitiveservices.operations.CommitmentPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: CommitmentPlanAccountAssociation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: CommitmentPlanAccountAssociation, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        def begin_create_or_update_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                association: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlanAccountAssociation]: ...

        @overload
        def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @overload
        def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @overload
        def begin_create_or_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @overload
        def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @overload
        def begin_update_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CommitmentPlan]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: CommitmentPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                commitment_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace
        def get_association(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                commitment_plan_association_name: str, 
                **kwargs: Any
            ) -> CommitmentPlanAccountAssociation: ...

        @distributed_trace
        def get_plan(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> CommitmentPlan: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommitmentPlan]: ...

        @distributed_trace
        def list_associations(
                self, 
                resource_group_name: str, 
                commitment_plan_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommitmentPlanAccountAssociation]: ...

        @distributed_trace
        def list_plans_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CommitmentPlan]: ...

        @distributed_trace
        def list_plans_by_subscription(self, **kwargs: Any) -> ItemPaged[CommitmentPlan]: ...


    class azure.mgmt.cognitiveservices.operations.CommitmentTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[CommitmentTier]: ...


    class azure.mgmt.cognitiveservices.operations.ComputeOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-01-15-preview', '2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ComputeOperationStatus: ...


    class azure.mgmt.cognitiveservices.operations.ComputesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: Compute, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Compute]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: Compute, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Compute]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Compute]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_restart(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'compute_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                compute_name: str, 
                **kwargs: Any
            ) -> Compute: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Compute]: ...


    class azure.mgmt.cognitiveservices.operations.DefenderForAISettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DefenderForAISetting]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: DefenderForAISetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                defender_for_ai_setting_name: str, 
                defender_for_ai_settings: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefenderForAISetting: ...


    class azure.mgmt.cognitiveservices.operations.DeletedAccountsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_purge(
                self, 
                location: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> Account: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Account]: ...


    class azure.mgmt.cognitiveservices.operations.DeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: Deployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: PatchResourceTagsAndSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                deployment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Deployment]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Deployment]: ...

        @distributed_trace
        def list_skus(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SkuResource]: ...

        @distributed_trace
        def pause(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...

        @distributed_trace
        def resume(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> Deployment: ...


    class azure.mgmt.cognitiveservices.operations.EncryptionScopesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: EncryptionScope, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                encryption_scope: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                encryption_scope_name: str, 
                **kwargs: Any
            ) -> EncryptionScope: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EncryptionScope]: ...


    class azure.mgmt.cognitiveservices.operations.LocationBasedModelCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                model_format: str, 
                model_name: str, 
                model_version: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelCapacityListResultValueItem]: ...


    class azure.mgmt.cognitiveservices.operations.ManagedComputeCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'offer', 'accelerator_type', 'deployment_id', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                *, 
                accelerator_type: Optional[str] = ..., 
                deployment_id: Optional[str] = ..., 
                offer: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedComputeCapacity]: ...


    class azure.mgmt.cognitiveservices.operations.ManagedComputeDeploymentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ManagedComputeDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: ManagedComputeDeployment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: PatchResourceSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: PatchResourceSku, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedComputeDeployment]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'deployment_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                deployment_name: str, 
                **kwargs: Any
            ) -> ManagedComputeDeployment: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedComputeDeployment]: ...


    class azure.mgmt.cognitiveservices.operations.ManagedComputeUsagesOperationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'location', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedComputeUsage]: ...


    class azure.mgmt.cognitiveservices.operations.ManagedNetworkProvisionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkProvisionOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkProvisionStatus]: ...

        @overload
        def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkProvisionOptions] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkProvisionStatus]: ...

        @overload
        def begin_provision_managed_network(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkProvisionStatus]: ...


    class azure.mgmt.cognitiveservices.operations.ManagedNetworkSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'managed_network_name']}, api_versions_list=['2026-01-15-preview', '2026-03-01', '2026-03-15-preview', '2026-05-01', '2026-05-15-preview', '2026-07-01', '2026-07-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkSettingsPropertiesBasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[ManagedNetworkSettingsPropertiesBasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsPropertiesBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsPropertiesBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @overload
        def begin_put(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagedNetworkSettingsPropertiesBasicResource]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> ManagedNetworkSettingsPropertiesBasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ManagedNetworkSettingsPropertiesBasicResource]: ...


    class azure.mgmt.cognitiveservices.operations.ModelCapacitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                model_format: str, 
                model_name: str, 
                model_version: str, 
                **kwargs: Any
            ) -> ItemPaged[ModelCapacityListResultValueItem]: ...


    class azure.mgmt.cognitiveservices.operations.ModelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Model]: ...


    class azure.mgmt.cognitiveservices.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_reconcile(
                self, 
                resource_group_name: str, 
                account_name: str, 
                nsp_configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                nsp_configuration_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.cognitiveservices.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.cognitiveservices.operations.OutboundRuleOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: OutboundRuleBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OutboundRuleBasicResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: OutboundRuleBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OutboundRuleBasicResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OutboundRuleBasicResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> OutboundRuleBasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                **kwargs: Any
            ) -> ItemPaged[OutboundRuleBasicResource]: ...


    class azure.mgmt.cognitiveservices.operations.OutboundRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[OutboundRuleBasicResource]]: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: ManagedNetworkSettingsBasicResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[OutboundRuleBasicResource]]: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ItemPaged[OutboundRuleBasicResource]]: ...


    class azure.mgmt.cognitiveservices.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionListResult: ...


    class azure.mgmt.cognitiveservices.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.cognitiveservices.operations.ProjectCapabilityHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: ProjectCapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectCapabilityHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: ProjectCapabilityHost, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectCapabilityHost]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                capability_host: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProjectCapabilityHost]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                capability_host_name: str, 
                **kwargs: Any
            ) -> ProjectCapabilityHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProjectCapabilityHost]: ...


    class azure.mgmt.cognitiveservices.operations.ProjectConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionPropertiesV2BasicResource] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                *, 
                category: Optional[str] = ..., 
                include_all: bool = False, 
                target: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConnectionPropertiesV2BasicResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[ConnectionUpdateContent] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                connection_name: str, 
                connection: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConnectionPropertiesV2BasicResource: ...


    class azure.mgmt.cognitiveservices.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                project: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Project]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...


    class azure.mgmt.cognitiveservices.operations.QuotaTiersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        def create_or_update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        def create_or_update(
                self, 
                default: str, 
                tier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @distributed_trace
        def get(
                self, 
                default: str, 
                **kwargs: Any
            ) -> QuotaTier: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[QuotaTier]: ...

        @overload
        def update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        def update(
                self, 
                default: str, 
                tier: QuotaTier, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...

        @overload
        def update(
                self, 
                default: str, 
                tier: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> QuotaTier: ...


    class azure.mgmt.cognitiveservices.operations.RaiBlocklistItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: List[RaiBlocklistItemBulkRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: List[RaiBlocklistItemBulkRequest], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        def batch_add(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        def batch_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items_names: List[str], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def batch_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_items_names: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: RaiBlocklistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: RaiBlocklistItem, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                rai_blocklist_item: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist_item_name: str, 
                **kwargs: Any
            ) -> RaiBlocklistItem: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiBlocklistItem]: ...


    class azure.mgmt.cognitiveservices.operations.RaiBlocklistsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: RaiBlocklist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: RaiBlocklist, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                rai_blocklist: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_blocklist_name: str, 
                **kwargs: Any
            ) -> RaiBlocklist: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiBlocklist]: ...


    class azure.mgmt.cognitiveservices.operations.RaiContentFiltersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                filter_name: str, 
                **kwargs: Any
            ) -> RaiContentFilter: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiContentFilter]: ...


    class azure.mgmt.cognitiveservices.operations.RaiExternalSafetyProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                safety_provider_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @distributed_trace
        def get(
                self, 
                safety_provider_name: str, 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...


    class azure.mgmt.cognitiveservices.operations.RaiExternalSafetyProvidersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[RaiExternalSafetyProviderSchema]: ...


    class azure.mgmt.cognitiveservices.operations.RaiPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                rai_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiPolicy]: ...


    class azure.mgmt.cognitiveservices.operations.RaiToolLabelsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: RaiToolLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: RaiToolLabel, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                rai_tool_label: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_tool_connection_name: str, 
                **kwargs: Any
            ) -> RaiToolLabel: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiToolLabel]: ...


    class azure.mgmt.cognitiveservices.operations.RaiTopicsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: RaiTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: RaiTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                rai_topic: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiTopic: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                rai_topic_name: str, 
                **kwargs: Any
            ) -> RaiTopic: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RaiTopic]: ...


    class azure.mgmt.cognitiveservices.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.cognitiveservices.operations.SubscriptionRaiPolicyOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: RaiPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @overload
        def create_or_update(
                self, 
                rai_policy_name: str, 
                rai_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiPolicy: ...

        @distributed_trace
        def get(
                self, 
                rai_policy_name: str, 
                **kwargs: Any
            ) -> RaiPolicy: ...


    class azure.mgmt.cognitiveservices.operations.TestRaiExternalSafetyProviderOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: RaiExternalSafetyProviderSchema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RaiExternalSafetyProviderSchema: ...


    class azure.mgmt.cognitiveservices.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cognitiveservices.operations.WorkbenchesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_restart(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_start(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def begin_stop(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: Workbench, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Workbench]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'workbench_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def get(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                workbench_name: str, 
                **kwargs: Any
            ) -> Workbench: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-15-preview', params_added_on={'2026-03-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'project_name', 'accept']}, api_versions_list=['2026-03-15-preview', '2026-05-15-preview', '2026-07-15-preview'])
        def list(
                self, 
                resource_group_name: str, 
                account_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Workbench]: ...


namespace azure.mgmt.cognitiveservices.types

    class azure.mgmt.cognitiveservices.types.AADAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.AAD]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.AAD]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.AbusePenalty(TypedDict, total=False):
        key "action": Union[str, AbusePenaltyAction]
        key "expiration": str
        key "rateLimitPercentage": float
        action: Union[str, AbusePenaltyAction]
        expiration: str
        rateLimitPercentage: float


    class azure.mgmt.cognitiveservices.types.AccessKeyAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.ACCESS_KEY]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionAccessKey', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.ACCESS_KEY]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionAccessKey
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.Account(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('AccountProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        kind: str
        location: str
        name: str
        properties: AccountProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.AccountKeyAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.ACCOUNT_KEY]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionAccountKey', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.ACCOUNT_KEY]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionAccountKey
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.AccountProperties(TypedDict, total=False):
        key "a365LoggingEnabled": bool
        key "abusePenalty": ForwardRef('AbusePenalty', module='types')
        key "allowProjectManagement": bool
        key "amlWorkspace": ForwardRef('UserOwnedAmlWorkspace', module='types')
        key "apiProperties": ForwardRef('ApiProperties', module='types')
        key "callRateLimit": ForwardRef('CallRateLimit', module='types')
        key "capabilitySettings": ForwardRef('CapabilitySettings', module='types')
        key "customSubDomainName": str
        key "dateCreated": str
        key "defaultProject": str
        key "deletionDate": str
        key "disableLocalAuth": bool
        key "dynamicThrottlingEnabled": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "endpoint": str
        key "foundryAutoUpgrade": ForwardRef('FoundryAutoUpgrade', module='types')
        key "internalId": str
        key "isMigrated": bool
        key "locations": ForwardRef('MultiRegionSettings', module='types')
        key "migrationToken": str
        key "networkAcls": ForwardRef('NetworkRuleSet', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "quotaLimit": ForwardRef('QuotaLimit', module='types')
        key "raiMonitorConfig": ForwardRef('RaiMonitorConfig', module='types')
        key "restore": bool
        key "restrictOutboundNetworkAccess": bool
        key "scheduledPurgeDate": str
        key "skuChangeInfo": ForwardRef('SkuChangeInfo', module='types')
        key "storedCompletionsDisabled": bool
        a365LoggingEnabled: bool
        abusePenalty: AbusePenalty
        agentHostingConfigurations: list[AgentHostingConfiguration]
        allowProjectManagement: bool
        allowedFqdnList: list[str]
        amlWorkspace: UserOwnedAmlWorkspace
        apiProperties: ApiProperties
        associatedProjects: list[str]
        callRateLimit: CallRateLimit
        capabilities: list[SkuCapability]
        capabilitySettings: CapabilitySettings
        commitmentPlanAssociations: list[CommitmentPlanAssociation]
        customSubDomainName: str
        dateCreated: str
        defaultProject: str
        deletionDate: str
        disableLocalAuth: bool
        dynamicThrottlingEnabled: bool
        encryption: Encryption
        endpoint: str
        endpoints: dict[str, str]
        foundryAutoUpgrade: FoundryAutoUpgrade
        internalId: str
        isMigrated: bool
        locations: MultiRegionSettings
        migrationToken: str
        networkAcls: NetworkRuleSet
        networkInjections: list[NetworkInjection]
        privateEndpointConnections: list[PrivateEndpointConnection]
        provisioningState: Union[str, ProvisioningState]
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        quotaLimit: QuotaLimit
        raiMonitorConfig: RaiMonitorConfig
        restore: bool
        restrictOutboundNetworkAccess: bool
        scheduledPurgeDate: str
        skuChangeInfo: SkuChangeInfo
        storedCompletionsDisabled: bool
        userOwnedStorage: list[UserOwnedStorage]


    class azure.mgmt.cognitiveservices.types.AgentApplication(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[AgenticApplicationProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgenticApplicationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.AgentDeployment(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[AgentDeploymentProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AgentDeploymentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.AgentDeploymentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM = "Custom"
        HOSTED = "Hosted"
        MANAGED = "Managed"


    class azure.mgmt.cognitiveservices.types.AgentHostingConfiguration(TypedDict, total=False):
        key "clusterResourceId": Required[str]
        key "hostingManagementIdentityResourceId": Required[str]
        key "hostingType": Required[Literal[AgentHostingType.MANAGED_CLUSTER]]
        key "name": Required[str]
        key "storageAccountResourceId": Required[str]
        key "workloadIdentityResourceId": Required[str]
        clusterResourceId: str
        hostingManagementIdentityResourceId: str
        hostingType: Literal[AgentHostingType.MANAGED_CLUSTER]
        name: str
        storageAccountResourceId: str
        workloadIdentityResourceId: str


    class azure.mgmt.cognitiveservices.types.AgentHostingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MANAGED_CLUSTER = "ManagedCluster"


    class azure.mgmt.cognitiveservices.types.AgentProtocolVersion(TypedDict, total=False):
        key "protocol": Union[str, AgentProtocol]
        key "version": Optional[str]
        protocol: Union[str, AgentProtocol]
        version: str


    class azure.mgmt.cognitiveservices.types.AgentReferenceProperties(TypedDict, total=False):
        key "agentId": Optional[str]
        key "agentName": Optional[str]
        agentId: str
        agentName: str


    class azure.mgmt.cognitiveservices.types.AgenticApplicationProperties(ResourceBase):
        key "agentIdentityBlueprint": Optional[AssignedIdentity]
        key "agents": Optional[list[AgentReferenceProperties]]
        key "authorizationPolicy": Optional[ApplicationAuthorizationPolicy]
        key "baseUrl": Optional[str]
        key "defaultInstanceIdentity": Optional[AssignedIdentity]
        key "description": Optional[str]
        key "displayName": Optional[str]
        key "isEnabled": bool
        key "provisioningState": Union[str, AgenticApplicationProvisioningState]
        key "tags": Optional[dict[str, str]]
        key "trafficRoutingPolicy": Optional[ApplicationTrafficRoutingPolicy]
        agentIdentityBlueprint: AssignedIdentity
        agents: list[AgentReferenceProperties]
        authorizationPolicy: ApplicationAuthorizationPolicy
        baseUrl: str
        defaultInstanceIdentity: AssignedIdentity
        description: str
        displayName: str
        isEnabled: bool
        provisioningState: Union[str, AgenticApplicationProvisioningState]
        tags: dict[str, str]
        trafficRoutingPolicy: ApplicationTrafficRoutingPolicy


    class azure.mgmt.cognitiveservices.types.ApiKeyAuthConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.API_KEY]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionApiKey', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.API_KEY]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionApiKey
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.ApiProperties(TypedDict, total=False):
        key "aadClientId": str
        key "aadTenantId": str
        key "eventHubConnectionString": str
        key "qnaAzureSearchEndpointId": str
        key "qnaAzureSearchEndpointKey": str
        key "qnaRuntimeEndpoint": str
        key "statisticsEnabled": bool
        key "storageAccountConnectionString": str
        key "superUser": str
        key "websiteName": str
        aadClientId: str
        aadTenantId: str
        eventHubConnectionString: str
        qnaAzureSearchEndpointId: str
        qnaAzureSearchEndpointKey: str
        qnaRuntimeEndpoint: str
        statisticsEnabled: bool
        storageAccountConnectionString: str
        superUser: str
        websiteName: str


    class azure.mgmt.cognitiveservices.types.ApplicationTrafficRoutingPolicy(TypedDict, total=False):
        key "protocol": Union[str, TrafficRoutingProtocol]
        key "rules": Optional[list[TrafficRoutingRule]]
        protocol: Union[str, TrafficRoutingProtocol]
        rules: list[TrafficRoutingRule]


    class azure.mgmt.cognitiveservices.types.ArcDeployment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": Required[ArcDeploymentProperties]
        key "sku": Required[ArcDeploymentSku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ArcDeploymentProperties
        sku: ArcDeploymentSku
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentCpuMemoryResourceRequirements(TypedDict, total=False):
        key "cpu": Required[str]
        key "memory": Required[str]
        cpu: str
        memory: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentKubernetesResources(TypedDict, total=False):
        key "limits": ForwardRef('ArcDeploymentResourceRequirements', module='types')
        key "requests": ForwardRef('ArcDeploymentCpuMemoryResourceRequirements', module='types')
        limits: ArcDeploymentResourceRequirements
        requests: ArcDeploymentCpuMemoryResourceRequirements


    class azure.mgmt.cognitiveservices.types.ArcDeploymentModel(TypedDict, total=False):
        key "format": Required[str]
        key "name": Required[str]
        format: str
        name: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentPatchCpuMemoryResourceRequirements(TypedDict, total=False):
        key "cpu": str
        key "memory": str
        cpu: str
        memory: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentPatchKubernetesResources(TypedDict, total=False):
        key "limits": ForwardRef('ArcDeploymentResourceRequirements', module='types')
        key "requests": ForwardRef('ArcDeploymentPatchCpuMemoryResourceRequirements', module='types')
        limits: ArcDeploymentResourceRequirements
        requests: ArcDeploymentPatchCpuMemoryResourceRequirements


    class azure.mgmt.cognitiveservices.types.ArcDeploymentProperties(TypedDict, total=False):
        key "compute": Required[Union[str, ArcDeploymentComputeType]]
        key "deploymentState": Union[str, DeploymentState]
        key "deploymentTemplate": str
        key "extensionId": Required[str]
        key "inferenceEndpoint": str
        key "model": Required[ArcDeploymentModel]
        key "provisioningDetails": ForwardRef('ArcDeploymentProvisioningDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "raiPolicyName": str
        key "replicas": Required[int]
        key "resources": Required[ArcDeploymentKubernetesResources]
        key "runtime": Required[Union[str, ArcDeploymentRuntime]]
        key "vllmParameters": ForwardRef('ArcDeploymentVllmParameters', module='types')
        capabilities: dict[str, str]
        compute: Union[str, ArcDeploymentComputeType]
        deploymentState: Union[str, DeploymentState]
        deploymentTemplate: str
        extensionId: str
        inferenceEndpoint: str
        model: ArcDeploymentModel
        nodeSelector: dict[str, str]
        provisioningDetails: ArcDeploymentProvisioningDetails
        provisioningState: Union[str, ProvisioningState]
        raiPolicyName: str
        replicas: int
        resources: ArcDeploymentKubernetesResources
        runtime: Union[str, ArcDeploymentRuntime]
        vllmParameters: ArcDeploymentVllmParameters


    class azure.mgmt.cognitiveservices.types.ArcDeploymentProvisioningDetails(TypedDict, total=False):
        key "lastOperationTimestamp": str
        key "message": str
        lastOperationTimestamp: str
        message: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentResourceRequirements(TypedDict, total=False):
        key "cpu": str
        key "gpu": int
        key "memory": str
        cpu: str
        gpu: int
        memory: str


    class azure.mgmt.cognitiveservices.types.ArcDeploymentSku(TypedDict, total=False):
        key "name": Required[Union[str, ArcDeploymentSkuName]]
        name: Union[str, ArcDeploymentSkuName]


    class azure.mgmt.cognitiveservices.types.ArcDeploymentUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ArcDeploymentUpdateProperties', module='types')
        properties: ArcDeploymentUpdateProperties


    class azure.mgmt.cognitiveservices.types.ArcDeploymentUpdateProperties(TypedDict, total=False):
        key "replicas": int
        key "resources": ForwardRef('ArcDeploymentPatchKubernetesResources', module='types')
        nodeSelector: dict[str, str]
        replicas: int
        resources: ArcDeploymentPatchKubernetesResources


    class azure.mgmt.cognitiveservices.types.ArcDeploymentVllmParameters(TypedDict, total=False):
        key "enforceEager": bool
        key "gpuMemoryUtilization": float
        key "maxModelLen": int
        key "tensorParallelSize": int
        enforceEager: bool
        gpuMemoryUtilization: float
        maxModelLen: int
        tensorParallelSize: int


    class azure.mgmt.cognitiveservices.types.AssignedIdentity(TypedDict, total=False):
        key "clientId": Required[str]
        key "kind": Required[Union[str, IdentityKind]]
        key "principalId": Required[str]
        key "provisioningState": Union[str, IdentityProvisioningState]
        key "subject": Optional[str]
        key "tenantId": Required[str]
        key "type": Required[Union[str, IdentityManagementType]]
        clientId: str
        kind: Union[str, IdentityKind]
        principalId: str
        provisioningState: Union[str, IdentityProvisioningState]
        subject: str
        tenantId: str
        type: Union[str, IdentityManagementType]


    class azure.mgmt.cognitiveservices.types.BuiltInAuthorizationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CHANNELS = "Channels"
        CUSTOM = "Custom"
        DEFAULT = "Default"
        ORGANIZATION_SCOPE = "OrganizationScope"


    class azure.mgmt.cognitiveservices.types.CalculateModelCapacityParameter(TypedDict, total=False):
        key "model": ForwardRef('DeploymentModel', module='types')
        key "skuName": str
        model: DeploymentModel
        skuName: str
        workloads: list[ModelCapacityCalculatorWorkload]


    class azure.mgmt.cognitiveservices.types.CallRateLimit(TypedDict, total=False):
        key "count": float
        key "renewalPeriod": float
        count: float
        renewalPeriod: float
        rules: list[ThrottlingRule]


    class azure.mgmt.cognitiveservices.types.CapabilityHost(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CapabilityHostProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CapabilityHostProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.CapabilityHostProperties(ResourceBase):
        key "aiServicesConnections": Optional[list[str]]
        key "capabilityHostKind": Union[str, CapabilityHostKind]
        key "customerSubnet": Optional[str]
        key "description": Optional[str]
        key "enablePublicHostingEnvironment": bool
        key "provisioningState": Union[str, CapabilityHostProvisioningState]
        key "storageConnections": Optional[list[str]]
        key "tags": Optional[dict[str, str]]
        key "threadStorageConnections": Optional[list[str]]
        key "vectorStoreConnections": Optional[list[str]]
        aiServicesConnections: list[str]
        capabilityHostKind: Union[str, CapabilityHostKind]
        customerSubnet: str
        description: str
        enablePublicHostingEnvironment: bool
        provisioningState: Union[str, CapabilityHostProvisioningState]
        storageConnections: list[str]
        tags: dict[str, str]
        threadStorageConnections: list[str]
        vectorStoreConnections: list[str]


    class azure.mgmt.cognitiveservices.types.CapabilitySettings(TypedDict, total=False):
        key "blobStore": str
        key "documentStore": str
        key "vectorStore": str
        blobStore: str
        documentStore: str
        vectorStore: str


    class azure.mgmt.cognitiveservices.types.ChannelsBuiltInAuthorizationPolicy(TypedDict, total=False):
        key "type": Required[Literal[BuiltInAuthorizationScheme.CHANNELS]]
        type: Literal[BuiltInAuthorizationScheme.CHANNELS]


    class azure.mgmt.cognitiveservices.types.CheckDomainAvailabilityParameter(TypedDict, total=False):
        key "kind": str
        key "subdomainName": Required[str]
        key "type": Required[str]
        kind: str
        subdomainName: str
        type: str


    class azure.mgmt.cognitiveservices.types.CheckSkuAvailabilityParameter(TypedDict, total=False):
        key "kind": Required[str]
        key "skus": Required[list[str]]
        key "type": Required[str]
        kind: str
        skus: list[str]
        type: str


    class azure.mgmt.cognitiveservices.types.ClusterComputeProperties(TypedDict, total=False):
        key "computeType": Required[Literal[ComputeType.CLUSTER]]
        key "creationTime": str
        key "location": Required[str]
        key "pools": Required[list[Pool]]
        key "provisioningState": Union[str, ComputeProvisioningState]
        key "subnetArmId": str
        computeType: Literal[ComputeType.CLUSTER]
        creationTime: str
        errors: list[ErrorDetail]
        location: str
        pools: list[Pool]
        provisioningState: Union[str, ComputeProvisioningState]
        subnetArmId: str


    class azure.mgmt.cognitiveservices.types.CommitmentPeriod(TypedDict, total=False):
        key "count": int
        key "endDate": str
        key "quota": ForwardRef('CommitmentQuota', module='types')
        key "startDate": str
        key "tier": str
        count: int
        endDate: str
        quota: CommitmentQuota
        startDate: str
        tier: str


    class azure.mgmt.cognitiveservices.types.CommitmentPlan(ProxyResource):
        key "etag": str
        key "id": str
        key "kind": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('CommitmentPlanProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        kind: str
        location: str
        name: str
        properties: CommitmentPlanProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.CommitmentPlanAccountAssociation(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('CommitmentPlanAccountAssociationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: CommitmentPlanAccountAssociationProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.CommitmentPlanAccountAssociationProperties(TypedDict, total=False):
        key "accountId": str
        accountId: str


    class azure.mgmt.cognitiveservices.types.CommitmentPlanAssociation(TypedDict, total=False):
        key "commitmentPlanId": str
        key "commitmentPlanLocation": str
        commitmentPlanId: str
        commitmentPlanLocation: str


    class azure.mgmt.cognitiveservices.types.CommitmentPlanProperties(TypedDict, total=False):
        key "autoRenew": bool
        key "commitmentPlanGuid": str
        key "current": ForwardRef('CommitmentPeriod', module='types')
        key "hostingModel": Union[str, HostingModel]
        key "last": ForwardRef('CommitmentPeriod', module='types')
        key "next": ForwardRef('CommitmentPeriod', module='types')
        key "planType": str
        key "provisioningState": Union[str, CommitmentPlanProvisioningState]
        autoRenew: bool
        commitmentPlanGuid: str
        current: CommitmentPeriod
        hostingModel: Union[str, HostingModel]
        last: CommitmentPeriod
        next: CommitmentPeriod
        planType: str
        provisioningIssues: list[str]
        provisioningState: Union[str, CommitmentPlanProvisioningState]


    class azure.mgmt.cognitiveservices.types.CommitmentQuota(TypedDict, total=False):
        key "quantity": int
        key "unit": str
        quantity: int
        unit: str


    class azure.mgmt.cognitiveservices.types.Compute(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "kind": str
        key "name": str
        key "properties": Required[ComputeProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        kind: str
        name: str
        properties: ComputeProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.ComputeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        CONTAINER_INSTANCE = "ContainerInstance"


    class azure.mgmt.cognitiveservices.types.ConnectionAccessKey(TypedDict, total=False):
        key "accessKeyId": str
        key "secretAccessKey": str
        accessKeyId: str
        secretAccessKey: str


    class azure.mgmt.cognitiveservices.types.ConnectionAccountKey(TypedDict, total=False):
        key "key": str
        key: str


    class azure.mgmt.cognitiveservices.types.ConnectionApiKey(TypedDict, total=False):
        key "key": str
        key: str


    class azure.mgmt.cognitiveservices.types.ConnectionAuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "AAD"
        ACCESS_KEY = "AccessKey"
        ACCOUNT_KEY = "AccountKey"
        ACCOUNT_MANAGED_IDENTITY = "AccountManagedIdentity"
        AGENTIC_IDENTITY_TOKEN = "AgenticIdentityToken"
        AGENTIC_USER = "AgenticUser"
        AGENT_USER_IMPERSONATION = "AgentUserImpersonation"
        API_KEY = "ApiKey"
        CUSTOM_KEYS = "CustomKeys"
        DELEGATED_SAS = "DelegatedSAS"
        MANAGED_IDENTITY = "ManagedIdentity"
        NONE = "None"
        O_AUTH2 = "OAuth2"
        PAT = "PAT"
        PROJECT_MANAGED_IDENTITY = "ProjectManagedIdentity"
        SAS = "SAS"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        USERNAME_PASSWORD = "UsernamePassword"
        USER_ENTRA_TOKEN = "UserEntraToken"


    class azure.mgmt.cognitiveservices.types.ConnectionManagedIdentity(TypedDict, total=False):
        key "clientId": str
        key "resourceId": str
        clientId: str
        resourceId: str


    class azure.mgmt.cognitiveservices.types.ConnectionOAuth2(TypedDict, total=False):
        key "authUrl": str
        key "clientId": str
        key "clientSecret": str
        key "developerToken": str
        key "password": str
        key "refreshToken": str
        key "tenantId": str
        key "username": str
        authUrl: str
        clientId: str
        clientSecret: str
        developerToken: str
        password: str
        refreshToken: str
        tenantId: str
        username: str


    class azure.mgmt.cognitiveservices.types.ConnectionPersonalAccessToken(TypedDict, total=False):
        key "pat": str
        pat: str


    class azure.mgmt.cognitiveservices.types.ConnectionPropertiesV2BasicResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ConnectionPropertiesV2]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ConnectionPropertiesV2
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ConnectionServicePrincipal(TypedDict, total=False):
        key "clientId": str
        key "clientSecret": str
        key "tenantId": str
        clientId: str
        clientSecret: str
        tenantId: str


    class azure.mgmt.cognitiveservices.types.ConnectionSharedAccessSignature(TypedDict, total=False):
        key "sas": str
        sas: str


    class azure.mgmt.cognitiveservices.types.ConnectionUpdateContent(TypedDict, total=False):
        key "properties": ForwardRef('ConnectionPropertiesV2', module='types')
        properties: ConnectionPropertiesV2


    class azure.mgmt.cognitiveservices.types.ConnectionUsernamePassword(TypedDict, total=False):
        key "password": str
        key "securityToken": str
        key "username": str
        password: str
        securityToken: str
        username: str


    class azure.mgmt.cognitiveservices.types.ConnectivityEndpoints(TypedDict, total=False):
        key "publicIpAddress": str
        key "sshPort": int
        publicIpAddress: str
        sshPort: int


    class azure.mgmt.cognitiveservices.types.ContainerInstanceComputeProperties(TypedDict, total=False):
        key "computeType": Required[Literal[ComputeType.CONTAINER_INSTANCE]]
        key "connectivityEndpoints": ForwardRef('ConnectivityEndpoints', module='types')
        key "creationTime": str
        key "idleTimeBeforeShutdown": str
        key "imageLink": Required[str]
        key "location": Required[str]
        key "provisioningState": Union[str, ComputeProvisioningState]
        key "sshSettings": ForwardRef('SshSettings', module='types')
        key "targetClusterId": Required[str]
        computeType: Literal[ComputeType.CONTAINER_INSTANCE]
        connectivityEndpoints: ConnectivityEndpoints
        creationTime: str
        errors: list[ErrorDetail]
        idleTimeBeforeShutdown: str
        imageLink: str
        location: str
        provisioningState: Union[str, ComputeProvisioningState]
        sshSettings: SshSettings
        targetClusterId: str


    class azure.mgmt.cognitiveservices.types.CustomBlocklistConfig(RaiBlocklistConfig):
        key "blocking": bool
        key "blocklistName": str
        key "source": Union[str, RaiPolicyContentSource]
        blocking: bool
        blocklistName: str
        source: Union[str, RaiPolicyContentSource]


    class azure.mgmt.cognitiveservices.types.CustomKeys(TypedDict, total=False):
        keys: dict[str, str]


    class azure.mgmt.cognitiveservices.types.CustomKeysConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.CUSTOM_KEYS]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('CustomKeys', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.CUSTOM_KEYS]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: CustomKeys
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.DefenderForAISetting(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('DefenderForAISettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: DefenderForAISettingProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.DefenderForAISettingProperties(TypedDict, total=False):
        key "state": Union[str, DefenderForAISettingState]
        state: Union[str, DefenderForAISettingState]


    class azure.mgmt.cognitiveservices.types.Deployment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('DeploymentProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: DeploymentProperties
        sku: Sku
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.DeploymentCapacitySettings(TypedDict, total=False):
        key "designatedCapacity": int
        key "priority": int
        designatedCapacity: int
        priority: int


    class azure.mgmt.cognitiveservices.types.DeploymentModel(TypedDict, total=False):
        key "callRateLimit": ForwardRef('CallRateLimit', module='types')
        key "format": str
        key "name": str
        key "publisher": str
        key "source": str
        key "sourceAccount": str
        key "version": str
        callRateLimit: CallRateLimit
        format: str
        name: str
        publisher: str
        source: str
        sourceAccount: str
        version: str


    class azure.mgmt.cognitiveservices.types.DeploymentProperties(TypedDict, total=False):
        key "callRateLimit": ForwardRef('CallRateLimit', module='types')
        key "capacitySettings": ForwardRef('DeploymentCapacitySettings', module='types')
        key "contextCacheContainerId": str
        key "currentCapacity": int
        key "deploymentState": Optional[Union[str, DeploymentState]]
        key "dynamicThrottlingEnabled": bool
        key "model": ForwardRef('DeploymentModel', module='types')
        key "parentDeploymentName": str
        key "provisioningState": Union[str, DeploymentProvisioningState]
        key "raiPolicyName": str
        key "routing": ForwardRef('DeploymentRouting', module='types')
        key "scaleSettings": ForwardRef('DeploymentScaleSettings', module='types')
        key "serviceTier": Optional[Union[str, ServiceTier]]
        key "speculativeDecoding": ForwardRef('DeploymentSpeculativeDecoding', module='types')
        key "spilloverDeploymentName": str
        key "versionUpgradeOption": Union[str, DeploymentModelVersionUpgradeOption]
        callRateLimit: CallRateLimit
        capabilities: dict[str, str]
        capacitySettings: DeploymentCapacitySettings
        contextCacheContainerId: str
        currentCapacity: int
        deploymentState: Union[str, DeploymentState]
        dynamicThrottlingEnabled: bool
        model: DeploymentModel
        parentDeploymentName: str
        provisioningState: Union[str, DeploymentProvisioningState]
        raiPolicyName: str
        rateLimits: list[ThrottlingRule]
        routing: DeploymentRouting
        scaleSettings: DeploymentScaleSettings
        serviceTier: Union[str, ServiceTier]
        speculativeDecoding: DeploymentSpeculativeDecoding
        spilloverDeploymentName: str
        versionUpgradeOption: Union[str, DeploymentModelVersionUpgradeOption]


    class azure.mgmt.cognitiveservices.types.DeploymentRouting(TypedDict, total=False):
        key "mode": Union[str, RoutingMode]
        mode: Union[str, RoutingMode]
        models: list[DeploymentModel]


    class azure.mgmt.cognitiveservices.types.DeploymentScaleSettings(TypedDict, total=False):
        key "activeCapacity": int
        key "capacity": int
        key "scaleType": Union[str, DeploymentScaleType]
        activeCapacity: int
        capacity: int
        scaleType: Union[str, DeploymentScaleType]


    class azure.mgmt.cognitiveservices.types.DeploymentSpeculativeDecoding(TypedDict, total=False):
        key "draftModel": Required[DeploymentModel]
        key "draftTokenCount": int
        draftModel: DeploymentModel
        draftTokenCount: int


    class azure.mgmt.cognitiveservices.types.Encryption(TypedDict, total=False):
        key "keySource": Union[str, KeySource]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        keySource: Union[str, KeySource]
        keyVaultProperties: KeyVaultProperties


    class azure.mgmt.cognitiveservices.types.EncryptionScope(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('EncryptionScopeProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: EncryptionScopeProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.EncryptionScopeProperties(Encryption):
        key "keySource": Union[str, KeySource]
        key "keyVaultProperties": ForwardRef('KeyVaultProperties', module='types')
        key "provisioningState": Union[str, EncryptionScopeProvisioningState]
        key "state": Union[str, EncryptionScopeState]
        keySource: Union[str, KeySource]
        keyVaultProperties: KeyVaultProperties
        provisioningState: Union[str, EncryptionScopeProvisioningState]
        state: Union[str, EncryptionScopeState]


    class azure.mgmt.cognitiveservices.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.cognitiveservices.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.cognitiveservices.types.EvaluateDeploymentPoliciesDeployment(TypedDict, total=False):
        key "name": Required[str]
        key "properties": Required[EvaluateDeploymentPoliciesDeploymentProperties]
        name: str
        properties: EvaluateDeploymentPoliciesDeploymentProperties


    class azure.mgmt.cognitiveservices.types.EvaluateDeploymentPoliciesDeploymentProperties(TypedDict, total=False):
        key "model": Required[DeploymentModel]
        key "raiPolicyName": str
        model: DeploymentModel
        raiPolicyName: str


    class azure.mgmt.cognitiveservices.types.EvaluateDeploymentPoliciesRequest(TypedDict, total=False):
        key "deployments": Required[list[EvaluateDeploymentPoliciesDeployment]]
        deployments: list[EvaluateDeploymentPoliciesDeployment]


    class azure.mgmt.cognitiveservices.types.FoundryAutoUpgrade(TypedDict, total=False):
        key "mode": Union[str, FoundryAutoUpgradeMode]
        key "plannedByMicrosoft": bool
        key "scheduledAt": str
        key "statusReason": str
        mode: Union[str, FoundryAutoUpgradeMode]
        plannedByMicrosoft: bool
        scheduledAt: str
        statusReason: str


    class azure.mgmt.cognitiveservices.types.FqdnOutboundRule(TypedDict, total=False):
        key "category": Union[str, RuleCategory]
        key "destination": str
        key "errorInformation": str
        key "status": Union[str, RuleStatus]
        key "type": Required[Literal[RuleType.FQDN]]
        category: Union[str, RuleCategory]
        destination: str
        errorInformation: str
        parentRuleNames: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.FQDN]


    class azure.mgmt.cognitiveservices.types.HostedAgentDeployment(TypedDict, total=False):
        key "agents": Optional[list[VersionedAgentReference]]
        key "deploymentId": Optional[str]
        key "deploymentType": Required[Literal[AgentDeploymentType.HOSTED]]
        key "description": Optional[str]
        key "displayName": Optional[str]
        key "maxReplicas": int
        key "minReplicas": int
        key "protocols": Optional[list[AgentProtocolVersion]]
        key "provisioningState": Union[str, AgentDeploymentProvisioningState]
        key "state": Optional[Union[str, AgentDeploymentState]]
        key "tags": Optional[dict[str, str]]
        agents: list[VersionedAgentReference]
        deploymentId: str
        deploymentType: Literal[AgentDeploymentType.HOSTED]
        description: str
        displayName: str
        maxReplicas: int
        minReplicas: int
        protocols: list[AgentProtocolVersion]
        provisioningState: Union[str, AgentDeploymentProvisioningState]
        state: Union[str, AgentDeploymentState]
        tags: dict[str, str]


    class azure.mgmt.cognitiveservices.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ResourceIdentityType]
        principalId: str
        tenantId: str
        type: Union[str, ResourceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.cognitiveservices.types.IpRule(TypedDict, total=False):
        key "value": Required[str]
        value: str


    class azure.mgmt.cognitiveservices.types.KeyVaultProperties(TypedDict, total=False):
        key "identityClientId": str
        key "keyName": str
        key "keyVaultUri": str
        key "keyVersion": str
        identityClientId: str
        keyName: str
        keyVaultUri: str
        keyVersion: str


    class azure.mgmt.cognitiveservices.types.ManagedAgentDeployment(TypedDict, total=False):
        key "agents": Optional[list[VersionedAgentReference]]
        key "deploymentId": Optional[str]
        key "deploymentType": Required[Literal[AgentDeploymentType.MANAGED]]
        key "description": Optional[str]
        key "displayName": Optional[str]
        key "protocols": Optional[list[AgentProtocolVersion]]
        key "provisioningState": Union[str, AgentDeploymentProvisioningState]
        key "state": Optional[Union[str, AgentDeploymentState]]
        key "tags": Optional[dict[str, str]]
        agents: list[VersionedAgentReference]
        deploymentId: str
        deploymentType: Literal[AgentDeploymentType.MANAGED]
        description: str
        displayName: str
        protocols: list[AgentProtocolVersion]
        provisioningState: Union[str, AgentDeploymentProvisioningState]
        state: Union[str, AgentDeploymentState]
        tags: dict[str, str]


    class azure.mgmt.cognitiveservices.types.ManagedClusterAgentHostingConfiguration(TypedDict, total=False):
        key "clusterResourceId": Required[str]
        key "hostingManagementIdentityResourceId": Required[str]
        key "hostingType": Required[Literal[AgentHostingType.MANAGED_CLUSTER]]
        key "name": Required[str]
        key "storageAccountResourceId": Required[str]
        key "workloadIdentityResourceId": Required[str]
        clusterResourceId: str
        hostingManagementIdentityResourceId: str
        hostingType: Literal[AgentHostingType.MANAGED_CLUSTER]
        name: str
        storageAccountResourceId: str
        workloadIdentityResourceId: str


    class azure.mgmt.cognitiveservices.types.ManagedComputeDeployment(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagedComputeDeploymentProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: ManagedComputeDeploymentProperties
        sku: Sku
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ManagedComputeDeploymentProperties(TypedDict, total=False):
        key "acceleratorType": str
        key "acceleratorsPerInstance": int
        key "computeId": str
        key "deploymentTemplate": str
        key "model": Required[str]
        key "priority": str
        key "provisioningDetails": ForwardRef('ManagedComputeDeploymentProvisioningDetails', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "routes": ForwardRef('ManagedComputeDeploymentRoutes', module='types')
        key "totalAccelerators": int
        key "versionUpgradeOption": Union[str, DeploymentModelVersionUpgradeOption]
        acceleratorType: str
        acceleratorsPerInstance: int
        capabilities: dict[str, str]
        computeId: str
        deploymentTemplate: str
        model: str
        priority: str
        provisioningDetails: ManagedComputeDeploymentProvisioningDetails
        provisioningState: Union[str, ProvisioningState]
        routes: ManagedComputeDeploymentRoutes
        totalAccelerators: int
        versionUpgradeOption: Union[str, DeploymentModelVersionUpgradeOption]


    class azure.mgmt.cognitiveservices.types.ManagedComputeDeploymentProvisioningDetails(TypedDict, total=False):
        key "lastOperationTimestamp": str
        key "message": str
        lastOperationTimestamp: str
        message: str


    class azure.mgmt.cognitiveservices.types.ManagedComputeDeploymentRoutes(TypedDict, total=False):
        key "chatCompletionsScoringPath": str
        key "messagesApiScoringPath": str
        key "swagger": str
        chatCompletionsScoringPath: str
        messagesApiScoringPath: str
        swagger: str


    class azure.mgmt.cognitiveservices.types.ManagedIdentityAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.MANAGED_IDENTITY]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionManagedIdentity', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.MANAGED_IDENTITY]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionManagedIdentity
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.ManagedNetworkProvisionOptions(TypedDict, total=False):


    class azure.mgmt.cognitiveservices.types.ManagedNetworkProvisionStatus(TypedDict, total=False):
        key "status": Union[str, ManagedNetworkStatus]
        status: Union[str, ManagedNetworkStatus]


    class azure.mgmt.cognitiveservices.types.ManagedNetworkSettings(TypedDict, total=False):
        key "firewallPublicIpAddress": Optional[str]
        key "firewallSku": Union[str, FirewallSku]
        key "isolationMode": Union[str, IsolationMode]
        key "managedNetworkKind": Union[str, ManagedNetworkKind]
        key "networkId": str
        key "outboundRules": Optional[dict[str, OutboundRule]]
        key "provisioningState": Union[str, ManagedNetworkProvisioningState]
        key "status": ForwardRef('ManagedNetworkProvisionStatus', module='types')
        firewallPublicIpAddress: str
        firewallSku: Union[str, FirewallSku]
        isolationMode: Union[str, IsolationMode]
        managedNetworkKind: Union[str, ManagedNetworkKind]
        networkId: str
        outboundRules: dict[str, OutboundRule]
        provisioningState: Union[str, ManagedNetworkProvisioningState]
        status: ManagedNetworkProvisionStatus


    class azure.mgmt.cognitiveservices.types.ManagedNetworkSettingsBasicResource(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagedNetworkSettings', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ManagedNetworkSettings
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ManagedNetworkSettingsEx(ManagedNetworkSettings):
        key "firewallPublicIpAddress": Optional[str]
        key "firewallSku": Union[str, FirewallSku]
        key "isolationMode": Union[str, IsolationMode]
        key "managedNetworkKind": Union[str, ManagedNetworkKind]
        key "networkId": str
        key "outboundRules": Optional[dict[str, OutboundRule]]
        key "provisioningState": Union[str, ManagedNetworkProvisioningState]
        key "status": ForwardRef('ManagedNetworkProvisionStatus', module='types')
        changeableIsolationModes: list[Union[str, IsolationMode]]
        firewallPublicIpAddress: str
        firewallSku: Union[str, FirewallSku]
        isolationMode: Union[str, IsolationMode]
        managedNetworkKind: Union[str, ManagedNetworkKind]
        networkId: str
        outboundRules: dict[str, OutboundRule]
        provisioningState: Union[str, ManagedNetworkProvisioningState]
        status: ManagedNetworkProvisionStatus


    class azure.mgmt.cognitiveservices.types.ManagedNetworkSettingsProperties(TypedDict, total=False):
        key "managedNetwork": ForwardRef('ManagedNetworkSettingsEx', module='types')
        key "provisioningState": Union[str, ManagedNetworkProvisioningState]
        managedNetwork: ManagedNetworkSettingsEx
        provisioningState: Union[str, ManagedNetworkProvisioningState]


    class azure.mgmt.cognitiveservices.types.ManagedNetworkSettingsPropertiesBasicResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('ManagedNetworkSettingsProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ManagedNetworkSettingsProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ModelCapacityCalculatorWorkload(TypedDict, total=False):
        key "requestParameters": ForwardRef('ModelCapacityCalculatorWorkloadRequestParam', module='types')
        key "requestPerMinute": int
        requestParameters: ModelCapacityCalculatorWorkloadRequestParam
        requestPerMinute: int


    class azure.mgmt.cognitiveservices.types.ModelCapacityCalculatorWorkloadRequestParam(TypedDict, total=False):
        key "avgGeneratedTokens": int
        key "avgPromptTokens": int
        avgGeneratedTokens: int
        avgPromptTokens: int


    class azure.mgmt.cognitiveservices.types.MultiRegionSettings(TypedDict, total=False):
        key "routingMethod": Union[str, RoutingMethods]
        regions: list[RegionSetting]
        routingMethod: Union[str, RoutingMethods]


    class azure.mgmt.cognitiveservices.types.NetworkInjection(TypedDict, total=False):
        key "scenario": Union[str, ScenarioType]
        key "subnetArmId": str
        key "useMicrosoftManagedNetwork": bool
        scenario: Union[str, ScenarioType]
        subnetArmId: str
        useMicrosoftManagedNetwork: bool


    class azure.mgmt.cognitiveservices.types.NetworkRuleSet(TypedDict, total=False):
        key "bypass": Union[str, ByPassSelection]
        key "defaultAction": Union[str, NetworkRuleAction]
        bypass: Union[str, ByPassSelection]
        defaultAction: Union[str, NetworkRuleAction]
        ipRules: list[IpRule]
        virtualNetworkRules: list[VirtualNetworkRule]


    class azure.mgmt.cognitiveservices.types.NoneAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.NONE]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.NONE]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.OAuth2AuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.O_AUTH2]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionOAuth2', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.O_AUTH2]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionOAuth2
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.OrganizationSharedBuiltInAuthorizationPolicy(TypedDict, total=False):
        key "type": Required[Literal[BuiltInAuthorizationScheme.ORGANIZATION_SCOPE]]
        type: Literal[BuiltInAuthorizationScheme.ORGANIZATION_SCOPE]


    class azure.mgmt.cognitiveservices.types.OutboundRuleBasicResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[OutboundRule]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OutboundRule
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.PATAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.PAT]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionPersonalAccessToken', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.PAT]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionPersonalAccessToken
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.PatchResourceSku(TypedDict, total=False):
        key "sku": ForwardRef('Sku', module='types')
        sku: Sku


    class azure.mgmt.cognitiveservices.types.PatchResourceTags(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.cognitiveservices.types.PatchResourceTagsAndSku(PatchResourceTags):
        key "sku": ForwardRef('Sku', module='types')
        sku: Sku
        tags: dict[str, str]


    class azure.mgmt.cognitiveservices.types.Pool(TypedDict, total=False):
        key "instanceType": Required[str]
        key "name": Required[str]
        key "nodeCount": Required[int]
        key "vmPriority": Union[str, VmPriority]
        instanceType: str
        name: str
        nodeCount: int
        vmPriority: Union[str, VmPriority]


    class azure.mgmt.cognitiveservices.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cognitiveservices.types.PrivateEndpointConnection(ProxyResource):
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
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.cognitiveservices.types.PrivateEndpointOutboundRule(TypedDict, total=False):
        key "category": Union[str, RuleCategory]
        key "destination": ForwardRef('PrivateEndpointOutboundRuleDestination', module='types')
        key "errorInformation": str
        key "status": Union[str, RuleStatus]
        key "type": Required[Literal[RuleType.PRIVATE_ENDPOINT]]
        category: Union[str, RuleCategory]
        destination: PrivateEndpointOutboundRuleDestination
        errorInformation: str
        fqdns: list[str]
        parentRuleNames: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.PRIVATE_ENDPOINT]


    class azure.mgmt.cognitiveservices.types.PrivateEndpointOutboundRuleDestination(TypedDict, total=False):
        key "serviceResourceId": str
        key "subresourceTarget": str
        serviceResourceId: str
        subresourceTarget: str


    class azure.mgmt.cognitiveservices.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.cognitiveservices.types.Project(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('ProjectProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        location: str
        name: str
        properties: ProjectProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.ProjectCapabilityHost(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[ProjectCapabilityHostProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: ProjectCapabilityHostProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ProjectCapabilityHostProperties(TypedDict, total=False):
        key "aiServicesConnections": Optional[list[str]]
        key "provisioningState": Union[str, CapabilityHostProvisioningState]
        key "storageConnections": Optional[list[str]]
        key "threadStorageConnections": Optional[list[str]]
        key "vectorStoreConnections": Optional[list[str]]
        aiServicesConnections: list[str]
        provisioningState: Union[str, CapabilityHostProvisioningState]
        storageConnections: list[str]
        threadStorageConnections: list[str]
        vectorStoreConnections: list[str]


    class azure.mgmt.cognitiveservices.types.ProjectProperties(TypedDict, total=False):
        key "capabilitySettings": ForwardRef('CapabilitySettings', module='types')
        key "description": str
        key "displayName": str
        key "isDefault": bool
        key "provisioningState": Union[str, ProvisioningState]
        capabilitySettings: CapabilitySettings
        description: str
        displayName: str
        endpoints: dict[str, str]
        isDefault: bool
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.cognitiveservices.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.QuotaLimit(TypedDict, total=False):
        key "count": float
        key "renewalPeriod": float
        count: float
        renewalPeriod: float
        rules: list[ThrottlingRule]


    class azure.mgmt.cognitiveservices.types.QuotaTier(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('QuotaTierProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: QuotaTierProperties
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.QuotaTierProperties(TypedDict, total=False):
        key "assignmentDate": str
        key "currentTierName": str
        key "tierUpgradeEligibilityInfo": Optional[QuotaTierUpgradeEligibilityInfo]
        key "tierUpgradePolicy": Union[str, TierUpgradePolicy]
        assignmentDate: str
        currentTierName: str
        tierUpgradeEligibilityInfo: QuotaTierUpgradeEligibilityInfo
        tierUpgradePolicy: Union[str, TierUpgradePolicy]


    class azure.mgmt.cognitiveservices.types.QuotaTierUpgradeEligibilityInfo(TypedDict, total=False):
        key "nextTierName": Optional[str]
        key "upgradeApplicableDate": Optional[str]
        key "upgradeAvailabilityStatus": Union[str, UpgradeAvailabilityStatus]
        key "upgradeUnavailabilityReason": Optional[str]
        nextTierName: str
        upgradeApplicableDate: str
        upgradeAvailabilityStatus: Union[str, UpgradeAvailabilityStatus]
        upgradeUnavailabilityReason: str


    class azure.mgmt.cognitiveservices.types.RaiBlocklist(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiBlocklistProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiBlocklistProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiBlocklistConfig(TypedDict, total=False):
        key "blocking": bool
        key "blocklistName": str
        blocking: bool
        blocklistName: str


    class azure.mgmt.cognitiveservices.types.RaiBlocklistItem(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiBlocklistItemProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiBlocklistItemProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiBlocklistItemBulkRequest(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('RaiBlocklistItemProperties', module='types')
        name: str
        properties: RaiBlocklistItemProperties


    class azure.mgmt.cognitiveservices.types.RaiBlocklistItemProperties(TypedDict, total=False):
        key "isRegex": bool
        key "pattern": str
        isRegex: bool
        pattern: str


    class azure.mgmt.cognitiveservices.types.RaiBlocklistProperties(TypedDict, total=False):
        key "description": str
        description: str


    class azure.mgmt.cognitiveservices.types.RaiEgressHeaderTransform(TypedDict, total=False):
        key "name": Required[str]
        key "operation": Required[Union[str, RaiEgressHeaderOperation]]
        key "value": str
        key "valueRef": ForwardRef('RaiEgressHeaderValueRef', module='types')
        name: str
        operation: Union[str, RaiEgressHeaderOperation]
        value: str
        valueRef: RaiEgressHeaderValueRef


    class azure.mgmt.cognitiveservices.types.RaiEgressHeaderValueRef(TypedDict, total=False):
        key "managedIdentityRef": ForwardRef('RaiEgressManagedIdentityRef', module='types')
        key "secretRef": ForwardRef('RaiEgressSecretRef', module='types')
        managedIdentityRef: RaiEgressManagedIdentityRef
        secretRef: RaiEgressSecretRef


    class azure.mgmt.cognitiveservices.types.RaiEgressManagedIdentityRef(TypedDict, total=False):
        key "format": str
        key "resource": Required[str]
        format: str
        resource: str


    class azure.mgmt.cognitiveservices.types.RaiEgressPolicyConfig(TypedDict, total=False):
        key "defaultAction": Union[str, RaiEgressDefaultAction]
        key "description": str
        key "mode": Union[str, RaiEgressMode]
        defaultAction: Union[str, RaiEgressDefaultAction]
        description: str
        mode: Union[str, RaiEgressMode]
        rules: list[RaiEgressRule]


    class azure.mgmt.cognitiveservices.types.RaiEgressRewriteTarget(TypedDict, total=False):
        key "host": str
        key "path": str
        key "scheme": Union[str, RaiEgressScheme]
        host: str
        path: str
        scheme: Union[str, RaiEgressScheme]


    class azure.mgmt.cognitiveservices.types.RaiEgressRule(TypedDict, total=False):
        key "action": Required[RaiEgressRuleAction]
        key "description": str
        key "match": ForwardRef('RaiEgressRuleMatch', module='types')
        key "name": Required[str]
        key "ruleType": Required[Union[str, RaiEgressRuleType]]
        action: RaiEgressRuleAction
        description: str
        match: RaiEgressRuleMatch
        name: str
        ruleType: Union[str, RaiEgressRuleType]


    class azure.mgmt.cognitiveservices.types.RaiEgressRuleAction(TypedDict, total=False):
        key "actionType": Required[Union[str, RaiEgressRuleActionType]]
        key "rewrite": ForwardRef('RaiEgressRewriteTarget', module='types')
        actionType: Union[str, RaiEgressRuleActionType]
        headers: list[RaiEgressHeaderTransform]
        rewrite: RaiEgressRewriteTarget


    class azure.mgmt.cognitiveservices.types.RaiEgressRuleMatch(TypedDict, total=False):
        key "host": str
        key "path": str
        host: str
        path: str


    class azure.mgmt.cognitiveservices.types.RaiEgressSecretRef(TypedDict, total=False):
        key "format": str
        key "secretId": Required[str]
        key "secretKey": str
        format: str
        secretId: str
        secretKey: str


    class azure.mgmt.cognitiveservices.types.RaiExternalSafetyProviderSchema(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiExternalSafetyProviderSchemaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiExternalSafetyProviderSchemaProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiExternalSafetyProviderSchemaProperties(TypedDict, total=False):
        key "createdAt": str
        key "keyVaultUri": str
        key "lastModifiedAt": str
        key "managedIdentity": str
        key "mode": str
        key "providerId": str
        key "providerName": str
        key "secretName": str
        key "url": str
        createdAt: str
        keyVaultUri: str
        lastModifiedAt: str
        managedIdentity: str
        mode: str
        providerId: str
        providerName: str
        secretName: str
        url: str


    class azure.mgmt.cognitiveservices.types.RaiMonitorConfig(TypedDict, total=False):
        key "adxStorageResourceId": str
        key "identityClientId": str
        adxStorageResourceId: str
        identityClientId: str


    class azure.mgmt.cognitiveservices.types.RaiPolicy(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiPolicyProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiPolicyContentFilter(TypedDict, total=False):
        key "action": Union[str, RaiActionType]
        key "blocking": bool
        key "enabled": bool
        key "name": str
        key "severityThreshold": Union[str, ContentLevel]
        key "source": Union[str, RaiPolicyContentSource]
        action: Union[str, RaiActionType]
        blocking: bool
        enabled: bool
        name: str
        severityThreshold: Union[str, ContentLevel]
        source: Union[str, RaiPolicyContentSource]


    class azure.mgmt.cognitiveservices.types.RaiPolicyProperties(TypedDict, total=False):
        key "basePolicyName": str
        key "egressPolicy": ForwardRef('RaiEgressPolicyConfig', module='types')
        key "mode": Union[str, RaiPolicyMode]
        key "type": Union[str, RaiPolicyType]
        basePolicyName: str
        contentFilters: list[RaiPolicyContentFilter]
        customBlocklists: list[CustomBlocklistConfig]
        egressPolicy: RaiEgressPolicyConfig
        mode: Union[str, RaiPolicyMode]
        safetyProviders: list[SafetyProviderConfig]
        type: Union[str, RaiPolicyType]


    class azure.mgmt.cognitiveservices.types.RaiSafetyProviderConfig(TypedDict, total=False):
        key "blocking": bool
        key "safetyProviderName": str
        blocking: bool
        safetyProviderName: str


    class azure.mgmt.cognitiveservices.types.RaiToolLabel(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiToolLabelProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiToolLabelProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiToolLabelProperties(TypedDict, total=False):
        key "accountScope": ForwardRef('RaiToolLabelPropertiesAccountScope', module='types')
        key "toolConnectionName": Required[str]
        accountScope: RaiToolLabelPropertiesAccountScope
        projectScopes: list[RaiToolLabelPropertiesProjectScopesItem]
        toolConnectionName: str


    class azure.mgmt.cognitiveservices.types.RaiToolLabelPropertiesAccountScope(TypedDict, total=False):
        labelValues: dict[str, str]


    class azure.mgmt.cognitiveservices.types.RaiToolLabelPropertiesProjectScopesItem(TypedDict, total=False):
        key "labelValues": Required[dict[str, str]]
        key "project": Required[str]
        labelValues: dict[str, str]
        project: str


    class azure.mgmt.cognitiveservices.types.RaiTopic(ProxyResource):
        key "etag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('RaiTopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        name: str
        properties: RaiTopicProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.RaiTopicProperties(TypedDict, total=False):
        key "createdAt": str
        key "description": str
        key "failedReason": str
        key "lastModifiedAt": str
        key "sampleBlobUrl": str
        key "status": str
        key "topicId": str
        key "topicName": str
        createdAt: str
        description: str
        failedReason: str
        lastModifiedAt: str
        sampleBlobUrl: str
        status: str
        topicId: str
        topicName: str


    class azure.mgmt.cognitiveservices.types.RegenerateKeyParameters(TypedDict, total=False):
        key "keyName": Required[Union[str, KeyName]]
        keyName: Union[str, KeyName]


    class azure.mgmt.cognitiveservices.types.RegionSetting(TypedDict, total=False):
        key "customsubdomain": str
        key "name": str
        key "value": float
        customsubdomain: str
        name: str
        value: float


    class azure.mgmt.cognitiveservices.types.RequestMatchPattern(TypedDict, total=False):
        key "method": str
        key "path": str
        method: str
        path: str


    class azure.mgmt.cognitiveservices.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.cognitiveservices.types.ResourceBase(TypedDict, total=False):
        key "description": Optional[str]
        key "tags": Optional[dict[str, str]]
        description: str
        tags: dict[str, str]


    class azure.mgmt.cognitiveservices.types.RoleBasedBuiltInAuthorizationPolicy(TypedDict, total=False):
        key "type": Required[Literal[BuiltInAuthorizationScheme.DEFAULT]]
        type: Literal[BuiltInAuthorizationScheme.DEFAULT]


    class azure.mgmt.cognitiveservices.types.RuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FQDN = "FQDN"
        PRIVATE_ENDPOINT = "PrivateEndpoint"
        SERVICE_TAG = "ServiceTag"


    class azure.mgmt.cognitiveservices.types.SASAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.SAS]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionSharedAccessSignature', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.SAS]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionSharedAccessSignature
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.SafetyProviderConfig(RaiSafetyProviderConfig):
        key "blocking": bool
        key "safetyProviderName": str
        key "source": Union[str, RaiPolicyContentSource]
        blocking: bool
        safetyProviderName: str
        source: Union[str, RaiPolicyContentSource]


    class azure.mgmt.cognitiveservices.types.ServicePrincipalAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.SERVICE_PRINCIPAL]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionServicePrincipal', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.SERVICE_PRINCIPAL]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionServicePrincipal
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.ServiceTagOutboundRule(TypedDict, total=False):
        key "category": Union[str, RuleCategory]
        key "destination": ForwardRef('ServiceTagOutboundRuleDestination', module='types')
        key "errorInformation": str
        key "status": Union[str, RuleStatus]
        key "type": Required[Literal[RuleType.SERVICE_TAG]]
        category: Union[str, RuleCategory]
        destination: ServiceTagOutboundRuleDestination
        errorInformation: str
        parentRuleNames: list[str]
        status: Union[str, RuleStatus]
        type: Literal[RuleType.SERVICE_TAG]


    class azure.mgmt.cognitiveservices.types.ServiceTagOutboundRuleDestination(TypedDict, total=False):
        key "action": Union[str, RuleAction]
        key "portRanges": str
        key "protocol": str
        key "serviceTag": str
        action: Union[str, RuleAction]
        addressPrefixes: list[str]
        portRanges: str
        protocol: str
        serviceTag: str


    class azure.mgmt.cognitiveservices.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "family": str
        key "name": Required[str]
        key "size": str
        key "tier": Union[str, SkuTier]
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]


    class azure.mgmt.cognitiveservices.types.SkuCapability(TypedDict, total=False):
        key "name": str
        key "value": str
        name: str
        value: str


    class azure.mgmt.cognitiveservices.types.SkuChangeInfo(TypedDict, total=False):
        key "countOfDowngrades": float
        key "countOfUpgradesAfterDowngrades": float
        key "lastChangeDate": str
        countOfDowngrades: float
        countOfUpgradesAfterDowngrades: float
        lastChangeDate: str


    class azure.mgmt.cognitiveservices.types.SshSettings(TypedDict, total=False):
        key "adminEnabled": bool
        key "sshPublicKey": str
        adminEnabled: bool
        sshPublicKey: str


    class azure.mgmt.cognitiveservices.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.cognitiveservices.types.ThrottlingRule(TypedDict, total=False):
        key "count": float
        key "dynamicThrottlingEnabled": bool
        key "key": str
        key "minCount": float
        key "renewalPeriod": float
        count: float
        dynamicThrottlingEnabled: bool
        key: str
        matchPatterns: list[RequestMatchPattern]
        minCount: float
        renewalPeriod: float


    class azure.mgmt.cognitiveservices.types.TrafficRoutingRule(TypedDict, total=False):
        key "deploymentId": Optional[str]
        key "description": Optional[str]
        key "ruleId": Optional[str]
        key "trafficPercentage": int
        deploymentId: str
        description: str
        ruleId: str
        trafficPercentage: int


    class azure.mgmt.cognitiveservices.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.cognitiveservices.types.UserOwnedAmlWorkspace(TypedDict, total=False):
        key "identityClientId": str
        key "resourceId": str
        identityClientId: str
        resourceId: str


    class azure.mgmt.cognitiveservices.types.UserOwnedStorage(TypedDict, total=False):
        key "identityClientId": str
        key "resourceId": str
        identityClientId: str
        resourceId: str


    class azure.mgmt.cognitiveservices.types.UsernamePasswordAuthTypeConnectionProperties(TypedDict, total=False):
        key "authType": Required[Literal[ConnectionAuthType.USERNAME_PASSWORD]]
        key "category": Union[str, ConnectionCategory]
        key "createdByWorkspaceArmId": str
        key "credentials": ForwardRef('ConnectionUsernamePassword', module='types')
        key "error": str
        key "expiryTime": str
        key "group": Union[str, ConnectionGroup]
        key "isSharedToAll": bool
        key "peRequirement": Union[str, ManagedPERequirement]
        key "peStatus": Union[str, ManagedPEStatus]
        key "target": str
        key "useWorkspaceManagedIdentity": bool
        authType: Literal[ConnectionAuthType.USERNAME_PASSWORD]
        category: Union[str, ConnectionCategory]
        createdByWorkspaceArmId: str
        credentials: ConnectionUsernamePassword
        error: str
        expiryTime: str
        group: Union[str, ConnectionGroup]
        isSharedToAll: bool
        metadata: dict[str, str]
        peRequirement: Union[str, ManagedPERequirement]
        peStatus: Union[str, ManagedPEStatus]
        sharedUserList: list[str]
        target: str
        useWorkspaceManagedIdentity: bool


    class azure.mgmt.cognitiveservices.types.VersionedAgentReference(AgentReferenceProperties):
        key "agentId": Optional[str]
        key "agentName": Optional[str]
        key "agentVersion": Optional[str]
        agentId: str
        agentName: str
        agentVersion: str


    class azure.mgmt.cognitiveservices.types.VirtualNetworkRule(TypedDict, total=False):
        key "id": Required[str]
        key "ignoreMissingVnetServiceEndpoint": bool
        key "state": str
        id: str
        ignoreMissingVnetServiceEndpoint: bool
        state: str


    class azure.mgmt.cognitiveservices.types.Workbench(ProxyResource):
        key "etag": str
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": Required[WorkbenchProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        identity: Identity
        location: str
        name: str
        properties: WorkbenchProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cognitiveservices.types.WorkbenchProperties(TypedDict, total=False):
        key "connectivityEndpoints": ForwardRef('ConnectivityEndpoints', module='types')
        key "creationTime": str
        key "datasetId": str
        key "idleTimeBeforeShutdown": str
        key "imageLink": Required[str]
        key "provisioningState": Union[str, ComputeProvisioningState]
        key "sshSettings": ForwardRef('SshSettings', module='types')
        key "targetClusterId": Required[str]
        key "webEndpoint": str
        connectivityEndpoints: ConnectivityEndpoints
        creationTime: str
        datasetId: str
        errors: list[ErrorDetail]
        idleTimeBeforeShutdown: str
        imageLink: str
        provisioningState: Union[str, ComputeProvisioningState]
        sshSettings: SshSettings
        targetClusterId: str
        webEndpoint: str


```