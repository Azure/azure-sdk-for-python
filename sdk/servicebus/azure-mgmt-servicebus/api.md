```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.servicebus

    class azure.mgmt.servicebus.ServiceBusManagementClient: implements ContextManager 
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        migration_configs: MigrationConfigsOperations
        namespaces: NamespacesOperations
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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.servicebus.aio

    class azure.mgmt.servicebus.aio.ServiceBusManagementClient: implements AsyncContextManager 
        disaster_recovery_configs: DisasterRecoveryConfigsOperations
        migration_configs: MigrationConfigsOperations
        namespaces: NamespacesOperations
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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                parameters: Optional[FailoverProperties] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...


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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


namespace azure.mgmt.servicebus.models

    class azure.mgmt.servicebus.models.AccessKeys(Model):
        alias_primary_connection_string: str
        alias_secondary_connection_string: str
        key_name: str
        primary_connection_string: str
        primary_key: str
        secondary_connection_string: str
        secondary_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.servicebus.models.Action(Model):
        compatibility_level: int
        requires_preprocessing: bool
        sql_expression: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compatibility_level: Optional[int] = ..., 
                requires_preprocessing: bool = True, 
                sql_expression: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ArmDisasterRecovery(ProxyResource):
        alternate_name: str
        id: str
        location: str
        name: str
        partner_namespace: str
        pending_replication_operations_count: int
        provisioning_state: Union[str, ProvisioningStateDR]
        role: Union[str, RoleDisasterRecovery]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                partner_namespace: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ArmDisasterRecoveryListResult(Model):
        next_link: str
        value: list[ArmDisasterRecovery]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ArmDisasterRecovery]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.CheckNameAvailability(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.CheckNameAvailabilityResult(Model):
        message: str
        name_available: bool
        reason: Union[str, UnavailableReason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, UnavailableReason]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ConnectionState(Model):
        description: str
        status: Union[str, PrivateLinkConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateLinkConnectionStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.CorrelationFilter(Model):
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

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_type: Optional[str] = ..., 
                correlation_id: Optional[str] = ..., 
                label: Optional[str] = ..., 
                message_id: Optional[str] = ..., 
                properties: Optional[Dict[str, str]] = ..., 
                reply_to: Optional[str] = ..., 
                reply_to_session_id: Optional[str] = ..., 
                requires_preprocessing: bool = True, 
                session_id: Optional[str] = ..., 
                to: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.servicebus.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.servicebus.models.Encryption(Model):
        key_source: str
        key_vault_properties: list[KeyVaultProperties]
        require_infrastructure_encryption: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_source: Literal["KeyVault"] = "Microsoft.KeyVault", 
                key_vault_properties: Optional[List[KeyVaultProperties]] = ..., 
                require_infrastructure_encryption: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.servicebus.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ErrorResponse(Model):
        error: ErrorResponseError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorResponseError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ErrorResponseError(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorResponse]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.FailoverProperties(Model):
        is_safe_failover: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_safe_failover: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.FilterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CORRELATION_FILTER = "CorrelationFilter"
        SQL_FILTER = "SqlFilter"


    class azure.mgmt.servicebus.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.servicebus.models.KeyVaultProperties(Model):
        identity: UserAssignedIdentityProperties
        key_name: str
        key_vault_uri: str
        key_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[UserAssignedIdentityProperties] = ..., 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.servicebus.models.MessageCountDetails(Model):
        active_message_count: int
        dead_letter_message_count: int
        scheduled_message_count: int
        transfer_dead_letter_message_count: int
        transfer_message_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.MigrationConfigListResult(Model):
        next_link: str
        value: list[MigrationConfigProperties]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[MigrationConfigProperties]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.MigrationConfigProperties(ProxyResource):
        id: str
        location: str
        migration_state: str
        name: str
        pending_replication_operations_count: int
        post_migration_name: str
        provisioning_state: str
        system_data: SystemData
        target_namespace: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                post_migration_name: Optional[str] = ..., 
                target_namespace: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.MigrationConfigurationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):


    class azure.mgmt.servicebus.models.NWRuleSetIpRules(Model):
        action: Union[str, NetworkRuleIPAction]
        ip_mask: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, NetworkRuleIPAction] = "Allow", 
                ip_mask: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.NWRuleSetVirtualNetworkRules(Model):
        ignore_missing_vnet_service_endpoint: bool
        subnet: Subnet

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ignore_missing_vnet_service_endpoint: Optional[bool] = ..., 
                subnet: Optional[Subnet] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.NetworkRuleIPAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.servicebus.models.NetworkRuleSet(ProxyResource):
        default_action: Union[str, DefaultAction]
        id: str
        ip_rules: list[NWRuleSetIpRules]
        location: str
        name: str
        public_network_access: Union[str, PublicNetworkAccessFlag]
        system_data: SystemData
        trusted_service_access_enabled: bool
        type: str
        virtual_network_rules: list[NWRuleSetVirtualNetworkRules]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_action: Optional[Union[str, DefaultAction]] = ..., 
                ip_rules: Optional[List[NWRuleSetIpRules]] = ..., 
                public_network_access: Union[str, PublicNetworkAccessFlag] = "Enabled", 
                trusted_service_access_enabled: Optional[bool] = ..., 
                virtual_network_rules: Optional[List[NWRuleSetVirtualNetworkRules]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.NetworkRuleSetListResult(Model):
        next_link: str
        value: list[NetworkRuleSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[NetworkRuleSet]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        properties: JSON

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                origin: Optional[str] = ..., 
                properties: Optional[JSON] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.OperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.OperationListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PrivateEndpoint(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PrivateEndpointConnection(ProxyResource):
        id: str
        location: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: ConnectionState
        provisioning_state: Union[str, EndPointProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[ConnectionState] = ..., 
                provisioning_state: Optional[Union[str, EndPointProvisioningState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PrivateEndpointConnectionListResult(Model):
        next_link: str
        value: list[PrivateEndpointConnection]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateEndpointConnection]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.servicebus.models.PrivateLinkResource(Model):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                required_members: Optional[List[str]] = ..., 
                required_zone_names: Optional[List[str]] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PrivateLinkResourcesListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[PrivateLinkResource]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ProvisioningStateDR(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.servicebus.models.ProxyResource(Model):
        id: str
        location: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.servicebus.models.PublicNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.servicebus.models.RegenerateAccessKeyParameters(Model):
        key: str
        key_type: Union[str, KeyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                key_type: Union[str, KeyType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.Resource(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.ResourceNamespacePatch(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.RoleDisasterRecovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_NOT_REPLICATING = "PrimaryNotReplicating"
        SECONDARY = "Secondary"


    class azure.mgmt.servicebus.models.Rule(ProxyResource):
        action: Action
        correlation_filter: CorrelationFilter
        filter_type: Union[str, FilterType]
        id: str
        location: str
        name: str
        sql_filter: SqlFilter
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Action] = ..., 
                correlation_filter: Optional[CorrelationFilter] = ..., 
                filter_type: Optional[Union[str, FilterType]] = ..., 
                sql_filter: Optional[SqlFilter] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.RuleListResult(Model):
        next_link: str
        value: list[Rule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Rule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBAuthorizationRule(ProxyResource):
        id: str
        location: str
        name: str
        rights: Union[list[str, AccessRights]]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rights: Optional[List[Union[str, AccessRights]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBAuthorizationRuleListResult(Model):
        next_link: str
        value: list[SBAuthorizationRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SBAuthorizationRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBClientAffineProperties(Model):
        client_id: str
        is_durable: bool
        is_shared: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                is_durable: Optional[bool] = ..., 
                is_shared: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBNamespace(TrackedResource):
        alternate_name: str
        created_at: datetime
        disable_local_auth: bool
        encryption: Encryption
        id: str
        identity: Identity
        location: str
        metric_id: str
        minimum_tls_version: Union[str, TlsVersion]
        name: str
        premium_messaging_partitions: int
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        service_bus_endpoint: str
        sku: SBSku
        status: str
        system_data: SystemData
        tags: dict[str, str]
        type: str
        updated_at: datetime
        zone_redundant: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                identity: Optional[Identity] = ..., 
                location: str, 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                premium_messaging_partitions: Optional[int] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                sku: Optional[SBSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                zone_redundant: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBNamespaceListResult(Model):
        next_link: str
        value: list[SBNamespace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SBNamespace]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBNamespaceUpdateParameters(ResourceNamespacePatch):
        alternate_name: str
        created_at: datetime
        disable_local_auth: bool
        encryption: Encryption
        id: str
        identity: Identity
        location: str
        metric_id: str
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        service_bus_endpoint: str
        sku: SBSku
        status: str
        tags: dict[str, str]
        type: str
        updated_at: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                alternate_name: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                identity: Optional[Identity] = ..., 
                location: Optional[str] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                sku: Optional[SBSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBQueue(ProxyResource):
        accessed_at: datetime
        auto_delete_on_idle: timedelta
        count_details: MessageCountDetails
        created_at: datetime
        dead_lettering_on_message_expiration: bool
        default_message_time_to_live: timedelta
        duplicate_detection_history_time_window: timedelta
        enable_batched_operations: bool
        enable_express: bool
        enable_partitioning: bool
        forward_dead_lettered_messages_to: str
        forward_to: str
        id: str
        location: str
        lock_duration: timedelta
        max_delivery_count: int
        max_message_size_in_kilobytes: int
        max_size_in_megabytes: int
        message_count: int
        name: str
        requires_duplicate_detection: bool
        requires_session: bool
        size_in_bytes: int
        status: Union[str, EntityStatus]
        system_data: SystemData
        type: str
        updated_at: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBQueueListResult(Model):
        next_link: str
        value: list[SBQueue]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SBQueue]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBSku(Model):
        capacity: int
        name: Union[str, SkuName]
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, SkuName], 
                tier: Optional[Union[str, SkuTier]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBSubscription(ProxyResource):
        accessed_at: datetime
        auto_delete_on_idle: timedelta
        client_affine_properties: SBClientAffineProperties
        count_details: MessageCountDetails
        created_at: datetime
        dead_lettering_on_filter_evaluation_exceptions: bool
        dead_lettering_on_message_expiration: bool
        default_message_time_to_live: timedelta
        duplicate_detection_history_time_window: timedelta
        enable_batched_operations: bool
        forward_dead_lettered_messages_to: str
        forward_to: str
        id: str
        is_client_affine: bool
        location: str
        lock_duration: timedelta
        max_delivery_count: int
        message_count: int
        name: str
        requires_session: bool
        status: Union[str, EntityStatus]
        system_data: SystemData
        type: str
        updated_at: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBSubscriptionListResult(Model):
        next_link: str
        value: list[SBSubscription]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SBSubscription]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBTopic(ProxyResource):
        accessed_at: datetime
        auto_delete_on_idle: timedelta
        count_details: MessageCountDetails
        created_at: datetime
        default_message_time_to_live: timedelta
        duplicate_detection_history_time_window: timedelta
        enable_batched_operations: bool
        enable_express: bool
        enable_partitioning: bool
        id: str
        location: str
        max_message_size_in_kilobytes: int
        max_size_in_megabytes: int
        name: str
        requires_duplicate_detection: bool
        size_in_bytes: int
        status: Union[str, EntityStatus]
        subscription_count: int
        support_ordering: bool
        system_data: SystemData
        type: str
        updated_at: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SBTopicListResult(Model):
        next_link: str
        value: list[SBTopic]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SBTopic]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.servicebus.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.servicebus.models.SqlFilter(Model):
        compatibility_level: int
        requires_preprocessing: bool
        sql_expression: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compatibility_level: Optional[int] = ..., 
                requires_preprocessing: bool = True, 
                sql_expression: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SqlRuleAction(Action):
        compatibility_level: int
        requires_preprocessing: bool
        sql_expression: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compatibility_level: Optional[int] = ..., 
                requires_preprocessing: bool = True, 
                sql_expression: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.Subnet(Model):
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"


    class azure.mgmt.servicebus.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.UnavailableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_NAME = "InvalidName"
        NAME_IN_LOCKDOWN = "NameInLockdown"
        NAME_IN_USE = "NameInUse"
        NONE = "None"
        SUBSCRIPTION_IS_DISABLED = "SubscriptionIsDisabled"
        TOO_MANY_NAMESPACE_IN_CURRENT_SUBSCRIPTION = "TooManyNamespaceInCurrentSubscription"


    class azure.mgmt.servicebus.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.servicebus.models.UserAssignedIdentityProperties(Model):
        user_assigned_identity: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_assigned_identity: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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
                parameters: Optional[FailoverProperties] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Optional[SBNamespace]: ...


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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AccessKeys: ...


```