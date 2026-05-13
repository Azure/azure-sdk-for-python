```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.avs

    class azure.mgmt.avs.AVSClient: implements ContextManager 
        addons: AddonsOperations
        authorizations: AuthorizationsOperations
        cloud_links: CloudLinksOperations
        clusters: ClustersOperations
        datastores: DatastoresOperations
        global_reach_connections: GlobalReachConnectionsOperations
        hcx_enterprise_sites: HcxEnterpriseSitesOperations
        hosts: HostsOperations
        iscsi_paths: IscsiPathsOperations
        licenses: LicensesOperations
        locations: LocationsOperations
        maintenances: MaintenancesOperations
        operations: Operations
        placement_policies: PlacementPoliciesOperations
        private_clouds: PrivateCloudsOperations
        provisioned_networks: ProvisionedNetworksOperations
        pure_storage_policies: PureStoragePoliciesOperations
        script_cmdlets: ScriptCmdletsOperations
        script_executions: ScriptExecutionsOperations
        script_packages: ScriptPackagesOperations
        skus: SkusOperations
        virtual_machines: VirtualMachinesOperations
        workload_networks: WorkloadNetworksOperations

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


namespace azure.mgmt.avs.aio

    class azure.mgmt.avs.aio.AVSClient: implements AsyncContextManager 
        addons: AddonsOperations
        authorizations: AuthorizationsOperations
        cloud_links: CloudLinksOperations
        clusters: ClustersOperations
        datastores: DatastoresOperations
        global_reach_connections: GlobalReachConnectionsOperations
        hcx_enterprise_sites: HcxEnterpriseSitesOperations
        hosts: HostsOperations
        iscsi_paths: IscsiPathsOperations
        licenses: LicensesOperations
        locations: LocationsOperations
        maintenances: MaintenancesOperations
        operations: Operations
        placement_policies: PlacementPoliciesOperations
        private_clouds: PrivateCloudsOperations
        provisioned_networks: ProvisionedNetworksOperations
        pure_storage_policies: PureStoragePoliciesOperations
        script_cmdlets: ScriptCmdletsOperations
        script_executions: ScriptExecutionsOperations
        script_packages: ScriptPackagesOperations
        skus: SkusOperations
        virtual_machines: VirtualMachinesOperations
        workload_networks: WorkloadNetworksOperations

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


namespace azure.mgmt.avs.aio.operations

    class azure.mgmt.avs.aio.operations.AddonsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: Addon, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Addon]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Addon]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Addon]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                **kwargs: Any
            ) -> Addon: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Addon]: ...


    class azure.mgmt.avs.aio.operations.AuthorizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: ExpressRouteAuthorization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpressRouteAuthorization]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpressRouteAuthorization]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ExpressRouteAuthorization]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> ExpressRouteAuthorization: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ExpressRouteAuthorization]: ...


    class azure.mgmt.avs.aio.operations.CloudLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: CloudLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CloudLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                **kwargs: Any
            ) -> CloudLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CloudLink]: ...


    class azure.mgmt.avs.aio.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: ClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Cluster]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Cluster]: ...

        @distributed_trace_async
        async def list_zones(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterZoneList: ...


    class azure.mgmt.avs.aio.operations.DatastoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: Datastore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Datastore]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Datastore]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Datastore]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Datastore]: ...


    class azure.mgmt.avs.aio.operations.GlobalReachConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: GlobalReachConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalReachConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalReachConnection]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GlobalReachConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                **kwargs: Any
            ) -> GlobalReachConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[GlobalReachConnection]: ...


    class azure.mgmt.avs.aio.operations.HcxEnterpriseSitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: HcxEnterpriseSite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[HcxEnterpriseSite]: ...


    class azure.mgmt.avs.aio.operations.HostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'cluster_name', 'host_id', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                host_id: str, 
                **kwargs: Any
            ) -> Host: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'cluster_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Host]: ...


    class azure.mgmt.avs.aio.operations.IscsiPathsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: IscsiPath, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IscsiPath]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IscsiPath]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[IscsiPath]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> IscsiPath: ...

        @distributed_trace
        def list_by_private_cloud(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[IscsiPath]: ...


    class azure.mgmt.avs.aio.operations.LicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[License]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name']}, api_versions_list=['2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name', 'accept']}, api_versions_list=['2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> License: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name', 'accept']}, api_versions_list=['2025-09-01'])
        async def get_properties(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> LicenseProperties: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[License]: ...


    class azure.mgmt.avs.aio.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def check_quota_availability(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Quota: ...

        @overload
        async def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[Sku] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...

        @overload
        async def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...

        @overload
        async def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...


    class azure.mgmt.avs.aio.operations.MaintenancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'maintenance_name', 'accept']}, api_versions_list=['2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'maintenance_name', 'accept']}, api_versions_list=['2025-09-01'])
        async def initiate_checks(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'state_name', 'status', 'from_parameter', 'to', 'accept']}, api_versions_list=['2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                *, 
                from_parameter: Optional[datetime] = ..., 
                state_name: Optional[Union[str, MaintenanceStateName]] = ..., 
                status: Optional[Union[str, MaintenanceStatusFilter]] = ..., 
                to: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Maintenance]: ...

        @overload
        async def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: MaintenanceReschedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        async def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        async def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        async def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: MaintenanceSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        async def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        async def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...


    class azure.mgmt.avs.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.avs.aio.operations.PlacementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: PlacementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: PlacementPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PlacementPolicy]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                **kwargs: Any
            ) -> PlacementPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PlacementPolicy]: ...


    class azure.mgmt.avs.aio.operations.PrivateCloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: PrivateCloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_rotate_nsxt_password(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_rotate_vcenter_password(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: PrivateCloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateCloud]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> PrivateCloud: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2025-09-01'])
        async def get_vcf_license(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> VcfLicense: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateCloud]: ...

        @distributed_trace_async
        async def list_admin_credentials(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AdminCredentials: ...

        @distributed_trace
        def list_in_subscription(self, **kwargs: Any) -> AsyncItemPaged[PrivateCloud]: ...


    class azure.mgmt.avs.aio.operations.ProvisionedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'provisioned_network_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                provisioned_network_name: str, 
                **kwargs: Any
            ) -> ProvisionedNetwork: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProvisionedNetwork]: ...


    class azure.mgmt.avs.aio.operations.PureStoragePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: PureStoragePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PureStoragePolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PureStoragePolicy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PureStoragePolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'storage_policy_name']}, api_versions_list=['2024-09-01', '2025-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'storage_policy_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                **kwargs: Any
            ) -> PureStoragePolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PureStoragePolicy]: ...


    class azure.mgmt.avs.aio.operations.ScriptCmdletsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                script_cmdlet_name: str, 
                **kwargs: Any
            ) -> ScriptCmdlet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScriptCmdlet]: ...


    class azure.mgmt.avs.aio.operations.ScriptExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: ScriptExecution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScriptExecution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScriptExecution]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ScriptExecution]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @overload
        async def get_execution_logs(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_output_stream_type: Optional[List[Union[str, ScriptOutputStreamType]]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @overload
        async def get_execution_logs(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_output_stream_type: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScriptExecution]: ...


    class azure.mgmt.avs.aio.operations.ScriptPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                **kwargs: Any
            ) -> ScriptPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ScriptPackage]: ...


    class azure.mgmt.avs.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(self, **kwargs: Any) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.avs.aio.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: VirtualMachineRestrictMovement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VirtualMachine]: ...


    class azure.mgmt.avs.aio.operations.WorkloadNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: WorkloadNetworkDhcp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: WorkloadNetworkDnsService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: WorkloadNetworkDnsZone, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: WorkloadNetworkPortMirroring, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: WorkloadNetworkPublicIP, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        async def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        async def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        async def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: WorkloadNetworkSegment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: WorkloadNetworkVMGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        async def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        async def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @distributed_trace_async
        async def begin_delete_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_dns_service(
                self, 
                resource_group_name: str, 
                dns_service_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_dns_zone(
                self, 
                resource_group_name: str, 
                dns_zone_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_port_mirroring(
                self, 
                resource_group_name: str, 
                port_mirroring_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_public_ip(
                self, 
                resource_group_name: str, 
                public_ip_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_segment(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete_vm_group(
                self, 
                resource_group_name: str, 
                vm_group_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: WorkloadNetworkDhcp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDhcp]: ...

        @overload
        async def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: WorkloadNetworkDnsService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsService]: ...

        @overload
        async def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: WorkloadNetworkDnsZone, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        async def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: WorkloadNetworkPortMirroring, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        async def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: WorkloadNetworkSegment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkSegment]: ...

        @overload
        async def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: WorkloadNetworkVMGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        async def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        async def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[WorkloadNetworkVMGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> WorkloadNetwork: ...

        @distributed_trace_async
        async def get_dhcp(
                self, 
                resource_group_name: str, 
                dhcp_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDhcp: ...

        @distributed_trace_async
        async def get_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDnsService: ...

        @distributed_trace_async
        async def get_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDnsZone: ...

        @distributed_trace_async
        async def get_gateway(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                gateway_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkGateway: ...

        @distributed_trace_async
        async def get_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkPortMirroring: ...

        @distributed_trace_async
        async def get_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkPublicIP: ...

        @distributed_trace_async
        async def get_segment(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkSegment: ...

        @distributed_trace_async
        async def get_virtual_machine(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                virtual_machine_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkVirtualMachine: ...

        @distributed_trace_async
        async def get_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkVMGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetwork]: ...

        @distributed_trace
        def list_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkDhcp]: ...

        @distributed_trace
        def list_dns_services(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkDnsService]: ...

        @distributed_trace
        def list_dns_zones(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkDnsZone]: ...

        @distributed_trace
        def list_gateways(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkGateway]: ...

        @distributed_trace
        def list_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkPortMirroring]: ...

        @distributed_trace
        def list_public_ips(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkPublicIP]: ...

        @distributed_trace
        def list_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkSegment]: ...

        @distributed_trace
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkVirtualMachine]: ...

        @distributed_trace
        def list_vm_groups(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[WorkloadNetworkVMGroup]: ...


namespace azure.mgmt.avs.models

    class azure.mgmt.avs.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.avs.models.Addon(ProxyResource):
        id: str
        name: str
        properties: Optional[AddonProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AddonProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AddonArcProperties(AddonProperties, discriminator='Arc'):
        addon_type: Literal[AddonType.ARC]
        provisioning_state: Union[str, AddonProvisioningState]
        v_center: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                v_center: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AddonHcxProperties(AddonProperties, discriminator='HCX'):
        addon_type: Literal[AddonType.HCX]
        management_network: Optional[str]
        offer: str
        provisioning_state: Union[str, AddonProvisioningState]
        uplink_network: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                management_network: Optional[str] = ..., 
                offer: str, 
                uplink_network: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AddonProperties(_Model):
        addon_type: str
        provisioning_state: Optional[Union[str, AddonProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                addon_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AddonProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        CANCELLED = "Cancelled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.AddonSrmProperties(AddonProperties, discriminator='SRM'):
        addon_type: Literal[AddonType.SRM]
        license_key: Optional[str]
        provisioning_state: Union[str, AddonProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                license_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AddonType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC = "Arc"
        HCX = "HCX"
        SRM = "SRM"
        VR = "VR"


    class azure.mgmt.avs.models.AddonVrProperties(AddonProperties, discriminator='VR'):
        addon_type: Literal[AddonType.VR]
        provisioning_state: Union[str, AddonProvisioningState]
        vrs_count: int

        @overload
        def __init__(
                self, 
                *, 
                vrs_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AdminCredentials(_Model):
        nsxt_password: Optional[str]
        nsxt_username: Optional[str]
        vcenter_password: Optional[str]
        vcenter_username: Optional[str]


    class azure.mgmt.avs.models.AffinityStrength(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MUST = "Must"
        SHOULD = "Should"


    class azure.mgmt.avs.models.AffinityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AFFINITY = "Affinity"
        ANTI_AFFINITY = "AntiAffinity"


    class azure.mgmt.avs.models.AvailabilityProperties(_Model):
        secondary_zone: Optional[int]
        strategy: Optional[Union[str, AvailabilityStrategy]]
        zone: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                secondary_zone: Optional[int] = ..., 
                strategy: Optional[Union[str, AvailabilityStrategy]] = ..., 
                zone: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AvailabilityStrategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DUAL_ZONE = "DualZone"
        SINGLE_ZONE = "SingleZone"


    class azure.mgmt.avs.models.AvailableWindowForMaintenanceWhileRescheduleOperation(RescheduleOperationConstraint, discriminator='AvailableWindowForMaintenance'):
        ends_at: datetime
        kind: Literal[RescheduleOperationConstraintKind.AVAILABLE_WINDOW_FOR_MAINTENANCE_WHILE_RESCHEDULE_OPERATION]
        starts_at: datetime

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AvailableWindowForMaintenanceWhileScheduleOperation(ScheduleOperationConstraint, discriminator='AvailableWindowForMaintenance'):
        ends_at: datetime
        kind: Literal[ScheduleOperationConstraintKind.AVAILABLE_WINDOW_FOR_MAINTENANCE_WHILE_SCHEDULE_OPERATION]
        starts_at: datetime

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.AzureHybridBenefitType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SQL_HOST = "SqlHost"


    class azure.mgmt.avs.models.BlockedDatesConstraintCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HI_PRIORITY_EVENT = "HiPriorityEvent"
        HOLIDAY = "Holiday"
        QUOTA_EXHAUSTED = "QuotaExhausted"


    class azure.mgmt.avs.models.BlockedDatesConstraintTimeRange(_Model):
        ends_at: datetime
        reason: Optional[str]
        starts_at: datetime


    class azure.mgmt.avs.models.BlockedWhileRescheduleOperation(RescheduleOperationConstraint, discriminator='Blocked'):
        category: Union[str, BlockedDatesConstraintCategory]
        kind: Literal[RescheduleOperationConstraintKind.BLOCKED_WHILE_RESCHEDULE_OPERATION]
        time_ranges: Optional[list[BlockedDatesConstraintTimeRange]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.BlockedWhileScheduleOperation(ScheduleOperationConstraint, discriminator='Blocked'):
        category: Union[str, BlockedDatesConstraintCategory]
        kind: Literal[ScheduleOperationConstraintKind.BLOCKED_WHILE_SCHEDULE_OPERATION]
        time_ranges: Optional[list[BlockedDatesConstraintTimeRange]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.Circuit(_Model):
        express_route_id: Optional[str]
        express_route_private_peering_id: Optional[str]
        primary_subnet: Optional[str]
        secondary_subnet: Optional[str]


    class azure.mgmt.avs.models.CloudLink(ProxyResource):
        id: str
        name: str
        properties: Optional[CloudLinkProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CloudLinkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.CloudLinkProperties(_Model):
        linked_cloud: Optional[str]
        provisioning_state: Optional[Union[str, CloudLinkProvisioningState]]
        status: Optional[Union[str, CloudLinkStatus]]

        @overload
        def __init__(
                self, 
                *, 
                linked_cloud: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.CloudLinkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.CloudLinkStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        BUILDING = "Building"
        DELETING = "Deleting"
        DISCONNECTED = "Disconnected"
        FAILED = "Failed"


    class azure.mgmt.avs.models.Cluster(ProxyResource):
        id: str
        name: str
        properties: Optional[ClusterProperties]
        sku: Sku
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterProperties] = ..., 
                sku: Sku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ClusterProperties(_Model):
        cluster_id: Optional[int]
        cluster_size: Optional[int]
        hosts: Optional[list[str]]
        provisioning_state: Optional[Union[str, ClusterProvisioningState]]
        vsan_datastore_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_size: Optional[int] = ..., 
                hosts: Optional[list[str]] = ..., 
                vsan_datastore_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ClusterProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLED = "Cancelled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.ClusterUpdate(_Model):
        properties: Optional[ClusterUpdateProperties]
        sku: Optional[Sku]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ClusterUpdateProperties] = ..., 
                sku: Optional[Sku] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ClusterUpdateProperties(_Model):
        cluster_size: Optional[int]
        hosts: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                cluster_size: Optional[int] = ..., 
                hosts: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ClusterZone(_Model):
        hosts: Optional[list[str]]
        zone: Optional[str]


    class azure.mgmt.avs.models.ClusterZoneList(_Model):
        zones: Optional[list[ClusterZone]]

        @overload
        def __init__(
                self, 
                *, 
                zones: Optional[list[ClusterZone]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.avs.models.Datastore(ProxyResource):
        id: str
        name: str
        properties: Optional[DatastoreProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DatastoreProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.DatastoreProperties(_Model):
        disk_pool_volume: Optional[DiskPoolVolume]
        elastic_san_volume: Optional[ElasticSanVolume]
        net_app_volume: Optional[NetAppVolume]
        provisioning_state: Optional[Union[str, DatastoreProvisioningState]]
        pure_storage_volume: Optional[PureStorageVolume]
        status: Optional[Union[str, DatastoreStatus]]

        @overload
        def __init__(
                self, 
                *, 
                disk_pool_volume: Optional[DiskPoolVolume] = ..., 
                elastic_san_volume: Optional[ElasticSanVolume] = ..., 
                net_app_volume: Optional[NetAppVolume] = ..., 
                pure_storage_volume: Optional[PureStorageVolume] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.DatastoreProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLED = "Cancelled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.DatastoreStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESSIBLE = "Accessible"
        ATTACHED = "Attached"
        DEAD_OR_ERROR = "DeadOrError"
        DETACHED = "Detached"
        INACCESSIBLE = "Inaccessible"
        LOST_COMMUNICATION = "LostCommunication"
        UNKNOWN = "Unknown"


    class azure.mgmt.avs.models.DhcpTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RELAY = "RELAY"
        SERVER = "SERVER"


    class azure.mgmt.avs.models.DiskPoolVolume(_Model):
        lun_name: str
        mount_option: Optional[Union[str, MountOptionEnum]]
        path: Optional[str]
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                lun_name: str, 
                mount_option: Optional[Union[str, MountOptionEnum]] = ..., 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.DnsServiceLogLevelEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEBUG = "DEBUG"
        ERROR = "ERROR"
        FATAL = "FATAL"
        INFO = "INFO"
        WARNING = "WARNING"


    class azure.mgmt.avs.models.DnsServiceStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"


    class azure.mgmt.avs.models.DnsZoneType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE = "Private"
        PUBLIC = "Public"


    class azure.mgmt.avs.models.ElasticSanVolume(_Model):
        target_id: str

        @overload
        def __init__(
                self, 
                *, 
                target_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.Encryption(_Model):
        key_vault_properties: Optional[EncryptionKeyVaultProperties]
        status: Optional[Union[str, EncryptionState]]

        @overload
        def __init__(
                self, 
                *, 
                key_vault_properties: Optional[EncryptionKeyVaultProperties] = ..., 
                status: Optional[Union[str, EncryptionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.EncryptionKeyStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS_DENIED = "AccessDenied"
        CONNECTED = "Connected"


    class azure.mgmt.avs.models.EncryptionKeyVaultProperties(_Model):
        auto_detected_key_version: Optional[str]
        key_name: Optional[str]
        key_state: Optional[Union[str, EncryptionKeyStatus]]
        key_vault_url: Optional[str]
        key_version: Optional[str]
        version_type: Optional[Union[str, EncryptionVersionType]]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_url: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.EncryptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.EncryptionVersionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTO_DETECTED = "AutoDetected"
        FIXED = "Fixed"


    class azure.mgmt.avs.models.Endpoints(_Model):
        hcx_cloud_manager: Optional[str]
        hcx_cloud_manager_ip: Optional[str]
        nsxt_manager: Optional[str]
        nsxt_manager_ip: Optional[str]
        vcenter_ip: Optional[str]
        vcsa: Optional[str]


    class azure.mgmt.avs.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.avs.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.avs.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ExpressRouteAuthorization(ProxyResource):
        id: str
        name: str
        properties: Optional[ExpressRouteAuthorizationProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ExpressRouteAuthorizationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ExpressRouteAuthorizationProperties(_Model):
        express_route_authorization_id: Optional[str]
        express_route_authorization_key: Optional[str]
        express_route_id: Optional[str]
        provisioning_state: Optional[Union[str, ExpressRouteAuthorizationProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                express_route_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ExpressRouteAuthorizationProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.GeneralHostProperties(HostProperties, discriminator='General'):
        display_name: str
        fault_domain: str
        fqdn: str
        kind: Literal[HostKind.GENERAL]
        maintenance: Union[str, HostMaintenance]
        mo_ref_id: str
        provisioning_state: Union[str, HostProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                maintenance: Optional[Union[str, HostMaintenance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.GlobalReachConnection(ProxyResource):
        id: str
        name: str
        properties: Optional[GlobalReachConnectionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[GlobalReachConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.GlobalReachConnectionProperties(_Model):
        address_prefix: Optional[str]
        authorization_key: Optional[str]
        circuit_connection_status: Optional[Union[str, GlobalReachConnectionStatus]]
        express_route_id: Optional[str]
        peer_express_route_circuit: Optional[str]
        provisioning_state: Optional[Union[str, GlobalReachConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_key: Optional[str] = ..., 
                express_route_id: Optional[str] = ..., 
                peer_express_route_circuit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.GlobalReachConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.GlobalReachConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECTED = "Connected"
        CONNECTING = "Connecting"
        DISCONNECTED = "Disconnected"


    class azure.mgmt.avs.models.HcxEnterpriseSite(ProxyResource):
        id: str
        name: str
        properties: Optional[HcxEnterpriseSiteProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HcxEnterpriseSiteProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.HcxEnterpriseSiteProperties(_Model):
        activation_key: Optional[str]
        provisioning_state: Optional[Union[str, HcxEnterpriseSiteProvisioningState]]
        status: Optional[Union[str, HcxEnterpriseSiteStatus]]


    class azure.mgmt.avs.models.HcxEnterpriseSiteProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.HcxEnterpriseSiteStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        CONSUMED = "Consumed"
        DEACTIVATED = "Deactivated"
        DELETED = "Deleted"


    class azure.mgmt.avs.models.Host(ProxyResource):
        id: str
        name: str
        properties: Optional[HostProperties]
        sku: Optional[Sku]
        system_data: SystemData
        type: str
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HostProperties] = ..., 
                sku: Optional[Sku] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.HostKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GENERAL = "General"
        SPECIALIZED = "Specialized"


    class azure.mgmt.avs.models.HostMaintenance(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        REPLACEMENT = "Replacement"
        UPGRADE = "Upgrade"


    class azure.mgmt.avs.models.HostProperties(_Model):
        display_name: Optional[str]
        fault_domain: Optional[str]
        fqdn: Optional[str]
        kind: str
        maintenance: Optional[Union[str, HostMaintenance]]
        mo_ref_id: Optional[str]
        provisioning_state: Optional[Union[str, HostProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                kind: str, 
                maintenance: Optional[Union[str, HostMaintenance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.HostProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.IdentitySource(_Model):
        alias: Optional[str]
        base_group_dn: Optional[str]
        base_user_dn: Optional[str]
        domain: Optional[str]
        name: Optional[str]
        password: Optional[str]
        primary_server: Optional[str]
        secondary_server: Optional[str]
        ssl: Optional[Union[str, SslEnum]]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                alias: Optional[str] = ..., 
                base_group_dn: Optional[str] = ..., 
                base_user_dn: Optional[str] = ..., 
                domain: Optional[str] = ..., 
                name: Optional[str] = ..., 
                password: Optional[str] = ..., 
                primary_server: Optional[str] = ..., 
                secondary_server: Optional[str] = ..., 
                ssl: Optional[Union[str, SslEnum]] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ImpactedMaintenanceResource(_Model):
        errors: Optional[list[ImpactedMaintenanceResourceError]]
        id: Optional[str]


    class azure.mgmt.avs.models.ImpactedMaintenanceResourceError(_Model):
        action_required: Optional[bool]
        details: Optional[str]
        error_code: Optional[str]
        name: Optional[str]
        resolution_steps: Optional[list[str]]


    class azure.mgmt.avs.models.InternetEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.IscsiPath(ProxyResource):
        id: str
        name: str
        properties: Optional[IscsiPathProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[IscsiPathProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.IscsiPathProperties(_Model):
        network_block: str
        provisioning_state: Optional[Union[str, IscsiPathProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                network_block: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.IscsiPathProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.Label(_Model):
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


    class azure.mgmt.avs.models.License(ProxyResource):
        id: str
        name: str
        properties: Optional[LicenseProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[LicenseProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.LicenseKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VMWARE_FIREWALL = "VmwareFirewall"


    class azure.mgmt.avs.models.LicenseName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VMWARE_FIREWALL = "VmwareFirewall"


    class azure.mgmt.avs.models.LicenseProperties(_Model):
        kind: str
        provisioning_state: Optional[Union[str, LicenseProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.LicenseProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.Maintenance(ProxyResource):
        id: str
        name: str
        properties: Optional[MaintenanceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MaintenanceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceCheckType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRECHECK = "Precheck"
        PREFLIGHT = "Preflight"


    class azure.mgmt.avs.models.MaintenanceFailedCheck(_Model):
        impacted_resources: Optional[list[ImpactedMaintenanceResource]]
        name: Optional[str]


    class azure.mgmt.avs.models.MaintenanceManagementOperation(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceManagementOperationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MAINTENANCE_READINESS_REFRESH = "MaintenanceReadinessRefresh"
        RESCHEDULE = "Reschedule"
        SCHEDULE = "Schedule"


    class azure.mgmt.avs.models.MaintenanceProperties(_Model):
        cluster_id: Optional[int]
        component: Optional[Union[str, MaintenanceType]]
        display_name: Optional[str]
        estimated_duration_in_minutes: Optional[int]
        impact: Optional[str]
        info_link: Optional[str]
        maintenance_readiness: Optional[MaintenanceReadiness]
        operations: Optional[list[MaintenanceManagementOperation]]
        provisioning_state: Optional[Union[str, MaintenanceProvisioningState]]
        scheduled_by_microsoft: Optional[bool]
        scheduled_start_time: Optional[datetime]
        state: Optional[MaintenanceState]


    class azure.mgmt.avs.models.MaintenanceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.MaintenanceReadiness(_Model):
        failed_checks: Optional[list[MaintenanceFailedCheck]]
        last_updated: Optional[datetime]
        message: Optional[str]
        status: Union[str, MaintenanceReadinessStatus]
        type: Union[str, MaintenanceCheckType]


    class azure.mgmt.avs.models.MaintenanceReadinessRefreshOperation(MaintenanceManagementOperation, discriminator='MaintenanceReadinessRefresh'):
        disabled_reason: Optional[str]
        is_disabled: Optional[bool]
        kind: Literal[MaintenanceManagementOperationKind.MAINTENANCE_READINESS_REFRESH]
        message: Optional[str]
        refreshed_by_microsoft: Optional[bool]
        status: Optional[Union[str, MaintenanceReadinessRefreshOperationStatus]]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceReadinessRefreshOperationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_APPLICABLE = "NotApplicable"
        NOT_STARTED = "NotStarted"


    class azure.mgmt.avs.models.MaintenanceReadinessStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATA_NOT_AVAILABLE = "DataNotAvailable"
        NOT_APPLICABLE = "NotApplicable"
        NOT_READY = "NotReady"
        READY = "Ready"


    class azure.mgmt.avs.models.MaintenanceReschedule(_Model):
        message: Optional[str]
        reschedule_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                reschedule_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceSchedule(_Model):
        message: Optional[str]
        schedule_time: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                schedule_time: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceState(_Model):
        ended_at: Optional[datetime]
        message: Optional[str]
        name: Optional[Union[str, MaintenanceStateName]]
        started_at: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                ended_at: Optional[datetime] = ..., 
                message: Optional[str] = ..., 
                name: Optional[Union[str, MaintenanceStateName]] = ..., 
                started_at: Optional[datetime] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MaintenanceStateName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_SCHEDULED = "NotScheduled"
        SCHEDULED = "Scheduled"
        SUCCESS = "Success"


    class azure.mgmt.avs.models.MaintenanceStatusFilter(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.avs.models.MaintenanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESXI = "ESXI"
        NSXT = "NSXT"
        VCSA = "VCSA"


    class azure.mgmt.avs.models.ManagementCluster(_Model):
        cluster_id: Optional[int]
        cluster_size: Optional[int]
        hosts: Optional[list[str]]
        provisioning_state: Optional[Union[str, ClusterProvisioningState]]
        vsan_datastore_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                cluster_size: Optional[int] = ..., 
                hosts: Optional[list[str]] = ..., 
                vsan_datastore_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.MountOptionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ATTACH = "ATTACH"
        MOUNT = "MOUNT"


    class azure.mgmt.avs.models.NetAppVolume(_Model):
        id: str

        @overload
        def __init__(
                self, 
                *, 
                id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.NsxPublicIpQuotaRaisedEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.Operation(_Model):
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


    class azure.mgmt.avs.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.avs.models.OptionalParamEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        OPTIONAL = "Optional"
        REQUIRED = "Required"


    class azure.mgmt.avs.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.avs.models.PSCredentialExecutionParameter(ScriptExecutionParameter, discriminator='Credential'):
        name: str
        password: Optional[str]
        type: Literal[ScriptExecutionParameterType.CREDENTIAL]
        username: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                password: Optional[str] = ..., 
                username: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PlacementPolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[PlacementPolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlacementPolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PlacementPolicyProperties(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, PlacementPolicyProvisioningState]]
        state: Optional[Union[str, PlacementPolicyState]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                state: Optional[Union[str, PlacementPolicyState]] = ..., 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PlacementPolicyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.PlacementPolicyState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.PlacementPolicyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VM_HOST = "VmHost"
        VM_VM = "VmVm"


    class azure.mgmt.avs.models.PlacementPolicyUpdate(_Model):
        properties: Optional[PlacementPolicyUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PlacementPolicyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.PlacementPolicyUpdateProperties(_Model):
        affinity_strength: Optional[Union[str, AffinityStrength]]
        azure_hybrid_benefit_type: Optional[Union[str, AzureHybridBenefitType]]
        host_members: Optional[list[str]]
        state: Optional[Union[str, PlacementPolicyState]]
        vm_members: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                affinity_strength: Optional[Union[str, AffinityStrength]] = ..., 
                azure_hybrid_benefit_type: Optional[Union[str, AzureHybridBenefitType]] = ..., 
                host_members: Optional[list[str]] = ..., 
                state: Optional[Union[str, PlacementPolicyState]] = ..., 
                vm_members: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PortMirroringDirectionEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BIDIRECTIONAL = "BIDIRECTIONAL"
        EGRESS = "EGRESS"
        INGRESS = "INGRESS"


    class azure.mgmt.avs.models.PortMirroringStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"


    class azure.mgmt.avs.models.PrivateCloud(TrackedResource):
        id: str
        identity: Optional[PrivateCloudIdentity]
        location: str
        name: str
        properties: Optional[PrivateCloudProperties]
        sku: Sku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        zones: Optional[list[str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[PrivateCloudIdentity] = ..., 
                location: str, 
                properties: Optional[PrivateCloudProperties] = ..., 
                sku: Sku, 
                tags: Optional[dict[str, str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.PrivateCloudIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ResourceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ResourceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PrivateCloudProperties(_Model):
        availability: Optional[AvailabilityProperties]
        circuit: Optional[Circuit]
        dns_zone_type: Optional[Union[str, DnsZoneType]]
        encryption: Optional[Encryption]
        endpoints: Optional[Endpoints]
        extended_network_blocks: Optional[list[str]]
        external_cloud_links: Optional[list[str]]
        identity_sources: Optional[list[IdentitySource]]
        internet: Optional[Union[str, InternetEnum]]
        management_cluster: ManagementCluster
        management_network: Optional[str]
        network_block: str
        nsx_public_ip_quota_raised: Optional[Union[str, NsxPublicIpQuotaRaisedEnum]]
        nsxt_certificate_thumbprint: Optional[str]
        nsxt_password: Optional[str]
        provisioning_network: Optional[str]
        provisioning_state: Optional[Union[str, PrivateCloudProvisioningState]]
        secondary_circuit: Optional[Circuit]
        vcenter_certificate_thumbprint: Optional[str]
        vcenter_password: Optional[str]
        vcf_license: Optional[VcfLicense]
        virtual_network_id: Optional[str]
        vmotion_network: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                availability: Optional[AvailabilityProperties] = ..., 
                circuit: Optional[Circuit] = ..., 
                dns_zone_type: Optional[Union[str, DnsZoneType]] = ..., 
                encryption: Optional[Encryption] = ..., 
                extended_network_blocks: Optional[list[str]] = ..., 
                identity_sources: Optional[list[IdentitySource]] = ..., 
                internet: Optional[Union[str, InternetEnum]] = ..., 
                management_cluster: ManagementCluster, 
                network_block: str, 
                nsxt_password: Optional[str] = ..., 
                secondary_circuit: Optional[Circuit] = ..., 
                vcenter_password: Optional[str] = ..., 
                vcf_license: Optional[VcfLicense] = ..., 
                virtual_network_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PrivateCloudProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        CANCELLED = "Cancelled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.PrivateCloudUpdate(_Model):
        identity: Optional[PrivateCloudIdentity]
        properties: Optional[PrivateCloudUpdateProperties]
        sku: Optional[Sku]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[PrivateCloudIdentity] = ..., 
                properties: Optional[PrivateCloudUpdateProperties] = ..., 
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


    class azure.mgmt.avs.models.PrivateCloudUpdateProperties(_Model):
        availability: Optional[AvailabilityProperties]
        dns_zone_type: Optional[Union[str, DnsZoneType]]
        encryption: Optional[Encryption]
        extended_network_blocks: Optional[list[str]]
        identity_sources: Optional[list[IdentitySource]]
        internet: Optional[Union[str, InternetEnum]]
        management_cluster: Optional[ManagementCluster]

        @overload
        def __init__(
                self, 
                *, 
                availability: Optional[AvailabilityProperties] = ..., 
                dns_zone_type: Optional[Union[str, DnsZoneType]] = ..., 
                encryption: Optional[Encryption] = ..., 
                extended_network_blocks: Optional[list[str]] = ..., 
                identity_sources: Optional[list[IdentitySource]] = ..., 
                internet: Optional[Union[str, InternetEnum]] = ..., 
                management_cluster: Optional[ManagementCluster] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ProvisionedNetwork(ProxyResource):
        id: str
        name: str
        properties: Optional[ProvisionedNetworkProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ProvisionedNetworkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ProvisionedNetworkProperties(_Model):
        address_prefix: Optional[str]
        network_type: Optional[Union[str, ProvisionedNetworkTypes]]
        provisioning_state: Optional[Union[str, ProvisionedNetworkProvisioningState]]


    class azure.mgmt.avs.models.ProvisionedNetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.ProvisionedNetworkTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ESX_MANAGEMENT = "esxManagement"
        ESX_REPLICATION = "esxReplication"
        HCX_MANAGEMENT = "hcxManagement"
        HCX_UPLINK = "hcxUplink"
        VCENTER_MANAGEMENT = "vcenterManagement"
        VMOTION = "vmotion"
        VSAN = "vsan"


    class azure.mgmt.avs.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.avs.models.PureStoragePolicy(ProxyResource):
        id: str
        name: str
        properties: Optional[PureStoragePolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PureStoragePolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PureStoragePolicyProperties(_Model):
        provisioning_state: Optional[Union[str, PureStoragePolicyProvisioningState]]
        storage_policy_definition: str
        storage_pool_id: str

        @overload
        def __init__(
                self, 
                *, 
                storage_policy_definition: str, 
                storage_pool_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.PureStoragePolicyProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.PureStorageVolume(_Model):
        size_gb: int
        storage_pool_id: str

        @overload
        def __init__(
                self, 
                *, 
                size_gb: int, 
                storage_pool_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.Quota(_Model):
        hosts_remaining: Optional[dict[str, int]]
        quota_enabled: Optional[Union[str, QuotaEnabled]]


    class azure.mgmt.avs.models.QuotaEnabled(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.RescheduleOperation(MaintenanceManagementOperation, discriminator='Reschedule'):
        constraints: Optional[list[RescheduleOperationConstraint]]
        disabled_reason: Optional[str]
        is_disabled: Optional[bool]
        kind: Literal[MaintenanceManagementOperationKind.RESCHEDULE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.RescheduleOperationConstraint(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.RescheduleOperationConstraintKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE_WINDOW_FOR_MAINTENANCE_WHILE_RESCHEDULE_OPERATION = "AvailableWindowForMaintenance"
        BLOCKED_WHILE_RESCHEDULE_OPERATION = "Blocked"


    class azure.mgmt.avs.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.avs.models.ResourceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.avs.models.ResourceSku(_Model):
        capabilities: Optional[list[ResourceSkuCapabilities]]
        family: Optional[str]
        location_info: list[ResourceSkuLocationInfo]
        locations: list[str]
        name: str
        resource_type: Union[str, ResourceSkuResourceType]
        restrictions: list[ResourceSkuRestrictions]
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[ResourceSkuCapabilities]] = ..., 
                family: Optional[str] = ..., 
                location_info: list[ResourceSkuLocationInfo], 
                locations: list[str], 
                name: str, 
                resource_type: Union[str, ResourceSkuResourceType], 
                restrictions: list[ResourceSkuRestrictions], 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ResourceSkuCapabilities(_Model):
        name: str
        value: str

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ResourceSkuLocationInfo(_Model):
        location: str
        zone_details: list[ResourceSkuZoneDetails]
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                zone_details: list[ResourceSkuZoneDetails], 
                zones: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ResourceSkuResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PRIVATE_CLOUDS = "privateClouds"
        PRIVATE_CLOUDS_CLUSTERS = "privateClouds/clusters"


    class azure.mgmt.avs.models.ResourceSkuRestrictionInfo(_Model):
        locations: Optional[list[str]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ResourceSkuRestrictions(_Model):
        reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]]
        restriction_info: ResourceSkuRestrictionInfo
        type: Optional[Union[str, ResourceSkuRestrictionsType]]
        values_property: list[str]

        @overload
        def __init__(
                self, 
                *, 
                reason_code: Optional[Union[str, ResourceSkuRestrictionsReasonCode]] = ..., 
                restriction_info: ResourceSkuRestrictionInfo, 
                type: Optional[Union[str, ResourceSkuRestrictionsType]] = ..., 
                values_property: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.avs.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "Location"
        ZONE = "Zone"


    class azure.mgmt.avs.models.ResourceSkuZoneDetails(_Model):
        capabilities: list[ResourceSkuCapabilities]
        name: list[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: list[ResourceSkuCapabilities], 
                name: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScheduleOperation(MaintenanceManagementOperation, discriminator='Schedule'):
        constraints: Optional[list[ScheduleOperationConstraint]]
        disabled_reason: Optional[str]
        is_disabled: Optional[bool]
        kind: Literal[MaintenanceManagementOperationKind.SCHEDULE]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScheduleOperationConstraint(_Model):
        kind: str

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScheduleOperationConstraintKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE_WINDOW_FOR_MAINTENANCE_WHILE_SCHEDULE_OPERATION = "AvailableWindowForMaintenance"
        BLOCKED_WHILE_SCHEDULE_OPERATION = "Blocked"
        SCHEDULING_WINDOW = "SchedulingWindow"


    class azure.mgmt.avs.models.SchedulingWindow(ScheduleOperationConstraint, discriminator='SchedulingWindow'):
        ends_at: datetime
        kind: Literal[ScheduleOperationConstraintKind.SCHEDULING_WINDOW]
        starts_at: datetime

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScriptCmdlet(ProxyResource):
        id: str
        name: str
        properties: Optional[ScriptCmdletProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScriptCmdletProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ScriptCmdletAudience(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANY = "Any"
        AUTOMATION = "Automation"


    class azure.mgmt.avs.models.ScriptCmdletProperties(_Model):
        audience: Optional[Union[str, ScriptCmdletAudience]]
        description: Optional[str]
        parameters: Optional[list[ScriptParameter]]
        provisioning_state: Optional[Union[str, ScriptCmdletProvisioningState]]
        timeout: Optional[str]


    class azure.mgmt.avs.models.ScriptCmdletProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.ScriptExecution(ProxyResource):
        id: str
        name: str
        properties: Optional[ScriptExecutionProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScriptExecutionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ScriptExecutionParameter(_Model):
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


    class azure.mgmt.avs.models.ScriptExecutionParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREDENTIAL = "Credential"
        SECURE_VALUE = "SecureValue"
        VALUE = "Value"


    class azure.mgmt.avs.models.ScriptExecutionProperties(_Model):
        errors: Optional[list[str]]
        failure_reason: Optional[str]
        finished_at: Optional[datetime]
        hidden_parameters: Optional[list[ScriptExecutionParameter]]
        information: Optional[list[str]]
        named_outputs: Optional[dict[str, Any]]
        output: Optional[list[str]]
        parameters: Optional[list[ScriptExecutionParameter]]
        provisioning_state: Optional[Union[str, ScriptExecutionProvisioningState]]
        retention: Optional[str]
        script_cmdlet_id: Optional[str]
        started_at: Optional[datetime]
        submitted_at: Optional[datetime]
        timeout: str
        warnings: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                failure_reason: Optional[str] = ..., 
                hidden_parameters: Optional[list[ScriptExecutionParameter]] = ..., 
                named_outputs: Optional[dict[str, Any]] = ..., 
                output: Optional[list[str]] = ..., 
                parameters: Optional[list[ScriptExecutionParameter]] = ..., 
                retention: Optional[str] = ..., 
                script_cmdlet_id: Optional[str] = ..., 
                timeout: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScriptExecutionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CANCELLED = "Cancelled"
        CANCELLING = "Cancelling"
        DELETING = "Deleting"
        FAILED = "Failed"
        PENDING = "Pending"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.ScriptOutputStreamType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        INFORMATION = "Information"
        OUTPUT = "Output"
        WARNING = "Warning"


    class azure.mgmt.avs.models.ScriptPackage(ProxyResource):
        id: str
        name: str
        properties: Optional[ScriptPackageProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ScriptPackageProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.ScriptPackageProperties(_Model):
        company: Optional[str]
        description: Optional[str]
        provisioning_state: Optional[Union[str, ScriptPackageProvisioningState]]
        uri: Optional[str]
        version: Optional[str]


    class azure.mgmt.avs.models.ScriptPackageProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.ScriptParameter(_Model):
        description: Optional[str]
        name: Optional[str]
        optional: Optional[Union[str, OptionalParamEnum]]
        type: Optional[Union[str, ScriptParameterTypes]]
        visibility: Optional[Union[str, VisibilityParameterEnum]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScriptParameterTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BOOL = "Bool"
        CREDENTIAL = "Credential"
        FLOAT = "Float"
        INT = "Int"
        SECURE_STRING = "SecureString"
        STRING = "String"


    class azure.mgmt.avs.models.ScriptSecureStringExecutionParameter(ScriptExecutionParameter, discriminator='SecureValue'):
        name: str
        secure_value: Optional[str]
        type: Literal[ScriptExecutionParameterType.SECURE_VALUE]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                secure_value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.ScriptStringExecutionParameter(ScriptExecutionParameter, discriminator='Value'):
        name: str
        type: Literal[ScriptExecutionParameterType.VALUE]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: str, 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.SegmentStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"


    class azure.mgmt.avs.models.Sku(_Model):
        capacity: Optional[int]
        family: Optional[str]
        name: str
        size: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.avs.models.SpecializedHostProperties(HostProperties, discriminator='Specialized'):
        display_name: str
        fault_domain: str
        fqdn: str
        kind: Literal[HostKind.SPECIALIZED]
        maintenance: Union[str, HostMaintenance]
        mo_ref_id: str
        provisioning_state: Union[str, HostProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                maintenance: Optional[Union[str, HostMaintenance]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.SslEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.SystemData(_Model):
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


    class azure.mgmt.avs.models.TrackedResource(Resource):
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


    class azure.mgmt.avs.models.Trial(_Model):
        available_hosts: Optional[int]
        status: Optional[Union[str, TrialStatus]]


    class azure.mgmt.avs.models.TrialStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        TRIAL_AVAILABLE = "TrialAvailable"
        TRIAL_DISABLED = "TrialDisabled"
        TRIAL_USED = "TrialUsed"


    class azure.mgmt.avs.models.VMGroupStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILURE = "FAILURE"
        SUCCESS = "SUCCESS"


    class azure.mgmt.avs.models.VMTypeEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EDGE = "EDGE"
        REGULAR = "REGULAR"
        SERVICE = "SERVICE"


    class azure.mgmt.avs.models.Vcf5License(VcfLicense, discriminator='vcf5'):
        broadcom_contract_number: Optional[str]
        broadcom_site_id: Optional[str]
        cores: int
        end_date: datetime
        kind: Literal[VcfLicenseKind.VCF5]
        labels: Optional[list[Label]]
        license_key: Optional[str]
        provisioning_state: Union[str, LicenseProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                broadcom_contract_number: Optional[str] = ..., 
                broadcom_site_id: Optional[str] = ..., 
                cores: int, 
                end_date: datetime, 
                labels: Optional[list[Label]] = ..., 
                license_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.VcfLicense(_Model):
        kind: str
        provisioning_state: Optional[Union[str, LicenseProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                kind: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.VcfLicenseKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        VCF5 = "vcf5"


    class azure.mgmt.avs.models.VirtualMachine(ProxyResource):
        id: str
        name: str
        properties: Optional[VirtualMachineProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VirtualMachineProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.VirtualMachineProperties(_Model):
        display_name: Optional[str]
        folder_path: Optional[str]
        mo_ref_id: Optional[str]
        provisioning_state: Optional[Union[str, VirtualMachineProvisioningState]]
        restrict_movement: Optional[Union[str, VirtualMachineRestrictMovementState]]


    class azure.mgmt.avs.models.VirtualMachineProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.avs.models.VirtualMachineRestrictMovement(_Model):
        restrict_movement: Optional[Union[str, VirtualMachineRestrictMovementState]]

        @overload
        def __init__(
                self, 
                *, 
                restrict_movement: Optional[Union[str, VirtualMachineRestrictMovementState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.VirtualMachineRestrictMovementState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.avs.models.VisibilityParameterEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HIDDEN = "Hidden"
        VISIBLE = "Visible"


    class azure.mgmt.avs.models.VmHostPlacementPolicyProperties(PlacementPolicyProperties, discriminator='VmHost'):
        affinity_strength: Optional[Union[str, AffinityStrength]]
        affinity_type: Union[str, AffinityType]
        azure_hybrid_benefit_type: Optional[Union[str, AzureHybridBenefitType]]
        display_name: str
        host_members: list[str]
        provisioning_state: Union[str, PlacementPolicyProvisioningState]
        state: Union[str, PlacementPolicyState]
        type: Literal[PlacementPolicyType.VM_HOST]
        vm_members: list[str]

        @overload
        def __init__(
                self, 
                *, 
                affinity_strength: Optional[Union[str, AffinityStrength]] = ..., 
                affinity_type: Union[str, AffinityType], 
                azure_hybrid_benefit_type: Optional[Union[str, AzureHybridBenefitType]] = ..., 
                display_name: Optional[str] = ..., 
                host_members: list[str], 
                state: Optional[Union[str, PlacementPolicyState]] = ..., 
                vm_members: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.VmPlacementPolicyProperties(PlacementPolicyProperties, discriminator='VmVm'):
        affinity_type: Union[str, AffinityType]
        display_name: str
        provisioning_state: Union[str, PlacementPolicyProvisioningState]
        state: Union[str, PlacementPolicyState]
        type: Literal[PlacementPolicyType.VM_VM]
        vm_members: list[str]

        @overload
        def __init__(
                self, 
                *, 
                affinity_type: Union[str, AffinityType], 
                display_name: Optional[str] = ..., 
                state: Optional[Union[str, PlacementPolicyState]] = ..., 
                vm_members: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.VmwareFirewallLicenseProperties(LicenseProperties, discriminator='VmwareFirewall'):
        broadcom_contract_number: Optional[str]
        broadcom_site_id: Optional[str]
        cores: int
        end_date: datetime
        kind: Literal[LicenseKind.VMWARE_FIREWALL]
        labels: Optional[list[Label]]
        license_key: Optional[str]
        provisioning_state: Union[str, LicenseProvisioningState]

        @overload
        def __init__(
                self, 
                *, 
                broadcom_contract_number: Optional[str] = ..., 
                broadcom_site_id: Optional[str] = ..., 
                cores: int, 
                end_date: datetime, 
                labels: Optional[list[Label]] = ..., 
                license_key: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetwork(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDhcp(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkDhcpEntity]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkDhcpEntity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDhcpEntity(_Model):
        dhcp_type: str
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, WorkloadNetworkDhcpProvisioningState]]
        revision: Optional[int]
        segments: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                dhcp_type: str, 
                display_name: Optional[str] = ..., 
                revision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDhcpProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkDhcpRelay(WorkloadNetworkDhcpEntity, discriminator='RELAY'):
        dhcp_type: Literal[DhcpTypeEnum.RELAY]
        display_name: str
        provisioning_state: Union[str, WorkloadNetworkDhcpProvisioningState]
        revision: int
        segments: list[str]
        server_addresses: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                revision: Optional[int] = ..., 
                server_addresses: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDhcpServer(WorkloadNetworkDhcpEntity, discriminator='SERVER'):
        dhcp_type: Literal[DhcpTypeEnum.SERVER]
        display_name: str
        lease_time: Optional[int]
        provisioning_state: Union[str, WorkloadNetworkDhcpProvisioningState]
        revision: int
        segments: list[str]
        server_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                lease_time: Optional[int] = ..., 
                revision: Optional[int] = ..., 
                server_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDnsService(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkDnsServiceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkDnsServiceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDnsServiceProperties(_Model):
        default_dns_zone: Optional[str]
        display_name: Optional[str]
        dns_service_ip: Optional[str]
        fqdn_zones: Optional[list[str]]
        log_level: Optional[Union[str, DnsServiceLogLevelEnum]]
        provisioning_state: Optional[Union[str, WorkloadNetworkDnsServiceProvisioningState]]
        revision: Optional[int]
        status: Optional[Union[str, DnsServiceStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                default_dns_zone: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                dns_service_ip: Optional[str] = ..., 
                fqdn_zones: Optional[list[str]] = ..., 
                log_level: Optional[Union[str, DnsServiceLogLevelEnum]] = ..., 
                revision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDnsServiceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkDnsZone(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkDnsZoneProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkDnsZoneProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDnsZoneProperties(_Model):
        display_name: Optional[str]
        dns_server_ips: Optional[list[str]]
        dns_services: Optional[int]
        domain: Optional[list[str]]
        provisioning_state: Optional[Union[str, WorkloadNetworkDnsZoneProvisioningState]]
        revision: Optional[int]
        source_ip: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                dns_server_ips: Optional[list[str]] = ..., 
                dns_services: Optional[int] = ..., 
                domain: Optional[list[str]] = ..., 
                revision: Optional[int] = ..., 
                source_ip: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkDnsZoneProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkGateway(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkGatewayProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkGatewayProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkGatewayProperties(_Model):
        display_name: Optional[str]
        path: Optional[str]
        provisioning_state: Optional[Union[str, WorkloadNetworkProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkPortMirroring(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkPortMirroringProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkPortMirroringProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkPortMirroringProperties(_Model):
        destination: Optional[str]
        direction: Optional[Union[str, PortMirroringDirectionEnum]]
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, WorkloadNetworkPortMirroringProvisioningState]]
        revision: Optional[int]
        source: Optional[str]
        status: Optional[Union[str, PortMirroringStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                destination: Optional[str] = ..., 
                direction: Optional[Union[str, PortMirroringDirectionEnum]] = ..., 
                display_name: Optional[str] = ..., 
                revision: Optional[int] = ..., 
                source: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkPortMirroringProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkProperties(_Model):
        provisioning_state: Optional[Union[str, WorkloadNetworkProvisioningState]]


    class azure.mgmt.avs.models.WorkloadNetworkProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkPublicIP(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkPublicIPProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkPublicIPProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkPublicIPProperties(_Model):
        display_name: Optional[str]
        number_of_public_i_ps: Optional[int]
        provisioning_state: Optional[Union[str, WorkloadNetworkPublicIPProvisioningState]]
        public_ip_block: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                number_of_public_i_ps: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkPublicIPProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkSegment(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkSegmentProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkSegmentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkSegmentPortVif(_Model):
        port_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                port_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkSegmentProperties(_Model):
        connected_gateway: Optional[str]
        display_name: Optional[str]
        port_vif: Optional[list[WorkloadNetworkSegmentPortVif]]
        provisioning_state: Optional[Union[str, WorkloadNetworkSegmentProvisioningState]]
        revision: Optional[int]
        status: Optional[Union[str, SegmentStatusEnum]]
        subnet: Optional[WorkloadNetworkSegmentSubnet]

        @overload
        def __init__(
                self, 
                *, 
                connected_gateway: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                revision: Optional[int] = ..., 
                subnet: Optional[WorkloadNetworkSegmentSubnet] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkSegmentProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkSegmentSubnet(_Model):
        dhcp_ranges: Optional[list[str]]
        gateway_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                dhcp_ranges: Optional[list[str]] = ..., 
                gateway_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkVMGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkVMGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkVMGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkVMGroupProperties(_Model):
        display_name: Optional[str]
        members: Optional[list[str]]
        provisioning_state: Optional[Union[str, WorkloadNetworkVMGroupProvisioningState]]
        revision: Optional[int]
        status: Optional[Union[str, VMGroupStatusEnum]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                members: Optional[list[str]] = ..., 
                revision: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkVMGroupProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BUILDING = "Building"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.avs.models.WorkloadNetworkVirtualMachine(ProxyResource):
        id: str
        name: str
        properties: Optional[WorkloadNetworkVirtualMachineProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WorkloadNetworkVirtualMachineProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.avs.models.WorkloadNetworkVirtualMachineProperties(_Model):
        display_name: Optional[str]
        provisioning_state: Optional[Union[str, WorkloadNetworkProvisioningState]]
        vm_type: Optional[Union[str, VMTypeEnum]]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.avs.operations

    class azure.mgmt.avs.operations.AddonsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: Addon, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Addon]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Addon]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                addon: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Addon]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                addon_name: str, 
                **kwargs: Any
            ) -> Addon: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Addon]: ...


    class azure.mgmt.avs.operations.AuthorizationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: ExpressRouteAuthorization, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpressRouteAuthorization]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpressRouteAuthorization]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                authorization: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ExpressRouteAuthorization]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                authorization_name: str, 
                **kwargs: Any
            ) -> ExpressRouteAuthorization: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ExpressRouteAuthorization]: ...


    class azure.mgmt.avs.operations.CloudLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: CloudLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                cloud_link: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CloudLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cloud_link_name: str, 
                **kwargs: Any
            ) -> CloudLink: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CloudLink]: ...


    class azure.mgmt.avs.operations.ClustersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: Cluster, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: ClusterUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                cluster_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Cluster]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> Cluster: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Cluster]: ...

        @distributed_trace
        def list_zones(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ClusterZoneList: ...


    class azure.mgmt.avs.operations.DatastoresOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: Datastore, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Datastore]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Datastore]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                datastore: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Datastore]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                datastore_name: str, 
                **kwargs: Any
            ) -> Datastore: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Datastore]: ...


    class azure.mgmt.avs.operations.GlobalReachConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: GlobalReachConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalReachConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalReachConnection]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                global_reach_connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GlobalReachConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                global_reach_connection_name: str, 
                **kwargs: Any
            ) -> GlobalReachConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[GlobalReachConnection]: ...


    class azure.mgmt.avs.operations.HcxEnterpriseSitesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: HcxEnterpriseSite, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                hcx_enterprise_site: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                hcx_enterprise_site_name: str, 
                **kwargs: Any
            ) -> HcxEnterpriseSite: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[HcxEnterpriseSite]: ...


    class azure.mgmt.avs.operations.HostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'cluster_name', 'host_id', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                host_id: str, 
                **kwargs: Any
            ) -> Host: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'cluster_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Host]: ...


    class azure.mgmt.avs.operations.IscsiPathsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: IscsiPath, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IscsiPath]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IscsiPath]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[IscsiPath]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> IscsiPath: ...

        @distributed_trace
        def list_by_private_cloud(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[IscsiPath]: ...


    class azure.mgmt.avs.operations.LicensesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: License, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[License]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name']}, api_versions_list=['2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name', 'accept']}, api_versions_list=['2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> License: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'license_name', 'accept']}, api_versions_list=['2025-09-01'])
        def get_properties(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                license_name: Union[str, LicenseName], 
                **kwargs: Any
            ) -> LicenseProperties: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[License]: ...


    class azure.mgmt.avs.operations.LocationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def check_quota_availability(
                self, 
                location: str, 
                **kwargs: Any
            ) -> Quota: ...

        @overload
        def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[Sku] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...

        @overload
        def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[JSON] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...

        @overload
        def check_trial_availability(
                self, 
                location: str, 
                sku: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Trial: ...


    class azure.mgmt.avs.operations.MaintenancesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'maintenance_name', 'accept']}, api_versions_list=['2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'maintenance_name', 'accept']}, api_versions_list=['2025-09-01'])
        def initiate_checks(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                **kwargs: Any
            ) -> Maintenance: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'state_name', 'status', 'from_parameter', 'to', 'accept']}, api_versions_list=['2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                *, 
                from_parameter: Optional[datetime] = ..., 
                state_name: Optional[Union[str, MaintenanceStateName]] = ..., 
                status: Optional[Union[str, MaintenanceStatusFilter]] = ..., 
                to: Optional[datetime] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Maintenance]: ...

        @overload
        def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: MaintenanceReschedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        def reschedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: MaintenanceSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...

        @overload
        def schedule(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                maintenance_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Maintenance: ...


    class azure.mgmt.avs.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.avs.operations.PlacementPoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: PlacementPolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: PlacementPolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                placement_policy_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PlacementPolicy]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                placement_policy_name: str, 
                **kwargs: Any
            ) -> PlacementPolicy: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PlacementPolicy]: ...


    class azure.mgmt.avs.operations.PrivateCloudsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: PrivateCloud, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_rotate_nsxt_password(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_rotate_vcenter_password(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: PrivateCloudUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                private_cloud_update: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateCloud]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> PrivateCloud: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01', params_added_on={'2025-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2025-09-01'])
        def get_vcf_license(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> VcfLicense: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateCloud]: ...

        @distributed_trace
        def list_admin_credentials(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> AdminCredentials: ...

        @distributed_trace
        def list_in_subscription(self, **kwargs: Any) -> ItemPaged[PrivateCloud]: ...


    class azure.mgmt.avs.operations.ProvisionedNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'provisioned_network_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                provisioned_network_name: str, 
                **kwargs: Any
            ) -> ProvisionedNetwork: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProvisionedNetwork]: ...


    class azure.mgmt.avs.operations.PureStoragePoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: PureStoragePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PureStoragePolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PureStoragePolicy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PureStoragePolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'storage_policy_name']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'storage_policy_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                storage_policy_name: str, 
                **kwargs: Any
            ) -> PureStoragePolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'private_cloud_name', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PureStoragePolicy]: ...


    class azure.mgmt.avs.operations.ScriptCmdletsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                script_cmdlet_name: str, 
                **kwargs: Any
            ) -> ScriptCmdlet: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScriptCmdlet]: ...


    class azure.mgmt.avs.operations.ScriptExecutionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: ScriptExecution, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScriptExecution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScriptExecution]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_execution: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ScriptExecution]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @overload
        def get_execution_logs(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_output_stream_type: Optional[List[Union[str, ScriptOutputStreamType]]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @overload
        def get_execution_logs(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_execution_name: str, 
                script_output_stream_type: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScriptExecution: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScriptExecution]: ...


    class azure.mgmt.avs.operations.ScriptPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                script_package_name: str, 
                **kwargs: Any
            ) -> ScriptPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ScriptPackage]: ...


    class azure.mgmt.avs.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01', params_added_on={'2024-09-01': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01', '2025-09-01'])
        def list(self, **kwargs: Any) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.avs.operations.VirtualMachinesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: VirtualMachineRestrictMovement, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_restrict_movement(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                restrict_movement: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                virtual_machine_id: str, 
                **kwargs: Any
            ) -> VirtualMachine: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                cluster_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VirtualMachine]: ...


    class azure.mgmt.avs.operations.WorkloadNetworksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: WorkloadNetworkDhcp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_create_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: WorkloadNetworkDnsService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_create_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: WorkloadNetworkDnsZone, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_create_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: WorkloadNetworkPortMirroring, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_create_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: WorkloadNetworkPublicIP, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        def begin_create_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                workload_network_public_ip: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPublicIP]: ...

        @overload
        def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: WorkloadNetworkSegment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_create_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: WorkloadNetworkVMGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        def begin_create_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @distributed_trace
        def begin_delete_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_dns_service(
                self, 
                resource_group_name: str, 
                dns_service_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_dns_zone(
                self, 
                resource_group_name: str, 
                dns_zone_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_port_mirroring(
                self, 
                resource_group_name: str, 
                port_mirroring_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_public_ip(
                self, 
                resource_group_name: str, 
                public_ip_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_segment(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete_vm_group(
                self, 
                resource_group_name: str, 
                vm_group_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: WorkloadNetworkDhcp, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_update_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dhcp_id: str, 
                workload_network_dhcp: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDhcp]: ...

        @overload
        def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: WorkloadNetworkDnsService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_update_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                workload_network_dns_service: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsService]: ...

        @overload
        def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: WorkloadNetworkDnsZone, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_update_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                workload_network_dns_zone: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkDnsZone]: ...

        @overload
        def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: WorkloadNetworkPortMirroring, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_update_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                workload_network_port_mirroring: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkPortMirroring]: ...

        @overload
        def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: WorkloadNetworkSegment, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_update_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                workload_network_segment: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkSegment]: ...

        @overload
        def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: WorkloadNetworkVMGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @overload
        def begin_update_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                workload_network_vm_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[WorkloadNetworkVMGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> WorkloadNetwork: ...

        @distributed_trace
        def get_dhcp(
                self, 
                resource_group_name: str, 
                dhcp_id: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDhcp: ...

        @distributed_trace
        def get_dns_service(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_service_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDnsService: ...

        @distributed_trace
        def get_dns_zone(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                dns_zone_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkDnsZone: ...

        @distributed_trace
        def get_gateway(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                gateway_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkGateway: ...

        @distributed_trace
        def get_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                port_mirroring_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkPortMirroring: ...

        @distributed_trace
        def get_public_ip(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                public_ip_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkPublicIP: ...

        @distributed_trace
        def get_segment(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                segment_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkSegment: ...

        @distributed_trace
        def get_virtual_machine(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                virtual_machine_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkVirtualMachine: ...

        @distributed_trace
        def get_vm_group(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                vm_group_id: str, 
                **kwargs: Any
            ) -> WorkloadNetworkVMGroup: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetwork]: ...

        @distributed_trace
        def list_dhcp(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkDhcp]: ...

        @distributed_trace
        def list_dns_services(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkDnsService]: ...

        @distributed_trace
        def list_dns_zones(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkDnsZone]: ...

        @distributed_trace
        def list_gateways(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkGateway]: ...

        @distributed_trace
        def list_port_mirroring(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkPortMirroring]: ...

        @distributed_trace
        def list_public_ips(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkPublicIP]: ...

        @distributed_trace
        def list_segments(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkSegment]: ...

        @distributed_trace
        def list_virtual_machines(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkVirtualMachine]: ...

        @distributed_trace
        def list_vm_groups(
                self, 
                resource_group_name: str, 
                private_cloud_name: str, 
                **kwargs: Any
            ) -> ItemPaged[WorkloadNetworkVMGroup]: ...


```