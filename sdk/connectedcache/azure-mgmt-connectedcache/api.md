```py
namespace azure.mgmt.connectedcache

    class azure.mgmt.connectedcache.ConnectedCacheMgmtClient: implements ContextManager 
        enterprise_mcc_cache_nodes_operations: EnterpriseMccCacheNodesOperationsOperations
        enterprise_mcc_customers: EnterpriseMccCustomersOperations
        isp_cache_nodes_operations: IspCacheNodesOperationsOperations
        isp_customers: IspCustomersOperations
        operations: Operations

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


namespace azure.mgmt.connectedcache.aio

    class azure.mgmt.connectedcache.aio.ConnectedCacheMgmtClient: implements AsyncContextManager 
        enterprise_mcc_cache_nodes_operations: EnterpriseMccCacheNodesOperationsOperations
        enterprise_mcc_customers: EnterpriseMccCustomersOperations
        isp_cache_nodes_operations: IspCacheNodesOperationsOperations
        isp_customers: IspCustomersOperations
        operations: Operations

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


namespace azure.mgmt.connectedcache.aio.operations

    class azure.mgmt.connectedcache.aio.operations.EnterpriseMccCacheNodesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: EnterpriseMccCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCacheNodeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: EnterpriseMccCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCacheNodeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCacheNodeResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        async def get_cache_node_auto_update_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeAutoUpdateHistory: ...

        @distributed_trace_async
        async def get_cache_node_install_details(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeInstallDetails: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        async def get_cache_node_mcc_issue_details_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeIssueHistory: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        async def get_cache_node_tls_certificate_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeTlsCertificateHistory: ...

        @distributed_trace
        def list_by_enterprise_mcc_customer_resource(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnterpriseMccCacheNodeResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...


    class azure.mgmt.connectedcache.aio.operations.EnterpriseMccCustomersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: EnterpriseMccCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCustomerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: EnterpriseMccCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCustomerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[EnterpriseMccCustomerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[EnterpriseMccCustomerResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[EnterpriseMccCustomerResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...


    class azure.mgmt.connectedcache.aio.operations.IspCacheNodesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IspCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCacheNodeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IspCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCacheNodeResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCacheNodeResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @distributed_trace_async
        async def get_bgp_cidrs(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeBgpCidrDetails: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        async def get_cache_node_auto_update_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeAutoUpdateHistory: ...

        @distributed_trace_async
        async def get_cache_node_install_details(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeInstallDetails: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        async def get_cache_node_mcc_issue_details_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeIssueHistory: ...

        @distributed_trace
        def list_by_isp_customer_resource(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IspCacheNodeResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...


    class azure.mgmt.connectedcache.aio.operations.IspCustomersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IspCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCustomerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IspCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCustomerResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IspCustomerResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IspCustomerResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[IspCustomerResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...


    class azure.mgmt.connectedcache.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.connectedcache.models

    class azure.mgmt.connectedcache.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.connectedcache.models.AdditionalCacheNodeProperties(_Model):
        aggregated_status_code: Optional[int]
        aggregated_status_details: Optional[str]
        aggregated_status_text: Optional[str]
        app_version_wsl: Optional[str]
        auto_update_applied_version: Optional[str]
        auto_update_last_applied_date_time: Optional[datetime]
        auto_update_last_applied_details: Optional[str]
        auto_update_last_applied_state: Optional[str]
        auto_update_last_triggered_date_time: Optional[datetime]
        auto_update_next_available_date_time: Optional[datetime]
        auto_update_next_available_version: Optional[str]
        auto_update_version: Optional[str]
        bgp_configuration: Optional[BgpConfiguration]
        cache_node_properties_details_issues_list: Optional[list[str]]
        cache_node_state: Optional[int]
        cache_node_state_detailed_text: Optional[str]
        cache_node_state_short_text: Optional[str]
        container_os_build: Optional[str]
        container_os_edition: Optional[str]
        container_os_version: Optional[str]
        creation_method: Optional[int]
        current_tls_certificate: Optional[MccCacheNodeTlsCertificate]
        distro_os_build_wsl: Optional[str]
        distro_os_edition_wsl: Optional[str]
        distro_os_version_wsl: Optional[str]
        drive_configuration: Optional[list[CacheNodeDriveConfiguration]]
        host_os_build: Optional[str]
        host_os_edition: Optional[str]
        host_os_version: Optional[str]
        install_version_msix: Optional[str]
        install_version_script: Optional[str]
        is_provisioned: Optional[bool]
        is_proxy_required: Optional[Union[str, ProxyRequired]]
        issues_count: Optional[int]
        issues_list: Optional[list[str]]
        last_auto_update_info: Optional[MccCacheNodeAutoUpdateInfo]
        optional_property1: Optional[str]
        optional_property2: Optional[str]
        optional_property3: Optional[str]
        optional_property4: Optional[str]
        optional_property5: Optional[str]
        os_type: Optional[Union[str, OsType]]
        product_version: Optional[str]
        proxy_url_configuration: Optional[ProxyUrlConfiguration]
        tls_status: Optional[str]
        update_info_details: Optional[str]
        update_requested_date_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                auto_update_version: Optional[str] = ..., 
                bgp_configuration: Optional[BgpConfiguration] = ..., 
                cache_node_properties_details_issues_list: Optional[list[str]] = ..., 
                creation_method: Optional[int] = ..., 
                drive_configuration: Optional[list[CacheNodeDriveConfiguration]] = ..., 
                is_proxy_required: Optional[Union[str, ProxyRequired]] = ..., 
                optional_property1: Optional[str] = ..., 
                optional_property2: Optional[str] = ..., 
                optional_property3: Optional[str] = ..., 
                optional_property4: Optional[str] = ..., 
                optional_property5: Optional[str] = ..., 
                os_type: Optional[Union[str, OsType]] = ..., 
                proxy_url_configuration: Optional[ProxyUrlConfiguration] = ..., 
                update_info_details: Optional[str] = ..., 
                update_requested_date_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.AdditionalCustomerProperties(_Model):
        customer_asn: Optional[str]
        customer_asn_estimated_egress_peek_gbps: Optional[float]
        customer_email: Optional[str]
        customer_entitlement_expiration: Optional[datetime]
        customer_entitlement_sku_guid: Optional[str]
        customer_entitlement_sku_id: Optional[str]
        customer_entitlement_sku_name: Optional[str]
        customer_org_name: Optional[str]
        customer_properties_overview_average_egress_mbps: Optional[float]
        customer_properties_overview_average_miss_mbps: Optional[float]
        customer_properties_overview_cache_efficiency: Optional[float]
        customer_properties_overview_cache_nodes_healthy_count: Optional[int]
        customer_properties_overview_cache_nodes_unhealthy_count: Optional[int]
        customer_properties_overview_egress_mbps_max: Optional[float]
        customer_properties_overview_egress_mbps_max_date_time: Optional[datetime]
        customer_properties_overview_miss_mbps_max: Optional[float]
        customer_properties_overview_miss_mbps_max_date_time: Optional[datetime]
        customer_transit_asn: Optional[str]
        customer_transit_state: Optional[Union[str, CustomerTransitState]]
        optional_property1: Optional[str]
        optional_property2: Optional[str]
        optional_property3: Optional[str]
        optional_property4: Optional[str]
        optional_property5: Optional[str]
        peering_db_last_update_date: Optional[datetime]
        signup_phase_status_code: Optional[int]
        signup_phase_status_text: Optional[str]
        signup_status: Optional[bool]
        signup_status_code: Optional[int]
        signup_status_text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                customer_asn: Optional[str] = ..., 
                customer_email: Optional[str] = ..., 
                customer_entitlement_expiration: Optional[datetime] = ..., 
                customer_entitlement_sku_guid: Optional[str] = ..., 
                customer_entitlement_sku_id: Optional[str] = ..., 
                customer_entitlement_sku_name: Optional[str] = ..., 
                customer_transit_asn: Optional[str] = ..., 
                customer_transit_state: Optional[Union[str, CustomerTransitState]] = ..., 
                optional_property1: Optional[str] = ..., 
                optional_property2: Optional[str] = ..., 
                optional_property3: Optional[str] = ..., 
                optional_property4: Optional[str] = ..., 
                optional_property5: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.AutoUpdateRingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BETA = "Beta"
        FAST = "Fast"
        PREVIEW = "Preview"
        SLOW = "Slow"
        STABLE = "Stable"


    class azure.mgmt.connectedcache.models.BgpCidrsConfiguration(_Model):
        bgp_cidrs: Optional[list[str]]


    class azure.mgmt.connectedcache.models.BgpConfiguration(_Model):
        asn_to_ip_address_mapping: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                asn_to_ip_address_mapping: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.BgpReviewStateEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        ATTENTION_REQUIRED = "AttentionRequired"
        IN_REVIEW = "InReview"
        NOT_CONFIGURED = "NotConfigured"


    class azure.mgmt.connectedcache.models.CacheNodeDriveConfiguration(_Model):
        cache_number: Optional[int]
        nginx_mapping: Optional[str]
        physical_path: Optional[str]
        size_in_gb: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                cache_number: Optional[int] = ..., 
                nginx_mapping: Optional[str] = ..., 
                physical_path: Optional[str] = ..., 
                size_in_gb: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CacheNodeEntity(_Model):
        address_space: Optional[int]
        auto_update_requested_day: Optional[int]
        auto_update_requested_time: Optional[str]
        auto_update_requested_week: Optional[int]
        auto_update_ring_type: Optional[Union[str, AutoUpdateRingType]]
        bgp_address_space: Optional[int]
        bgp_cidr_blocks_count: Optional[int]
        bgp_cidr_csv_last_update_time: Optional[datetime]
        bgp_file_bytes_truncated: Optional[int]
        bgp_last_reported_time: Optional[datetime]
        bgp_network_interface: Optional[str]
        bgp_number_of_records: Optional[int]
        bgp_number_of_times_updated: Optional[int]
        bgp_review_feedback: Optional[str]
        bgp_review_state: Optional[Union[str, BgpReviewStateEnum]]
        bgp_review_state_text: Optional[str]
        cache_node_id: Optional[str]
        cache_node_name: Optional[str]
        category: Optional[str]
        cidr_csv: Optional[list[str]]
        cidr_csv_last_update_time: Optional[datetime]
        cidr_selection_type: Optional[int]
        client_tenant_id: Optional[str]
        configuration_state: Optional[Union[str, ConfigurationState]]
        configuration_state_text: Optional[str]
        container_configurations: Optional[str]
        container_resync_trigger: Optional[int]
        create_async_operation_id: Optional[str]
        customer_asn: Optional[int]
        customer_id: Optional[str]
        customer_index: Optional[str]
        customer_name: Optional[str]
        delete_async_operation_id: Optional[str]
        fully_qualified_domain_name: Optional[str]
        fully_qualified_resource_id: Optional[str]
        image_uri: Optional[str]
        ip_address: Optional[str]
        is_enabled: Optional[bool]
        is_enterprise_managed: Optional[bool]
        is_frozen: Optional[bool]
        last_sync_with_azure_timestamp: Optional[datetime]
        last_updated_timestamp: Optional[datetime]
        max_allowable_egress_in_mbps: Optional[int]
        max_allowable_probability: Optional[float]
        open_firewall_port443: Optional[bool]
        open_firewall_port5000: Optional[bool]
        open_firewall_port5001: Optional[bool]
        open_firewall_port80: Optional[bool]
        release_version: Optional[int]
        review_feedback: Optional[str]
        review_state: Optional[int]
        review_state_text: Optional[str]
        runtime_account_type: Optional[str]
        should_migrate: Optional[bool]
        synch_with_azure_attempts_count: Optional[int]
        worker_connections: Optional[int]
        worker_connections_last_updated_date_time: Optional[datetime]
        x_cid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_update_requested_day: Optional[int] = ..., 
                auto_update_requested_time: Optional[str] = ..., 
                auto_update_requested_week: Optional[int] = ..., 
                auto_update_ring_type: Optional[Union[str, AutoUpdateRingType]] = ..., 
                bgp_network_interface: Optional[str] = ..., 
                cache_node_id: Optional[str] = ..., 
                cache_node_name: Optional[str] = ..., 
                cidr_csv: Optional[list[str]] = ..., 
                cidr_selection_type: Optional[int] = ..., 
                customer_asn: Optional[int] = ..., 
                customer_index: Optional[str] = ..., 
                customer_name: Optional[str] = ..., 
                fully_qualified_domain_name: Optional[str] = ..., 
                fully_qualified_resource_id: Optional[str] = ..., 
                ip_address: Optional[str] = ..., 
                is_enabled: Optional[bool] = ..., 
                is_enterprise_managed: Optional[bool] = ..., 
                max_allowable_egress_in_mbps: Optional[int] = ..., 
                open_firewall_port443: Optional[bool] = ..., 
                open_firewall_port5000: Optional[bool] = ..., 
                open_firewall_port5001: Optional[bool] = ..., 
                open_firewall_port80: Optional[bool] = ..., 
                runtime_account_type: Optional[str] = ..., 
                should_migrate: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CacheNodeInstallProperties(_Model):
        cache_node_id: Optional[str]
        customer_id: Optional[str]
        drive_configuration: Optional[list[CacheNodeDriveConfiguration]]
        primary_account_key: Optional[str]
        proxy_url_configuration: Optional[ProxyUrlConfiguration]
        registration_key: Optional[str]
        secondary_account_key: Optional[str]
        tls_certificate_provisioning_key: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cache_node_id: Optional[str] = ..., 
                customer_id: Optional[str] = ..., 
                drive_configuration: Optional[list[CacheNodeDriveConfiguration]] = ..., 
                proxy_url_configuration: Optional[ProxyUrlConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CacheNodeProperty(_Model):
        additional_cache_node_properties: Optional[AdditionalCacheNodeProperties]
        cache_node: Optional[CacheNodeEntity]
        error: Optional[ErrorDetail]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]
        status_code: Optional[str]
        status_details: Optional[str]
        status_text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_cache_node_properties: Optional[AdditionalCacheNodeProperties] = ..., 
                cache_node: Optional[CacheNodeEntity] = ..., 
                error: Optional[ErrorDetail] = ..., 
                status_code: Optional[str] = ..., 
                status_details: Optional[str] = ..., 
                status_text: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.ConfigurationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONFIGURED = "Configured"
        NOT_CONFIGURED_IP = "NotConfigured_Ip"


    class azure.mgmt.connectedcache.models.ConnectedCachePatchResource(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.connectedcache.models.CustomerEntity(_Model):
        client_tenant_id: Optional[str]
        contact_email: Optional[str]
        contact_name: Optional[str]
        contact_phone: Optional[str]
        create_async_operation_id: Optional[str]
        customer_id: Optional[str]
        customer_name: Optional[str]
        delete_async_operation_id: Optional[str]
        fully_qualified_resource_id: Optional[str]
        is_enterprise_managed: Optional[bool]
        is_entitled: Optional[bool]
        last_sync_with_azure_timestamp: Optional[datetime]
        release_version: Optional[int]
        resend_signup_code: Optional[bool]
        should_migrate: Optional[bool]
        synch_with_azure_attempts_count: Optional[int]
        verify_signup_code: Optional[bool]
        verify_signup_phrase: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                client_tenant_id: Optional[str] = ..., 
                contact_email: Optional[str] = ..., 
                contact_name: Optional[str] = ..., 
                contact_phone: Optional[str] = ..., 
                customer_name: Optional[str] = ..., 
                fully_qualified_resource_id: Optional[str] = ..., 
                is_enterprise_managed: Optional[bool] = ..., 
                is_entitled: Optional[bool] = ..., 
                release_version: Optional[int] = ..., 
                resend_signup_code: Optional[bool] = ..., 
                should_migrate: Optional[bool] = ..., 
                verify_signup_code: Optional[bool] = ..., 
                verify_signup_phrase: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CustomerProperty(_Model):
        additional_customer_properties: Optional[AdditionalCustomerProperties]
        customer: Optional[CustomerEntity]
        error: Optional[ErrorDetail]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[str]
        status_code: Optional[str]
        status_details: Optional[str]
        status_text: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_customer_properties: Optional[AdditionalCustomerProperties] = ..., 
                customer: Optional[CustomerEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.CustomerTransitState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMBINED_TRANSIT = "CombinedTransit"
        NO_TRANSIT = "NoTransit"
        TRANSIT_ONLY = "TransitOnly"


    class azure.mgmt.connectedcache.models.EnterpriseMccCacheNodeResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CacheNodeProperty]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CacheNodeProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.EnterpriseMccCustomerResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CustomerProperty]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CustomerProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.connectedcache.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.connectedcache.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.IspCacheNodeResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CacheNodeProperty]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CacheNodeProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.IspCustomerResource(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CustomerProperty]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CustomerProperty] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeAutoUpdateHistory(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MccCacheNodeAutoUpdateHistoryProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MccCacheNodeAutoUpdateHistoryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeAutoUpdateHistoryProperties(_Model):
        auto_update_history: Optional[list[MccCacheNodeAutoUpdateInfo]]
        cache_node_id: Optional[str]
        customer_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                auto_update_history: Optional[list[MccCacheNodeAutoUpdateInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeAutoUpdateInfo(_Model):
        auto_update_last_applied_status: Optional[int]
        auto_update_last_applied_status_detailed_text: Optional[str]
        auto_update_last_applied_status_text: Optional[str]
        auto_update_ring_type: Optional[int]
        created_date_time_utc: Optional[datetime]
        image_uri_before_update: Optional[str]
        image_uri_targeted: Optional[str]
        image_uri_terminal: Optional[str]
        moved_to_terminal_state_date_time: Optional[datetime]
        plan_change_log_text: Optional[str]
        plan_id: Optional[int]
        rule_requested_day: Optional[int]
        rule_requested_hour: Optional[str]
        rule_requested_minute: Optional[str]
        rule_requested_week: Optional[int]
        time_to_go_live_date_time: Optional[str]
        updated_registry_date_time_utc: Optional[datetime]


    class azure.mgmt.connectedcache.models.MccCacheNodeBgpCidrDetails(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[BgpCidrsConfiguration]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[BgpCidrsConfiguration] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeInstallDetails(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CacheNodeInstallProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CacheNodeInstallProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeIssueHistory(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MccCacheNodeIssueHistoryProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MccCacheNodeIssueHistoryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeIssueHistoryProperties(_Model):
        cache_node_id: Optional[str]
        customer_id: Optional[str]
        mcc_issue_history: Optional[list[MccIssue]]

        @overload
        def __init__(
                self, 
                *, 
                mcc_issue_history: Optional[list[MccIssue]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeTlsCertificate(_Model):
        action_required: Optional[str]
        cert_type: Optional[str]
        certificate_file_name: Optional[str]
        expiry_date: Optional[datetime]
        not_before_date: Optional[datetime]
        subject: Optional[str]
        subject_alt_name: Optional[str]
        thumbprint: Optional[str]


    class azure.mgmt.connectedcache.models.MccCacheNodeTlsCertificateHistory(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[MccCacheNodeTlsCertificateProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[MccCacheNodeTlsCertificateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccCacheNodeTlsCertificateProperties(_Model):
        cache_node_id: Optional[str]
        customer_id: Optional[str]
        tls_certificate_history: Optional[list[MccCacheNodeTlsCertificate]]

        @overload
        def __init__(
                self, 
                *, 
                tls_certificate_history: Optional[list[MccCacheNodeTlsCertificate]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.MccIssue(_Model):
        detail_string: Optional[str]
        help_link: Optional[str]
        issue_end_date: Optional[datetime]
        issue_start_date: Optional[datetime]
        mcc_issue_type: Optional[str]
        toast_string: Optional[str]


    class azure.mgmt.connectedcache.models.Operation(_Model):
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


    class azure.mgmt.connectedcache.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.connectedcache.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.connectedcache.models.OsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EFLOW = "Eflow"
        LINUX = "Linux"
        WINDOWS = "Windows"


    class azure.mgmt.connectedcache.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"
        UPGRADING = "Upgrading"


    class azure.mgmt.connectedcache.models.ProxyRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REQUIRED = "Required"


    class azure.mgmt.connectedcache.models.ProxyUrlConfiguration(_Model):
        proxy_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                proxy_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.connectedcache.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.connectedcache.models.SystemData(_Model):
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


    class azure.mgmt.connectedcache.models.TrackedResource(Resource):
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


namespace azure.mgmt.connectedcache.operations

    class azure.mgmt.connectedcache.operations.EnterpriseMccCacheNodesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: EnterpriseMccCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCacheNodeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: EnterpriseMccCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCacheNodeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCacheNodeResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        def get_cache_node_auto_update_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeAutoUpdateHistory: ...

        @distributed_trace
        def get_cache_node_install_details(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeInstallDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        def get_cache_node_mcc_issue_details_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeIssueHistory: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        def get_cache_node_tls_certificate_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeTlsCertificateHistory: ...

        @distributed_trace
        def list_by_enterprise_mcc_customer_resource(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnterpriseMccCacheNodeResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCacheNodeResource: ...


    class azure.mgmt.connectedcache.operations.EnterpriseMccCustomersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: EnterpriseMccCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCustomerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: EnterpriseMccCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCustomerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[EnterpriseMccCustomerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[EnterpriseMccCustomerResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[EnterpriseMccCustomerResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> EnterpriseMccCustomerResource: ...


    class azure.mgmt.connectedcache.operations.IspCacheNodesOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IspCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCacheNodeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IspCacheNodeResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCacheNodeResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCacheNodeResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @distributed_trace
        def get_bgp_cidrs(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeBgpCidrDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        def get_cache_node_auto_update_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeAutoUpdateHistory: ...

        @distributed_trace
        def get_cache_node_install_details(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeInstallDetails: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-11-30-preview', params_added_on={'2024-11-30-preview': ['api_version', 'subscription_id', 'resource_group_name', 'customer_resource_name', 'cache_node_resource_name', 'accept']}, api_versions_list=['2024-11-30-preview', '2026-06-01'])
        def get_cache_node_mcc_issue_details_history(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                **kwargs: Any
            ) -> MccCacheNodeIssueHistory: ...

        @distributed_trace
        def list_by_isp_customer_resource(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IspCacheNodeResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                cache_node_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCacheNodeResource: ...


    class azure.mgmt.connectedcache.operations.IspCustomersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IspCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCustomerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IspCustomerResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCustomerResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IspCustomerResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IspCustomerResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[IspCustomerResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: ConnectedCachePatchResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                customer_resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> IspCustomerResource: ...


    class azure.mgmt.connectedcache.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


namespace azure.mgmt.connectedcache.types

    class azure.mgmt.connectedcache.types.AdditionalCacheNodeProperties(TypedDict, total=False):
        key "aggregatedStatusCode": int
        key "aggregatedStatusDetails": str
        key "aggregatedStatusText": str
        key "appVersionWsl": str
        key "autoUpdateAppliedVersion": str
        key "autoUpdateLastAppliedDateTime": str
        key "autoUpdateLastAppliedDetails": str
        key "autoUpdateLastAppliedState": str
        key "autoUpdateLastTriggeredDateTime": str
        key "autoUpdateNextAvailableDateTime": str
        key "autoUpdateNextAvailableVersion": str
        key "autoUpdateVersion": str
        key "bgpConfiguration": ForwardRef('BgpConfiguration', module='types')
        key "cacheNodeState": int
        key "cacheNodeStateDetailedText": str
        key "cacheNodeStateShortText": str
        key "containerOsBuild": str
        key "containerOsEdition": str
        key "containerOsVersion": str
        key "creationMethod": int
        key "currentTlsCertificate": ForwardRef('MccCacheNodeTlsCertificate', module='types')
        key "distroOsBuildWsl": str
        key "distroOsEditionWsl": str
        key "distroOsVersionWsl": str
        key "hostOsBuild": str
        key "hostOsEdition": str
        key "hostOsVersion": str
        key "installVersionMsix": str
        key "installVersionScript": str
        key "isProvisioned": bool
        key "isProxyRequired": Union[str, ProxyRequired]
        key "issuesCount": int
        key "lastAutoUpdateInfo": ForwardRef('MccCacheNodeAutoUpdateInfo', module='types')
        key "optionalProperty1": str
        key "optionalProperty2": str
        key "optionalProperty3": str
        key "optionalProperty4": str
        key "optionalProperty5": str
        key "osType": Union[str, OsType]
        key "productVersion": str
        key "proxyUrlConfiguration": ForwardRef('ProxyUrlConfiguration', module='types')
        key "tlsStatus": str
        key "updateInfoDetails": str
        key "updateRequestedDateTime": str
        aggregated_status_code: int
        aggregated_status_details: str
        aggregated_status_text: str
        app_version_wsl: str
        auto_update_applied_version: str
        auto_update_last_applied_date_time: str
        auto_update_last_applied_details: str
        auto_update_last_applied_state: str
        auto_update_last_triggered_date_time: str
        auto_update_next_available_date_time: str
        auto_update_next_available_version: str
        auto_update_version: str
        bgp_configuration: BgpConfiguration
        cacheNodePropertiesDetailsIssuesList: list[str]
        cache_node_properties_details_issues_list: list[str]
        cache_node_state: int
        cache_node_state_detailed_text: str
        cache_node_state_short_text: str
        container_os_build: str
        container_os_edition: str
        container_os_version: str
        creation_method: int
        current_tls_certificate: MccCacheNodeTlsCertificate
        distro_os_build_wsl: str
        distro_os_edition_wsl: str
        distro_os_version_wsl: str
        driveConfiguration: list[CacheNodeDriveConfiguration]
        drive_configuration: list[CacheNodeDriveConfiguration]
        host_os_build: str
        host_os_edition: str
        host_os_version: str
        install_version_msix: str
        install_version_script: str
        is_provisioned: bool
        is_proxy_required: Union[str, ProxyRequired]
        issuesList: list[str]
        issues_count: int
        issues_list: list[str]
        last_auto_update_info: MccCacheNodeAutoUpdateInfo
        optional_property1: str
        optional_property2: str
        optional_property3: str
        optional_property4: str
        optional_property5: str
        os_type: Union[str, OsType]
        product_version: str
        proxy_url_configuration: ProxyUrlConfiguration
        tls_status: str
        update_info_details: str
        update_requested_date_time: str


    class azure.mgmt.connectedcache.types.AdditionalCustomerProperties(TypedDict, total=False):
        key "customerAsn": str
        key "customerAsnEstimatedEgressPeekGbps": float
        key "customerEmail": str
        key "customerEntitlementExpiration": str
        key "customerEntitlementSkuGuid": str
        key "customerEntitlementSkuId": str
        key "customerEntitlementSkuName": str
        key "customerOrgName": str
        key "customerPropertiesOverviewAverageEgressMbps": float
        key "customerPropertiesOverviewAverageMissMbps": float
        key "customerPropertiesOverviewCacheEfficiency": float
        key "customerPropertiesOverviewCacheNodesHealthyCount": int
        key "customerPropertiesOverviewCacheNodesUnhealthyCount": int
        key "customerPropertiesOverviewEgressMbpsMax": float
        key "customerPropertiesOverviewEgressMbpsMaxDateTime": str
        key "customerPropertiesOverviewMissMbpsMax": float
        key "customerPropertiesOverviewMissMbpsMaxDateTime": str
        key "customerTransitAsn": str
        key "customerTransitState": Union[str, CustomerTransitState]
        key "optionalProperty1": str
        key "optionalProperty2": str
        key "optionalProperty3": str
        key "optionalProperty4": str
        key "optionalProperty5": str
        key "peeringDbLastUpdateDate": str
        key "signupPhaseStatusCode": int
        key "signupPhaseStatusText": str
        key "signupStatus": bool
        key "signupStatusCode": int
        key "signupStatusText": str
        customer_asn: str
        customer_asn_estimated_egress_peek_gbps: float
        customer_email: str
        customer_entitlement_expiration: str
        customer_entitlement_sku_guid: str
        customer_entitlement_sku_id: str
        customer_entitlement_sku_name: str
        customer_org_name: str
        customer_properties_overview_average_egress_mbps: float
        customer_properties_overview_average_miss_mbps: float
        customer_properties_overview_cache_efficiency: float
        customer_properties_overview_cache_nodes_healthy_count: int
        customer_properties_overview_cache_nodes_unhealthy_count: int
        customer_properties_overview_egress_mbps_max: float
        customer_properties_overview_egress_mbps_max_date_time: str
        customer_properties_overview_miss_mbps_max: float
        customer_properties_overview_miss_mbps_max_date_time: str
        customer_transit_asn: str
        customer_transit_state: Union[str, CustomerTransitState]
        optional_property1: str
        optional_property2: str
        optional_property3: str
        optional_property4: str
        optional_property5: str
        peering_db_last_update_date: str
        signup_phase_status_code: int
        signup_phase_status_text: str
        signup_status: bool
        signup_status_code: int
        signup_status_text: str


    class azure.mgmt.connectedcache.types.BgpConfiguration(TypedDict, total=False):
        key "asnToIpAddressMapping": str
        asn_to_ip_address_mapping: str


    class azure.mgmt.connectedcache.types.CacheNodeDriveConfiguration(TypedDict, total=False):
        key "cacheNumber": int
        key "nginxMapping": str
        key "physicalPath": str
        key "sizeInGb": int
        cache_number: int
        nginx_mapping: str
        physical_path: str
        size_in_gb: int


    class azure.mgmt.connectedcache.types.CacheNodeEntity(TypedDict, total=False):
        key "addressSpace": int
        key "autoUpdateRequestedDay": int
        key "autoUpdateRequestedTime": str
        key "autoUpdateRequestedWeek": int
        key "autoUpdateRingType": Union[str, AutoUpdateRingType]
        key "bgpAddressSpace": int
        key "bgpCidrBlocksCount": int
        key "bgpCidrCsvLastUpdateTime": str
        key "bgpFileBytesTruncated": int
        key "bgpLastReportedTime": str
        key "bgpNetworkInterface": str
        key "bgpNumberOfRecords": int
        key "bgpNumberOfTimesUpdated": int
        key "bgpReviewFeedback": str
        key "bgpReviewState": Union[str, BgpReviewStateEnum]
        key "bgpReviewStateText": str
        key "cacheNodeId": str
        key "cacheNodeName": str
        key "category": str
        key "cidrCsvLastUpdateTime": str
        key "cidrSelectionType": int
        key "clientTenantId": str
        key "configurationState": Union[str, ConfigurationState]
        key "configurationStateText": str
        key "containerConfigurations": str
        key "containerResyncTrigger": int
        key "createAsyncOperationId": str
        key "customerAsn": int
        key "customerId": str
        key "customerIndex": str
        key "customerName": str
        key "deleteAsyncOperationId": str
        key "fullyQualifiedDomainName": str
        key "fullyQualifiedResourceId": str
        key "imageUri": str
        key "ipAddress": str
        key "isEnabled": bool
        key "isEnterpriseManaged": bool
        key "isFrozen": bool
        key "lastSyncWithAzureTimestamp": str
        key "lastUpdatedTimestamp": str
        key "maxAllowableEgressInMbps": int
        key "maxAllowableProbability": float
        key "openFirewallPort443": bool
        key "openFirewallPort5000": bool
        key "openFirewallPort5001": bool
        key "openFirewallPort80": bool
        key "releaseVersion": int
        key "reviewFeedback": str
        key "reviewState": int
        key "reviewStateText": str
        key "runtimeAccountType": str
        key "shouldMigrate": bool
        key "synchWithAzureAttemptsCount": int
        key "workerConnections": int
        key "workerConnectionsLastUpdatedDateTime": str
        key "xCid": str
        address_space: int
        auto_update_requested_day: int
        auto_update_requested_time: str
        auto_update_requested_week: int
        auto_update_ring_type: Union[str, AutoUpdateRingType]
        bgp_address_space: int
        bgp_cidr_blocks_count: int
        bgp_cidr_csv_last_update_time: str
        bgp_file_bytes_truncated: int
        bgp_last_reported_time: str
        bgp_network_interface: str
        bgp_number_of_records: int
        bgp_number_of_times_updated: int
        bgp_review_feedback: str
        bgp_review_state: Union[str, BgpReviewStateEnum]
        bgp_review_state_text: str
        cache_node_id: str
        cache_node_name: str
        category: str
        cidrCsv: list[str]
        cidr_csv: list[str]
        cidr_csv_last_update_time: str
        cidr_selection_type: int
        client_tenant_id: str
        configuration_state: Union[str, ConfigurationState]
        configuration_state_text: str
        container_configurations: str
        container_resync_trigger: int
        create_async_operation_id: str
        customer_asn: int
        customer_id: str
        customer_index: str
        customer_name: str
        delete_async_operation_id: str
        fully_qualified_domain_name: str
        fully_qualified_resource_id: str
        image_uri: str
        ip_address: str
        is_enabled: bool
        is_enterprise_managed: bool
        is_frozen: bool
        last_sync_with_azure_timestamp: str
        last_updated_timestamp: str
        max_allowable_egress_in_mbps: int
        max_allowable_probability: float
        open_firewall_port443: bool
        open_firewall_port5000: bool
        open_firewall_port5001: bool
        open_firewall_port80: bool
        release_version: int
        review_feedback: str
        review_state: int
        review_state_text: str
        runtime_account_type: str
        should_migrate: bool
        synch_with_azure_attempts_count: int
        worker_connections: int
        worker_connections_last_updated_date_time: str
        x_cid: str


    class azure.mgmt.connectedcache.types.CacheNodeProperty(TypedDict, total=False):
        key "additionalCacheNodeProperties": ForwardRef('AdditionalCacheNodeProperties', module='types')
        key "cacheNode": ForwardRef('CacheNodeEntity', module='types')
        key "error": ForwardRef('ErrorDetail', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "status": str
        key "statusCode": str
        key "statusDetails": str
        key "statusText": str
        additional_cache_node_properties: AdditionalCacheNodeProperties
        cache_node: CacheNodeEntity
        error: ErrorDetail
        provisioning_state: Union[str, ProvisioningState]
        status: str
        status_code: str
        status_details: str
        status_text: str


    class azure.mgmt.connectedcache.types.ConnectedCachePatchResource(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.connectedcache.types.CustomerEntity(TypedDict, total=False):
        key "clientTenantId": str
        key "contactEmail": str
        key "contactName": str
        key "contactPhone": str
        key "createAsyncOperationId": str
        key "customerId": str
        key "customerName": str
        key "deleteAsyncOperationId": str
        key "fullyQualifiedResourceId": str
        key "isEnterpriseManaged": bool
        key "isEntitled": bool
        key "lastSyncWithAzureTimestamp": str
        key "releaseVersion": int
        key "resendSignupCode": bool
        key "shouldMigrate": bool
        key "synchWithAzureAttemptsCount": int
        key "verifySignupCode": bool
        key "verifySignupPhrase": str
        client_tenant_id: str
        contact_email: str
        contact_name: str
        contact_phone: str
        create_async_operation_id: str
        customer_id: str
        customer_name: str
        delete_async_operation_id: str
        fully_qualified_resource_id: str
        is_enterprise_managed: bool
        is_entitled: bool
        last_sync_with_azure_timestamp: str
        release_version: int
        resend_signup_code: bool
        should_migrate: bool
        synch_with_azure_attempts_count: int
        verify_signup_code: bool
        verify_signup_phrase: str


    class azure.mgmt.connectedcache.types.CustomerProperty(TypedDict, total=False):
        key "additionalCustomerProperties": ForwardRef('AdditionalCustomerProperties', module='types')
        key "customer": ForwardRef('CustomerEntity', module='types')
        key "error": ForwardRef('ErrorDetail', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "status": str
        key "statusCode": str
        key "statusDetails": str
        key "statusText": str
        additional_customer_properties: AdditionalCustomerProperties
        customer: CustomerEntity
        error: ErrorDetail
        provisioning_state: Union[str, ProvisioningState]
        status: str
        status_code: str
        status_details: str
        status_text: str


    class azure.mgmt.connectedcache.types.EnterpriseMccCacheNodeResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CacheNodeProperty', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CacheNodeProperty
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.connectedcache.types.EnterpriseMccCustomerResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CustomerProperty', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CustomerProperty
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.connectedcache.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.connectedcache.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.connectedcache.types.IspCacheNodeResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CacheNodeProperty', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CacheNodeProperty
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.connectedcache.types.IspCustomerResource(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CustomerProperty', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CustomerProperty
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.connectedcache.types.MccCacheNodeAutoUpdateInfo(TypedDict, total=False):
        key "autoUpdateLastAppliedStatus": int
        key "autoUpdateLastAppliedStatusDetailedText": str
        key "autoUpdateLastAppliedStatusText": str
        key "autoUpdateRingType": int
        key "createdDateTimeUtc": str
        key "imageUriBeforeUpdate": str
        key "imageUriTargeted": str
        key "imageUriTerminal": str
        key "movedToTerminalStateDateTime": str
        key "planChangeLogText": str
        key "planId": int
        key "ruleRequestedDay": int
        key "ruleRequestedHour": str
        key "ruleRequestedMinute": str
        key "ruleRequestedWeek": int
        key "timeToGoLiveDateTime": str
        key "updatedRegistryDateTimeUtc": str
        auto_update_last_applied_status: int
        auto_update_last_applied_status_detailed_text: str
        auto_update_last_applied_status_text: str
        auto_update_ring_type: int
        created_date_time_utc: str
        image_uri_before_update: str
        image_uri_targeted: str
        image_uri_terminal: str
        moved_to_terminal_state_date_time: str
        plan_change_log_text: str
        plan_id: int
        rule_requested_day: int
        rule_requested_hour: str
        rule_requested_minute: str
        rule_requested_week: int
        time_to_go_live_date_time: str
        updated_registry_date_time_utc: str


    class azure.mgmt.connectedcache.types.MccCacheNodeTlsCertificate(TypedDict, total=False):
        key "actionRequired": str
        key "certType": str
        key "certificateFileName": str
        key "expiryDate": str
        key "notBeforeDate": str
        key "subject": str
        key "subjectAltName": str
        key "thumbprint": str
        action_required: str
        cert_type: str
        certificate_file_name: str
        expiry_date: str
        not_before_date: str
        subject: str
        subject_alt_name: str
        thumbprint: str


    class azure.mgmt.connectedcache.types.ProxyUrlConfiguration(TypedDict, total=False):
        key "proxyUrl": str
        proxy_url: str


    class azure.mgmt.connectedcache.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.connectedcache.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.connectedcache.types.TrackedResource(Resource):
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


```