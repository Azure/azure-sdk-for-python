```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


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
                polling_interval: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
            ) -> AsyncLROPoller[None]: ...


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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaGroup]: ...


namespace azure.mgmt.eventhub.models

    class azure.mgmt.eventhub.models.AccessKeys(Model):
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


    class azure.mgmt.eventhub.models.AccessRights(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LISTEN = "Listen"
        MANAGE = "Manage"
        SEND = "Send"


    class azure.mgmt.eventhub.models.ApplicationGroup(ProxyResource):
        client_app_group_identifier: str
        id: str
        is_enabled: bool
        location: str
        name: str
        policies: list[ApplicationGroupPolicy]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_app_group_identifier: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                policies: Optional[List[ApplicationGroupPolicy]] = ..., 
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


    class azure.mgmt.eventhub.models.ApplicationGroupListResult(Model):
        next_link: str
        value: list[ApplicationGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ApplicationGroup]] = ..., 
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


    class azure.mgmt.eventhub.models.ApplicationGroupPolicy(Model):
        name: str
        type: Union[str, ApplicationGroupPolicyType]

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


    class azure.mgmt.eventhub.models.ApplicationGroupPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        THROTTLING_POLICY = "ThrottlingPolicy"


    class azure.mgmt.eventhub.models.ArmDisasterRecovery(ProxyResource):
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


    class azure.mgmt.eventhub.models.ArmDisasterRecoveryListResult(Model):
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


    class azure.mgmt.eventhub.models.AuthorizationRule(ProxyResource):
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


    class azure.mgmt.eventhub.models.AuthorizationRuleListResult(Model):
        next_link: str
        value: list[AuthorizationRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AuthorizationRule]] = ..., 
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


    class azure.mgmt.eventhub.models.AvailableCluster(Model):
        location: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.AvailableClustersList(Model):
        value: list[AvailableCluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AvailableCluster]] = ..., 
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


    class azure.mgmt.eventhub.models.CaptureDescription(Model):
        destination: Destination
        enabled: bool
        encoding: Union[str, EncodingCaptureDescription]
        interval_in_seconds: int
        size_limit_in_bytes: int
        skip_empty_archives: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination: Optional[Destination] = ..., 
                enabled: Optional[bool] = ..., 
                encoding: Optional[Union[str, EncodingCaptureDescription]] = ..., 
                interval_in_seconds: Optional[int] = ..., 
                size_limit_in_bytes: Optional[int] = ..., 
                skip_empty_archives: Optional[bool] = ..., 
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


    class azure.mgmt.eventhub.models.CheckNameAvailabilityParameter(Model):
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


    class azure.mgmt.eventhub.models.CheckNameAvailabilityResult(Model):
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


    class azure.mgmt.eventhub.models.Cluster(TrackedResource):
        created_at: str
        id: str
        location: str
        metric_id: str
        name: str
        sku: ClusterSku
        status: str
        supports_scaling: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str
        updated_at: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                sku: Optional[ClusterSku] = ..., 
                supports_scaling: Optional[bool] = ..., 
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


    class azure.mgmt.eventhub.models.ClusterListResult(Model):
        next_link: str
        value: list[Cluster]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Cluster]] = ..., 
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


    class azure.mgmt.eventhub.models.ClusterQuotaConfigurationProperties(Model):
        settings: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                settings: Optional[Dict[str, str]] = ..., 
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


    class azure.mgmt.eventhub.models.ClusterSku(Model):
        capacity: int
        name: Union[str, ClusterSkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                name: Union[str, ClusterSkuName], 
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


    class azure.mgmt.eventhub.models.ClusterSkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"


    class azure.mgmt.eventhub.models.ConnectionState(Model):
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


    class azure.mgmt.eventhub.models.ConsumerGroup(ProxyResource):
        created_at: datetime
        id: str
        location: str
        name: str
        system_data: SystemData
        type: str
        updated_at: datetime
        user_metadata: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                user_metadata: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.ConsumerGroupListResult(Model):
        next_link: str
        value: list[ConsumerGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ConsumerGroup]] = ..., 
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


    class azure.mgmt.eventhub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.eventhub.models.DefaultAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY = "Deny"


    class azure.mgmt.eventhub.models.Destination(Model):
        archive_name_format: str
        blob_container: str
        data_lake_account_name: str
        data_lake_folder_path: str
        data_lake_subscription_id: str
        name: str
        storage_account_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                archive_name_format: Optional[str] = ..., 
                blob_container: Optional[str] = ..., 
                data_lake_account_name: Optional[str] = ..., 
                data_lake_folder_path: Optional[str] = ..., 
                data_lake_subscription_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.EHNamespace(TrackedResource):
        alternate_name: str
        cluster_arm_id: str
        created_at: datetime
        disable_local_auth: bool
        encryption: Encryption
        id: str
        identity: Identity
        is_auto_inflate_enabled: bool
        kafka_enabled: bool
        location: str
        maximum_throughput_units: int
        metric_id: str
        minimum_tls_version: Union[str, TlsVersion]
        name: str
        private_endpoint_connections: list[PrivateEndpointConnection]
        provisioning_state: str
        public_network_access: Union[str, PublicNetworkAccess]
        service_bus_endpoint: str
        sku: Sku
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
                cluster_arm_id: Optional[str] = ..., 
                disable_local_auth: Optional[bool] = ..., 
                encryption: Optional[Encryption] = ..., 
                identity: Optional[Identity] = ..., 
                is_auto_inflate_enabled: Optional[bool] = ..., 
                kafka_enabled: Optional[bool] = ..., 
                location: Optional[str] = ..., 
                maximum_throughput_units: Optional[int] = ..., 
                minimum_tls_version: Optional[Union[str, TlsVersion]] = ..., 
                private_endpoint_connections: Optional[List[PrivateEndpointConnection]] = ..., 
                public_network_access: Union[str, PublicNetworkAccess] = "Enabled", 
                sku: Optional[Sku] = ..., 
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


    class azure.mgmt.eventhub.models.EHNamespaceIdContainer(Model):
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


    class azure.mgmt.eventhub.models.EHNamespaceIdListResult(Model):
        value: list[EHNamespaceIdContainer]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[EHNamespaceIdContainer]] = ..., 
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


    class azure.mgmt.eventhub.models.EHNamespaceListResult(Model):
        next_link: str
        value: list[EHNamespace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[EHNamespace]] = ..., 
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


    class azure.mgmt.eventhub.models.EncodingCaptureDescription(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        AVRO_DEFLATE = "AvroDeflate"


    class azure.mgmt.eventhub.models.Encryption(Model):
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


    class azure.mgmt.eventhub.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.eventhub.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
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


    class azure.mgmt.eventhub.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
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


    class azure.mgmt.eventhub.models.EventHubListResult(Model):
        next_link: str
        value: list[Eventhub]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Eventhub]] = ..., 
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


    class azure.mgmt.eventhub.models.Eventhub(ProxyResource):
        capture_description: CaptureDescription
        created_at: datetime
        id: str
        location: str
        message_retention_in_days: int
        name: str
        partition_count: int
        partition_ids: list[str]
        status: Union[str, EntityStatus]
        system_data: SystemData
        type: str
        updated_at: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capture_description: Optional[CaptureDescription] = ..., 
                message_retention_in_days: Optional[int] = ..., 
                partition_count: Optional[int] = ..., 
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


    class azure.mgmt.eventhub.models.Identity(Model):
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


    class azure.mgmt.eventhub.models.KeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY_KEY = "PrimaryKey"
        SECONDARY_KEY = "SecondaryKey"


    class azure.mgmt.eventhub.models.KeyVaultProperties(Model):
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


    class azure.mgmt.eventhub.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.eventhub.models.MetricId(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INCOMING_BYTES = "IncomingBytes"
        INCOMING_MESSAGES = "IncomingMessages"
        OUTGOING_BYTES = "OutgoingBytes"
        OUTGOING_MESSAGES = "OutgoingMessages"


    class azure.mgmt.eventhub.models.NWRuleSetIpRules(Model):
        action: Union[str, NetworkRuleIPAction]
        ip_mask: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, NetworkRuleIPAction]] = ..., 
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


    class azure.mgmt.eventhub.models.NWRuleSetVirtualNetworkRules(Model):
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


    class azure.mgmt.eventhub.models.NetworkRuleIPAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.eventhub.models.NetworkRuleSet(ProxyResource):
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


    class azure.mgmt.eventhub.models.NetworkRuleSetListResult(Model):
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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeter(Model):
        id: str
        location: str
        perimeter_guid: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                perimeter_guid: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfiguration(TrackedResource):
        id: str
        location: str
        name: str
        network_security_perimeter: NetworkSecurityPerimeter
        profile: NetworkSecurityPerimeterConfigurationPropertiesProfile
        provisioning_issues: list[ProvisioningIssue]
        provisioning_state: Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]
        resource_association: NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                provisioning_issues: Optional[List[ProvisioningIssue]] = ..., 
                provisioning_state: Optional[Union[str, NetworkSecurityPerimeterConfigurationProvisioningState]] = ..., 
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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationList(Model):
        value: list[NetworkSecurityPerimeterConfiguration]

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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationPropertiesProfile(Model):
        access_rules: list[NspAccessRule]
        access_rules_version: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_rules: Optional[List[NspAccessRule]] = ..., 
                access_rules_version: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.NetworkSecurityPerimeterConfigurationPropertiesResourceAssociation(Model):
        access_mode: Union[str, ResourceAssociationAccessMode]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                access_mode: Optional[Union[str, ResourceAssociationAccessMode]] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.NspAccessRule(Model):
        id: str
        name: str
        properties: NspAccessRuleProperties
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.NspAccessRuleDirection(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INBOUND = "Inbound"
        OUTBOUND = "Outbound"


    class azure.mgmt.eventhub.models.NspAccessRuleProperties(Model):
        address_prefixes: list[str]
        direction: Union[str, NspAccessRuleDirection]
        fully_qualified_domain_names: list[str]
        network_security_perimeters: list[NetworkSecurityPerimeter]
        subscriptions: list[NspAccessRulePropertiesSubscriptionsItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_prefixes: Optional[List[str]] = ..., 
                direction: Optional[Union[str, NspAccessRuleDirection]] = ..., 
                subscriptions: Optional[List[NspAccessRulePropertiesSubscriptionsItem]] = ..., 
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


    class azure.mgmt.eventhub.models.NspAccessRulePropertiesSubscriptionsItem(Model):
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


    class azure.mgmt.eventhub.models.Operation(Model):
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


    class azure.mgmt.eventhub.models.OperationDisplay(Model):
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


    class azure.mgmt.eventhub.models.OperationListResult(Model):
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


    class azure.mgmt.eventhub.models.PrivateEndpoint(Model):
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


    class azure.mgmt.eventhub.models.PrivateEndpointConnection(ProxyResource):
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


    class azure.mgmt.eventhub.models.PrivateEndpointConnectionListResult(Model):
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


    class azure.mgmt.eventhub.models.PrivateLinkConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.eventhub.models.PrivateLinkResource(Model):
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


    class azure.mgmt.eventhub.models.PrivateLinkResourcesListResult(Model):
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


    class azure.mgmt.eventhub.models.ProvisioningIssue(Model):
        name: str
        properties: ProvisioningIssueProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.ProvisioningIssueProperties(Model):
        description: str
        issue_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                issue_type: Optional[str] = ..., 
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


    class azure.mgmt.eventhub.models.ProvisioningStateDR(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.eventhub.models.ProxyResource(Model):
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


    class azure.mgmt.eventhub.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventhub.models.PublicNetworkAccessFlag(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        SECURED_BY_PERIMETER = "SecuredByPerimeter"


    class azure.mgmt.eventhub.models.RegenerateAccessKeyParameters(Model):
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


    class azure.mgmt.eventhub.models.Resource(Model):
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


    class azure.mgmt.eventhub.models.ResourceAssociationAccessMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT_MODE = "AuditMode"
        ENFORCED_MODE = "EnforcedMode"
        LEARNING_MODE = "LearningMode"
        NO_ASSOCIATION_MODE = "NoAssociationMode"
        UNSPECIFIED_MODE = "UnspecifiedMode"


    class azure.mgmt.eventhub.models.RoleDisasterRecovery(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIMARY = "Primary"
        PRIMARY_NOT_REPLICATING = "PrimaryNotReplicating"
        SECONDARY = "Secondary"


    class azure.mgmt.eventhub.models.SchemaCompatibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKWARD = "Backward"
        FORWARD = "Forward"
        NONE = "None"


    class azure.mgmt.eventhub.models.SchemaGroup(ProxyResource):
        created_at_utc: datetime
        e_tag: str
        group_properties: dict[str, str]
        id: str
        location: str
        name: str
        schema_compatibility: Union[str, SchemaCompatibility]
        schema_type: Union[str, SchemaType]
        system_data: SystemData
        type: str
        updated_at_utc: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_properties: Optional[Dict[str, str]] = ..., 
                schema_compatibility: Optional[Union[str, SchemaCompatibility]] = ..., 
                schema_type: Optional[Union[str, SchemaType]] = ..., 
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


    class azure.mgmt.eventhub.models.SchemaGroupListResult(Model):
        next_link: str
        value: list[SchemaGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[SchemaGroup]] = ..., 
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


    class azure.mgmt.eventhub.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVRO = "Avro"
        UNKNOWN = "Unknown"


    class azure.mgmt.eventhub.models.Sku(Model):
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


    class azure.mgmt.eventhub.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.eventhub.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.eventhub.models.Subnet(Model):
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


    class azure.mgmt.eventhub.models.SystemData(Model):
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


    class azure.mgmt.eventhub.models.ThrottlingPolicy(ApplicationGroupPolicy):
        metric_id: Union[str, MetricId]
        name: str
        rate_limit_threshold: int
        type: Union[str, ApplicationGroupPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric_id: Union[str, MetricId], 
                name: str, 
                rate_limit_threshold: int, 
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


    class azure.mgmt.eventhub.models.TlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ONE0 = "1.0"
        ONE1 = "1.1"
        ONE2 = "1.2"


    class azure.mgmt.eventhub.models.TrackedResource(Resource):
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


    class azure.mgmt.eventhub.models.UnavailableReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID_NAME = "InvalidName"
        NAME_IN_LOCKDOWN = "NameInLockdown"
        NAME_IN_USE = "NameInUse"
        NONE = "None"
        SUBSCRIPTION_IS_DISABLED = "SubscriptionIsDisabled"
        TOO_MANY_NAMESPACE_IN_CURRENT_SUBSCRIPTION = "TooManyNamespaceInCurrentSubscription"


    class azure.mgmt.eventhub.models.UserAssignedIdentity(Model):
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


    class azure.mgmt.eventhub.models.UserAssignedIdentityProperties(Model):
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
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
            ) -> LROPoller[None]: ...


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
                skip: Optional[int] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[SchemaGroup]: ...


```