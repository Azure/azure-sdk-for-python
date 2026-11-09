```py
namespace azure.mgmt.horizondb

    class azure.mgmt.horizondb.HorizonDBMgmtClient: implements ContextManager 
        authentications: AuthenticationsOperations
        capabilities: CapabilitiesOperations
        change_data_capture_capabilities: ChangeDataCaptureCapabilitiesOperations
        change_data_capture_configurations: ChangeDataCaptureConfigurationsOperations
        change_data_capture_destinations: ChangeDataCaptureDestinationsOperations
        clusters: ClustersOperations
        default_parameter_groups: DefaultParameterGroupsOperations
        endpoints: EndpointsOperations
        firewall_rules: FirewallRulesOperations
        identity_assignments: IdentityAssignmentsOperations
        log_capture_configurations: LogCaptureConfigurationsOperations
        log_files: LogFilesOperations
        maintenance_events: MaintenanceEventsOperations
        microsoft_entra_administrators: MicrosoftEntraAdministratorsOperations
        microsoft_entra_authentications: MicrosoftEntraAuthenticationsOperations
        nodes: NodesOperations
        operations: Operations
        parameter_groups: ParameterGroupsOperations
        password_authentications: PasswordAuthenticationsOperations
        pools: PoolsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.horizondb.aio

    class azure.mgmt.horizondb.aio.HorizonDBMgmtClient: implements AsyncContextManager 
        authentications: AuthenticationsOperations
        capabilities: CapabilitiesOperations
        change_data_capture_capabilities: ChangeDataCaptureCapabilitiesOperations
        change_data_capture_configurations: ChangeDataCaptureConfigurationsOperations
        change_data_capture_destinations: ChangeDataCaptureDestinationsOperations
        clusters: ClustersOperations
        default_parameter_groups: DefaultParameterGroupsOperations
        endpoints: EndpointsOperations
        firewall_rules: FirewallRulesOperations
        identity_assignments: IdentityAssignmentsOperations
        log_capture_configurations: LogCaptureConfigurationsOperations
        log_files: LogFilesOperations
        maintenance_events: MaintenanceEventsOperations
        microsoft_entra_administrators: MicrosoftEntraAdministratorsOperations
        microsoft_entra_authentications: MicrosoftEntraAuthenticationsOperations
        nodes: NodesOperations
        operations: Operations
        parameter_groups: ParameterGroupsOperations
        password_authentications: PasswordAuthenticationsOperations
        pools: PoolsOperations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.horizondb.aio.operations

    class azure.mgmt.horizondb.aio.operations.AuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Authentication]: ...


    class azure.mgmt.horizondb.aio.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Capability]: ...


    class azure.mgmt.horizondb.aio.operations.ChangeDataCaptureCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: ChangeDataCaptureCapability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: ChangeDataCaptureCapability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

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
                properties: ChangeDataCaptureCapabilityForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ChangeDataCaptureCapabilityForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureCapability]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureCapability: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ChangeDataCaptureCapability]: ...


    class azure.mgmt.horizondb.aio.operations.ChangeDataCaptureConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: ChangeDataCaptureConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: ChangeDataCaptureConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: ChangeDataCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: ChangeDataCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ChangeDataCaptureConfiguration]: ...


    class azure.mgmt.horizondb.aio.operations.ChangeDataCaptureDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: ActivateChangeDataCaptureIdentityRequest, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        async def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: ActivateChangeDataCaptureIdentityRequest, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        async def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> AsyncLROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: ChangeDataCaptureDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: ChangeDataCaptureDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: ChangeDataCaptureDestinationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: ChangeDataCaptureDestinationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ChangeDataCaptureDestination]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureDestination: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ChangeDataCaptureDestination]: ...


    class azure.mgmt.horizondb.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
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

        @distributed_trace_async
        async def begin_failover(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
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

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Cluster]: ...


    class azure.mgmt.horizondb.aio.operations.DefaultParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> DefaultParameterGroup: ...

        @distributed_trace
        def list_by_subscription_and_region(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DefaultParameterGroup]: ...


    class azure.mgmt.horizondb.aio.operations.EndpointsOperations:

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
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Endpoint]: ...


    class azure.mgmt.horizondb.aio.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallRule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallRule]: ...


    class azure.mgmt.horizondb.aio.operations.IdentityAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IdentityAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityAssignment]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IdentityAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityAssignment]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IdentityAssignment]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                **kwargs: Any
            ) -> IdentityAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IdentityAssignment]: ...


    class azure.mgmt.horizondb.aio.operations.LogCaptureConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: LogCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogCaptureConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: LogCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogCaptureConfiguration]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LogCaptureConfiguration]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                **kwargs: Any
            ) -> LogCaptureConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogCaptureConfiguration]: ...


    class azure.mgmt.horizondb.aio.operations.LogFilesOperations:

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
                log_file_name: str, 
                **kwargs: Any
            ) -> LogFile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LogFile]: ...

        @distributed_trace_async
        async def list_download_urls(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_file_name: str, 
                **kwargs: Any
            ) -> LogFileDownloadUrl: ...


    class azure.mgmt.horizondb.aio.operations.MaintenanceEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_apply_now(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceEventActionResponse]: ...

        @overload
        async def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: MaintenanceEventRescheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceEventActionResponse]: ...

        @overload
        async def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: MaintenanceEventRescheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceEventActionResponse]: ...

        @overload
        async def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MaintenanceEventActionResponse]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                **kwargs: Any
            ) -> MaintenanceEvent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[MaintenanceEvent]: ...


    class azure.mgmt.horizondb.aio.operations.MicrosoftEntraAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: MicrosoftEntraAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAdministrator]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: MicrosoftEntraAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAdministrator]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAdministrator]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> MicrosoftEntraAdministrator: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MicrosoftEntraAdministrator]: ...


    class azure.mgmt.horizondb.aio.operations.MicrosoftEntraAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: MicrosoftEntraAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: MicrosoftEntraAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: MicrosoftEntraAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: MicrosoftEntraAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MicrosoftEntraAuthentication]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> MicrosoftEntraAuthentication: ...


    class azure.mgmt.horizondb.aio.operations.NodesOperations:

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
                pool_name: str, 
                node_name: str, 
                **kwargs: Any
            ) -> Node: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Node]: ...


    class azure.mgmt.horizondb.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.horizondb.aio.operations.ParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: ParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: ParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: ParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: ParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ParameterGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> ParameterGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ParameterGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ParameterGroup]: ...

        @distributed_trace
        def list_connections(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ParameterGroupConnectionProperties]: ...


    class azure.mgmt.horizondb.aio.operations.PasswordAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: PasswordAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: PasswordAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: PasswordAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: PasswordAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PasswordAuthentication]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> PasswordAuthentication: ...


    class azure.mgmt.horizondb.aio.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: PoolForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: PoolForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Pool]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Pool]: ...


    class azure.mgmt.horizondb.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        async def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.horizondb.aio.operations.PrivateLinkResourcesOperations:

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
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.horizondb.models

    class azure.mgmt.horizondb.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.horizondb.models.ActivateChangeDataCaptureIdentityRequest(_Model):
        drain_existing_sessions: Optional[bool]
        identity_assignment_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                drain_existing_sessions: Optional[bool] = ..., 
                identity_assignment_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ActivateChangeDataCaptureIdentityResult(_Model):
        previous_identity_assignment_resource_id: Optional[str]
        status: Literal["Succeeded"]
        target_identity_assignment_resource_id: str

        def __init__(
                self, 
                *args: Any, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.horizondb.models.AiModelManagementStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.Authentication(ProxyResource):
        id: str
        name: str
        properties: Optional[AuthenticationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AuthenticationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.AuthenticationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_ENTRA = "microsoftEntra"
        PASSWORD_METHOD = "passwordMethod"


    class azure.mgmt.horizondb.models.AuthenticationProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Union[str, AuthenticationState]


    class azure.mgmt.horizondb.models.AuthenticationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.BackupProperties(_Model):
        earliest_restore_point_utc: Optional[datetime]
        geo_redundancy: Union[str, GeoRedundancyState]
        retention_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                geo_redundancy: Union[str, GeoRedundancyState], 
                retention_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.BackupPropertiesForPatchUpdate(_Model):
        retention_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                retention_days: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.Capability(ProxyResource):
        id: str
        name: str
        properties: Optional[CapabilityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CapabilityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.CapabilityProperties(_Model):
        cluster_capabilities: ClusterCapability
        pool_capabilities: PoolCapability
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.horizondb.models.ChangeDataCaptureCapability(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ChangeDataCaptureCapabilityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureCapabilityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureCapabilityForPatchUpdate(_Model):
        properties: Optional[ChangeDataCaptureCapabilityPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureCapabilityPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureCapabilityProperties(_Model):
        auto_upgrade_extension: Optional[bool]
        configuration_count: int
        desired_state: Union[str, ChangeDataCaptureDesiredState]
        destination_count: int
        effective_state: Union[str, ChangeDataCaptureEffectiveState]
        extension: ChangeDataCaptureExtensionStatus
        prerequisites: ChangeDataCapturePrerequisiteStatus
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication_architecture: Union[str, ChangeDataCaptureReplicationArchitecture]
        status: ChangeDataCaptureStatus

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_extension: Optional[bool] = ..., 
                desired_state: Union[str, ChangeDataCaptureDesiredState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureCapabilityPropertiesForPatchUpdate(_Model):
        auto_upgrade_extension: Optional[bool]
        desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]]

        @overload
        def __init__(
                self, 
                *, 
                auto_upgrade_extension: Optional[bool] = ..., 
                desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureConfiguration(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ChangeDataCaptureConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureConfigurationForPatchUpdate(_Model):
        properties: Optional[ChangeDataCaptureConfigurationPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureConfigurationPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureConfigurationProperties(_Model):
        database_name: str
        desired_state: Union[str, ChangeDataCaptureDesiredState]
        destination_resource_id: str
        effective_state: Union[str, ChangeDataCaptureEffectiveState]
        extension: ChangeDataCaptureExtensionStatus
        logical_stream_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        replication: ChangeDataCaptureReplicationStatus
        status: ChangeDataCaptureStatus
        topology: ChangeDataCaptureTopologyBindingStatus
        usage_profile: Union[str, ChangeDataCaptureUsageProfile]

        @overload
        def __init__(
                self, 
                *, 
                database_name: str, 
                desired_state: Union[str, ChangeDataCaptureDesiredState], 
                destination_resource_id: str, 
                usage_profile: Union[str, ChangeDataCaptureUsageProfile]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureConfigurationPropertiesForPatchUpdate(_Model):
        desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]]

        @overload
        def __init__(
                self, 
                *, 
                desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDesiredState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestination(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ChangeDataCaptureDestinationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureDestinationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationDetails(_Model):
        destination_type: str
        protocol: Union[str, ChangeDataCaptureProtocol]

        @overload
        def __init__(
                self, 
                *, 
                destination_type: str, 
                protocol: Union[str, ChangeDataCaptureProtocol]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationEffectiveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED = "Failed"
        WAITING_FOR_IDENTITY = "WaitingForIdentity"


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationForPatchUpdate(_Model):
        properties: Optional[ChangeDataCaptureDestinationPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureDestinationPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationProperties(_Model):
        active_identity_assignment_resource_id: Optional[str]
        configuration_count: int
        desired_state: Union[str, ChangeDataCaptureDesiredState]
        destination: ChangeDataCaptureDestinationDetails
        effective_state: Union[str, ChangeDataCaptureDestinationEffectiveState]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: ChangeDataCaptureStatus

        @overload
        def __init__(
                self, 
                *, 
                desired_state: Union[str, ChangeDataCaptureDesiredState], 
                destination: ChangeDataCaptureDestinationDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationPropertiesForPatchUpdate(_Model):
        desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]]

        @overload
        def __init__(
                self, 
                *, 
                desired_state: Optional[Union[str, ChangeDataCaptureDesiredState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC = "Fabric"


    class azure.mgmt.horizondb.models.ChangeDataCaptureEffectiveState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEGRADED = "Degraded"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED = "Failed"


    class azure.mgmt.horizondb.models.ChangeDataCaptureEngineConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_READY = "NotReady"
        READY = "Ready"
        RECONCILING = "Reconciling"


    class azure.mgmt.horizondb.models.ChangeDataCaptureExtensionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INSTALLING = "Installing"
        NOT_INSTALLED = "NotInstalled"
        READY = "Ready"
        REMOVING = "Removing"
        UPGRADING = "Upgrading"


    class azure.mgmt.horizondb.models.ChangeDataCaptureExtensionStatus(_Model):
        name: str
        state: Union[str, ChangeDataCaptureExtensionState]
        version: str


    class azure.mgmt.horizondb.models.ChangeDataCaptureIdentityActivationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVATING = "Activating"
        ACTIVE = "Active"
        DEACTIVATING = "Deactivating"
        FAILED = "Failed"
        INACTIVE = "Inactive"


    class azure.mgmt.horizondb.models.ChangeDataCaptureIdentityAssignmentProperties(_Model):
        activation_state: Union[str, ChangeDataCaptureIdentityActivationState]
        effective_state: Union[str, ChangeDataCaptureIdentityAssignmentState]
        identity_resource_id: str
        principal_id: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: ChangeDataCaptureStatus
        tenant_id: str
        validation: IdentityValidationStatus

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ChangeDataCaptureIdentityAssignmentState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGNED = "Assigned"
        ASSIGNING = "Assigning"
        FAILED = "Failed"
        REMOVING = "Removing"


    class azure.mgmt.horizondb.models.ChangeDataCaptureIdentityValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.horizondb.models.ChangeDataCapturePrerequisiteStatus(_Model):
        engine_configuration_state: Union[str, ChangeDataCaptureEngineConfigurationState]
        read_write_endpoint_state: Union[str, ChangeDataCaptureReadWriteEndpointState]


    class azure.mgmt.horizondb.models.ChangeDataCaptureProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NATIVE = "Native"


    class azure.mgmt.horizondb.models.ChangeDataCaptureReadWriteEndpointState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READY = "Ready"
        UNAVAILABLE = "Unavailable"


    class azure.mgmt.horizondb.models.ChangeDataCaptureReplicationArchitecture(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPUTE_BASED = "ComputeBased"
        HYBRID = "Hybrid"
        STORAGE_BASED = "StorageBased"


    class azure.mgmt.horizondb.models.ChangeDataCaptureReplicationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTING = "Connecting"
        DEGRADED = "Degraded"
        FAILED = "Failed"
        NOT_APPLICABLE = "NotApplicable"
        NOT_CONNECTED = "NotConnected"
        PAUSED = "Paused"
        RECONNECTING = "Reconnecting"
        REPLICATING = "Replicating"
        STOPPING = "Stopping"


    class azure.mgmt.horizondb.models.ChangeDataCaptureReplicationStatus(_Model):
        external_artifact_id: Optional[str]
        last_connected_at_utc: Optional[datetime]
        state: Union[str, ChangeDataCaptureReplicationState]


    class azure.mgmt.horizondb.models.ChangeDataCaptureStatus(_Model):
        code: str
        message: str


    class azure.mgmt.horizondb.models.ChangeDataCaptureTopologyBindingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CONFLICT = "Conflict"
        REBIND_REQUIRED = "RebindRequired"
        RECONCILING = "Reconciling"
        SUPERSEDED = "Superseded"


    class azure.mgmt.horizondb.models.ChangeDataCaptureTopologyBindingStatus(_Model):
        active_cluster_resource_id: str
        generation: int
        replacement_configuration_resource_id: Optional[str]
        state: Union[str, ChangeDataCaptureTopologyBindingState]


    class azure.mgmt.horizondb.models.ChangeDataCaptureUsageProfile(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIRRORING = "Mirroring"


    class azure.mgmt.horizondb.models.Cluster(TrackedResource):
        id: str
        identity: Optional[HorizonDbClusterManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[ClusterProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[HorizonDbClusterManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ClusterProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ClusterCapability(_Model):
        recommended_postgre_sql_version: Union[str, PostgreSqlCapabilityVersion]
        supported_features: list[ClusterFeatureCapability]
        supported_postgre_sql_versions: list[PostgreSqlVersionCapability]


    class azure.mgmt.horizondb.models.ClusterCreateMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        POINT_IN_TIME_RESTORE = "PointInTimeRestore"


    class azure.mgmt.horizondb.models.ClusterFeatureCapability(_Model):
        name: str


    class azure.mgmt.horizondb.models.ClusterForPatchUpdate(_Model):
        identity: Optional[HorizonDbClusterManagedServiceIdentity]
        properties: Optional[ClusterPropertiesForPatchUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[HorizonDbClusterManagedServiceIdentity] = ..., 
                properties: Optional[ClusterPropertiesForPatchUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ClusterProperties(_Model):
        ai_model_management: Optional[Union[str, AiModelManagementStatus]]
        backup: Optional[BackupProperties]
        creation_mode: Optional[Union[str, ClusterCreateMode]]
        creation_source_cluster_location: Optional[str]
        creation_source_cluster_resource_id: Optional[str]
        data_encryption: Optional[HorizonDbClusterDataEncryption]
        network: Optional[Network]
        point_in_time_utc: Optional[datetime]
        postgre_sql_version: Optional[Union[str, PostgreSqlVersion]]
        provisioning_state: Union[str, ProvisioningState]
        read_write_pool: ReadWritePoolProperties
        state: Union[str, ClusterState]

        @overload
        def __init__(
                self, 
                *, 
                ai_model_management: Optional[Union[str, AiModelManagementStatus]] = ..., 
                backup: Optional[BackupProperties] = ..., 
                creation_mode: Optional[Union[str, ClusterCreateMode]] = ..., 
                creation_source_cluster_location: Optional[str] = ..., 
                creation_source_cluster_resource_id: Optional[str] = ..., 
                data_encryption: Optional[HorizonDbClusterDataEncryption] = ..., 
                network: Optional[Network] = ..., 
                point_in_time_utc: Optional[datetime] = ..., 
                postgre_sql_version: Optional[Union[str, PostgreSqlVersion]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ClusterPropertiesForPatchUpdate(_Model):
        ai_model_management: Optional[Union[str, AiModelManagementStatus]]
        backup: Optional[BackupPropertiesForPatchUpdate]
        data_encryption: Optional[HorizonDbClusterDataEncryptionForPatchUpdate]
        network: Optional[NetworkForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                ai_model_management: Optional[Union[str, AiModelManagementStatus]] = ..., 
                backup: Optional[BackupPropertiesForPatchUpdate] = ..., 
                data_encryption: Optional[HorizonDbClusterDataEncryptionForPatchUpdate] = ..., 
                network: Optional[NetworkForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ClusterState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        INACCESSIBLE = "Inaccessible"
        PROVISIONING = "Provisioning"
        READY = "Ready"
        UPDATING = "Updating"


    class azure.mgmt.horizondb.models.ComputeGenerationCapability(_Model):
        compute_generation: int
        recommended_compute_model_type: Union[str, PoolComputeModelType]
        supported_compute_models: list[ComputeModelCapability]


    class azure.mgmt.horizondb.models.ComputeModelCapability(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ComputeProcessorCapability(_Model):
        name: Union[str, ComputeProcessorType]
        supported_generations: list[ComputeGenerationCapability]


    class azure.mgmt.horizondb.models.ComputeProcessorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AMD = "AMD"
        INTEL = "Intel"


    class azure.mgmt.horizondb.models.ComputeSizeCapability(_Model):
        memory_per_v_core_in_mb: int
        v_cores: int


    class azure.mgmt.horizondb.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.horizondb.models.DefaultParameterGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[DefaultParameterGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DefaultParameterGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.DefaultParameterGroupProperties(_Model):
        description: Optional[str]
        parameters: list[ParameterProperties]
        postgre_sql_version: Union[str, PostgreSqlVersion]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: list[ParameterProperties], 
                postgre_sql_version: Union[str, PostgreSqlVersion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.Endpoint(ProxyResource):
        id: str
        name: str
        properties: Optional[EndpointProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EndpointProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.EndpointProperties(_Model):
        associated_resource_id: str
        fully_qualified_domain_name: str
        role: Union[str, EndpointRole]
        scope: Union[str, EndpointScope]


    class azure.mgmt.horizondb.models.EndpointRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"


    class azure.mgmt.horizondb.models.EndpointScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLUSTER = "Cluster"
        POOL = "Pool"


    class azure.mgmt.horizondb.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.horizondb.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.horizondb.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.FabricDestinationDetails(ChangeDataCaptureDestinationDetails, discriminator='Fabric'):
        destination_type: Literal[ChangeDataCaptureDestinationType.FABRIC]
        protocol: Literal[ChangeDataCaptureProtocol.NATIVE]
        workspace_id: str

        @overload
        def __init__(
                self, 
                *, 
                protocol: Literal[ChangeDataCaptureProtocol.NATIVE], 
                workspace_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.FirewallRule(ProxyResource):
        id: str
        name: str
        properties: Optional[FirewallRuleProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FirewallRuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.FirewallRuleProperties(_Model):
        description: Optional[str]
        end_ip_address: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_ip_address: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                end_ip_address: str, 
                start_ip_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.GeoRedundancyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.HorizonDbClusterDataEncryption(_Model):
        primary_encryption_key_current_version: Optional[str]
        primary_encryption_key_status: Optional[Union[str, HorizonDbClusterEncryptionKeyStatus]]
        primary_key_uri: Optional[str]
        primary_user_assigned_identity_id: Optional[str]
        type: Optional[Union[str, HorizonDbClusterDataEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                primary_key_uri: Optional[str] = ..., 
                primary_user_assigned_identity_id: Optional[str] = ..., 
                type: Optional[Union[str, HorizonDbClusterDataEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterDataEncryptionForPatchUpdate(_Model):
        primary_key_uri: Optional[str]
        primary_user_assigned_identity_id: Optional[str]
        type: Optional[Union[str, HorizonDbClusterDataEncryptionType]]

        @overload
        def __init__(
                self, 
                *, 
                primary_key_uri: Optional[str] = ..., 
                primary_user_assigned_identity_id: Optional[str] = ..., 
                type: Optional[Union[str, HorizonDbClusterDataEncryptionType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.HorizonDbClusterDataEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        SYSTEM_MANAGED = "SystemManaged"


    class azure.mgmt.horizondb.models.HorizonDbClusterEncryptionKeyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.horizondb.models.HorizonDbClusterIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.horizondb.models.HorizonDbClusterManagedServiceIdentity(_Model):
        type: Union[str, HorizonDbClusterIdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, HorizonDbClusterIdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.IdentityAssignment(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[ChangeDataCaptureIdentityAssignmentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ChangeDataCaptureIdentityAssignmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.IdentityValidationStatus(_Model):
        error: Optional[ErrorDetail]
        state: Union[str, ChangeDataCaptureIdentityValidationState]
        validated_at_utc: Optional[datetime]


    class azure.mgmt.horizondb.models.LogCaptureConfiguration(ProxyResource):
        id: str
        name: str
        properties: Optional[LogCaptureConfigurationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogCaptureConfigurationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogCaptureConfigurationForPatchUpdate(_Model):
        properties: Optional[LogCaptureConfigurationPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogCaptureConfigurationPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogCaptureConfigurationProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        retention_days: int
        state: Union[str, LogCaptureState]

        @overload
        def __init__(
                self, 
                *, 
                retention_days: int, 
                state: Union[str, LogCaptureState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogCaptureConfigurationPropertiesForPatchUpdate(_Model):
        retention_days: Optional[int]
        state: Optional[Union[str, LogCaptureState]]

        @overload
        def __init__(
                self, 
                *, 
                retention_days: Optional[int] = ..., 
                state: Optional[Union[str, LogCaptureState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogCaptureState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.LogFile(ProxyResource):
        id: str
        name: str
        properties: Optional[LogFileProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LogFileProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogFileDownloadUrl(_Model):
        download_uri: str
        expires_at_utc: datetime

        @overload
        def __init__(
                self, 
                *, 
                download_uri: str, 
                expires_at_utc: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.LogFileProperties(_Model):
        created_at_utc: datetime
        is_mutable: bool
        last_modified_at_utc: datetime
        log_type: Union[str, LogFileType]
        node: str
        pool: str
        retention_expires_at_utc: datetime
        role: Union[str, NodeRole]
        size_in_kilobytes: int


    class azure.mgmt.horizondb.models.LogFileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POSTGRE_SQL_SERVER = "PostgreSqlServer"


    class azure.mgmt.horizondb.models.MaintenanceEvent(ProxyResource):
        id: str
        name: str
        properties: Optional[MaintenanceEventProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaintenanceEventProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MaintenanceEventActionResponse(_Model):
        applied_now: Optional[bool]
        last_updated_time_utc: Optional[datetime]
        maintenance_event_id: Optional[str]
        planned_end_time_utc: Optional[datetime]
        planned_start_time_utc: Optional[datetime]
        pool_resource_id: Optional[str]
        status: Optional[Union[str, MaintenanceEventStatus]]

        @overload
        def __init__(
                self, 
                *, 
                applied_now: Optional[bool] = ..., 
                last_updated_time_utc: Optional[datetime] = ..., 
                maintenance_event_id: Optional[str] = ..., 
                planned_end_time_utc: Optional[datetime] = ..., 
                planned_start_time_utc: Optional[datetime] = ..., 
                pool_resource_id: Optional[str] = ..., 
                status: Optional[Union[str, MaintenanceEventStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MaintenanceEventProperties(_Model):
        deferrable: bool
        deferral_deadline_utc: Optional[datetime]
        description: Optional[str]
        end_time_utc: datetime
        estimated_downtime: Optional[timedelta]
        last_updated_time_utc: Optional[datetime]
        maintenance_event_id: Optional[str]
        maintenance_type: Union[str, MaintenanceType]
        original_start_time_utc: datetime
        rescheduled_from_utc: Optional[datetime]
        start_time_utc: datetime
        status: Union[str, MaintenanceEventStatus]


    class azure.mgmt.horizondb.models.MaintenanceEventRescheduleRequest(_Model):
        postpone_to_date_time_utc: datetime

        @overload
        def __init__(
                self, 
                *, 
                postpone_to_date_time_utc: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MaintenanceEventStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETE = "Complete"
        IN_PROGRESS = "InProgress"
        PLANNED = "Planned"
        RESCHEDULED = "Rescheduled"


    class azure.mgmt.horizondb.models.MaintenanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PLANNED_MAINTENANCE = "PlannedMaintenance"


    class azure.mgmt.horizondb.models.MicrosoftEntraAdministrator(ProxyResource):
        id: str
        name: str
        properties: Optional[MicrosoftEntraAdministratorProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MicrosoftEntraAdministratorProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAdministratorAdd(_Model):
        properties: MicrosoftEntraAdministratorPropertiesForAdd

        @overload
        def __init__(
                self, 
                *, 
                properties: MicrosoftEntraAdministratorPropertiesForAdd
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAdministratorProperties(_Model):
        object_id: Optional[str]
        principal_name: str
        principal_type: Union[str, PrincipalTypes]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_name: str, 
                principal_type: Union[str, PrincipalTypes], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAdministratorPropertiesForAdd(_Model):
        principal_name: str
        principal_type: Union[str, PrincipalTypes]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                principal_name: str, 
                principal_type: Union[str, PrincipalTypes], 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAuthentication(ProxyResource):
        id: str
        name: str
        properties: Optional[MicrosoftEntraAuthenticationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MicrosoftEntraAuthenticationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAuthenticationForPatchUpdate(_Model):
        properties: Optional[MicrosoftEntraAuthenticationPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MicrosoftEntraAuthenticationPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAuthenticationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_ENTRA = "microsoftEntra"


    class azure.mgmt.horizondb.models.MicrosoftEntraAuthenticationProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Union[str, AuthenticationState]

        @overload
        def __init__(
                self, 
                *, 
                state: Union[str, AuthenticationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.MicrosoftEntraAuthenticationPropertiesForPatchUpdate(_Model):
        state: Optional[Union[str, AuthenticationState]]

        @overload
        def __init__(
                self, 
                *, 
                state: Optional[Union[str, AuthenticationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.Network(_Model):
        public_access: Optional[Union[str, PublicNetworkAccessState]]

        @overload
        def __init__(
                self, 
                *, 
                public_access: Optional[Union[str, PublicNetworkAccessState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.NetworkForPatchUpdate(_Model):
        public_access: Optional[Union[str, PublicNetworkAccessState]]

        @overload
        def __init__(
                self, 
                *, 
                public_access: Optional[Union[str, PublicNetworkAccessState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.Node(ProxyResource):
        id: str
        name: str
        properties: Optional[NodeProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.NodeProperties(_Model):
        availability_zone: str
        role: Union[str, NodeRole]


    class azure.mgmt.horizondb.models.NodeRole(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        READ_ONLY = "ReadOnly"
        READ_WRITE = "ReadWrite"
        UNASSIGNED = "Unassigned"


    class azure.mgmt.horizondb.models.Operation(_Model):
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


    class azure.mgmt.horizondb.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.horizondb.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.horizondb.models.ParameterApplyMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMMEDIATE = "Immediate"
        PENDING_REBOOT = "PendingReboot"


    class azure.mgmt.horizondb.models.ParameterGroup(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ParameterGroupProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ParameterGroupProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ParameterGroupConnectionProperties(_Model):
        pool_resource_id: str


    class azure.mgmt.horizondb.models.ParameterGroupForPatchUpdate(_Model):
        properties: Optional[ParameterGroupPropertiesForPatchUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ParameterGroupPropertiesForPatchUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ParameterGroupProperties(_Model):
        description: Optional[str]
        parameters: Optional[list[ParameterProperties]]
        postgre_sql_version: Union[str, PostgreSqlVersion]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: Optional[list[ParameterProperties]] = ..., 
                postgre_sql_version: Union[str, PostgreSqlVersion]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ParameterGroupPropertiesForPatchUpdate(_Model):
        description: Optional[str]
        parameters: Optional[list[ParameterProperties]]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                parameters: Optional[list[ParameterProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ParameterGroupSyncStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLYING = "Applying"
        FAILED_TO_APPLY = "FailedToApply"
        IN_SYNC = "InSync"
        PENDING_REBOOT = "PendingReboot"


    class azure.mgmt.horizondb.models.ParameterProperties(_Model):
        allowed_values: Optional[str]
        data_type: Optional[str]
        default_value: Optional[str]
        description: Optional[str]
        documentation_link: Optional[str]
        is_dynamic: Optional[bool]
        is_read_only: Optional[bool]
        name: Optional[str]
        unit: Optional[str]
        value: Optional[str]
        value_source: Optional[Union[str, ParameterValueSource]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ParameterValueSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_DEFAULT = "SystemDefault"
        USER_OVERRIDE = "UserOverride"


    class azure.mgmt.horizondb.models.PasswordAuthentication(ProxyResource):
        id: str
        name: str
        properties: Optional[PasswordAuthenticationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PasswordAuthenticationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PasswordAuthenticationForPatchUpdate(_Model):
        properties: Optional[PasswordAuthenticationPropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PasswordAuthenticationPropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PasswordAuthenticationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PASSWORD_METHOD = "passwordMethod"


    class azure.mgmt.horizondb.models.PasswordAuthenticationProperties(_Model):
        administrator_login: Optional[str]
        administrator_login_password: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        state: Union[str, AuthenticationState]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login: Optional[str] = ..., 
                administrator_login_password: Optional[str] = ..., 
                state: Union[str, AuthenticationState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PasswordAuthenticationPropertiesForPatchUpdate(_Model):
        administrator_login_password: Optional[str]
        state: Optional[Union[str, AuthenticationState]]

        @overload
        def __init__(
                self, 
                *, 
                administrator_login_password: Optional[str] = ..., 
                state: Optional[Union[str, AuthenticationState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.Pool(ProxyResource):
        id: str
        name: str
        properties: Optional[PoolProperties]
        system_data: SystemData
        tags: Optional[dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PoolProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolCapability(_Model):
        recommended_compute_processor: Union[str, ComputeProcessorType]
        supported_features: list[PoolFeatureCapability]
        supported_processors: list[ComputeProcessorCapability]


    class azure.mgmt.horizondb.models.PoolComputeModel(_Model):
        compute_generation: int
        compute_processor: Union[str, ComputeProcessorType]
        type: Union[str, PoolComputeModelType]
        v_cores: int

        @overload
        def __init__(
                self, 
                *, 
                compute_generation: int, 
                compute_processor: Union[str, ComputeProcessorType], 
                type: Union[str, PoolComputeModelType], 
                v_cores: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolComputeModelForPatchUpdate(_Model):
        compute_generation: Optional[int]
        compute_processor: Optional[Union[str, ComputeProcessorType]]
        type: Optional[Union[str, PoolComputeModelType]]
        v_cores: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                compute_generation: Optional[int] = ..., 
                compute_processor: Optional[Union[str, ComputeProcessorType]] = ..., 
                type: Optional[Union[str, PoolComputeModelType]] = ..., 
                v_cores: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolComputeModelType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROVISIONED = "Provisioned"


    class azure.mgmt.horizondb.models.PoolFeatureCapability(_Model):
        name: str


    class azure.mgmt.horizondb.models.PoolForPatchUpdate(_Model):
        properties: Optional[PoolPropertiesForPatchUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PoolPropertiesForPatchUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolHighAvailability(_Model):
        mode: Union[str, PoolHighAvailabilityMode]

        @overload
        def __init__(
                self, 
                *, 
                mode: Union[str, PoolHighAvailabilityMode]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolHighAvailabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY_ZONE = "AnyZone"
        DISABLED = "Disabled"
        ZONE_REDUNDANT = "ZoneRedundant"


    class azure.mgmt.horizondb.models.PoolHighAvailabilityPatch(_Model):
        mode: Optional[Union[str, PoolHighAvailabilityMode]]

        @overload
        def __init__(
                self, 
                *, 
                mode: Optional[Union[str, PoolHighAvailabilityMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolParameterGroupReference(_Model):
        apply_method: Union[str, ParameterApplyMethod]
        parameter_group_resource_id: str
        sync_status: Optional[Union[str, ParameterGroupSyncStatus]]

        @overload
        def __init__(
                self, 
                *, 
                apply_method: Union[str, ParameterApplyMethod], 
                parameter_group_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolParameterGroupReferenceForPatchUpdate(_Model):
        apply_method: Optional[Union[str, ParameterApplyMethod]]
        parameter_group_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                apply_method: Optional[Union[str, ParameterApplyMethod]] = ..., 
                parameter_group_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolProperties(_Model):
        compute_model: PoolComputeModel
        high_availability: PoolHighAvailability
        node_count: int
        parameter_group: PoolParameterGroupReference
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scheduled_maintenance: Optional[ScheduledMaintenanceProperties]
        state: Optional[Union[str, PoolState]]

        @overload
        def __init__(
                self, 
                *, 
                compute_model: PoolComputeModel, 
                high_availability: PoolHighAvailability, 
                node_count: int, 
                parameter_group: PoolParameterGroupReference, 
                scheduled_maintenance: Optional[ScheduledMaintenanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolPropertiesForPatchUpdate(_Model):
        compute_model: Optional[PoolComputeModelForPatchUpdate]
        high_availability: Optional[PoolHighAvailabilityPatch]
        node_count: Optional[int]
        parameter_group: Optional[PoolParameterGroupReferenceForPatchUpdate]
        scheduled_maintenance: Optional[ScheduledMaintenancePropertiesForPatchUpdate]

        @overload
        def __init__(
                self, 
                *, 
                compute_model: Optional[PoolComputeModelForPatchUpdate] = ..., 
                high_availability: Optional[PoolHighAvailabilityPatch] = ..., 
                node_count: Optional[int] = ..., 
                parameter_group: Optional[PoolParameterGroupReferenceForPatchUpdate] = ..., 
                scheduled_maintenance: Optional[ScheduledMaintenancePropertiesForPatchUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PoolState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        INACCESSIBLE = "Inaccessible"
        PROVISIONING = "Provisioning"
        READY = "Ready"
        RESTARTING = "Restarting"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        UPDATING = "Updating"


    class azure.mgmt.horizondb.models.PostgreSqlCapabilityVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V17 = "17"
        V18 = "18"


    class azure.mgmt.horizondb.models.PostgreSqlVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        V17 = "17"
        V18 = "18"


    class azure.mgmt.horizondb.models.PostgreSqlVersionCapability(_Model):
        name: Union[str, PostgreSqlCapabilityVersion]
        supported_versions_to_upgrade: list[Union[str, PostgreSqlCapabilityVersion]]


    class azure.mgmt.horizondb.models.PrincipalTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GROUP = "Group"
        SERVICE_PRINCIPAL = "ServicePrincipal"
        UNKNOWN = "Unknown"
        USER = "User"


    class azure.mgmt.horizondb.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.horizondb.models.PrivateEndpointConnectionResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.horizondb.models.PrivateLinkResource(ProxyResource):
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


    class azure.mgmt.horizondb.models.PrivateLinkResourceProperties(_Model):
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


    class azure.mgmt.horizondb.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.horizondb.models.ProvisionedComputeModelCapability(ComputeModelCapability, discriminator='Provisioned'):
        recommended_v_core_count: int
        supported_compute_sizes: list[ComputeSizeCapability]
        type: Literal[PoolComputeModelType.PROVISIONED]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.horizondb.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.horizondb.models.PublicNetworkAccessState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.horizondb.models.ReadWritePoolProperties(_Model):
        designated_pool_resource_id: Optional[str]


    class azure.mgmt.horizondb.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.horizondb.models.ScheduledMaintenanceManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"


    class azure.mgmt.horizondb.models.ScheduledMaintenanceProperties(_Model):
        maintenance_management_type: str

        @overload
        def __init__(
                self, 
                *, 
                maintenance_management_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.ScheduledMaintenancePropertiesForPatchUpdate(_Model):
        maintenance_management_type: Optional[Union[str, ScheduledMaintenanceManagementType]]

        @overload
        def __init__(
                self, 
                *, 
                maintenance_management_type: Optional[Union[str, ScheduledMaintenanceManagementType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.SystemData(_Model):
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


    class azure.mgmt.horizondb.models.SystemScheduledMaintenanceProperties(ScheduledMaintenanceProperties, discriminator='System'):
        maintenance_management_type: Literal[ScheduledMaintenanceManagementType.SYSTEM]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.horizondb.models.TrackedResource(Resource):
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


    class azure.mgmt.horizondb.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.horizondb.operations

    class azure.mgmt.horizondb.operations.AuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Authentication]: ...


    class azure.mgmt.horizondb.operations.CapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Capability: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Capability]: ...


    class azure.mgmt.horizondb.operations.ChangeDataCaptureCapabilitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: ChangeDataCaptureCapability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: ChangeDataCaptureCapability, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

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
                properties: ChangeDataCaptureCapabilityForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ChangeDataCaptureCapabilityForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureCapability]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureCapability: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ChangeDataCaptureCapability]: ...


    class azure.mgmt.horizondb.operations.ChangeDataCaptureConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: ChangeDataCaptureConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: ChangeDataCaptureConfiguration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: ChangeDataCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: ChangeDataCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                configuration_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ChangeDataCaptureConfiguration]: ...


    class azure.mgmt.horizondb.operations.ChangeDataCaptureDestinationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: ActivateChangeDataCaptureIdentityRequest, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: ActivateChangeDataCaptureIdentityRequest, 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        def begin_activate_identity(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                etag: str, 
                match_condition: MatchConditions, 
                **kwargs: Any
            ) -> LROPoller[ActivateChangeDataCaptureIdentityResult]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: ChangeDataCaptureDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: ChangeDataCaptureDestination, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: ChangeDataCaptureDestinationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: ChangeDataCaptureDestinationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ChangeDataCaptureDestination]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> ChangeDataCaptureDestination: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ChangeDataCaptureDestination]: ...


    class azure.mgmt.horizondb.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
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

        @distributed_trace
        def begin_failover(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: ClusterForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
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
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Cluster]: ...


    class azure.mgmt.horizondb.operations.DefaultParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                name: str, 
                **kwargs: Any
            ) -> DefaultParameterGroup: ...

        @distributed_trace
        def list_by_subscription_and_region(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[DefaultParameterGroup]: ...


    class azure.mgmt.horizondb.operations.EndpointsOperations:

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
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Endpoint]: ...


    class azure.mgmt.horizondb.operations.FirewallRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: FirewallRule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallRule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                firewall_rule_name: str, 
                **kwargs: Any
            ) -> FirewallRule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallRule]: ...


    class azure.mgmt.horizondb.operations.IdentityAssignmentsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IdentityAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityAssignment]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IdentityAssignment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityAssignment]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IdentityAssignment]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                assignment_name: str, 
                **kwargs: Any
            ) -> IdentityAssignment: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                destination_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IdentityAssignment]: ...


    class azure.mgmt.horizondb.operations.LogCaptureConfigurationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: LogCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogCaptureConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: LogCaptureConfigurationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogCaptureConfiguration]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LogCaptureConfiguration]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_capture_configuration_name: str, 
                **kwargs: Any
            ) -> LogCaptureConfiguration: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogCaptureConfiguration]: ...


    class azure.mgmt.horizondb.operations.LogFilesOperations:

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
                log_file_name: str, 
                **kwargs: Any
            ) -> LogFile: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LogFile]: ...

        @distributed_trace
        def list_download_urls(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                log_file_name: str, 
                **kwargs: Any
            ) -> LogFileDownloadUrl: ...


    class azure.mgmt.horizondb.operations.MaintenanceEventsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_apply_now(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                **kwargs: Any
            ) -> LROPoller[MaintenanceEventActionResponse]: ...

        @overload
        def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: MaintenanceEventRescheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceEventActionResponse]: ...

        @overload
        def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: MaintenanceEventRescheduleRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceEventActionResponse]: ...

        @overload
        def begin_reschedule(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MaintenanceEventActionResponse]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                maintenance_event_id: str, 
                **kwargs: Any
            ) -> MaintenanceEvent: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[MaintenanceEvent]: ...


    class azure.mgmt.horizondb.operations.MicrosoftEntraAdministratorsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: MicrosoftEntraAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAdministrator]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: MicrosoftEntraAdministratorAdd, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAdministrator]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAdministrator]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                object_id: str, 
                **kwargs: Any
            ) -> MicrosoftEntraAdministrator: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MicrosoftEntraAdministrator]: ...


    class azure.mgmt.horizondb.operations.MicrosoftEntraAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: MicrosoftEntraAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: MicrosoftEntraAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: MicrosoftEntraAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: MicrosoftEntraAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MicrosoftEntraAuthentication]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> MicrosoftEntraAuthentication: ...


    class azure.mgmt.horizondb.operations.NodesOperations:

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
                pool_name: str, 
                node_name: str, 
                **kwargs: Any
            ) -> Node: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Node]: ...


    class azure.mgmt.horizondb.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.horizondb.operations.ParameterGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: ParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: ParameterGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: ParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: ParameterGroupForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ParameterGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> ParameterGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ParameterGroup]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ParameterGroup]: ...

        @distributed_trace
        def list_connections(
                self, 
                resource_group_name: str, 
                parameter_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ParameterGroupConnectionProperties]: ...


    class azure.mgmt.horizondb.operations.PasswordAuthenticationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: PasswordAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: PasswordAuthentication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: PasswordAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: PasswordAuthenticationForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PasswordAuthentication]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> PasswordAuthentication: ...


    class azure.mgmt.horizondb.operations.PoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: Pool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_restart(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: PoolForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: PoolForPatchUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Pool]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                pool_name: str, 
                **kwargs: Any
            ) -> Pool: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Pool]: ...


    class azure.mgmt.horizondb.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnectionResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @overload
        def begin_approve_or_reject(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnectionResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnectionResource]: ...


    class azure.mgmt.horizondb.operations.PrivateLinkResourcesOperations:

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
                group_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.horizondb.types

    class azure.mgmt.horizondb.types.ActivateChangeDataCaptureIdentityRequest(TypedDict, total=False):
        key "drainExistingSessions": bool
        key "identityAssignmentResourceId": Required[str]
        drainExistingSessions: bool
        identityAssignmentResourceId: str


    class azure.mgmt.horizondb.types.BackupProperties(TypedDict, total=False):
        key "earliestRestorePointUtc": str
        key "geoRedundancy": Required[Union[str, GeoRedundancyState]]
        key "retentionDays": int
        earliestRestorePointUtc: str
        geoRedundancy: Union[str, GeoRedundancyState]
        retentionDays: int


    class azure.mgmt.horizondb.types.BackupPropertiesForPatchUpdate(TypedDict, total=False):
        key "retentionDays": int
        retentionDays: int


    class azure.mgmt.horizondb.types.ChangeDataCaptureCapability(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChangeDataCaptureCapabilityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ChangeDataCaptureCapabilityProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureCapabilityForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ChangeDataCaptureCapabilityPropertiesForPatchUpdate', module='types')
        properties: ChangeDataCaptureCapabilityPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.ChangeDataCaptureCapabilityProperties(TypedDict, total=False):
        key "autoUpgradeExtension": bool
        key "configurationCount": Required[int]
        key "desiredState": Required[Union[str, ChangeDataCaptureDesiredState]]
        key "destinationCount": Required[int]
        key "effectiveState": Required[Union[str, ChangeDataCaptureEffectiveState]]
        key "extension": Required[ChangeDataCaptureExtensionStatus]
        key "prerequisites": Required[ChangeDataCapturePrerequisiteStatus]
        key "provisioningState": Union[str, ProvisioningState]
        key "replicationArchitecture": Required[Union[str, ChangeDataCaptureReplicationArchitecture]]
        key "status": Required[ChangeDataCaptureStatus]
        autoUpgradeExtension: bool
        configurationCount: int
        desiredState: Union[str, ChangeDataCaptureDesiredState]
        destinationCount: int
        effectiveState: Union[str, ChangeDataCaptureEffectiveState]
        extension: ChangeDataCaptureExtensionStatus
        prerequisites: ChangeDataCapturePrerequisiteStatus
        provisioningState: Union[str, ProvisioningState]
        replicationArchitecture: Union[str, ChangeDataCaptureReplicationArchitecture]
        status: ChangeDataCaptureStatus


    class azure.mgmt.horizondb.types.ChangeDataCaptureCapabilityPropertiesForPatchUpdate(TypedDict, total=False):
        key "autoUpgradeExtension": bool
        key "desiredState": Union[str, ChangeDataCaptureDesiredState]
        autoUpgradeExtension: bool
        desiredState: Union[str, ChangeDataCaptureDesiredState]


    class azure.mgmt.horizondb.types.ChangeDataCaptureConfiguration(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChangeDataCaptureConfigurationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ChangeDataCaptureConfigurationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureConfigurationForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ChangeDataCaptureConfigurationPropertiesForPatchUpdate', module='types')
        properties: ChangeDataCaptureConfigurationPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.ChangeDataCaptureConfigurationProperties(TypedDict, total=False):
        key "databaseName": Required[str]
        key "desiredState": Required[Union[str, ChangeDataCaptureDesiredState]]
        key "destinationResourceId": Required[str]
        key "effectiveState": Required[Union[str, ChangeDataCaptureEffectiveState]]
        key "extension": Required[ChangeDataCaptureExtensionStatus]
        key "logicalStreamId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "replication": Required[ChangeDataCaptureReplicationStatus]
        key "status": Required[ChangeDataCaptureStatus]
        key "topology": Required[ChangeDataCaptureTopologyBindingStatus]
        key "usageProfile": Required[Union[str, ChangeDataCaptureUsageProfile]]
        databaseName: str
        desiredState: Union[str, ChangeDataCaptureDesiredState]
        destinationResourceId: str
        effectiveState: Union[str, ChangeDataCaptureEffectiveState]
        extension: ChangeDataCaptureExtensionStatus
        logicalStreamId: str
        provisioningState: Union[str, ProvisioningState]
        replication: ChangeDataCaptureReplicationStatus
        status: ChangeDataCaptureStatus
        topology: ChangeDataCaptureTopologyBindingStatus
        usageProfile: Union[str, ChangeDataCaptureUsageProfile]


    class azure.mgmt.horizondb.types.ChangeDataCaptureConfigurationPropertiesForPatchUpdate(TypedDict, total=False):
        key "desiredState": Union[str, ChangeDataCaptureDesiredState]
        desiredState: Union[str, ChangeDataCaptureDesiredState]


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestination(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChangeDataCaptureDestinationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ChangeDataCaptureDestinationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestinationDetails(TypedDict, total=False):
        key "destinationType": Required[Literal[ChangeDataCaptureDestinationType.FABRIC]]
        key "protocol": Required[Literal[ChangeDataCaptureProtocol.NATIVE]]
        key "workspaceId": Required[str]
        destinationType: Literal[ChangeDataCaptureDestinationType.FABRIC]
        protocol: Literal[ChangeDataCaptureProtocol.NATIVE]
        workspaceId: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestinationForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ChangeDataCaptureDestinationPropertiesForPatchUpdate', module='types')
        properties: ChangeDataCaptureDestinationPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestinationProperties(TypedDict, total=False):
        key "activeIdentityAssignmentResourceId": str
        key "configurationCount": Required[int]
        key "desiredState": Required[Union[str, ChangeDataCaptureDesiredState]]
        key "destination": Required[ChangeDataCaptureDestinationDetails]
        key "effectiveState": Required[Union[str, ChangeDataCaptureDestinationEffectiveState]]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Required[ChangeDataCaptureStatus]
        activeIdentityAssignmentResourceId: str
        configurationCount: int
        desiredState: Union[str, ChangeDataCaptureDesiredState]
        destination: ChangeDataCaptureDestinationDetails
        effectiveState: Union[str, ChangeDataCaptureDestinationEffectiveState]
        provisioningState: Union[str, ProvisioningState]
        status: ChangeDataCaptureStatus


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestinationPropertiesForPatchUpdate(TypedDict, total=False):
        key "desiredState": Union[str, ChangeDataCaptureDesiredState]
        desiredState: Union[str, ChangeDataCaptureDesiredState]


    class azure.mgmt.horizondb.types.ChangeDataCaptureDestinationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FABRIC = "Fabric"


    class azure.mgmt.horizondb.types.ChangeDataCaptureExtensionStatus(TypedDict, total=False):
        key "name": Required[str]
        key "state": Required[Union[str, ChangeDataCaptureExtensionState]]
        key "version": Required[str]
        name: str
        state: Union[str, ChangeDataCaptureExtensionState]
        version: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureIdentityAssignmentProperties(TypedDict, total=False):
        key "activationState": Required[Union[str, ChangeDataCaptureIdentityActivationState]]
        key "effectiveState": Required[Union[str, ChangeDataCaptureIdentityAssignmentState]]
        key "identityResourceId": Required[str]
        key "principalId": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": Required[ChangeDataCaptureStatus]
        key "tenantId": Required[str]
        key "validation": Required[IdentityValidationStatus]
        activationState: Union[str, ChangeDataCaptureIdentityActivationState]
        effectiveState: Union[str, ChangeDataCaptureIdentityAssignmentState]
        identityResourceId: str
        principalId: str
        provisioningState: Union[str, ProvisioningState]
        status: ChangeDataCaptureStatus
        tenantId: str
        validation: IdentityValidationStatus


    class azure.mgmt.horizondb.types.ChangeDataCapturePrerequisiteStatus(TypedDict, total=False):
        key "engineConfigurationState": Required[Union[str, ChangeDataCaptureEngineConfigurationState]]
        key "readWriteEndpointState": Required[Union[str, ChangeDataCaptureReadWriteEndpointState]]
        engineConfigurationState: Union[str, ChangeDataCaptureEngineConfigurationState]
        readWriteEndpointState: Union[str, ChangeDataCaptureReadWriteEndpointState]


    class azure.mgmt.horizondb.types.ChangeDataCaptureProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NATIVE = "Native"


    class azure.mgmt.horizondb.types.ChangeDataCaptureReplicationStatus(TypedDict, total=False):
        key "externalArtifactId": str
        key "lastConnectedAtUtc": str
        key "state": Required[Union[str, ChangeDataCaptureReplicationState]]
        externalArtifactId: str
        lastConnectedAtUtc: str
        state: Union[str, ChangeDataCaptureReplicationState]


    class azure.mgmt.horizondb.types.ChangeDataCaptureStatus(TypedDict, total=False):
        key "code": Required[str]
        key "message": Required[str]
        code: str
        message: str


    class azure.mgmt.horizondb.types.ChangeDataCaptureTopologyBindingStatus(TypedDict, total=False):
        key "activeClusterResourceId": Required[str]
        key "generation": Required[int]
        key "replacementConfigurationResourceId": str
        key "state": Required[Union[str, ChangeDataCaptureTopologyBindingState]]
        activeClusterResourceId: str
        generation: int
        replacementConfigurationResourceId: str
        state: Union[str, ChangeDataCaptureTopologyBindingState]


    class azure.mgmt.horizondb.types.Cluster(TrackedResource):
        key "id": str
        key "identity": ForwardRef('HorizonDbClusterManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ClusterProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: HorizonDbClusterManagedServiceIdentity
        location: str
        name: str
        properties: ClusterProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.ClusterForPatchUpdate(TypedDict, total=False):
        key "identity": ForwardRef('HorizonDbClusterManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ClusterPropertiesForPatchUpdate', module='types')
        identity: HorizonDbClusterManagedServiceIdentity
        properties: ClusterPropertiesForPatchUpdate
        tags: dict[str, str]


    class azure.mgmt.horizondb.types.ClusterProperties(TypedDict, total=False):
        key "aiModelManagement": Union[str, AiModelManagementStatus]
        key "backup": ForwardRef('BackupProperties', module='types')
        key "creationMode": Union[str, ClusterCreateMode]
        key "creationSourceClusterLocation": str
        key "creationSourceClusterResourceId": str
        key "dataEncryption": ForwardRef('HorizonDbClusterDataEncryption', module='types')
        key "network": ForwardRef('Network', module='types')
        key "pointInTimeUtc": str
        key "postgreSqlVersion": Union[str, PostgreSqlVersion]
        key "provisioningState": Required[Union[str, ProvisioningState]]
        key "readWritePool": Required[ReadWritePoolProperties]
        key "state": Required[Union[str, ClusterState]]
        aiModelManagement: Union[str, AiModelManagementStatus]
        backup: BackupProperties
        creationMode: Union[str, ClusterCreateMode]
        creationSourceClusterLocation: str
        creationSourceClusterResourceId: str
        dataEncryption: HorizonDbClusterDataEncryption
        network: Network
        pointInTimeUtc: str
        postgreSqlVersion: Union[str, PostgreSqlVersion]
        provisioningState: Union[str, ProvisioningState]
        readWritePool: ReadWritePoolProperties
        state: Union[str, ClusterState]


    class azure.mgmt.horizondb.types.ClusterPropertiesForPatchUpdate(TypedDict, total=False):
        key "aiModelManagement": Union[str, AiModelManagementStatus]
        key "backup": ForwardRef('BackupPropertiesForPatchUpdate', module='types')
        key "dataEncryption": ForwardRef('HorizonDbClusterDataEncryptionForPatchUpdate', module='types')
        key "network": ForwardRef('NetworkForPatchUpdate', module='types')
        aiModelManagement: Union[str, AiModelManagementStatus]
        backup: BackupPropertiesForPatchUpdate
        dataEncryption: HorizonDbClusterDataEncryptionForPatchUpdate
        network: NetworkForPatchUpdate


    class azure.mgmt.horizondb.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.horizondb.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.horizondb.types.FabricDestinationDetails(TypedDict, total=False):
        key "destinationType": Required[Literal[ChangeDataCaptureDestinationType.FABRIC]]
        key "protocol": Required[Literal[ChangeDataCaptureProtocol.NATIVE]]
        key "workspaceId": Required[str]
        destinationType: Literal[ChangeDataCaptureDestinationType.FABRIC]
        protocol: Literal[ChangeDataCaptureProtocol.NATIVE]
        workspaceId: str


    class azure.mgmt.horizondb.types.FirewallRule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FirewallRuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FirewallRuleProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.FirewallRuleProperties(TypedDict, total=False):
        key "description": str
        key "endIpAddress": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "startIpAddress": Required[str]
        description: str
        endIpAddress: str
        provisioningState: Union[str, ProvisioningState]
        startIpAddress: str


    class azure.mgmt.horizondb.types.HorizonDbClusterDataEncryption(TypedDict, total=False):
        key "primaryEncryptionKeyCurrentVersion": str
        key "primaryEncryptionKeyStatus": Union[str, HorizonDbClusterEncryptionKeyStatus]
        key "primaryKeyUri": str
        key "primaryUserAssignedIdentityId": str
        key "type": Union[str, HorizonDbClusterDataEncryptionType]
        primaryEncryptionKeyCurrentVersion: str
        primaryEncryptionKeyStatus: Union[str, HorizonDbClusterEncryptionKeyStatus]
        primaryKeyUri: str
        primaryUserAssignedIdentityId: str
        type: Union[str, HorizonDbClusterDataEncryptionType]


    class azure.mgmt.horizondb.types.HorizonDbClusterDataEncryptionForPatchUpdate(TypedDict, total=False):
        key "primaryKeyUri": str
        key "primaryUserAssignedIdentityId": str
        key "type": Union[str, HorizonDbClusterDataEncryptionType]
        primaryKeyUri: str
        primaryUserAssignedIdentityId: str
        type: Union[str, HorizonDbClusterDataEncryptionType]


    class azure.mgmt.horizondb.types.HorizonDbClusterManagedServiceIdentity(TypedDict, total=False):
        key "type": Required[Union[str, HorizonDbClusterIdentityType]]
        type: Union[str, HorizonDbClusterIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.horizondb.types.IdentityAssignment(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('ChangeDataCaptureIdentityAssignmentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: ChangeDataCaptureIdentityAssignmentProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.IdentityValidationStatus(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        key "state": Required[Union[str, ChangeDataCaptureIdentityValidationState]]
        key "validatedAtUtc": str
        error: ErrorDetail
        state: Union[str, ChangeDataCaptureIdentityValidationState]
        validatedAtUtc: str


    class azure.mgmt.horizondb.types.LogCaptureConfigurationForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('LogCaptureConfigurationPropertiesForPatchUpdate', module='types')
        properties: LogCaptureConfigurationPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.LogCaptureConfigurationPropertiesForPatchUpdate(TypedDict, total=False):
        key "retentionDays": int
        key "state": Union[str, LogCaptureState]
        retentionDays: int
        state: Union[str, LogCaptureState]


    class azure.mgmt.horizondb.types.MaintenanceEventRescheduleRequest(TypedDict, total=False):
        key "postponeToDateTimeUtc": Required[str]
        postponeToDateTimeUtc: str


    class azure.mgmt.horizondb.types.MicrosoftEntraAdministratorAdd(TypedDict, total=False):
        key "properties": Required[MicrosoftEntraAdministratorPropertiesForAdd]
        properties: MicrosoftEntraAdministratorPropertiesForAdd


    class azure.mgmt.horizondb.types.MicrosoftEntraAdministratorPropertiesForAdd(TypedDict, total=False):
        key "principalName": Required[str]
        key "principalType": Required[Union[str, PrincipalTypes]]
        key "tenantId": str
        principalName: str
        principalType: Union[str, PrincipalTypes]
        tenantId: str


    class azure.mgmt.horizondb.types.MicrosoftEntraAuthentication(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('MicrosoftEntraAuthenticationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MicrosoftEntraAuthenticationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.MicrosoftEntraAuthenticationForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('MicrosoftEntraAuthenticationPropertiesForPatchUpdate', module='types')
        properties: MicrosoftEntraAuthenticationPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.MicrosoftEntraAuthenticationProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Required[Union[str, AuthenticationState]]
        provisioningState: Union[str, ProvisioningState]
        state: Union[str, AuthenticationState]


    class azure.mgmt.horizondb.types.MicrosoftEntraAuthenticationPropertiesForPatchUpdate(TypedDict, total=False):
        key "state": Union[str, AuthenticationState]
        state: Union[str, AuthenticationState]


    class azure.mgmt.horizondb.types.Network(TypedDict, total=False):
        key "publicAccess": Union[str, PublicNetworkAccessState]
        publicAccess: Union[str, PublicNetworkAccessState]


    class azure.mgmt.horizondb.types.NetworkForPatchUpdate(TypedDict, total=False):
        key "publicAccess": Union[str, PublicNetworkAccessState]
        publicAccess: Union[str, PublicNetworkAccessState]


    class azure.mgmt.horizondb.types.ParameterGroup(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ParameterGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ParameterGroupProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.ParameterGroupForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('ParameterGroupPropertiesForPatchUpdate', module='types')
        properties: ParameterGroupPropertiesForPatchUpdate
        tags: dict[str, str]


    class azure.mgmt.horizondb.types.ParameterGroupProperties(TypedDict, total=False):
        key "description": str
        key "postgreSqlVersion": Required[Union[str, PostgreSqlVersion]]
        key "provisioningState": Union[str, ProvisioningState]
        description: str
        parameters: list[ParameterProperties]
        postgreSqlVersion: Union[str, PostgreSqlVersion]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.horizondb.types.ParameterGroupPropertiesForPatchUpdate(TypedDict, total=False):
        key "description": str
        description: str
        parameters: list[ParameterProperties]


    class azure.mgmt.horizondb.types.ParameterProperties(TypedDict, total=False):
        key "allowedValues": str
        key "dataType": str
        key "defaultValue": str
        key "description": str
        key "documentationLink": str
        key "isDynamic": bool
        key "isReadOnly": bool
        key "name": str
        key "unit": str
        key "value": str
        key "valueSource": Union[str, ParameterValueSource]
        allowedValues: str
        dataType: str
        defaultValue: str
        description: str
        documentationLink: str
        isDynamic: bool
        isReadOnly: bool
        name: str
        unit: str
        value: str
        valueSource: Union[str, ParameterValueSource]


    class azure.mgmt.horizondb.types.PasswordAuthentication(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PasswordAuthenticationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PasswordAuthenticationProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.PasswordAuthenticationForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PasswordAuthenticationPropertiesForPatchUpdate', module='types')
        properties: PasswordAuthenticationPropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.PasswordAuthenticationProperties(TypedDict, total=False):
        key "administratorLogin": str
        key "administratorLoginPassword": str
        key "provisioningState": Union[str, ProvisioningState]
        key "state": Required[Union[str, AuthenticationState]]
        administratorLogin: str
        administratorLoginPassword: str
        provisioningState: Union[str, ProvisioningState]
        state: Union[str, AuthenticationState]


    class azure.mgmt.horizondb.types.PasswordAuthenticationPropertiesForPatchUpdate(TypedDict, total=False):
        key "administratorLoginPassword": str
        key "state": Union[str, AuthenticationState]
        administratorLoginPassword: str
        state: Union[str, AuthenticationState]


    class azure.mgmt.horizondb.types.Pool(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PoolProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PoolProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.PoolComputeModel(TypedDict, total=False):
        key "computeGeneration": Required[int]
        key "computeProcessor": Required[Union[str, ComputeProcessorType]]
        key "type": Required[Union[str, PoolComputeModelType]]
        key "vCores": Required[int]
        computeGeneration: int
        computeProcessor: Union[str, ComputeProcessorType]
        type: Union[str, PoolComputeModelType]
        vCores: int


    class azure.mgmt.horizondb.types.PoolComputeModelForPatchUpdate(TypedDict, total=False):
        key "computeGeneration": int
        key "computeProcessor": Union[str, ComputeProcessorType]
        key "type": Union[str, PoolComputeModelType]
        key "vCores": int
        computeGeneration: int
        computeProcessor: Union[str, ComputeProcessorType]
        type: Union[str, PoolComputeModelType]
        vCores: int


    class azure.mgmt.horizondb.types.PoolForPatchUpdate(TypedDict, total=False):
        key "properties": ForwardRef('PoolPropertiesForPatchUpdate', module='types')
        properties: PoolPropertiesForPatchUpdate
        tags: dict[str, str]


    class azure.mgmt.horizondb.types.PoolHighAvailability(TypedDict, total=False):
        key "mode": Required[Union[str, PoolHighAvailabilityMode]]
        mode: Union[str, PoolHighAvailabilityMode]


    class azure.mgmt.horizondb.types.PoolHighAvailabilityPatch(TypedDict, total=False):
        key "mode": Union[str, PoolHighAvailabilityMode]
        mode: Union[str, PoolHighAvailabilityMode]


    class azure.mgmt.horizondb.types.PoolParameterGroupReference(TypedDict, total=False):
        key "applyMethod": Required[Union[str, ParameterApplyMethod]]
        key "parameterGroupResourceId": Required[str]
        key "syncStatus": Union[str, ParameterGroupSyncStatus]
        applyMethod: Union[str, ParameterApplyMethod]
        parameterGroupResourceId: str
        syncStatus: Union[str, ParameterGroupSyncStatus]


    class azure.mgmt.horizondb.types.PoolParameterGroupReferenceForPatchUpdate(TypedDict, total=False):
        key "applyMethod": Union[str, ParameterApplyMethod]
        key "parameterGroupResourceId": str
        applyMethod: Union[str, ParameterApplyMethod]
        parameterGroupResourceId: str


    class azure.mgmt.horizondb.types.PoolProperties(TypedDict, total=False):
        key "computeModel": Required[PoolComputeModel]
        key "highAvailability": Required[PoolHighAvailability]
        key "nodeCount": Required[int]
        key "parameterGroup": Required[PoolParameterGroupReference]
        key "provisioningState": Union[str, ProvisioningState]
        key "scheduledMaintenance": ForwardRef('ScheduledMaintenanceProperties', module='types')
        key "state": Union[str, PoolState]
        computeModel: PoolComputeModel
        highAvailability: PoolHighAvailability
        nodeCount: int
        parameterGroup: PoolParameterGroupReference
        provisioningState: Union[str, ProvisioningState]
        scheduledMaintenance: ScheduledMaintenanceProperties
        state: Union[str, PoolState]


    class azure.mgmt.horizondb.types.PoolPropertiesForPatchUpdate(TypedDict, total=False):
        key "computeModel": ForwardRef('PoolComputeModelForPatchUpdate', module='types')
        key "highAvailability": ForwardRef('PoolHighAvailabilityPatch', module='types')
        key "nodeCount": int
        key "parameterGroup": ForwardRef('PoolParameterGroupReferenceForPatchUpdate', module='types')
        key "scheduledMaintenance": ForwardRef('ScheduledMaintenancePropertiesForPatchUpdate', module='types')
        computeModel: PoolComputeModelForPatchUpdate
        highAvailability: PoolHighAvailabilityPatch
        nodeCount: int
        parameterGroup: PoolParameterGroupReferenceForPatchUpdate
        scheduledMaintenance: ScheduledMaintenancePropertiesForPatchUpdate


    class azure.mgmt.horizondb.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.horizondb.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.horizondb.types.PrivateEndpointConnectionResource(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.horizondb.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.ReadWritePoolProperties(TypedDict, total=False):
        key "designatedPoolResourceId": str
        designatedPoolResourceId: str


    class azure.mgmt.horizondb.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.horizondb.types.ScheduledMaintenanceManagementType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "System"


    class azure.mgmt.horizondb.types.ScheduledMaintenanceProperties(TypedDict, total=False):
        key "maintenanceManagementType": Required[Literal[ScheduledMaintenanceManagementType.SYSTEM]]
        maintenanceManagementType: Literal[ScheduledMaintenanceManagementType.SYSTEM]


    class azure.mgmt.horizondb.types.ScheduledMaintenancePropertiesForPatchUpdate(TypedDict, total=False):
        key "maintenanceManagementType": Union[str, ScheduledMaintenanceManagementType]
        maintenanceManagementType: Union[str, ScheduledMaintenanceManagementType]


    class azure.mgmt.horizondb.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.horizondb.types.SystemScheduledMaintenanceProperties(TypedDict, total=False):
        key "maintenanceManagementType": Required[Literal[ScheduledMaintenanceManagementType.SYSTEM]]
        maintenanceManagementType: Literal[ScheduledMaintenanceManagementType.SYSTEM]


    class azure.mgmt.horizondb.types.TrackedResource(Resource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.horizondb.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```