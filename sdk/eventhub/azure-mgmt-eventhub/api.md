```py
namespace azure.mgmt.eventhub

    class azure.mgmt.eventhub.EventHubManagementClient: implements ContextManager 
        application_group: ApplicationGroupOperations
        clusters: ClustersOperations
        configuration: ConfigurationOperations
        consumer_groups: ConsumerGroupsOperations
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        event_hubs: EventHubsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configuration: NetworkSecurityPerimeterConfigurationOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        schema_registry: SchemaRegistryOperations

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


namespace azure.mgmt.eventhub.aio

    class azure.mgmt.eventhub.aio.EventHubManagementClient: implements AsyncContextManager 
        application_group: ApplicationGroupOperations
        clusters: ClustersOperations
        configuration: ConfigurationOperations
        consumer_groups: ConsumerGroupsOperations
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        event_hubs: EventHubsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configuration: NetworkSecurityPerimeterConfigurationOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        schema_registry: SchemaRegistryOperations

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


namespace azure.mgmt.eventhub.aio.operations

    class azure.mgmt.eventhub.aio.operations.ApplicationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        async def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        async def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ApplicationGroup]: ...


    class azure.mgmt.eventhub.aio.operations.ClustersOperations:

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
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace_async
        async def list_available_cluster_region(self, **kwargs: Any) -> AvailableClustersList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace_async
        async def list_namespaces(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> EHNamespaceIdListResult: ...


    class azure.mgmt.eventhub.aio.operations.ConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterQuotaConfigurationProperties: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterQuotaConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterQuotaConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...

        @overload
        async def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...


    class azure.mgmt.eventhub.aio.operations.ConsumerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: ConsumerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: ConsumerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @distributed_trace
        def list_by_event_hub(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ConsumerGroup]: ...


    class azure.mgmt.eventhub.aio.operations.DisasterRecoveryConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def break_pairing(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: ArmDisasterRecovery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: ArmDisasterRecovery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ArmDisasterRecovery]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthorizationRule]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.eventhub.aio.operations.EventHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: Eventhub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: Eventhub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> Eventhub: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Eventhub]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.eventhub.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EHNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EHNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EHNamespace]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: FailOver, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailOver]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: FailOver, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailOver]: ...

        @overload
        async def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FailOver]: ...

        @overload
        async def check_name_availability(
                self, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        async def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NetworkRuleSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @overload
        async def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NetworkRuleSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @overload
        async def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> EHNamespace: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace_async
        async def get_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[EHNamespace]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthorizationRule]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EHNamespace]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @distributed_trace_async
        async def list_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSetListResult: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...


    class azure.mgmt.eventhub.aio.operations.NetworkSecurityPerimeterConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfigurationList: ...


    class azure.mgmt.eventhub.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace_async
        async def get_resource_association_name(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...


    class azure.mgmt.eventhub.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.eventhub.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventhub.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourcesListResult: ...


    class azure.mgmt.eventhub.aio.operations.SchemaRegistryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: SchemaGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: SchemaGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaGroup]: ...


namespace azure.mgmt.eventhub.models

    class azure.mgmt.eventhub.models.AccessKeys(_Model):
        alias_primary_connection_string: Optional[str]
        alias_secondary_connection_string: Optional[str]
        key_name: Optional[str]
        primary_connection_string: Optional[str]
        primary_key: Optional[str]
        secondary_connection_string: Optional[str]
        secondary_key: Optional[str]


    class azure.mgmt.eventhub.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.eventhub.models.ApplicationGroup(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ApplicationGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ApplicationGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.ApplicationGroupPolicy(_Model):
        name: str
        type: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ApplicationGroupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLING_POLICY = "ThrottlingPolicy"


    class azure.mgmt.eventhub.models.ApplicationGroupProperties(_Model):
        client_app_group_identifier: str
        is_enabled: Optional[bool]
        policies: Optional[list[ApplicationGroupPolicy]]

        @overload
        def __init__(
                self, 
                *, 
                client_app_group_identifier: str, 
                is_enabled: Optional[bool] = ..., 
                policies: Optional[list[ApplicationGroupPolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ArmDisasterRecovery(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ArmDisasterRecoveryProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ArmDisasterRecoveryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.ArmDisasterRecoveryProperties(_Model):
        alternate_name: Optional[str]
        partner_namespace: Optional[str]
        pending_replication_operations_count: Optional[int]
        provisioning_state: Optional[Union[str, ProvisioningStateDR]]
        role: Optional[Union[str, RoleDisasterRecovery]]

        @overload
        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                partner_namespace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.AuthorizationRule(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[AuthorizationRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AuthorizationRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.AuthorizationRuleProperties(_Model):
        rights: list[Union[str, AccessRights]]

        @overload
        def __init__(
                self, 
                *, 
                rights: list[Union[str, AccessRights]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.AvailableCluster(_Model):
        location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.AvailableClustersList(_Model):
        value: Optional[list[AvailableCluster]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[AvailableCluster]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CaptureDescription(_Model):
        destination: Optional[Destination]
        enabled: Optional[bool]
        encoding: Optional[Union[str, EncodingCaptureDescription]]
        interval_in_seconds: Optional[int]
        size_limit_in_bytes: Optional[int]
        skip_empty_archives: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[Destination] = ..., 
                enabled: Optional[bool] = ..., 
                encoding: Optional[Union[str, EncodingCaptureDescription]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                size_limit_in_bytes: Optional[int] = ..., 
                skip_empty_archives: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CaptureIdentity(_Model):
        type: Optional[Union[str, CaptureIdentityType]]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, CaptureIdentityType]] = ..., 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CaptureIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventhub.models.CheckNameAvailabilityParameter(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, UnavailableReason]]

        @overload
        def __init__(
                self, 
                *, 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, UnavailableReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CleanupPolicyRetentionDescription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPACT = "Compact"
        DELETE = "Delete"
        DELETE_OR_COMPACT = "DeleteOrCompact"


    class azure.mgmt.eventhub.models.Cluster(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ClusterProperties]
        sku: Optional[ClusterSku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                properties: Optional[ClusterProperties] = ..., 
                sku: Optional[ClusterSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.ClusterProperties(_Model):
        created_at: Optional[str]
        metric_id: Optional[str]
        platform_capabilities: Optional[PlatformCapabilities]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]
        supports_scaling: Optional[bool]
        updated_at: Optional[str]
        zone_redundant: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                platform_capabilities: Optional[PlatformCapabilities] = ..., 
                supports_scaling: Optional[bool] = ..., 
                zone_redundant: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ClusterQuotaConfigurationProperties(_Model):
        settings: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                settings: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ClusterSku(_Model):
        capacity: Optional[int]
        name: Union[str, ClusterSkuName]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, ClusterSkuName]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ClusterSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"


    class azure.mgmt.eventhub.models.ConfidentialCompute(_Model):
        mode: Optional[Union[str, Mode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ConnectionState(_Model):
        description: Optional[str]
        status: Optional[Union[str, PrivateLinkConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateLinkConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ConsumerGroup(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[ConsumerGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ConsumerGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.ConsumerGroupProperties(_Model):
        created_at: Optional[datetime]
        updated_at: Optional[datetime]
        user_metadata: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_metadata: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.eventhub.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.eventhub.models.Destination(_Model):
        identity: Optional[CaptureIdentity]
        name: Optional[str]
        properties: Optional[DestinationProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[CaptureIdentity] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[DestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.DestinationProperties(_Model):
        archive_name_format: Optional[str]
        blob_container: Optional[str]
        data_lake_account_name: Optional[str]
        data_lake_folder_path: Optional[str]
        data_lake_subscription_id: Optional[str]
        storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                archive_name_format: Optional[str] = ..., 
                blob_container: Optional[str] = ..., 
                data_lake_account_name: Optional[str] = ..., 
                data_lake_folder_path: Optional[str] = ..., 
                data_lake_subscription_id: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.EHNamespace(ProxyResource):
        id: str
        identity: Optional[Identity]
        location: Optional[str]
        name: str
        properties: Optional[EHNamespaceProperties]
        sku: Optional[Sku]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[EHNamespaceProperties] = ..., 
                sku: Optional[Sku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.EHNamespaceIdContainer(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.EHNamespaceIdListResult(_Model):
        value: Optional[list[EHNamespaceIdContainer]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[EHNamespaceIdContainer]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.EHNamespaceProperties(_Model):
        alternate_name: Optional[str]
        cluster_arm_id: Optional[str]
        created_at: Optional[datetime]
        disable_local_auth: Optional[bool]
        encryption: Optional[Encryption]
        geo_data_replication: Optional[GeoDataReplicationProperties]
        ip_address_type: Optional[Union[str, IpAddressType]]
        is_auto_inflate_enabled: Optional[bool]
        kafka_enabled: Optional[bool]
        maximum_throughput_units: Optional[int]
        metric_id: Optional[str]
        minimum_tls_version: Optional[Union[str, TlsVersion]]
        platform_capabilities: Optional[PlatformCapabilities]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        service_bus_endpoint: Optional[str]
        status: Optional[str]
        updated_at: Optional[datetime]
        zone_redundant: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                cluster_arm_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                geo_data_replication: Optional[GeoDataReplicationProperties] = ..., 
                ip_address_type: Optional[Union[str, IpAddressType]] = ..., 
                is_auto_inflate_enabled: Optional[bool] = ..., 
                kafka_enabled: Optional[bool] = ..., 
                maximum_throughput_units: Optional[int] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                platform_capabilities: Optional[PlatformCapabilities] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                zone_redundant: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.EncodingCaptureDescription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        AVRO_DEFLATE = "AvroDeflate"


    class azure.mgmt.eventhub.models.Encryption(_Model):
        key_source: Optional[Literal["KeyVault"]]
        key_vault_properties: Optional[list[KeyVaultProperties]]
        require_infrastructure_encryption: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                key_source: Optional[Literal[KeyVault]] = ..., 
                key_vault_properties: Optional[list[KeyVaultProperties]] = ..., 
                require_infrastructure_encryption: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.EndPointProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.eventhub.models.EntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        RECEIVE_DISABLED = "ReceiveDisabled"
        RENAMING = "Renaming"
        RESTORING = "Restoring"
        SEND_DISABLED = "SendDisabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.eventhub.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.eventhub.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.eventhub.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.Eventhub(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[EventhubProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EventhubProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.EventhubProperties(_Model):
        capture_description: Optional[CaptureDescription]
        created_at: Optional[datetime]
        identifier: Optional[str]
        message_retention_in_days: Optional[int]
        message_timestamp_description: Optional[MessageTimestampDescription]
        partition_count: Optional[int]
        partition_ids: Optional[list[str]]
        retention_description: Optional[RetentionDescription]
        status: Optional[Union[str, EntityStatus]]
        updated_at: Optional[datetime]
        user_metadata: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capture_description: Optional[CaptureDescription] = ..., 
                message_retention_in_days: Optional[int] = ..., 
                message_timestamp_description: Optional[MessageTimestampDescription] = ..., 
                partition_count: Optional[int] = ..., 
                retention_description: Optional[RetentionDescription] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                user_metadata: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.FailOver(_Model):
        properties: Optional[FailOverProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FailOverProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.FailOverProperties(_Model):
        force: Optional[bool]
        primary_location: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                force: Optional[bool] = ..., 
                primary_location: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.GeoDRRoleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.eventhub.models.GeoDataReplicationProperties(_Model):
        locations: Optional[list[NamespaceReplicaLocation]]
        max_replication_lag_duration_in_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[NamespaceReplicaLocation]] = ..., 
                max_replication_lag_duration_in_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.IpAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        I_PV4 = "IPv4"


    class azure.mgmt.eventhub.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.eventhub.models.KeyVaultProperties(_Model):
        identity: Optional[UserAssignedIdentityProperties]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedIdentityProperties] = ..., 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventhub.models.MessageTimestampDescription(_Model):
        timestamp_type: Optional[Union[str, TimestampType]]

        @overload
        def __init__(
                self, 
                *, 
                timestamp_type: Optional[Union[str, TimestampType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.MetricId(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCOMING_BYTES = "IncomingBytes"
        INCOMING_MESSAGES = "IncomingMessages"
        OUTGOING_BYTES = "OutgoingBytes"
        OUTGOING_MESSAGES = "OutgoingMessages"


    class azure.mgmt.eventhub.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.eventhub.models.NWRuleSetIpRules(_Model):
        action: Optional[Union[str, NetworkRuleIPAction]]
        ip_mask: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, NetworkRuleIPAction]] = ..., 
                ip_mask: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NWRuleSetVirtualNetworkRules(_Model):
        ignore_missing_vnet_service_endpoint: Optional[bool]
        subnet: Optional[Subnet]

        @overload
        def __init__(
                self, 
                *, 
                ignore_missing_vnet_service_endpoint: Optional[bool] = ..., 
                subnet: Optional[Subnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NamespaceReplicaLocation(_Model):
        cluster_arm_id: Optional[str]
        location_name: Optional[str]
        replica_state: Optional[str]
        role_type: Optional[Union[str, GeoDRRoleType]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_arm_id: Optional[str] = ..., 
                location_name: Optional[str] = ..., 
                role_type: Optional[Union[str, GeoDRRoleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkRuleIPAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.eventhub.models.NetworkRuleSet(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[NetworkRuleSetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkRuleSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.NetworkRuleSetListResult(_Model):
        next_link: Optional[str]
        value: list[NetworkRuleSet]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[NetworkRuleSet]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkRuleSetProperties(_Model):
        default_action: Optional[Union[str, DefaultAction]]
        ip_rules: Optional[list[NWRuleSetIpRules]]
        public_network_access: Optional[Union[str, PublicNetworkAccessFlag]]
        trusted_service_access_enabled: Optional[bool]
        virtual_network_rules: Optional[list[NWRuleSetVirtualNetworkRules]]

        @overload
        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, DefaultAction]] = ..., 
                ip_rules: Optional[list[NWRuleSetIpRules]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccessFlag]] = ..., 
                trusted_service_access_enabled: Optional[bool] = ..., 
                virtual_network_rules: Optional[list[NWRuleSetVirtualNetworkRules]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeter(_Model):
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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[NetworkSecurityPerimeterConfigurationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NetworkSecurityPerimeterConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationList(_Model):
        value: Optional[list[NetworkSecurityPerimeterConfiguration]]


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
        applicable_features: Optional[list[str]]
        is_backing_resource: Optional[bool]
        network_security_perimeter: Optional[NetworkSecurityPerimeter]
        parent_association_name: Optional[str]
        profile: Optional[NetworkSecurityPerimeterConfigurationPropertiesProfile]
        provisioning_issues: Optional[list[ProvisioningIssue]]
        provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]]
        resource_association: Optional[NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation]
        source_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationPropertiesProfile(_Model):
        access_rules: Optional[list[NspAccessRule]]
        access_rules_version: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_rules: Optional[list[NspAccessRule]] = ..., 
                access_rules_version: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(_Model):
        access_mode: Optional[Union[str, ResourceAssociationAccessMode]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID_RESPONSE = "InvalidResponse"
        SUCCEEDED = "Succeeded"
        SUCCEEDED_WITH_ISSUES = "SucceededWithIssues"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.eventhub.models.NspAccessRule(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[NspAccessRuleProperties]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.eventhub.models.NspAccessRuleProperties(_Model):
        address_prefixes: Optional[list[str]]
        direction: Optional[Union[str, NspAccessRuleDirection]]
        fully_qualified_domain_names: Optional[list[str]]
        network_security_perimeters: Optional[list[NetworkSecurityPerimeter]]
        subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                address_prefixes: Optional[list[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                subscriptions: Optional[list[NspAccessRulePropertiesSubscriptionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.NspAccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        origin: Optional[str]
        properties: Optional[Any]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.eventhub.models.PlatformCapabilities(_Model):
        confidential_compute: Optional[ConfidentialCompute]

        @overload
        def __init__(
                self, 
                *, 
                confidential_compute: Optional[ConfidentialCompute] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.PrivateEndpointConnection(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.PrivateEndpointConnectionProperties(_Model):
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: Optional[ConnectionState]
        provisioning_state: Optional[Union[str, EndPointProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[ConnectionState] = ..., 
                provisioning_state: Optional[Union[str, EndPointProvisioningState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.eventhub.models.PrivateLinkResource(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[PrivateLinkResourceProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[PrivateLinkResourceProperties] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                required_members: Optional[list[str]] = ..., 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.PrivateLinkResourcesListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateLinkResource]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrivateLinkResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ProvisioningIssue(_Model):
        name: Optional[str]
        properties: Optional[ProvisioningIssueProperties]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ProvisioningIssueProperties(_Model):
        description: Optional[str]
        issue_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SCALING = "Scaling"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.eventhub.models.ProvisioningStateDR(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.eventhub.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventhub.models.PublicNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventhub.models.RegenerateAccessKeyParameters(_Model):
        key: Optional[str]
        key_type: Union[str, KeyType]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                key_type: Union[str, KeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.eventhub.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT_MODE = "AuditMode"
        ENFORCED_MODE = "EnforcedMode"
        LEARNING_MODE = "LearningMode"
        NO_ASSOCIATION_MODE = "NoAssociationMode"
        UNSPECIFIED_MODE = "UnspecifiedMode"


    class azure.mgmt.eventhub.models.RetentionDescription(_Model):
        cleanup_policy: Optional[Union[str, CleanupPolicyRetentionDescription]]
        min_compaction_lag_time_in_minutes: Optional[int]
        retention_time_in_hours: Optional[int]
        tombstone_retention_time_in_hours: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cleanup_policy: Optional[Union[str, CleanupPolicyRetentionDescription]] = ..., 
                min_compaction_lag_time_in_minutes: Optional[int] = ..., 
                retention_time_in_hours: Optional[int] = ..., 
                tombstone_retention_time_in_hours: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.RoleDisasterRecovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_NOT_REPLICATING = "PrimaryNotReplicating"
        SECONDARY = "Secondary"


    class azure.mgmt.eventhub.models.SchemaCompatibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKWARD = "Backward"
        FORWARD = "Forward"
        NONE = "None"


    class azure.mgmt.eventhub.models.SchemaGroup(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SchemaGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.eventhub.models.SchemaGroupProperties(_Model):
        created_at_utc: Optional[datetime]
        e_tag: Optional[str]
        group_properties: Optional[dict[str, str]]
        schema_compatibility: Optional[Union[str, SchemaCompatibility]]
        schema_type: Optional[Union[str, SchemaType]]
        updated_at_utc: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                group_properties: Optional[dict[str, str]] = ..., 
                schema_compatibility: Optional[Union[str, SchemaCompatibility]] = ..., 
                schema_type: Optional[Union[str, SchemaType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        JSON = "Json"
        PROTO_BUF = "ProtoBuf"
        UNKNOWN = "Unknown"


    class azure.mgmt.eventhub.models.Sku(_Model):
        capacity: Optional[int]
        name: Union[str, SkuName]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SkuName], 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.eventhub.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.eventhub.models.Subnet(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.SystemData(_Model):
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


    class azure.mgmt.eventhub.models.ThrottlingPolicy(ApplicationGroupPolicy, discriminator='ThrottlingPolicy'):
        metric_id: Union[str, MetricId]
        name: str
        rate_limit_threshold: int
        type: Literal[ApplicationGroupPolicyType.THROTTLING_POLICY]

        @overload
        def __init__(
                self, 
                *, 
                metric_id: Union[str, MetricId], 
                name: str, 
                rate_limit_threshold: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.eventhub.models.TimestampType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        LOG_APPEND = "LogAppend"


    class azure.mgmt.eventhub.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"
        ONE3 = "1.3"


    class azure.mgmt.eventhub.models.UnavailableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_NAME = "InvalidName"
        NAME_IN_LOCKDOWN = "NameInLockdown"
        NAME_IN_USE = "NameInUse"
        NONE = "None"
        SUBSCRIPTION_IS_DISABLED = "SubscriptionIsDisabled"
        TOO_MANY_NAMESPACE_IN_CURRENT_SUBSCRIPTION = "TooManyNamespaceInCurrentSubscription"


    class azure.mgmt.eventhub.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.eventhub.models.UserAssignedIdentityProperties(_Model):
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.eventhub.operations

    class azure.mgmt.eventhub.operations.ApplicationGroupOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        def create_or_update_application_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ApplicationGroup]: ...


    class azure.mgmt.eventhub.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list_available_cluster_region(self, **kwargs: Any) -> AvailableClustersList: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_namespaces(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> EHNamespaceIdListResult: ...


    class azure.mgmt.eventhub.operations.ConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterQuotaConfigurationProperties: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterQuotaConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: ClusterQuotaConfigurationProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...

        @overload
        def patch(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[ClusterQuotaConfigurationProperties]: ...


    class azure.mgmt.eventhub.operations.ConsumerGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: ConsumerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: ConsumerGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                consumer_group_name: str, 
                **kwargs: Any
            ) -> ConsumerGroup: ...

        @distributed_trace
        def list_by_event_hub(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ConsumerGroup]: ...


    class azure.mgmt.eventhub.operations.DisasterRecoveryConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def break_pairing(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: ArmDisasterRecovery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: ArmDisasterRecovery, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> ArmDisasterRecovery: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ArmDisasterRecovery]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthorizationRule]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.eventhub.operations.EventHubsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: Eventhub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: Eventhub, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Eventhub: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> Eventhub: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Eventhub]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                event_hub_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.eventhub.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EHNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EHNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EHNamespace]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: FailOver, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailOver]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: FailOver, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailOver]: ...

        @overload
        def begin_failover(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FailOver]: ...

        @overload
        def check_name_availability(
                self, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                parameters: CheckNameAvailabilityParameter, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: AuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @overload
        def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NetworkRuleSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @overload
        def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: NetworkRuleSet, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @overload
        def create_or_update_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> EHNamespace: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AuthorizationRule: ...

        @distributed_trace
        def get_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[EHNamespace]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthorizationRule]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EHNamespace]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @distributed_trace
        def list_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSetListResult: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: RegenerateAccessKeyParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: EHNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[EHNamespace]: ...


    class azure.mgmt.eventhub.operations.NetworkSecurityPerimeterConfigurationOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfigurationList: ...


    class azure.mgmt.eventhub.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> LROPoller[NetworkSecurityPerimeterConfiguration]: ...

        @distributed_trace
        def get_resource_association_name(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...


    class azure.mgmt.eventhub.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.eventhub.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.eventhub.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourcesListResult: ...


    class azure.mgmt.eventhub.operations.SchemaRegistryOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: SchemaGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: SchemaGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                schema_group_name: str, 
                **kwargs: Any
            ) -> SchemaGroup: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SchemaGroup]: ...


namespace azure.mgmt.eventhub.types

    class azure.mgmt.eventhub.types.AccessKeys(TypedDict, total=False):
        key "aliasPrimaryConnectionString": str
        key "aliasSecondaryConnectionString": str
        key "keyName": str
        key "primaryConnectionString": str
        key "primaryKey": str
        key "secondaryConnectionString": str
        key "secondaryKey": str
        alias_primary_connection_string: str
        alias_secondary_connection_string: str
        key_name: str
        primary_connection_string: str
        primary_key: str
        secondary_connection_string: str
        secondary_key: str


    class azure.mgmt.eventhub.types.ApplicationGroup(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ApplicationGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ApplicationGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.ApplicationGroupPolicy(TypedDict, total=False):
        key "metricId": Required[Union[str, MetricId]]
        key "name": Required[str]
        key "rateLimitThreshold": Required[int]
        key "type": Required[Literal[ApplicationGroupPolicyType.THROTTLING_POLICY]]
        metric_id: Union[str, MetricId]
        name: str
        rate_limit_threshold: int
        type: Literal[ApplicationGroupPolicyType.THROTTLING_POLICY]


    class azure.mgmt.eventhub.types.ApplicationGroupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLING_POLICY = "ThrottlingPolicy"


    class azure.mgmt.eventhub.types.ApplicationGroupProperties(TypedDict, total=False):
        key "clientAppGroupIdentifier": Required[str]
        key "isEnabled": bool
        client_app_group_identifier: str
        is_enabled: bool
        policies: list[ApplicationGroupPolicy]


    class azure.mgmt.eventhub.types.ArmDisasterRecovery(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ArmDisasterRecoveryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ArmDisasterRecoveryProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.ArmDisasterRecoveryProperties(TypedDict, total=False):
        key "alternateName": str
        key "partnerNamespace": str
        key "pendingReplicationOperationsCount": int
        key "provisioningState": Union[str, ProvisioningStateDR]
        key "role": Union[str, RoleDisasterRecovery]
        alternate_name: str
        partner_namespace: str
        pending_replication_operations_count: int
        provisioning_state: Union[str, ProvisioningStateDR]
        role: Union[str, RoleDisasterRecovery]


    class azure.mgmt.eventhub.types.AuthorizationRule(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('AuthorizationRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AuthorizationRuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.AuthorizationRuleProperties(TypedDict, total=False):
        key "rights": Required[list[Union[str, AccessRights]]]
        rights: list[Union[str, AccessRights]]


    class azure.mgmt.eventhub.types.AvailableCluster(TypedDict, total=False):
        key "location": str
        location: str


    class azure.mgmt.eventhub.types.AvailableClustersList(TypedDict, total=False):
        value: list[AvailableCluster]


    class azure.mgmt.eventhub.types.CaptureDescription(TypedDict, total=False):
        key "destination": ForwardRef('Destination', module='types')
        key "enabled": bool
        key "encoding": Union[str, EncodingCaptureDescription]
        key "intervalInSeconds": int
        key "sizeLimitInBytes": int
        key "skipEmptyArchives": bool
        destination: Destination
        enabled: bool
        encoding: Union[str, EncodingCaptureDescription]
        interval_in_seconds: int
        size_limit_in_bytes: int
        skip_empty_archives: bool


    class azure.mgmt.eventhub.types.CaptureIdentity(TypedDict, total=False):
        key "type": Union[str, CaptureIdentityType]
        key "userAssignedIdentity": str
        type: Union[str, CaptureIdentityType]
        user_assigned_identity: str


    class azure.mgmt.eventhub.types.CheckNameAvailabilityParameter(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.eventhub.types.CheckNameAvailabilityResult(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": Union[str, UnavailableReason]
        message: str
        name_available: bool
        reason: Union[str, UnavailableReason]


    class azure.mgmt.eventhub.types.Cluster(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "sku": ForwardRef('ClusterSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ClusterProperties
        sku: ClusterSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventhub.types.ClusterProperties(TypedDict, total=False):
        key "createdAt": str
        key "metricId": str
        key "platformCapabilities": ForwardRef('PlatformCapabilities', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "status": str
        key "supportsScaling": bool
        key "updatedAt": str
        key "zoneRedundant": bool
        created_at: str
        metric_id: str
        platform_capabilities: PlatformCapabilities
        provisioning_state: Union[str, ProvisioningState]
        status: str
        supports_scaling: bool
        updated_at: str
        zone_redundant: bool


    class azure.mgmt.eventhub.types.ClusterQuotaConfigurationProperties(TypedDict, total=False):
        settings: dict[str, str]


    class azure.mgmt.eventhub.types.ClusterSku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[Union[str, ClusterSkuName]]
        capacity: int
        name: Union[str, ClusterSkuName]


    class azure.mgmt.eventhub.types.ConfidentialCompute(TypedDict, total=False):
        key "mode": Union[str, Mode]
        mode: Union[str, Mode]


    class azure.mgmt.eventhub.types.ConnectionState(TypedDict, total=False):
        key "description": str
        key "status": Union[str, PrivateLinkConnectionStatus]
        description: str
        status: Union[str, PrivateLinkConnectionStatus]


    class azure.mgmt.eventhub.types.ConsumerGroup(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('ConsumerGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ConsumerGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.ConsumerGroupProperties(TypedDict, total=False):
        key "createdAt": str
        key "updatedAt": str
        key "userMetadata": str
        created_at: str
        updated_at: str
        user_metadata: str


    class azure.mgmt.eventhub.types.Destination(TypedDict, total=False):
        key "identity": ForwardRef('CaptureIdentity', module='types')
        key "name": str
        key "properties": ForwardRef('DestinationProperties', module='types')
        identity: CaptureIdentity
        name: str
        properties: DestinationProperties


    class azure.mgmt.eventhub.types.DestinationProperties(TypedDict, total=False):
        key "archiveNameFormat": str
        key "blobContainer": str
        key "dataLakeAccountName": str
        key "dataLakeFolderPath": str
        key "dataLakeSubscriptionId": str
        key "storageAccountResourceId": str
        archive_name_format: str
        blob_container: str
        data_lake_account_name: str
        data_lake_folder_path: str
        data_lake_subscription_id: str
        storage_account_resource_id: str


    class azure.mgmt.eventhub.types.EHNamespace(ProxyResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('EHNamespaceProperties', module='types')
        key "sku": ForwardRef('Sku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        location: str
        name: str
        properties: EHNamespaceProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.eventhub.types.EHNamespaceIdContainer(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.eventhub.types.EHNamespaceIdListResult(TypedDict, total=False):
        value: list[EHNamespaceIdContainer]


    class azure.mgmt.eventhub.types.EHNamespaceProperties(TypedDict, total=False):
        key "alternateName": str
        key "clusterArmId": str
        key "createdAt": str
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "geoDataReplication": ForwardRef('GeoDataReplicationProperties', module='types')
        key "ipAddressType": Union[str, IpAddressType]
        key "isAutoInflateEnabled": bool
        key "kafkaEnabled": bool
        key "maximumThroughputUnits": int
        key "metricId": str
        key "minimumTlsVersion": Union[str, TlsVersion]
        key "platformCapabilities": ForwardRef('PlatformCapabilities', module='types')
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "serviceBusEndpoint": str
        key "status": str
        key "updatedAt": str
        key "zoneRedundant": bool
        alternate_name: str
        cluster_arm_id: str
        created_at: str
        disable_local_auth: bool
        encryption: Encryption
        geo_data_replication: GeoDataReplicationProperties
        ip_address_type: Union[str, IpAddressType]
        is_auto_inflate_enabled: bool
        kafka_enabled: bool
        maximum_throughput_units: int
        metric_id: str
        minimum_tls_version: Union[str, TlsVersion]
        platform_capabilities: PlatformCapabilities
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        service_bus_endpoint: str
        status: str
        updated_at: str
        zone_redundant: bool


    class azure.mgmt.eventhub.types.Encryption(TypedDict, total=False):
        key "keySource": Literal["KeyVault"]
        key "requireInfrastructureEncryption": bool
        keyVaultProperties: list[KeyVaultProperties]
        key_source: Literal[KeyVault]
        key_vault_properties: list[KeyVaultProperties]
        require_infrastructure_encryption: bool


    class azure.mgmt.eventhub.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.eventhub.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.eventhub.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.eventhub.types.Eventhub(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('EventhubProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: EventhubProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.EventhubProperties(TypedDict, total=False):
        key "captureDescription": ForwardRef('CaptureDescription', module='types')
        key "createdAt": str
        key "identifier": str
        key "messageRetentionInDays": int
        key "messageTimestampDescription": ForwardRef('MessageTimestampDescription', module='types')
        key "partitionCount": int
        key "retentionDescription": ForwardRef('RetentionDescription', module='types')
        key "status": Union[str, EntityStatus]
        key "updatedAt": str
        key "userMetadata": str
        capture_description: CaptureDescription
        created_at: str
        identifier: str
        message_retention_in_days: int
        message_timestamp_description: MessageTimestampDescription
        partitionIds: list[str]
        partition_count: int
        partition_ids: list[str]
        retention_description: RetentionDescription
        status: Union[str, EntityStatus]
        updated_at: str
        user_metadata: str


    class azure.mgmt.eventhub.types.FailOver(TypedDict, total=False):
        key "properties": ForwardRef('FailOverProperties', module='types')
        properties: FailOverProperties


    class azure.mgmt.eventhub.types.FailOverProperties(TypedDict, total=False):
        key "force": bool
        key "primaryLocation": str
        force: bool
        primary_location: str


    class azure.mgmt.eventhub.types.GeoDataReplicationProperties(TypedDict, total=False):
        key "maxReplicationLagDurationInSeconds": int
        locations: list[NamespaceReplicaLocation]
        max_replication_lag_duration_in_seconds: int


    class azure.mgmt.eventhub.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedServiceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.eventhub.types.KeyVaultProperties(TypedDict, total=False):
        key "identity": ForwardRef('UserAssignedIdentityProperties', module='types')
        key "keyName": str
        key "keyVaultUri": str
        key "keyVersion": str
        identity: UserAssignedIdentityProperties
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.eventhub.types.MessageTimestampDescription(TypedDict, total=False):
        key "timestampType": Union[str, TimestampType]
        timestamp_type: Union[str, TimestampType]


    class azure.mgmt.eventhub.types.NWRuleSetIpRules(TypedDict, total=False):
        key "action": Union[str, NetworkRuleIPAction]
        key "ipMask": str
        action: Union[str, NetworkRuleIPAction]
        ip_mask: str


    class azure.mgmt.eventhub.types.NWRuleSetVirtualNetworkRules(TypedDict, total=False):
        key "ignoreMissingVnetServiceEndpoint": bool
        key "subnet": ForwardRef('Subnet', module='types')
        ignore_missing_vnet_service_endpoint: bool
        subnet: Subnet


    class azure.mgmt.eventhub.types.NamespaceReplicaLocation(TypedDict, total=False):
        key "clusterArmId": str
        key "locationName": str
        key "replicaState": str
        key "roleType": Union[str, GeoDRRoleType]
        cluster_arm_id: str
        location_name: str
        replica_state: str
        role_type: Union[str, GeoDRRoleType]


    class azure.mgmt.eventhub.types.NetworkRuleSet(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('NetworkRuleSetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NetworkRuleSetProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.NetworkRuleSetListResult(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[NetworkRuleSet]]
        next_link: str
        value: list[NetworkRuleSet]


    class azure.mgmt.eventhub.types.NetworkRuleSetProperties(TypedDict, total=False):
        key "defaultAction": Union[str, DefaultAction]
        key "publicNetworkAccess": Union[str, PublicNetworkAccessFlag]
        key "trustedServiceAccessEnabled": bool
        default_action: Union[str, DefaultAction]
        ipRules: list[NWRuleSetIpRules]
        ip_rules: list[NWRuleSetIpRules]
        public_network_access: Union[str, PublicNetworkAccessFlag]
        trusted_service_access_enabled: bool
        virtualNetworkRules: list[NWRuleSetVirtualNetworkRules]
        virtual_network_rules: list[NWRuleSetVirtualNetworkRules]


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeter(TypedDict, total=False):
        key "id": str
        key "location": str
        key "perimeterGuid": str
        id: str
        location: str
        perimeter_guid: str


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeterConfiguration(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('NetworkSecurityPerimeterConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: NetworkSecurityPerimeterConfigurationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeterConfigurationList(TypedDict, total=False):
        value: list[NetworkSecurityPerimeterConfiguration]


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeterConfigurationProperties(TypedDict, total=False):
        key "isBackingResource": bool
        key "networkSecurityPerimeter": ForwardRef('NetworkSecurityPerimeter', module='types')
        key "parentAssociationName": str
        key "profile": ForwardRef('NetworkSecurityPerimeterConfigurationPropertiesProfile', module='types')
        key "provisioningState": Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]
        key "resourceAssociation": ForwardRef('NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation', module='types')
        key "sourceResourceId": str
        applicableFeatures: list[str]
        applicable_features: list[str]
        is_backing_resource: bool
        network_security_perimeter: NetworkSecurityPerimeter
        parent_association_name: str
        profile: NetworkSecurityPerimeterConfigurationPropertiesProfile
        provisioningIssues: list[ProvisioningIssue]
        provisioning_issues: list[ProvisioningIssue]
        provisioning_state: Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]
        resource_association: NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation
        source_resource_id: str


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeterConfigurationPropertiesProfile(TypedDict, total=False):
        key "accessRulesVersion": str
        key "name": str
        accessRules: list[NspAccessRule]
        access_rules: list[NspAccessRule]
        access_rules_version: str
        name: str


    class azure.mgmt.eventhub.types.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(TypedDict, total=False):
        key "accessMode": Union[str, ResourceAssociationAccessMode]
        key "name": str
        access_mode: Union[str, ResourceAssociationAccessMode]
        name: str


    class azure.mgmt.eventhub.types.NspAccessRule(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NspAccessRuleProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: NspAccessRuleProperties
        type: str


    class azure.mgmt.eventhub.types.NspAccessRuleProperties(TypedDict, total=False):
        key "direction": Union[str, NspAccessRuleDirection]
        addressPrefixes: list[str]
        address_prefixes: list[str]
        direction: Union[str, NspAccessRuleDirection]
        fullyQualifiedDomainNames: list[str]
        fully_qualified_domain_names: list[str]
        networkSecurityPerimeters: list[NetworkSecurityPerimeter]
        network_security_perimeters: list[NetworkSecurityPerimeter]
        subscriptions: list[NspAccessRulePropertiesSubscriptionsItem]


    class azure.mgmt.eventhub.types.NspAccessRulePropertiesSubscriptionsItem(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.eventhub.types.Operation(TypedDict, total=False):
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": str
        key "properties": Any
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: Any


    class azure.mgmt.eventhub.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.eventhub.types.PlatformCapabilities(TypedDict, total=False):
        key "confidentialCompute": ForwardRef('ConfidentialCompute', module='types')
        confidential_compute: ConfidentialCompute


    class azure.mgmt.eventhub.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.eventhub.types.PrivateEndpointConnection(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('ConnectionState', module='types')
        key "provisioningState": Union[str, EndPointProvisioningState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: ConnectionState
        provisioning_state: Union[str, EndPointProvisioningState]


    class azure.mgmt.eventhub.types.PrivateLinkResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        type: str


    class azure.mgmt.eventhub.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.eventhub.types.PrivateLinkResourcesListResult(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[PrivateLinkResource]]
        next_link: str
        value: list[PrivateLinkResource]


    class azure.mgmt.eventhub.types.ProvisioningIssue(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ProvisioningIssueProperties', module='types')
        name: str
        properties: ProvisioningIssueProperties


    class azure.mgmt.eventhub.types.ProvisioningIssueProperties(TypedDict, total=False):
        key "description": str
        key "issueType": str
        description: str
        issue_type: str


    class azure.mgmt.eventhub.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.RegenerateAccessKeyParameters(TypedDict, total=False):
        key "key": str
        key "keyType": Required[Union[str, KeyType]]
        key: str
        key_type: Union[str, KeyType]


    class azure.mgmt.eventhub.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.RetentionDescription(TypedDict, total=False):
        key "cleanupPolicy": Union[str, CleanupPolicyRetentionDescription]
        key "minCompactionLagTimeInMinutes": int
        key "retentionTimeInHours": int
        key "tombstoneRetentionTimeInHours": int
        cleanup_policy: Union[str, CleanupPolicyRetentionDescription]
        min_compaction_lag_time_in_minutes: int
        retention_time_in_hours: int
        tombstone_retention_time_in_hours: int


    class azure.mgmt.eventhub.types.SchemaGroup(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SchemaGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SchemaGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.eventhub.types.SchemaGroupProperties(TypedDict, total=False):
        key "createdAtUtc": str
        key "eTag": str
        key "schemaCompatibility": Union[str, SchemaCompatibility]
        key "schemaType": Union[str, SchemaType]
        key "updatedAtUtc": str
        created_at_utc: str
        e_tag: str
        groupProperties: dict[str, str]
        group_properties: dict[str, str]
        schema_compatibility: Union[str, SchemaCompatibility]
        schema_type: Union[str, SchemaType]
        updated_at_utc: str


    class azure.mgmt.eventhub.types.Sku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[Union[str, SkuName]]
        key "tier": Union[str, SkuTier]
        capacity: int
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.eventhub.types.Subnet(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.eventhub.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.eventhub.types.ThrottlingPolicy(TypedDict, total=False):
        key "metricId": Required[Union[str, MetricId]]
        key "name": Required[str]
        key "rateLimitThreshold": Required[int]
        key "type": Required[Literal[ApplicationGroupPolicyType.THROTTLING_POLICY]]
        metric_id: Union[str, MetricId]
        name: str
        rate_limit_threshold: int
        type: Literal[ApplicationGroupPolicyType.THROTTLING_POLICY]


    class azure.mgmt.eventhub.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.eventhub.types.UserAssignedIdentityProperties(TypedDict, total=False):
        key "userAssignedIdentity": str
        user_assigned_identity: str


```