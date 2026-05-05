```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.paloaltonetworksngfw

    class azure.mgmt.paloaltonetworksngfw.PaloAltoNetworksNgfwMgmtClient: implements ContextManager 
        certificate_object_global_rulestack: CertificateObjectGlobalRulestackOperations
        certificate_object_local_rulestack: CertificateObjectLocalRulestackOperations
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


namespace azure.mgmt.paloaltonetworksngfw.aio

    class azure.mgmt.paloaltonetworksngfw.aio.PaloAltoNetworksNgfwMgmtClient: implements AsyncContextManager 
        certificate_object_global_rulestack: CertificateObjectGlobalRulestackOperations
        certificate_object_local_rulestack: CertificateObjectLocalRulestackOperations
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
                email: Optional[str] = None, 
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
                type: Union[str, AdvSecurityObjectTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace_async
        async def list_app_ids(
                self, 
                global_rulestack_name: str, 
                app_id_version: Optional[str] = None, 
                app_prefix: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ListAppIdResponse: ...

        @distributed_trace_async
        async def list_countries(
                self, 
                global_rulestack_name: str, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> PredefinedUrlCategoriesResponse: ...

        @distributed_trace_async
        async def list_security_services(
                self, 
                global_rulestack_name: str, 
                type: Union[str, SecurityServicesTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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
                email: Optional[str] = None, 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace_async
        async def list_advanced_security_objects(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                app_id_version: Optional[str] = None, 
                app_prefix: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[PredefinedUrlCategory]: ...

        @distributed_trace_async
        async def list_security_services(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                type: Union[str, SecurityServicesTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectListResponse(Model):
        next_link: str
        value: AdvSecurityObjectModel

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: AdvSecurityObjectModel, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectModel(Model):
        entry: list[NameDescriptionObject]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                entry: list[NameDescriptionObject], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.AdvSecurityObjectTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FEEDS = "feeds"
        URL_CUSTOM = "urlCustom"


    class azure.mgmt.paloaltonetworksngfw.models.AppSeenData(Model):
        app_seen_list: list[AppSeenInfo]
        count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_seen_list: list[AppSeenInfo], 
                count: int, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.AppSeenInfo(Model):
        category: str
        risk: str
        standard_ports: str
        sub_category: str
        tag: str
        technology: str
        title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                category: str, 
                risk: str, 
                standard_ports: str, 
                sub_category: str, 
                tag: str, 
                technology: str, 
                title: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ApplicationInsights(Model):
        id: str
        key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                key: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.AzureResourceManagerManagedIdentityProperties(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedIdentityType]
        user_assigned_identities: dict[str, AzureResourceManagerUserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedIdentityType], 
                user_assigned_identities: Optional[dict[str, AzureResourceManagerUserAssignedIdentity]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.AzureResourceManagerUserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_id: Optional[str] = ..., 
                principal_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.BillingCycle(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONTHLY = "MONTHLY"
        WEEKLY = "WEEKLY"


    class azure.mgmt.paloaltonetworksngfw.models.BooleanEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "FALSE"
        TRUE = "TRUE"


    class azure.mgmt.paloaltonetworksngfw.models.Category(Model):
        feeds: list[str]
        url_custom: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                feeds: list[str], 
                url_custom: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectGlobalRulestackResource(ProxyResource):
        audit_comment: str
        certificate_self_signed: Union[str, BooleanEnum]
        certificate_signer_resource_id: str
        description: str
        etag: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                certificate_self_signed: Union[str, BooleanEnum], 
                certificate_signer_resource_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectGlobalRulestackResourceListResult(Model):
        next_link: str
        value: list[CertificateObjectGlobalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[CertificateObjectGlobalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectLocalRulestackResource(ProxyResource):
        audit_comment: str
        certificate_self_signed: Union[str, BooleanEnum]
        certificate_signer_resource_id: str
        description: str
        etag: str
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                certificate_self_signed: Union[str, BooleanEnum], 
                certificate_signer_resource_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CertificateObjectLocalRulestackResourceListResult(Model):
        next_link: str
        value: list[CertificateObjectLocalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[CertificateObjectLocalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.Changelog(Model):
        changes: list[str]
        last_committed: datetime
        last_modified: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                changes: list[str], 
                last_committed: Optional[datetime] = ..., 
                last_modified: Optional[datetime] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CloudManagerTenantList(Model):
        value: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CountriesResponse(Model):
        next_link: str
        value: list[Country]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[Country], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.Country(Model):
        code: str
        description: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: str, 
                description: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.paloaltonetworksngfw.models.DNSProxy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.DNSSettings(Model):
        dns_servers: list[IPAddress]
        enable_dns_proxy: Union[str, DNSProxy]
        enabled_dns_type: Union[str, EnabledDNSType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dns_servers: Optional[list[IPAddress]] = ..., 
                enable_dns_proxy: Optional[Union[str, DNSProxy]] = ..., 
                enabled_dns_type: Optional[Union[str, EnabledDNSType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.DecryptionRuleTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SSL_INBOUND_INSPECTION = "SSLInboundInspection"
        SSL_OUTBOUND_INSPECTION = "SSLOutboundInspection"


    class azure.mgmt.paloaltonetworksngfw.models.DefaultMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FIREWALL = "FIREWALL"
        IPS = "IPS"
        NONE = "NONE"


    class azure.mgmt.paloaltonetworksngfw.models.DestinationAddr(Model):
        cidrs: list[str]
        countries: list[str]
        feeds: list[str]
        fqdn_lists: list[str]
        prefix_lists: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cidrs: Optional[list[str]] = ..., 
                countries: Optional[list[str]] = ..., 
                feeds: Optional[list[str]] = ..., 
                fqdn_lists: Optional[list[str]] = ..., 
                prefix_lists: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.EgressNat(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.EnableStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.paloaltonetworksngfw.models.EnabledDNSType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE = "AZURE"
        CUSTOM = "CUSTOM"


    class azure.mgmt.paloaltonetworksngfw.models.EndpointConfiguration(Model):
        address: IPAddress
        port: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: IPAddress, 
                port: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ErrorAdditionalInfo(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ErrorDetail(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ErrorResponse(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.EventHub(Model):
        id: str
        name: str
        name_space: str
        policy_name: str
        subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                name_space: Optional[str] = ..., 
                policy_name: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResource(TrackedResource):
        associated_rulestack: RulestackDetails
        dns_settings: DNSSettings
        front_end_settings: list[FrontendSetting]
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        location: str
        marketplace_details: MarketplaceDetails
        name: str
        network_profile: NetworkProfile
        pan_etag: str
        panorama_config: PanoramaConfig
        plan_data: PlanData
        provisioning_state: Union[str, ProvisioningState]
        strata_cloud_manager_config: StrataCloudManagerConfig
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                associated_rulestack: Optional[RulestackDetails] = ..., 
                dns_settings: DNSSettings, 
                front_end_settings: Optional[list[FrontendSetting]] = ..., 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                is_panorama_managed: Optional[Union[str, BooleanEnum]] = ..., 
                is_strata_cloud_managed: Optional[Union[str, BooleanEnum]] = ..., 
                location: str, 
                marketplace_details: MarketplaceDetails, 
                network_profile: NetworkProfile, 
                pan_etag: Optional[str] = ..., 
                panorama_config: Optional[PanoramaConfig] = ..., 
                plan_data: PlanData, 
                strata_cloud_manager_config: Optional[StrataCloudManagerConfig] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResourceListResult(Model):
        next_link: str
        value: list[FirewallResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[FirewallResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResourceUpdate(Model):
        identity: AzureResourceManagerManagedIdentityProperties
        properties: FirewallResourceUpdateProperties
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                properties: Optional[FirewallResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallResourceUpdateProperties(Model):
        associated_rulestack: RulestackDetails
        dns_settings: DNSSettings
        front_end_settings: list[FrontendSetting]
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        marketplace_details: MarketplaceDetails
        network_profile: NetworkProfile
        pan_etag: str
        panorama_config: PanoramaConfig
        plan_data: PlanData
        strata_cloud_manager_config: StrataCloudManagerConfig

        def __eq__(self, other: Any) -> bool: ...

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
                strata_cloud_manager_config: Optional[StrataCloudManagerConfig] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallStatusResource(ProxyResource):
        health_reason: str
        health_status: Union[str, HealthStatus]
        id: str
        is_panorama_managed: Union[str, BooleanEnum]
        is_strata_cloud_managed: Union[str, BooleanEnum]
        name: str
        panorama_status: PanoramaStatus
        provisioning_state: Union[str, ReadOnlyProvisioningState]
        strata_cloud_manager_info: StrataCloudManagerInfo
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                strata_cloud_manager_info: Optional[StrataCloudManagerInfo] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FirewallStatusResourceListResult(Model):
        next_link: str
        value: list[FirewallStatusResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[FirewallStatusResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListGlobalRulestackResource(ProxyResource):
        audit_comment: str
        description: str
        etag: str
        fqdn_list: list[str]
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                fqdn_list: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListGlobalRulestackResourceListResult(Model):
        next_link: str
        value: list[FqdnListGlobalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[FqdnListGlobalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListLocalRulestackResource(ProxyResource):
        audit_comment: str
        description: str
        etag: str
        fqdn_list: list[str]
        id: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                fqdn_list: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FqdnListLocalRulestackResourceListResult(Model):
        next_link: str
        value: list[FqdnListLocalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[FqdnListLocalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.FrontendSetting(Model):
        backend_configuration: EndpointConfiguration
        frontend_configuration: EndpointConfiguration
        name: str
        protocol: Union[str, ProtocolType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backend_configuration: EndpointConfiguration, 
                frontend_configuration: EndpointConfiguration, 
                name: str, 
                protocol: Union[str, ProtocolType], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackInfo(Model):
        azure_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_id: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResource(ProxyResource):
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        min_app_id_version: str
        name: str
        pan_etag: str
        pan_location: str
        provisioning_state: Union[str, ProvisioningState]
        scope: Union[str, ScopeType]
        security_services: SecurityServices
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                associated_subscriptions: Optional[list[str]] = ..., 
                default_mode: Optional[Union[str, DefaultMode]] = ..., 
                description: Optional[str] = ..., 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: str, 
                min_app_id_version: Optional[str] = ..., 
                pan_etag: Optional[str] = ..., 
                pan_location: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                security_services: Optional[SecurityServices] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResourceListResult(Model):
        next_link: str
        value: list[GlobalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[GlobalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResourceUpdate(Model):
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        properties: GlobalRulestackResourceUpdateProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: Optional[str] = ..., 
                properties: Optional[GlobalRulestackResourceUpdateProperties] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.GlobalRulestackResourceUpdateProperties(Model):
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        min_app_id_version: str
        pan_etag: str
        pan_location: str
        scope: Union[str, ScopeType]
        security_services: SecurityServices

        def __eq__(self, other: Any) -> bool: ...

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
                security_services: Optional[SecurityServices] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GREEN = "GREEN"
        INITIALIZING = "INITIALIZING"
        RED = "RED"
        YELLOW = "YELLOW"


    class azure.mgmt.paloaltonetworksngfw.models.IPAddress(Model):
        address: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.IPAddressSpace(Model):
        address_space: str
        resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                address_space: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ListAppIdResponse(Model):
        next_link: str
        value: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ListFirewallsResponse(Model):
        next_link: str
        value: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulesResource(ProxyResource):
        action_type: Union[str, ActionEnum]
        applications: list[str]
        audit_comment: str
        category: Category
        decryption_rule_type: Union[str, DecryptionRuleTypeEnum]
        description: str
        destination: DestinationAddr
        enable_logging: Union[str, StateEnum]
        etag: str
        id: str
        inbound_inspection_certificate: str
        name: str
        negate_destination: Union[str, BooleanEnum]
        negate_source: Union[str, BooleanEnum]
        priority: int
        protocol: str
        protocol_port_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        rule_name: str
        rule_state: Union[str, StateEnum]
        source: SourceAddr
        system_data: SystemData
        tags: list[TagInfo]
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                protocol: str = "application-default", 
                protocol_port_list: Optional[list[str]] = ..., 
                rule_name: str, 
                rule_state: Optional[Union[str, StateEnum]] = ..., 
                source: Optional[SourceAddr] = ..., 
                tags: Optional[list[TagInfo]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulesResourceListResult(Model):
        next_link: str
        value: list[LocalRulesResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[LocalRulesResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResource(TrackedResource):
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        id: str
        identity: AzureResourceManagerManagedIdentityProperties
        location: str
        min_app_id_version: str
        name: str
        pan_etag: str
        pan_location: str
        provisioning_state: Union[str, ProvisioningState]
        scope: Union[str, ScopeType]
        security_services: SecurityServices
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                associated_subscriptions: Optional[list[str]] = ..., 
                default_mode: Optional[Union[str, DefaultMode]] = ..., 
                description: Optional[str] = ..., 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                location: str, 
                min_app_id_version: Optional[str] = ..., 
                pan_etag: Optional[str] = ..., 
                pan_location: Optional[str] = ..., 
                scope: Optional[Union[str, ScopeType]] = ..., 
                security_services: Optional[SecurityServices] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResourceListResult(Model):
        next_link: str
        value: list[LocalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[LocalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResourceUpdate(Model):
        identity: AzureResourceManagerManagedIdentityProperties
        properties: LocalRulestackResourceUpdateProperties
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[AzureResourceManagerManagedIdentityProperties] = ..., 
                properties: Optional[LocalRulestackResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LocalRulestackResourceUpdateProperties(Model):
        associated_subscriptions: list[str]
        default_mode: Union[str, DefaultMode]
        description: str
        min_app_id_version: str
        pan_etag: str
        pan_location: str
        scope: Union[str, ScopeType]
        security_services: SecurityServices

        def __eq__(self, other: Any) -> bool: ...

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
                security_services: Optional[SecurityServices] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LogDestination(Model):
        event_hub_configurations: EventHub
        monitor_configurations: MonitorLog
        storage_configurations: StorageAccount

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                event_hub_configurations: Optional[EventHub] = ..., 
                monitor_configurations: Optional[MonitorLog] = ..., 
                storage_configurations: Optional[StorageAccount] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.LogOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INDIVIDUAL_DESTINATION = "INDIVIDUAL_DESTINATION"
        SAME_DESTINATION = "SAME_DESTINATION"


    class azure.mgmt.paloaltonetworksngfw.models.LogSettings(Model):
        application_insights: ApplicationInsights
        common_destination: LogDestination
        decrypt_log_destination: LogDestination
        log_option: Union[str, LogOption]
        log_type: Union[str, LogType]
        threat_log_destination: LogDestination
        traffic_log_destination: LogDestination

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_insights: Optional[ApplicationInsights] = ..., 
                common_destination: Optional[LogDestination] = ..., 
                decrypt_log_destination: Optional[LogDestination] = ..., 
                log_option: Optional[Union[str, LogOption]] = ..., 
                log_type: Optional[Union[str, LogType]] = ..., 
                threat_log_destination: Optional[LogDestination] = ..., 
                traffic_log_destination: Optional[LogDestination] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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


    class azure.mgmt.paloaltonetworksngfw.models.MarketplaceDetails(Model):
        marketplace_subscription_id: str
        marketplace_subscription_status: Union[str, MarketplaceSubscriptionStatus]
        offer_id: str
        publisher_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]] = ..., 
                offer_id: str, 
                publisher_id: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULFILLMENT_REQUESTED = "FulfillmentRequested"
        NOT_STARTED = "NotStarted"
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.paloaltonetworksngfw.models.MetricsObjectFirewallResource(ProxyResource):
        application_insights_connection_string: str
        application_insights_resource_id: str
        id: str
        name: str
        pan_etag: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_insights_connection_string: str, 
                application_insights_resource_id: str, 
                pan_etag: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.MetricsObjectFirewallResourceListResult(Model):
        next_link: str
        value: list[MetricsObjectFirewallResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[MetricsObjectFirewallResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.MonitorLog(Model):
        id: str
        primary_key: str
        secondary_key: str
        subscription_id: str
        workspace: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                primary_key: Optional[str] = ..., 
                secondary_key: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
                workspace: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.NameDescriptionObject(Model):
        description: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.NetworkProfile(Model):
        egress_nat_ip: list[IPAddress]
        enable_egress_nat: Union[str, EgressNat]
        network_type: Union[str, NetworkType]
        private_source_nat_rules_destination: list[str]
        public_ips: list[IPAddress]
        trusted_ranges: list[str]
        vnet_configuration: VnetConfiguration
        vwan_configuration: VwanConfiguration

        def __eq__(self, other: Any) -> bool: ...

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
                vwan_configuration: Optional[VwanConfiguration] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.NetworkType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VNET = "VNET"
        VWAN = "VWAN"


    class azure.mgmt.paloaltonetworksngfw.models.Operation(Model):
        action_type: Union[str, ActionType]
        display: OperationDisplay
        is_data_action: bool
        name: str
        origin: Union[str, Origin]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[OperationDisplay] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.OperationDisplay(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.OperationListResult(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.paloaltonetworksngfw.models.PanoramaConfig(Model):
        cg_name: str
        config_string: str
        dg_name: str
        host_name: str
        panorama_server: str
        panorama_server2: str
        tpl_name: str
        vm_auth_key: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                config_string: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PanoramaStatus(Model):
        panorama_server2_status: Union[str, ServerStatus]
        panorama_server_status: Union[str, ServerStatus]

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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PlanData(Model):
        billing_cycle: Union[str, BillingCycle]
        effective_date: datetime
        plan_id: str
        usage_type: Union[str, UsageType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                billing_cycle: Union[str, BillingCycle], 
                plan_id: str, 
                usage_type: Optional[Union[str, UsageType]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PostRulesResource(ProxyResource):
        action_type: Union[str, ActionEnum]
        applications: list[str]
        audit_comment: str
        category: Category
        decryption_rule_type: Union[str, DecryptionRuleTypeEnum]
        description: str
        destination: DestinationAddr
        enable_logging: Union[str, StateEnum]
        etag: str
        id: str
        inbound_inspection_certificate: str
        name: str
        negate_destination: Union[str, BooleanEnum]
        negate_source: Union[str, BooleanEnum]
        priority: int
        protocol: str
        protocol_port_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        rule_name: str
        rule_state: Union[str, StateEnum]
        source: SourceAddr
        system_data: SystemData
        tags: list[TagInfo]
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                protocol: str = "application-default", 
                protocol_port_list: Optional[list[str]] = ..., 
                rule_name: str, 
                rule_state: Optional[Union[str, StateEnum]] = ..., 
                source: Optional[SourceAddr] = ..., 
                tags: Optional[list[TagInfo]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PostRulesResourceListResult(Model):
        next_link: str
        value: list[PostRulesResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PostRulesResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PreRulesResource(ProxyResource):
        action_type: Union[str, ActionEnum]
        applications: list[str]
        audit_comment: str
        category: Category
        decryption_rule_type: Union[str, DecryptionRuleTypeEnum]
        description: str
        destination: DestinationAddr
        enable_logging: Union[str, StateEnum]
        etag: str
        id: str
        inbound_inspection_certificate: str
        name: str
        negate_destination: Union[str, BooleanEnum]
        negate_source: Union[str, BooleanEnum]
        priority: int
        protocol: str
        protocol_port_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        rule_name: str
        rule_state: Union[str, StateEnum]
        source: SourceAddr
        system_data: SystemData
        tags: list[TagInfo]
        type: str

        def __eq__(self, other: Any) -> bool: ...

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
                protocol: str = "application-default", 
                protocol_port_list: Optional[list[str]] = ..., 
                rule_name: str, 
                rule_state: Optional[Union[str, StateEnum]] = ..., 
                source: Optional[SourceAddr] = ..., 
                tags: Optional[list[TagInfo]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PreRulesResourceListResult(Model):
        next_link: str
        value: list[PreRulesResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PreRulesResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PredefinedUrlCategoriesResponse(Model):
        next_link: str
        value: list[PredefinedUrlCategory]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PredefinedUrlCategory], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PredefinedUrlCategory(Model):
        action: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                action: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListGlobalRulestackResource(ProxyResource):
        audit_comment: str
        description: str
        etag: str
        id: str
        name: str
        prefix_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                prefix_list: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListGlobalRulestackResourceListResult(Model):
        next_link: str
        value: list[PrefixListGlobalRulestackResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrefixListGlobalRulestackResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListResource(ProxyResource):
        audit_comment: str
        description: str
        etag: str
        id: str
        name: str
        prefix_list: list[str]
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                audit_comment: Optional[str] = ..., 
                description: Optional[str] = ..., 
                etag: Optional[str] = ..., 
                prefix_list: list[str], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.PrefixListResourceListResult(Model):
        next_link: str
        value: list[PrefixListResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: list[PrefixListResource], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ProductSerialNumberRequestStatus(Model):
        status: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                status: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ProductSerialNumberStatus(Model):
        serial_number: str
        status: Union[str, ProductSerialStatusValues]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                serial_number: Optional[str] = ..., 
                status: Union[str, ProductSerialStatusValues], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ReadOnlyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.paloaltonetworksngfw.models.RegistrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_REGISTERED = "Not Registered"
        REGISTERED = "Registered"


    class azure.mgmt.paloaltonetworksngfw.models.Resource(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.RuleCounter(Model):
        app_seen: AppSeenData
        firewall_name: str
        hit_count: int
        last_updated_timestamp: datetime
        priority: str
        request_timestamp: datetime
        rule_list_name: str
        rule_name: str
        rule_stack_name: str
        timestamp: datetime

        def __eq__(self, other: Any) -> bool: ...

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
                timestamp: Optional[datetime] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.RuleCounterReset(Model):
        firewall_name: str
        priority: str
        rule_list_name: str
        rule_name: str
        rule_stack_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                firewall_name: Optional[str] = ..., 
                rule_list_name: Optional[str] = ..., 
                rule_name: Optional[str] = ..., 
                rule_stack_name: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.RulestackDetails(Model):
        location: str
        resource_id: str
        rulestack_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                resource_id: Optional[str] = ..., 
                rulestack_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ScopeType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "GLOBAL"
        GLOBAL_ENUM = "GLOBAL"
        LOCAL = "LOCAL"


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServices(Model):
        anti_spyware_profile: str
        anti_virus_profile: str
        dns_subscription: str
        file_blocking_profile: str
        outbound_trust_certificate: str
        outbound_un_trust_certificate: str
        url_filtering_profile: str
        vulnerability_profile: str

        def __eq__(self, other: Any) -> bool: ...

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
                vulnerability_profile: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesResponse(Model):
        next_link: str
        value: SecurityServicesTypeList

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: SecurityServicesTypeList, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANTI_SPYWARE = "antiSpyware"
        ANTI_VIRUS = "antiVirus"
        DNS_SUBSCRIPTION = "dnsSubscription"
        FILE_BLOCKING = "fileBlocking"
        IPS_VULNERABILITY = "ipsVulnerability"
        URL_FILTERING = "urlFiltering"


    class azure.mgmt.paloaltonetworksngfw.models.SecurityServicesTypeList(Model):
        entry: list[NameDescriptionObject]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                entry: list[NameDescriptionObject], 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.ServerStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DOWN = "DOWN"
        UP = "UP"


    class azure.mgmt.paloaltonetworksngfw.models.SourceAddr(Model):
        cidrs: list[str]
        countries: list[str]
        feeds: list[str]
        prefix_lists: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cidrs: Optional[list[str]] = ..., 
                countries: Optional[list[str]] = ..., 
                feeds: Optional[list[str]] = ..., 
                prefix_lists: Optional[list[str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.StateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "DISABLED"
        ENABLED = "ENABLED"


    class azure.mgmt.paloaltonetworksngfw.models.StorageAccount(Model):
        account_name: str
        id: str
        subscription_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                subscription_id: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.StrataCloudManagerConfig(Model):
        cloud_manager_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cloud_manager_name: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.StrataCloudManagerInfo(Model):
        folder_name: str
        hub_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                folder_name: Optional[str] = ..., 
                hub_url: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.SupportInfo(Model):
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

        def __eq__(self, other: Any) -> bool: ...

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
                user_registered: Optional[Union[str, BooleanEnum]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.SupportInfoModel(Model):
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

        def __eq__(self, other: Any) -> bool: ...

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
                support_url: Optional[str] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.SystemData(Model):
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.TagInfo(Model):
        key: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                key: str, 
                value: str, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.TrackedResource(Resource):
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
                tags: Optional[dict[str, str]] = ..., 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.UsageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMMITTED = "COMMITTED"
        PAYG = "PAYG"


    class azure.mgmt.paloaltonetworksngfw.models.VnetConfiguration(Model):
        ip_of_trust_subnet_for_udr: IPAddress
        trust_subnet: IPAddressSpace
        un_trust_subnet: IPAddressSpace
        vnet: IPAddressSpace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_of_trust_subnet_for_udr: Optional[IPAddress] = ..., 
                trust_subnet: IPAddressSpace, 
                un_trust_subnet: IPAddressSpace, 
                vnet: IPAddressSpace, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.paloaltonetworksngfw.models.VwanConfiguration(Model):
        ip_of_trust_subnet_for_udr: IPAddress
        network_virtual_appliance_id: str
        trust_subnet: IPAddressSpace
        un_trust_subnet: IPAddressSpace
        v_hub: IPAddressSpace

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                ip_of_trust_subnet_for_udr: Optional[IPAddress] = ..., 
                network_virtual_appliance_id: Optional[str] = ..., 
                trust_subnet: Optional[IPAddressSpace] = ..., 
                un_trust_subnet: Optional[IPAddressSpace] = ..., 
                v_hub: IPAddressSpace, 
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
                key_extractors: Optional[Callable[[str, dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


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
                email: Optional[str] = None, 
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
                type: Union[str, AdvSecurityObjectTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                global_rulestack_name: str, 
                app_id_version: Optional[str] = None, 
                app_prefix: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ListAppIdResponse: ...

        @distributed_trace
        def list_countries(
                self, 
                global_rulestack_name: str, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> PredefinedUrlCategoriesResponse: ...

        @distributed_trace
        def list_security_services(
                self, 
                global_rulestack_name: str, 
                type: Union[str, SecurityServicesTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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
                email: Optional[str] = None, 
                **kwargs: Any
            ) -> SupportInfo: ...

        @distributed_trace
        def list_advanced_security_objects(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                type: Union[str, AdvSecurityObjectTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> AdvSecurityObjectListResponse: ...

        @distributed_trace
        def list_app_ids(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                app_id_version: Optional[str] = None, 
                app_prefix: Optional[str] = None, 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
                **kwargs: Any
            ) -> ItemPaged[PredefinedUrlCategory]: ...

        @distributed_trace
        def list_security_services(
                self, 
                resource_group_name: str, 
                local_rulestack_name: str, 
                type: Union[str, SecurityServicesTypeEnum], 
                skip: Optional[str] = None, 
                top: Optional[int] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
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
                firewall_name: Optional[str] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def reset_counters(
                self, 
                global_rulestack_name: str, 
                priority: str, 
                firewall_name: Optional[str] = None, 
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


```