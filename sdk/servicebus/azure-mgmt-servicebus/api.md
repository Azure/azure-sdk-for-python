```py
namespace azure.mgmt.servicebus

    class azure.mgmt.servicebus.ServiceBusManagementClient: implements ContextManager 
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        migration_configs: MigrationConfigsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configuration: NetworkSecurityPerimeterConfigurationOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        queues: QueuesOperations
        rules: RulesOperations
        subscriptions: SubscriptionsOperations
        topics: TopicsOperations

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


namespace azure.mgmt.servicebus.aio

    class azure.mgmt.servicebus.aio.ServiceBusManagementClient: implements AsyncContextManager 
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        migration_configs: MigrationConfigsOperations
        namespaces: NamespacesOperations
        network_security_perimeter_configuration: NetworkSecurityPerimeterConfigurationOperations
        network_security_perimeter_configurations: NetworkSecurityPerimeterConfigurationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        queues: QueuesOperations
        rules: RulesOperations
        subscriptions: SubscriptionsOperations
        topics: TopicsOperations

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


namespace azure.mgmt.servicebus.aio.operations

    class azure.mgmt.servicebus.aio.operations.DisasterRecoveryConfigsOperations:

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
                parameters: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailability, 
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

        @overload
        async def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[NamespaceFailoverProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[NamespaceFailoverProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
            ) -> SBAuthorizationRule: ...

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
            ) -> AsyncItemPaged[SBAuthorizationRule]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.servicebus.aio.operations.MigrationConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: MigrationConfigProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationConfigProperties]: ...

        @overload
        async def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: MigrationConfigProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationConfigProperties]: ...

        @overload
        async def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationConfigProperties]: ...

        @distributed_trace_async
        async def complete_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> MigrationConfigProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationConfigProperties]: ...

        @distributed_trace_async
        async def revert(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicebus.aio.operations.NamespacesOperations:

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
                parameters: SBNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SBNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: SBNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SBNamespace]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SBNamespace]: ...

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
                parameters: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                parameters: CheckNameAvailability, 
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
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

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
            ) -> SBAuthorizationRule: ...

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
            ) -> SBNamespace: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace_async
        async def get_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[SBNamespace]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SBNamespace]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @distributed_trace
        def list_network_rule_sets(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NetworkRuleSet]: ...

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
                parameters: SBNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: SBNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...


    class azure.mgmt.servicebus.aio.operations.NetworkSecurityPerimeterConfigurationOperations:

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
            ) -> AsyncItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.servicebus.aio.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_resource_association_name(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace_async
        async def reconcile(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicebus.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.servicebus.aio.operations.PrivateEndpointConnectionsOperations:

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


    class azure.mgmt.servicebus.aio.operations.PrivateLinkResourcesOperations:

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


    class azure.mgmt.servicebus.aio.operations.QueuesOperations:

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
                queue_name: str, 
                parameters: SBQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                parameters: SBQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> SBQueue: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SBQueue]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
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
                queue_name: str, 
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
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.servicebus.aio.operations.RulesOperations:

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
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list_by_subscriptions(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Rule]: ...


    class azure.mgmt.servicebus.aio.operations.SubscriptionsOperations:

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
                topic_name: str, 
                subscription_name: str, 
                parameters: SBSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                parameters: SBSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SBSubscription: ...

        @distributed_trace
        def list_by_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SBSubscription]: ...


    class azure.mgmt.servicebus.aio.operations.TopicsOperations:

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
                topic_name: str, 
                parameters: SBTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                parameters: SBTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        async def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> SBTopic: ...

        @distributed_trace_async
        async def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SBTopic]: ...

        @distributed_trace_async
        async def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        async def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
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
                topic_name: str, 
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
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


namespace azure.mgmt.servicebus.models

    class azure.mgmt.servicebus.models.AccessKeys(_Model):
        alias_primary_connection_string: Optional[str]
        alias_secondary_connection_string: Optional[str]
        key_name: Optional[str]
        primary_connection_string: Optional[str]
        primary_key: Optional[str]
        secondary_connection_string: Optional[str]
        secondary_key: Optional[str]


    class azure.mgmt.servicebus.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.servicebus.models.Action(_Model):
        compatibility_level: Optional[int]
        requires_preprocessing: Optional[bool]
        sql_expression: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compatibility_level: Optional[int] = ..., 
                requires_preprocessing: Optional[bool] = ..., 
                sql_expression: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.ArmDisasterRecovery(ProxyResource):
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


    class azure.mgmt.servicebus.models.ArmDisasterRecoveryProperties(_Model):
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


    class azure.mgmt.servicebus.models.CheckNameAvailability(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.CheckNameAvailabilityResult(_Model):
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


    class azure.mgmt.servicebus.models.ConfidentialCompute(_Model):
        mode: Optional[Union[str, Mode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, Mode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.ConnectionState(_Model):
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


    class azure.mgmt.servicebus.models.CorrelationFilter(_Model):
        content_type: Optional[str]
        correlation_id: Optional[str]
        label: Optional[str]
        message_id: Optional[str]
        properties: Optional[dict[str, str]]
        reply_to: Optional[str]
        reply_to_session_id: Optional[str]
        requires_preprocessing: Optional[bool]
        session_id: Optional[str]
        to: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                correlation_id: Optional[str] = ..., 
                label: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                properties: Optional[dict[str, str]] = ..., 
                reply_to: Optional[str] = ..., 
                reply_to_session_id: Optional[str] = ..., 
                requires_preprocessing: Optional[bool] = ..., 
                session_id: Optional[str] = ..., 
                to: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicebus.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.servicebus.models.Encryption(_Model):
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


    class azure.mgmt.servicebus.models.EndPointProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.servicebus.models.EntityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        RECEIVE_DISABLED = "ReceiveDisabled"
        RENAMING = "Renaming"
        RESTORING = "Restoring"
        SEND_DISABLED = "SendDisabled"
        UNKNOWN = "Unknown"


    class azure.mgmt.servicebus.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.servicebus.models.ErrorResponse(_Model):
        error: Optional[ErrorResponseError]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.ErrorResponseError(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorResponse]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.servicebus.models.FailOver(_Model):
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


    class azure.mgmt.servicebus.models.FailOverProperties(_Model):
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


    class azure.mgmt.servicebus.models.FailoverPropertiesProperties(_Model):
        is_safe_failover: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                is_safe_failover: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CORRELATION_FILTER = "CorrelationFilter"
        SQL_FILTER = "SqlFilter"


    class azure.mgmt.servicebus.models.GeoDRRoleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        SECONDARY = "Secondary"


    class azure.mgmt.servicebus.models.GeoDataReplicationProperties(_Model):
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


    class azure.mgmt.servicebus.models.Identity(_Model):
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


    class azure.mgmt.servicebus.models.IpAddressType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_STACK = "DualStack"
        I_PV4 = "IPv4"


    class azure.mgmt.servicebus.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.servicebus.models.KeyVaultProperties(_Model):
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


    class azure.mgmt.servicebus.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.servicebus.models.MessageCountDetails(_Model):
        active_message_count: Optional[int]
        dead_letter_message_count: Optional[int]
        scheduled_message_count: Optional[int]
        transfer_dead_letter_message_count: Optional[int]
        transfer_message_count: Optional[int]


    class azure.mgmt.servicebus.models.MigrationConfigProperties(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[MigrationConfigPropertiesProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrationConfigPropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.MigrationConfigPropertiesProperties(_Model):
        migration_state: Optional[str]
        pending_replication_operations_count: Optional[int]
        post_migration_name: str
        provisioning_state: Optional[str]
        target_namespace: str

        @overload
        def __init__(
                self, 
                *, 
                post_migration_name: str, 
                target_namespace: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.MigrationConfigurationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "$default"


    class azure.mgmt.servicebus.models.Mode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.servicebus.models.NWRuleSetIpRules(_Model):
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


    class azure.mgmt.servicebus.models.NWRuleSetVirtualNetworkRules(_Model):
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


    class azure.mgmt.servicebus.models.NamespaceFailoverProperties(_Model):
        properties: Optional[FailoverPropertiesProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FailoverPropertiesProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.NamespaceReplicaLocation(_Model):
        location_name: Optional[str]
        role_type: Optional[Union[str, GeoDRRoleType]]

        @overload
        def __init__(
                self, 
                *, 
                location_name: Optional[str] = ..., 
                role_type: Optional[Union[str, GeoDRRoleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.NetworkRuleIPAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.servicebus.models.NetworkRuleSet(ProxyResource):
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


    class azure.mgmt.servicebus.models.NetworkRuleSetProperties(_Model):
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


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeter(_Model):
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


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeterConfiguration(ProxyResource):
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


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeterConfigurationProperties(_Model):
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
                network_security_perimeter: Optional[NetworkSecurityPerimeter] = ..., 
                provisioning_issues: Optional[list[ProvisioningIssue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeterConfigurationPropertiesProfile(_Model):
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


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(_Model):
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


    class azure.mgmt.servicebus.models.NetworkSecurityPerimeterConfigurationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.servicebus.models.NspAccessRule(_Model):
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


    class azure.mgmt.servicebus.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.servicebus.models.NspAccessRuleProperties(_Model):
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


    class azure.mgmt.servicebus.models.NspAccessRulePropertiesSubscriptionsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.Operation(_Model):
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


    class azure.mgmt.servicebus.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.servicebus.models.PlatformCapabilities(_Model):
        confidential_compute: Optional[ConfidentialCompute]

        @overload
        def __init__(
                self, 
                *, 
                confidential_compute: Optional[ConfidentialCompute] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.PrivateEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.servicebus.models.PrivateEndpointConnectionProperties(_Model):
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


    class azure.mgmt.servicebus.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.servicebus.models.PrivateLinkResource(_Model):
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


    class azure.mgmt.servicebus.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.servicebus.models.PrivateLinkResourcesListResult(_Model):
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


    class azure.mgmt.servicebus.models.ProvisioningIssue(_Model):
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


    class azure.mgmt.servicebus.models.ProvisioningIssueProperties(_Model):
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


    class azure.mgmt.servicebus.models.ProvisioningStateDR(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.servicebus.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.servicebus.models.PublicNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.servicebus.models.RegenerateAccessKeyParameters(_Model):
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


    class azure.mgmt.servicebus.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.servicebus.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT_MODE = "AuditMode"
        ENFORCED_MODE = "EnforcedMode"
        LEARNING_MODE = "LearningMode"
        NO_ASSOCIATION_MODE = "NoAssociationMode"
        UNSPECIFIED_MODE = "UnspecifiedMode"


    class azure.mgmt.servicebus.models.ResourceNamespacePatch(Resource):
        id: str
        location: Optional[str]
        name: str
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.RoleDisasterRecovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_NOT_REPLICATING = "PrimaryNotReplicating"
        SECONDARY = "Secondary"


    class azure.mgmt.servicebus.models.Rule(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[Ruleproperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[Ruleproperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.Ruleproperties(_Model):
        action: Optional[Action]
        correlation_filter: Optional[CorrelationFilter]
        filter_type: Optional[Union[str, FilterType]]
        sql_filter: Optional[SqlFilter]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Action] = ..., 
                correlation_filter: Optional[CorrelationFilter] = ..., 
                filter_type: Optional[Union[str, FilterType]] = ..., 
                sql_filter: Optional[SqlFilter] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBAuthorizationRule(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SBAuthorizationRuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SBAuthorizationRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBAuthorizationRuleProperties(_Model):
        rights: list[Union[str, AccessRights]]

        @overload
        def __init__(
                self, 
                *, 
                rights: list[Union[str, AccessRights]]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBClientAffineProperties(_Model):
        client_id: Optional[str]
        is_durable: Optional[bool]
        is_shared: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                is_durable: Optional[bool] = ..., 
                is_shared: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBNamespace(TrackedResource):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[SBNamespaceProperties]
        sku: Optional[SBSku]
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
                properties: Optional[SBNamespaceProperties] = ..., 
                sku: Optional[SBSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBNamespaceProperties(_Model):
        alternate_name: Optional[str]
        created_at: Optional[datetime]
        disable_local_auth: Optional[bool]
        encryption: Optional[Encryption]
        geo_data_replication: Optional[GeoDataReplicationProperties]
        ip_address_type: Optional[Union[str, IpAddressType]]
        metric_id: Optional[str]
        minimum_tls_version: Optional[Union[str, TlsVersion]]
        platform_capabilities: Optional[PlatformCapabilities]
        premium_messaging_partitions: Optional[int]
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
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                geo_data_replication: Optional[GeoDataReplicationProperties] = ..., 
                ip_address_type: Optional[Union[str, IpAddressType]] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                platform_capabilities: Optional[PlatformCapabilities] = ..., 
                premium_messaging_partitions: Optional[int] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                zone_redundant: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBNamespaceUpdateParameters(ResourceNamespacePatch):
        id: str
        identity: Optional[Identity]
        location: str
        name: str
        properties: Optional[SBNamespaceUpdateProperties]
        sku: Optional[SBSku]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[SBNamespaceUpdateProperties] = ..., 
                sku: Optional[SBSku] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBNamespaceUpdateProperties(_Model):
        alternate_name: Optional[str]
        created_at: Optional[datetime]
        disable_local_auth: Optional[bool]
        encryption: Optional[Encryption]
        metric_id: Optional[str]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[str]
        service_bus_endpoint: Optional[str]
        status: Optional[str]
        updated_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                private_endpoint_connections: Optional[list[PrivateEndpointConnection]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBQueue(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SBQueueProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SBQueueProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBQueueProperties(_Model):
        accessed_at: Optional[datetime]
        auto_delete_on_idle: Optional[timedelta]
        count_details: Optional[MessageCountDetails]
        created_at: Optional[datetime]
        dead_lettering_on_message_expiration: Optional[bool]
        default_message_time_to_live: Optional[timedelta]
        duplicate_detection_history_time_window: Optional[timedelta]
        enable_batched_operations: Optional[bool]
        enable_express: Optional[bool]
        enable_partitioning: Optional[bool]
        forward_dead_lettered_messages_to: Optional[str]
        forward_to: Optional[str]
        lock_duration: Optional[timedelta]
        max_delivery_count: Optional[int]
        max_message_size_in_kilobytes: Optional[int]
        max_size_in_megabytes: Optional[int]
        message_count: Optional[int]
        requires_duplicate_detection: Optional[bool]
        requires_session: Optional[bool]
        size_in_bytes: Optional[int]
        status: Optional[Union[str, EntityStatus]]
        updated_at: Optional[datetime]
        user_metadata: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_delete_on_idle: Optional[timedelta] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[timedelta] = ..., 
                duplicate_detection_history_time_window: Optional[timedelta] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                lock_duration: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                requires_session: Optional[bool] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                user_metadata: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBSku(_Model):
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


    class azure.mgmt.servicebus.models.SBSubscription(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SBSubscriptionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SBSubscriptionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBSubscriptionProperties(_Model):
        accessed_at: Optional[datetime]
        auto_delete_on_idle: Optional[timedelta]
        client_affine_properties: Optional[SBClientAffineProperties]
        count_details: Optional[MessageCountDetails]
        created_at: Optional[datetime]
        dead_lettering_on_filter_evaluation_exceptions: Optional[bool]
        dead_lettering_on_message_expiration: Optional[bool]
        default_message_time_to_live: Optional[timedelta]
        duplicate_detection_history_time_window: Optional[timedelta]
        enable_batched_operations: Optional[bool]
        forward_dead_lettered_messages_to: Optional[str]
        forward_to: Optional[str]
        is_client_affine: Optional[bool]
        lock_duration: Optional[timedelta]
        max_delivery_count: Optional[int]
        message_count: Optional[int]
        requires_session: Optional[bool]
        status: Optional[Union[str, EntityStatus]]
        updated_at: Optional[datetime]
        user_metadata: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_delete_on_idle: Optional[timedelta] = ..., 
                client_affine_properties: Optional[SBClientAffineProperties] = ..., 
                dead_lettering_on_filter_evaluation_exceptions: Optional[bool] = ..., 
                dead_lettering_on_message_expiration: Optional[bool] = ..., 
                default_message_time_to_live: Optional[timedelta] = ..., 
                duplicate_detection_history_time_window: Optional[timedelta] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                forward_dead_lettered_messages_to: Optional[str] = ..., 
                forward_to: Optional[str] = ..., 
                is_client_affine: Optional[bool] = ..., 
                lock_duration: Optional[timedelta] = ..., 
                max_delivery_count: Optional[int] = ..., 
                requires_session: Optional[bool] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                user_metadata: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SBTopic(ProxyResource):
        id: str
        location: Optional[str]
        name: str
        properties: Optional[SBTopicProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SBTopicProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.servicebus.models.SBTopicProperties(_Model):
        accessed_at: Optional[datetime]
        auto_delete_on_idle: Optional[timedelta]
        count_details: Optional[MessageCountDetails]
        created_at: Optional[datetime]
        default_message_time_to_live: Optional[timedelta]
        duplicate_detection_history_time_window: Optional[timedelta]
        enable_batched_operations: Optional[bool]
        enable_express: Optional[bool]
        enable_partitioning: Optional[bool]
        max_message_size_in_kilobytes: Optional[int]
        max_size_in_megabytes: Optional[int]
        requires_duplicate_detection: Optional[bool]
        size_in_bytes: Optional[int]
        status: Optional[Union[str, EntityStatus]]
        subscription_count: Optional[int]
        support_ordering: Optional[bool]
        updated_at: Optional[datetime]
        user_metadata: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_delete_on_idle: Optional[timedelta] = ..., 
                default_message_time_to_live: Optional[timedelta] = ..., 
                duplicate_detection_history_time_window: Optional[timedelta] = ..., 
                enable_batched_operations: Optional[bool] = ..., 
                enable_express: Optional[bool] = ..., 
                enable_partitioning: Optional[bool] = ..., 
                max_message_size_in_kilobytes: Optional[int] = ..., 
                max_size_in_megabytes: Optional[int] = ..., 
                requires_duplicate_detection: Optional[bool] = ..., 
                status: Optional[Union[str, EntityStatus]] = ..., 
                support_ordering: Optional[bool] = ..., 
                user_metadata: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.servicebus.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.servicebus.models.SqlFilter(_Model):
        compatibility_level: Optional[int]
        requires_preprocessing: Optional[bool]
        sql_expression: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                compatibility_level: Optional[int] = ..., 
                requires_preprocessing: Optional[bool] = ..., 
                sql_expression: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.Subnet(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.servicebus.models.SystemData(_Model):
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


    class azure.mgmt.servicebus.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"
        ONE3 = "1.3"


    class azure.mgmt.servicebus.models.TrackedResource(Resource):
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


    class azure.mgmt.servicebus.models.UnavailableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_NAME = "InvalidName"
        NAME_IN_LOCKDOWN = "NameInLockdown"
        NAME_IN_USE = "NameInUse"
        NONE = "None"
        SUBSCRIPTION_IS_DISABLED = "SubscriptionIsDisabled"
        TOO_MANY_NAMESPACE_IN_CURRENT_SUBSCRIPTION = "TooManyNamespaceInCurrentSubscription"


    class azure.mgmt.servicebus.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.servicebus.models.UserAssignedIdentityProperties(_Model):
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.servicebus.operations

    class azure.mgmt.servicebus.operations.DisasterRecoveryConfigsOperations:

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
                parameters: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: CheckNameAvailability, 
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

        @overload
        def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[NamespaceFailoverProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[NamespaceFailoverProperties] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def fail_over(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
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
            ) -> SBAuthorizationRule: ...

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
            ) -> ItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                alias: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.servicebus.operations.MigrationConfigsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: MigrationConfigProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationConfigProperties]: ...

        @overload
        def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: MigrationConfigProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationConfigProperties]: ...

        @overload
        def begin_create_and_start_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationConfigProperties]: ...

        @distributed_trace
        def complete_migration(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> MigrationConfigProperties: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MigrationConfigProperties]: ...

        @distributed_trace
        def revert(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                config_name: Union[str, MigrationConfigurationName], 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicebus.operations.NamespacesOperations:

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
                parameters: SBNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SBNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: SBNamespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SBNamespace]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SBNamespace]: ...

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
                parameters: CheckNameAvailability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                parameters: CheckNameAvailability, 
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
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

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
            ) -> SBAuthorizationRule: ...

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
            ) -> SBNamespace: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def get_network_rule_set(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> NetworkRuleSet: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[SBNamespace]: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SBNamespace]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @distributed_trace
        def list_network_rule_sets(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NetworkRuleSet]: ...

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
                parameters: SBNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: SBNamespaceUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...


    class azure.mgmt.servicebus.operations.NetworkSecurityPerimeterConfigurationOperations:

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
            ) -> ItemPaged[NetworkSecurityPerimeterConfiguration]: ...


    class azure.mgmt.servicebus.operations.NetworkSecurityPerimeterConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get_resource_association_name(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> NetworkSecurityPerimeterConfiguration: ...

        @distributed_trace
        def reconcile(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource_association_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.servicebus.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.servicebus.operations.PrivateEndpointConnectionsOperations:

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


    class azure.mgmt.servicebus.operations.PrivateLinkResourcesOperations:

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


    class azure.mgmt.servicebus.operations.QueuesOperations:

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
                queue_name: str, 
                parameters: SBQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                parameters: SBQueue, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBQueue: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> SBQueue: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SBQueue]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                queue_name: str, 
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
                queue_name: str, 
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
                queue_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


    class azure.mgmt.servicebus.operations.RulesOperations:

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
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list_by_subscriptions(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Rule]: ...


    class azure.mgmt.servicebus.operations.SubscriptionsOperations:

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
                topic_name: str, 
                subscription_name: str, 
                parameters: SBSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                parameters: SBSubscription, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBSubscription: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                subscription_name: str, 
                **kwargs: Any
            ) -> SBSubscription: ...

        @distributed_trace
        def list_by_topic(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SBSubscription]: ...


    class azure.mgmt.servicebus.operations.TopicsOperations:

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
                topic_name: str, 
                parameters: SBTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                parameters: SBTopic, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBTopic: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: SBAuthorizationRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @overload
        def create_or_update_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> SBTopic: ...

        @distributed_trace
        def get_authorization_rule(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> SBAuthorizationRule: ...

        @distributed_trace
        def list_authorization_rules(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SBAuthorizationRule]: ...

        @distributed_trace
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                *, 
                skip: Optional[int] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SBTopic]: ...

        @distributed_trace
        def list_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
                authorization_rule_name: str, 
                **kwargs: Any
            ) -> AccessKeys: ...

        @overload
        def regenerate_keys(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                topic_name: str, 
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
                topic_name: str, 
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
                topic_name: str, 
                authorization_rule_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


namespace azure.mgmt.servicebus.types

    class azure.mgmt.servicebus.types.AccessKeys(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.Action(TypedDict, total=False):
        key "compatibilityLevel": int
        key "requiresPreprocessing": bool
        key "sqlExpression": str
        compatibility_level: int
        requires_preprocessing: bool
        sql_expression: str


    class azure.mgmt.servicebus.types.ArmDisasterRecovery(ProxyResource):
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


    class azure.mgmt.servicebus.types.ArmDisasterRecoveryProperties(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.CheckNameAvailability(TypedDict, total=False):
        key "name": Required[str]
        name: str


    class azure.mgmt.servicebus.types.CheckNameAvailabilityResult(TypedDict, total=False):
        key "message": str
        key "nameAvailable": bool
        key "reason": Union[str, UnavailableReason]
        message: str
        name_available: bool
        reason: Union[str, UnavailableReason]


    class azure.mgmt.servicebus.types.ConfidentialCompute(TypedDict, total=False):
        key "mode": Union[str, Mode]
        mode: Union[str, Mode]


    class azure.mgmt.servicebus.types.ConnectionState(TypedDict, total=False):
        key "description": str
        key "status": Union[str, PrivateLinkConnectionStatus]
        description: str
        status: Union[str, PrivateLinkConnectionStatus]


    class azure.mgmt.servicebus.types.CorrelationFilter(TypedDict, total=False):
        key "contentType": str
        key "correlationId": str
        key "label": str
        key "messageId": str
        key "replyTo": str
        key "replyToSessionId": str
        key "requiresPreprocessing": bool
        key "sessionId": str
        key "to": str
        content_type: str
        correlation_id: str
        label: str
        message_id: str
        properties: dict[str, str]
        reply_to: str
        reply_to_session_id: str
        requires_preprocessing: bool
        session_id: str
        to: str


    class azure.mgmt.servicebus.types.Encryption(TypedDict, total=False):
        key "keySource": Literal["KeyVault"]
        key "requireInfrastructureEncryption": bool
        keyVaultProperties: list[KeyVaultProperties]
        key_source: Literal[KeyVault]
        key_vault_properties: list[KeyVaultProperties]
        require_infrastructure_encryption: bool


    class azure.mgmt.servicebus.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.servicebus.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorResponseError', module='types')
        error: ErrorResponseError


    class azure.mgmt.servicebus.types.ErrorResponseError(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponse]
        message: str
        target: str


    class azure.mgmt.servicebus.types.FailOver(TypedDict, total=False):
        key "properties": ForwardRef('FailOverProperties', module='types')
        properties: FailOverProperties


    class azure.mgmt.servicebus.types.FailOverProperties(TypedDict, total=False):
        key "force": bool
        key "primaryLocation": str
        force: bool
        primary_location: str


    class azure.mgmt.servicebus.types.FailoverPropertiesProperties(TypedDict, total=False):
        key "IsSafeFailover": bool
        is_safe_failover: bool


    class azure.mgmt.servicebus.types.GeoDataReplicationProperties(TypedDict, total=False):
        key "maxReplicationLagDurationInSeconds": int
        locations: list[NamespaceReplicaLocation]
        max_replication_lag_duration_in_seconds: int


    class azure.mgmt.servicebus.types.Identity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Union[str, ManagedServiceIdentityType]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.servicebus.types.KeyVaultProperties(TypedDict, total=False):
        key "identity": ForwardRef('UserAssignedIdentityProperties', module='types')
        key "keyName": str
        key "keyVaultUri": str
        key "keyVersion": str
        identity: UserAssignedIdentityProperties
        key_name: str
        key_vault_uri: str
        key_version: str


    class azure.mgmt.servicebus.types.MessageCountDetails(TypedDict, total=False):
        key "activeMessageCount": int
        key "deadLetterMessageCount": int
        key "scheduledMessageCount": int
        key "transferDeadLetterMessageCount": int
        key "transferMessageCount": int
        active_message_count: int
        dead_letter_message_count: int
        scheduled_message_count: int
        transfer_dead_letter_message_count: int
        transfer_message_count: int


    class azure.mgmt.servicebus.types.MigrationConfigProperties(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('MigrationConfigPropertiesProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: MigrationConfigPropertiesProperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.MigrationConfigPropertiesProperties(TypedDict, total=False):
        key "migrationState": str
        key "pendingReplicationOperationsCount": int
        key "postMigrationName": Required[str]
        key "provisioningState": str
        key "targetNamespace": Required[str]
        migration_state: str
        pending_replication_operations_count: int
        post_migration_name: str
        provisioning_state: str
        target_namespace: str


    class azure.mgmt.servicebus.types.NWRuleSetIpRules(TypedDict, total=False):
        key "action": Union[str, NetworkRuleIPAction]
        key "ipMask": str
        action: Union[str, NetworkRuleIPAction]
        ip_mask: str


    class azure.mgmt.servicebus.types.NWRuleSetVirtualNetworkRules(TypedDict, total=False):
        key "ignoreMissingVnetServiceEndpoint": bool
        key "subnet": ForwardRef('Subnet', module='types')
        ignore_missing_vnet_service_endpoint: bool
        subnet: Subnet


    class azure.mgmt.servicebus.types.NamespaceFailoverProperties(TypedDict, total=False):
        key "properties": ForwardRef('FailoverPropertiesProperties', module='types')
        properties: FailoverPropertiesProperties


    class azure.mgmt.servicebus.types.NamespaceReplicaLocation(TypedDict, total=False):
        key "locationName": str
        key "roleType": Union[str, GeoDRRoleType]
        location_name: str
        role_type: Union[str, GeoDRRoleType]


    class azure.mgmt.servicebus.types.NetworkRuleSet(ProxyResource):
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


    class azure.mgmt.servicebus.types.NetworkRuleSetProperties(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.NetworkSecurityPerimeter(TypedDict, total=False):
        key "id": str
        key "location": str
        key "perimeterGuid": str
        id: str
        location: str
        perimeter_guid: str


    class azure.mgmt.servicebus.types.NetworkSecurityPerimeterConfiguration(ProxyResource):
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


    class azure.mgmt.servicebus.types.NetworkSecurityPerimeterConfigurationProperties(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.NetworkSecurityPerimeterConfigurationPropertiesProfile(TypedDict, total=False):
        key "accessRulesVersion": str
        key "name": str
        accessRules: list[NspAccessRule]
        access_rules: list[NspAccessRule]
        access_rules_version: str
        name: str


    class azure.mgmt.servicebus.types.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(TypedDict, total=False):
        key "accessMode": Union[str, ResourceAssociationAccessMode]
        key "name": str
        access_mode: Union[str, ResourceAssociationAccessMode]
        name: str


    class azure.mgmt.servicebus.types.NspAccessRule(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NspAccessRuleProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: NspAccessRuleProperties
        type: str


    class azure.mgmt.servicebus.types.NspAccessRuleProperties(TypedDict, total=False):
        key "direction": Union[str, NspAccessRuleDirection]
        addressPrefixes: list[str]
        address_prefixes: list[str]
        direction: Union[str, NspAccessRuleDirection]
        fullyQualifiedDomainNames: list[str]
        fully_qualified_domain_names: list[str]
        networkSecurityPerimeters: list[NetworkSecurityPerimeter]
        network_security_perimeters: list[NetworkSecurityPerimeter]
        subscriptions: list[NspAccessRulePropertiesSubscriptionsItem]


    class azure.mgmt.servicebus.types.NspAccessRulePropertiesSubscriptionsItem(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.servicebus.types.Operation(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.servicebus.types.PlatformCapabilities(TypedDict, total=False):
        key "confidentialCompute": ForwardRef('ConfidentialCompute', module='types')
        confidential_compute: ConfidentialCompute


    class azure.mgmt.servicebus.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.servicebus.types.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.servicebus.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": ForwardRef('ConnectionState', module='types')
        key "provisioningState": Union[str, EndPointProvisioningState]
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: ConnectionState
        provisioning_state: Union[str, EndPointProvisioningState]


    class azure.mgmt.servicebus.types.PrivateLinkResource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateLinkResourceProperties', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateLinkResourceProperties
        type: str


    class azure.mgmt.servicebus.types.PrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        group_id: str
        requiredMembers: list[str]
        requiredZoneNames: list[str]
        required_members: list[str]
        required_zone_names: list[str]


    class azure.mgmt.servicebus.types.PrivateLinkResourcesListResult(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[PrivateLinkResource]]
        next_link: str
        value: list[PrivateLinkResource]


    class azure.mgmt.servicebus.types.ProvisioningIssue(TypedDict, total=False):
        key "name": str
        key "properties": ForwardRef('ProvisioningIssueProperties', module='types')
        name: str
        properties: ProvisioningIssueProperties


    class azure.mgmt.servicebus.types.ProvisioningIssueProperties(TypedDict, total=False):
        key "description": str
        key "issueType": str
        description: str
        issue_type: str


    class azure.mgmt.servicebus.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.RegenerateAccessKeyParameters(TypedDict, total=False):
        key "key": str
        key "keyType": Required[Union[str, KeyType]]
        key: str
        key_type: Union[str, KeyType]


    class azure.mgmt.servicebus.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.ResourceNamespacePatch(Resource):
        key "id": str
        key "location": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicebus.types.Rule(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('Ruleproperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: Ruleproperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.Ruleproperties(TypedDict, total=False):
        key "action": ForwardRef('Action', module='types')
        key "correlationFilter": ForwardRef('CorrelationFilter', module='types')
        key "filterType": Union[str, FilterType]
        key "sqlFilter": ForwardRef('SqlFilter', module='types')
        action: Action
        correlation_filter: CorrelationFilter
        filter_type: Union[str, FilterType]
        sql_filter: SqlFilter


    class azure.mgmt.servicebus.types.SBAuthorizationRule(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SBAuthorizationRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SBAuthorizationRuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.SBAuthorizationRuleProperties(TypedDict, total=False):
        key "rights": Required[list[Union[str, AccessRights]]]
        rights: list[Union[str, AccessRights]]


    class azure.mgmt.servicebus.types.SBClientAffineProperties(TypedDict, total=False):
        key "clientId": str
        key "isDurable": bool
        key "isShared": bool
        client_id: str
        is_durable: bool
        is_shared: bool


    class azure.mgmt.servicebus.types.SBNamespace(TrackedResource):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SBNamespaceProperties', module='types')
        key "sku": ForwardRef('SBSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        location: str
        name: str
        properties: SBNamespaceProperties
        sku: SBSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicebus.types.SBNamespaceProperties(TypedDict, total=False):
        key "alternateName": str
        key "createdAt": str
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "geoDataReplication": ForwardRef('GeoDataReplicationProperties', module='types')
        key "ipAddressType": Union[str, IpAddressType]
        key "metricId": str
        key "minimumTlsVersion": Union[str, TlsVersion]
        key "platformCapabilities": ForwardRef('PlatformCapabilities', module='types')
        key "premiumMessagingPartitions": int
        key "provisioningState": str
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "serviceBusEndpoint": str
        key "status": str
        key "updatedAt": str
        key "zoneRedundant": bool
        alternate_name: str
        created_at: str
        disable_local_auth: bool
        encryption: Encryption
        geo_data_replication: GeoDataReplicationProperties
        ip_address_type: Union[str, IpAddressType]
        metric_id: str
        minimum_tls_version: Union[str, TlsVersion]
        platform_capabilities: PlatformCapabilities
        premium_messaging_partitions: int
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        service_bus_endpoint: str
        status: str
        updated_at: str
        zone_redundant: bool


    class azure.mgmt.servicebus.types.SBNamespaceUpdateParameters(ResourceNamespacePatch):
        key "id": str
        key "identity": ForwardRef('Identity', module='types')
        key "location": str
        key "name": str
        key "properties": ForwardRef('SBNamespaceUpdateProperties', module='types')
        key "sku": ForwardRef('SBSku', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: Identity
        location: str
        name: str
        properties: SBNamespaceUpdateProperties
        sku: SBSku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.servicebus.types.SBNamespaceUpdateProperties(TypedDict, total=False):
        key "alternateName": str
        key "createdAt": str
        key "disableLocalAuth": bool
        key "encryption": ForwardRef('Encryption', module='types')
        key "metricId": str
        key "provisioningState": str
        key "serviceBusEndpoint": str
        key "status": str
        key "updatedAt": str
        alternate_name: str
        created_at: str
        disable_local_auth: bool
        encryption: Encryption
        metric_id: str
        privateEndpointConnections: list[PrivateEndpointConnection]
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        service_bus_endpoint: str
        status: str
        updated_at: str


    class azure.mgmt.servicebus.types.SBQueue(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SBQueueProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SBQueueProperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.SBQueueProperties(TypedDict, total=False):
        key "accessedAt": str
        key "autoDeleteOnIdle": str
        key "countDetails": ForwardRef('MessageCountDetails', module='types')
        key "createdAt": str
        key "deadLetteringOnMessageExpiration": bool
        key "defaultMessageTimeToLive": str
        key "duplicateDetectionHistoryTimeWindow": str
        key "enableBatchedOperations": bool
        key "enableExpress": bool
        key "enablePartitioning": bool
        key "forwardDeadLetteredMessagesTo": str
        key "forwardTo": str
        key "lockDuration": str
        key "maxDeliveryCount": int
        key "maxMessageSizeInKilobytes": int
        key "maxSizeInMegabytes": int
        key "messageCount": int
        key "requiresDuplicateDetection": bool
        key "requiresSession": bool
        key "sizeInBytes": int
        key "status": Union[str, EntityStatus]
        key "updatedAt": str
        key "userMetadata": str
        accessed_at: str
        auto_delete_on_idle: str
        count_details: MessageCountDetails
        created_at: str
        dead_lettering_on_message_expiration: bool
        default_message_time_to_live: str
        duplicate_detection_history_time_window: str
        enable_batched_operations: bool
        enable_express: bool
        enable_partitioning: bool
        forward_dead_lettered_messages_to: str
        forward_to: str
        lock_duration: str
        max_delivery_count: int
        max_message_size_in_kilobytes: int
        max_size_in_megabytes: int
        message_count: int
        requires_duplicate_detection: bool
        requires_session: bool
        size_in_bytes: int
        status: Union[str, EntityStatus]
        updated_at: str
        user_metadata: str


    class azure.mgmt.servicebus.types.SBSku(TypedDict, total=False):
        key "capacity": int
        key "name": Required[Union[str, SkuName]]
        key "tier": Union[str, SkuTier]
        capacity: int
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]


    class azure.mgmt.servicebus.types.SBSubscription(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SBSubscriptionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SBSubscriptionProperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.SBSubscriptionProperties(TypedDict, total=False):
        key "accessedAt": str
        key "autoDeleteOnIdle": str
        key "clientAffineProperties": ForwardRef('SBClientAffineProperties', module='types')
        key "countDetails": ForwardRef('MessageCountDetails', module='types')
        key "createdAt": str
        key "deadLetteringOnFilterEvaluationExceptions": bool
        key "deadLetteringOnMessageExpiration": bool
        key "defaultMessageTimeToLive": str
        key "duplicateDetectionHistoryTimeWindow": str
        key "enableBatchedOperations": bool
        key "forwardDeadLetteredMessagesTo": str
        key "forwardTo": str
        key "isClientAffine": bool
        key "lockDuration": str
        key "maxDeliveryCount": int
        key "messageCount": int
        key "requiresSession": bool
        key "status": Union[str, EntityStatus]
        key "updatedAt": str
        key "userMetadata": str
        accessed_at: str
        auto_delete_on_idle: str
        client_affine_properties: SBClientAffineProperties
        count_details: MessageCountDetails
        created_at: str
        dead_lettering_on_filter_evaluation_exceptions: bool
        dead_lettering_on_message_expiration: bool
        default_message_time_to_live: str
        duplicate_detection_history_time_window: str
        enable_batched_operations: bool
        forward_dead_lettered_messages_to: str
        forward_to: str
        is_client_affine: bool
        lock_duration: str
        max_delivery_count: int
        message_count: int
        requires_session: bool
        status: Union[str, EntityStatus]
        updated_at: str
        user_metadata: str


    class azure.mgmt.servicebus.types.SBTopic(ProxyResource):
        key "id": str
        key "location": str
        key "name": str
        key "properties": ForwardRef('SBTopicProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: SBTopicProperties
        system_data: SystemData
        type: str


    class azure.mgmt.servicebus.types.SBTopicProperties(TypedDict, total=False):
        key "accessedAt": str
        key "autoDeleteOnIdle": str
        key "countDetails": ForwardRef('MessageCountDetails', module='types')
        key "createdAt": str
        key "defaultMessageTimeToLive": str
        key "duplicateDetectionHistoryTimeWindow": str
        key "enableBatchedOperations": bool
        key "enableExpress": bool
        key "enablePartitioning": bool
        key "maxMessageSizeInKilobytes": int
        key "maxSizeInMegabytes": int
        key "requiresDuplicateDetection": bool
        key "sizeInBytes": int
        key "status": Union[str, EntityStatus]
        key "subscriptionCount": int
        key "supportOrdering": bool
        key "updatedAt": str
        key "userMetadata": str
        accessed_at: str
        auto_delete_on_idle: str
        count_details: MessageCountDetails
        created_at: str
        default_message_time_to_live: str
        duplicate_detection_history_time_window: str
        enable_batched_operations: bool
        enable_express: bool
        enable_partitioning: bool
        max_message_size_in_kilobytes: int
        max_size_in_megabytes: int
        requires_duplicate_detection: bool
        size_in_bytes: int
        status: Union[str, EntityStatus]
        subscription_count: int
        support_ordering: bool
        updated_at: str
        user_metadata: str


    class azure.mgmt.servicebus.types.SqlFilter(TypedDict, total=False):
        key "compatibilityLevel": int
        key "requiresPreprocessing": bool
        key "sqlExpression": str
        compatibility_level: int
        requires_preprocessing: bool
        sql_expression: str


    class azure.mgmt.servicebus.types.Subnet(TypedDict, total=False):
        key "id": Required[str]
        id: str


    class azure.mgmt.servicebus.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.servicebus.types.TrackedResource(Resource):
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


    class azure.mgmt.servicebus.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.servicebus.types.UserAssignedIdentityProperties(TypedDict, total=False):
        key "userAssignedIdentity": str
        user_assigned_identity: str


```