```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.cdn

    class azure.mgmt.cdn.CdnManagementClient(CdnManagementClientOperationsMixin): implements ContextManager 
        afd_custom_domains: AFDCustomDomainsOperations
        afd_endpoints: AFDEndpointsOperations
        afd_origin_groups: AFDOriginGroupsOperations
        afd_origins: AFDOriginsOperations
        afd_profiles: AFDProfilesOperations
        custom_domains: CustomDomainsOperations
        edge_nodes: EdgeNodesOperations
        endpoints: EndpointsOperations
        log_analytics: LogAnalyticsOperations
        managed_rule_sets: ManagedRuleSetsOperations
        operations: Operations
        origin_groups: OriginGroupsOperations
        origins: OriginsOperations
        policies: PoliciesOperations
        profiles: ProfilesOperations
        resource_usage: ResourceUsageOperations
        routes: RoutesOperations
        rule_sets: RuleSetsOperations
        rules: RulesOperations
        secrets: SecretsOperations
        security_policies: SecurityPoliciesOperations

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

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        def close(self) -> None: ...

        @overload
        def validate_probe(
                self, 
                validate_probe_input: ValidateProbeInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...

        @overload
        def validate_probe(
                self, 
                validate_probe_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...


namespace azure.mgmt.cdn.aio

    class azure.mgmt.cdn.aio.CdnManagementClient(CdnManagementClientOperationsMixin): implements AsyncContextManager 
        afd_custom_domains: AFDCustomDomainsOperations
        afd_endpoints: AFDEndpointsOperations
        afd_origin_groups: AFDOriginGroupsOperations
        afd_origins: AFDOriginsOperations
        afd_profiles: AFDProfilesOperations
        custom_domains: CustomDomainsOperations
        edge_nodes: EdgeNodesOperations
        endpoints: EndpointsOperations
        log_analytics: LogAnalyticsOperations
        managed_rule_sets: ManagedRuleSetsOperations
        operations: Operations
        origin_groups: OriginGroupsOperations
        origins: OriginsOperations
        policies: PoliciesOperations
        profiles: ProfilesOperations
        resource_usage: ResourceUsageOperations
        routes: RoutesOperations
        rule_sets: RuleSetsOperations
        rules: RulesOperations
        secrets: SecretsOperations
        security_policies: SecurityPoliciesOperations

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

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        async def close(self) -> None: ...

        @overload
        async def validate_probe(
                self, 
                validate_probe_input: ValidateProbeInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...

        @overload
        async def validate_probe(
                self, 
                validate_probe_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...


namespace azure.mgmt.cdn.aio.operations

    class azure.mgmt.cdn.aio.operations.AFDCustomDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain: AFDDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDDomain]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_refresh_validation_token(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain_update_properties: AFDDomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDDomain]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDDomain]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AFDDomain: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AFDDomain]: ...


    class azure.mgmt.cdn.aio.operations.AFDEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: AFDEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDEndpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDEndpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                contents: AfdPurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                contents: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: AFDEndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDEndpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDEndpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AFDEndpoint: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AFDEndpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.cdn.aio.operations.AFDOriginGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group: AFDOriginGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOriginGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOriginGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: AFDOriginGroupUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOriginGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOriginGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AFDOriginGroup: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AFDOriginGroup]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.cdn.aio.operations.AFDOriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin: AFDOrigin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOrigin]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOrigin]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin_update_properties: AFDOriginUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOrigin]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AFDOrigin]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> AFDOrigin: ...

        @distributed_trace
        def list_by_origin_group(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AFDOrigin]: ...


    class azure.mgmt.cdn.aio.operations.AFDProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_upgrade_parameters: ProfileUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_upgrade(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_host_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_host_name_availability_input: CheckHostNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_host_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_host_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...

        @overload
        async def validate_secret(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                validate_secret_input: ValidateSecretInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSecretOutput: ...

        @overload
        async def validate_secret(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                validate_secret_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSecretOutput: ...


    class azure.mgmt.cdn.aio.operations.CdnManagementClientOperationsMixin(CdnManagementClientMixinABC):

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        async def validate_probe(
                self, 
                validate_probe_input: ValidateProbeInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...

        @overload
        async def validate_probe(
                self, 
                validate_probe_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...


    class azure.mgmt.cdn.aio.operations.CustomDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_properties: CustomDomainParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @distributed_trace_async
        async def begin_disable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @overload
        async def begin_enable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_https_parameters: Optional[CustomDomainHttpsParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @overload
        async def begin_enable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_https_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomDomain]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> CustomDomain: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[CustomDomain]: ...


    class azure.mgmt.cdn.aio.operations.EdgeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[EdgeNode]: ...


    class azure.mgmt.cdn.aio.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_load_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: LoadParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_load_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: EndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Endpoint]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Endpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ResourceUsage]: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        async def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.cdn.aio.operations.LogAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get_log_analytics_locations(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ContinentsResponse: ...

        @distributed_trace_async
        async def get_log_analytics_metrics(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, LogMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, LogMetricsGranularity], 
                custom_domains: List[str], 
                protocols: List[str], 
                group_by: Optional[List[Union[str, LogMetricsGroupBy]]] = None, 
                continents: Optional[List[str]] = None, 
                country_or_regions: Optional[List[str]] = None, 
                **kwargs: Any
            ) -> MetricsResponse: ...

        @distributed_trace_async
        async def get_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rankings: List[Union[str, LogRanking]], 
                metrics: List[Union[str, LogRankingMetric]], 
                max_ranking: int, 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                custom_domains: Optional[List[str]] = None, 
                **kwargs: Any
            ) -> RankingsResponse: ...

        @distributed_trace_async
        async def get_log_analytics_resources(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ResourcesResponse: ...

        @distributed_trace_async
        async def get_waf_log_analytics_metrics(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, WafMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, WafGranularity], 
                actions: Optional[List[Union[str, WafAction]]] = None, 
                group_by: Optional[List[Union[str, WafRankingGroupBy]]] = None, 
                rule_types: Optional[List[Union[str, WafRuleType]]] = None, 
                **kwargs: Any
            ) -> WafMetricsResponse: ...

        @distributed_trace_async
        async def get_waf_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, WafMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                rankings: List[Union[str, WafRankingType]], 
                actions: Optional[List[Union[str, WafAction]]] = None, 
                rule_types: Optional[List[Union[str, WafRuleType]]] = None, 
                **kwargs: Any
            ) -> WafRankingsResponse: ...


    class azure.mgmt.cdn.aio.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ManagedRuleSetDefinition]: ...


    class azure.mgmt.cdn.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.cdn.aio.operations.OriginGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group: OriginGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OriginGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OriginGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: OriginGroupUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OriginGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[OriginGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> OriginGroup: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[OriginGroup]: ...


    class azure.mgmt.cdn.aio.operations.OriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin: Origin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Origin]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Origin]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin_update_properties: OriginUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Origin]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Origin]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> Origin: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Origin]: ...


    class azure.mgmt.cdn.aio.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy: CdnWebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy_patch_parameters: CdnWebApplicationFirewallPolicyPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy_patch_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CdnWebApplicationFirewallPolicy]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> CdnWebApplicationFirewallPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[CdnWebApplicationFirewallPolicy]: ...


    class azure.mgmt.cdn.aio.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_can_migrate(
                self, 
                resource_group_name: str, 
                can_migrate_parameters: CanMigrateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CanMigrateResult]: ...

        @overload
        async def begin_can_migrate(
                self, 
                resource_group_name: str, 
                can_migrate_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CanMigrateResult]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                migration_parameters: MigrationParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateResult]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                migration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateResult]: ...

        @distributed_trace_async
        async def begin_migration_commit(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_update_parameters: ProfileUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Profile]: ...

        @distributed_trace_async
        async def generate_sso_uri(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> SsoUri: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Profile]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[ResourceUsage]: ...

        @distributed_trace_async
        async def list_supported_optimization_types(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> SupportedOptimizationTypesListResult: ...


    class azure.mgmt.cdn.aio.operations.ResourceUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ResourceUsage]: ...


    class azure.mgmt.cdn.aio.operations.RoutesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route: Route, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Route]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Route]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route_update_properties: RouteUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Route]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Route]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                **kwargs: Any
            ) -> Route: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Route]: ...


    class azure.mgmt.cdn.aio.operations.RuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> RuleSet: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> RuleSet: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[RuleSet]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Usage]: ...


    class azure.mgmt.cdn.aio.operations.RulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Rule]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Rule]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule_update_properties: RuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Rule]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Rule]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list_by_rule_set(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Rule]: ...


    class azure.mgmt.cdn.aio.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                secret: Secret, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Secret]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                secret: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Secret]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Secret]: ...


    class azure.mgmt.cdn.aio.operations.SecurityPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy_update_properties: SecurityPolicyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @overload
        async def begin_patch(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SecurityPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SecurityPolicy]: ...


namespace azure.mgmt.cdn.models

    class azure.mgmt.cdn.models.AFDDomain(ProxyResource):
        azure_dns_zone: ResourceReference
        deployment_status: Union[str, DeploymentStatus]
        domain_validation_state: Union[str, DomainValidationState]
        extended_properties: dict[str, str]
        host_name: str
        id: str
        name: str
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        system_data: SystemData
        tls_settings: AFDDomainHttpsParameters
        type: str
        validation_properties: DomainValidationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                extended_properties: Optional[Dict[str, str]] = ..., 
                host_name: Optional[str] = ..., 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDDomainHttpsParameters(Model):
        certificate_type: Union[str, AfdCertificateType]
        minimum_tls_version: Union[str, AfdMinimumTlsVersion]
        secret: ResourceReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_type: Union[str, AfdCertificateType], 
                minimum_tls_version: Optional[Union[str, AfdMinimumTlsVersion]] = ..., 
                secret: Optional[ResourceReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDDomainListResult(Model):
        next_link: str
        value: list[AFDDomain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDDomainProperties(AFDDomainUpdatePropertiesParameters, AFDStateProperties):
        azure_dns_zone: ResourceReference
        deployment_status: Union[str, DeploymentStatus]
        domain_validation_state: Union[str, DomainValidationState]
        extended_properties: dict[str, str]
        host_name: str
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        tls_settings: AFDDomainHttpsParameters
        validation_properties: DomainValidationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                extended_properties: Optional[Dict[str, str]] = ..., 
                host_name: str, 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDDomainUpdateParameters(Model):
        azure_dns_zone: ResourceReference
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        tls_settings: AFDDomainHttpsParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDDomainUpdatePropertiesParameters(Model):
        azure_dns_zone: ResourceReference
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        tls_settings: AFDDomainHttpsParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDEndpoint(TrackedResource):
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        host_name: str
        id: str
        location: str
        name: str
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDEndpointListResult(Model):
        next_link: str
        value: list[AFDEndpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDEndpointProperties(AFDEndpointPropertiesUpdateParameters, AFDStateProperties):
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        host_name: str
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDEndpointPropertiesUpdateParameters(Model):
        enabled_state: Union[str, EnabledState]
        profile_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDEndpointProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.cdn.models.AFDEndpointUpdateParameters(Model):
        enabled_state: Union[str, EnabledState]
        profile_name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOrigin(ProxyResource):
        azure_origin: ResourceReference
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        enforce_certificate_name_check: bool
        host_name: str
        http_port: int
        https_port: int
        id: str
        name: str
        origin_group_name: str
        origin_host_header: str
        priority: int
        provisioning_state: Union[str, AfdProvisioningState]
        shared_private_link_resource: SharedPrivateLinkResourceProperties
        system_data: SystemData
        type: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: bool = True, 
                host_name: Optional[str] = ..., 
                http_port: int = 80, 
                https_port: int = 443, 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginGroup(ProxyResource):
        deployment_status: Union[str, DeploymentStatus]
        health_probe_settings: HealthProbeParameters
        id: str
        load_balancing_settings: LoadBalancingSettingsParameters
        name: str
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        session_affinity_state: Union[str, EnabledState]
        system_data: SystemData
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginGroupListResult(Model):
        next_link: str
        value: list[AFDOriginGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginGroupProperties(AFDOriginGroupUpdatePropertiesParameters, AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        health_probe_settings: HealthProbeParameters
        load_balancing_settings: LoadBalancingSettingsParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        session_affinity_state: Union[str, EnabledState]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginGroupUpdateParameters(Model):
        health_probe_settings: HealthProbeParameters
        load_balancing_settings: LoadBalancingSettingsParameters
        profile_name: str
        session_affinity_state: Union[str, EnabledState]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginGroupUpdatePropertiesParameters(Model):
        health_probe_settings: HealthProbeParameters
        load_balancing_settings: LoadBalancingSettingsParameters
        profile_name: str
        session_affinity_state: Union[str, EnabledState]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginListResult(Model):
        next_link: str
        value: list[AFDOrigin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginProperties(AFDOriginUpdatePropertiesParameters, AFDStateProperties):
        azure_origin: ResourceReference
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        enforce_certificate_name_check: bool
        host_name: str
        http_port: int
        https_port: int
        origin_group_name: str
        origin_host_header: str
        priority: int
        provisioning_state: Union[str, AfdProvisioningState]
        shared_private_link_resource: SharedPrivateLinkResourceProperties
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: bool = True, 
                host_name: Optional[str] = ..., 
                http_port: int = 80, 
                https_port: int = 443, 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginUpdateParameters(Model):
        azure_origin: ResourceReference
        enabled_state: Union[str, EnabledState]
        enforce_certificate_name_check: bool
        host_name: str
        http_port: int
        https_port: int
        origin_group_name: str
        origin_host_header: str
        priority: int
        shared_private_link_resource: SharedPrivateLinkResourceProperties
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: bool = True, 
                host_name: Optional[str] = ..., 
                http_port: int = 80, 
                https_port: int = 443, 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDOriginUpdatePropertiesParameters(Model):
        azure_origin: ResourceReference
        enabled_state: Union[str, EnabledState]
        enforce_certificate_name_check: bool
        host_name: str
        http_port: int
        https_port: int
        origin_group_name: str
        origin_host_header: str
        priority: int
        shared_private_link_resource: SharedPrivateLinkResourceProperties
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: bool = True, 
                host_name: Optional[str] = ..., 
                http_port: int = 80, 
                https_port: int = 443, 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AFDStateProperties(Model):
        deployment_status: Union[str, DeploymentStatus]
        provisioning_state: Union[str, AfdProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        BLOCK = "Block"
        LOG = "Log"
        REDIRECT = "Redirect"


    class azure.mgmt.cdn.models.ActivatedResourceReference(Model):
        id: str
        is_active: bool

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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AfdCertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIRST_PARTY_MANAGED_CERTIFICATE = "AzureFirstPartyManagedCertificate"
        CUSTOMER_CERTIFICATE = "CustomerCertificate"
        MANAGED_CERTIFICATE = "ManagedCertificate"


    class azure.mgmt.cdn.models.AfdErrorResponse(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AfdMinimumTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS10 = "TLS10"
        TLS12 = "TLS12"


    class azure.mgmt.cdn.models.AfdProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.AfdPurgeParameters(Model):
        content_paths: list[str]
        domains: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_paths: List[str], 
                domains: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AfdQueryStringCachingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE_QUERY_STRING = "IgnoreQueryString"
        IGNORE_SPECIFIED_QUERY_STRINGS = "IgnoreSpecifiedQueryStrings"
        INCLUDE_SPECIFIED_QUERY_STRINGS = "IncludeSpecifiedQueryStrings"
        USE_QUERY_STRING = "UseQueryString"


    class azure.mgmt.cdn.models.AfdRouteCacheConfiguration(Model):
        compression_settings: CompressionSettings
        query_parameters: str
        query_string_caching_behavior: Union[str, AfdQueryStringCachingBehavior]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                compression_settings: Optional[CompressionSettings] = ..., 
                query_parameters: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, AfdQueryStringCachingBehavior]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Algorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHA256 = "SHA256"


    class azure.mgmt.cdn.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.cdn.models.AzureFirstPartyManagedCertificate(Certificate):
        expiration_date: str
        subject: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SecretType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.AzureFirstPartyManagedCertificateParameters(SecretParameters):
        certificate_authority: str
        expiration_date: str
        secret_source: ResourceReference
        subject: str
        subject_alternative_names: list[str]
        thumbprint: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                subject_alternative_names: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CacheBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS_CACHE = "BypassCache"
        OVERRIDE = "Override"
        SET_IF_MISSING = "SetIfMissing"


    class azure.mgmt.cdn.models.CacheConfiguration(Model):
        cache_behavior: Union[str, RuleCacheBehavior]
        cache_duration: str
        is_compression_enabled: Union[str, RuleIsCompressionEnabled]
        query_parameters: str
        query_string_caching_behavior: Union[str, RuleQueryStringCachingBehavior]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_behavior: Optional[Union[str, RuleCacheBehavior]] = ..., 
                cache_duration: Optional[str] = ..., 
                is_compression_enabled: Optional[Union[str, RuleIsCompressionEnabled]] = ..., 
                query_parameters: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, RuleQueryStringCachingBehavior]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CacheExpirationActionParameters(Model):
        cache_behavior: Union[str, CacheBehavior]
        cache_duration: str
        cache_type: Union[str, CacheType]
        type_name: Union[str, CacheExpirationActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_behavior: Union[str, CacheBehavior], 
                cache_duration: Optional[str] = ..., 
                cache_type: Union[str, CacheType], 
                type_name: Union[str, CacheExpirationActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CacheExpirationActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS = "DeliveryRuleCacheExpirationActionParameters"


    class azure.mgmt.cdn.models.CacheKeyQueryStringActionParameters(Model):
        query_parameters: str
        query_string_behavior: Union[str, QueryStringBehavior]
        type_name: Union[str, CacheKeyQueryStringActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query_parameters: Optional[str] = ..., 
                query_string_behavior: Union[str, QueryStringBehavior], 
                type_name: Union[str, CacheKeyQueryStringActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CacheKeyQueryStringActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS = "DeliveryRuleCacheKeyQueryStringBehaviorActionParameters"


    class azure.mgmt.cdn.models.CacheType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"


    class azure.mgmt.cdn.models.CanMigrateDefaultSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_AZURE_FRONT_DOOR = "Premium_AzureFrontDoor"
        STANDARD_AZURE_FRONT_DOOR = "Standard_AzureFrontDoor"


    class azure.mgmt.cdn.models.CanMigrateParameters(Model):
        classic_resource_reference: ResourceReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                classic_resource_reference: ResourceReference, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CanMigrateResult(Model):
        can_migrate: bool
        default_sku: Union[str, CanMigrateDefaultSku]
        errors: list[MigrationErrorType]
        id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                errors: Optional[List[MigrationErrorType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnCertificateSourceParameters(Model):
        certificate_type: Union[str, CertificateType]
        type_name: Union[str, CdnCertificateSourceParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_type: Union[str, CertificateType], 
                type_name: Union[str, CdnCertificateSourceParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnCertificateSourceParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDN_CERTIFICATE_SOURCE_PARAMETERS = "CdnCertificateSourceParameters"


    class azure.mgmt.cdn.models.CdnEndpoint(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnManagedHttpsParameters(CustomDomainHttpsParameters):
        certificate_source: Union[str, CertificateSource]
        certificate_source_parameters: CdnCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_source_parameters: CdnCertificateSourceParameters, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicy(TrackedResource):
        custom_rules: CustomRuleList
        endpoint_links: list[CdnEndpoint]
        etag: str
        extended_properties: dict[str, str]
        id: str
        location: str
        managed_rules: ManagedRuleSetList
        name: str
        policy_settings: PolicySettings
        provisioning_state: Union[str, ProvisioningState]
        rate_limit_rules: RateLimitRuleList
        resource_state: Union[str, PolicyResourceState]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_rules: Optional[CustomRuleList] = ..., 
                etag: Optional[str] = ..., 
                extended_properties: Optional[Dict[str, str]] = ..., 
                location: str, 
                managed_rules: Optional[ManagedRuleSetList] = ..., 
                policy_settings: Optional[PolicySettings] = ..., 
                rate_limit_rules: Optional[RateLimitRuleList] = ..., 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicyList(Model):
        next_link: str
        value: list[CdnWebApplicationFirewallPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicyPatchParameters(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Certificate(Model):
        expiration_date: str
        subject: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SecretType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CertificateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        CDN = "Cdn"


    class azure.mgmt.cdn.models.CertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"
        SHARED = "Shared"


    class azure.mgmt.cdn.models.CheckEndpointNameAvailabilityInput(Model):
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        name: str
        type: Union[str, ResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                name: str, 
                type: Union[str, ResourceType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CheckEndpointNameAvailabilityOutput(Model):
        available_hostname: str
        message: str
        name_available: bool
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CheckHostNameAvailabilityInput(Model):
        host_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CheckNameAvailabilityInput(Model):
        name: str
        type: Union[str, ResourceType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ResourceType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CheckNameAvailabilityOutput(Model):
        message: str
        name_available: bool
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CidrIpAddress(Model):
        base_ip_address: str
        prefix_length: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                base_ip_address: Optional[str] = ..., 
                prefix_length: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ClientPortMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, ClientPortOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, ClientPortMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, ClientPortOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, ClientPortMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ClientPortMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS = "DeliveryRuleClientPortConditionParameters"


    class azure.mgmt.cdn.models.ClientPortOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems(Model):
        date_time: datetime
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date_time: Optional[datetime] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems(Model):
        date_time: datetime
        value: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date_time: Optional[datetime] = ..., 
                value: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems(Model):
        metric: str
        percentage: float
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric: Optional[str] = ..., 
                percentage: Optional[float] = ..., 
                value: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CompressionSettings(Model):
        content_types_to_compress: list[str]
        is_compression_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[List[str]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ContinentsResponse(Model):
        continents: list[ContinentsResponseContinentsItem]
        country_or_regions: list[ContinentsResponseCountryOrRegionsItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                continents: Optional[List[ContinentsResponseContinentsItem]] = ..., 
                country_or_regions: Optional[List[ContinentsResponseCountryOrRegionsItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ContinentsResponseContinentsItem(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ContinentsResponseCountryOrRegionsItem(Model):
        continent_id: str
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                continent_id: Optional[str] = ..., 
                id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CookiesMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, CookiesOperator]
        selector: str
        transforms: Union[list[str, Transform]]
        type_name: Union[str, CookiesMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, CookiesOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, CookiesMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CookiesMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS = "DeliveryRuleCookiesConditionParameters"


    class azure.mgmt.cdn.models.CookiesOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.CustomDomain(ProxyResource):
        custom_https_parameters: CustomDomainHttpsParameters
        custom_https_provisioning_state: Union[str, CustomHttpsProvisioningState]
        custom_https_provisioning_substate: Union[str, CustomHttpsProvisioningSubstate]
        host_name: str
        id: str
        name: str
        provisioning_state: Union[str, CustomHttpsProvisioningState]
        resource_state: Union[str, CustomDomainResourceState]
        system_data: SystemData
        type: str
        validation_data: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_https_parameters: Optional[CustomDomainHttpsParameters] = ..., 
                host_name: Optional[str] = ..., 
                validation_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomDomainHttpsParameters(Model):
        certificate_source: Union[str, CertificateSource]
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomDomainListResult(Model):
        next_link: str
        value: list[CustomDomain]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomDomainParameters(Model):
        host_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomDomainResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"


    class azure.mgmt.cdn.models.CustomHttpsProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"
        FAILED = "Failed"


    class azure.mgmt.cdn.models.CustomHttpsProvisioningSubstate(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE_DELETED = "CertificateDeleted"
        CERTIFICATE_DEPLOYED = "CertificateDeployed"
        DELETING_CERTIFICATE = "DeletingCertificate"
        DEPLOYING_CERTIFICATE = "DeployingCertificate"
        DOMAIN_CONTROL_VALIDATION_REQUEST_APPROVED = "DomainControlValidationRequestApproved"
        DOMAIN_CONTROL_VALIDATION_REQUEST_REJECTED = "DomainControlValidationRequestRejected"
        DOMAIN_CONTROL_VALIDATION_REQUEST_TIMED_OUT = "DomainControlValidationRequestTimedOut"
        ISSUING_CERTIFICATE = "IssuingCertificate"
        PENDING_DOMAIN_CONTROL_VALIDATION_R_EQUEST_APPROVAL = "PendingDomainControlValidationREquestApproval"
        SUBMITTING_DOMAIN_CONTROL_VALIDATION_REQUEST = "SubmittingDomainControlValidationRequest"


    class azure.mgmt.cdn.models.CustomRule(Model):
        action: Union[str, ActionType]
        enabled_state: Union[str, CustomRuleEnabledState]
        match_conditions: list[MatchCondition]
        name: str
        priority: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, ActionType], 
                enabled_state: Optional[Union[str, CustomRuleEnabledState]] = ..., 
                match_conditions: List[MatchCondition], 
                name: str, 
                priority: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.CustomRuleList(Model):
        rules: list[CustomRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rules: Optional[List[CustomRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomerCertificate(Certificate):
        certificate_authority: str
        expiration_date: str
        secret_source: ResourceReference
        secret_version: str
        subject: str
        subject_alternative_names: list[str]
        thumbprint: str
        type: Union[str, SecretType]
        use_latest_version: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secret_source: Optional[ResourceReference] = ..., 
                secret_version: Optional[str] = ..., 
                subject_alternative_names: Optional[List[str]] = ..., 
                type: Optional[Union[str, SecretType]] = ..., 
                use_latest_version: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.CustomerCertificateParameters(SecretParameters):
        certificate_authority: str
        expiration_date: str
        secret_source: ResourceReference
        secret_version: str
        subject: str
        subject_alternative_names: list[str]
        thumbprint: str
        type: Union[str, SecretType]
        use_latest_version: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secret_source: ResourceReference, 
                secret_version: Optional[str] = ..., 
                subject_alternative_names: Optional[List[str]] = ..., 
                use_latest_version: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeepCreatedCustomDomain(Model):
        host_name: str
        name: str
        validation_data: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_name: Optional[str] = ..., 
                name: str, 
                validation_data: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeepCreatedOrigin(Model):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        name: str
        origin_host_header: str
        priority: int
        private_endpoint_status: Union[str, PrivateEndpointStatus]
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                name: str, 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeepCreatedOriginGroup(Model):
        health_probe_settings: HealthProbeParameters
        name: str
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                name: str, 
                origins: Optional[List[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeleteRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACTION = "NoAction"


    class azure.mgmt.cdn.models.DeliveryRule(Model):
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        name: str
        order: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: List[DeliveryRuleAction], 
                conditions: Optional[List[DeliveryRuleCondition]] = ..., 
                name: Optional[str] = ..., 
                order: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleAction(Model):
        name: Union[str, DeliveryRuleActionEnum]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_EXPIRATION = "CacheExpiration"
        CACHE_KEY_QUERY_STRING = "CacheKeyQueryString"
        MODIFY_REQUEST_HEADER = "ModifyRequestHeader"
        MODIFY_RESPONSE_HEADER = "ModifyResponseHeader"
        ORIGIN_GROUP_OVERRIDE = "OriginGroupOverride"
        ROUTE_CONFIGURATION_OVERRIDE = "RouteConfigurationOverride"
        URL_REDIRECT = "UrlRedirect"
        URL_REWRITE = "UrlRewrite"
        URL_SIGNING = "UrlSigning"


    class azure.mgmt.cdn.models.DeliveryRuleCacheExpirationAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: CacheExpirationActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: CacheExpirationActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleCacheKeyQueryStringAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: CacheKeyQueryStringActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: CacheKeyQueryStringActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleClientPortCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: ClientPortMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: ClientPortMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleCondition(Model):
        name: Union[str, MatchVariable]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleCookiesCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: CookiesMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: CookiesMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleHostNameCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: HostNameMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: HostNameMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleHttpVersionCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: HttpVersionMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: HttpVersionMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleIsDeviceCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: IsDeviceMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: IsDeviceMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRulePostArgsCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: PostArgsMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: PostArgsMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleQueryStringCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: QueryStringMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: QueryStringMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRemoteAddressCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RemoteAddressMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RemoteAddressMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestBodyCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RequestBodyMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RequestBodyMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestHeaderAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: HeaderActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: HeaderActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestHeaderCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RequestHeaderMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RequestHeaderMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestMethodCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RequestMethodMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RequestMethodMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestSchemeCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RequestSchemeMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RequestSchemeMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRequestUriCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: RequestUriMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RequestUriMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleResponseHeaderAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: HeaderActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: HeaderActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleRouteConfigurationOverrideAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: RouteConfigurationOverrideActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: RouteConfigurationOverrideActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleServerPortCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: ServerPortMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: ServerPortMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleSocketAddrCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: SocketAddrMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: SocketAddrMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleSslProtocolCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: SslProtocolMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: SslProtocolMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleUrlFileExtensionCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: UrlFileExtensionMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlFileExtensionMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleUrlFileNameCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: UrlFileNameMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlFileNameMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeliveryRuleUrlPathCondition(DeliveryRuleCondition):
        name: Union[str, MatchVariable]
        parameters: UrlPathMatchConditionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlPathMatchConditionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DeploymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cdn.models.DestinationProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.cdn.models.DimensionProperties(Model):
        display_name: str
        internal_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DomainValidationProperties(Model):
        expiration_date: str
        validation_token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.DomainValidationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        INTERNAL_ERROR = "InternalError"
        PENDING = "Pending"
        PENDING_REVALIDATION = "PendingRevalidation"
        REFRESHING_VALIDATION_TOKEN = "RefreshingValidationToken"
        REJECTED = "Rejected"
        SUBMITTING = "Submitting"
        TIMED_OUT = "TimedOut"
        UNKNOWN = "Unknown"


    class azure.mgmt.cdn.models.EdgeNode(ProxyResource):
        id: str
        ip_address_groups: list[IpAddressGroup]
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_address_groups: Optional[List[IpAddressGroup]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EdgenodeResult(Model):
        next_link: str
        value: list[EdgeNode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.Endpoint(TrackedResource):
        content_types_to_compress: list[str]
        custom_domains: list[DeepCreatedCustomDomain]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geo_filters: list[GeoFilter]
        host_name: str
        id: str
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        location: str
        name: str
        optimization_type: Union[str, OptimizationType]
        origin_groups: list[DeepCreatedOriginGroup]
        origin_host_header: str
        origin_path: str
        origins: list[DeepCreatedOrigin]
        probe_path: str
        provisioning_state: Union[str, EndpointProvisioningState]
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        resource_state: Union[str, EndpointResourceState]
        system_data: SystemData
        tags: dict[str, str]
        type: str
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[List[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[List[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: bool = True, 
                is_https_allowed: bool = True, 
                location: str, 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_groups: Optional[List[DeepCreatedOriginGroup]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                origins: Optional[List[DeepCreatedOrigin]] = ..., 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                url_signing_keys: Optional[List[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointListResult(Model):
        next_link: str
        value: list[Endpoint]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointProperties(EndpointPropertiesUpdateParameters):
        content_types_to_compress: list[str]
        custom_domains: list[DeepCreatedCustomDomain]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geo_filters: list[GeoFilter]
        host_name: str
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        origin_groups: list[DeepCreatedOriginGroup]
        origin_host_header: str
        origin_path: str
        origins: list[DeepCreatedOrigin]
        probe_path: str
        provisioning_state: Union[str, EndpointProvisioningState]
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        resource_state: Union[str, EndpointResourceState]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[List[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[List[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: bool = True, 
                is_https_allowed: bool = True, 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_groups: Optional[List[DeepCreatedOriginGroup]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                origins: List[DeepCreatedOrigin], 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                url_signing_keys: Optional[List[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParameters(Model):
        content_types_to_compress: list[str]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geo_filters: list[GeoFilter]
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        origin_host_header: str
        origin_path: str
        probe_path: str
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[List[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[List[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: bool = True, 
                is_https_allowed: bool = True, 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                url_signing_keys: Optional[List[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParametersDeliveryPolicy(Model):
        description: str
        rules: list[DeliveryRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                rules: List[DeliveryRule], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.EndpointProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.EndpointResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"


    class azure.mgmt.cdn.models.EndpointUpdateParameters(Model):
        content_types_to_compress: list[str]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geo_filters: list[GeoFilter]
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        origin_host_header: str
        origin_path: str
        probe_path: str
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        tags: dict[str, str]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[List[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[List[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: bool = True, 
                is_https_allowed: bool = True, 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                url_signing_keys: Optional[List[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ErrorDetail(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ErrorResponse(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ForwardingProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS_ONLY = "HttpsOnly"
        HTTP_ONLY = "HttpOnly"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.cdn.models.GeoFilter(Model):
        action: Union[str, GeoFilterActions]
        country_codes: list[str]
        relative_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, GeoFilterActions], 
                country_codes: List[str], 
                relative_path: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.GeoFilterActions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        BLOCK = "Block"


    class azure.mgmt.cdn.models.HeaderAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPEND = "Append"
        DELETE = "Delete"
        OVERWRITE = "Overwrite"


    class azure.mgmt.cdn.models.HeaderActionParameters(Model):
        header_action: Union[str, HeaderAction]
        header_name: str
        type_name: Union[str, HeaderActionParametersTypeName]
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                header_action: Union[str, HeaderAction], 
                header_name: str, 
                type_name: Union[str, HeaderActionParametersTypeName], 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.HeaderActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_HEADER_ACTION_PARAMETERS = "DeliveryRuleHeaderActionParameters"


    class azure.mgmt.cdn.models.HealthProbeParameters(Model):
        probe_interval_in_seconds: int
        probe_path: str
        probe_protocol: Union[str, ProbeProtocol]
        probe_request_type: Union[str, HealthProbeRequestType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                probe_interval_in_seconds: Optional[int] = ..., 
                probe_path: Optional[str] = ..., 
                probe_protocol: Optional[Union[str, ProbeProtocol]] = ..., 
                probe_request_type: Optional[Union[str, HealthProbeRequestType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.HealthProbeRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GET = "GET"
        HEAD = "HEAD"
        NOT_SET = "NotSet"


    class azure.mgmt.cdn.models.HostNameMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, HostNameOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, HostNameMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, HostNameOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, HostNameMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.HostNameMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS = "DeliveryRuleHostNameConditionParameters"


    class azure.mgmt.cdn.models.HostNameOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.HttpErrorRangeParameters(Model):
        begin: int
        end: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                begin: Optional[int] = ..., 
                end: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.HttpVersionMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, HttpVersionOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, HttpVersionMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, HttpVersionOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, HttpVersionMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.HttpVersionMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS = "DeliveryRuleHttpVersionConditionParameters"


    class azure.mgmt.cdn.models.HttpVersionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.HttpsRedirect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "application"
        KEY = "key"
        MANAGED_IDENTITY = "managedIdentity"
        USER = "user"


    class azure.mgmt.cdn.models.IpAddressGroup(Model):
        delivery_region: str
        ipv4_addresses: list[CidrIpAddress]
        ipv6_addresses: list[CidrIpAddress]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delivery_region: Optional[str] = ..., 
                ipv4_addresses: Optional[List[CidrIpAddress]] = ..., 
                ipv6_addresses: Optional[List[CidrIpAddress]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.IsDeviceMatchConditionParameters(Model):
        match_values: Union[list[str, IsDeviceMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, IsDeviceOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, IsDeviceMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[Union[str, IsDeviceMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, IsDeviceOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, IsDeviceMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.IsDeviceMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESKTOP = "Desktop"
        MOBILE = "Mobile"


    class azure.mgmt.cdn.models.IsDeviceMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS = "DeliveryRuleIsDeviceConditionParameters"


    class azure.mgmt.cdn.models.IsDeviceOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.KeyVaultCertificateSourceParameters(Model):
        delete_rule: Union[str, DeleteRule]
        resource_group_name: str
        secret_name: str
        secret_version: str
        subscription_id: str
        type_name: Union[str, KeyVaultCertificateSourceParametersTypeName]
        update_rule: Union[str, UpdateRule]
        vault_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                delete_rule: Union[str, DeleteRule], 
                resource_group_name: str, 
                secret_name: str, 
                secret_version: Optional[str] = ..., 
                subscription_id: str, 
                type_name: Union[str, KeyVaultCertificateSourceParametersTypeName], 
                update_rule: Union[str, UpdateRule], 
                vault_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.KeyVaultCertificateSourceParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS = "KeyVaultCertificateSourceParameters"


    class azure.mgmt.cdn.models.KeyVaultSigningKeyParameters(Model):
        resource_group_name: str
        secret_name: str
        secret_version: str
        subscription_id: str
        type_name: Union[str, KeyVaultSigningKeyParametersTypeName]
        vault_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                resource_group_name: str, 
                secret_name: str, 
                secret_version: str, 
                subscription_id: str, 
                type_name: Union[str, KeyVaultSigningKeyParametersTypeName], 
                vault_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.KeyVaultSigningKeyParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_SIGNING_KEY_PARAMETERS = "KeyVaultSigningKeyParameters"


    class azure.mgmt.cdn.models.LinkToDefaultDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.LoadBalancingSettingsParameters(Model):
        additional_latency_in_milliseconds: int
        sample_size: int
        successful_samples_required: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_latency_in_milliseconds: Optional[int] = ..., 
                sample_size: Optional[int] = ..., 
                successful_samples_required: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.LoadParameters(Model):
        content_paths: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_paths: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.LogMetric(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_REQUEST_BANDWIDTH = "clientRequestBandwidth"
        CLIENT_REQUEST_COUNT = "clientRequestCount"
        CLIENT_REQUEST_TRAFFIC = "clientRequestTraffic"
        ORIGIN_REQUEST_BANDWIDTH = "originRequestBandwidth"
        ORIGIN_REQUEST_TRAFFIC = "originRequestTraffic"
        TOTAL_LATENCY = "totalLatency"


    class azure.mgmt.cdn.models.LogMetricsGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_D = "P1D"
        PT1_H = "PT1H"
        PT5_M = "PT5M"


    class azure.mgmt.cdn.models.LogMetricsGroupBy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_STATUS = "cacheStatus"
        COUNTRY_OR_REGION = "countryOrRegion"
        CUSTOM_DOMAIN = "customDomain"
        HTTP_STATUS_CODE = "httpStatusCode"
        PROTOCOL = "protocol"


    class azure.mgmt.cdn.models.LogRanking(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROWSER = "browser"
        COUNTRY_OR_REGION = "countryOrRegion"
        REFERRER = "referrer"
        URL = "url"
        USER_AGENT = "userAgent"


    class azure.mgmt.cdn.models.LogRankingMetric(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_REQUEST_COUNT = "clientRequestCount"
        CLIENT_REQUEST_TRAFFIC = "clientRequestTraffic"
        ERROR_COUNT = "errorCount"
        HIT_COUNT = "hitCount"
        MISS_COUNT = "missCount"
        USER_ERROR_COUNT = "userErrorCount"


    class azure.mgmt.cdn.models.LogSpecification(Model):
        blob_duration: str
        display_name: str
        log_filter_pattern: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                log_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedCertificate(Certificate):
        expiration_date: str
        subject: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, SecretType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedCertificateParameters(SecretParameters):
        expiration_date: str
        subject: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleDefinition(Model):
        description: str
        rule_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.ManagedRuleGroupDefinition(Model):
        description: str
        rule_group_name: str
        rules: list[ManagedRuleDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleGroupOverride(Model):
        rule_group_name: str
        rules: list[ManagedRuleOverride]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rule_group_name: str, 
                rules: Optional[List[ManagedRuleOverride]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleOverride(Model):
        action: Union[str, ActionType]
        enabled_state: Union[str, ManagedRuleEnabledState]
        rule_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ActionType]] = ..., 
                enabled_state: Optional[Union[str, ManagedRuleEnabledState]] = ..., 
                rule_id: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleSet(Model):
        anomaly_score: int
        rule_group_overrides: list[ManagedRuleGroupOverride]
        rule_set_type: str
        rule_set_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                anomaly_score: Optional[int] = ..., 
                rule_group_overrides: Optional[List[ManagedRuleGroupOverride]] = ..., 
                rule_set_type: str, 
                rule_set_version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleSetDefinition(Resource):
        id: str
        name: str
        provisioning_state: str
        rule_groups: list[ManagedRuleGroupDefinition]
        rule_set_type: str
        rule_set_version: str
        sku: Sku
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sku: Optional[Sku] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleSetDefinitionList(Model):
        next_link: str
        value: list[ManagedRuleSetDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedRuleSetList(Model):
        managed_rule_sets: list[ManagedRuleSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_rule_sets: Optional[List[ManagedRuleSet]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cdn.models.MatchCondition(Model):
        match_value: list[str]
        match_variable: Union[str, WafMatchVariable]
        negate_condition: bool
        operator: Union[str, Operator]
        selector: str
        transforms: Union[list[str, TransformType]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_value: List[str], 
                match_variable: Union[str, WafMatchVariable], 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, Operator], 
                selector: Optional[str] = ..., 
                transforms: Optional[List[Union[str, TransformType]]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MatchProcessingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_ENUM = "Continue"
        STOP = "Stop"


    class azure.mgmt.cdn.models.MatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_PORT = "ClientPort"
        COOKIES = "Cookies"
        HOST_NAME = "HostName"
        HTTP_VERSION = "HttpVersion"
        IS_DEVICE = "IsDevice"
        POST_ARGS = "PostArgs"
        QUERY_STRING = "QueryString"
        REMOTE_ADDRESS = "RemoteAddress"
        REQUEST_BODY = "RequestBody"
        REQUEST_HEADER = "RequestHeader"
        REQUEST_METHOD = "RequestMethod"
        REQUEST_SCHEME = "RequestScheme"
        REQUEST_URI = "RequestUri"
        SERVER_PORT = "ServerPort"
        SOCKET_ADDR = "SocketAddr"
        SSL_PROTOCOL = "SslProtocol"
        URL_FILE_EXTENSION = "UrlFileExtension"
        URL_FILE_NAME = "UrlFileName"
        URL_PATH = "UrlPath"


    class azure.mgmt.cdn.models.MetricAvailability(Model):
        blob_duration: str
        time_grain: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MetricSpecification(Model):
        aggregation_type: str
        availabilities: list[MetricAvailability]
        dimensions: list[DimensionProperties]
        display_description: str
        display_name: str
        fill_gap_with_zero: bool
        is_internal: bool
        metric_filter_pattern: str
        name: str
        supported_time_grain_types: list[str]
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[List[MetricAvailability]] = ..., 
                dimensions: Optional[List[DimensionProperties]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                is_internal: Optional[bool] = ..., 
                metric_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_time_grain_types: Optional[List[str]] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MetricsGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_D = "P1D"
        PT1_H = "PT1H"
        PT5_M = "PT5M"


    class azure.mgmt.cdn.models.MetricsResponse(Model):
        date_time_begin: datetime
        date_time_end: datetime
        granularity: Union[str, MetricsGranularity]
        series: list[MetricsResponseSeriesItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                granularity: Optional[Union[str, MetricsGranularity]] = ..., 
                series: Optional[List[MetricsResponseSeriesItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MetricsResponseSeriesItem(Model):
        data: list[Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems]
        groups: list[MetricsResponseSeriesPropertiesItemsItem]
        metric: str
        unit: Union[str, MetricsSeriesUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[List[Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems]] = ..., 
                groups: Optional[List[MetricsResponseSeriesPropertiesItemsItem]] = ..., 
                metric: Optional[str] = ..., 
                unit: Optional[Union[str, MetricsSeriesUnit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MetricsResponseSeriesPropertiesItemsItem(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MetricsSeriesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BITS_PER_SECOND = "bitsPerSecond"
        BYTES = "bytes"
        COUNT = "count"
        MILLI_SECONDS = "milliSeconds"


    class azure.mgmt.cdn.models.MigrateResult(Model):
        id: str
        migrated_profile_resource_id: ResourceReference
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MigrationErrorType(Model):
        code: str
        error_message: str
        next_steps: str
        resource_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MigrationParameters(Model):
        classic_resource_reference: ResourceReference
        migration_web_application_firewall_mappings: list[MigrationWebApplicationFirewallMapping]
        profile_name: str
        sku: Sku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                classic_resource_reference: ResourceReference, 
                migration_web_application_firewall_mappings: Optional[List[MigrationWebApplicationFirewallMapping]] = ..., 
                profile_name: str, 
                sku: Sku, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MigrationWebApplicationFirewallMapping(Model):
        migrated_from: ResourceReference
        migrated_to: ResourceReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migrated_from: Optional[ResourceReference] = ..., 
                migrated_to: Optional[ResourceReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.MinimumTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TLS10 = "TLS10"
        TLS12 = "TLS12"


    class azure.mgmt.cdn.models.Operation(Model):
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: str
        service_specification: ServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                service_specification: Optional[ServiceSpecification] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OperationDisplay(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OperationsListResult(Model):
        next_link: str
        value: list[Operation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Operation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Operator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GEO_MATCH = "GeoMatch"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        IP_MATCH = "IPMatch"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.OptimizationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DYNAMIC_SITE_ACCELERATION = "DynamicSiteAcceleration"
        GENERAL_MEDIA_STREAMING = "GeneralMediaStreaming"
        GENERAL_WEB_DELIVERY = "GeneralWebDelivery"
        LARGE_FILE_DOWNLOAD = "LargeFileDownload"
        VIDEO_ON_DEMAND_MEDIA_STREAMING = "VideoOnDemandMediaStreaming"


    class azure.mgmt.cdn.models.Origin(ProxyResource):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        id: str
        name: str
        origin_host_header: str
        priority: int
        private_endpoint_status: Union[str, PrivateEndpointStatus]
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        provisioning_state: Union[str, OriginProvisioningState]
        resource_state: Union[str, OriginResourceState]
        system_data: SystemData
        type: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroup(ProxyResource):
        health_probe_settings: HealthProbeParameters
        id: str
        name: str
        origins: list[ResourceReference]
        provisioning_state: Union[str, OriginGroupProvisioningState]
        resource_state: Union[str, OriginGroupResourceState]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        system_data: SystemData
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[List[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupListResult(Model):
        next_link: str
        value: list[OriginGroup]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupOverride(Model):
        forwarding_protocol: Union[str, ForwardingProtocol]
        origin_group: ResourceReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                origin_group: Optional[ResourceReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupOverrideAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: OriginGroupOverrideActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: OriginGroupOverrideActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupOverrideActionParameters(Model):
        origin_group: ResourceReference
        type_name: Union[str, OriginGroupOverrideActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                origin_group: ResourceReference, 
                type_name: Union[str, OriginGroupOverrideActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupOverrideActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleOriginGroupOverrideActionParameters"


    class azure.mgmt.cdn.models.OriginGroupProperties(OriginGroupUpdatePropertiesParameters):
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        provisioning_state: Union[str, OriginGroupProvisioningState]
        resource_state: Union[str, OriginGroupResourceState]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[List[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.OriginGroupResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"


    class azure.mgmt.cdn.models.OriginGroupUpdateParameters(Model):
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[List[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginGroupUpdatePropertiesParameters(Model):
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[List[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginListResult(Model):
        next_link: str
        value: list[Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginProperties(OriginUpdatePropertiesParameters):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        origin_host_header: str
        priority: int
        private_endpoint_status: Union[str, PrivateEndpointStatus]
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        provisioning_state: Union[str, OriginProvisioningState]
        resource_state: Union[str, OriginResourceState]
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.OriginResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        CREATING = "Creating"
        DELETING = "Deleting"


    class azure.mgmt.cdn.models.OriginUpdateParameters(Model):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        origin_host_header: str
        priority: int
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.OriginUpdatePropertiesParameters(Model):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        origin_host_header: str
        priority: int
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        weight: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ParamIndicator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXPIRES = "Expires"
        KEY_ID = "KeyId"
        SIGNATURE = "Signature"


    class azure.mgmt.cdn.models.PolicyEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.PolicyMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DETECTION = "Detection"
        PREVENTION = "Prevention"


    class azure.mgmt.cdn.models.PolicyResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        DISABLING = "Disabling"
        ENABLED = "Enabled"
        ENABLING = "Enabling"


    class azure.mgmt.cdn.models.PolicySettings(Model):
        default_custom_block_response_body: str
        default_custom_block_response_status_code: Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]
        default_redirect_url: str
        enabled_state: Union[str, PolicyEnabledState]
        mode: Union[str, PolicyMode]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default_custom_block_response_body: Optional[str] = ..., 
                default_custom_block_response_status_code: Optional[Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]] = ..., 
                default_redirect_url: Optional[str] = ..., 
                enabled_state: Optional[Union[str, PolicyEnabledState]] = ..., 
                mode: Optional[Union[str, PolicyMode]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.PolicySettingsDefaultCustomBlockResponseStatusCode(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR_HUNDRED_FIVE = 405
        FOUR_HUNDRED_SIX = 406
        FOUR_HUNDRED_THREE = 403
        FOUR_HUNDRED_TWENTY_NINE = 429
        TWO_HUNDRED = 200


    class azure.mgmt.cdn.models.PostArgsMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, PostArgsOperator]
        selector: str
        transforms: Union[list[str, Transform]]
        type_name: Union[str, PostArgsMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, PostArgsOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, PostArgsMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.PostArgsMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS = "DeliveryRulePostArgsConditionParameters"


    class azure.mgmt.cdn.models.PostArgsOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.PrivateEndpointStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.cdn.models.ProbeProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"
        NOT_SET = "NotSet"


    class azure.mgmt.cdn.models.Profile(TrackedResource):
        extended_properties: dict[str, str]
        front_door_id: str
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        log_scrubbing: ProfileLogScrubbing
        name: str
        origin_response_timeout_seconds: int
        provisioning_state: Union[str, ProfileProvisioningState]
        resource_state: Union[str, ProfileResourceState]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                log_scrubbing: Optional[ProfileLogScrubbing] = ..., 
                origin_response_timeout_seconds: Optional[int] = ..., 
                sku: Sku, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileChangeSkuWafMapping(Model):
        change_to_waf_policy: ResourceReference
        security_policy_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                change_to_waf_policy: ResourceReference, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileListResult(Model):
        next_link: str
        value: list[Profile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileLogScrubbing(Model):
        scrubbing_rules: list[ProfileScrubbingRules]
        state: Union[str, ProfileScrubbingState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                scrubbing_rules: Optional[List[ProfileScrubbingRules]] = ..., 
                state: Optional[Union[str, ProfileScrubbingState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.ProfileResourceState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ABORTING_MIGRATION = "AbortingMigration"
        ACTIVE = "Active"
        COMMITTING_MIGRATION = "CommittingMigration"
        CREATING = "Creating"
        DELETING = "Deleting"
        DISABLED = "Disabled"
        MIGRATED = "Migrated"
        MIGRATING = "Migrating"
        PENDING_MIGRATION_COMMIT = "PendingMigrationCommit"


    class azure.mgmt.cdn.models.ProfileScrubbingRules(Model):
        match_variable: Union[str, ScrubbingRuleEntryMatchVariable]
        selector: str
        selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator]
        state: Union[str, ScrubbingRuleEntryState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_variable: Union[str, ScrubbingRuleEntryMatchVariable], 
                selector: Optional[str] = ..., 
                selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator], 
                state: Optional[Union[str, ScrubbingRuleEntryState]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileScrubbingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.ProfileUpdateParameters(Model):
        identity: ManagedServiceIdentity
        log_scrubbing: ProfileLogScrubbing
        origin_response_timeout_seconds: int
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                log_scrubbing: Optional[ProfileLogScrubbing] = ..., 
                origin_response_timeout_seconds: Optional[int] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProfileUpgradeParameters(Model):
        waf_mapping_list: list[ProfileChangeSkuWafMapping]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                waf_mapping_list: List[ProfileChangeSkuWafMapping], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IP_BASED = "IPBased"
        SERVER_NAME_INDICATION = "ServerNameIndication"


    class azure.mgmt.cdn.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cdn.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.PurgeParameters(Model):
        content_paths: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                content_paths: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.QueryStringBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXCLUDE = "Exclude"
        EXCLUDE_ALL = "ExcludeAll"
        INCLUDE = "Include"
        INCLUDE_ALL = "IncludeAll"


    class azure.mgmt.cdn.models.QueryStringCachingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS_CACHING = "BypassCaching"
        IGNORE_QUERY_STRING = "IgnoreQueryString"
        NOT_SET = "NotSet"
        USE_QUERY_STRING = "UseQueryString"


    class azure.mgmt.cdn.models.QueryStringMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, QueryStringOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, QueryStringMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, QueryStringOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, QueryStringMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.QueryStringMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS = "DeliveryRuleQueryStringConditionParameters"


    class azure.mgmt.cdn.models.QueryStringOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.RankingsResponse(Model):
        date_time_begin: datetime
        date_time_end: datetime
        tables: list[RankingsResponseTablesItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                tables: Optional[List[RankingsResponseTablesItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RankingsResponseTablesItem(Model):
        data: list[RankingsResponseTablesPropertiesItemsItem]
        ranking: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[List[RankingsResponseTablesPropertiesItemsItem]] = ..., 
                ranking: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RankingsResponseTablesPropertiesItemsItem(Model):
        metrics: list[RankingsResponseTablesPropertiesItemsMetricsItem]
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metrics: Optional[List[RankingsResponseTablesPropertiesItemsMetricsItem]] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RankingsResponseTablesPropertiesItemsMetricsItem(Model):
        metric: str
        percentage: float
        value: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                metric: Optional[str] = ..., 
                percentage: Optional[float] = ..., 
                value: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RateLimitRule(CustomRule):
        action: Union[str, ActionType]
        enabled_state: Union[str, CustomRuleEnabledState]
        match_conditions: list[MatchCondition]
        name: str
        priority: int
        rate_limit_duration_in_minutes: int
        rate_limit_threshold: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: Union[str, ActionType], 
                enabled_state: Optional[Union[str, CustomRuleEnabledState]] = ..., 
                match_conditions: List[MatchCondition], 
                name: str, 
                priority: int, 
                rate_limit_duration_in_minutes: int, 
                rate_limit_threshold: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RateLimitRuleList(Model):
        rules: list[RateLimitRule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                rules: Optional[List[RateLimitRule]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RedirectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUND = "Found"
        MOVED = "Moved"
        PERMANENT_REDIRECT = "PermanentRedirect"
        TEMPORARY_REDIRECT = "TemporaryRedirect"


    class azure.mgmt.cdn.models.RemoteAddressMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RemoteAddressOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RemoteAddressMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RemoteAddressOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RemoteAddressMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RemoteAddressMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS = "DeliveryRuleRemoteAddressConditionParameters"


    class azure.mgmt.cdn.models.RemoteAddressOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        GEO_MATCH = "GeoMatch"
        IP_MATCH = "IPMatch"


    class azure.mgmt.cdn.models.RequestBodyMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestBodyOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RequestBodyMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RequestBodyOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RequestBodyMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RequestBodyMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS = "DeliveryRuleRequestBodyConditionParameters"


    class azure.mgmt.cdn.models.RequestBodyOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.RequestHeaderMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestHeaderOperator]
        selector: str
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RequestHeaderMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RequestHeaderOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RequestHeaderMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RequestHeaderMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS = "DeliveryRuleRequestHeaderConditionParameters"


    class azure.mgmt.cdn.models.RequestHeaderOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.RequestMethodMatchConditionParameters(Model):
        match_values: Union[list[str, RequestMethodMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, RequestMethodOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RequestMethodMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[Union[str, RequestMethodMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RequestMethodOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RequestMethodMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RequestMethodMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        POST = "POST"
        PUT = "PUT"
        TRACE = "TRACE"


    class azure.mgmt.cdn.models.RequestMethodMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS = "DeliveryRuleRequestMethodConditionParameters"


    class azure.mgmt.cdn.models.RequestMethodOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParameters(Model):
        match_values: Union[list[str, RequestSchemeMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, RequestSchemeMatchConditionParametersOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RequestSchemeMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[Union[str, RequestSchemeMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RequestSchemeMatchConditionParametersOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RequestSchemeMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParametersOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS = "DeliveryRuleRequestSchemeConditionParameters"


    class azure.mgmt.cdn.models.RequestUriMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestUriOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, RequestUriMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, RequestUriOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, RequestUriMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RequestUriMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS = "DeliveryRuleRequestUriConditionParameters"


    class azure.mgmt.cdn.models.RequestUriOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourceReference(Model):
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_CDN_PROFILES_AFD_ENDPOINTS = "Microsoft.Cdn/Profiles/AfdEndpoints"
        MICROSOFT_CDN_PROFILES_ENDPOINTS = "Microsoft.Cdn/Profiles/Endpoints"


    class azure.mgmt.cdn.models.ResourceUsage(Model):
        current_value: int
        limit: int
        resource_type: str
        unit: Union[str, ResourceUsageUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourceUsageListResult(Model):
        next_link: str
        value: list[ResourceUsage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourceUsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "count"


    class azure.mgmt.cdn.models.ResourcesResponse(Model):
        custom_domains: list[ResourcesResponseCustomDomainsItem]
        endpoints: list[ResourcesResponseEndpointsItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_domains: Optional[List[ResourcesResponseCustomDomainsItem]] = ..., 
                endpoints: Optional[List[ResourcesResponseEndpointsItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourcesResponseCustomDomainsItem(Model):
        endpoint_id: str
        history: bool
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_id: Optional[str] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourcesResponseEndpointsItem(Model):
        custom_domains: list[ResourcesResponseEndpointsPropertiesItemsItem]
        history: bool
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_domains: Optional[List[ResourcesResponseEndpointsPropertiesItemsItem]] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResourcesResponseEndpointsPropertiesItemsItem(Model):
        endpoint_id: str
        history: bool
        id: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                endpoint_id: Optional[str] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ResponseBasedDetectedErrorTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TCP_AND_HTTP_ERRORS = "TcpAndHttpErrors"
        TCP_ERRORS_ONLY = "TcpErrorsOnly"


    class azure.mgmt.cdn.models.ResponseBasedOriginErrorDetectionParameters(Model):
        http_error_ranges: list[HttpErrorRangeParameters]
        response_based_detected_error_types: Union[str, ResponseBasedDetectedErrorTypes]
        response_based_failover_threshold_percentage: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                http_error_ranges: Optional[List[HttpErrorRangeParameters]] = ..., 
                response_based_detected_error_types: Optional[Union[str, ResponseBasedDetectedErrorTypes]] = ..., 
                response_based_failover_threshold_percentage: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Route(ProxyResource):
        cache_configuration: AfdRouteCacheConfiguration
        custom_domains: list[ActivatedResourceReference]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        id: str
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        name: str
        origin_group: ResourceReference
        origin_path: str
        patterns_to_match: list[str]
        provisioning_state: Union[str, AfdProvisioningState]
        rule_sets: list[ResourceReference]
        supported_protocols: Union[list[str, AFDEndpointProtocols]]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[List[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Union[str, HttpsRedirect] = "Disabled", 
                link_to_default_domain: Union[str, LinkToDefaultDomain] = "Disabled", 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[List[str]] = ..., 
                rule_sets: Optional[List[ResourceReference]] = ..., 
                supported_protocols: List[Union[str, AFDEndpointProtocols]] = [Http, Https], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RouteConfigurationOverrideActionParameters(Model):
        cache_configuration: CacheConfiguration
        origin_group_override: OriginGroupOverride
        type_name: Union[str, RouteConfigurationOverrideActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_configuration: Optional[CacheConfiguration] = ..., 
                origin_group_override: Optional[OriginGroupOverride] = ..., 
                type_name: Union[str, RouteConfigurationOverrideActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RouteConfigurationOverrideActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleRouteConfigurationOverrideActionParameters"


    class azure.mgmt.cdn.models.RouteListResult(Model):
        next_link: str
        value: list[Route]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RouteProperties(RouteUpdatePropertiesParameters, AFDStateProperties):
        cache_configuration: AfdRouteCacheConfiguration
        custom_domains: list[ActivatedResourceReference]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        origin_group: ResourceReference
        origin_path: str
        patterns_to_match: list[str]
        provisioning_state: Union[str, AfdProvisioningState]
        rule_sets: list[ResourceReference]
        supported_protocols: Union[list[str, AFDEndpointProtocols]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[List[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Union[str, HttpsRedirect] = "Disabled", 
                link_to_default_domain: Union[str, LinkToDefaultDomain] = "Disabled", 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[List[str]] = ..., 
                rule_sets: Optional[List[ResourceReference]] = ..., 
                supported_protocols: List[Union[str, AFDEndpointProtocols]] = [Http, Https], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RouteUpdateParameters(Model):
        cache_configuration: AfdRouteCacheConfiguration
        custom_domains: list[ActivatedResourceReference]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        origin_group: ResourceReference
        origin_path: str
        patterns_to_match: list[str]
        rule_sets: list[ResourceReference]
        supported_protocols: Union[list[str, AFDEndpointProtocols]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[List[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Union[str, HttpsRedirect] = "Disabled", 
                link_to_default_domain: Union[str, LinkToDefaultDomain] = "Disabled", 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[List[str]] = ..., 
                rule_sets: Optional[List[ResourceReference]] = ..., 
                supported_protocols: List[Union[str, AFDEndpointProtocols]] = [Http, Https], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RouteUpdatePropertiesParameters(Model):
        cache_configuration: AfdRouteCacheConfiguration
        custom_domains: list[ActivatedResourceReference]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        origin_group: ResourceReference
        origin_path: str
        patterns_to_match: list[str]
        rule_sets: list[ResourceReference]
        supported_protocols: Union[list[str, AFDEndpointProtocols]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[List[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Union[str, HttpsRedirect] = "Disabled", 
                link_to_default_domain: Union[str, LinkToDefaultDomain] = "Disabled", 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[List[str]] = ..., 
                rule_sets: Optional[List[ResourceReference]] = ..., 
                supported_protocols: List[Union[str, AFDEndpointProtocols]] = [Http, Https], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Rule(ProxyResource):
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        deployment_status: Union[str, DeploymentStatus]
        id: str
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        name: str
        order: int
        provisioning_state: Union[str, AfdProvisioningState]
        rule_set_name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[DeliveryRuleAction]] = ..., 
                conditions: Optional[List[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Union[str, MatchProcessingBehavior] = "Continue", 
                order: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleCacheBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HONOR_ORIGIN = "HonorOrigin"
        OVERRIDE_ALWAYS = "OverrideAlways"
        OVERRIDE_IF_ORIGIN_MISSING = "OverrideIfOriginMissing"


    class azure.mgmt.cdn.models.RuleIsCompressionEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.RuleListResult(Model):
        next_link: str
        value: list[Rule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleProperties(RuleUpdatePropertiesParameters, AFDStateProperties):
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        deployment_status: Union[str, DeploymentStatus]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        provisioning_state: Union[str, AfdProvisioningState]
        rule_set_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[DeliveryRuleAction]] = ..., 
                conditions: Optional[List[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Union[str, MatchProcessingBehavior] = "Continue", 
                order: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleQueryStringCachingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE_QUERY_STRING = "IgnoreQueryString"
        IGNORE_SPECIFIED_QUERY_STRINGS = "IgnoreSpecifiedQueryStrings"
        INCLUDE_SPECIFIED_QUERY_STRINGS = "IncludeSpecifiedQueryStrings"
        USE_QUERY_STRING = "UseQueryString"


    class azure.mgmt.cdn.models.RuleSet(ProxyResource):
        deployment_status: Union[str, DeploymentStatus]
        id: str
        name: str
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleSetListResult(Model):
        next_link: str
        value: list[RuleSet]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleSetProperties(AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleUpdateParameters(Model):
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        rule_set_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[DeliveryRuleAction]] = ..., 
                conditions: Optional[List[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Union[str, MatchProcessingBehavior] = "Continue", 
                order: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.RuleUpdatePropertiesParameters(Model):
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        rule_set_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions: Optional[List[DeliveryRuleAction]] = ..., 
                conditions: Optional[List[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Union[str, MatchProcessingBehavior] = "Continue", 
                order: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ScrubbingRuleEntryMatchOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUALS_ANY = "EqualsAny"


    class azure.mgmt.cdn.models.ScrubbingRuleEntryMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QUERY_STRING_ARG_NAMES = "QueryStringArgNames"
        REQUEST_IP_ADDRESS = "RequestIPAddress"
        REQUEST_URI = "RequestUri"


    class azure.mgmt.cdn.models.ScrubbingRuleEntryState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.Secret(ProxyResource):
        deployment_status: Union[str, DeploymentStatus]
        id: str
        name: str
        parameters: SecretParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[SecretParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecretListResult(Model):
        next_link: str
        value: list[Secret]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecretParameters(Model):
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecretProperties(AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        parameters: SecretParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[SecretParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIRST_PARTY_MANAGED_CERTIFICATE = "AzureFirstPartyManagedCertificate"
        CUSTOMER_CERTIFICATE = "CustomerCertificate"
        MANAGED_CERTIFICATE = "ManagedCertificate"
        URL_SIGNING_KEY = "UrlSigningKey"


    class azure.mgmt.cdn.models.SecurityPolicy(ProxyResource):
        deployment_status: Union[str, DeploymentStatus]
        id: str
        name: str
        parameters: SecurityPolicyPropertiesParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[SecurityPolicyPropertiesParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyListResult(Model):
        next_link: str
        value: list[SecurityPolicy]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyProperties(AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        parameters: SecurityPolicyPropertiesParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[SecurityPolicyPropertiesParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyPropertiesParameters(Model):
        type: Union[str, SecurityPolicyType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_APPLICATION_FIREWALL = "WebApplicationFirewall"


    class azure.mgmt.cdn.models.SecurityPolicyUpdateParameters(Model):
        parameters: SecurityPolicyPropertiesParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: Optional[SecurityPolicyPropertiesParameters] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyWebApplicationFirewallAssociation(Model):
        domains: list[ActivatedResourceReference]
        patterns_to_match: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                domains: Optional[List[ActivatedResourceReference]] = ..., 
                patterns_to_match: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SecurityPolicyWebApplicationFirewallParameters(SecurityPolicyPropertiesParameters):
        associations: list[SecurityPolicyWebApplicationFirewallAssociation]
        type: Union[str, SecurityPolicyType]
        waf_policy: ResourceReference

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                associations: Optional[List[SecurityPolicyWebApplicationFirewallAssociation]] = ..., 
                waf_policy: Optional[ResourceReference] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ServerPortMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, ServerPortOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, ServerPortMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, ServerPortOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, ServerPortMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ServerPortMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS = "DeliveryRuleServerPortConditionParameters"


    class azure.mgmt.cdn.models.ServerPortOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.ServiceSpecification(Model):
        log_specifications: list[LogSpecification]
        metric_specifications: list[MetricSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[LogSpecification]] = ..., 
                metric_specifications: Optional[List[MetricSpecification]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SharedPrivateLinkResourceProperties(Model):
        group_id: str
        private_link: ResourceReference
        private_link_location: str
        request_message: str
        status: Union[str, SharedPrivateLinkResourceStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_link: Optional[ResourceReference] = ..., 
                private_link_location: Optional[str] = ..., 
                request_message: Optional[str] = ..., 
                status: Optional[Union[str, SharedPrivateLinkResourceStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.cdn.models.Sku(Model):
        name: Union[str, SkuName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_VERIZON = "Custom_Verizon"
        PREMIUM_AZURE_FRONT_DOOR = "Premium_AzureFrontDoor"
        PREMIUM_VERIZON = "Premium_Verizon"
        STANDARD955_BAND_WIDTH_CHINA_CDN = "Standard_955BandWidth_ChinaCdn"
        STANDARD_AKAMAI = "Standard_Akamai"
        STANDARD_AVG_BAND_WIDTH_CHINA_CDN = "Standard_AvgBandWidth_ChinaCdn"
        STANDARD_AZURE_FRONT_DOOR = "Standard_AzureFrontDoor"
        STANDARD_CHINA_CDN = "Standard_ChinaCdn"
        STANDARD_MICROSOFT = "Standard_Microsoft"
        STANDARD_PLUS955_BAND_WIDTH_CHINA_CDN = "StandardPlus_955BandWidth_ChinaCdn"
        STANDARD_PLUS_AVG_BAND_WIDTH_CHINA_CDN = "StandardPlus_AvgBandWidth_ChinaCdn"
        STANDARD_PLUS_CHINA_CDN = "StandardPlus_ChinaCdn"
        STANDARD_VERIZON = "Standard_Verizon"


    class azure.mgmt.cdn.models.SocketAddrMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, SocketAddrOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, SocketAddrMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, SocketAddrOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, SocketAddrMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SocketAddrMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS = "DeliveryRuleSocketAddrConditionParameters"


    class azure.mgmt.cdn.models.SocketAddrOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        IP_MATCH = "IPMatch"


    class azure.mgmt.cdn.models.SslProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TL_SV1 = "TLSv1"
        TL_SV1_1 = "TLSv1.1"
        TL_SV1_2 = "TLSv1.2"


    class azure.mgmt.cdn.models.SslProtocolMatchConditionParameters(Model):
        match_values: Union[list[str, SslProtocol]]
        negate_condition: bool
        operator: Union[str, SslProtocolOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, SslProtocolMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[Union[str, SslProtocol]]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, SslProtocolOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, SslProtocolMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SslProtocolMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS = "DeliveryRuleSslProtocolConditionParameters"


    class azure.mgmt.cdn.models.SslProtocolOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.SsoUri(Model):
        sso_uri_value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_DENIED = "AccessDenied"
        CERTIFICATE_EXPIRED = "CertificateExpired"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.cdn.models.SupportedOptimizationTypesListResult(Model):
        supported_optimization_types: Union[list[str, OptimizationType]]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, IdentityType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, IdentityType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, IdentityType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, IdentityType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
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
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Transform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWERCASE = "Lowercase"
        REMOVE_NULLS = "RemoveNulls"
        TRIM = "Trim"
        UPPERCASE = "Uppercase"
        URL_DECODE = "UrlDecode"
        URL_ENCODE = "UrlEncode"


    class azure.mgmt.cdn.models.TransformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOWERCASE = "Lowercase"
        REMOVE_NULLS = "RemoveNulls"
        TRIM = "Trim"
        UPPERCASE = "Uppercase"
        URL_DECODE = "UrlDecode"
        URL_ENCODE = "UrlEncode"


    class azure.mgmt.cdn.models.UpdateRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACTION = "NoAction"


    class azure.mgmt.cdn.models.UrlFileExtensionMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlFileExtensionOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, UrlFileExtensionMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, UrlFileExtensionOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, UrlFileExtensionMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlFileExtensionMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlFileExtensionMatchConditionParameters"


    class azure.mgmt.cdn.models.UrlFileExtensionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.UrlFileNameMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlFileNameOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, UrlFileNameMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, UrlFileNameOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, UrlFileNameMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlFileNameMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS = "DeliveryRuleUrlFilenameConditionParameters"


    class azure.mgmt.cdn.models.UrlFileNameOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"


    class azure.mgmt.cdn.models.UrlPathMatchConditionParameters(Model):
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlPathOperator]
        transforms: Union[list[str, Transform]]
        type_name: Union[str, UrlPathMatchConditionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                match_values: Optional[List[str]] = ..., 
                negate_condition: bool = False, 
                operator: Union[str, UrlPathOperator], 
                transforms: Optional[List[Union[str, Transform]]] = ..., 
                type_name: Union[str, UrlPathMatchConditionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlPathMatchConditionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlPathMatchConditionParameters"


    class azure.mgmt.cdn.models.UrlPathOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        BEGINS_WITH = "BeginsWith"
        CONTAINS = "Contains"
        ENDS_WITH = "EndsWith"
        EQUAL = "Equal"
        GREATER_THAN = "GreaterThan"
        GREATER_THAN_OR_EQUAL = "GreaterThanOrEqual"
        LESS_THAN = "LessThan"
        LESS_THAN_OR_EQUAL = "LessThanOrEqual"
        REG_EX = "RegEx"
        WILDCARD = "Wildcard"


    class azure.mgmt.cdn.models.UrlRedirectAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: UrlRedirectActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlRedirectActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlRedirectActionParameters(Model):
        custom_fragment: str
        custom_hostname: str
        custom_path: str
        custom_query_string: str
        destination_protocol: Union[str, DestinationProtocol]
        redirect_type: Union[str, RedirectType]
        type_name: Union[str, UrlRedirectActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                custom_fragment: Optional[str] = ..., 
                custom_hostname: Optional[str] = ..., 
                custom_path: Optional[str] = ..., 
                custom_query_string: Optional[str] = ..., 
                destination_protocol: Optional[Union[str, DestinationProtocol]] = ..., 
                redirect_type: Union[str, RedirectType], 
                type_name: Union[str, UrlRedirectActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlRedirectActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS = "DeliveryRuleUrlRedirectActionParameters"


    class azure.mgmt.cdn.models.UrlRewriteAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: UrlRewriteActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlRewriteActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlRewriteActionParameters(Model):
        destination: str
        preserve_unmatched_path: bool
        source_pattern: str
        type_name: Union[str, UrlRewriteActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                destination: str, 
                preserve_unmatched_path: Optional[bool] = ..., 
                source_pattern: str, 
                type_name: Union[str, UrlRewriteActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlRewriteActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS = "DeliveryRuleUrlRewriteActionParameters"


    class azure.mgmt.cdn.models.UrlSigningAction(DeliveryRuleAction):
        name: Union[str, DeliveryRuleActionEnum]
        parameters: UrlSigningActionParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                parameters: UrlSigningActionParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlSigningActionParameters(Model):
        algorithm: Union[str, Algorithm]
        parameter_name_override: list[UrlSigningParamIdentifier]
        type_name: Union[str, UrlSigningActionParametersTypeName]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                algorithm: Optional[Union[str, Algorithm]] = ..., 
                parameter_name_override: Optional[List[UrlSigningParamIdentifier]] = ..., 
                type_name: Union[str, UrlSigningActionParametersTypeName], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlSigningActionParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS = "DeliveryRuleUrlSigningActionParameters"


    class azure.mgmt.cdn.models.UrlSigningKey(Model):
        key_id: str
        key_source_parameters: KeyVaultSigningKeyParameters

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_id: str, 
                key_source_parameters: KeyVaultSigningKeyParameters, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlSigningKeyParameters(SecretParameters):
        key_id: str
        secret_source: ResourceReference
        secret_version: str
        type: Union[str, SecretType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key_id: str, 
                secret_source: ResourceReference, 
                secret_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UrlSigningParamIdentifier(Model):
        param_indicator: Union[str, ParamIndicator]
        param_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                param_indicator: Union[str, ParamIndicator], 
                param_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.Usage(Model):
        current_value: int
        id: str
        limit: int
        name: UsageName
        unit: Union[str, UsageUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: int, 
                limit: int, 
                name: UsageName, 
                unit: Union[str, UsageUnit], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UsageName(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.cdn.models.UsagesListResult(Model):
        next_link: str
        value: list[Usage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Usage]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.UserManagedHttpsParameters(CustomDomainHttpsParameters):
        certificate_source: Union[str, CertificateSource]
        certificate_source_parameters: KeyVaultCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_source_parameters: KeyVaultCertificateSourceParameters, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateCustomDomainInput(Model):
        host_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateCustomDomainOutput(Model):
        custom_domain_validated: bool
        message: str
        reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateProbeInput(Model):
        probe_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                probe_url: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateProbeOutput(Model):
        error_code: str
        is_valid: bool
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateSecretInput(Model):
        secret_source: ResourceReference
        secret_type: Union[str, SecretType]
        secret_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                secret_source: ResourceReference, 
                secret_type: Union[str, SecretType], 
                secret_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidateSecretOutput(Model):
        message: str
        status: Union[str, Status]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.ValidationToken(Model):
        token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "allow"
        BLOCK = "block"
        LOG = "log"
        REDIRECT = "redirect"


    class azure.mgmt.cdn.models.WafGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_D = "P1D"
        PT1_H = "PT1H"
        PT5_M = "PT5M"


    class azure.mgmt.cdn.models.WafMatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COOKIES = "Cookies"
        POST_ARGS = "PostArgs"
        QUERY_STRING = "QueryString"
        REMOTE_ADDR = "RemoteAddr"
        REQUEST_BODY = "RequestBody"
        REQUEST_HEADER = "RequestHeader"
        REQUEST_METHOD = "RequestMethod"
        REQUEST_URI = "RequestUri"
        SOCKET_ADDR = "SocketAddr"


    class azure.mgmt.cdn.models.WafMetric(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_REQUEST_COUNT = "clientRequestCount"


    class azure.mgmt.cdn.models.WafMetricsGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_D = "P1D"
        PT1_H = "PT1H"
        PT5_M = "PT5M"


    class azure.mgmt.cdn.models.WafMetricsResponse(Model):
        date_time_begin: datetime
        date_time_end: datetime
        granularity: Union[str, WafMetricsGranularity]
        series: list[WafMetricsResponseSeriesItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                granularity: Optional[Union[str, WafMetricsGranularity]] = ..., 
                series: Optional[List[WafMetricsResponseSeriesItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafMetricsResponseSeriesItem(Model):
        data: list[Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems]
        groups: list[WafMetricsResponseSeriesPropertiesItemsItem]
        metric: str
        unit: Union[str, WafMetricsSeriesUnit]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[List[Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems]] = ..., 
                groups: Optional[List[WafMetricsResponseSeriesPropertiesItemsItem]] = ..., 
                metric: Optional[str] = ..., 
                unit: Optional[Union[str, WafMetricsSeriesUnit]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafMetricsResponseSeriesPropertiesItemsItem(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafMetricsSeriesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "count"


    class azure.mgmt.cdn.models.WafRankingGroupBy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOM_DOMAIN = "customDomain"
        HTTP_STATUS_CODE = "httpStatusCode"


    class azure.mgmt.cdn.models.WafRankingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION = "action"
        CLIENT_IP = "clientIp"
        COUNTRY_OR_REGION = "countryOrRegion"
        RULE_GROUP = "ruleGroup"
        RULE_ID = "ruleId"
        RULE_TYPE = "ruleType"
        URL = "url"
        USER_AGENT = "userAgent"


    class azure.mgmt.cdn.models.WafRankingsResponse(Model):
        data: list[WafRankingsResponseDataItem]
        date_time_begin: datetime
        date_time_end: datetime
        groups: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                data: Optional[List[WafRankingsResponseDataItem]] = ..., 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                groups: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafRankingsResponseDataItem(Model):
        group_values: list[str]
        metrics: list[ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                group_values: Optional[List[str]] = ..., 
                metrics: Optional[List[ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls: Type[ModelType], 
                data: Any, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls: Type[ModelType], 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> ModelType: ...

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


    class azure.mgmt.cdn.models.WafRuleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOT = "bot"
        CUSTOM = "custom"
        MANAGED = "managed"


namespace azure.mgmt.cdn.operations

    class azure.mgmt.cdn.operations.AFDCustomDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain: AFDDomain, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDDomain]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_refresh_validation_token(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain_update_properties: AFDDomainUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDDomain]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                custom_domain_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDDomain]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> AFDDomain: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[AFDDomain]: ...


    class azure.mgmt.cdn.operations.AFDEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: AFDEndpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDEndpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDEndpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                contents: AfdPurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                contents: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: AFDEndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDEndpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDEndpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AFDEndpoint: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[AFDEndpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.cdn.operations.AFDOriginGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group: AFDOriginGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOriginGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOriginGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: AFDOriginGroupUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOriginGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOriginGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AFDOriginGroup: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[AFDOriginGroup]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.cdn.operations.AFDOriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin: AFDOrigin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOrigin]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOrigin]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin_update_properties: AFDOriginUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOrigin]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                origin_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AFDOrigin]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> AFDOrigin: ...

        @distributed_trace
        def list_by_origin_group(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> Iterable[AFDOrigin]: ...


    class azure.mgmt.cdn.operations.AFDProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_upgrade_parameters: ProfileUpgradeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_upgrade(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_upgrade_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_host_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_host_name_availability_input: CheckHostNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_host_name_availability(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                check_host_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...

        @overload
        def validate_secret(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                validate_secret_input: ValidateSecretInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSecretOutput: ...

        @overload
        def validate_secret(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                validate_secret_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateSecretOutput: ...


    class azure.mgmt.cdn.operations.CdnManagementClientOperationsMixin(CdnManagementClientMixinABC):

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: CheckEndpointNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_endpoint_name_availability(
                self, 
                resource_group_name: str, 
                check_endpoint_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckEndpointNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: CheckNameAvailabilityInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def check_name_availability_with_subscription(
                self, 
                check_name_availability_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityOutput: ...

        @overload
        def validate_probe(
                self, 
                validate_probe_input: ValidateProbeInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...

        @overload
        def validate_probe(
                self, 
                validate_probe_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateProbeOutput: ...


    class azure.mgmt.cdn.operations.CustomDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_properties: CustomDomainParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @distributed_trace
        def begin_disable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @overload
        def begin_enable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_https_parameters: Optional[CustomDomainHttpsParameters] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @overload
        def begin_enable_custom_https(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                custom_domain_https_parameters: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomDomain]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_name: str, 
                **kwargs: Any
            ) -> CustomDomain: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[CustomDomain]: ...


    class azure.mgmt.cdn.operations.EdgeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[EdgeNode]: ...


    class azure.mgmt.cdn.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: Endpoint, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_load_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: LoadParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_load_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: PurgeParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_purge_content(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                content_file_paths: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: EndpointUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                endpoint_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Endpoint]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Endpoint: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[Endpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[ResourceUsage]: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: ValidateCustomDomainInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...

        @overload
        def validate_custom_domain(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                custom_domain_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ValidateCustomDomainOutput: ...


    class azure.mgmt.cdn.operations.LogAnalyticsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get_log_analytics_locations(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ContinentsResponse: ...

        @distributed_trace
        def get_log_analytics_metrics(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, LogMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, LogMetricsGranularity], 
                custom_domains: List[str], 
                protocols: List[str], 
                group_by: Optional[List[Union[str, LogMetricsGroupBy]]] = None, 
                continents: Optional[List[str]] = None, 
                country_or_regions: Optional[List[str]] = None, 
                **kwargs: Any
            ) -> MetricsResponse: ...

        @distributed_trace
        def get_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rankings: List[Union[str, LogRanking]], 
                metrics: List[Union[str, LogRankingMetric]], 
                max_ranking: int, 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                custom_domains: Optional[List[str]] = None, 
                **kwargs: Any
            ) -> RankingsResponse: ...

        @distributed_trace
        def get_log_analytics_resources(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ResourcesResponse: ...

        @distributed_trace
        def get_waf_log_analytics_metrics(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, WafMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, WafGranularity], 
                actions: Optional[List[Union[str, WafAction]]] = None, 
                group_by: Optional[List[Union[str, WafRankingGroupBy]]] = None, 
                rule_types: Optional[List[Union[str, WafRuleType]]] = None, 
                **kwargs: Any
            ) -> WafMetricsResponse: ...

        @distributed_trace
        def get_waf_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                metrics: List[Union[str, WafMetric]], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                rankings: List[Union[str, WafRankingType]], 
                actions: Optional[List[Union[str, WafAction]]] = None, 
                rule_types: Optional[List[Union[str, WafRuleType]]] = None, 
                **kwargs: Any
            ) -> WafRankingsResponse: ...


    class azure.mgmt.cdn.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ManagedRuleSetDefinition]: ...


    class azure.mgmt.cdn.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.cdn.operations.OriginGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group: OriginGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OriginGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OriginGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: OriginGroupUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OriginGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                origin_group_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[OriginGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> OriginGroup: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[OriginGroup]: ...


    class azure.mgmt.cdn.operations.OriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin: Origin, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Origin]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Origin]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin_update_properties: OriginUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Origin]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                origin_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Origin]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                origin_name: str, 
                **kwargs: Any
            ) -> Origin: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[Origin]: ...


    class azure.mgmt.cdn.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy: CdnWebApplicationFirewallPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy_patch_parameters: CdnWebApplicationFirewallPolicyPatchParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CdnWebApplicationFirewallPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                cdn_web_application_firewall_policy_patch_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CdnWebApplicationFirewallPolicy]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> CdnWebApplicationFirewallPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[CdnWebApplicationFirewallPolicy]: ...


    class azure.mgmt.cdn.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_can_migrate(
                self, 
                resource_group_name: str, 
                can_migrate_parameters: CanMigrateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CanMigrateResult]: ...

        @overload
        def begin_can_migrate(
                self, 
                resource_group_name: str, 
                can_migrate_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CanMigrateResult]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile: Profile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                migration_parameters: MigrationParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrateResult]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                migration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrateResult]: ...

        @distributed_trace
        def begin_migration_commit(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_update_parameters: ProfileUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                profile_update_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Profile]: ...

        @distributed_trace
        def generate_sso_uri(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> SsoUri: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Profile: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Profile]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[ResourceUsage]: ...

        @distributed_trace
        def list_supported_optimization_types(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> SupportedOptimizationTypesListResult: ...


    class azure.mgmt.cdn.operations.ResourceUsageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ResourceUsage]: ...


    class azure.mgmt.cdn.operations.RoutesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route: Route, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Route]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Route]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route_update_properties: RouteUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Route]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                route_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Route]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                route_name: str, 
                **kwargs: Any
            ) -> Route: ...

        @distributed_trace
        def list_by_endpoint(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> Iterable[Route]: ...


    class azure.mgmt.cdn.operations.RuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> RuleSet: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> RuleSet: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[RuleSet]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> Iterable[Usage]: ...


    class azure.mgmt.cdn.operations.RulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule: Rule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Rule]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Rule]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule_update_properties: RuleUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Rule]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                rule_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Rule]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                rule_name: str, 
                **kwargs: Any
            ) -> Rule: ...

        @distributed_trace
        def list_by_rule_set(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> Iterable[Rule]: ...


    class azure.mgmt.cdn.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                secret: Secret, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Secret]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                secret: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Secret]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                secret_name: str, 
                **kwargs: Any
            ) -> Secret: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[Secret]: ...


    class azure.mgmt.cdn.operations.SecurityPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy: SecurityPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy_update_properties: SecurityPolicyUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @overload
        def begin_patch(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                security_policy_update_properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SecurityPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                security_policy_name: str, 
                **kwargs: Any
            ) -> SecurityPolicy: ...

        @distributed_trace
        def list_by_profile(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> Iterable[SecurityPolicy]: ...


```