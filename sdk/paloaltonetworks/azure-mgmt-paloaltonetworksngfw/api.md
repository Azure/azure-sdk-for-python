```py
namespace azure.mgmt.paloaltonetworksngfw

    class azure.mgmt.paloaltonetworksngfw.PaloAltoNetworksNgfwMgmtClient: implements ContextManager 
        certificate_object_global_rulestack: CertificateObjectGlobalRulestackOperations
        certificate_object_local_rulestack: CertificateObjectLocalRulestackOperations
        custom_capture_configurations_firewall_resources: CustomCaptureConfigurationsFirewallResourcesOperations
        firewall_status: FirewallStatusOperations
        firewalls: FirewallsOperations
        fqdn_list_global_rulestack: FqdnListGlobalRulestackOperations
        fqdn_list_local_rulestack: FqdnListLocalRulestackOperations
        global_rulestack: GlobalRulestackOperations
        local_rules: LocalRulesOperations
        local_rulestacks: LocalRulestacksOperations
        metrics_object_firewall: MetricsObjectFirewallOperations
        operations: Operations
        palo_alto_networks_cloudngfw_operations: PaloAltoNetworksCloudngfwOperationsOperations
        post_rules: PostRulesOperations
        pre_rules: PreRulesOperations
        prefix_list_global_rulestack: PrefixListGlobalRulestackOperations
        prefix_list_local_rulestack: PrefixListLocalRulestackOperations

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


namespace azure.mgmt.paloaltonetworksngfw.aio

    class azure.mgmt.paloaltonetworksngfw.aio.PaloAltoNetworksNgfwMgmtClient: implements AsyncContextManager 
        certificate_object_global_rulestack: CertificateObjectGlobalRulestackOperations
        certificate_object_local_rulestack: CertificateObjectLocalRulestackOperations
        custom_capture_configurations_firewall_resources: CustomCaptureConfigurationsFirewallResourcesOperations
        firewall_status: FirewallStatusOperations
        firewalls: FirewallsOperations
        fqdn_list_global_rulestack: FqdnListGlobalRulestackOperations
        fqdn_list_local_rulestack: FqdnListLocalRulestackOperations
        global_rulestack: GlobalRulestackOperations
        local_rules: LocalRulesOperations
        local_rulestacks: LocalRulestacksOperations
        metrics_object_firewall: MetricsObjectFirewallOperations
        operations: Operations
        palo_alto_networks_cloudngfw_operations: PaloAltoNetworksCloudngfwOperationsOperations
        post_rules: PostRulesOperations
        pre_rules: PreRulesOperations
        prefix_list_global_rulestack: PrefixListGlobalRulestackOperations
        prefix_list_local_rulestack: PrefixListLocalRulestackOperations

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


namespace azure.mgmt.paloaltonetworksngfw.aio.operations

    class azure.mgmt.paloaltonetworksngfw.aio.operations.CertificateObjectGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectGlobalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CertificateObjectGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateObjectGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.CertificateObjectLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectLocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectLocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateObjectLocalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CertificateObjectLocalRulestackResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateObjectLocalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.CustomCaptureConfigurationsFirewallResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: CustomCaptureConfigurationsFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: CustomCaptureConfigurationsFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name']}, api_versions_list=['2026-05-11-preview'])
        async def delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name', 'accept']}, api_versions_list=['2026-05-11-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name', 'accept']}, api_versions_list=['2026-05-11-preview'])
        def list_by_firewall(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomCaptureConfigurationsFirewallResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.FirewallStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> FirewallStatusResource: ...

        @distributed_trace
        def list_by_firewalls(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallStatusResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.FirewallsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: FirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: FirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FirewallResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> FirewallResource: ...

        @distributed_trace_async
        async def get_global_rulestack(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> GlobalRulestackInfo: ...

        @distributed_trace_async
        async def get_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> LogSettings: ...

        @distributed_trace_async
        async def get_support_info(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                *, 
                email: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FirewallResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FirewallResource]: ...

        @overload
        async def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[LogSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[LogSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: FirewallResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: FirewallResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.FqdnListGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: FqdnListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: FqdnListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListGlobalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FqdnListGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FqdnListGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.FqdnListLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: FqdnListLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListLocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: FqdnListLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListLocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FqdnListLocalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FqdnListLocalRulestackResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FqdnListLocalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.GlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: GlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: GlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @distributed_trace_async
        async def get_change_log(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> Changelog: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[GlobalRulestackResource]: ...

        @distributed_trace_async
        async def list_advanced_security_objects(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace_async
        async def list_app_ids(
                self, 
                global_rulestack_name: str, 
                *, 
                app_id_version: Optional[str] = ..., 
                app_prefix: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ListAppIdResponse: ...

        @distributed_trace_async
        async def list_countries(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> CountriesResponse: ...

        @distributed_trace_async
        async def list_firewalls(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ListFirewallsResponse: ...

        @distributed_trace_async
        async def list_predefined_url_categories(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PredefinedUrlCategoriesResponse: ...

        @distributed_trace_async
        async def list_security_services(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, SecurityServicesTypeEnum], 
                **kwargs: Any
            ) -> SecurityServicesResponse: ...

        @distributed_trace_async
        async def revert(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                global_rulestack_name: str, 
                properties: GlobalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @overload
        async def update(
                self, 
                global_rulestack_name: str, 
                properties: GlobalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @overload
        async def update(
                self, 
                global_rulestack_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.LocalRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: LocalRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: LocalRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulesResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> LocalRulesResource: ...

        @distributed_trace_async
        async def get_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocalRulesResource]: ...

        @distributed_trace_async
        async def refresh_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.LocalRulestacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def begin_commit(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: LocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: LocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[LocalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @distributed_trace_async
        async def get_change_log(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> Changelog: ...

        @distributed_trace_async
        async def get_support_info(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                email: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace_async
        async def list_advanced_security_objects(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                app_id_version: Optional[str] = ..., 
                app_prefix: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[str]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[LocalRulestackResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[LocalRulestackResource]: ...

        @distributed_trace
        def list_countries(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Country]: ...

        @distributed_trace_async
        async def list_firewalls(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ListFirewallsResponse: ...

        @distributed_trace
        def list_predefined_url_categories(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[PredefinedUrlCategory]: ...

        @distributed_trace_async
        async def list_security_services(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, SecurityServicesTypeEnum], 
                **kwargs: Any
            ) -> SecurityServicesResponse: ...

        @distributed_trace_async
        async def revert(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: LocalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: LocalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.MetricsObjectFirewallOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: MetricsObjectFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MetricsObjectFirewallResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: MetricsObjectFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MetricsObjectFirewallResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MetricsObjectFirewallResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> MetricsObjectFirewallResource: ...

        @distributed_trace
        def list_by_firewalls(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MetricsObjectFirewallResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.PaloAltoNetworksCloudngfwOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create_product_serial_number(self, **kwargs: Any) -> ProductSerialNumberRequestStatus: ...

        @distributed_trace_async
        async def list_cloud_manager_tenants(self, **kwargs: Any) -> CloudManagerTenantList: ...

        @distributed_trace_async
        async def list_product_serial_number_status(self, **kwargs: Any) -> Optional[ProductSerialNumberStatus]: ...

        @distributed_trace_async
        async def list_support_info(self, **kwargs: Any) -> SupportInfoModel: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.PostRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PostRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PostRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PostRulesResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> PostRulesResource: ...

        @distributed_trace_async
        async def get_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PostRulesResource]: ...

        @distributed_trace_async
        async def refresh_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.PreRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PreRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PreRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreRulesResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreRulesResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> PreRulesResource: ...

        @distributed_trace_async
        async def get_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PreRulesResource]: ...

        @distributed_trace_async
        async def refresh_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.PrefixListGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: PrefixListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: PrefixListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListGlobalRulestackResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListGlobalRulestackResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> PrefixListGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrefixListGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.aio.operations.PrefixListLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: PrefixListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: PrefixListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrefixListResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> PrefixListResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrefixListResource]: ...


namespace azure.mgmt.paloaltonetworksngfw.models

    class azure.mgmt.paloaltonetworksngfw.models.ActionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DENY_RESET_BOTH = "DenyResetBoth"
        DENY_RESET_SERVER = "DenyResetServer"
        DENY_SILENT = "DenySilent"


    class azure.mgmt.paloaltonetworksngfw.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectListResponse(_Model):
        next_link: Optional[str]
        value: AdvSecurityObjectModel

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: AdvSecurityObjectModel
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectModel(_Model):
        entry: list[NameDescriptionObject]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                entry: list[NameDescriptionObject], 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEEDS = "feeds"
        URL_CUSTOM = "urlCustom"


    class azure.mgmt.paloaltonetworksngfw.models.AppSeenData(_Model):
        app_seen_list: list[AppSeenInfo]
        count: int

        @overload
        def __init__(
                self, 
                *, 
                app_seen_list: list[AppSeenInfo], 
                count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.AppSeenInfo(_Model):
        category: str
        risk: str
        standard_ports: str
        sub_category: str
        tag: str
        technology: str
        title: str

        @overload
        def __init__(
                self, 
                *, 
                category: str, 
                risk: str, 
                standard_ports: str, 
                sub_category: str, 
                tag: str, 
                technology: str, 
                title: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ApplicationInsights(_Model):
        id: Optional[str]
        key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.AzureResourceManagerManagedIdentityProperties(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedIdentityType]
        user_assigned_identities: Optional[dict[str, AzureResourceManagerUserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedIdentityType], 
                user_assigned_identities: Optional[dict[str, AzureResourceManagerUserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.AzureResourceManagerUserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.BillingCycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "MONTHLY"
        WEEKLY = "WEEKLY"


    class azure.mgmt.paloaltonetworksngfw.models.BooleanEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "FALSE"
        TRUE = "TRUE"


    class azure.mgmt.paloaltonetworksngfw.models.Category(_Model):
        feeds: list[str]
        url_custom: list[str]

        @overload
        def __init__(
                self, 
                *, 
                feeds: list[str], 
                url_custom: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObject(_Model):
        audit_comment: Optional[str]
        certificate_self_signed: Union[str, BooleanEnum]
        certificate_signer_resource_id: Optional[str]
        description: Optional[str]
        etag: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                certificate_self_signed: Union[str, BooleanEnum], 
                certificate_signer_resource_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectGlobalRulestackResource(ProxyResource):
        id: str
        name: str
        properties: CertificateObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: CertificateObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectLocalRulestackResource(ProxyResource):
        id: str
        name: str
        properties: CertificateObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: CertificateObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.Changelog(_Model):
        changes: list[str]
        last_committed: Optional[datetime]
        last_modified: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                changes: list[str], 
                last_committed: Optional[datetime] = ..., 
                last_modified: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CloudManagerTenantList(_Model):
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                value: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CountriesResponse(_Model):
        next_link: Optional[str]
        value: list[Country]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Country]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.Country(_Model):
        code: str
        description: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                code: str, 
                description: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsFilter(_Model):
        destination_ip_address: str
        destination_port: int
        protocol: Union[str, CustomCaptureConfigurationsProtocol]
        source_ip_address: str
        source_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                destination_ip_address: str, 
                destination_port: int, 
                protocol: Union[str, CustomCaptureConfigurationsProtocol], 
                source_ip_address: str, 
                source_port: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsFirewallResource(ProxyResource):
        id: str
        name: str
        properties: CustomCaptureConfigurationsProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: CustomCaptureConfigurationsProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsProperties(_Model):
        duration_in_sec: Optional[int]
        message: Optional[str]
        next_check_in_seconds: Optional[int]
        pcap_detail_reason: Optional[str]
        pcap_filter: Optional[list[CustomCaptureConfigurationsFilter]]
        pcap_stages: Optional[list[Union[str, CustomCaptureConfigurationsStage]]]
        pcap_status: Optional[Union[str, CustomCaptureConfigurationsStatus]]
        storage_account_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                duration_in_sec: Optional[int] = ..., 
                pcap_filter: Optional[list[CustomCaptureConfigurationsFilter]] = ..., 
                pcap_stages: Optional[list[Union[str, CustomCaptureConfigurationsStage]]] = ..., 
                storage_account_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsProtocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DROP = "Drop"
        FIREWALL = "Firewall"
        RECEIVE = "Receive"
        TRANSMIT = "Transmit"


    class azure.mgmt.paloaltonetworksngfw.models.CustomCaptureConfigurationsStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCESS = "Success"


    class azure.mgmt.paloaltonetworksngfw.models.DNSProxy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.DNSSettings(_Model):
        dns_servers: Optional[list[IPAddress]]
        enable_dns_proxy: Optional[Union[str, DNSProxy]]
        enabled_dns_type: Optional[Union[str, EnabledDNSType]]

        @overload
        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[IPAddress]] = ..., 
                enable_dns_proxy: Optional[Union[str, DNSProxy]] = ..., 
                enabled_dns_type: Optional[Union[str, EnabledDNSType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.DecryptionRuleTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SSL_INBOUND_INSPECTION = "SSLInboundInspection"
        SSL_OUTBOUND_INSPECTION = "SSLOutboundInspection"


    class azure.mgmt.paloaltonetworksngfw.models.DefaultMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIREWALL = "FIREWALL"
        IPS = "IPS"
        NONE = "NONE"


    class azure.mgmt.paloaltonetworksngfw.models.DestinationAddr(_Model):
        cidrs: Optional[list[str]]
        countries: Optional[list[str]]
        feeds: Optional[list[str]]
        fqdn_lists: Optional[list[str]]
        prefix_lists: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                cidrs: Optional[list[str]] = ..., 
                countries: Optional[list[str]] = ..., 
                feeds: Optional[list[str]] = ..., 
                fqdn_lists: Optional[list[str]] = ..., 
                prefix_lists: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.EgressNat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.EnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.paloaltonetworksngfw.models.EnabledDNSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "AZURE"
        CUSTOM = "CUSTOM"


    class azure.mgmt.paloaltonetworksngfw.models.EndpointConfiguration(_Model):
        address: IPAddress
        port: str

        @overload
        def __init__(
                self, 
                *, 
                address: IPAddress, 
                port: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.paloaltonetworksngfw.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.paloaltonetworksngfw.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.EventHub(_Model):
        id: Optional[str]
        name: Optional[str]
        name_space: Optional[str]
        policy_name: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_space: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallDeploymentProperties(_Model):
        associated_rulestack: Optional[RulestackDetails]
        dns_settings: DNSSettings
        firewall_sku: Optional[str]
        front_end_settings: Optional[list[FrontendSetting]]
        is_panorama_managed: Optional[Union[str, BooleanEnum]]
        is_strata_cloud_managed: Optional[Union[str, BooleanEnum]]
        marketplace_details: MarketplaceDetails
        network_profile: NetworkProfile
        pan_etag: Optional[str]
        panorama_config: Optional[PanoramaConfig]
        plan_data: PlanData
        provisioning_state: Optional[Union[str, ProvisioningState]]
        strata_cloud_manager_config: Optional[StrataCloudManagerConfig]

        @overload
        def __init__(
                self, 
                *, 
                associated_rulestack: Optional[RulestackDetails] = ..., 
                dns_settings: DNSSettings, 
                firewall_sku: Optional[str] = ..., 
                front_end_settings: Optional[list[FrontendSetting]] = ..., 
                is_panorama_managed: Optional[Union[str, BooleanEnum]] = ..., 
                is_strata_cloud_managed: Optional[Union[str, BooleanEnum]] = ..., 
                marketplace_details: MarketplaceDetails, 
                network_profile: NetworkProfile, 
                pan_etag: Optional[str] = ..., 
                panorama_config: Optional[PanoramaConfig] = ..., 
                plan_data: PlanData, 
                strata_cloud_manager_config: Optional[StrataCloudManagerConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResource(TrackedResource):
        id: str
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        location: str
        name: str
        properties: FirewallDeploymentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: str, 
                properties: FirewallDeploymentProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResourceUpdate(_Model):
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        properties: Optional[FirewallResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                properties: Optional[FirewallResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResourceUpdateProperties(_Model):
        associated_rulestack: Optional[RulestackDetails]
        dns_settings: Optional[DNSSettings]
        front_end_settings: Optional[list[FrontendSetting]]
        is_panorama_managed: Optional[Union[str, BooleanEnum]]
        is_strata_cloud_managed: Optional[Union[str, BooleanEnum]]
        marketplace_details: Optional[MarketplaceDetails]
        network_profile: Optional[NetworkProfile]
        pan_etag: Optional[str]
        panorama_config: Optional[PanoramaConfig]
        plan_data: Optional[PlanData]
        strata_cloud_manager_config: Optional[StrataCloudManagerConfig]

        @overload
        def __init__(
                self, 
                *, 
                associated_rulestack: Optional[RulestackDetails] = ..., 
                dns_settings: Optional[DNSSettings] = ..., 
                front_end_settings: Optional[list[FrontendSetting]] = ..., 
                is_panorama_managed: Optional[Union[str, BooleanEnum]] = ..., 
                is_strata_cloud_managed: Optional[Union[str, BooleanEnum]] = ..., 
                marketplace_details: Optional[MarketplaceDetails] = ..., 
                network_profile: Optional[NetworkProfile] = ..., 
                pan_etag: Optional[str] = ..., 
                panorama_config: Optional[PanoramaConfig] = ..., 
                plan_data: Optional[PlanData] = ..., 
                strata_cloud_manager_config: Optional[StrataCloudManagerConfig] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallStatusProperty(_Model):
        health_reason: Optional[str]
        health_status: Optional[Union[str, HealthStatus]]
        is_panorama_managed: Optional[Union[str, BooleanEnum]]
        is_strata_cloud_managed: Optional[Union[str, BooleanEnum]]
        panorama_status: Optional[PanoramaStatus]
        provisioning_state: Optional[Union[str, ReadOnlyProvisioningState]]
        strata_cloud_manager_info: Optional[StrataCloudManagerInfo]

        @overload
        def __init__(
                self, 
                *, 
                strata_cloud_manager_info: Optional[StrataCloudManagerInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallStatusResource(ProxyResource):
        id: str
        name: str
        properties: FirewallStatusProperty
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FirewallStatusProperty
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListGlobalRulestackResource(ProxyResource):
        id: str
        name: str
        properties: FqdnObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FqdnObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListLocalRulestackResource(ProxyResource):
        id: str
        name: str
        properties: FqdnObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: FqdnObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnObject(_Model):
        audit_comment: Optional[str]
        description: Optional[str]
        etag: Optional[str]
        fqdn_list: list[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                fqdn_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.FrontendSetting(_Model):
        backend_configuration: EndpointConfiguration
        frontend_configuration: EndpointConfiguration
        name: str
        protocol: Union[str, ProtocolType]

        @overload
        def __init__(
                self, 
                *, 
                backend_configuration: EndpointConfiguration, 
                frontend_configuration: EndpointConfiguration, 
                name: str, 
                protocol: Union[str, ProtocolType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackInfo(_Model):
        azure_id: str

        @overload
        def __init__(
                self, 
                *, 
                azure_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResource(ProxyResource):
        id: str
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        location: str
        name: str
        properties: RulestackProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: str, 
                properties: RulestackProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResourceUpdate(_Model):
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        location: Optional[str]
        properties: Optional[GlobalRulestackResourceUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GlobalRulestackResourceUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResourceUpdateProperties(_Model):
        associated_subscriptions: Optional[list[str]]
        default_mode: Optional[Union[str, DefaultMode]]
        description: Optional[str]
        min_app_id_version: Optional[str]
        pan_etag: Optional[str]
        pan_location: Optional[str]
        scope: Optional[Union[str, ScopeType]]
        security_services: Optional[SecurityServices]

        @overload
        def __init__(
                self, 
                *, 
                associated_subscriptions: Optional[list[str]] = ..., 
                default_mode: Optional[Union[str, DefaultMode]] = ..., 
                description: Optional[str] = ..., 
                min_app_id_version: Optional[str] = ..., 
                pan_etag: Optional[str] = ..., 
                pan_location: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                security_services: Optional[SecurityServices] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GREEN = "GREEN"
        INITIALIZING = "INITIALIZING"
        RED = "RED"
        YELLOW = "YELLOW"


    class azure.mgmt.paloaltonetworksngfw.models.IPAddress(_Model):
        address: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.IPAddressSpace(_Model):
        address_space: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address_space: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ListAppIdResponse(_Model):
        next_link: Optional[str]
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ListFirewallsResponse(_Model):
        next_link: Optional[str]
        value: list[str]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulesResource(ProxyResource):
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RuleEntry
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResource(TrackedResource):
        id: str
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        location: str
        name: str
        properties: RulestackProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: str, 
                properties: RulestackProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResourceUpdate(_Model):
        identity: Optional[AzureResourceManagerManagedIdentityProperties]
        properties: Optional[LocalRulestackResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                properties: Optional[LocalRulestackResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResourceUpdateProperties(_Model):
        associated_subscriptions: Optional[list[str]]
        default_mode: Optional[Union[str, DefaultMode]]
        description: Optional[str]
        min_app_id_version: Optional[str]
        pan_etag: Optional[str]
        pan_location: Optional[str]
        scope: Optional[Union[str, ScopeType]]
        security_services: Optional[SecurityServices]

        @overload
        def __init__(
                self, 
                *, 
                associated_subscriptions: Optional[list[str]] = ..., 
                default_mode: Optional[Union[str, DefaultMode]] = ..., 
                description: Optional[str] = ..., 
                min_app_id_version: Optional[str] = ..., 
                pan_etag: Optional[str] = ..., 
                pan_location: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                security_services: Optional[SecurityServices] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LogDestination(_Model):
        event_hub_configurations: Optional[EventHub]
        monitor_configurations: Optional[MonitorLog]
        storage_configurations: Optional[StorageAccount]

        @overload
        def __init__(
                self, 
                *, 
                event_hub_configurations: Optional[EventHub] = ..., 
                monitor_configurations: Optional[MonitorLog] = ..., 
                storage_configurations: Optional[StorageAccount] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LogOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDIVIDUAL_DESTINATION = "INDIVIDUAL_DESTINATION"
        SAME_DESTINATION = "SAME_DESTINATION"


    class azure.mgmt.paloaltonetworksngfw.models.LogSettings(_Model):
        application_insights: Optional[ApplicationInsights]
        common_destination: Optional[LogDestination]
        decrypt_log_destination: Optional[LogDestination]
        log_option: Optional[Union[str, LogOption]]
        log_type: Optional[Union[str, LogType]]
        threat_log_destination: Optional[LogDestination]
        traffic_log_destination: Optional[LogDestination]

        @overload
        def __init__(
                self, 
                *, 
                application_insights: Optional[ApplicationInsights] = ..., 
                common_destination: Optional[LogDestination] = ..., 
                decrypt_log_destination: Optional[LogDestination] = ..., 
                log_option: Optional[Union[str, LogOption]] = ..., 
                log_type: Optional[Union[str, LogType]] = ..., 
                threat_log_destination: Optional[LogDestination] = ..., 
                traffic_log_destination: Optional[LogDestination] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.LogType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "AUDIT"
        DECRYPTION = "DECRYPTION"
        DLP = "DLP"
        THREAT = "THREAT"
        TRAFFIC = "TRAFFIC"
        WILDFIRE = "WILDFIRE"


    class azure.mgmt.paloaltonetworksngfw.models.ManagedIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_AND_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.paloaltonetworksngfw.models.MarketplaceDetails(_Model):
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        offer_id: str
        publisher_id: str

        @overload
        def __init__(
                self, 
                *, 
                marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]] = ..., 
                offer_id: str, 
                publisher_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULFILLMENT_REQUESTED = "FulfillmentRequested"
        NOT_STARTED = "NotStarted"
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.paloaltonetworksngfw.models.MetricsObject(_Model):
        application_insights_connection_string: str
        application_insights_resource_id: str
        pan_etag: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                application_insights_connection_string: str, 
                application_insights_resource_id: str, 
                pan_etag: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.MetricsObjectFirewallResource(ProxyResource):
        id: str
        name: str
        properties: MetricsObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: MetricsObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.MonitorLog(_Model):
        id: Optional[str]
        primary_key: Optional[str]
        secondary_key: Optional[str]
        subscription_id: Optional[str]
        workspace: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                workspace: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.NameDescriptionObject(_Model):
        description: Optional[str]
        name: str

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.NetworkProfile(_Model):
        egress_nat_ip: Optional[list[IPAddress]]
        enable_egress_nat: Union[str, EgressNat]
        network_type: Union[str, NetworkType]
        private_source_nat_rules_destination: Optional[list[str]]
        public_ips: list[IPAddress]
        trusted_ranges: Optional[list[str]]
        vnet_configuration: Optional[VnetConfiguration]
        vwan_configuration: Optional[VwanConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                egress_nat_ip: Optional[list[IPAddress]] = ..., 
                enable_egress_nat: Union[str, EgressNat], 
                network_type: Union[str, NetworkType], 
                private_source_nat_rules_destination: Optional[list[str]] = ..., 
                public_ips: list[IPAddress], 
                trusted_ranges: Optional[list[str]] = ..., 
                vnet_configuration: Optional[VnetConfiguration] = ..., 
                vwan_configuration: Optional[VwanConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.NetworkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VNET = "VNET"
        VWAN = "VWAN"


    class azure.mgmt.paloaltonetworksngfw.models.Operation(_Model):
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


    class azure.mgmt.paloaltonetworksngfw.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.paloaltonetworksngfw.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.paloaltonetworksngfw.models.PanoramaConfig(_Model):
        cg_name: Optional[str]
        config_string: str
        dg_name: Optional[str]
        host_name: Optional[str]
        panorama_server: Optional[str]
        panorama_server2: Optional[str]
        tpl_name: Optional[str]
        vm_auth_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                config_string: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PanoramaStatus(_Model):
        panorama_server2_status: Optional[Union[str, ServerStatus]]
        panorama_server_status: Optional[Union[str, ServerStatus]]


    class azure.mgmt.paloaltonetworksngfw.models.PlanData(_Model):
        billing_cycle: Union[str, BillingCycle]
        effective_date: Optional[datetime]
        plan_id: str
        usage_type: Optional[Union[str, UsageType]]

        @overload
        def __init__(
                self, 
                *, 
                billing_cycle: Union[str, BillingCycle], 
                plan_id: str, 
                usage_type: Optional[Union[str, UsageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PostRulesResource(ProxyResource):
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RuleEntry
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PreRulesResource(ProxyResource):
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: RuleEntry
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PredefinedUrlCategoriesResponse(_Model):
        next_link: Optional[str]
        value: list[PredefinedUrlCategory]

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PredefinedUrlCategory]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PredefinedUrlCategory(_Model):
        action: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                action: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListGlobalRulestackResource(ProxyResource):
        id: str
        name: str
        properties: PrefixObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PrefixObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListResource(ProxyResource):
        id: str
        name: str
        properties: PrefixObject
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PrefixObject
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixObject(_Model):
        audit_comment: Optional[str]
        description: Optional[str]
        etag: Optional[str]
        prefix_list: list[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                prefix_list: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ProductSerialNumberRequestStatus(_Model):
        status: str

        @overload
        def __init__(
                self, 
                *, 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ProductSerialNumberStatus(_Model):
        serial_number: Optional[str]
        status: Union[str, ProductSerialStatusValues]

        @overload
        def __init__(
                self, 
                *, 
                serial_number: Optional[str] = ..., 
                status: Union[str, ProductSerialStatusValues]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ProductSerialStatusValues(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOCATED = "Allocated"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.paloaltonetworksngfw.models.ProtocolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TCP = "TCP"
        UDP = "UDP"


    class azure.mgmt.paloaltonetworksngfw.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.paloaltonetworksngfw.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.models.ReadOnlyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.paloaltonetworksngfw.models.RegistrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REGISTERED = "Not Registered"
        REGISTERED = "Registered"


    class azure.mgmt.paloaltonetworksngfw.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.paloaltonetworksngfw.models.RuleCounter(_Model):
        app_seen: Optional[AppSeenData]
        firewall_name: Optional[str]
        hit_count: Optional[int]
        last_updated_timestamp: Optional[datetime]
        priority: str
        request_timestamp: Optional[datetime]
        rule_list_name: Optional[str]
        rule_name: str
        rule_stack_name: Optional[str]
        timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                app_seen: Optional[AppSeenData] = ..., 
                firewall_name: Optional[str] = ..., 
                hit_count: Optional[int] = ..., 
                last_updated_timestamp: Optional[datetime] = ..., 
                priority: str, 
                request_timestamp: Optional[datetime] = ..., 
                rule_list_name: Optional[str] = ..., 
                rule_name: str, 
                rule_stack_name: Optional[str] = ..., 
                timestamp: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.RuleCounterReset(_Model):
        firewall_name: Optional[str]
        priority: Optional[str]
        rule_list_name: Optional[str]
        rule_name: Optional[str]
        rule_stack_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                firewall_name: Optional[str] = ..., 
                rule_list_name: Optional[str] = ..., 
                rule_name: Optional[str] = ..., 
                rule_stack_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.RuleEntry(_Model):
        action_type: Optional[Union[str, ActionEnum]]
        applications: Optional[list[str]]
        audit_comment: Optional[str]
        category: Optional[Category]
        decryption_rule_type: Optional[Union[str, DecryptionRuleTypeEnum]]
        description: Optional[str]
        destination: Optional[DestinationAddr]
        enable_logging: Optional[Union[str, StateEnum]]
        etag: Optional[str]
        inbound_inspection_certificate: Optional[str]
        negate_destination: Optional[Union[str, BooleanEnum]]
        negate_source: Optional[Union[str, BooleanEnum]]
        priority: Optional[int]
        protocol: Optional[str]
        protocol_port_list: Optional[list[str]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        rule_name: str
        rule_state: Optional[Union[str, StateEnum]]
        source: Optional[SourceAddr]
        tags: Optional[list[TagInfo]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, ActionEnum]] = ..., 
                applications: Optional[list[str]] = ..., 
                audit_comment: Optional[str] = ..., 
                category: Optional[Category] = ..., 
                decryption_rule_type: Optional[Union[str, DecryptionRuleTypeEnum]] = ..., 
                description: Optional[str] = ..., 
                destination: Optional[DestinationAddr] = ..., 
                enable_logging: Optional[Union[str, StateEnum]] = ..., 
                etag: Optional[str] = ..., 
                inbound_inspection_certificate: Optional[str] = ..., 
                negate_destination: Optional[Union[str, BooleanEnum]] = ..., 
                negate_source: Optional[Union[str, BooleanEnum]] = ..., 
                protocol: Optional[str] = ..., 
                protocol_port_list: Optional[list[str]] = ..., 
                rule_name: str, 
                rule_state: Optional[Union[str, StateEnum]] = ..., 
                source: Optional[SourceAddr] = ..., 
                tags: Optional[list[TagInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.RulestackDetails(_Model):
        location: Optional[str]
        resource_id: Optional[str]
        rulestack_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                rulestack_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.RulestackProperties(_Model):
        associated_subscriptions: Optional[list[str]]
        default_mode: Optional[Union[str, DefaultMode]]
        description: Optional[str]
        min_app_id_version: Optional[str]
        pan_etag: Optional[str]
        pan_location: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scope: Optional[Union[str, ScopeType]]
        security_services: Optional[SecurityServices]

        @overload
        def __init__(
                self, 
                *, 
                associated_subscriptions: Optional[list[str]] = ..., 
                default_mode: Optional[Union[str, DefaultMode]] = ..., 
                description: Optional[str] = ..., 
                min_app_id_version: Optional[str] = ..., 
                pan_etag: Optional[str] = ..., 
                pan_location: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                security_services: Optional[SecurityServices] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "GLOBAL"
        LOCAL = "LOCAL"


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServices(_Model):
        anti_spyware_profile: Optional[str]
        anti_virus_profile: Optional[str]
        dns_subscription: Optional[str]
        file_blocking_profile: Optional[str]
        outbound_trust_certificate: Optional[str]
        outbound_un_trust_certificate: Optional[str]
        url_filtering_profile: Optional[str]
        vulnerability_profile: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                anti_spyware_profile: Optional[str] = ..., 
                anti_virus_profile: Optional[str] = ..., 
                dns_subscription: Optional[str] = ..., 
                file_blocking_profile: Optional[str] = ..., 
                outbound_trust_certificate: Optional[str] = ..., 
                outbound_un_trust_certificate: Optional[str] = ..., 
                url_filtering_profile: Optional[str] = ..., 
                vulnerability_profile: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesResponse(_Model):
        next_link: Optional[str]
        value: SecurityServicesTypeList

        @overload
        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: SecurityServicesTypeList
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANTI_SPYWARE = "antiSpyware"
        ANTI_VIRUS = "antiVirus"
        DNS_SUBSCRIPTION = "dnsSubscription"
        FILE_BLOCKING = "fileBlocking"
        IPS_VULNERABILITY = "ipsVulnerability"
        URL_FILTERING = "urlFiltering"


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesTypeList(_Model):
        entry: list[NameDescriptionObject]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                entry: list[NameDescriptionObject], 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.ServerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "DOWN"
        UP = "UP"


    class azure.mgmt.paloaltonetworksngfw.models.SourceAddr(_Model):
        cidrs: Optional[list[str]]
        countries: Optional[list[str]]
        feeds: Optional[list[str]]
        prefix_lists: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                cidrs: Optional[list[str]] = ..., 
                countries: Optional[list[str]] = ..., 
                feeds: Optional[list[str]] = ..., 
                prefix_lists: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.StateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.StorageAccount(_Model):
        account_name: Optional[str]
        id: Optional[str]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.StrataCloudManagerConfig(_Model):
        cloud_manager_name: str

        @overload
        def __init__(
                self, 
                *, 
                cloud_manager_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.StrataCloudManagerInfo(_Model):
        folder_name: Optional[str]
        hub_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                folder_name: Optional[str] = ..., 
                hub_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.SupportInfo(_Model):
        account_id: Optional[str]
        account_registered: Optional[Union[str, BooleanEnum]]
        free_trial: Optional[Union[str, BooleanEnum]]
        free_trial_credit_left: Optional[int]
        free_trial_days_left: Optional[int]
        help_url: Optional[str]
        product_serial: Optional[str]
        product_sku: Optional[str]
        register_url: Optional[str]
        support_url: Optional[str]
        user_domain_supported: Optional[Union[str, BooleanEnum]]
        user_registered: Optional[Union[str, BooleanEnum]]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                account_registered: Optional[Union[str, BooleanEnum]] = ..., 
                free_trial: Optional[Union[str, BooleanEnum]] = ..., 
                free_trial_credit_left: Optional[int] = ..., 
                free_trial_days_left: Optional[int] = ..., 
                help_url: Optional[str] = ..., 
                product_serial: Optional[str] = ..., 
                product_sku: Optional[str] = ..., 
                register_url: Optional[str] = ..., 
                support_url: Optional[str] = ..., 
                user_domain_supported: Optional[Union[str, BooleanEnum]] = ..., 
                user_registered: Optional[Union[str, BooleanEnum]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.SupportInfoModel(_Model):
        account_id: Optional[str]
        account_registration_status: Optional[Union[str, RegistrationStatus]]
        credits: Optional[int]
        end_date_for_credits: Optional[str]
        free_trial: Optional[Union[str, EnableStatus]]
        free_trial_credit_left: Optional[int]
        free_trial_days_left: Optional[int]
        help_url: Optional[str]
        hub_url: Optional[str]
        monthly_credit_left: Optional[int]
        product_serial: Optional[str]
        product_sku: Optional[str]
        register_url: Optional[str]
        start_date_for_credits: Optional[str]
        support_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_id: Optional[str] = ..., 
                account_registration_status: Optional[Union[str, RegistrationStatus]] = ..., 
                credits: Optional[int] = ..., 
                end_date_for_credits: Optional[str] = ..., 
                free_trial: Optional[Union[str, EnableStatus]] = ..., 
                free_trial_credit_left: Optional[int] = ..., 
                free_trial_days_left: Optional[int] = ..., 
                help_url: Optional[str] = ..., 
                hub_url: Optional[str] = ..., 
                monthly_credit_left: Optional[int] = ..., 
                product_serial: Optional[str] = ..., 
                product_sku: Optional[str] = ..., 
                register_url: Optional[str] = ..., 
                start_date_for_credits: Optional[str] = ..., 
                support_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.SystemData(_Model):
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


    class azure.mgmt.paloaltonetworksngfw.models.TagInfo(_Model):
        key: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                key: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.TrackedResource(Resource):
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


    class azure.mgmt.paloaltonetworksngfw.models.UsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITTED = "COMMITTED"
        PAYG = "PAYG"


    class azure.mgmt.paloaltonetworksngfw.models.VnetConfiguration(_Model):
        ip_of_trust_subnet_for_udr: Optional[IPAddress]
        trust_subnet: IPAddressSpace
        un_trust_subnet: IPAddressSpace
        vnet: IPAddressSpace

        @overload
        def __init__(
                self, 
                *, 
                ip_of_trust_subnet_for_udr: Optional[IPAddress] = ..., 
                trust_subnet: IPAddressSpace, 
                un_trust_subnet: IPAddressSpace, 
                vnet: IPAddressSpace
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.paloaltonetworksngfw.models.VwanConfiguration(_Model):
        ip_of_trust_subnet_for_udr: Optional[IPAddress]
        network_virtual_appliance_id: Optional[str]
        trust_subnet: Optional[IPAddressSpace]
        un_trust_subnet: Optional[IPAddressSpace]
        v_hub: IPAddressSpace

        @overload
        def __init__(
                self, 
                *, 
                ip_of_trust_subnet_for_udr: Optional[IPAddress] = ..., 
                network_virtual_appliance_id: Optional[str] = ..., 
                trust_subnet: Optional[IPAddressSpace] = ..., 
                un_trust_subnet: Optional[IPAddressSpace] = ..., 
                v_hub: IPAddressSpace
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.paloaltonetworksngfw.operations

    class azure.mgmt.paloaltonetworksngfw.operations.CertificateObjectGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectGlobalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CertificateObjectGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificateObjectGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.CertificateObjectLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectLocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: CertificateObjectLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectLocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateObjectLocalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> CertificateObjectLocalRulestackResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificateObjectLocalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.CustomCaptureConfigurationsFirewallResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: CustomCaptureConfigurationsFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: CustomCaptureConfigurationsFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name']}, api_versions_list=['2026-05-11-preview'])
        def delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name', 'accept']}, api_versions_list=['2026-05-11-preview'])
        def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> CustomCaptureConfigurationsFirewallResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-05-11-preview', params_added_on={'2026-05-11-preview': ['api_version', 'subscription_id', 'resource_group_name', 'firewall_name', 'accept']}, api_versions_list=['2026-05-11-preview'])
        def list_by_firewall(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomCaptureConfigurationsFirewallResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.FirewallStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> FirewallStatusResource: ...

        @distributed_trace
        def list_by_firewalls(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallStatusResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.FirewallsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: FirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: FirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FirewallResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> FirewallResource: ...

        @distributed_trace
        def get_global_rulestack(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> GlobalRulestackInfo: ...

        @distributed_trace
        def get_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> LogSettings: ...

        @distributed_trace
        def get_support_info(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                *, 
                email: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FirewallResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FirewallResource]: ...

        @overload
        def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[LogSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[LogSettings] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def save_log_profile(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                log_settings: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: FirewallResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: FirewallResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FirewallResource: ...


    class azure.mgmt.paloaltonetworksngfw.operations.FqdnListGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: FqdnListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: FqdnListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListGlobalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FqdnListGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FqdnListGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.FqdnListLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: FqdnListLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListLocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: FqdnListLocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListLocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FqdnListLocalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FqdnListLocalRulestackResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FqdnListLocalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.GlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_commit(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: GlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: GlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @distributed_trace
        def get_change_log(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> Changelog: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[GlobalRulestackResource]: ...

        @distributed_trace
        def list_advanced_security_objects(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                global_rulestack_name: str, 
                *, 
                app_id_version: Optional[str] = ..., 
                app_prefix: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ListAppIdResponse: ...

        @distributed_trace
        def list_countries(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> CountriesResponse: ...

        @distributed_trace
        def list_firewalls(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ListFirewallsResponse: ...

        @distributed_trace
        def list_predefined_url_categories(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> PredefinedUrlCategoriesResponse: ...

        @distributed_trace
        def list_security_services(
                self, 
                global_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, SecurityServicesTypeEnum], 
                **kwargs: Any
            ) -> SecurityServicesResponse: ...

        @distributed_trace
        def revert(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                global_rulestack_name: str, 
                properties: GlobalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @overload
        def update(
                self, 
                global_rulestack_name: str, 
                properties: GlobalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...

        @overload
        def update(
                self, 
                global_rulestack_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GlobalRulestackResource: ...


    class azure.mgmt.paloaltonetworksngfw.operations.LocalRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: LocalRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: LocalRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulesResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> LocalRulesResource: ...

        @distributed_trace
        def get_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LocalRulesResource]: ...

        @distributed_trace
        def refresh_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.operations.LocalRulestacksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def begin_commit(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: LocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: LocalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[LocalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @distributed_trace
        def get_change_log(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> Changelog: ...

        @distributed_trace
        def get_support_info(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                email: Optional[str] = ..., 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace
        def list_advanced_security_objects(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                app_id_version: Optional[str] = ..., 
                app_prefix: Optional[str] = ..., 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[str]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[LocalRulestackResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[LocalRulestackResource]: ...

        @distributed_trace
        def list_countries(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Country]: ...

        @distributed_trace
        def list_firewalls(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ListFirewallsResponse: ...

        @distributed_trace
        def list_predefined_url_categories(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[PredefinedUrlCategory]: ...

        @distributed_trace
        def list_security_services(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                *, 
                skip: Optional[str] = ..., 
                top: Optional[int] = ..., 
                type: Union[str, SecurityServicesTypeEnum], 
                **kwargs: Any
            ) -> SecurityServicesResponse: ...

        @distributed_trace
        def revert(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> None: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: LocalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: LocalRulestackResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LocalRulestackResource: ...


    class azure.mgmt.paloaltonetworksngfw.operations.MetricsObjectFirewallOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: MetricsObjectFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MetricsObjectFirewallResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: MetricsObjectFirewallResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MetricsObjectFirewallResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MetricsObjectFirewallResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> MetricsObjectFirewallResource: ...

        @distributed_trace
        def list_by_firewalls(
                self, 
                resource_group_name: str, 
                firewall_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MetricsObjectFirewallResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.PaloAltoNetworksCloudngfwOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create_product_serial_number(self, **kwargs: Any) -> ProductSerialNumberRequestStatus: ...

        @distributed_trace
        def list_cloud_manager_tenants(self, **kwargs: Any) -> CloudManagerTenantList: ...

        @distributed_trace
        def list_product_serial_number_status(self, **kwargs: Any) -> Optional[ProductSerialNumberStatus]: ...

        @distributed_trace
        def list_support_info(self, **kwargs: Any) -> SupportInfoModel: ...


    class azure.mgmt.paloaltonetworksngfw.operations.PostRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PostRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PostRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PostRulesResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> PostRulesResource: ...

        @distributed_trace
        def get_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PostRulesResource]: ...

        @distributed_trace
        def refresh_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.operations.PreRulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PreRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: PreRulesResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreRulesResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreRulesResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                **kwargs: Any
            ) -> PreRulesResource: ...

        @distributed_trace
        def get_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounter: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PreRulesResource]: ...

        @distributed_trace
        def refresh_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                *, 
                firewall_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> RuleCounterReset: ...


    class azure.mgmt.paloaltonetworksngfw.operations.PrefixListGlobalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: PrefixListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: PrefixListGlobalRulestackResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListGlobalRulestackResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                global_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListGlobalRulestackResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                global_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> PrefixListGlobalRulestackResource: ...

        @distributed_trace
        def list(
                self, 
                global_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrefixListGlobalRulestackResource]: ...


    class azure.mgmt.paloaltonetworksngfw.operations.PrefixListLocalRulestackOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: PrefixListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: PrefixListResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrefixListResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                name: str, 
                **kwargs: Any
            ) -> PrefixListResource: ...

        @distributed_trace
        def list_by_local_rulestacks(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrefixListResource]: ...


namespace azure.mgmt.paloaltonetworksngfw.types

    class azure.mgmt.paloaltonetworksngfw.types.AdvSecurityObjectListResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[AdvSecurityObjectModel]
        next_link: str
        value: AdvSecurityObjectModel


    class azure.mgmt.paloaltonetworksngfw.types.AdvSecurityObjectModel(TypedDict, total=False):
        key "entry": Required[list[NameDescriptionObject]]
        key "type": str
        entry: list[NameDescriptionObject]
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.AppSeenData(TypedDict, total=False):
        key "appSeenList": Required[list[AppSeenInfo]]
        key "count": Required[int]
        app_seen_list: list[AppSeenInfo]
        count: int


    class azure.mgmt.paloaltonetworksngfw.types.AppSeenInfo(TypedDict, total=False):
        key "category": Required[str]
        key "risk": Required[str]
        key "standardPorts": Required[str]
        key "subCategory": Required[str]
        key "tag": Required[str]
        key "technology": Required[str]
        key "title": Required[str]
        category: str
        risk: str
        standard_ports: str
        sub_category: str
        tag: str
        technology: str
        title: str


    class azure.mgmt.paloaltonetworksngfw.types.ApplicationInsights(TypedDict, total=False):
        key "id": str
        key "key": str
        id: str
        key: str


    class azure.mgmt.paloaltonetworksngfw.types.AzureResourceManagerManagedIdentityProperties(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedIdentityType]]
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        userAssignedIdentities: dict[str, AzureResourceManagerUserAssignedIdentity]
        user_assigned_identities: dict[str, AzureResourceManagerUserAssignedIdentity]


    class azure.mgmt.paloaltonetworksngfw.types.AzureResourceManagerUserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        client_id: str
        principal_id: str


    class azure.mgmt.paloaltonetworksngfw.types.Category(TypedDict, total=False):
        key "feeds": Required[list[str]]
        key "urlCustom": Required[list[str]]
        feeds: list[str]
        url_custom: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.CertificateObject(TypedDict, total=False):
        key "auditComment": str
        key "certificateSelfSigned": Required[Union[str, BooleanEnum]]
        key "certificateSignerResourceId": str
        key "description": str
        key "etag": str
        key "provisioningState": Union[str, ProvisioningState]
        audit_comment: str
        certificate_self_signed: Union[str, BooleanEnum]
        certificate_signer_resource_id: str
        description: str
        etag: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.paloaltonetworksngfw.types.CertificateObjectGlobalRulestackResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CertificateObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CertificateObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.CertificateObjectLocalRulestackResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CertificateObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CertificateObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.Changelog(TypedDict, total=False):
        key "changes": Required[list[str]]
        key "lastCommitted": str
        key "lastModified": str
        changes: list[str]
        last_committed: str
        last_modified: str


    class azure.mgmt.paloaltonetworksngfw.types.CloudManagerTenantList(TypedDict, total=False):
        key "value": Required[list[str]]
        value: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.CountriesResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[Country]]
        next_link: str
        value: list[Country]


    class azure.mgmt.paloaltonetworksngfw.types.Country(TypedDict, total=False):
        key "code": Required[str]
        key "description": str
        code: str
        description: str


    class azure.mgmt.paloaltonetworksngfw.types.CustomCaptureConfigurationsFilter(TypedDict, total=False):
        key "destinationIpAddress": Required[str]
        key "destinationPort": Required[int]
        key "protocol": Required[Union[str, CustomCaptureConfigurationsProtocol]]
        key "sourceIpAddress": Required[str]
        key "sourcePort": int
        destination_ip_address: str
        destination_port: int
        protocol: Union[str, CustomCaptureConfigurationsProtocol]
        source_ip_address: str
        source_port: int


    class azure.mgmt.paloaltonetworksngfw.types.CustomCaptureConfigurationsFirewallResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CustomCaptureConfigurationsProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CustomCaptureConfigurationsProperties
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.CustomCaptureConfigurationsProperties(TypedDict, total=False):
        key "durationInSec": int
        key "message": str
        key "nextCheckInSeconds": int
        key "pcapDetailReason": str
        key "pcapStatus": Union[str, CustomCaptureConfigurationsStatus]
        key "storageAccountResourceId": str
        duration_in_sec: int
        message: str
        next_check_in_seconds: int
        pcapFilter: list[CustomCaptureConfigurationsFilter]
        pcapStages: list[Union[str, CustomCaptureConfigurationsStage]]
        pcap_detail_reason: str
        pcap_filter: list[CustomCaptureConfigurationsFilter]
        pcap_stages: list[Union[str, CustomCaptureConfigurationsStage]]
        pcap_status: Union[str, CustomCaptureConfigurationsStatus]
        storage_account_resource_id: str


    class azure.mgmt.paloaltonetworksngfw.types.DNSSettings(TypedDict, total=False):
        key "enableDnsProxy": Union[str, DNSProxy]
        key "enabledDnsType": Union[str, EnabledDNSType]
        dnsServers: list[IPAddress]
        dns_servers: list[IPAddress]
        enable_dns_proxy: Union[str, DNSProxy]
        enabled_dns_type: Union[str, EnabledDNSType]


    class azure.mgmt.paloaltonetworksngfw.types.DestinationAddr(TypedDict, total=False):
        cidrs: list[str]
        countries: list[str]
        feeds: list[str]
        fqdnLists: list[str]
        fqdn_lists: list[str]
        prefixLists: list[str]
        prefix_lists: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.EndpointConfiguration(TypedDict, total=False):
        key "address": Required[IPAddress]
        key "port": Required[str]
        address: IPAddress
        port: str


    class azure.mgmt.paloaltonetworksngfw.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.paloaltonetworksngfw.types.ErrorResponse(TypedDict, total=False):
        key "error": ForwardRef('ErrorDetail', module='types')
        error: ErrorDetail


    class azure.mgmt.paloaltonetworksngfw.types.EventHub(TypedDict, total=False):
        key "id": str
        key "name": str
        key "nameSpace": str
        key "policyName": str
        key "subscriptionId": str
        id: str
        name: str
        name_space: str
        policy_name: str
        subscription_id: str


    class azure.mgmt.paloaltonetworksngfw.types.FirewallDeploymentProperties(TypedDict, total=False):
        key "associatedRulestack": ForwardRef('RulestackDetails', module='types')
        key "dnsSettings": Required[DNSSettings]
        key "firewallSku": str
        key "isPanoramaManaged": Union[str, BooleanEnum]
        key "isStrataCloudManaged": Union[str, BooleanEnum]
        key "marketplaceDetails": Required[MarketplaceDetails]
        key "networkProfile": Required[NetworkProfile]
        key "panEtag": str
        key "panoramaConfig": ForwardRef('PanoramaConfig', module='types')
        key "planData": Required[PlanData]
        key "provisioningState": Union[str, ProvisioningState]
        key "strataCloudManagerConfig": ForwardRef('StrataCloudManagerConfig', module='types')
        associated_rulestack: RulestackDetails
        dns_settings: DNSSettings
        firewall_sku: str
        frontEndSettings: list[FrontendSetting]
        front_end_settings: list[FrontendSetting]
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        marketplace_details: MarketplaceDetails
        network_profile: NetworkProfile
        pan_etag: str
        panorama_config: PanoramaConfig
        plan_data: PlanData
        provisioning_state: Union[str, ProvisioningState]
        strata_cloud_manager_config: StrataCloudManagerConfig


    class azure.mgmt.paloaltonetworksngfw.types.FirewallResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[FirewallDeploymentProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        name: str
        properties: FirewallDeploymentProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.FirewallResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "properties": ForwardRef('FirewallResourceUpdateProperties', module='types')
        identity: AzureResourceManagerManagedIdentityProperties
        properties: FirewallResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.paloaltonetworksngfw.types.FirewallResourceUpdateProperties(TypedDict, total=False):
        key "associatedRulestack": ForwardRef('RulestackDetails', module='types')
        key "dnsSettings": ForwardRef('DNSSettings', module='types')
        key "isPanoramaManaged": Union[str, BooleanEnum]
        key "isStrataCloudManaged": Union[str, BooleanEnum]
        key "marketplaceDetails": ForwardRef('MarketplaceDetails', module='types')
        key "networkProfile": ForwardRef('NetworkProfile', module='types')
        key "panEtag": str
        key "panoramaConfig": ForwardRef('PanoramaConfig', module='types')
        key "planData": ForwardRef('PlanData', module='types')
        key "strataCloudManagerConfig": ForwardRef('StrataCloudManagerConfig', module='types')
        associated_rulestack: RulestackDetails
        dns_settings: DNSSettings
        frontEndSettings: list[FrontendSetting]
        front_end_settings: list[FrontendSetting]
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        marketplace_details: MarketplaceDetails
        network_profile: NetworkProfile
        pan_etag: str
        panorama_config: PanoramaConfig
        plan_data: PlanData
        strata_cloud_manager_config: StrataCloudManagerConfig


    class azure.mgmt.paloaltonetworksngfw.types.FirewallStatusProperty(TypedDict, total=False):
        key "healthReason": str
        key "healthStatus": Union[str, HealthStatus]
        key "isPanoramaManaged": Union[str, BooleanEnum]
        key "isStrataCloudManaged": Union[str, BooleanEnum]
        key "panoramaStatus": ForwardRef('PanoramaStatus', module='types')
        key "provisioningState": Union[str, ReadOnlyProvisioningState]
        key "strataCloudManagerInfo": ForwardRef('StrataCloudManagerInfo', module='types')
        health_reason: str
        health_status: Union[str, HealthStatus]
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        panorama_status: PanoramaStatus
        provisioning_state: Union[str, ReadOnlyProvisioningState]
        strata_cloud_manager_info: StrataCloudManagerInfo


    class azure.mgmt.paloaltonetworksngfw.types.FirewallStatusResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[FirewallStatusProperty]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FirewallStatusProperty
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.FqdnListGlobalRulestackResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[FqdnObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FqdnObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.FqdnListLocalRulestackResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[FqdnObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FqdnObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.FqdnObject(TypedDict, total=False):
        key "auditComment": str
        key "description": str
        key "etag": str
        key "fqdnList": Required[list[str]]
        key "provisioningState": Union[str, ProvisioningState]
        audit_comment: str
        description: str
        etag: str
        fqdn_list: list[str]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.paloaltonetworksngfw.types.FrontendSetting(TypedDict, total=False):
        key "backendConfiguration": Required[EndpointConfiguration]
        key "frontendConfiguration": Required[EndpointConfiguration]
        key "name": Required[str]
        key "protocol": Required[Union[str, ProtocolType]]
        backend_configuration: EndpointConfiguration
        frontend_configuration: EndpointConfiguration
        name: str
        protocol: Union[str, ProtocolType]


    class azure.mgmt.paloaltonetworksngfw.types.GlobalRulestackInfo(TypedDict, total=False):
        key "azureId": Required[str]
        azure_id: str


    class azure.mgmt.paloaltonetworksngfw.types.GlobalRulestackResource(ProxyResource):
        key "id": str
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[RulestackProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        name: str
        properties: RulestackProperties
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.GlobalRulestackResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "location": str
        key "properties": ForwardRef('GlobalRulestackResourceUpdateProperties', module='types')
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        properties: GlobalRulestackResourceUpdateProperties


    class azure.mgmt.paloaltonetworksngfw.types.GlobalRulestackResourceUpdateProperties(TypedDict, total=False):
        key "defaultMode": Union[str, DefaultMode]
        key "description": str
        key "minAppIdVersion": str
        key "panEtag": str
        key "panLocation": str
        key "scope": Union[str, ScopeType]
        key "securityServices": ForwardRef('SecurityServices', module='types')
        associatedSubscriptions: list[str]
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        min_app_id_version: str
        pan_etag: str
        pan_location: str
        scope: Union[str, ScopeType]
        security_services: SecurityServices


    class azure.mgmt.paloaltonetworksngfw.types.IPAddress(TypedDict, total=False):
        key "address": str
        key "resourceId": str
        address: str
        resource_id: str


    class azure.mgmt.paloaltonetworksngfw.types.IPAddressSpace(TypedDict, total=False):
        key "addressSpace": str
        key "resourceId": str
        address_space: str
        resource_id: str


    class azure.mgmt.paloaltonetworksngfw.types.ListAppIdResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[str]]
        next_link: str
        value: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.ListFirewallsResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[str]]
        next_link: str
        value: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.LocalRulesResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[RuleEntry]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.LocalRulestackResource(TrackedResource):
        key "id": str
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": Required[RulestackProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        name: str
        properties: RulestackProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.LocalRulestackResourceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('AzureResourceManagerManagedIdentityProperties', module='types')
        key "properties": ForwardRef('LocalRulestackResourceUpdateProperties', module='types')
        identity: AzureResourceManagerManagedIdentityProperties
        properties: LocalRulestackResourceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.paloaltonetworksngfw.types.LocalRulestackResourceUpdateProperties(TypedDict, total=False):
        key "defaultMode": Union[str, DefaultMode]
        key "description": str
        key "minAppIdVersion": str
        key "panEtag": str
        key "panLocation": str
        key "scope": Union[str, ScopeType]
        key "securityServices": ForwardRef('SecurityServices', module='types')
        associatedSubscriptions: list[str]
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        min_app_id_version: str
        pan_etag: str
        pan_location: str
        scope: Union[str, ScopeType]
        security_services: SecurityServices


    class azure.mgmt.paloaltonetworksngfw.types.LogDestination(TypedDict, total=False):
        key "eventHubConfigurations": ForwardRef('EventHub', module='types')
        key "monitorConfigurations": ForwardRef('MonitorLog', module='types')
        key "storageConfigurations": ForwardRef('StorageAccount', module='types')
        event_hub_configurations: EventHub
        monitor_configurations: MonitorLog
        storage_configurations: StorageAccount


    class azure.mgmt.paloaltonetworksngfw.types.LogSettings(TypedDict, total=False):
        key "applicationInsights": ForwardRef('ApplicationInsights', module='types')
        key "commonDestination": ForwardRef('LogDestination', module='types')
        key "decryptLogDestination": ForwardRef('LogDestination', module='types')
        key "logOption": Union[str, LogOption]
        key "logType": Union[str, LogType]
        key "threatLogDestination": ForwardRef('LogDestination', module='types')
        key "trafficLogDestination": ForwardRef('LogDestination', module='types')
        application_insights: ApplicationInsights
        common_destination: LogDestination
        decrypt_log_destination: LogDestination
        log_option: Union[str, LogOption]
        log_type: Union[str, LogType]
        threat_log_destination: LogDestination
        traffic_log_destination: LogDestination


    class azure.mgmt.paloaltonetworksngfw.types.MarketplaceDetails(TypedDict, total=False):
        key "marketplaceSubscriptionId": str
        key "marketplaceSubscriptionStatus": Union[str, MarketplaceSubscriptionStatus]
        key "offerId": Required[str]
        key "publisherId": Required[str]
        marketplace_subscription_id: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        offer_id: str
        publisher_id: str


    class azure.mgmt.paloaltonetworksngfw.types.MetricsObject(TypedDict, total=False):
        key "applicationInsightsConnectionString": Required[str]
        key "applicationInsightsResourceId": Required[str]
        key "panEtag": str
        key "provisioningState": Union[str, ProvisioningState]
        application_insights_connection_string: str
        application_insights_resource_id: str
        pan_etag: str
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.paloaltonetworksngfw.types.MetricsObjectFirewallResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[MetricsObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: MetricsObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.MonitorLog(TypedDict, total=False):
        key "id": str
        key "primaryKey": str
        key "secondaryKey": str
        key "subscriptionId": str
        key "workspace": str
        id: str
        primary_key: str
        secondary_key: str
        subscription_id: str
        workspace: str


    class azure.mgmt.paloaltonetworksngfw.types.NameDescriptionObject(TypedDict, total=False):
        key "description": str
        key "name": Required[str]
        description: str
        name: str


    class azure.mgmt.paloaltonetworksngfw.types.NetworkProfile(TypedDict, total=False):
        key "enableEgressNat": Required[Union[str, EgressNat]]
        key "networkType": Required[Union[str, NetworkType]]
        key "publicIps": Required[list[IPAddress]]
        key "vnetConfiguration": ForwardRef('VnetConfiguration', module='types')
        key "vwanConfiguration": ForwardRef('VwanConfiguration', module='types')
        egressNatIp: list[IPAddress]
        egress_nat_ip: list[IPAddress]
        enable_egress_nat: Union[str, EgressNat]
        network_type: Union[str, NetworkType]
        privateSourceNatRulesDestination: list[str]
        private_source_nat_rules_destination: list[str]
        public_ips: list[IPAddress]
        trustedRanges: list[str]
        trusted_ranges: list[str]
        vnet_configuration: VnetConfiguration
        vwan_configuration: VwanConfiguration


    class azure.mgmt.paloaltonetworksngfw.types.Operation(TypedDict, total=False):
        key "actionType": Union[str, ActionType]
        key "display": ForwardRef('OperationDisplay', module='types')
        key "isDataAction": bool
        key "name": str
        key "origin": Union[str, Origin]
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]


    class azure.mgmt.paloaltonetworksngfw.types.OperationDisplay(TypedDict, total=False):
        key "description": str
        key "operation": str
        key "provider": str
        key "resource": str
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.paloaltonetworksngfw.types.PanoramaConfig(TypedDict, total=False):
        key "cgName": str
        key "configString": Required[str]
        key "dgName": str
        key "hostName": str
        key "panoramaServer": str
        key "panoramaServer2": str
        key "tplName": str
        key "vmAuthKey": str
        cg_name: str
        config_string: str
        dg_name: str
        host_name: str
        panorama_server: str
        panorama_server2: str
        tpl_name: str
        vm_auth_key: str


    class azure.mgmt.paloaltonetworksngfw.types.PanoramaStatus(TypedDict, total=False):
        key "panoramaServer2Status": Union[str, ServerStatus]
        key "panoramaServerStatus": Union[str, ServerStatus]
        panorama_server2_status: Union[str, ServerStatus]
        panorama_server_status: Union[str, ServerStatus]


    class azure.mgmt.paloaltonetworksngfw.types.PlanData(TypedDict, total=False):
        key "billingCycle": Required[Union[str, BillingCycle]]
        key "effectiveDate": str
        key "planId": Required[str]
        key "usageType": Union[str, UsageType]
        billing_cycle: Union[str, BillingCycle]
        effective_date: str
        plan_id: str
        usage_type: Union[str, UsageType]


    class azure.mgmt.paloaltonetworksngfw.types.PostRulesResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[RuleEntry]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.PreRulesResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[RuleEntry]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: RuleEntry
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.PredefinedUrlCategoriesResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[list[PredefinedUrlCategory]]
        next_link: str
        value: list[PredefinedUrlCategory]


    class azure.mgmt.paloaltonetworksngfw.types.PredefinedUrlCategory(TypedDict, total=False):
        key "action": Required[str]
        key "name": Required[str]
        action: str
        name: str


    class azure.mgmt.paloaltonetworksngfw.types.PrefixListGlobalRulestackResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[PrefixObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrefixObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.PrefixListResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[PrefixObject]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrefixObject
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.PrefixObject(TypedDict, total=False):
        key "auditComment": str
        key "description": str
        key "etag": str
        key "prefixList": Required[list[str]]
        key "provisioningState": Union[str, ProvisioningState]
        audit_comment: str
        description: str
        etag: str
        prefix_list: list[str]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.paloaltonetworksngfw.types.ProductSerialNumberRequestStatus(TypedDict, total=False):
        key "status": Required[str]
        status: str


    class azure.mgmt.paloaltonetworksngfw.types.ProductSerialNumberStatus(TypedDict, total=False):
        key "serialNumber": str
        key "status": Required[Union[str, ProductSerialStatusValues]]
        serial_number: str
        status: Union[str, ProductSerialStatusValues]


    class azure.mgmt.paloaltonetworksngfw.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.RuleCounter(TypedDict, total=False):
        key "appSeen": ForwardRef('AppSeenData', module='types')
        key "firewallName": str
        key "hitCount": int
        key "lastUpdatedTimestamp": str
        key "priority": Required[str]
        key "requestTimestamp": str
        key "ruleListName": str
        key "ruleName": Required[str]
        key "ruleStackName": str
        key "timestamp": str
        app_seen: AppSeenData
        firewall_name: str
        hit_count: int
        last_updated_timestamp: str
        priority: str
        request_timestamp: str
        rule_list_name: str
        rule_name: str
        rule_stack_name: str
        timestamp: str


    class azure.mgmt.paloaltonetworksngfw.types.RuleCounterReset(TypedDict, total=False):
        key "firewallName": str
        key "priority": str
        key "ruleListName": str
        key "ruleName": str
        key "ruleStackName": str
        firewall_name: str
        priority: str
        rule_list_name: str
        rule_name: str
        rule_stack_name: str


    class azure.mgmt.paloaltonetworksngfw.types.RuleEntry(TypedDict, total=False):
        key "actionType": Union[str, ActionEnum]
        key "auditComment": str
        key "category": ForwardRef('Category', module='types')
        key "decryptionRuleType": Union[str, DecryptionRuleTypeEnum]
        key "description": str
        key "destination": ForwardRef('DestinationAddr', module='types')
        key "enableLogging": Union[str, StateEnum]
        key "etag": str
        key "inboundInspectionCertificate": str
        key "negateDestination": Union[str, BooleanEnum]
        key "negateSource": Union[str, BooleanEnum]
        key "priority": int
        key "protocol": str
        key "provisioningState": Union[str, ProvisioningState]
        key "ruleName": Required[str]
        key "ruleState": Union[str, StateEnum]
        key "source": ForwardRef('SourceAddr', module='types')
        action_type: Union[str, ActionEnum]
        applications: list[str]
        audit_comment: str
        category: Category
        decryption_rule_type: Union[str, DecryptionRuleTypeEnum]
        description: str
        destination: DestinationAddr
        enable_logging: Union[str, StateEnum]
        etag: str
        inbound_inspection_certificate: str
        negate_destination: Union[str, BooleanEnum]
        negate_source: Union[str, BooleanEnum]
        priority: int
        protocol: str
        protocolPortList: list[str]
        protocol_port_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        rule_name: str
        rule_state: Union[str, StateEnum]
        source: SourceAddr
        tags: list[TagInfo]


    class azure.mgmt.paloaltonetworksngfw.types.RulestackDetails(TypedDict, total=False):
        key "location": str
        key "resourceId": str
        key "rulestackId": str
        location: str
        resource_id: str
        rulestack_id: str


    class azure.mgmt.paloaltonetworksngfw.types.RulestackProperties(TypedDict, total=False):
        key "defaultMode": Union[str, DefaultMode]
        key "description": str
        key "minAppIdVersion": str
        key "panEtag": str
        key "panLocation": str
        key "provisioningState": Union[str, ProvisioningState]
        key "scope": Union[str, ScopeType]
        key "securityServices": ForwardRef('SecurityServices', module='types')
        associatedSubscriptions: list[str]
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        min_app_id_version: str
        pan_etag: str
        pan_location: str
        provisioning_state: Union[str, ProvisioningState]
        scope: Union[str, ScopeType]
        security_services: SecurityServices


    class azure.mgmt.paloaltonetworksngfw.types.SecurityServices(TypedDict, total=False):
        key "antiSpywareProfile": str
        key "antiVirusProfile": str
        key "dnsSubscription": str
        key "fileBlockingProfile": str
        key "outboundTrustCertificate": str
        key "outboundUnTrustCertificate": str
        key "urlFilteringProfile": str
        key "vulnerabilityProfile": str
        anti_spyware_profile: str
        anti_virus_profile: str
        dns_subscription: str
        file_blocking_profile: str
        outbound_trust_certificate: str
        outbound_un_trust_certificate: str
        url_filtering_profile: str
        vulnerability_profile: str


    class azure.mgmt.paloaltonetworksngfw.types.SecurityServicesResponse(TypedDict, total=False):
        key "nextLink": str
        key "value": Required[SecurityServicesTypeList]
        next_link: str
        value: SecurityServicesTypeList


    class azure.mgmt.paloaltonetworksngfw.types.SecurityServicesTypeList(TypedDict, total=False):
        key "entry": Required[list[NameDescriptionObject]]
        key "type": str
        entry: list[NameDescriptionObject]
        type: str


    class azure.mgmt.paloaltonetworksngfw.types.SourceAddr(TypedDict, total=False):
        cidrs: list[str]
        countries: list[str]
        feeds: list[str]
        prefixLists: list[str]
        prefix_lists: list[str]


    class azure.mgmt.paloaltonetworksngfw.types.StorageAccount(TypedDict, total=False):
        key "accountName": str
        key "id": str
        key "subscriptionId": str
        account_name: str
        id: str
        subscription_id: str


    class azure.mgmt.paloaltonetworksngfw.types.StrataCloudManagerConfig(TypedDict, total=False):
        key "cloudManagerName": Required[str]
        cloud_manager_name: str


    class azure.mgmt.paloaltonetworksngfw.types.StrataCloudManagerInfo(TypedDict, total=False):
        key "folderName": str
        key "hubUrl": str
        folder_name: str
        hub_url: str


    class azure.mgmt.paloaltonetworksngfw.types.SupportInfo(TypedDict, total=False):
        key "accountId": str
        key "accountRegistered": Union[str, BooleanEnum]
        key "freeTrial": Union[str, BooleanEnum]
        key "freeTrialCreditLeft": int
        key "freeTrialDaysLeft": int
        key "helpURL": str
        key "productSerial": str
        key "productSku": str
        key "registerURL": str
        key "supportURL": str
        key "userDomainSupported": Union[str, BooleanEnum]
        key "userRegistered": Union[str, BooleanEnum]
        account_id: str
        account_registered: Union[str, BooleanEnum]
        free_trial: Union[str, BooleanEnum]
        free_trial_credit_left: int
        free_trial_days_left: int
        help_url: str
        product_serial: str
        product_sku: str
        register_url: str
        support_url: str
        user_domain_supported: Union[str, BooleanEnum]
        user_registered: Union[str, BooleanEnum]


    class azure.mgmt.paloaltonetworksngfw.types.SupportInfoModel(TypedDict, total=False):
        key "accountId": str
        key "accountRegistrationStatus": Union[str, RegistrationStatus]
        key "credits": int
        key "endDateForCredits": str
        key "freeTrial": Union[str, EnableStatus]
        key "freeTrialCreditLeft": int
        key "freeTrialDaysLeft": int
        key "helpURL": str
        key "hubUrl": str
        key "monthlyCreditLeft": int
        key "productSerial": str
        key "productSku": str
        key "registerURL": str
        key "startDateForCredits": str
        key "supportURL": str
        account_id: str
        account_registration_status: Union[str, RegistrationStatus]
        credits: int
        end_date_for_credits: str
        free_trial: Union[str, EnableStatus]
        free_trial_credit_left: int
        free_trial_days_left: int
        help_url: str
        hub_url: str
        monthly_credit_left: int
        product_serial: str
        product_sku: str
        register_url: str
        start_date_for_credits: str
        support_url: str


    class azure.mgmt.paloaltonetworksngfw.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.paloaltonetworksngfw.types.TagInfo(TypedDict, total=False):
        key "key": Required[str]
        key "value": Required[str]
        key: str
        value: str


    class azure.mgmt.paloaltonetworksngfw.types.TrackedResource(Resource):
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


    class azure.mgmt.paloaltonetworksngfw.types.VnetConfiguration(TypedDict, total=False):
        key "ipOfTrustSubnetForUdr": ForwardRef('IPAddress', module='types')
        key "trustSubnet": Required[IPAddressSpace]
        key "unTrustSubnet": Required[IPAddressSpace]
        key "vnet": Required[IPAddressSpace]
        ip_of_trust_subnet_for_udr: IPAddress
        trust_subnet: IPAddressSpace
        un_trust_subnet: IPAddressSpace
        vnet: IPAddressSpace


    class azure.mgmt.paloaltonetworksngfw.types.VwanConfiguration(TypedDict, total=False):
        key "ipOfTrustSubnetForUdr": ForwardRef('IPAddress', module='types')
        key "networkVirtualApplianceId": str
        key "trustSubnet": ForwardRef('IPAddressSpace', module='types')
        key "unTrustSubnet": ForwardRef('IPAddressSpace', module='types')
        key "vHub": Required[IPAddressSpace]
        ip_of_trust_subnet_for_udr: IPAddress
        network_virtual_appliance_id: str
        trust_subnet: IPAddressSpace
        un_trust_subnet: IPAddressSpace
        v_hub: IPAddressSpace


```