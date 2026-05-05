```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.cognitiveservices

    class azure.mgmt.cognitiveservices.CognitiveServicesManagementClient(_CognitiveServicesManagementClientOperationsMixin): implements ContextManager 
        account_capability_hosts: AccountCapabilityHostsOperations
        account_connections: AccountConnectionsOperations
        accounts: AccountsOperations
        agent_applications: AgentApplicationsOperations
        agent_deployments: AgentDeploymentsOperations
        commitment_plans: CommitmentPlansOperations
        commitment_tiers: CommitmentTiersOperations
        compute_operations: ComputeOperationsOperations
        defender_for_ai_settings: DefenderForAISettingsOperations
        deleted_accounts: DeletedAccountsOperations
        deployments: DeploymentsOperations
        encryption_scopes: EncryptionScopesOperations
        location_based_model_capacities: LocationBasedModelCapacitiesOperations
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
        commitment_plans: CommitmentPlansOperations
        commitment_tiers: CommitmentTiersOperations
        compute_operations: ComputeOperationsOperations
        defender_for_ai_settings: DefenderForAISettingsOperations
        deleted_accounts: DeletedAccountsOperations
        deployments: DeploymentsOperations
        encryption_scopes: EncryptionScopesOperations
        location_based_model_capacities: LocationBasedModelCapacitiesOperations
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                parameters: JSON, 
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
                capability_host: JSON, 
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
                connection: Optional[JSON] = None, 
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
                connection: Optional[JSON] = None, 
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
                account: JSON, 
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
                account: JSON, 
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
                parameters: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                association: JSON, 
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
                commitment_plan: JSON, 
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
                commitment_plan: JSON, 
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
                commitment_plan: JSON, 
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
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ComputeOperationStatus: ...


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
                defender_for_ai_settings: JSON, 
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
                defender_for_ai_settings: JSON, 
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
                deployment: JSON, 
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
                deployment: JSON, 
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
                encryption_scope: JSON, 
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
                body: Optional[JSON] = None, 
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
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'managed_network_name']}, api_versions_list=['2026-01-15-preview'])
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
                body: Optional[JSON] = None, 
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
                body: JSON, 
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
                body: JSON, 
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
            ) -> AsyncLROPoller[OutboundRuleListResult]: ...

        @overload
        async def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OutboundRuleListResult]: ...

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
            ) -> AsyncLROPoller[OutboundRuleListResult]: ...


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
                properties: JSON, 
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
                capability_host: JSON, 
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
                connection: Optional[JSON] = None, 
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
                connection: Optional[JSON] = None, 
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
                project: JSON, 
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
                project: JSON, 
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
                tier: JSON, 
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
                tier: JSON, 
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
                rai_blocklist_items: List[JSON], 
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
                rai_blocklist_item: JSON, 
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
                rai_blocklist: JSON, 
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
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

        @overload
        async def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

        @overload
        async def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

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
                rai_policy: JSON, 
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
                rai_tool_label: JSON, 
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
                rai_topic: JSON, 
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
                rai_policy: JSON, 
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
                safety_provider: JSON, 
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


    class azure.mgmt.cognitiveservices.models.Account(Resource):
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
        abuse_penalty: Optional[AbusePenalty]
        allow_project_management: Optional[bool]
        allowed_fqdn_list: Optional[list[str]]
        aml_workspace: Optional[UserOwnedAmlWorkspace]
        api_properties: Optional[ApiProperties]
        associated_projects: Optional[list[str]]
        call_rate_limit: Optional[CallRateLimit]
        capabilities: Optional[list[SkuCapability]]
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
                allow_project_management: Optional[bool] = ..., 
                allowed_fqdn_list: Optional[list[str]] = ..., 
                aml_workspace: Optional[UserOwnedAmlWorkspace] = ..., 
                api_properties: Optional[ApiProperties] = ..., 
                associated_projects: Optional[list[str]] = ..., 
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


    class azure.mgmt.cognitiveservices.models.CommitmentPlan(Resource):
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


    class azure.mgmt.cognitiveservices.models.CustomTopicConfig(RaiTopicConfig):
        blocking: bool
        source: Optional[Union[str, RaiPolicyContentSource]]
        topic_name: str

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                source: Optional[Union[str, RaiPolicyContentSource]] = ..., 
                topic_name: Optional[str] = ...
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


    class azure.mgmt.cognitiveservices.models.DeploymentProperties(_Model):
        call_rate_limit: Optional[CallRateLimit]
        capabilities: Optional[dict[str, str]]
        capacity_settings: Optional[DeploymentCapacitySettings]
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
        spillover_deployment_name: Optional[str]
        version_upgrade_option: Optional[Union[str, DeploymentModelVersionUpgradeOption]]

        @overload
        def __init__(
                self, 
                *, 
                capacity_settings: Optional[DeploymentCapacitySettings] = ..., 
                current_capacity: Optional[int] = ..., 
                deployment_state: Optional[Union[str, DeploymentState]] = ..., 
                model: Optional[DeploymentModel] = ..., 
                parent_deployment_name: Optional[str] = ..., 
                rai_policy_name: Optional[str] = ..., 
                routing: Optional[DeploymentRouting] = ..., 
                scale_settings: Optional[DeploymentScaleSettings] = ..., 
                service_tier: Optional[Union[str, ServiceTier]] = ..., 
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


    class azure.mgmt.cognitiveservices.models.OutboundRuleListResult(_Model):
        next_link: Optional[str]
        value: Optional[list[OutboundRuleBasicResource]]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[list[OutboundRuleBasicResource]] = ...
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


    class azure.mgmt.cognitiveservices.models.Project(Resource):
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
        description: Optional[str]
        display_name: Optional[str]
        endpoints: Optional[dict[str, str]]
        is_default: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
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


    class azure.mgmt.cognitiveservices.models.RaiExternalSafetyProvider(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[RaiExternalSafetyProviderProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RaiExternalSafetyProviderProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cognitiveservices.models.RaiExternalSafetyProviderProperties(_Model):
        created_at: Optional[datetime]
        last_modified_at: Optional[datetime]
        mode: Optional[str]
        provider_id: Optional[str]
        provider_name: Optional[str]
        url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                mode: Optional[str] = ..., 
                provider_id: Optional[str] = ..., 
                provider_name: Optional[str] = ..., 
                url: Optional[str] = ...
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
        custom_topics: Optional[list[CustomTopicConfig]]
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
                custom_topics: Optional[list[CustomTopicConfig]] = ..., 
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


    class azure.mgmt.cognitiveservices.models.RaiTopicConfig(_Model):
        blocking: Optional[bool]
        topic_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blocking: Optional[bool] = ..., 
                topic_name: Optional[str] = ...
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
        ACCURACY = "accuracy"
        BALANCED = "balanced"
        COST = "cost"


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
                capability_host: JSON, 
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
                connection: Optional[JSON] = None, 
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
                connection: Optional[JSON] = None, 
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
                account: JSON, 
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
                account: JSON, 
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
                parameters: JSON, 
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
                body: JSON, 
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
                body: JSON, 
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
                association: JSON, 
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
                commitment_plan: JSON, 
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
                commitment_plan: JSON, 
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
                commitment_plan: JSON, 
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
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-01-15-preview'])
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> ComputeOperationStatus: ...


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
                defender_for_ai_settings: JSON, 
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
                defender_for_ai_settings: JSON, 
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
                deployment: JSON, 
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
                deployment: JSON, 
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
                encryption_scope: JSON, 
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
                body: Optional[JSON] = None, 
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
        @api_version_validation(method_added_on='2026-01-15-preview', params_added_on={'2026-01-15-preview': ['api_version', 'subscription_id', 'resource_group_name', 'account_name', 'managed_network_name']}, api_versions_list=['2026-01-15-preview'])
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
                body: Optional[JSON] = None, 
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
                body: JSON, 
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
                body: JSON, 
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
            ) -> LROPoller[OutboundRuleListResult]: ...

        @overload
        def begin_post(
                self, 
                resource_group_name: str, 
                account_name: str, 
                managed_network_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OutboundRuleListResult]: ...

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
            ) -> LROPoller[OutboundRuleListResult]: ...


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
                properties: JSON, 
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
                capability_host: JSON, 
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
                connection: Optional[JSON] = None, 
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
                connection: Optional[JSON] = None, 
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
                project: JSON, 
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
                project: JSON, 
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
                tier: JSON, 
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
                tier: JSON, 
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
                rai_blocklist_items: List[JSON], 
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
                rai_blocklist_item: JSON, 
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
                rai_blocklist: JSON, 
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
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

        @overload
        def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

        @overload
        def create_or_update(
                self, 
                safety_provider_name: str, 
                safety_provider: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Union[RaiExternalSafetyProviderSchema, RaiExternalSafetyProvider]: ...

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
                rai_policy: JSON, 
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
                rai_tool_label: JSON, 
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
                rai_topic: JSON, 
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
                rai_policy: JSON, 
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
                safety_provider: JSON, 
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


```