```py
namespace azure.mgmt.cdn

    class azure.mgmt.cdn.CdnManagementClient(_CdnManagementClientOperationsMixin): implements ContextManager 
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

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

    class azure.mgmt.cdn.aio.CdnManagementClient(_CdnManagementClientOperationsMixin): implements AsyncContextManager 
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
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
                cloud_setting: Optional[AzureClouds] = ..., 
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

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

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
            ) -> AsyncItemPaged[AFDDomain]: ...


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
            ) -> AsyncItemPaged[AFDEndpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...

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
            ) -> AsyncItemPaged[AFDOriginGroup]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


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
            ) -> AsyncItemPaged[AFDOrigin]: ...


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
            ) -> AsyncItemPaged[Usage]: ...

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
            ) -> AsyncItemPaged[CustomDomain]: ...


    class azure.mgmt.cdn.aio.operations.EdgeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[EdgeNode]: ...


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
            ) -> AsyncItemPaged[Endpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceUsage]: ...

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
                *, 
                continents: Optional[List[str]] = ..., 
                country_or_regions: Optional[List[str]] = ..., 
                custom_domains: List[str], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, LogMetricsGranularity], 
                group_by: Optional[List[Union[str, LogMetricsGroupBy]]] = ..., 
                metrics: List[Union[str, LogMetric]], 
                protocols: List[str], 
                **kwargs: Any
            ) -> MetricsResponse: ...

        @distributed_trace_async
        async def get_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                custom_domains: Optional[List[str]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                metrics: List[Union[str, LogRankingMetric]], 
                rankings: List[Union[str, LogRanking]], 
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
                *, 
                actions: Optional[List[Union[str, WafAction]]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, WafGranularity], 
                group_by: Optional[List[Union[str, WafRankingGroupBy]]] = ..., 
                metrics: List[Union[str, WafMetric]], 
                rule_types: Optional[List[Union[str, WafRuleType]]] = ..., 
                **kwargs: Any
            ) -> WafMetricsResponse: ...

        @distributed_trace_async
        async def get_waf_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                actions: Optional[List[Union[str, WafAction]]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                metrics: List[Union[str, WafMetric]], 
                rankings: List[Union[str, WafRankingType]], 
                rule_types: Optional[List[Union[str, WafRuleType]]] = ..., 
                **kwargs: Any
            ) -> WafRankingsResponse: ...


    class azure.mgmt.cdn.aio.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ManagedRuleSetDefinition]: ...


    class azure.mgmt.cdn.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


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
            ) -> AsyncItemPaged[OriginGroup]: ...


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
            ) -> AsyncItemPaged[Origin]: ...


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
            ) -> AsyncItemPaged[CdnWebApplicationFirewallPolicy]: ...


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

        @distributed_trace_async
        async def begin_cdn_can_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[CanMigrateResult]: ...

        @overload
        async def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: CdnMigrationToAfdParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateResult]: ...

        @overload
        async def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: CdnMigrationToAfdParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateResult]: ...

        @overload
        async def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrateResult]: ...

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
        async def begin_migration_abort(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

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
        def list(self, **kwargs: Any) -> AsyncItemPaged[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Profile]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceUsage]: ...

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
        def list(self, **kwargs: Any) -> AsyncItemPaged[ResourceUsage]: ...


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
            ) -> AsyncItemPaged[Route]: ...


    class azure.mgmt.cdn.aio.operations.RuleSetsOperations:

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
                resource: Optional[RuleSet] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuleSet]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                resource: Optional[RuleSet] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuleSet]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                resource: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RuleSet]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

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
            ) -> AsyncItemPaged[RuleSet]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Usage]: ...


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
            ) -> AsyncItemPaged[Rule]: ...


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
            ) -> AsyncItemPaged[Secret]: ...


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
            ) -> AsyncItemPaged[SecurityPolicy]: ...


namespace azure.mgmt.cdn.models

    class azure.mgmt.cdn.models.AFDDomain(ProxyResource):
        id: str
        name: str
        properties: Optional[AFDDomainProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDDomainProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDDomainHttpsCustomizedCipherSuiteSet(_Model):
        cipher_suite_set_for_tls12: Optional[list[Union[str, AfdCustomizedCipherSuiteForTls12]]]
        cipher_suite_set_for_tls13: Optional[list[Union[str, AfdCustomizedCipherSuiteForTls13]]]

        @overload
        def __init__(
                self, 
                *, 
                cipher_suite_set_for_tls12: Optional[list[Union[str, AfdCustomizedCipherSuiteForTls12]]] = ..., 
                cipher_suite_set_for_tls13: Optional[list[Union[str, AfdCustomizedCipherSuiteForTls13]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDDomainHttpsParameters(_Model):
        certificate_type: Union[str, AfdCertificateType]
        cipher_suite_set_type: Optional[Union[str, AfdCipherSuiteSetType]]
        customized_cipher_suite_set: Optional[AFDDomainHttpsCustomizedCipherSuiteSet]
        minimum_tls_version: Optional[Union[str, AfdMinimumTlsVersion]]
        secret: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                certificate_type: Union[str, AfdCertificateType], 
                cipher_suite_set_type: Optional[Union[str, AfdCipherSuiteSetType]] = ..., 
                customized_cipher_suite_set: Optional[AFDDomainHttpsCustomizedCipherSuiteSet] = ..., 
                minimum_tls_version: Optional[Union[str, AfdMinimumTlsVersion]] = ..., 
                secret: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDDomainProperties(_Model):
        azure_dns_zone: Optional[ResourceReference]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        domain_validation_state: Optional[Union[str, DomainValidationState]]
        extended_properties: Optional[dict[str, str]]
        host_name: str
        pre_validated_custom_domain_resource_id: Optional[ResourceReference]
        profile_name: Optional[str]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]
        tls_settings: Optional[AFDDomainHttpsParameters]
        validation_properties: Optional[DomainValidationProperties]

        @overload
        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                extended_properties: Optional[dict[str, str]] = ..., 
                host_name: str, 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDDomainUpdateParameters(_Model):
        properties: Optional[AFDDomainUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDDomainUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDDomainUpdatePropertiesParameters(_Model):
        azure_dns_zone: Optional[ResourceReference]
        pre_validated_custom_domain_resource_id: Optional[ResourceReference]
        profile_name: Optional[str]
        tls_settings: Optional[AFDDomainHttpsParameters]

        @overload
        def __init__(
                self, 
                *, 
                azure_dns_zone: Optional[ResourceReference] = ..., 
                pre_validated_custom_domain_resource_id: Optional[ResourceReference] = ..., 
                tls_settings: Optional[AFDDomainHttpsParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDEndpoint(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AFDEndpointProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AFDEndpointProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDEndpointProperties(_Model):
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        enabled_state: Optional[Union[str, EnabledState]]
        host_name: Optional[str]
        profile_name: Optional[str]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDEndpointPropertiesUpdateParameters(_Model):
        enabled_state: Optional[Union[str, EnabledState]]
        profile_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enabled_state: Optional[Union[str, EnabledState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDEndpointProtocols(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"


    class azure.mgmt.cdn.models.AFDEndpointUpdateParameters(_Model):
        properties: Optional[AFDEndpointPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDEndpointPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDOrigin(ProxyResource):
        id: str
        name: str
        properties: Optional[AFDOriginProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDOriginProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[AFDOriginGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDOriginGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginGroupProperties(_Model):
        authentication: Optional[OriginAuthenticationProperties]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        health_probe_settings: Optional[HealthProbeParameters]
        load_balancing_settings: Optional[LoadBalancingSettingsParameters]
        profile_name: Optional[str]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]
        session_affinity_state: Optional[Union[str, EnabledState]]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[OriginAuthenticationProperties] = ..., 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginGroupUpdateParameters(_Model):
        properties: Optional[AFDOriginGroupUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDOriginGroupUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginGroupUpdatePropertiesParameters(_Model):
        authentication: Optional[OriginAuthenticationProperties]
        health_probe_settings: Optional[HealthProbeParameters]
        load_balancing_settings: Optional[LoadBalancingSettingsParameters]
        profile_name: Optional[str]
        session_affinity_state: Optional[Union[str, EnabledState]]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                authentication: Optional[OriginAuthenticationProperties] = ..., 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                load_balancing_settings: Optional[LoadBalancingSettingsParameters] = ..., 
                session_affinity_state: Optional[Union[str, EnabledState]] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginProperties(_Model):
        azure_origin: Optional[ResourceReference]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        enabled_state: Optional[Union[str, EnabledState]]
        enforce_certificate_name_check: Optional[bool]
        host_name: Optional[str]
        http_port: Optional[int]
        https_port: Optional[int]
        origin_group_name: Optional[str]
        origin_host_header: Optional[str]
        priority: Optional[int]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]
        shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginUpdateParameters(_Model):
        properties: Optional[AFDOriginUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AFDOriginUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.AFDOriginUpdatePropertiesParameters(_Model):
        azure_origin: Optional[ResourceReference]
        enabled_state: Optional[Union[str, EnabledState]]
        enforce_certificate_name_check: Optional[bool]
        host_name: Optional[str]
        http_port: Optional[int]
        https_port: Optional[int]
        origin_group_name: Optional[str]
        origin_host_header: Optional[str]
        priority: Optional[int]
        shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                azure_origin: Optional[ResourceReference] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                enforce_certificate_name_check: Optional[bool] = ..., 
                host_name: Optional[str] = ..., 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                shared_private_link_resource: Optional[SharedPrivateLinkResourceProperties] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AFDStateProperties(_Model):
        deployment_status: Optional[Union[str, DeploymentStatus]]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]


    class azure.mgmt.cdn.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        BLOCK = "Block"
        LOG = "Log"
        REDIRECT = "Redirect"


    class azure.mgmt.cdn.models.ActivatedResourceReference(_Model):
        id: Optional[str]
        is_active: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AfdCertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIRST_PARTY_MANAGED_CERTIFICATE = "AzureFirstPartyManagedCertificate"
        CUSTOMER_CERTIFICATE = "CustomerCertificate"
        MANAGED_CERTIFICATE = "ManagedCertificate"


    class azure.mgmt.cdn.models.AfdCipherSuiteSetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMIZED = "Customized"
        TLS10_2019 = "TLS10_2019"
        TLS12_2022 = "TLS12_2022"
        TLS12_2023 = "TLS12_2023"


    class azure.mgmt.cdn.models.AfdCustomizedCipherSuiteForTls12(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DHE_RSA_AES128_GCM_SHA256 = "DHE_RSA_AES128_GCM_SHA256"
        DHE_RSA_AES256_GCM_SHA384 = "DHE_RSA_AES256_GCM_SHA384"
        ECDHE_RSA_AES128_GCM_SHA256 = "ECDHE_RSA_AES128_GCM_SHA256"
        ECDHE_RSA_AES128_SHA256 = "ECDHE_RSA_AES128_SHA256"
        ECDHE_RSA_AES256_GCM_SHA384 = "ECDHE_RSA_AES256_GCM_SHA384"
        ECDHE_RSA_AES256_SHA384 = "ECDHE_RSA_AES256_SHA384"


    class azure.mgmt.cdn.models.AfdCustomizedCipherSuiteForTls13(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS_AES128_GCM_SHA256 = "TLS_AES_128_GCM_SHA256"
        TLS_AES256_GCM_SHA384 = "TLS_AES_256_GCM_SHA384"


    class azure.mgmt.cdn.models.AfdMinimumTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TLS10 = "TLS10"
        TLS12 = "TLS12"
        TLS13 = "TLS13"


    class azure.mgmt.cdn.models.AfdProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.cdn.models.AfdPurgeParameters(_Model):
        content_paths: list[str]
        domains: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                content_paths: list[str], 
                domains: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.AfdQueryStringCachingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE_QUERY_STRING = "IgnoreQueryString"
        IGNORE_SPECIFIED_QUERY_STRINGS = "IgnoreSpecifiedQueryStrings"
        INCLUDE_SPECIFIED_QUERY_STRINGS = "IncludeSpecifiedQueryStrings"
        USE_QUERY_STRING = "UseQueryString"


    class azure.mgmt.cdn.models.AfdRouteCacheConfiguration(_Model):
        compression_settings: Optional[CompressionSettings]
        query_parameters: Optional[str]
        query_string_caching_behavior: Optional[Union[str, AfdQueryStringCachingBehavior]]

        @overload
        def __init__(
                self, 
                *, 
                compression_settings: Optional[CompressionSettings] = ..., 
                query_parameters: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, AfdQueryStringCachingBehavior]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.Algorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SHA256 = "SHA256"


    class azure.mgmt.cdn.models.AutoGeneratedDomainNameLabelScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_REUSE = "NoReuse"
        RESOURCE_GROUP_REUSE = "ResourceGroupReuse"
        SUBSCRIPTION_REUSE = "SubscriptionReuse"
        TENANT_REUSE = "TenantReuse"


    class azure.mgmt.cdn.models.AzureFirstPartyManagedCertificateParameters(SecretParameters, discriminator='AzureFirstPartyManagedCertificate'):
        certificate_authority: Optional[str]
        expiration_date: Optional[str]
        secret_source: Optional[ResourceReference]
        subject: Optional[str]
        subject_alternative_names: Optional[list[str]]
        thumbprint: Optional[str]
        type: Literal[SecretType.AZURE_FIRST_PARTY_MANAGED_CERTIFICATE]

        @overload
        def __init__(
                self, 
                *, 
                subject_alternative_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.BatchRuleProperties(_Model):
        actions: Optional[list[DeliveryRuleAction]]
        conditions: Optional[list[DeliveryRuleCondition]]
        match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]]
        order: Optional[int]
        rule_name: str
        rule_set_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[DeliveryRuleAction]] = ..., 
                conditions: Optional[list[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]] = ..., 
                order: Optional[int] = ..., 
                rule_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CacheBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS_CACHE = "BypassCache"
        OVERRIDE = "Override"
        SET_IF_MISSING = "SetIfMissing"


    class azure.mgmt.cdn.models.CacheConfiguration(_Model):
        cache_behavior: Optional[Union[str, RuleCacheBehavior]]
        cache_duration: Optional[str]
        is_compression_enabled: Optional[Union[str, RuleIsCompressionEnabled]]
        query_parameters: Optional[str]
        query_string_caching_behavior: Optional[Union[str, RuleQueryStringCachingBehavior]]

        @overload
        def __init__(
                self, 
                *, 
                cache_behavior: Optional[Union[str, RuleCacheBehavior]] = ..., 
                cache_duration: Optional[str] = ..., 
                is_compression_enabled: Optional[Union[str, RuleIsCompressionEnabled]] = ..., 
                query_parameters: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, RuleQueryStringCachingBehavior]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CacheExpirationActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleCacheExpirationActionParameters'):
        cache_behavior: Union[str, CacheBehavior]
        cache_duration: Optional[str]
        cache_type: Union[str, CacheType]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                cache_behavior: Union[str, CacheBehavior], 
                cache_duration: Optional[str] = ..., 
                cache_type: Union[str, CacheType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CacheKeyQueryStringActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleCacheKeyQueryStringBehaviorActionParameters'):
        query_parameters: Optional[str]
        query_string_behavior: Union[str, QueryStringBehavior]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                query_parameters: Optional[str] = ..., 
                query_string_behavior: Union[str, QueryStringBehavior]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CacheType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"


    class azure.mgmt.cdn.models.CanMigrateDefaultSku(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_AZURE_FRONT_DOOR = "Premium_AzureFrontDoor"
        STANDARD_AZURE_FRONT_DOOR = "Standard_AzureFrontDoor"


    class azure.mgmt.cdn.models.CanMigrateParameters(_Model):
        classic_resource_reference: ResourceReference

        @overload
        def __init__(
                self, 
                *, 
                classic_resource_reference: ResourceReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CanMigrateProperties(_Model):
        can_migrate: Optional[bool]
        default_sku: Optional[Union[str, CanMigrateDefaultSku]]
        errors: Optional[list[MigrationErrorType]]

        @overload
        def __init__(
                self, 
                *, 
                errors: Optional[list[MigrationErrorType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CanMigrateResult(_Model):
        id: Optional[str]
        properties: Optional[CanMigrateProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CanMigrateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.CdnCertificateSourceParameters(CertificateSourceParameters, discriminator='CdnCertificateSourceParameters'):
        certificate_type: Union[str, CertificateType]
        type_name: Literal[CertificateSourceParametersType.CDN_CERTIFICATE_SOURCE_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                certificate_type: Union[str, CertificateType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CdnEndpoint(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CdnManagedHttpsParameters(CustomDomainHttpsParameters, discriminator='Cdn'):
        certificate_source: Literal[CertificateSource.CDN]
        certificate_source_parameters: CdnCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]

        @overload
        def __init__(
                self, 
                *, 
                certificate_source_parameters: CdnCertificateSourceParameters, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CdnMigrationToAfdParameters(_Model):
        migration_endpoint_mappings: Optional[list[MigrationEndpointMapping]]
        sku: Sku

        @overload
        def __init__(
                self, 
                *, 
                migration_endpoint_mappings: Optional[list[MigrationEndpointMapping]] = ..., 
                sku: Sku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicy(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[CdnWebApplicationFirewallPolicyProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                location: str, 
                properties: Optional[CdnWebApplicationFirewallPolicyProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicyPatchParameters(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CdnWebApplicationFirewallPolicyProperties(_Model):
        custom_rules: Optional[CustomRuleList]
        endpoint_links: Optional[list[CdnEndpoint]]
        extended_properties: Optional[dict[str, str]]
        managed_rules: Optional[ManagedRuleSetList]
        policy_settings: Optional[PolicySettings]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rate_limit_rules: Optional[RateLimitRuleList]
        resource_state: Optional[Union[str, PolicyResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                custom_rules: Optional[CustomRuleList] = ..., 
                extended_properties: Optional[dict[str, str]] = ..., 
                managed_rules: Optional[ManagedRuleSetList] = ..., 
                policy_settings: Optional[PolicySettings] = ..., 
                rate_limit_rules: Optional[RateLimitRuleList] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CertificateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        CDN = "Cdn"


    class azure.mgmt.cdn.models.CertificateSourceParameters(_Model):
        type_name: str

        @overload
        def __init__(
                self, 
                *, 
                type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CertificateSourceParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDN_CERTIFICATE_SOURCE_PARAMETERS = "CdnCertificateSourceParameters"
        KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS = "KeyVaultCertificateSourceParameters"


    class azure.mgmt.cdn.models.CertificateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEDICATED = "Dedicated"
        SHARED = "Shared"


    class azure.mgmt.cdn.models.CheckEndpointNameAvailabilityInput(_Model):
        auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]]
        name: str
        type: Union[str, ResourceType]

        @overload
        def __init__(
                self, 
                *, 
                auto_generated_domain_name_label_scope: Optional[Union[str, AutoGeneratedDomainNameLabelScope]] = ..., 
                name: str, 
                type: Union[str, ResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CheckEndpointNameAvailabilityOutput(_Model):
        available_hostname: Optional[str]
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]


    class azure.mgmt.cdn.models.CheckHostNameAvailabilityInput(_Model):
        host_name: str

        @overload
        def __init__(
                self, 
                *, 
                host_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CheckNameAvailabilityInput(_Model):
        name: str
        type: Union[str, ResourceType]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                type: Union[str, ResourceType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CheckNameAvailabilityOutput(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[str]


    class azure.mgmt.cdn.models.CidrIpAddress(_Model):
        base_ip_address: Optional[str]
        prefix_length: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                base_ip_address: Optional[str] = ..., 
                prefix_length: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ClientPortMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleClientPortConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, ClientPortOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, ClientPortOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems(_Model):
        date_time: Optional[datetime]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                date_time: Optional[datetime] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems(_Model):
        date_time: Optional[datetime]
        value: Optional[float]

        @overload
        def __init__(
                self, 
                *, 
                date_time: Optional[datetime] = ..., 
                value: Optional[float] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems(_Model):
        metric: Optional[str]
        percentage: Optional[float]
        value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                metric: Optional[str] = ..., 
                percentage: Optional[float] = ..., 
                value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CompressionSettings(_Model):
        content_types_to_compress: Optional[list[str]]
        is_compression_enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[list[str]] = ..., 
                is_compression_enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ContinentsResponse(_Model):
        continents: Optional[list[ContinentsResponseContinentsItem]]
        country_or_regions: Optional[list[ContinentsResponseCountryOrRegionsItem]]

        @overload
        def __init__(
                self, 
                *, 
                continents: Optional[list[ContinentsResponseContinentsItem]] = ..., 
                country_or_regions: Optional[list[ContinentsResponseCountryOrRegionsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ContinentsResponseContinentsItem(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ContinentsResponseCountryOrRegionsItem(_Model):
        continent_id: Optional[str]
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                continent_id: Optional[str] = ..., 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CookiesMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleCookiesConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, CookiesOperator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, CookiesOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.cdn.models.CustomDomain(ProxyResource):
        id: str
        name: str
        properties: Optional[CustomDomainProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomDomainProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.CustomDomainHttpsParameters(_Model):
        certificate_source: str
        minimum_tls_version: Optional[Union[str, MinimumTlsVersion]]
        protocol_type: Union[str, ProtocolType]

        @overload
        def __init__(
                self, 
                *, 
                certificate_source: str, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CustomDomainParameters(_Model):
        properties: Optional[CustomDomainPropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CustomDomainPropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.CustomDomainProperties(_Model):
        custom_https_parameters: Optional[CustomDomainHttpsParameters]
        custom_https_provisioning_state: Optional[Union[str, CustomHttpsProvisioningState]]
        custom_https_provisioning_substate: Optional[Union[str, CustomHttpsProvisioningSubstate]]
        host_name: str
        provisioning_state: Optional[Union[str, CustomHttpsProvisioningState]]
        resource_state: Optional[Union[str, CustomDomainResourceState]]
        validation_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_https_parameters: Optional[CustomDomainHttpsParameters] = ..., 
                host_name: str, 
                validation_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CustomDomainPropertiesParameters(_Model):
        host_name: str

        @overload
        def __init__(
                self, 
                *, 
                host_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.CustomRule(_Model):
        action: Union[str, ActionType]
        enabled_state: Optional[Union[str, CustomRuleEnabledState]]
        match_conditions: list[MatchCondition]
        name: str
        priority: int

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, ActionType], 
                enabled_state: Optional[Union[str, CustomRuleEnabledState]] = ..., 
                match_conditions: list[MatchCondition], 
                name: str, 
                priority: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CustomRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.CustomRuleList(_Model):
        rules: Optional[list[CustomRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[CustomRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.CustomerCertificateParameters(SecretParameters, discriminator='CustomerCertificate'):
        certificate_authority: Optional[str]
        expiration_date: Optional[str]
        secret_source: ResourceReference
        secret_version: Optional[str]
        subject: Optional[str]
        subject_alternative_names: Optional[list[str]]
        thumbprint: Optional[str]
        type: Literal[SecretType.CUSTOMER_CERTIFICATE]
        use_latest_version: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                secret_source: ResourceReference, 
                secret_version: Optional[str] = ..., 
                use_latest_version: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedCustomDomain(_Model):
        name: str
        properties: Optional[DeepCreatedCustomDomainProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[DeepCreatedCustomDomainProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedCustomDomainProperties(_Model):
        host_name: str
        validation_data: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                host_name: str, 
                validation_data: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedOrigin(_Model):
        name: str
        properties: Optional[DeepCreatedOriginProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[DeepCreatedOriginProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedOriginGroup(_Model):
        name: str
        properties: Optional[DeepCreatedOriginGroupProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                properties: Optional[DeepCreatedOriginGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedOriginGroupProperties(_Model):
        health_probe_settings: Optional[HealthProbeParameters]
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: list[ResourceReference], 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeepCreatedOriginProperties(_Model):
        enabled: Optional[bool]
        host_name: str
        http_port: Optional[int]
        https_port: Optional[int]
        origin_host_header: Optional[str]
        priority: Optional[int]
        private_endpoint_status: Optional[Union[str, PrivateEndpointStatus]]
        private_link_alias: Optional[str]
        private_link_approval_message: Optional[str]
        private_link_location: Optional[str]
        private_link_resource_id: Optional[str]
        weight: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: str, 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeleteRule(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NO_ACTION = "NoAction"


    class azure.mgmt.cdn.models.DeliveryRule(_Model):
        actions: list[DeliveryRuleAction]
        conditions: Optional[list[DeliveryRuleCondition]]
        name: Optional[str]
        order: int

        @overload
        def __init__(
                self, 
                *, 
                actions: list[DeliveryRuleAction], 
                conditions: Optional[list[DeliveryRuleCondition]] = ..., 
                name: Optional[str] = ..., 
                order: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleAction(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.DeliveryRuleActionParameters(_Model):
        type_name: str

        @overload
        def __init__(
                self, 
                *, 
                type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleActionParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS = "DeliveryRuleCacheExpirationActionParameters"
        DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS = "DeliveryRuleCacheKeyQueryStringBehaviorActionParameters"
        DELIVERY_RULE_HEADER_ACTION_PARAMETERS = "DeliveryRuleHeaderActionParameters"
        DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleOriginGroupOverrideActionParameters"
        DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleRouteConfigurationOverrideActionParameters"
        DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS = "DeliveryRuleUrlRedirectActionParameters"
        DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS = "DeliveryRuleUrlRewriteActionParameters"
        DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS = "DeliveryRuleUrlSigningActionParameters"


    class azure.mgmt.cdn.models.DeliveryRuleCacheExpirationAction(DeliveryRuleAction, discriminator='CacheExpiration'):
        name: Literal[DeliveryRuleActionEnum.CACHE_EXPIRATION]
        parameters: CacheExpirationActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: CacheExpirationActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleCacheKeyQueryStringAction(DeliveryRuleAction, discriminator='CacheKeyQueryString'):
        name: Literal[DeliveryRuleActionEnum.CACHE_KEY_QUERY_STRING]
        parameters: CacheKeyQueryStringActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: CacheKeyQueryStringActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleClientPortCondition(DeliveryRuleCondition, discriminator='ClientPort'):
        name: Literal[MatchVariable.CLIENT_PORT]
        parameters: ClientPortMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: ClientPortMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleCondition(_Model):
        name: str

        @overload
        def __init__(
                self, 
                *, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleConditionParameters(_Model):
        type_name: str

        @overload
        def __init__(
                self, 
                *, 
                type_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleConditionParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS = "DeliveryRuleClientPortConditionParameters"
        DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS = "DeliveryRuleCookiesConditionParameters"
        DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS = "DeliveryRuleHostNameConditionParameters"
        DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS = "DeliveryRuleHttpVersionConditionParameters"
        DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS = "DeliveryRuleIsDeviceConditionParameters"
        DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS = "DeliveryRulePostArgsConditionParameters"
        DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS = "DeliveryRuleQueryStringConditionParameters"
        DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS = "DeliveryRuleRemoteAddressConditionParameters"
        DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS = "DeliveryRuleRequestBodyConditionParameters"
        DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS = "DeliveryRuleRequestHeaderConditionParameters"
        DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS = "DeliveryRuleRequestMethodConditionParameters"
        DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS = "DeliveryRuleRequestSchemeConditionParameters"
        DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS = "DeliveryRuleRequestUriConditionParameters"
        DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS = "DeliveryRuleServerPortConditionParameters"
        DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS = "DeliveryRuleSocketAddrConditionParameters"
        DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS = "DeliveryRuleSslProtocolConditionParameters"
        DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS = "DeliveryRuleUrlFilenameConditionParameters"
        DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlFileExtensionMatchConditionParameters"
        DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlPathMatchConditionParameters"


    class azure.mgmt.cdn.models.DeliveryRuleCookiesCondition(DeliveryRuleCondition, discriminator='Cookies'):
        name: Literal[MatchVariable.COOKIES]
        parameters: CookiesMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: CookiesMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleHostNameCondition(DeliveryRuleCondition, discriminator='HostName'):
        name: Literal[MatchVariable.HOST_NAME]
        parameters: HostNameMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: HostNameMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleHttpVersionCondition(DeliveryRuleCondition, discriminator='HttpVersion'):
        name: Literal[MatchVariable.HTTP_VERSION]
        parameters: HttpVersionMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: HttpVersionMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleIsDeviceCondition(DeliveryRuleCondition, discriminator='IsDevice'):
        name: Literal[MatchVariable.IS_DEVICE]
        parameters: IsDeviceMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: IsDeviceMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRulePostArgsCondition(DeliveryRuleCondition, discriminator='PostArgs'):
        name: Literal[MatchVariable.POST_ARGS]
        parameters: PostArgsMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: PostArgsMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleQueryStringCondition(DeliveryRuleCondition, discriminator='QueryString'):
        name: Literal[MatchVariable.QUERY_STRING]
        parameters: QueryStringMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: QueryStringMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRemoteAddressCondition(DeliveryRuleCondition, discriminator='RemoteAddress'):
        name: Literal[MatchVariable.REMOTE_ADDRESS]
        parameters: RemoteAddressMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RemoteAddressMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestBodyCondition(DeliveryRuleCondition, discriminator='RequestBody'):
        name: Literal[MatchVariable.REQUEST_BODY]
        parameters: RequestBodyMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RequestBodyMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestHeaderAction(DeliveryRuleAction, discriminator='ModifyRequestHeader'):
        name: Literal[DeliveryRuleActionEnum.MODIFY_REQUEST_HEADER]
        parameters: HeaderActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: HeaderActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestHeaderCondition(DeliveryRuleCondition, discriminator='RequestHeader'):
        name: Literal[MatchVariable.REQUEST_HEADER]
        parameters: RequestHeaderMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RequestHeaderMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestMethodCondition(DeliveryRuleCondition, discriminator='RequestMethod'):
        name: Literal[MatchVariable.REQUEST_METHOD]
        parameters: RequestMethodMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RequestMethodMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestSchemeCondition(DeliveryRuleCondition, discriminator='RequestScheme'):
        name: Literal[MatchVariable.REQUEST_SCHEME]
        parameters: RequestSchemeMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RequestSchemeMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRequestUriCondition(DeliveryRuleCondition, discriminator='RequestUri'):
        name: Literal[MatchVariable.REQUEST_URI]
        parameters: RequestUriMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RequestUriMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleResponseHeaderAction(DeliveryRuleAction, discriminator='ModifyResponseHeader'):
        name: Literal[DeliveryRuleActionEnum.MODIFY_RESPONSE_HEADER]
        parameters: HeaderActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: HeaderActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleRouteConfigurationOverrideAction(DeliveryRuleAction, discriminator='RouteConfigurationOverride'):
        name: Literal[DeliveryRuleActionEnum.ROUTE_CONFIGURATION_OVERRIDE]
        parameters: RouteConfigurationOverrideActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: RouteConfigurationOverrideActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleServerPortCondition(DeliveryRuleCondition, discriminator='ServerPort'):
        name: Literal[MatchVariable.SERVER_PORT]
        parameters: ServerPortMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: ServerPortMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleSocketAddrCondition(DeliveryRuleCondition, discriminator='SocketAddr'):
        name: Literal[MatchVariable.SOCKET_ADDR]
        parameters: SocketAddrMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: SocketAddrMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleSslProtocolCondition(DeliveryRuleCondition, discriminator='SslProtocol'):
        name: Literal[MatchVariable.SSL_PROTOCOL]
        parameters: SslProtocolMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: SslProtocolMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleUrlFileExtensionCondition(DeliveryRuleCondition, discriminator='UrlFileExtension'):
        name: Literal[MatchVariable.URL_FILE_EXTENSION]
        parameters: UrlFileExtensionMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlFileExtensionMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleUrlFileNameCondition(DeliveryRuleCondition, discriminator='UrlFileName'):
        name: Literal[MatchVariable.URL_FILE_NAME]
        parameters: UrlFileNameMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlFileNameMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeliveryRuleUrlPathCondition(DeliveryRuleCondition, discriminator='UrlPath'):
        name: Literal[MatchVariable.URL_PATH]
        parameters: UrlPathMatchConditionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlPathMatchConditionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DeploymentStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.cdn.models.DestinationProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "Http"
        HTTPS = "Https"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.cdn.models.DimensionProperties(_Model):
        display_name: Optional[str]
        internal_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                internal_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.DomainValidationProperties(_Model):
        expiration_date: Optional[str]
        validation_token: Optional[str]


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
        name: str
        properties: Optional[EdgeNodeProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EdgeNodeProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.EdgeNodeProperties(_Model):
        ip_address_groups: list[IpAddressGroup]

        @overload
        def __init__(
                self, 
                *, 
                ip_address_groups: list[IpAddressGroup]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.EnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.Endpoint(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[EndpointProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[EndpointProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.EndpointProperties(EndpointPropertiesUpdateParameters):
        content_types_to_compress: list[str]
        custom_domains: Optional[list[DeepCreatedCustomDomain]]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geo_filters: list[GeoFilter]
        host_name: Optional[str]
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        origin_groups: Optional[list[DeepCreatedOriginGroup]]
        origin_host_header: str
        origin_path: str
        origins: list[DeepCreatedOrigin]
        probe_path: str
        provisioning_state: Optional[Union[str, EndpointProvisioningState]]
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        resource_state: Optional[Union[str, EndpointResourceState]]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink

        @overload
        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[list[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[list[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: Optional[bool] = ..., 
                is_https_allowed: Optional[bool] = ..., 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_groups: Optional[list[DeepCreatedOriginGroup]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                origins: list[DeepCreatedOrigin], 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                url_signing_keys: Optional[list[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParameters(_Model):
        content_types_to_compress: Optional[list[str]]
        default_origin_group: Optional[ResourceReference]
        delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy]
        geo_filters: Optional[list[GeoFilter]]
        is_compression_enabled: Optional[bool]
        is_http_allowed: Optional[bool]
        is_https_allowed: Optional[bool]
        optimization_type: Optional[Union[str, OptimizationType]]
        origin_host_header: Optional[str]
        origin_path: Optional[str]
        probe_path: Optional[str]
        query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]]
        url_signing_keys: Optional[list[UrlSigningKey]]
        web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink]

        @overload
        def __init__(
                self, 
                *, 
                content_types_to_compress: Optional[list[str]] = ..., 
                default_origin_group: Optional[ResourceReference] = ..., 
                delivery_policy: Optional[EndpointPropertiesUpdateParametersDeliveryPolicy] = ..., 
                geo_filters: Optional[list[GeoFilter]] = ..., 
                is_compression_enabled: Optional[bool] = ..., 
                is_http_allowed: Optional[bool] = ..., 
                is_https_allowed: Optional[bool] = ..., 
                optimization_type: Optional[Union[str, OptimizationType]] = ..., 
                origin_host_header: Optional[str] = ..., 
                origin_path: Optional[str] = ..., 
                probe_path: Optional[str] = ..., 
                query_string_caching_behavior: Optional[Union[str, QueryStringCachingBehavior]] = ..., 
                url_signing_keys: Optional[list[UrlSigningKey]] = ..., 
                web_application_firewall_policy_link: Optional[EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParametersDeliveryPolicy(_Model):
        description: Optional[str]
        rules: list[DeliveryRule]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                rules: list[DeliveryRule]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.EndpointUpdateParameters(_Model):
        properties: Optional[EndpointPropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EndpointPropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.cdn.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.cdn.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ForwardingProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTPS_ONLY = "HttpsOnly"
        HTTP_ONLY = "HttpOnly"
        MATCH_REQUEST = "MatchRequest"


    class azure.mgmt.cdn.models.GeoFilter(_Model):
        action: Union[str, GeoFilterActions]
        country_codes: list[str]
        relative_path: str

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, GeoFilterActions], 
                country_codes: list[str], 
                relative_path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.GeoFilterActions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        BLOCK = "Block"


    class azure.mgmt.cdn.models.HeaderAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPEND = "Append"
        DELETE = "Delete"
        OVERWRITE = "Overwrite"


    class azure.mgmt.cdn.models.HeaderActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleHeaderActionParameters'):
        header_action: Union[str, HeaderAction]
        header_name: str
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_HEADER_ACTION_PARAMETERS]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                header_action: Union[str, HeaderAction], 
                header_name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.HealthProbeParameters(_Model):
        probe_interval_in_seconds: Optional[int]
        probe_path: Optional[str]
        probe_protocol: Optional[Union[str, ProbeProtocol]]
        probe_request_type: Optional[Union[str, HealthProbeRequestType]]

        @overload
        def __init__(
                self, 
                *, 
                probe_interval_in_seconds: Optional[int] = ..., 
                probe_path: Optional[str] = ..., 
                probe_protocol: Optional[Union[str, ProbeProtocol]] = ..., 
                probe_request_type: Optional[Union[str, HealthProbeRequestType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.HealthProbeRequestType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GET = "GET"
        HEAD = "HEAD"
        NOT_SET = "NotSet"


    class azure.mgmt.cdn.models.HostNameMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleHostNameConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, HostNameOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, HostNameOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.HttpErrorRangeParameters(_Model):
        begin: Optional[int]
        end: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                begin: Optional[int] = ..., 
                end: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.HttpVersionMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleHttpVersionConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, HttpVersionOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, HttpVersionOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.HttpVersionOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.HttpsRedirect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.IpAddressGroup(_Model):
        delivery_region: Optional[str]
        ipv4_addresses: Optional[list[CidrIpAddress]]
        ipv6_addresses: Optional[list[CidrIpAddress]]

        @overload
        def __init__(
                self, 
                *, 
                delivery_region: Optional[str] = ..., 
                ipv4_addresses: Optional[list[CidrIpAddress]] = ..., 
                ipv6_addresses: Optional[list[CidrIpAddress]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.IsDeviceMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleIsDeviceConditionParameters'):
        match_values: Optional[list[Union[str, IsDeviceMatchConditionParametersMatchValuesItem]]]
        negate_condition: Optional[bool]
        operator: Union[str, IsDeviceOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[Union[str, IsDeviceMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, IsDeviceOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.IsDeviceMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESKTOP = "Desktop"
        MOBILE = "Mobile"


    class azure.mgmt.cdn.models.IsDeviceOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.KeyVaultCertificateSourceParameters(CertificateSourceParameters, discriminator='KeyVaultCertificateSourceParameters'):
        delete_rule: Union[str, DeleteRule]
        resource_group_name: str
        secret_name: str
        secret_version: Optional[str]
        subscription_id: str
        type_name: Literal[CertificateSourceParametersType.KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS]
        update_rule: Union[str, UpdateRule]
        vault_name: str

        @overload
        def __init__(
                self, 
                *, 
                delete_rule: Union[str, DeleteRule], 
                resource_group_name: str, 
                secret_name: str, 
                secret_version: Optional[str] = ..., 
                subscription_id: str, 
                update_rule: Union[str, UpdateRule], 
                vault_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.KeyVaultSigningKeyParameters(_Model):
        resource_group_name: str
        secret_name: str
        secret_version: str
        subscription_id: str
        type_name: Union[str, KeyVaultSigningKeyParametersTypeName]
        vault_name: str

        @overload
        def __init__(
                self, 
                *, 
                resource_group_name: str, 
                secret_name: str, 
                secret_version: str, 
                subscription_id: str, 
                type_name: Union[str, KeyVaultSigningKeyParametersTypeName], 
                vault_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.KeyVaultSigningKeyParametersTypeName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEY_VAULT_SIGNING_KEY_PARAMETERS = "KeyVaultSigningKeyParameters"


    class azure.mgmt.cdn.models.LinkToDefaultDomain(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.LoadBalancingSettingsParameters(_Model):
        additional_latency_in_milliseconds: Optional[int]
        sample_size: Optional[int]
        successful_samples_required: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                additional_latency_in_milliseconds: Optional[int] = ..., 
                sample_size: Optional[int] = ..., 
                successful_samples_required: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.LoadParameters(_Model):
        content_paths: list[str]

        @overload
        def __init__(
                self, 
                *, 
                content_paths: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.LogSpecification(_Model):
        blob_duration: Optional[str]
        display_name: Optional[str]
        log_filter_pattern: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                log_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedCertificateParameters(SecretParameters, discriminator='ManagedCertificate'):
        expiration_date: Optional[str]
        subject: Optional[str]
        type: Literal[SecretType.MANAGED_CERTIFICATE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedRuleDefinition(_Model):
        description: Optional[str]
        rule_id: Optional[str]


    class azure.mgmt.cdn.models.ManagedRuleEnabledState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.ManagedRuleGroupDefinition(_Model):
        description: Optional[str]
        rule_group_name: Optional[str]
        rules: Optional[list[ManagedRuleDefinition]]


    class azure.mgmt.cdn.models.ManagedRuleGroupOverride(_Model):
        rule_group_name: str
        rules: Optional[list[ManagedRuleOverride]]

        @overload
        def __init__(
                self, 
                *, 
                rule_group_name: str, 
                rules: Optional[list[ManagedRuleOverride]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedRuleOverride(_Model):
        action: Optional[Union[str, ActionType]]
        enabled_state: Optional[Union[str, ManagedRuleEnabledState]]
        rule_id: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, ActionType]] = ..., 
                enabled_state: Optional[Union[str, ManagedRuleEnabledState]] = ..., 
                rule_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedRuleSet(_Model):
        anomaly_score: Optional[int]
        rule_group_overrides: Optional[list[ManagedRuleGroupOverride]]
        rule_set_type: str
        rule_set_version: str

        @overload
        def __init__(
                self, 
                *, 
                anomaly_score: Optional[int] = ..., 
                rule_group_overrides: Optional[list[ManagedRuleGroupOverride]] = ..., 
                rule_set_type: str, 
                rule_set_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedRuleSetDefinition(Resource):
        id: str
        name: str
        properties: Optional[ManagedRuleSetDefinitionProperties]
        sku: Optional[Sku]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagedRuleSetDefinitionProperties] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.ManagedRuleSetDefinitionProperties(_Model):
        provisioning_state: Optional[str]
        rule_groups: Optional[list[ManagedRuleGroupDefinition]]
        rule_set_type: Optional[str]
        rule_set_version: Optional[str]


    class azure.mgmt.cdn.models.ManagedRuleSetList(_Model):
        managed_rule_sets: Optional[list[ManagedRuleSet]]

        @overload
        def __init__(
                self, 
                *, 
                managed_rule_sets: Optional[list[ManagedRuleSet]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.cdn.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.cdn.models.MatchCondition(_Model):
        match_value: list[str]
        match_variable: Union[str, WafMatchVariable]
        negate_condition: Optional[bool]
        operator: Union[str, Operator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, TransformType]]]

        @overload
        def __init__(
                self, 
                *, 
                match_value: list[str], 
                match_variable: Union[str, WafMatchVariable], 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, Operator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, TransformType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.MetricAvailability(_Model):
        blob_duration: Optional[str]
        time_grain: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                time_grain: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MetricSpecification(_Model):
        aggregation_type: Optional[str]
        availabilities: Optional[list[MetricAvailability]]
        dimensions: Optional[list[DimensionProperties]]
        display_description: Optional[str]
        display_name: Optional[str]
        fill_gap_with_zero: Optional[bool]
        is_internal: Optional[bool]
        metric_filter_pattern: Optional[str]
        name: Optional[str]
        supported_time_grain_types: Optional[list[str]]
        unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                aggregation_type: Optional[str] = ..., 
                availabilities: Optional[list[MetricAvailability]] = ..., 
                dimensions: Optional[list[DimensionProperties]] = ..., 
                display_description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                fill_gap_with_zero: Optional[bool] = ..., 
                is_internal: Optional[bool] = ..., 
                metric_filter_pattern: Optional[str] = ..., 
                name: Optional[str] = ..., 
                supported_time_grain_types: Optional[list[str]] = ..., 
                unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MetricsGranularity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        P1_D = "P1D"
        PT1_H = "PT1H"
        PT5_M = "PT5M"


    class azure.mgmt.cdn.models.MetricsResponse(_Model):
        date_time_begin: Optional[datetime]
        date_time_end: Optional[datetime]
        granularity: Optional[Union[str, MetricsGranularity]]
        series: Optional[list[MetricsResponseSeriesItem]]

        @overload
        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                granularity: Optional[Union[str, MetricsGranularity]] = ..., 
                series: Optional[list[MetricsResponseSeriesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MetricsResponseSeriesItem(_Model):
        data: Optional[list[Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems]]
        groups: Optional[list[MetricsResponseSeriesPropertiesItemsItem]]
        metric: Optional[str]
        unit: Optional[Union[str, MetricsSeriesUnit]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[Components1Gs0LlpSchemasMetricsresponsePropertiesSeriesItemsPropertiesDataItems]] = ..., 
                groups: Optional[list[MetricsResponseSeriesPropertiesItemsItem]] = ..., 
                metric: Optional[str] = ..., 
                unit: Optional[Union[str, MetricsSeriesUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MetricsResponseSeriesPropertiesItemsItem(_Model):
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


    class azure.mgmt.cdn.models.MetricsSeriesUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BITS_PER_SECOND = "bitsPerSecond"
        BYTES = "bytes"
        COUNT = "count"
        MILLI_SECONDS = "milliSeconds"


    class azure.mgmt.cdn.models.MigrateResult(_Model):
        id: Optional[str]
        properties: Optional[MigrateResultProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrateResultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.MigrateResultProperties(_Model):
        migrated_profile_resource_id: Optional[ResourceReference]


    class azure.mgmt.cdn.models.MigrationEndpointMapping(_Model):
        migrated_from: Optional[str]
        migrated_to: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                migrated_from: Optional[str] = ..., 
                migrated_to: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MigrationErrorType(_Model):
        code: Optional[str]
        error_message: Optional[str]
        next_steps: Optional[str]
        resource_name: Optional[str]


    class azure.mgmt.cdn.models.MigrationParameters(_Model):
        classic_resource_reference: ResourceReference
        migration_web_application_firewall_mappings: Optional[list[MigrationWebApplicationFirewallMapping]]
        profile_name: str
        sku: Sku

        @overload
        def __init__(
                self, 
                *, 
                classic_resource_reference: ResourceReference, 
                migration_web_application_firewall_mappings: Optional[list[MigrationWebApplicationFirewallMapping]] = ..., 
                profile_name: str, 
                sku: Sku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MigrationWebApplicationFirewallMapping(_Model):
        migrated_from: Optional[ResourceReference]
        migrated_to: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                migrated_from: Optional[ResourceReference] = ..., 
                migrated_to: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.MinimumTlsVersion(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TLS10 = "TLS10"
        TLS12 = "TLS12"


    class azure.mgmt.cdn.models.Operation(_Model):
        display: Optional[OperationDisplay]
        is_data_action: Optional[bool]
        name: Optional[str]
        operation_properties: Optional[OperationProperties]
        origin: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                operation_properties: Optional[OperationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.cdn.models.OperationProperties(_Model):
        service_specification: Optional[ServiceSpecification]

        @overload
        def __init__(
                self, 
                *, 
                service_specification: Optional[ServiceSpecification] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        name: str
        properties: Optional[OriginProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OriginProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.OriginAuthenticationProperties(_Model):
        scope: Optional[str]
        type: Optional[Union[str, OriginAuthenticationType]]
        user_assigned_identity: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                scope: Optional[str] = ..., 
                type: Optional[Union[str, OriginAuthenticationType]] = ..., 
                user_assigned_identity: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.OriginAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED_IDENTITY = "SystemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "UserAssignedIdentity"


    class azure.mgmt.cdn.models.OriginGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[OriginGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OriginGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.OriginGroupOverride(_Model):
        forwarding_protocol: Optional[Union[str, ForwardingProtocol]]
        origin_group: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                origin_group: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.OriginGroupOverrideAction(DeliveryRuleAction, discriminator='OriginGroupOverride'):
        name: Literal[DeliveryRuleActionEnum.ORIGIN_GROUP_OVERRIDE]
        parameters: OriginGroupOverrideActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: OriginGroupOverrideActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.OriginGroupOverrideActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleOriginGroupOverrideActionParameters'):
        origin_group: ResourceReference
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                origin_group: ResourceReference
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.OriginGroupProperties(OriginGroupUpdatePropertiesParameters):
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        provisioning_state: Optional[Union[str, OriginGroupProvisioningState]]
        resource_state: Optional[Union[str, OriginGroupResourceState]]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int

        @overload
        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[list[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.OriginGroupUpdateParameters(_Model):
        properties: Optional[OriginGroupUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OriginGroupUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.OriginGroupUpdatePropertiesParameters(_Model):
        health_probe_settings: Optional[HealthProbeParameters]
        origins: Optional[list[ResourceReference]]
        response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                health_probe_settings: Optional[HealthProbeParameters] = ..., 
                origins: Optional[list[ResourceReference]] = ..., 
                response_based_origin_error_detection_settings: Optional[ResponseBasedOriginErrorDetectionParameters] = ..., 
                traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.OriginProperties(OriginUpdatePropertiesParameters):
        enabled: bool
        host_name: str
        http_port: int
        https_port: int
        origin_host_header: str
        priority: int
        private_endpoint_status: Optional[Union[str, PrivateEndpointStatus]]
        private_link_alias: str
        private_link_approval_message: str
        private_link_location: str
        private_link_resource_id: str
        provisioning_state: Optional[Union[str, OriginProvisioningState]]
        resource_state: Optional[Union[str, OriginResourceState]]
        weight: int

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                host_name: str, 
                http_port: Optional[int] = ..., 
                https_port: Optional[int] = ..., 
                origin_host_header: Optional[str] = ..., 
                priority: Optional[int] = ..., 
                private_link_alias: Optional[str] = ..., 
                private_link_approval_message: Optional[str] = ..., 
                private_link_location: Optional[str] = ..., 
                private_link_resource_id: Optional[str] = ..., 
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.OriginUpdateParameters(_Model):
        properties: Optional[OriginUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OriginUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.OriginUpdatePropertiesParameters(_Model):
        enabled: Optional[bool]
        host_name: Optional[str]
        http_port: Optional[int]
        https_port: Optional[int]
        origin_host_header: Optional[str]
        priority: Optional[int]
        private_link_alias: Optional[str]
        private_link_approval_message: Optional[str]
        private_link_location: Optional[str]
        private_link_resource_id: Optional[str]
        weight: Optional[int]

        @overload
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
                weight: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.PolicySettings(_Model):
        default_custom_block_response_body: Optional[str]
        default_custom_block_response_status_code: Optional[Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]]
        default_redirect_url: Optional[str]
        enabled_state: Optional[Union[str, PolicyEnabledState]]
        mode: Optional[Union[str, PolicyMode]]

        @overload
        def __init__(
                self, 
                *, 
                default_custom_block_response_body: Optional[str] = ..., 
                default_custom_block_response_status_code: Optional[Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]] = ..., 
                default_redirect_url: Optional[str] = ..., 
                enabled_state: Optional[Union[str, PolicyEnabledState]] = ..., 
                mode: Optional[Union[str, PolicyMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.PolicySettingsDefaultCustomBlockResponseStatusCode(int, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUR_HUNDRED_FIVE = 405
        FOUR_HUNDRED_SIX = 406
        FOUR_HUNDRED_THREE = 403
        FOUR_HUNDRED_TWENTY_NINE = 429
        TWO_HUNDRED = 200


    class azure.mgmt.cdn.models.PostArgsMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRulePostArgsConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, PostArgsOperator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, PostArgsOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        identity: Optional[ManagedServiceIdentity]
        kind: Optional[str]
        location: str
        name: str
        properties: Optional[ProfileProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[ProfileProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.ProfileChangeSkuWafMapping(_Model):
        change_to_waf_policy: ResourceReference
        security_policy_name: str

        @overload
        def __init__(
                self, 
                *, 
                change_to_waf_policy: ResourceReference, 
                security_policy_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ProfileLogScrubbing(_Model):
        scrubbing_rules: Optional[list[ProfileScrubbingRules]]
        state: Optional[Union[str, ProfileScrubbingState]]

        @overload
        def __init__(
                self, 
                *, 
                scrubbing_rules: Optional[list[ProfileScrubbingRules]] = ..., 
                state: Optional[Union[str, ProfileScrubbingState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ProfileProperties(_Model):
        extended_properties: Optional[dict[str, str]]
        front_door_id: Optional[str]
        log_scrubbing: Optional[ProfileLogScrubbing]
        origin_response_timeout_seconds: Optional[int]
        provisioning_state: Optional[Union[str, ProfileProvisioningState]]
        resource_state: Optional[Union[str, ProfileResourceState]]

        @overload
        def __init__(
                self, 
                *, 
                log_scrubbing: Optional[ProfileLogScrubbing] = ..., 
                origin_response_timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ProfilePropertiesUpdateParameters(_Model):
        log_scrubbing: Optional[ProfileLogScrubbing]
        origin_response_timeout_seconds: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                log_scrubbing: Optional[ProfileLogScrubbing] = ..., 
                origin_response_timeout_seconds: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.ProfileScrubbingRules(_Model):
        match_variable: Union[str, ScrubbingRuleEntryMatchVariable]
        selector: Optional[str]
        selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator]
        state: Optional[Union[str, ScrubbingRuleEntryState]]

        @overload
        def __init__(
                self, 
                *, 
                match_variable: Union[str, ScrubbingRuleEntryMatchVariable], 
                selector: Optional[str] = ..., 
                selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator], 
                state: Optional[Union[str, ScrubbingRuleEntryState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ProfileScrubbingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.ProfileUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[ProfilePropertiesUpdateParameters]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[ProfilePropertiesUpdateParameters] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.ProfileUpgradeParameters(_Model):
        waf_mapping_list: list[ProfileChangeSkuWafMapping]

        @overload
        def __init__(
                self, 
                *, 
                waf_mapping_list: list[ProfileChangeSkuWafMapping]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.PurgeParameters(_Model):
        content_paths: list[str]

        @overload
        def __init__(
                self, 
                *, 
                content_paths: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.QueryStringMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleQueryStringConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, QueryStringOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, QueryStringOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.RankingsResponse(_Model):
        date_time_begin: Optional[datetime]
        date_time_end: Optional[datetime]
        tables: Optional[list[RankingsResponseTablesItem]]

        @overload
        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                tables: Optional[list[RankingsResponseTablesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RankingsResponseTablesItem(_Model):
        data: Optional[list[RankingsResponseTablesPropertiesItemsItem]]
        ranking: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[RankingsResponseTablesPropertiesItemsItem]] = ..., 
                ranking: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RankingsResponseTablesPropertiesItemsItem(_Model):
        metrics: Optional[list[RankingsResponseTablesPropertiesItemsMetricsItem]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[list[RankingsResponseTablesPropertiesItemsMetricsItem]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RankingsResponseTablesPropertiesItemsMetricsItem(_Model):
        metric: Optional[str]
        percentage: Optional[float]
        value: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                metric: Optional[str] = ..., 
                percentage: Optional[float] = ..., 
                value: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RateLimitRule(CustomRule):
        action: Union[str, ActionType]
        enabled_state: Union[str, CustomRuleEnabledState]
        match_conditions: list[MatchCondition]
        name: str
        priority: int
        rate_limit_duration_in_minutes: int
        rate_limit_threshold: int

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, ActionType], 
                enabled_state: Optional[Union[str, CustomRuleEnabledState]] = ..., 
                match_conditions: list[MatchCondition], 
                name: str, 
                priority: int, 
                rate_limit_duration_in_minutes: int, 
                rate_limit_threshold: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RateLimitRuleList(_Model):
        rules: Optional[list[RateLimitRule]]

        @overload
        def __init__(
                self, 
                *, 
                rules: Optional[list[RateLimitRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RedirectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FOUND = "Found"
        MOVED = "Moved"
        PERMANENT_REDIRECT = "PermanentRedirect"
        TEMPORARY_REDIRECT = "TemporaryRedirect"


    class azure.mgmt.cdn.models.RemoteAddressMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRemoteAddressConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, RemoteAddressOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RemoteAddressOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RemoteAddressOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        GEO_MATCH = "GeoMatch"
        IP_MATCH = "IPMatch"


    class azure.mgmt.cdn.models.RequestBodyMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRequestBodyConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, RequestBodyOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RequestBodyOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.RequestHeaderMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRequestHeaderConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, RequestHeaderOperator]
        selector: Optional[str]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RequestHeaderOperator], 
                selector: Optional[str] = ..., 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.RequestMethodMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRequestMethodConditionParameters'):
        match_values: Optional[list[Union[str, RequestMethodMatchConditionParametersMatchValuesItem]]]
        negate_condition: Optional[bool]
        operator: Union[str, RequestMethodOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[Union[str, RequestMethodMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RequestMethodOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RequestMethodMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "DELETE"
        GET = "GET"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"
        POST = "POST"
        PUT = "PUT"
        TRACE = "TRACE"


    class azure.mgmt.cdn.models.RequestMethodOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRequestSchemeConditionParameters'):
        match_values: Optional[list[Union[str, RequestSchemeMatchConditionParametersMatchValuesItem]]]
        negate_condition: Optional[bool]
        operator: Union[str, RequestSchemeMatchConditionParametersOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[Union[str, RequestSchemeMatchConditionParametersMatchValuesItem]]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RequestSchemeMatchConditionParametersOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParametersMatchValuesItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HTTP = "HTTP"
        HTTPS = "HTTPS"


    class azure.mgmt.cdn.models.RequestSchemeMatchConditionParametersOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.RequestUriMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleRequestUriConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, RequestUriOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, RequestUriOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.cdn.models.ResourceReference(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_CDN_PROFILES_AFD_ENDPOINTS = "Microsoft.Cdn/Profiles/AfdEndpoints"
        MICROSOFT_CDN_PROFILES_ENDPOINTS = "Microsoft.Cdn/Profiles/Endpoints"


    class azure.mgmt.cdn.models.ResourceUsage(_Model):
        current_value: Optional[int]
        limit: Optional[int]
        resource_type: Optional[str]
        unit: Optional[Union[str, ResourceUsageUnit]]


    class azure.mgmt.cdn.models.ResourceUsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "count"


    class azure.mgmt.cdn.models.ResourcesResponse(_Model):
        custom_domains: Optional[list[ResourcesResponseCustomDomainsItem]]
        endpoints: Optional[list[ResourcesResponseEndpointsItem]]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains: Optional[list[ResourcesResponseCustomDomainsItem]] = ..., 
                endpoints: Optional[list[ResourcesResponseEndpointsItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ResourcesResponseCustomDomainsItem(_Model):
        endpoint_id: Optional[str]
        history: Optional[bool]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: Optional[str] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ResourcesResponseEndpointsItem(_Model):
        custom_domains: Optional[list[ResourcesResponseEndpointsPropertiesItemsItem]]
        history: Optional[bool]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                custom_domains: Optional[list[ResourcesResponseEndpointsPropertiesItemsItem]] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ResourcesResponseEndpointsPropertiesItemsItem(_Model):
        endpoint_id: Optional[str]
        history: Optional[bool]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_id: Optional[str] = ..., 
                history: Optional[bool] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ResponseBasedDetectedErrorTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        TCP_AND_HTTP_ERRORS = "TcpAndHttpErrors"
        TCP_ERRORS_ONLY = "TcpErrorsOnly"


    class azure.mgmt.cdn.models.ResponseBasedOriginErrorDetectionParameters(_Model):
        http_error_ranges: Optional[list[HttpErrorRangeParameters]]
        response_based_detected_error_types: Optional[Union[str, ResponseBasedDetectedErrorTypes]]
        response_based_failover_threshold_percentage: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                http_error_ranges: Optional[list[HttpErrorRangeParameters]] = ..., 
                response_based_detected_error_types: Optional[Union[str, ResponseBasedDetectedErrorTypes]] = ..., 
                response_based_failover_threshold_percentage: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.Route(ProxyResource):
        id: str
        name: str
        properties: Optional[RouteProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RouteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.RouteConfigurationOverrideActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleRouteConfigurationOverrideActionParameters'):
        cache_configuration: Optional[CacheConfiguration]
        origin_group_override: Optional[OriginGroupOverride]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                cache_configuration: Optional[CacheConfiguration] = ..., 
                origin_group_override: Optional[OriginGroupOverride] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RouteProperties(_Model):
        cache_configuration: Optional[AfdRouteCacheConfiguration]
        custom_domains: Optional[list[ActivatedResourceReference]]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        enabled_state: Optional[Union[str, EnabledState]]
        endpoint_name: Optional[str]
        forwarding_protocol: Optional[Union[str, ForwardingProtocol]]
        https_redirect: Optional[Union[str, HttpsRedirect]]
        link_to_default_domain: Optional[Union[str, LinkToDefaultDomain]]
        origin_group: Optional[ResourceReference]
        origin_path: Optional[str]
        patterns_to_match: Optional[list[str]]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]
        rule_sets: Optional[list[ResourceReference]]
        supported_protocols: Optional[list[Union[str, AFDEndpointProtocols]]]

        @overload
        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[list[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Optional[Union[str, HttpsRedirect]] = ..., 
                link_to_default_domain: Optional[Union[str, LinkToDefaultDomain]] = ..., 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[list[str]] = ..., 
                rule_sets: Optional[list[ResourceReference]] = ..., 
                supported_protocols: Optional[list[Union[str, AFDEndpointProtocols]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RouteUpdateParameters(_Model):
        properties: Optional[RouteUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RouteUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.RouteUpdatePropertiesParameters(_Model):
        cache_configuration: Optional[AfdRouteCacheConfiguration]
        custom_domains: Optional[list[ActivatedResourceReference]]
        enabled_state: Optional[Union[str, EnabledState]]
        endpoint_name: Optional[str]
        forwarding_protocol: Optional[Union[str, ForwardingProtocol]]
        https_redirect: Optional[Union[str, HttpsRedirect]]
        link_to_default_domain: Optional[Union[str, LinkToDefaultDomain]]
        origin_group: Optional[ResourceReference]
        origin_path: Optional[str]
        patterns_to_match: Optional[list[str]]
        rule_sets: Optional[list[ResourceReference]]
        supported_protocols: Optional[list[Union[str, AFDEndpointProtocols]]]

        @overload
        def __init__(
                self, 
                *, 
                cache_configuration: Optional[AfdRouteCacheConfiguration] = ..., 
                custom_domains: Optional[list[ActivatedResourceReference]] = ..., 
                enabled_state: Optional[Union[str, EnabledState]] = ..., 
                forwarding_protocol: Optional[Union[str, ForwardingProtocol]] = ..., 
                https_redirect: Optional[Union[str, HttpsRedirect]] = ..., 
                link_to_default_domain: Optional[Union[str, LinkToDefaultDomain]] = ..., 
                origin_group: Optional[ResourceReference] = ..., 
                origin_path: Optional[str] = ..., 
                patterns_to_match: Optional[list[str]] = ..., 
                rule_sets: Optional[list[ResourceReference]] = ..., 
                supported_protocols: Optional[list[Union[str, AFDEndpointProtocols]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.Rule(ProxyResource):
        id: str
        name: str
        properties: Optional[RuleProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuleProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.RuleCacheBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HONOR_ORIGIN = "HonorOrigin"
        OVERRIDE_ALWAYS = "OverrideAlways"
        OVERRIDE_IF_ORIGIN_MISSING = "OverrideIfOriginMissing"


    class azure.mgmt.cdn.models.RuleIsCompressionEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.cdn.models.RuleProperties(_Model):
        actions: Optional[list[DeliveryRuleAction]]
        conditions: Optional[list[DeliveryRuleCondition]]
        deployment_status: Optional[Union[str, DeploymentStatus]]
        match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]]
        order: Optional[int]
        provisioning_state: Optional[Union[str, AfdProvisioningState]]
        rule_set_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[DeliveryRuleAction]] = ..., 
                conditions: Optional[list[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]] = ..., 
                order: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RuleQueryStringCachingBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE_QUERY_STRING = "IgnoreQueryString"
        IGNORE_SPECIFIED_QUERY_STRINGS = "IgnoreSpecifiedQueryStrings"
        INCLUDE_SPECIFIED_QUERY_STRINGS = "IncludeSpecifiedQueryStrings"
        USE_QUERY_STRING = "UseQueryString"


    class azure.mgmt.cdn.models.RuleSet(ProxyResource):
        id: str
        name: str
        properties: Optional[RuleSetProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuleSetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.RuleSetProperties(AFDStateProperties):
        batch_mode: Optional[bool]
        deployment_status: Union[str, DeploymentStatus]
        profile_name: Optional[str]
        provisioning_state: Union[str, AfdProvisioningState]
        rules: Optional[list[BatchRuleProperties]]

        @overload
        def __init__(
                self, 
                *, 
                batch_mode: Optional[bool] = ..., 
                rules: Optional[list[BatchRuleProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.RuleUpdateParameters(_Model):
        properties: Optional[RuleUpdatePropertiesParameters]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RuleUpdatePropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.RuleUpdatePropertiesParameters(_Model):
        actions: Optional[list[DeliveryRuleAction]]
        conditions: Optional[list[DeliveryRuleCondition]]
        match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]]
        order: Optional[int]
        rule_set_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[DeliveryRuleAction]] = ..., 
                conditions: Optional[list[DeliveryRuleCondition]] = ..., 
                match_processing_behavior: Optional[Union[str, MatchProcessingBehavior]] = ..., 
                order: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        id: str
        name: str
        properties: Optional[SecretProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecretProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.SecretParameters(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecretProperties(AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        parameters: Optional[SecretParameters]
        profile_name: Optional[str]
        provisioning_state: Union[str, AfdProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[SecretParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIRST_PARTY_MANAGED_CERTIFICATE = "AzureFirstPartyManagedCertificate"
        CUSTOMER_CERTIFICATE = "CustomerCertificate"
        MANAGED_CERTIFICATE = "ManagedCertificate"
        URL_SIGNING_KEY = "UrlSigningKey"


    class azure.mgmt.cdn.models.SecurityPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[SecurityPolicyProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyProperties(AFDStateProperties):
        deployment_status: Union[str, DeploymentStatus]
        parameters: Optional[SecurityPolicyPropertiesParameters]
        profile_name: Optional[str]
        provisioning_state: Union[str, AfdProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[SecurityPolicyPropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyPropertiesParameters(_Model):
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_APPLICATION_FIREWALL = "WebApplicationFirewall"


    class azure.mgmt.cdn.models.SecurityPolicyUpdateParameters(_Model):
        properties: Optional[SecurityPolicyUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SecurityPolicyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyUpdateProperties(_Model):
        parameters: Optional[SecurityPolicyPropertiesParameters]

        @overload
        def __init__(
                self, 
                *, 
                parameters: Optional[SecurityPolicyPropertiesParameters] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyWebApplicationFirewallAssociation(_Model):
        domains: Optional[list[ActivatedResourceReference]]
        patterns_to_match: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                domains: Optional[list[ActivatedResourceReference]] = ..., 
                patterns_to_match: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SecurityPolicyWebApplicationFirewallParameters(SecurityPolicyPropertiesParameters, discriminator='WebApplicationFirewall'):
        associations: Optional[list[SecurityPolicyWebApplicationFirewallAssociation]]
        type: Literal[SecurityPolicyType.WEB_APPLICATION_FIREWALL]
        waf_policy: Optional[ResourceReference]

        @overload
        def __init__(
                self, 
                *, 
                associations: Optional[list[SecurityPolicyWebApplicationFirewallAssociation]] = ..., 
                waf_policy: Optional[ResourceReference] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ServerPortMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleServerPortConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, ServerPortOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, ServerPortOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.ServiceSpecification(_Model):
        log_specifications: Optional[list[LogSpecification]]
        metric_specifications: Optional[list[MetricSpecification]]

        @overload
        def __init__(
                self, 
                *, 
                log_specifications: Optional[list[LogSpecification]] = ..., 
                metric_specifications: Optional[list[MetricSpecification]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SharedPrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        private_link: Optional[ResourceReference]
        private_link_location: Optional[str]
        request_message: Optional[str]
        status: Optional[Union[str, SharedPrivateLinkResourceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                group_id: Optional[str] = ..., 
                private_link: Optional[ResourceReference] = ..., 
                private_link_location: Optional[str] = ..., 
                request_message: Optional[str] = ..., 
                status: Optional[Union[str, SharedPrivateLinkResourceStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"
        TIMEOUT = "Timeout"


    class azure.mgmt.cdn.models.Sku(_Model):
        name: Optional[Union[str, SkuName]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[Union[str, SkuName]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.SocketAddrMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleSocketAddrConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, SocketAddrOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, SocketAddrOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SocketAddrOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        IP_MATCH = "IPMatch"


    class azure.mgmt.cdn.models.SslProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TL_SV1 = "TLSv1"
        TL_SV1_1 = "TLSv1.1"
        TL_SV1_2 = "TLSv1.2"


    class azure.mgmt.cdn.models.SslProtocolMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleSslProtocolConditionParameters'):
        match_values: Optional[list[Union[str, SslProtocol]]]
        negate_condition: Optional[bool]
        operator: Union[str, SslProtocolOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[Union[str, SslProtocol]]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, SslProtocolOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.SslProtocolOperator(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EQUAL = "Equal"


    class azure.mgmt.cdn.models.SsoUri(_Model):
        sso_uri_value: Optional[str]


    class azure.mgmt.cdn.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_DENIED = "AccessDenied"
        CERTIFICATE_EXPIRED = "CertificateExpired"
        INVALID = "Invalid"
        VALID = "Valid"


    class azure.mgmt.cdn.models.SupportedOptimizationTypesListResult(_Model):
        supported_optimization_types: Optional[list[Union[str, OptimizationType]]]


    class azure.mgmt.cdn.models.SystemData(_Model):
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


    class azure.mgmt.cdn.models.TrackedResource(Resource):
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


    class azure.mgmt.cdn.models.UrlFileExtensionMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleUrlFileExtensionMatchConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, UrlFileExtensionOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, UrlFileExtensionOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.UrlFileNameMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleUrlFilenameConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, UrlFileNameOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, UrlFileNameOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.UrlPathMatchConditionParameters(DeliveryRuleConditionParameters, discriminator='DeliveryRuleUrlPathMatchConditionParameters'):
        match_values: Optional[list[str]]
        negate_condition: Optional[bool]
        operator: Union[str, UrlPathOperator]
        transforms: Optional[list[Union[str, Transform]]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                match_values: Optional[list[str]] = ..., 
                negate_condition: Optional[bool] = ..., 
                operator: Union[str, UrlPathOperator], 
                transforms: Optional[list[Union[str, Transform]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.UrlRedirectAction(DeliveryRuleAction, discriminator='UrlRedirect'):
        name: Literal[DeliveryRuleActionEnum.URL_REDIRECT]
        parameters: UrlRedirectActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlRedirectActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlRedirectActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleUrlRedirectActionParameters'):
        custom_fragment: Optional[str]
        custom_hostname: Optional[str]
        custom_path: Optional[str]
        custom_query_string: Optional[str]
        destination_protocol: Optional[Union[str, DestinationProtocol]]
        redirect_type: Union[str, RedirectType]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                custom_fragment: Optional[str] = ..., 
                custom_hostname: Optional[str] = ..., 
                custom_path: Optional[str] = ..., 
                custom_query_string: Optional[str] = ..., 
                destination_protocol: Optional[Union[str, DestinationProtocol]] = ..., 
                redirect_type: Union[str, RedirectType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlRewriteAction(DeliveryRuleAction, discriminator='UrlRewrite'):
        name: Literal[DeliveryRuleActionEnum.URL_REWRITE]
        parameters: UrlRewriteActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlRewriteActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlRewriteActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleUrlRewriteActionParameters'):
        destination: str
        preserve_unmatched_path: Optional[bool]
        source_pattern: str
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                destination: str, 
                preserve_unmatched_path: Optional[bool] = ..., 
                source_pattern: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlSigningAction(DeliveryRuleAction, discriminator='UrlSigning'):
        name: Literal[DeliveryRuleActionEnum.URL_SIGNING]
        parameters: UrlSigningActionParameters

        @overload
        def __init__(
                self, 
                *, 
                parameters: UrlSigningActionParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlSigningActionParameters(DeliveryRuleActionParameters, discriminator='DeliveryRuleUrlSigningActionParameters'):
        algorithm: Optional[Union[str, Algorithm]]
        parameter_name_override: Optional[list[UrlSigningParamIdentifier]]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS]

        @overload
        def __init__(
                self, 
                *, 
                algorithm: Optional[Union[str, Algorithm]] = ..., 
                parameter_name_override: Optional[list[UrlSigningParamIdentifier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlSigningKey(_Model):
        key_id: str
        key_source_parameters: KeyVaultSigningKeyParameters

        @overload
        def __init__(
                self, 
                *, 
                key_id: str, 
                key_source_parameters: KeyVaultSigningKeyParameters
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlSigningKeyParameters(SecretParameters, discriminator='UrlSigningKey'):
        key_id: str
        secret_source: ResourceReference
        secret_version: str
        type: Literal[SecretType.URL_SIGNING_KEY]

        @overload
        def __init__(
                self, 
                *, 
                key_id: str, 
                secret_source: ResourceReference, 
                secret_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UrlSigningParamIdentifier(_Model):
        param_indicator: Union[str, ParamIndicator]
        param_name: str

        @overload
        def __init__(
                self, 
                *, 
                param_indicator: Union[str, ParamIndicator], 
                param_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.Usage(_Model):
        current_value: int
        id: Optional[str]
        limit: int
        name: UsageName
        unit: Union[str, UsageUnit]

        @overload
        def __init__(
                self, 
                *, 
                current_value: int, 
                limit: int, 
                name: UsageName, 
                unit: Union[str, UsageUnit]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.UsageName(_Model):
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


    class azure.mgmt.cdn.models.UsageUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNT = "Count"


    class azure.mgmt.cdn.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.cdn.models.UserManagedHttpsParameters(CustomDomainHttpsParameters, discriminator='AzureKeyVault'):
        certificate_source: Literal[CertificateSource.AZURE_KEY_VAULT]
        certificate_source_parameters: KeyVaultCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]

        @overload
        def __init__(
                self, 
                *, 
                certificate_source_parameters: KeyVaultCertificateSourceParameters, 
                minimum_tls_version: Optional[Union[str, MinimumTlsVersion]] = ..., 
                protocol_type: Union[str, ProtocolType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ValidateCustomDomainInput(_Model):
        host_name: str

        @overload
        def __init__(
                self, 
                *, 
                host_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ValidateCustomDomainOutput(_Model):
        custom_domain_validated: Optional[bool]
        message: Optional[str]
        reason: Optional[str]


    class azure.mgmt.cdn.models.ValidateProbeInput(_Model):
        probe_url: str

        @overload
        def __init__(
                self, 
                *, 
                probe_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ValidateProbeOutput(_Model):
        error_code: Optional[str]
        is_valid: Optional[bool]
        message: Optional[str]


    class azure.mgmt.cdn.models.ValidateSecretInput(_Model):
        secret_source: ResourceReference
        secret_type: Union[str, SecretType]
        secret_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                secret_source: ResourceReference, 
                secret_type: Union[str, SecretType], 
                secret_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.ValidateSecretOutput(_Model):
        message: Optional[str]
        status: Optional[Union[str, Status]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                status: Optional[Union[str, Status]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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


    class azure.mgmt.cdn.models.WafMetricsResponse(_Model):
        date_time_begin: Optional[datetime]
        date_time_end: Optional[datetime]
        granularity: Optional[Union[str, WafMetricsGranularity]]
        series: Optional[list[WafMetricsResponseSeriesItem]]

        @overload
        def __init__(
                self, 
                *, 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                granularity: Optional[Union[str, WafMetricsGranularity]] = ..., 
                series: Optional[list[WafMetricsResponseSeriesItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.WafMetricsResponseSeriesItem(_Model):
        data: Optional[list[Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems]]
        groups: Optional[list[WafMetricsResponseSeriesPropertiesItemsItem]]
        metric: Optional[str]
        unit: Optional[Union[str, WafMetricsSeriesUnit]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[Components18OrqelSchemasWafmetricsresponsePropertiesSeriesItemsPropertiesDataItems]] = ..., 
                groups: Optional[list[WafMetricsResponseSeriesPropertiesItemsItem]] = ..., 
                metric: Optional[str] = ..., 
                unit: Optional[Union[str, WafMetricsSeriesUnit]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.WafMetricsResponseSeriesPropertiesItemsItem(_Model):
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


    class azure.mgmt.cdn.models.WafRankingsResponse(_Model):
        data: Optional[list[WafRankingsResponseDataItem]]
        date_time_begin: Optional[datetime]
        date_time_end: Optional[datetime]
        groups: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                data: Optional[list[WafRankingsResponseDataItem]] = ..., 
                date_time_begin: Optional[datetime] = ..., 
                date_time_end: Optional[datetime] = ..., 
                groups: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.cdn.models.WafRankingsResponseDataItem(_Model):
        group_values: Optional[list[str]]
        metrics: Optional[list[ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems]]

        @overload
        def __init__(
                self, 
                *, 
                group_values: Optional[list[str]] = ..., 
                metrics: Optional[list[ComponentsKpo1PjSchemasWafrankingsresponsePropertiesDataItemsPropertiesMetricsItems]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
            ) -> None: ...

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
            ) -> ItemPaged[AFDDomain]: ...


    class azure.mgmt.cdn.operations.AFDEndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[AFDEndpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...

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
            ) -> None: ...

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
            ) -> ItemPaged[AFDOriginGroup]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                origin_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cdn.operations.AFDOriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[AFDOrigin]: ...


    class azure.mgmt.cdn.operations.AFDProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Usage]: ...

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


    class azure.mgmt.cdn.operations.CustomDomainsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[CustomDomain]: ...


    class azure.mgmt.cdn.operations.EdgeNodesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[EdgeNode]: ...


    class azure.mgmt.cdn.operations.EndpointsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Endpoint]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                endpoint_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceUsage]: ...

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
            ) -> None: ...

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
                *, 
                continents: Optional[List[str]] = ..., 
                country_or_regions: Optional[List[str]] = ..., 
                custom_domains: List[str], 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, LogMetricsGranularity], 
                group_by: Optional[List[Union[str, LogMetricsGroupBy]]] = ..., 
                metrics: List[Union[str, LogMetric]], 
                protocols: List[str], 
                **kwargs: Any
            ) -> MetricsResponse: ...

        @distributed_trace
        def get_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                custom_domains: Optional[List[str]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                metrics: List[Union[str, LogRankingMetric]], 
                rankings: List[Union[str, LogRanking]], 
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
                *, 
                actions: Optional[List[Union[str, WafAction]]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                granularity: Union[str, WafGranularity], 
                group_by: Optional[List[Union[str, WafRankingGroupBy]]] = ..., 
                metrics: List[Union[str, WafMetric]], 
                rule_types: Optional[List[Union[str, WafRuleType]]] = ..., 
                **kwargs: Any
            ) -> WafMetricsResponse: ...

        @distributed_trace
        def get_waf_log_analytics_rankings(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                *, 
                actions: Optional[List[Union[str, WafAction]]] = ..., 
                date_time_begin: datetime, 
                date_time_end: datetime, 
                max_ranking: int, 
                metrics: List[Union[str, WafMetric]], 
                rankings: List[Union[str, WafRankingType]], 
                rule_types: Optional[List[Union[str, WafRuleType]]] = ..., 
                **kwargs: Any
            ) -> WafRankingsResponse: ...


    class azure.mgmt.cdn.operations.ManagedRuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ManagedRuleSetDefinition]: ...


    class azure.mgmt.cdn.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.cdn.operations.OriginGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[OriginGroup]: ...


    class azure.mgmt.cdn.operations.OriginsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Origin]: ...


    class azure.mgmt.cdn.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[CdnWebApplicationFirewallPolicy]: ...


    class azure.mgmt.cdn.operations.ProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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

        @distributed_trace
        def begin_cdn_can_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[CanMigrateResult]: ...

        @overload
        def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: CdnMigrationToAfdParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrateResult]: ...

        @overload
        def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: CdnMigrationToAfdParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrateResult]: ...

        @overload
        def begin_cdn_migrate_to_afd(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                migration_parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrateResult]: ...

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
        def begin_migration_abort(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

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
        def list(self, **kwargs: Any) -> ItemPaged[Profile]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Profile]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceUsage]: ...

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
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ResourceUsage]: ...


    class azure.mgmt.cdn.operations.RoutesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Route]: ...


    class azure.mgmt.cdn.operations.RuleSetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                resource: Optional[RuleSet] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuleSet]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                resource: Optional[RuleSet] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuleSet]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                resource: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RuleSet]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

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
            ) -> ItemPaged[RuleSet]: ...

        @distributed_trace
        def list_resource_usage(
                self, 
                resource_group_name: str, 
                profile_name: str, 
                rule_set_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Usage]: ...


    class azure.mgmt.cdn.operations.RulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Rule]: ...


    class azure.mgmt.cdn.operations.SecretsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[Secret]: ...


    class azure.mgmt.cdn.operations.SecurityPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

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
            ) -> ItemPaged[SecurityPolicy]: ...


namespace azure.mgmt.cdn.types

    class azure.mgmt.cdn.types.AFDDomain(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AFDDomainProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AFDDomainProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.AFDDomainHttpsCustomizedCipherSuiteSet(TypedDict, total=False):
        cipherSuiteSetForTls12: list[Union[str, AfdCustomizedCipherSuiteForTls12]]
        cipherSuiteSetForTls13: list[Union[str, AfdCustomizedCipherSuiteForTls13]]
        cipher_suite_set_for_tls12: list[Union[str, AfdCustomizedCipherSuiteForTls12]]
        cipher_suite_set_for_tls13: list[Union[str, AfdCustomizedCipherSuiteForTls13]]


    class azure.mgmt.cdn.types.AFDDomainHttpsParameters(TypedDict, total=False):
        key "certificateType": Required[Union[str, AfdCertificateType]]
        key "cipherSuiteSetType": Union[str, AfdCipherSuiteSetType]
        key "customizedCipherSuiteSet": ForwardRef('AFDDomainHttpsCustomizedCipherSuiteSet', module='types')
        key "minimumTlsVersion": Union[str, AfdMinimumTlsVersion]
        key "secret": ForwardRef('ResourceReference', module='types')
        certificate_type: Union[str, AfdCertificateType]
        cipher_suite_set_type: Union[str, AfdCipherSuiteSetType]
        customized_cipher_suite_set: AFDDomainHttpsCustomizedCipherSuiteSet
        minimum_tls_version: Union[str, AfdMinimumTlsVersion]
        secret: ResourceReference


    class azure.mgmt.cdn.types.AFDDomainProperties(TypedDict, total=False):
        key "azureDnsZone": ForwardRef('ResourceReference', module='types')
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "domainValidationState": Union[str, DomainValidationState]
        key "hostName": Required[str]
        key "preValidatedCustomDomainResourceId": ForwardRef('ResourceReference', module='types')
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        key "tlsSettings": ForwardRef('AFDDomainHttpsParameters', module='types')
        key "validationProperties": ForwardRef('DomainValidationProperties', module='types')
        azure_dns_zone: ResourceReference
        deployment_status: Union[str, DeploymentStatus]
        domain_validation_state: Union[str, DomainValidationState]
        extendedProperties: dict[str, str]
        extended_properties: dict[str, str]
        host_name: str
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        tls_settings: AFDDomainHttpsParameters
        validation_properties: DomainValidationProperties


    class azure.mgmt.cdn.types.AFDDomainUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AFDDomainUpdatePropertiesParameters', module='types')
        properties: AFDDomainUpdatePropertiesParameters


    class azure.mgmt.cdn.types.AFDDomainUpdatePropertiesParameters(TypedDict, total=False):
        key "azureDnsZone": ForwardRef('ResourceReference', module='types')
        key "preValidatedCustomDomainResourceId": ForwardRef('ResourceReference', module='types')
        key "profileName": str
        key "tlsSettings": ForwardRef('AFDDomainHttpsParameters', module='types')
        azure_dns_zone: ResourceReference
        pre_validated_custom_domain_resource_id: ResourceReference
        profile_name: str
        tls_settings: AFDDomainHttpsParameters


    class azure.mgmt.cdn.types.AFDEndpoint(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AFDEndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AFDEndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cdn.types.AFDEndpointProperties(TypedDict, total=False):
        key "autoGeneratedDomainNameLabelScope": Union[str, AutoGeneratedDomainNameLabelScope]
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "enabledState": Union[str, EnabledState]
        key "hostName": str
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        host_name: str
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]


    class azure.mgmt.cdn.types.AFDEndpointPropertiesUpdateParameters(TypedDict, total=False):
        key "enabledState": Union[str, EnabledState]
        key "profileName": str
        enabled_state: Union[str, EnabledState]
        profile_name: str


    class azure.mgmt.cdn.types.AFDEndpointUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AFDEndpointPropertiesUpdateParameters', module='types')
        properties: AFDEndpointPropertiesUpdateParameters
        tags: dict[str, str]


    class azure.mgmt.cdn.types.AFDOrigin(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AFDOriginProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AFDOriginProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.AFDOriginGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AFDOriginGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AFDOriginGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.AFDOriginGroupProperties(TypedDict, total=False):
        key "authentication": ForwardRef('OriginAuthenticationProperties', module='types')
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "healthProbeSettings": ForwardRef('HealthProbeParameters', module='types')
        key "loadBalancingSettings": ForwardRef('LoadBalancingSettingsParameters', module='types')
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        key "sessionAffinityState": Union[str, EnabledState]
        key "trafficRestorationTimeToHealedOrNewEndpointsInMinutes": int
        authentication: OriginAuthenticationProperties
        deployment_status: Union[str, DeploymentStatus]
        health_probe_settings: HealthProbeParameters
        load_balancing_settings: LoadBalancingSettingsParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        session_affinity_state: Union[str, EnabledState]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int


    class azure.mgmt.cdn.types.AFDOriginGroupUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AFDOriginGroupUpdatePropertiesParameters', module='types')
        properties: AFDOriginGroupUpdatePropertiesParameters


    class azure.mgmt.cdn.types.AFDOriginGroupUpdatePropertiesParameters(TypedDict, total=False):
        key "authentication": ForwardRef('OriginAuthenticationProperties', module='types')
        key "healthProbeSettings": ForwardRef('HealthProbeParameters', module='types')
        key "loadBalancingSettings": ForwardRef('LoadBalancingSettingsParameters', module='types')
        key "profileName": str
        key "sessionAffinityState": Union[str, EnabledState]
        key "trafficRestorationTimeToHealedOrNewEndpointsInMinutes": int
        authentication: OriginAuthenticationProperties
        health_probe_settings: HealthProbeParameters
        load_balancing_settings: LoadBalancingSettingsParameters
        profile_name: str
        session_affinity_state: Union[str, EnabledState]
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int


    class azure.mgmt.cdn.types.AFDOriginProperties(TypedDict, total=False):
        key "azureOrigin": ForwardRef('ResourceReference', module='types')
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "enabledState": Union[str, EnabledState]
        key "enforceCertificateNameCheck": bool
        key "hostName": str
        key "httpPort": int
        key "httpsPort": int
        key "originGroupName": str
        key "originHostHeader": str
        key "priority": int
        key "provisioningState": Union[str, AfdProvisioningState]
        key "sharedPrivateLinkResource": ForwardRef('SharedPrivateLinkResourceProperties', module='types')
        key "weight": int
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


    class azure.mgmt.cdn.types.AFDOriginUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('AFDOriginUpdatePropertiesParameters', module='types')
        properties: AFDOriginUpdatePropertiesParameters


    class azure.mgmt.cdn.types.AFDOriginUpdatePropertiesParameters(TypedDict, total=False):
        key "azureOrigin": ForwardRef('ResourceReference', module='types')
        key "enabledState": Union[str, EnabledState]
        key "enforceCertificateNameCheck": bool
        key "hostName": str
        key "httpPort": int
        key "httpsPort": int
        key "originGroupName": str
        key "originHostHeader": str
        key "priority": int
        key "sharedPrivateLinkResource": ForwardRef('SharedPrivateLinkResourceProperties', module='types')
        key "weight": int
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


    class azure.mgmt.cdn.types.AFDStateProperties(TypedDict, total=False):
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "provisioningState": Union[str, AfdProvisioningState]
        deployment_status: Union[str, DeploymentStatus]
        provisioning_state: Union[str, AfdProvisioningState]


    class azure.mgmt.cdn.types.ActivatedResourceReference(TypedDict, total=False):
        key "id": str
        key "isActive": bool
        id: str
        is_active: bool


    class azure.mgmt.cdn.types.AfdPurgeParameters(TypedDict, total=False):
        key "contentPaths": Required[list[str]]
        content_paths: list[str]
        domains: list[str]


    class azure.mgmt.cdn.types.AfdRouteCacheConfiguration(TypedDict, total=False):
        key "compressionSettings": ForwardRef('CompressionSettings', module='types')
        key "queryParameters": str
        key "queryStringCachingBehavior": Union[str, AfdQueryStringCachingBehavior]
        compression_settings: CompressionSettings
        query_parameters: str
        query_string_caching_behavior: Union[str, AfdQueryStringCachingBehavior]


    class azure.mgmt.cdn.types.AzureFirstPartyManagedCertificateParameters(TypedDict, total=False):
        key "certificateAuthority": str
        key "expirationDate": str
        key "secretSource": ForwardRef('ResourceReference', module='types')
        key "subject": str
        key "thumbprint": str
        key "type": Required[Literal[SecretType.AZURE_FIRST_PARTY_MANAGED_CERTIFICATE]]
        certificate_authority: str
        expiration_date: str
        secret_source: ResourceReference
        subject: str
        subjectAlternativeNames: list[str]
        subject_alternative_names: list[str]
        thumbprint: str
        type: Literal[SecretType.AZURE_FIRST_PARTY_MANAGED_CERTIFICATE]


    class azure.mgmt.cdn.types.BatchRuleProperties(TypedDict, total=False):
        key "matchProcessingBehavior": Union[str, MatchProcessingBehavior]
        key "order": int
        key "ruleName": Required[str]
        key "ruleSetName": str
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        rule_name: str
        rule_set_name: str


    class azure.mgmt.cdn.types.CacheConfiguration(TypedDict, total=False):
        key "cacheBehavior": Union[str, RuleCacheBehavior]
        key "cacheDuration": str
        key "isCompressionEnabled": Union[str, RuleIsCompressionEnabled]
        key "queryParameters": str
        key "queryStringCachingBehavior": Union[str, RuleQueryStringCachingBehavior]
        cache_behavior: Union[str, RuleCacheBehavior]
        cache_duration: str
        is_compression_enabled: Union[str, RuleIsCompressionEnabled]
        query_parameters: str
        query_string_caching_behavior: Union[str, RuleQueryStringCachingBehavior]


    class azure.mgmt.cdn.types.CacheExpirationActionParameters(TypedDict, total=False):
        key "cacheBehavior": Required[Union[str, CacheBehavior]]
        key "cacheDuration": Optional[str]
        key "cacheType": Required[Union[str, CacheType]]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS]]
        cache_behavior: Union[str, CacheBehavior]
        cache_duration: str
        cache_type: Union[str, CacheType]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.CacheKeyQueryStringActionParameters(TypedDict, total=False):
        key "queryParameters": Optional[str]
        key "queryStringBehavior": Required[Union[str, QueryStringBehavior]]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS]]
        query_parameters: str
        query_string_behavior: Union[str, QueryStringBehavior]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.CanMigrateParameters(TypedDict, total=False):
        key "classicResourceReference": Required[ResourceReference]
        classic_resource_reference: ResourceReference


    class azure.mgmt.cdn.types.CdnCertificateSourceParameters(TypedDict, total=False):
        key "certificateType": Required[Union[str, CertificateType]]
        key "typeName": Required[Literal[CertificateSourceParametersType.CDN_CERTIFICATE_SOURCE_PARAMETERS]]
        certificate_type: Union[str, CertificateType]
        type_name: Literal[CertificateSourceParametersType.CDN_CERTIFICATE_SOURCE_PARAMETERS]


    class azure.mgmt.cdn.types.CdnEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cdn.types.CdnManagedHttpsParameters(TypedDict, total=False):
        key "certificateSource": Required[Literal[CertificateSource.CDN]]
        key "certificateSourceParameters": Required[CdnCertificateSourceParameters]
        key "minimumTlsVersion": Union[str, MinimumTlsVersion]
        key "protocolType": Required[Union[str, ProtocolType]]
        certificate_source: Literal[CertificateSource.CDN]
        certificate_source_parameters: CdnCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]


    class azure.mgmt.cdn.types.CdnMigrationToAfdParameters(TypedDict, total=False):
        key "sku": Required[Sku]
        migrationEndpointMappings: list[MigrationEndpointMapping]
        migration_endpoint_mappings: list[MigrationEndpointMapping]
        sku: Sku


    class azure.mgmt.cdn.types.CdnWebApplicationFirewallPolicy(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CdnWebApplicationFirewallPolicyProperties', module='types')
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: CdnWebApplicationFirewallPolicyProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cdn.types.CdnWebApplicationFirewallPolicyPatchParameters(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.cdn.types.CdnWebApplicationFirewallPolicyProperties(TypedDict, total=False):
        key "customRules": ForwardRef('CustomRuleList', module='types')
        key "managedRules": ForwardRef('ManagedRuleSetList', module='types')
        key "policySettings": ForwardRef('PolicySettings', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "rateLimitRules": ForwardRef('RateLimitRuleList', module='types')
        key "resourceState": Union[str, PolicyResourceState]
        custom_rules: CustomRuleList
        endpointLinks: list[CdnEndpoint]
        endpoint_links: list[CdnEndpoint]
        extendedProperties: dict[str, str]
        extended_properties: dict[str, str]
        managed_rules: ManagedRuleSetList
        policy_settings: PolicySettings
        provisioning_state: Union[str, ProvisioningState]
        rate_limit_rules: RateLimitRuleList
        resource_state: Union[str, PolicyResourceState]


    class azure.mgmt.cdn.types.CertificateSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_KEY_VAULT = "AzureKeyVault"
        CDN = "Cdn"


    class azure.mgmt.cdn.types.CertificateSourceParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CDN_CERTIFICATE_SOURCE_PARAMETERS = "CdnCertificateSourceParameters"
        KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS = "KeyVaultCertificateSourceParameters"


    class azure.mgmt.cdn.types.CheckEndpointNameAvailabilityInput(TypedDict, total=False):
        key "autoGeneratedDomainNameLabelScope": Union[str, AutoGeneratedDomainNameLabelScope]
        key "name": Required[str]
        key "type": Required[Union[str, ResourceType]]
        auto_generated_domain_name_label_scope: Union[str, AutoGeneratedDomainNameLabelScope]
        name: str
        type: Union[str, ResourceType]


    class azure.mgmt.cdn.types.CheckHostNameAvailabilityInput(TypedDict, total=False):
        key "hostName": Required[str]
        host_name: str


    class azure.mgmt.cdn.types.CheckNameAvailabilityInput(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[Union[str, ResourceType]]
        name: str
        type: Union[str, ResourceType]


    class azure.mgmt.cdn.types.ClientPortMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, ClientPortOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, ClientPortOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.CompressionSettings(TypedDict, total=False):
        key "isCompressionEnabled": bool
        contentTypesToCompress: list[str]
        content_types_to_compress: list[str]
        is_compression_enabled: bool


    class azure.mgmt.cdn.types.CookiesMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, CookiesOperator]]
        key "selector": str
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, CookiesOperator]
        selector: str
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.CustomDomainParameters(TypedDict, total=False):
        key "properties": ForwardRef('CustomDomainPropertiesParameters', module='types')
        properties: CustomDomainPropertiesParameters


    class azure.mgmt.cdn.types.CustomDomainPropertiesParameters(TypedDict, total=False):
        key "hostName": Required[str]
        host_name: str


    class azure.mgmt.cdn.types.CustomRule(TypedDict, total=False):
        key "action": Required[Union[str, ActionType]]
        key "enabledState": Union[str, CustomRuleEnabledState]
        key "matchConditions": Required[list[MatchCondition]]
        key "name": Required[str]
        key "priority": Required[int]
        action: Union[str, ActionType]
        enabled_state: Union[str, CustomRuleEnabledState]
        match_conditions: list[MatchCondition]
        name: str
        priority: int


    class azure.mgmt.cdn.types.CustomRuleList(TypedDict, total=False):
        rules: list[CustomRule]


    class azure.mgmt.cdn.types.CustomerCertificateParameters(TypedDict, total=False):
        key "certificateAuthority": str
        key "expirationDate": str
        key "secretSource": Required[ResourceReference]
        key "secretVersion": str
        key "subject": str
        key "thumbprint": str
        key "type": Required[Literal[SecretType.CUSTOMER_CERTIFICATE]]
        key "useLatestVersion": bool
        certificate_authority: str
        expiration_date: str
        secret_source: ResourceReference
        secret_version: str
        subject: str
        subjectAlternativeNames: list[str]
        subject_alternative_names: list[str]
        thumbprint: str
        type: Literal[SecretType.CUSTOMER_CERTIFICATE]
        use_latest_version: bool


    class azure.mgmt.cdn.types.DeepCreatedCustomDomain(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('DeepCreatedCustomDomainProperties', module='types')
        name: str
        properties: DeepCreatedCustomDomainProperties


    class azure.mgmt.cdn.types.DeepCreatedCustomDomainProperties(TypedDict, total=False):
        key "hostName": Required[str]
        key "validationData": str
        host_name: str
        validation_data: str


    class azure.mgmt.cdn.types.DeepCreatedOrigin(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('DeepCreatedOriginProperties', module='types')
        name: str
        properties: DeepCreatedOriginProperties


    class azure.mgmt.cdn.types.DeepCreatedOriginGroup(TypedDict, total=False):
        key "name": Required[str]
        key "properties": ForwardRef('DeepCreatedOriginGroupProperties', module='types')
        name: str
        properties: DeepCreatedOriginGroupProperties


    class azure.mgmt.cdn.types.DeepCreatedOriginGroupProperties(TypedDict, total=False):
        key "healthProbeSettings": ForwardRef('HealthProbeParameters', module='types')
        key "origins": Required[list[ResourceReference]]
        key "responseBasedOriginErrorDetectionSettings": ForwardRef('ResponseBasedOriginErrorDetectionParameters', module='types')
        key "trafficRestorationTimeToHealedOrNewEndpointsInMinutes": int
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int


    class azure.mgmt.cdn.types.DeepCreatedOriginProperties(TypedDict, total=False):
        key "enabled": bool
        key "hostName": Required[str]
        key "httpPort": int
        key "httpsPort": int
        key "originHostHeader": str
        key "priority": int
        key "privateEndpointStatus": Union[str, PrivateEndpointStatus]
        key "privateLinkAlias": str
        key "privateLinkApprovalMessage": str
        key "privateLinkLocation": str
        key "privateLinkResourceId": str
        key "weight": int
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
        weight: int


    class azure.mgmt.cdn.types.DeliveryRule(TypedDict, total=False):
        key "actions": Required[list[DeliveryRuleAction]]
        key "name": str
        key "order": Required[int]
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        name: str
        order: int


    class azure.mgmt.cdn.types.DeliveryRuleActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CACHE_EXPIRATION = "CacheExpiration"
        CACHE_KEY_QUERY_STRING = "CacheKeyQueryString"
        MODIFY_REQUEST_HEADER = "ModifyRequestHeader"
        MODIFY_RESPONSE_HEADER = "ModifyResponseHeader"
        ORIGIN_GROUP_OVERRIDE = "OriginGroupOverride"
        ROUTE_CONFIGURATION_OVERRIDE = "RouteConfigurationOverride"
        URL_REDIRECT = "UrlRedirect"
        URL_REWRITE = "UrlRewrite"
        URL_SIGNING = "UrlSigning"


    class azure.mgmt.cdn.types.DeliveryRuleActionParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CACHE_EXPIRATION_ACTION_PARAMETERS = "DeliveryRuleCacheExpirationActionParameters"
        DELIVERY_RULE_CACHE_KEY_QUERY_STRING_BEHAVIOR_ACTION_PARAMETERS = "DeliveryRuleCacheKeyQueryStringBehaviorActionParameters"
        DELIVERY_RULE_HEADER_ACTION_PARAMETERS = "DeliveryRuleHeaderActionParameters"
        DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleOriginGroupOverrideActionParameters"
        DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS = "DeliveryRuleRouteConfigurationOverrideActionParameters"
        DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS = "DeliveryRuleUrlRedirectActionParameters"
        DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS = "DeliveryRuleUrlRewriteActionParameters"
        DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS = "DeliveryRuleUrlSigningActionParameters"


    class azure.mgmt.cdn.types.DeliveryRuleCacheExpirationAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.CACHE_EXPIRATION]]
        key "parameters": Required[CacheExpirationActionParameters]
        name: Literal[DeliveryRuleActionEnum.CACHE_EXPIRATION]
        parameters: CacheExpirationActionParameters


    class azure.mgmt.cdn.types.DeliveryRuleCacheKeyQueryStringAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.CACHE_KEY_QUERY_STRING]]
        key "parameters": Required[CacheKeyQueryStringActionParameters]
        name: Literal[DeliveryRuleActionEnum.CACHE_KEY_QUERY_STRING]
        parameters: CacheKeyQueryStringActionParameters


    class azure.mgmt.cdn.types.DeliveryRuleClientPortCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.CLIENT_PORT]]
        key "parameters": Required[ClientPortMatchConditionParameters]
        name: Literal[MatchVariable.CLIENT_PORT]
        parameters: ClientPortMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleConditionParametersType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELIVERY_RULE_CLIENT_PORT_CONDITION_PARAMETERS = "DeliveryRuleClientPortConditionParameters"
        DELIVERY_RULE_COOKIES_CONDITION_PARAMETERS = "DeliveryRuleCookiesConditionParameters"
        DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS = "DeliveryRuleHostNameConditionParameters"
        DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS = "DeliveryRuleHttpVersionConditionParameters"
        DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS = "DeliveryRuleIsDeviceConditionParameters"
        DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS = "DeliveryRulePostArgsConditionParameters"
        DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS = "DeliveryRuleQueryStringConditionParameters"
        DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS = "DeliveryRuleRemoteAddressConditionParameters"
        DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS = "DeliveryRuleRequestBodyConditionParameters"
        DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS = "DeliveryRuleRequestHeaderConditionParameters"
        DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS = "DeliveryRuleRequestMethodConditionParameters"
        DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS = "DeliveryRuleRequestSchemeConditionParameters"
        DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS = "DeliveryRuleRequestUriConditionParameters"
        DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS = "DeliveryRuleServerPortConditionParameters"
        DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS = "DeliveryRuleSocketAddrConditionParameters"
        DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS = "DeliveryRuleSslProtocolConditionParameters"
        DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS = "DeliveryRuleUrlFilenameConditionParameters"
        DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlFileExtensionMatchConditionParameters"
        DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS = "DeliveryRuleUrlPathMatchConditionParameters"


    class azure.mgmt.cdn.types.DeliveryRuleCookiesCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.COOKIES]]
        key "parameters": Required[CookiesMatchConditionParameters]
        name: Literal[MatchVariable.COOKIES]
        parameters: CookiesMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleHostNameCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.HOST_NAME]]
        key "parameters": Required[HostNameMatchConditionParameters]
        name: Literal[MatchVariable.HOST_NAME]
        parameters: HostNameMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleHttpVersionCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.HTTP_VERSION]]
        key "parameters": Required[HttpVersionMatchConditionParameters]
        name: Literal[MatchVariable.HTTP_VERSION]
        parameters: HttpVersionMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleIsDeviceCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.IS_DEVICE]]
        key "parameters": Required[IsDeviceMatchConditionParameters]
        name: Literal[MatchVariable.IS_DEVICE]
        parameters: IsDeviceMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRulePostArgsCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.POST_ARGS]]
        key "parameters": Required[PostArgsMatchConditionParameters]
        name: Literal[MatchVariable.POST_ARGS]
        parameters: PostArgsMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleQueryStringCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.QUERY_STRING]]
        key "parameters": Required[QueryStringMatchConditionParameters]
        name: Literal[MatchVariable.QUERY_STRING]
        parameters: QueryStringMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRemoteAddressCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REMOTE_ADDRESS]]
        key "parameters": Required[RemoteAddressMatchConditionParameters]
        name: Literal[MatchVariable.REMOTE_ADDRESS]
        parameters: RemoteAddressMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestBodyCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REQUEST_BODY]]
        key "parameters": Required[RequestBodyMatchConditionParameters]
        name: Literal[MatchVariable.REQUEST_BODY]
        parameters: RequestBodyMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestHeaderAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.MODIFY_REQUEST_HEADER]]
        key "parameters": Required[HeaderActionParameters]
        name: Literal[DeliveryRuleActionEnum.MODIFY_REQUEST_HEADER]
        parameters: HeaderActionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestHeaderCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REQUEST_HEADER]]
        key "parameters": Required[RequestHeaderMatchConditionParameters]
        name: Literal[MatchVariable.REQUEST_HEADER]
        parameters: RequestHeaderMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestMethodCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REQUEST_METHOD]]
        key "parameters": Required[RequestMethodMatchConditionParameters]
        name: Literal[MatchVariable.REQUEST_METHOD]
        parameters: RequestMethodMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestSchemeCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REQUEST_SCHEME]]
        key "parameters": Required[RequestSchemeMatchConditionParameters]
        name: Literal[MatchVariable.REQUEST_SCHEME]
        parameters: RequestSchemeMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRequestUriCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.REQUEST_URI]]
        key "parameters": Required[RequestUriMatchConditionParameters]
        name: Literal[MatchVariable.REQUEST_URI]
        parameters: RequestUriMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleResponseHeaderAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.MODIFY_RESPONSE_HEADER]]
        key "parameters": Required[HeaderActionParameters]
        name: Literal[DeliveryRuleActionEnum.MODIFY_RESPONSE_HEADER]
        parameters: HeaderActionParameters


    class azure.mgmt.cdn.types.DeliveryRuleRouteConfigurationOverrideAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.ROUTE_CONFIGURATION_OVERRIDE]]
        key "parameters": Required[RouteConfigurationOverrideActionParameters]
        name: Literal[DeliveryRuleActionEnum.ROUTE_CONFIGURATION_OVERRIDE]
        parameters: RouteConfigurationOverrideActionParameters


    class azure.mgmt.cdn.types.DeliveryRuleServerPortCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.SERVER_PORT]]
        key "parameters": Required[ServerPortMatchConditionParameters]
        name: Literal[MatchVariable.SERVER_PORT]
        parameters: ServerPortMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleSocketAddrCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.SOCKET_ADDR]]
        key "parameters": Required[SocketAddrMatchConditionParameters]
        name: Literal[MatchVariable.SOCKET_ADDR]
        parameters: SocketAddrMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleSslProtocolCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.SSL_PROTOCOL]]
        key "parameters": Required[SslProtocolMatchConditionParameters]
        name: Literal[MatchVariable.SSL_PROTOCOL]
        parameters: SslProtocolMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleUrlFileExtensionCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.URL_FILE_EXTENSION]]
        key "parameters": Required[UrlFileExtensionMatchConditionParameters]
        name: Literal[MatchVariable.URL_FILE_EXTENSION]
        parameters: UrlFileExtensionMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleUrlFileNameCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.URL_FILE_NAME]]
        key "parameters": Required[UrlFileNameMatchConditionParameters]
        name: Literal[MatchVariable.URL_FILE_NAME]
        parameters: UrlFileNameMatchConditionParameters


    class azure.mgmt.cdn.types.DeliveryRuleUrlPathCondition(TypedDict, total=False):
        key "name": Required[Literal[MatchVariable.URL_PATH]]
        key "parameters": Required[UrlPathMatchConditionParameters]
        name: Literal[MatchVariable.URL_PATH]
        parameters: UrlPathMatchConditionParameters


    class azure.mgmt.cdn.types.DomainValidationProperties(TypedDict, total=False):
        key "expirationDate": str
        key "validationToken": str
        expiration_date: str
        validation_token: str


    class azure.mgmt.cdn.types.Endpoint(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('EndpointProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: EndpointProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cdn.types.EndpointProperties(EndpointPropertiesUpdateParameters):
        key "defaultOriginGroup": ForwardRef('ResourceReference', module='types')
        key "deliveryPolicy": ForwardRef('EndpointPropertiesUpdateParametersDeliveryPolicy', module='types')
        key "hostName": str
        key "isCompressionEnabled": bool
        key "isHttpAllowed": bool
        key "isHttpsAllowed": bool
        key "optimizationType": Union[str, OptimizationType]
        key "originHostHeader": str
        key "originPath": str
        key "origins": Required[list[DeepCreatedOrigin]]
        key "probePath": str
        key "provisioningState": Union[str, EndpointProvisioningState]
        key "queryStringCachingBehavior": Union[str, QueryStringCachingBehavior]
        key "resourceState": Union[str, EndpointResourceState]
        key "webApplicationFirewallPolicyLink": ForwardRef('EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        contentTypesToCompress: list[str]
        content_types_to_compress: list[str]
        customDomains: list[DeepCreatedCustomDomain]
        custom_domains: list[DeepCreatedCustomDomain]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geoFilters: list[GeoFilter]
        geo_filters: list[GeoFilter]
        host_name: str
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        originGroups: list[DeepCreatedOriginGroup]
        origin_groups: list[DeepCreatedOriginGroup]
        origin_host_header: str
        origin_path: str
        origins: list[DeepCreatedOrigin]
        probe_path: str
        provisioning_state: Union[str, EndpointProvisioningState]
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        resource_state: Union[str, EndpointResourceState]
        urlSigningKeys: list[UrlSigningKey]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.cdn.types.EndpointPropertiesUpdateParameters(TypedDict, total=False):
        key "defaultOriginGroup": ForwardRef('ResourceReference', module='types')
        key "deliveryPolicy": ForwardRef('EndpointPropertiesUpdateParametersDeliveryPolicy', module='types')
        key "isCompressionEnabled": bool
        key "isHttpAllowed": bool
        key "isHttpsAllowed": bool
        key "optimizationType": Union[str, OptimizationType]
        key "originHostHeader": str
        key "originPath": str
        key "probePath": str
        key "queryStringCachingBehavior": Union[str, QueryStringCachingBehavior]
        key "webApplicationFirewallPolicyLink": ForwardRef('EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink', module='types')
        contentTypesToCompress: list[str]
        content_types_to_compress: list[str]
        default_origin_group: ResourceReference
        delivery_policy: EndpointPropertiesUpdateParametersDeliveryPolicy
        geoFilters: list[GeoFilter]
        geo_filters: list[GeoFilter]
        is_compression_enabled: bool
        is_http_allowed: bool
        is_https_allowed: bool
        optimization_type: Union[str, OptimizationType]
        origin_host_header: str
        origin_path: str
        probe_path: str
        query_string_caching_behavior: Union[str, QueryStringCachingBehavior]
        urlSigningKeys: list[UrlSigningKey]
        url_signing_keys: list[UrlSigningKey]
        web_application_firewall_policy_link: EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink


    class azure.mgmt.cdn.types.EndpointPropertiesUpdateParametersDeliveryPolicy(TypedDict, total=False):
        key "description": str
        key "rules": Required[list[DeliveryRule]]
        description: str
        rules: list[DeliveryRule]


    class azure.mgmt.cdn.types.EndpointPropertiesUpdateParametersWebApplicationFirewallPolicyLink(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cdn.types.EndpointUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('EndpointPropertiesUpdateParameters', module='types')
        properties: EndpointPropertiesUpdateParameters
        tags: dict[str, str]


    class azure.mgmt.cdn.types.GeoFilter(TypedDict, total=False):
        key "action": Required[Union[str, GeoFilterActions]]
        key "countryCodes": Required[list[str]]
        key "relativePath": Required[str]
        action: Union[str, GeoFilterActions]
        country_codes: list[str]
        relative_path: str


    class azure.mgmt.cdn.types.HeaderActionParameters(TypedDict, total=False):
        key "headerAction": Required[Union[str, HeaderAction]]
        key "headerName": Required[str]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_HEADER_ACTION_PARAMETERS]]
        key "value": str
        header_action: Union[str, HeaderAction]
        header_name: str
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_HEADER_ACTION_PARAMETERS]
        value: str


    class azure.mgmt.cdn.types.HealthProbeParameters(TypedDict, total=False):
        key "probeIntervalInSeconds": int
        key "probePath": str
        key "probeProtocol": Union[str, ProbeProtocol]
        key "probeRequestType": Union[str, HealthProbeRequestType]
        probe_interval_in_seconds: int
        probe_path: str
        probe_protocol: Union[str, ProbeProtocol]
        probe_request_type: Union[str, HealthProbeRequestType]


    class azure.mgmt.cdn.types.HostNameMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, HostNameOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, HostNameOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HOST_NAME_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.HttpErrorRangeParameters(TypedDict, total=False):
        key "begin": int
        key "end": int
        begin: int
        end: int


    class azure.mgmt.cdn.types.HttpVersionMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, HttpVersionOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, HttpVersionOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_HTTP_VERSION_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.IsDeviceMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, IsDeviceOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS]]
        matchValues: list[Union[str, IsDeviceMatchConditionParametersMatchValuesItem]]
        match_values: list[Union[str, IsDeviceMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, IsDeviceOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_IS_DEVICE_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.KeyVaultCertificateSourceParameters(TypedDict, total=False):
        key "deleteRule": Required[Union[str, DeleteRule]]
        key "resourceGroupName": Required[str]
        key "secretName": Required[str]
        key "secretVersion": str
        key "subscriptionId": Required[str]
        key "typeName": Required[Literal[CertificateSourceParametersType.KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS]]
        key "updateRule": Required[Union[str, UpdateRule]]
        key "vaultName": Required[str]
        delete_rule: Union[str, DeleteRule]
        resource_group_name: str
        secret_name: str
        secret_version: str
        subscription_id: str
        type_name: Literal[CertificateSourceParametersType.KEY_VAULT_CERTIFICATE_SOURCE_PARAMETERS]
        update_rule: Union[str, UpdateRule]
        vault_name: str


    class azure.mgmt.cdn.types.KeyVaultSigningKeyParameters(TypedDict, total=False):
        key "resourceGroupName": Required[str]
        key "secretName": Required[str]
        key "secretVersion": Required[str]
        key "subscriptionId": Required[str]
        key "typeName": Required[Union[str, KeyVaultSigningKeyParametersTypeName]]
        key "vaultName": Required[str]
        resource_group_name: str
        secret_name: str
        secret_version: str
        subscription_id: str
        type_name: Union[str, KeyVaultSigningKeyParametersTypeName]
        vault_name: str


    class azure.mgmt.cdn.types.LoadBalancingSettingsParameters(TypedDict, total=False):
        key "additionalLatencyInMilliseconds": int
        key "sampleSize": int
        key "successfulSamplesRequired": int
        additional_latency_in_milliseconds: int
        sample_size: int
        successful_samples_required: int


    class azure.mgmt.cdn.types.LoadParameters(TypedDict, total=False):
        key "contentPaths": Required[list[str]]
        content_paths: list[str]


    class azure.mgmt.cdn.types.ManagedCertificateParameters(TypedDict, total=False):
        key "expirationDate": str
        key "subject": str
        key "type": Required[Literal[SecretType.MANAGED_CERTIFICATE]]
        expiration_date: str
        subject: str
        type: Literal[SecretType.MANAGED_CERTIFICATE]


    class azure.mgmt.cdn.types.ManagedRuleGroupOverride(TypedDict, total=False):
        key "ruleGroupName": Required[str]
        rule_group_name: str
        rules: list[ManagedRuleOverride]


    class azure.mgmt.cdn.types.ManagedRuleOverride(TypedDict, total=False):
        key "action": Union[str, ActionType]
        key "enabledState": Union[str, ManagedRuleEnabledState]
        key "ruleId": Required[str]
        action: Union[str, ActionType]
        enabled_state: Union[str, ManagedRuleEnabledState]
        rule_id: str


    class azure.mgmt.cdn.types.ManagedRuleSet(TypedDict, total=False):
        key "anomalyScore": int
        key "ruleSetType": Required[str]
        key "ruleSetVersion": Required[str]
        anomaly_score: int
        ruleGroupOverrides: list[ManagedRuleGroupOverride]
        rule_group_overrides: list[ManagedRuleGroupOverride]
        rule_set_type: str
        rule_set_version: str


    class azure.mgmt.cdn.types.ManagedRuleSetList(TypedDict, total=False):
        managedRuleSets: list[ManagedRuleSet]
        managed_rule_sets: list[ManagedRuleSet]


    class azure.mgmt.cdn.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]
        user_assigned_identities: dict[str, UserAssignedIdentity]


    class azure.mgmt.cdn.types.MatchCondition(TypedDict, total=False):
        key "matchValue": Required[list[str]]
        key "matchVariable": Required[Union[str, WafMatchVariable]]
        key "negateCondition": bool
        key "operator": Required[Union[str, Operator]]
        key "selector": str
        match_value: list[str]
        match_variable: Union[str, WafMatchVariable]
        negate_condition: bool
        operator: Union[str, Operator]
        selector: str
        transforms: list[Union[str, TransformType]]


    class azure.mgmt.cdn.types.MatchVariable(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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


    class azure.mgmt.cdn.types.MigrationEndpointMapping(TypedDict, total=False):
        key "migratedFrom": str
        key "migratedTo": str
        migrated_from: str
        migrated_to: str


    class azure.mgmt.cdn.types.MigrationParameters(TypedDict, total=False):
        key "classicResourceReference": Required[ResourceReference]
        key "profileName": Required[str]
        key "sku": Required[Sku]
        classic_resource_reference: ResourceReference
        migrationWebApplicationFirewallMappings: list[MigrationWebApplicationFirewallMapping]
        migration_web_application_firewall_mappings: list[MigrationWebApplicationFirewallMapping]
        profile_name: str
        sku: Sku


    class azure.mgmt.cdn.types.MigrationWebApplicationFirewallMapping(TypedDict, total=False):
        key "migratedFrom": ForwardRef('ResourceReference', module='types')
        key "migratedTo": ForwardRef('ResourceReference', module='types')
        migrated_from: ResourceReference
        migrated_to: ResourceReference


    class azure.mgmt.cdn.types.Origin(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OriginProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OriginProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.OriginAuthenticationProperties(TypedDict, total=False):
        key "scope": str
        key "type": Union[str, OriginAuthenticationType]
        key "userAssignedIdentity": ForwardRef('ResourceReference', module='types')
        scope: str
        type: Union[str, OriginAuthenticationType]
        user_assigned_identity: ResourceReference


    class azure.mgmt.cdn.types.OriginGroup(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OriginGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OriginGroupProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.OriginGroupOverride(TypedDict, total=False):
        key "forwardingProtocol": Union[str, ForwardingProtocol]
        key "originGroup": ForwardRef('ResourceReference', module='types')
        forwarding_protocol: Union[str, ForwardingProtocol]
        origin_group: ResourceReference


    class azure.mgmt.cdn.types.OriginGroupOverrideAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.ORIGIN_GROUP_OVERRIDE]]
        key "parameters": Required[OriginGroupOverrideActionParameters]
        name: Literal[DeliveryRuleActionEnum.ORIGIN_GROUP_OVERRIDE]
        parameters: OriginGroupOverrideActionParameters


    class azure.mgmt.cdn.types.OriginGroupOverrideActionParameters(TypedDict, total=False):
        key "originGroup": Required[ResourceReference]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS]]
        origin_group: ResourceReference
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ORIGIN_GROUP_OVERRIDE_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.OriginGroupProperties(OriginGroupUpdatePropertiesParameters):
        key "healthProbeSettings": ForwardRef('HealthProbeParameters', module='types')
        key "provisioningState": Union[str, OriginGroupProvisioningState]
        key "resourceState": Union[str, OriginGroupResourceState]
        key "responseBasedOriginErrorDetectionSettings": ForwardRef('ResponseBasedOriginErrorDetectionParameters', module='types')
        key "trafficRestorationTimeToHealedOrNewEndpointsInMinutes": int
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        provisioning_state: Union[str, OriginGroupProvisioningState]
        resource_state: Union[str, OriginGroupResourceState]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int


    class azure.mgmt.cdn.types.OriginGroupUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('OriginGroupUpdatePropertiesParameters', module='types')
        properties: OriginGroupUpdatePropertiesParameters


    class azure.mgmt.cdn.types.OriginGroupUpdatePropertiesParameters(TypedDict, total=False):
        key "healthProbeSettings": ForwardRef('HealthProbeParameters', module='types')
        key "responseBasedOriginErrorDetectionSettings": ForwardRef('ResponseBasedOriginErrorDetectionParameters', module='types')
        key "trafficRestorationTimeToHealedOrNewEndpointsInMinutes": int
        health_probe_settings: HealthProbeParameters
        origins: list[ResourceReference]
        response_based_origin_error_detection_settings: ResponseBasedOriginErrorDetectionParameters
        traffic_restoration_time_to_healed_or_new_endpoints_in_minutes: int


    class azure.mgmt.cdn.types.OriginProperties(OriginUpdatePropertiesParameters):
        key "enabled": bool
        key "hostName": Required[str]
        key "httpPort": int
        key "httpsPort": int
        key "originHostHeader": str
        key "priority": int
        key "privateEndpointStatus": Union[str, PrivateEndpointStatus]
        key "privateLinkAlias": str
        key "privateLinkApprovalMessage": str
        key "privateLinkLocation": str
        key "privateLinkResourceId": str
        key "provisioningState": Union[str, OriginProvisioningState]
        key "resourceState": Union[str, OriginResourceState]
        key "weight": int
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


    class azure.mgmt.cdn.types.OriginUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('OriginUpdatePropertiesParameters', module='types')
        properties: OriginUpdatePropertiesParameters


    class azure.mgmt.cdn.types.OriginUpdatePropertiesParameters(TypedDict, total=False):
        key "enabled": bool
        key "hostName": str
        key "httpPort": int
        key "httpsPort": int
        key "originHostHeader": str
        key "priority": int
        key "privateLinkAlias": str
        key "privateLinkApprovalMessage": str
        key "privateLinkLocation": str
        key "privateLinkResourceId": str
        key "weight": int
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


    class azure.mgmt.cdn.types.PolicySettings(TypedDict, total=False):
        key "defaultCustomBlockResponseBody": str
        key "defaultCustomBlockResponseStatusCode": Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]
        key "defaultRedirectUrl": str
        key "enabledState": Union[str, PolicyEnabledState]
        key "mode": Union[str, PolicyMode]
        default_custom_block_response_body: str
        default_custom_block_response_status_code: Union[int, PolicySettingsDefaultCustomBlockResponseStatusCode]
        default_redirect_url: str
        enabled_state: Union[str, PolicyEnabledState]
        mode: Union[str, PolicyMode]


    class azure.mgmt.cdn.types.PostArgsMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, PostArgsOperator]]
        key "selector": str
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, PostArgsOperator]
        selector: str
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_POST_ARGS_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.Profile(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "kind": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProfileProperties', module='types')
        key "sku": Required[Sku]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        kind: str
        location: str
        name: str
        properties: ProfileProperties
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.cdn.types.ProfileChangeSkuWafMapping(TypedDict, total=False):
        key "changeToWafPolicy": Required[ResourceReference]
        key "securityPolicyName": Required[str]
        change_to_waf_policy: ResourceReference
        security_policy_name: str


    class azure.mgmt.cdn.types.ProfileLogScrubbing(TypedDict, total=False):
        key "state": Union[str, ProfileScrubbingState]
        scrubbingRules: list[ProfileScrubbingRules]
        scrubbing_rules: list[ProfileScrubbingRules]
        state: Union[str, ProfileScrubbingState]


    class azure.mgmt.cdn.types.ProfileProperties(TypedDict, total=False):
        key "frontDoorId": str
        key "logScrubbing": ForwardRef('ProfileLogScrubbing', module='types')
        key "originResponseTimeoutSeconds": int
        key "provisioningState": Union[str, ProfileProvisioningState]
        key "resourceState": Union[str, ProfileResourceState]
        extendedProperties: dict[str, str]
        extended_properties: dict[str, str]
        front_door_id: str
        log_scrubbing: ProfileLogScrubbing
        origin_response_timeout_seconds: int
        provisioning_state: Union[str, ProfileProvisioningState]
        resource_state: Union[str, ProfileResourceState]


    class azure.mgmt.cdn.types.ProfilePropertiesUpdateParameters(TypedDict, total=False):
        key "logScrubbing": ForwardRef('ProfileLogScrubbing', module='types')
        key "originResponseTimeoutSeconds": int
        log_scrubbing: ProfileLogScrubbing
        origin_response_timeout_seconds: int


    class azure.mgmt.cdn.types.ProfileScrubbingRules(TypedDict, total=False):
        key "matchVariable": Required[Union[str, ScrubbingRuleEntryMatchVariable]]
        key "selector": str
        key "selectorMatchOperator": Required[Union[str, ScrubbingRuleEntryMatchOperator]]
        key "state": Union[str, ScrubbingRuleEntryState]
        match_variable: Union[str, ScrubbingRuleEntryMatchVariable]
        selector: str
        selector_match_operator: Union[str, ScrubbingRuleEntryMatchOperator]
        state: Union[str, ScrubbingRuleEntryState]


    class azure.mgmt.cdn.types.ProfileUpdateParameters(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('ProfilePropertiesUpdateParameters', module='types')
        identity: ManagedServiceIdentity
        properties: ProfilePropertiesUpdateParameters
        tags: dict[str, str]


    class azure.mgmt.cdn.types.ProfileUpgradeParameters(TypedDict, total=False):
        key "wafMappingList": Required[list[ProfileChangeSkuWafMapping]]
        waf_mapping_list: list[ProfileChangeSkuWafMapping]


    class azure.mgmt.cdn.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.PurgeParameters(TypedDict, total=False):
        key "contentPaths": Required[list[str]]
        content_paths: list[str]


    class azure.mgmt.cdn.types.QueryStringMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, QueryStringOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, QueryStringOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_QUERY_STRING_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RateLimitRule(CustomRule):
        key "action": Required[Union[str, ActionType]]
        key "enabledState": Union[str, CustomRuleEnabledState]
        key "matchConditions": Required[list[MatchCondition]]
        key "name": Required[str]
        key "priority": Required[int]
        key "rateLimitDurationInMinutes": Required[int]
        key "rateLimitThreshold": Required[int]
        action: Union[str, ActionType]
        enabled_state: Union[str, CustomRuleEnabledState]
        match_conditions: list[MatchCondition]
        name: str
        priority: int
        rate_limit_duration_in_minutes: int
        rate_limit_threshold: int


    class azure.mgmt.cdn.types.RateLimitRuleList(TypedDict, total=False):
        rules: list[RateLimitRule]


    class azure.mgmt.cdn.types.RemoteAddressMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RemoteAddressOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RemoteAddressOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REMOTE_ADDRESS_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RequestBodyMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RequestBodyOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestBodyOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_BODY_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RequestHeaderMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RequestHeaderOperator]]
        key "selector": str
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestHeaderOperator]
        selector: str
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_HEADER_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RequestMethodMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RequestMethodOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS]]
        matchValues: list[Union[str, RequestMethodMatchConditionParametersMatchValuesItem]]
        match_values: list[Union[str, RequestMethodMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, RequestMethodOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_METHOD_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RequestSchemeMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RequestSchemeMatchConditionParametersOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS]]
        matchValues: list[Union[str, RequestSchemeMatchConditionParametersMatchValuesItem]]
        match_values: list[Union[str, RequestSchemeMatchConditionParametersMatchValuesItem]]
        negate_condition: bool
        operator: Union[str, RequestSchemeMatchConditionParametersOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_SCHEME_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.RequestUriMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, RequestUriOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, RequestUriOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_REQUEST_URI_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.ResourceReference(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.cdn.types.ResponseBasedOriginErrorDetectionParameters(TypedDict, total=False):
        key "responseBasedDetectedErrorTypes": Union[str, ResponseBasedDetectedErrorTypes]
        key "responseBasedFailoverThresholdPercentage": int
        httpErrorRanges: list[HttpErrorRangeParameters]
        http_error_ranges: list[HttpErrorRangeParameters]
        response_based_detected_error_types: Union[str, ResponseBasedDetectedErrorTypes]
        response_based_failover_threshold_percentage: int


    class azure.mgmt.cdn.types.Route(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RouteProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RouteProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.RouteConfigurationOverrideActionParameters(TypedDict, total=False):
        key "cacheConfiguration": ForwardRef('CacheConfiguration', module='types')
        key "originGroupOverride": ForwardRef('OriginGroupOverride', module='types')
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS]]
        cache_configuration: CacheConfiguration
        origin_group_override: OriginGroupOverride
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_ROUTE_CONFIGURATION_OVERRIDE_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.RouteProperties(TypedDict, total=False):
        key "cacheConfiguration": ForwardRef('AfdRouteCacheConfiguration', module='types')
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "enabledState": Union[str, EnabledState]
        key "endpointName": str
        key "forwardingProtocol": Union[str, ForwardingProtocol]
        key "httpsRedirect": Union[str, HttpsRedirect]
        key "linkToDefaultDomain": Union[str, LinkToDefaultDomain]
        key "originGroup": ForwardRef('ResourceReference', module='types')
        key "originPath": str
        key "provisioningState": Union[str, AfdProvisioningState]
        cache_configuration: AfdRouteCacheConfiguration
        customDomains: list[ActivatedResourceReference]
        custom_domains: list[ActivatedResourceReference]
        deployment_status: Union[str, DeploymentStatus]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        origin_group: ResourceReference
        origin_path: str
        patternsToMatch: list[str]
        patterns_to_match: list[str]
        provisioning_state: Union[str, AfdProvisioningState]
        ruleSets: list[ResourceReference]
        rule_sets: list[ResourceReference]
        supportedProtocols: list[Union[str, AFDEndpointProtocols]]
        supported_protocols: list[Union[str, AFDEndpointProtocols]]


    class azure.mgmt.cdn.types.RouteUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('RouteUpdatePropertiesParameters', module='types')
        properties: RouteUpdatePropertiesParameters


    class azure.mgmt.cdn.types.RouteUpdatePropertiesParameters(TypedDict, total=False):
        key "cacheConfiguration": ForwardRef('AfdRouteCacheConfiguration', module='types')
        key "enabledState": Union[str, EnabledState]
        key "endpointName": str
        key "forwardingProtocol": Union[str, ForwardingProtocol]
        key "httpsRedirect": Union[str, HttpsRedirect]
        key "linkToDefaultDomain": Union[str, LinkToDefaultDomain]
        key "originGroup": ForwardRef('ResourceReference', module='types')
        key "originPath": str
        cache_configuration: AfdRouteCacheConfiguration
        customDomains: list[ActivatedResourceReference]
        custom_domains: list[ActivatedResourceReference]
        enabled_state: Union[str, EnabledState]
        endpoint_name: str
        forwarding_protocol: Union[str, ForwardingProtocol]
        https_redirect: Union[str, HttpsRedirect]
        link_to_default_domain: Union[str, LinkToDefaultDomain]
        origin_group: ResourceReference
        origin_path: str
        patternsToMatch: list[str]
        patterns_to_match: list[str]
        ruleSets: list[ResourceReference]
        rule_sets: list[ResourceReference]
        supportedProtocols: list[Union[str, AFDEndpointProtocols]]
        supported_protocols: list[Union[str, AFDEndpointProtocols]]


    class azure.mgmt.cdn.types.Rule(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RuleProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.RuleProperties(TypedDict, total=False):
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "matchProcessingBehavior": Union[str, MatchProcessingBehavior]
        key "order": int
        key "provisioningState": Union[str, AfdProvisioningState]
        key "ruleSetName": str
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        deployment_status: Union[str, DeploymentStatus]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        provisioning_state: Union[str, AfdProvisioningState]
        rule_set_name: str


    class azure.mgmt.cdn.types.RuleSet(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('RuleSetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleSetProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.RuleSetProperties(AFDStateProperties):
        key "batchMode": bool
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        batch_mode: bool
        deployment_status: Union[str, DeploymentStatus]
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]
        rules: list[BatchRuleProperties]


    class azure.mgmt.cdn.types.RuleUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('RuleUpdatePropertiesParameters', module='types')
        properties: RuleUpdatePropertiesParameters


    class azure.mgmt.cdn.types.RuleUpdatePropertiesParameters(TypedDict, total=False):
        key "matchProcessingBehavior": Union[str, MatchProcessingBehavior]
        key "order": int
        key "ruleSetName": str
        actions: list[DeliveryRuleAction]
        conditions: list[DeliveryRuleCondition]
        match_processing_behavior: Union[str, MatchProcessingBehavior]
        order: int
        rule_set_name: str


    class azure.mgmt.cdn.types.Secret(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecretProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecretProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.SecretProperties(AFDStateProperties):
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "parameters": ForwardRef('SecretParameters', module='types')
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        deployment_status: Union[str, DeploymentStatus]
        parameters: SecretParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]


    class azure.mgmt.cdn.types.SecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_FIRST_PARTY_MANAGED_CERTIFICATE = "AzureFirstPartyManagedCertificate"
        CUSTOMER_CERTIFICATE = "CustomerCertificate"
        MANAGED_CERTIFICATE = "ManagedCertificate"
        URL_SIGNING_KEY = "UrlSigningKey"


    class azure.mgmt.cdn.types.SecurityPolicy(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SecurityPolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SecurityPolicyProperties
        system_data: SystemData
        type: str


    class azure.mgmt.cdn.types.SecurityPolicyProperties(AFDStateProperties):
        key "deploymentStatus": Union[str, DeploymentStatus]
        key "parameters": ForwardRef('SecurityPolicyPropertiesParameters', module='types')
        key "profileName": str
        key "provisioningState": Union[str, AfdProvisioningState]
        deployment_status: Union[str, DeploymentStatus]
        parameters: SecurityPolicyPropertiesParameters
        profile_name: str
        provisioning_state: Union[str, AfdProvisioningState]


    class azure.mgmt.cdn.types.SecurityPolicyPropertiesParameters(TypedDict, total=False):
        key "type": Required[Literal[SecurityPolicyType.WEB_APPLICATION_FIREWALL]]
        key "wafPolicy": ForwardRef('ResourceReference', module='types')
        associations: list[SecurityPolicyWebApplicationFirewallAssociation]
        type: Literal[SecurityPolicyType.WEB_APPLICATION_FIREWALL]
        waf_policy: ResourceReference


    class azure.mgmt.cdn.types.SecurityPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        WEB_APPLICATION_FIREWALL = "WebApplicationFirewall"


    class azure.mgmt.cdn.types.SecurityPolicyUpdateParameters(TypedDict, total=False):
        key "properties": ForwardRef('SecurityPolicyUpdateProperties', module='types')
        properties: SecurityPolicyUpdateProperties


    class azure.mgmt.cdn.types.SecurityPolicyUpdateProperties(TypedDict, total=False):
        key "parameters": ForwardRef('SecurityPolicyPropertiesParameters', module='types')
        parameters: SecurityPolicyPropertiesParameters


    class azure.mgmt.cdn.types.SecurityPolicyWebApplicationFirewallAssociation(TypedDict, total=False):
        domains: list[ActivatedResourceReference]
        patternsToMatch: list[str]
        patterns_to_match: list[str]


    class azure.mgmt.cdn.types.SecurityPolicyWebApplicationFirewallParameters(TypedDict, total=False):
        key "type": Required[Literal[SecurityPolicyType.WEB_APPLICATION_FIREWALL]]
        key "wafPolicy": ForwardRef('ResourceReference', module='types')
        associations: list[SecurityPolicyWebApplicationFirewallAssociation]
        type: Literal[SecurityPolicyType.WEB_APPLICATION_FIREWALL]
        waf_policy: ResourceReference


    class azure.mgmt.cdn.types.ServerPortMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, ServerPortOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, ServerPortOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SERVER_PORT_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.SharedPrivateLinkResourceProperties(TypedDict, total=False):
        key "groupId": str
        key "privateLink": ForwardRef('ResourceReference', module='types')
        key "privateLinkLocation": str
        key "requestMessage": str
        key "status": Union[str, SharedPrivateLinkResourceStatus]
        group_id: str
        private_link: ResourceReference
        private_link_location: str
        request_message: str
        status: Union[str, SharedPrivateLinkResourceStatus]


    class azure.mgmt.cdn.types.Sku(TypedDict, total=False):
        key "name": Union[str, SkuName]
        name: Union[str, SkuName]


    class azure.mgmt.cdn.types.SocketAddrMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, SocketAddrOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, SocketAddrOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SOCKET_ADDR_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.SslProtocolMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, SslProtocolOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS]]
        matchValues: list[Union[str, SslProtocol]]
        match_values: list[Union[str, SslProtocol]]
        negate_condition: bool
        operator: Union[str, SslProtocolOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_SSL_PROTOCOL_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.cdn.types.TrackedResource(Resource):
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


    class azure.mgmt.cdn.types.UrlFileExtensionMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, UrlFileExtensionOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlFileExtensionOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILE_EXTENSION_MATCH_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlFileNameMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, UrlFileNameOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlFileNameOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_FILENAME_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlPathMatchConditionParameters(TypedDict, total=False):
        key "negateCondition": bool
        key "operator": Required[Union[str, UrlPathOperator]]
        key "typeName": Required[Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS]]
        matchValues: list[str]
        match_values: list[str]
        negate_condition: bool
        operator: Union[str, UrlPathOperator]
        transforms: list[Union[str, Transform]]
        type_name: Literal[DeliveryRuleConditionParametersType.DELIVERY_RULE_URL_PATH_MATCH_CONDITION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlRedirectAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.URL_REDIRECT]]
        key "parameters": Required[UrlRedirectActionParameters]
        name: Literal[DeliveryRuleActionEnum.URL_REDIRECT]
        parameters: UrlRedirectActionParameters


    class azure.mgmt.cdn.types.UrlRedirectActionParameters(TypedDict, total=False):
        key "customFragment": str
        key "customHostname": str
        key "customPath": str
        key "customQueryString": str
        key "destinationProtocol": Union[str, DestinationProtocol]
        key "redirectType": Required[Union[str, RedirectType]]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS]]
        custom_fragment: str
        custom_hostname: str
        custom_path: str
        custom_query_string: str
        destination_protocol: Union[str, DestinationProtocol]
        redirect_type: Union[str, RedirectType]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REDIRECT_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlRewriteAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.URL_REWRITE]]
        key "parameters": Required[UrlRewriteActionParameters]
        name: Literal[DeliveryRuleActionEnum.URL_REWRITE]
        parameters: UrlRewriteActionParameters


    class azure.mgmt.cdn.types.UrlRewriteActionParameters(TypedDict, total=False):
        key "destination": Required[str]
        key "preserveUnmatchedPath": bool
        key "sourcePattern": Required[str]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS]]
        destination: str
        preserve_unmatched_path: bool
        source_pattern: str
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_REWRITE_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlSigningAction(TypedDict, total=False):
        key "name": Required[Literal[DeliveryRuleActionEnum.URL_SIGNING]]
        key "parameters": Required[UrlSigningActionParameters]
        name: Literal[DeliveryRuleActionEnum.URL_SIGNING]
        parameters: UrlSigningActionParameters


    class azure.mgmt.cdn.types.UrlSigningActionParameters(TypedDict, total=False):
        key "algorithm": Union[str, Algorithm]
        key "typeName": Required[Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS]]
        algorithm: Union[str, Algorithm]
        parameterNameOverride: list[UrlSigningParamIdentifier]
        parameter_name_override: list[UrlSigningParamIdentifier]
        type_name: Literal[DeliveryRuleActionParametersType.DELIVERY_RULE_URL_SIGNING_ACTION_PARAMETERS]


    class azure.mgmt.cdn.types.UrlSigningKey(TypedDict, total=False):
        key "keyId": Required[str]
        key "keySourceParameters": Required[KeyVaultSigningKeyParameters]
        key_id: str
        key_source_parameters: KeyVaultSigningKeyParameters


    class azure.mgmt.cdn.types.UrlSigningKeyParameters(TypedDict, total=False):
        key "keyId": Required[str]
        key "secretSource": Required[ResourceReference]
        key "secretVersion": Required[str]
        key "type": Required[Literal[SecretType.URL_SIGNING_KEY]]
        key_id: str
        secret_source: ResourceReference
        secret_version: str
        type: Literal[SecretType.URL_SIGNING_KEY]


    class azure.mgmt.cdn.types.UrlSigningParamIdentifier(TypedDict, total=False):
        key "paramIndicator": Required[Union[str, ParamIndicator]]
        key "paramName": Required[str]
        param_indicator: Union[str, ParamIndicator]
        param_name: str


    class azure.mgmt.cdn.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.cdn.types.UserManagedHttpsParameters(TypedDict, total=False):
        key "certificateSource": Required[Literal[CertificateSource.AZURE_KEY_VAULT]]
        key "certificateSourceParameters": Required[KeyVaultCertificateSourceParameters]
        key "minimumTlsVersion": Union[str, MinimumTlsVersion]
        key "protocolType": Required[Union[str, ProtocolType]]
        certificate_source: Literal[CertificateSource.AZURE_KEY_VAULT]
        certificate_source_parameters: KeyVaultCertificateSourceParameters
        minimum_tls_version: Union[str, MinimumTlsVersion]
        protocol_type: Union[str, ProtocolType]


    class azure.mgmt.cdn.types.ValidateCustomDomainInput(TypedDict, total=False):
        key "hostName": Required[str]
        host_name: str


    class azure.mgmt.cdn.types.ValidateProbeInput(TypedDict, total=False):
        key "probeURL": Required[str]
        probe_url: str


    class azure.mgmt.cdn.types.ValidateSecretInput(TypedDict, total=False):
        key "secretSource": Required[ResourceReference]
        key "secretType": Required[Union[str, SecretType]]
        key "secretVersion": str
        secret_source: ResourceReference
        secret_type: Union[str, SecretType]
        secret_version: str


```