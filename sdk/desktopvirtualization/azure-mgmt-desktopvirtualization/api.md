```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.desktopvirtualization

    class azure.mgmt.desktopvirtualization.DesktopVirtualizationMgmtClient: implements ContextManager 
        app_attach_package: AppAttachPackageOperations
        app_attach_package_info: AppAttachPackageInfoOperations
        application_groups: ApplicationGroupsOperations
        applications: ApplicationsOperations
        desktops: DesktopsOperations
        host_pools: HostPoolsOperations
        msix_images: MsixImagesOperations
        msix_packages: MSIXPackagesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        scaling_plan_personal_schedules: ScalingPlanPersonalSchedulesOperations
        scaling_plan_pooled_schedules: ScalingPlanPooledSchedulesOperations
        scaling_plans: ScalingPlansOperations
        session_hosts: SessionHostsOperations
        start_menu_items: StartMenuItemsOperations
        user_sessions: UserSessionsOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        def close(self) -> None: ...


namespace azure.mgmt.desktopvirtualization.aio

    class azure.mgmt.desktopvirtualization.aio.DesktopVirtualizationMgmtClient: implements AsyncContextManager 
        app_attach_package: AppAttachPackageOperations
        app_attach_package_info: AppAttachPackageInfoOperations
        application_groups: ApplicationGroupsOperations
        applications: ApplicationsOperations
        desktops: DesktopsOperations
        host_pools: HostPoolsOperations
        msix_images: MsixImagesOperations
        msix_packages: MSIXPackagesOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        scaling_plan_personal_schedules: ScalingPlanPersonalSchedulesOperations
        scaling_plan_pooled_schedules: ScalingPlanPooledSchedulesOperations
        scaling_plans: ScalingPlansOperations
        session_hosts: SessionHostsOperations
        start_menu_items: StartMenuItemsOperations
        user_sessions: UserSessionsOperations
        workspaces: WorkspacesOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
                *, 
                api_version: str = ..., 
                **kwargs: Any
            ) -> None: ...

        async def close(self) -> None: ...


namespace azure.mgmt.desktopvirtualization.aio.operations

    class azure.mgmt.desktopvirtualization.aio.operations.AppAttachPackageInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def import_method(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                import_package_info_request: ImportPackageInfoRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[AppAttachPackage]: ...

        @overload
        def import_method(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                import_package_info_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[AppAttachPackage]: ...


    class azure.mgmt.desktopvirtualization.aio.operations.AppAttachPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package: AppAttachPackage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AppAttachPackage]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[AppAttachPackage]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package_patch: Optional[AppAttachPackagePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package_patch: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...


    class azure.mgmt.desktopvirtualization.aio.operations.ApplicationGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ApplicationGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ApplicationGroup]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: Optional[ApplicationGroupPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...


    class azure.mgmt.desktopvirtualization.aio.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Application]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Optional[ApplicationPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.desktopvirtualization.aio.operations.DesktopsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                **kwargs: Any
            ) -> Desktop: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Desktop]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                desktop: Optional[DesktopPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Desktop: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                desktop: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Desktop: ...


    class azure.mgmt.desktopvirtualization.aio.operations.HostPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: HostPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> HostPool: ...

        @distributed_trace
        def list(
                self, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[HostPool]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[HostPool]: ...

        @distributed_trace_async
        async def list_registration_tokens(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> RegistrationTokenList: ...

        @distributed_trace_async
        async def retrieve_registration_token(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> RegistrationInfo: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: Optional[HostPoolPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...


    class azure.mgmt.desktopvirtualization.aio.operations.MSIXPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: MSIXPackage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[MSIXPackage]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: Optional[MSIXPackagePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...


    class azure.mgmt.desktopvirtualization.aio.operations.MsixImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_image_uri: MSIXImageURI, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ExpandMsixImage]: ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_image_uri: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncIterable[ExpandMsixImage]: ...


    class azure.mgmt.desktopvirtualization.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[ResourceProviderOperation]: ...


    class azure.mgmt.desktopvirtualization.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @distributed_trace_async
        async def get_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnectionWithSystemData]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateEndpointConnectionWithSystemData]: ...

        @overload
        async def update_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        async def update_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        async def update_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        async def update_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...


    class azure.mgmt.desktopvirtualization.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[PrivateLinkResource]: ...


    class azure.mgmt.desktopvirtualization.aio.operations.ScalingPlanPersonalSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: ScalingPlanPersonalSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ScalingPlanPersonalSchedule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[ScalingPlanPersonalSchedulePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...


    class azure.mgmt.desktopvirtualization.aio.operations.ScalingPlanPooledSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: ScalingPlanPooledSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ScalingPlanPooledSchedule]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[ScalingPlanPooledSchedulePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...


    class azure.mgmt.desktopvirtualization.aio.operations.ScalingPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: ScalingPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @overload
        async def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ScalingPlan]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ScalingPlan]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[ScalingPlan]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: Optional[ScalingPlanPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...


    class azure.mgmt.desktopvirtualization.aio.operations.SessionHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                **kwargs: Any
            ) -> SessionHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[SessionHost]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                session_host: Optional[SessionHostPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SessionHost: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                session_host: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SessionHost: ...


    class azure.mgmt.desktopvirtualization.aio.operations.StartMenuItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[StartMenuItem]: ...


    class azure.mgmt.desktopvirtualization.aio.operations.UserSessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def disconnect(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                **kwargs: Any
            ) -> UserSession: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[UserSession]: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[UserSession]: ...

        @overload
        async def send_message(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                send_message: Optional[SendMessage] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def send_message(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                send_message: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.desktopvirtualization.aio.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> AsyncIterable[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[Workspace]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Optional[WorkspacePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


namespace azure.mgmt.desktopvirtualization.models

    class azure.mgmt.desktopvirtualization.models.AgentUpdatePatchProperties(Model):
        maintenance_window_time_zone: str
        maintenance_windows: list[MaintenanceWindowPatchProperties]
        type: Union[str, SessionHostComponentUpdateType]
        use_session_host_local_time: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                maintenance_window_time_zone: Optional[str] = ..., 
                maintenance_windows: Optional[List[MaintenanceWindowPatchProperties]] = ..., 
                type: Optional[Union[str, SessionHostComponentUpdateType]] = ..., 
                use_session_host_local_time: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AgentUpdateProperties(Model):
        maintenance_window_time_zone: str
        maintenance_windows: list[MaintenanceWindowProperties]
        type: Union[str, SessionHostComponentUpdateType]
        use_session_host_local_time: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                maintenance_window_time_zone: Optional[str] = ..., 
                maintenance_windows: Optional[List[MaintenanceWindowProperties]] = ..., 
                type: Optional[Union[str, SessionHostComponentUpdateType]] = ..., 
                use_session_host_local_time: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackage(TrackedResource):
        id: str
        location: str
        name: str
        properties: AppAttachPackageProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                properties: AppAttachPackageProperties, 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackageArchitectures(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "ALL"
        ARM = "ARM"
        ARM64 = "ARM64"
        NEUTRAL = "Neutral"
        X64 = "x64"
        X86 = "x86"
        X86_A64 = "x86a64"


    class azure.mgmt.desktopvirtualization.models.AppAttachPackageInfoProperties(Model):
        certificate_expiry: datetime
        certificate_name: str
        display_name: str
        image_path: str
        is_active: bool
        is_package_timestamped: Union[str, PackageTimestamped]
        is_regular_registration: bool
        last_updated: datetime
        package_alias: str
        package_applications: list[MsixPackageApplications]
        package_dependencies: list[MsixPackageDependencies]
        package_family_name: str
        package_full_name: str
        package_name: str
        package_relative_path: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_expiry: Optional[datetime] = ..., 
                certificate_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                image_path: Optional[str] = ..., 
                is_active: Optional[bool] = ..., 
                is_package_timestamped: Optional[Union[str, PackageTimestamped]] = ..., 
                is_regular_registration: Optional[bool] = ..., 
                last_updated: Optional[datetime] = ..., 
                package_alias: Optional[str] = ..., 
                package_applications: Optional[List[MsixPackageApplications]] = ..., 
                package_dependencies: Optional[List[MsixPackageDependencies]] = ..., 
                package_family_name: Optional[str] = ..., 
                package_full_name: Optional[str] = ..., 
                package_name: Optional[str] = ..., 
                package_relative_path: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackageList(Model):
        next_link: str
        value: list[AppAttachPackage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[AppAttachPackage]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackagePatch(Resource):
        id: str
        name: str
        properties: AppAttachPackagePatchProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[AppAttachPackagePatchProperties] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackagePatchProperties(Model):
        fail_health_check_on_staging_failure: Union[str, FailHealthCheckOnStagingFailure]
        host_pool_references: list[str]
        image: AppAttachPackageInfoProperties
        key_vault_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fail_health_check_on_staging_failure: Optional[Union[str, FailHealthCheckOnStagingFailure]] = ..., 
                host_pool_references: Optional[List[str]] = ..., 
                image: Optional[AppAttachPackageInfoProperties] = ..., 
                key_vault_url: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.AppAttachPackageProperties(Model):
        fail_health_check_on_staging_failure: Union[str, FailHealthCheckOnStagingFailure]
        host_pool_references: list[str]
        image: AppAttachPackageInfoProperties
        key_vault_url: str
        provisioning_state: Union[str, ProvisioningState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fail_health_check_on_staging_failure: Optional[Union[str, FailHealthCheckOnStagingFailure]] = ..., 
                host_pool_references: Optional[List[str]] = ..., 
                image: Optional[AppAttachPackageInfoProperties] = ..., 
                key_vault_url: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.Application(Resource):
        application_type: Union[str, RemoteApplicationType]
        command_line_arguments: str
        command_line_setting: Union[str, CommandLineSetting]
        description: str
        file_path: str
        friendly_name: str
        icon_content: bytes
        icon_hash: str
        icon_index: int
        icon_path: str
        id: str
        msix_package_application_id: str
        msix_package_family_name: str
        name: str
        object_id: str
        show_in_portal: bool
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_type: Optional[Union[str, RemoteApplicationType]] = ..., 
                command_line_arguments: Optional[str] = ..., 
                command_line_setting: Union[str, CommandLineSetting], 
                description: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                icon_index: Optional[int] = ..., 
                icon_path: Optional[str] = ..., 
                msix_package_application_id: Optional[str] = ..., 
                msix_package_family_name: Optional[str] = ..., 
                show_in_portal: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ApplicationGroup(ResourceModelWithAllowedPropertySet):
        application_group_type: Union[str, ApplicationGroupType]
        cloud_pc_resource: bool
        description: str
        etag: str
        friendly_name: str
        host_pool_arm_path: str
        id: str
        identity: ResourceModelWithAllowedPropertySetIdentity
        kind: str
        location: str
        managed_by: str
        name: str
        object_id: str
        plan: ResourceModelWithAllowedPropertySetPlan
        show_in_feed: bool
        sku: ResourceModelWithAllowedPropertySetSku
        system_data: SystemData
        tags: dict[str, str]
        type: str
        workspace_arm_path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_group_type: Union[str, ApplicationGroupType], 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                host_pool_arm_path: str, 
                identity: Optional[ResourceModelWithAllowedPropertySetIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[ResourceModelWithAllowedPropertySetPlan] = ..., 
                show_in_feed: Optional[bool] = ..., 
                sku: Optional[ResourceModelWithAllowedPropertySetSku] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ApplicationGroupList(Model):
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


    class azure.mgmt.desktopvirtualization.models.ApplicationGroupPatch(Resource):
        description: str
        friendly_name: str
        id: str
        name: str
        show_in_feed: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                show_in_feed: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ApplicationGroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESKTOP = "Desktop"
        REMOTE_APP = "RemoteApp"


    class azure.mgmt.desktopvirtualization.models.ApplicationList(Model):
        next_link: str
        value: list[Application]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Application]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ApplicationPatch(Model):
        application_type: Union[str, RemoteApplicationType]
        command_line_arguments: str
        command_line_setting: Union[str, CommandLineSetting]
        description: str
        file_path: str
        friendly_name: str
        icon_index: int
        icon_path: str
        msix_package_application_id: str
        msix_package_family_name: str
        show_in_portal: bool
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_type: Optional[Union[str, RemoteApplicationType]] = ..., 
                command_line_arguments: Optional[str] = ..., 
                command_line_setting: Optional[Union[str, CommandLineSetting]] = ..., 
                description: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                icon_index: Optional[int] = ..., 
                icon_path: Optional[str] = ..., 
                msix_package_application_id: Optional[str] = ..., 
                msix_package_family_name: Optional[str] = ..., 
                show_in_portal: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESKTOP = "Desktop"
        REMOTE_APP = "RemoteApp"


    class azure.mgmt.desktopvirtualization.models.CloudErrorProperties(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                message: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.CommandLineSetting(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DO_NOT_ALLOW = "DoNotAllow"
        REQUIRE = "Require"


    class azure.mgmt.desktopvirtualization.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.desktopvirtualization.models.DayOfWeek(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.desktopvirtualization.models.Desktop(Resource):
        description: str
        friendly_name: str
        icon_content: bytes
        icon_hash: str
        id: str
        name: str
        object_id: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.DesktopList(Model):
        next_link: str
        value: list[Desktop]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Desktop]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.DesktopPatch(Model):
        description: str
        friendly_name: str
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ErrorAdditionalInfo(Model):
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


    class azure.mgmt.desktopvirtualization.models.ErrorDetail(Model):
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


    class azure.mgmt.desktopvirtualization.models.ErrorResponse(Model):
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


    class azure.mgmt.desktopvirtualization.models.ExpandMsixImage(Resource):
        certificate_expiry: datetime
        certificate_name: str
        display_name: str
        id: str
        image_path: str
        is_active: bool
        is_regular_registration: bool
        last_updated: datetime
        name: str
        package_alias: str
        package_applications: list[MsixPackageApplications]
        package_dependencies: list[MsixPackageDependencies]
        package_family_name: str
        package_full_name: str
        package_name: str
        package_relative_path: str
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_expiry: Optional[datetime] = ..., 
                certificate_name: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                image_path: Optional[str] = ..., 
                is_active: Optional[bool] = ..., 
                is_regular_registration: Optional[bool] = ..., 
                last_updated: Optional[datetime] = ..., 
                package_alias: Optional[str] = ..., 
                package_applications: Optional[List[MsixPackageApplications]] = ..., 
                package_dependencies: Optional[List[MsixPackageDependencies]] = ..., 
                package_family_name: Optional[str] = ..., 
                package_full_name: Optional[str] = ..., 
                package_name: Optional[str] = ..., 
                package_relative_path: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ExpandMsixImageList(Model):
        next_link: str
        value: list[ExpandMsixImage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ExpandMsixImage]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.FailHealthCheckOnStagingFailure(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DO_NOT_FAIL = "DoNotFail"
        NEEDS_ASSISTANCE = "NeedsAssistance"
        UNHEALTHY = "Unhealthy"


    class azure.mgmt.desktopvirtualization.models.HealthCheckName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APP_ATTACH_HEALTH_CHECK = "AppAttachHealthCheck"
        DOMAIN_JOINED_CHECK = "DomainJoinedCheck"
        DOMAIN_REACHABLE = "DomainReachable"
        DOMAIN_TRUST_CHECK = "DomainTrustCheck"
        FS_LOGIX_HEALTH_CHECK = "FSLogixHealthCheck"
        META_DATA_SERVICE_CHECK = "MetaDataServiceCheck"
        MONITORING_AGENT_CHECK = "MonitoringAgentCheck"
        SUPPORTED_ENCRYPTION_CHECK = "SupportedEncryptionCheck"
        SX_S_STACK_LISTENER_CHECK = "SxSStackListenerCheck"
        URLS_ACCESSIBLE_CHECK = "UrlsAccessibleCheck"
        WEB_RTC_REDIRECTOR_CHECK = "WebRTCRedirectorCheck"


    class azure.mgmt.desktopvirtualization.models.HealthCheckResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTH_CHECK_FAILED = "HealthCheckFailed"
        HEALTH_CHECK_SUCCEEDED = "HealthCheckSucceeded"
        SESSION_HOST_SHUTDOWN = "SessionHostShutdown"
        UNKNOWN = "Unknown"


    class azure.mgmt.desktopvirtualization.models.HostPool(ResourceModelWithAllowedPropertySet):
        agent_update: AgentUpdateProperties
        app_attach_package_references: list[str]
        application_group_references: list[str]
        cloud_pc_resource: bool
        custom_rdp_property: str
        description: str
        etag: str
        friendly_name: str
        host_pool_type: Union[str, HostPoolType]
        id: str
        identity: ResourceModelWithAllowedPropertySetIdentity
        kind: str
        load_balancer_type: Union[str, LoadBalancerType]
        location: str
        managed_by: str
        max_session_limit: int
        name: str
        object_id: str
        personal_desktop_assignment_type: Union[str, PersonalDesktopAssignmentType]
        plan: ResourceModelWithAllowedPropertySetPlan
        preferred_app_group_type: Union[str, PreferredAppGroupType]
        private_endpoint_connections: list[PrivateEndpointConnection]
        public_network_access: Union[str, HostpoolPublicNetworkAccess]
        registration_info: RegistrationInfo
        ring: int
        sku: ResourceModelWithAllowedPropertySetSku
        sso_client_id: str
        sso_client_secret_key_vault_path: str
        sso_secret_type: Union[str, SSOSecretType]
        ssoadfs_authority: str
        start_vm_on_connect: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str
        validation_environment: bool
        vm_template: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_update: Optional[AgentUpdateProperties] = ..., 
                custom_rdp_property: Optional[str] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                host_pool_type: Union[str, HostPoolType], 
                identity: Optional[ResourceModelWithAllowedPropertySetIdentity] = ..., 
                kind: Optional[str] = ..., 
                load_balancer_type: Union[str, LoadBalancerType], 
                location: str, 
                managed_by: Optional[str] = ..., 
                max_session_limit: Optional[int] = ..., 
                personal_desktop_assignment_type: Optional[Union[str, PersonalDesktopAssignmentType]] = ..., 
                plan: Optional[ResourceModelWithAllowedPropertySetPlan] = ..., 
                preferred_app_group_type: Union[str, PreferredAppGroupType], 
                public_network_access: Optional[Union[str, HostpoolPublicNetworkAccess]] = ..., 
                registration_info: Optional[RegistrationInfo] = ..., 
                ring: Optional[int] = ..., 
                sku: Optional[ResourceModelWithAllowedPropertySetSku] = ..., 
                sso_client_id: Optional[str] = ..., 
                sso_client_secret_key_vault_path: Optional[str] = ..., 
                sso_secret_type: Optional[Union[str, SSOSecretType]] = ..., 
                ssoadfs_authority: Optional[str] = ..., 
                start_vm_on_connect: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                validation_environment: Optional[bool] = ..., 
                vm_template: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.HostPoolList(Model):
        next_link: str
        value: list[HostPool]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[HostPool]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.HostPoolPatch(Resource):
        agent_update: AgentUpdatePatchProperties
        custom_rdp_property: str
        description: str
        friendly_name: str
        id: str
        load_balancer_type: Union[str, LoadBalancerType]
        max_session_limit: int
        name: str
        personal_desktop_assignment_type: Union[str, PersonalDesktopAssignmentType]
        preferred_app_group_type: Union[str, PreferredAppGroupType]
        public_network_access: Union[str, HostpoolPublicNetworkAccess]
        registration_info: RegistrationInfoPatch
        ring: int
        sso_client_id: str
        sso_client_secret_key_vault_path: str
        sso_secret_type: Union[str, SSOSecretType]
        ssoadfs_authority: str
        start_vm_on_connect: bool
        system_data: SystemData
        tags: dict[str, str]
        type: str
        validation_environment: bool
        vm_template: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_update: Optional[AgentUpdatePatchProperties] = ..., 
                custom_rdp_property: Optional[str] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                load_balancer_type: Optional[Union[str, LoadBalancerType]] = ..., 
                max_session_limit: Optional[int] = ..., 
                personal_desktop_assignment_type: Optional[Union[str, PersonalDesktopAssignmentType]] = ..., 
                preferred_app_group_type: Optional[Union[str, PreferredAppGroupType]] = ..., 
                public_network_access: Optional[Union[str, HostpoolPublicNetworkAccess]] = ..., 
                registration_info: Optional[RegistrationInfoPatch] = ..., 
                ring: Optional[int] = ..., 
                sso_client_id: Optional[str] = ..., 
                sso_client_secret_key_vault_path: Optional[str] = ..., 
                sso_secret_type: Optional[Union[str, SSOSecretType]] = ..., 
                ssoadfs_authority: Optional[str] = ..., 
                start_vm_on_connect: Optional[bool] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                validation_environment: Optional[bool] = ..., 
                vm_template: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.HostPoolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYO_DESKTOP = "BYODesktop"
        PERSONAL = "Personal"
        POOLED = "Pooled"


    class azure.mgmt.desktopvirtualization.models.HostpoolPublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        ENABLED_FOR_CLIENTS_ONLY = "EnabledForClientsOnly"
        ENABLED_FOR_SESSION_HOSTS_ONLY = "EnabledForSessionHostsOnly"


    class azure.mgmt.desktopvirtualization.models.Identity(Model):
        principal_id: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Literal[SystemAssigned]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ImportPackageInfoRequest(Model):
        package_architecture: Union[str, AppAttachPackageArchitectures]
        path: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                package_architecture: Optional[Union[str, AppAttachPackageArchitectures]] = ..., 
                path: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.LoadBalancerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BREADTH_FIRST = "BreadthFirst"
        DEPTH_FIRST = "DepthFirst"
        PERSISTENT = "Persistent"


    class azure.mgmt.desktopvirtualization.models.LogSpecification(Model):
        blob_duration: str
        display_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                blob_duration: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MSIXImageURI(Model):
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                uri: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MSIXPackage(Resource):
        display_name: str
        id: str
        image_path: str
        is_active: bool
        is_regular_registration: bool
        last_updated: datetime
        name: str
        package_applications: list[MsixPackageApplications]
        package_dependencies: list[MsixPackageDependencies]
        package_family_name: str
        package_name: str
        package_relative_path: str
        system_data: SystemData
        type: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                image_path: Optional[str] = ..., 
                is_active: Optional[bool] = ..., 
                is_regular_registration: Optional[bool] = ..., 
                last_updated: Optional[datetime] = ..., 
                package_applications: Optional[List[MsixPackageApplications]] = ..., 
                package_dependencies: Optional[List[MsixPackageDependencies]] = ..., 
                package_family_name: Optional[str] = ..., 
                package_name: Optional[str] = ..., 
                package_relative_path: Optional[str] = ..., 
                version: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MSIXPackageList(Model):
        next_link: str
        value: list[MSIXPackage]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[MSIXPackage]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MSIXPackagePatch(Resource):
        display_name: str
        id: str
        is_active: bool
        is_regular_registration: bool
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                is_active: Optional[bool] = ..., 
                is_regular_registration: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MaintenanceWindowPatchProperties(Model):
        day_of_week: Union[str, DayOfWeek]
        hour: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                hour: Optional[int] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MaintenanceWindowProperties(Model):
        day_of_week: Union[str, DayOfWeek]
        hour: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                day_of_week: Optional[Union[str, DayOfWeek]] = ..., 
                hour: Optional[int] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MsixPackageApplications(Model):
        app_id: str
        app_user_model_id: str
        description: str
        friendly_name: str
        icon_image_name: str
        raw_icon: bytes
        raw_png: bytes

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_id: Optional[str] = ..., 
                app_user_model_id: Optional[str] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                icon_image_name: Optional[str] = ..., 
                raw_icon: Optional[bytes] = ..., 
                raw_png: Optional[bytes] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.MsixPackageDependencies(Model):
        dependency_name: str
        min_version: str
        publisher: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                dependency_name: Optional[str] = ..., 
                min_version: Optional[str] = ..., 
                publisher: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.OperationProperties(Model):
        service_specification: ServiceSpecification

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
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


    class azure.mgmt.desktopvirtualization.models.PackageTimestamped(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_TIMESTAMPED = "NotTimestamped"
        TIMESTAMPED = "Timestamped"


    class azure.mgmt.desktopvirtualization.models.PersonalDesktopAssignmentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        DIRECT = "Direct"


    class azure.mgmt.desktopvirtualization.models.Plan(Model):
        name: str
        product: str
        promotion_code: str
        publisher: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PreferredAppGroupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DESKTOP = "Desktop"
        NONE = "None"
        RAIL_APPLICATIONS = "RailApplications"


    class azure.mgmt.desktopvirtualization.models.PrivateEndpoint(Model):
        id: str

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


    class azure.mgmt.desktopvirtualization.models.PrivateEndpointConnection(Resource):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PrivateEndpointConnectionListResultWithSystemData(Model):
        next_link: str
        value: list[PrivateEndpointConnectionWithSystemData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateEndpointConnectionWithSystemData]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.desktopvirtualization.models.PrivateEndpointConnectionWithSystemData(PrivateEndpointConnection):
        group_ids: list[str]
        id: str
        name: str
        private_endpoint: PrivateEndpoint
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Union[str, PrivateEndpointConnectionProvisioningState]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: Optional[PrivateLinkServiceConnectionState] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.desktopvirtualization.models.PrivateLinkResource(Resource):
        group_id: str
        id: str
        name: str
        required_members: list[str]
        required_zone_names: list[str]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                required_zone_names: Optional[List[str]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PrivateLinkResourceListResult(Model):
        next_link: str
        value: list[PrivateLinkResource]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[PrivateLinkResource]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.PrivateLinkServiceConnectionState(Model):
        actions_required: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.desktopvirtualization.models.ProxyResource(Resource):
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


    class azure.mgmt.desktopvirtualization.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.desktopvirtualization.models.RegistrationInfo(Model):
        expiration_time: datetime
        registration_token_operation: Union[str, RegistrationTokenOperation]
        token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiration_time: Optional[datetime] = ..., 
                registration_token_operation: Optional[Union[str, RegistrationTokenOperation]] = ..., 
                token: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.RegistrationInfoPatch(Model):
        expiration_time: datetime
        registration_token_operation: Union[str, RegistrationTokenOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiration_time: Optional[datetime] = ..., 
                registration_token_operation: Optional[Union[str, RegistrationTokenOperation]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.RegistrationTokenList(Model):
        next_link: str
        value: list[RegistrationTokenMinimal]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[RegistrationTokenMinimal]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.RegistrationTokenMinimal(Model):
        expiration_time: datetime
        token: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                expiration_time: Optional[datetime] = ..., 
                token: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.RegistrationTokenOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        NONE = "None"
        UPDATE = "Update"


    class azure.mgmt.desktopvirtualization.models.RemoteApplicationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IN_BUILT = "InBuilt"
        MSIX_APPLICATION = "MsixApplication"


    class azure.mgmt.desktopvirtualization.models.Resource(Model):
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


    class azure.mgmt.desktopvirtualization.models.ResourceModelWithAllowedPropertySet(TrackedResource):
        etag: str
        id: str
        identity: ResourceModelWithAllowedPropertySetIdentity
        kind: str
        location: str
        managed_by: str
        name: str
        plan: ResourceModelWithAllowedPropertySetPlan
        sku: ResourceModelWithAllowedPropertySetSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                identity: Optional[ResourceModelWithAllowedPropertySetIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[ResourceModelWithAllowedPropertySetPlan] = ..., 
                sku: Optional[ResourceModelWithAllowedPropertySetSku] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceModelWithAllowedPropertySetIdentity(Identity):
        principal_id: str
        tenant_id: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Literal[SystemAssigned]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceModelWithAllowedPropertySetPlan(Plan):
        name: str
        product: str
        promotion_code: str
        publisher: str
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                product: str, 
                promotion_code: Optional[str] = ..., 
                publisher: str, 
                version: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceModelWithAllowedPropertySetSku(Sku):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceProviderOperation(Model):
        display: ResourceProviderOperationDisplay
        is_data_action: bool
        name: str
        properties: OperationProperties

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[ResourceProviderOperationDisplay] = ..., 
                is_data_action: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[OperationProperties] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceProviderOperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ResourceProviderOperationList(Model):
        next_link: str
        value: list[ResourceProviderOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ResourceProviderOperation]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SSOSecretType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CERTIFICATE = "Certificate"
        CERTIFICATE_IN_KEY_VAULT = "CertificateInKeyVault"
        SHARED_KEY = "SharedKey"
        SHARED_KEY_IN_KEY_VAULT = "SharedKeyInKeyVault"


    class azure.mgmt.desktopvirtualization.models.ScalingHostPoolReference(Model):
        host_pool_arm_path: str
        scaling_plan_enabled: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                host_pool_arm_path: Optional[str] = ..., 
                scaling_plan_enabled: Optional[bool] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingHostPoolType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        POOLED = "Pooled"


    class azure.mgmt.desktopvirtualization.models.ScalingPlan(ResourceModelWithAllowedPropertySet):
        description: str
        etag: str
        exclusion_tag: str
        friendly_name: str
        host_pool_references: list[ScalingHostPoolReference]
        host_pool_type: Union[str, ScalingHostPoolType]
        id: str
        identity: ResourceModelWithAllowedPropertySetIdentity
        kind: str
        location: str
        managed_by: str
        name: str
        object_id: str
        plan: ResourceModelWithAllowedPropertySetPlan
        schedules: list[ScalingSchedule]
        sku: ResourceModelWithAllowedPropertySetSku
        system_data: SystemData
        tags: dict[str, str]
        time_zone: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                exclusion_tag: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                host_pool_references: Optional[List[ScalingHostPoolReference]] = ..., 
                host_pool_type: Union[str, ScalingHostPoolType] = "Pooled", 
                identity: Optional[ResourceModelWithAllowedPropertySetIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[ResourceModelWithAllowedPropertySetPlan] = ..., 
                schedules: Optional[List[ScalingSchedule]] = ..., 
                sku: Optional[ResourceModelWithAllowedPropertySetSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time_zone: str, 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanList(Model):
        next_link: str
        value: list[ScalingPlan]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ScalingPlan]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPatch(Model):
        description: str
        exclusion_tag: str
        friendly_name: str
        host_pool_references: list[ScalingHostPoolReference]
        schedules: list[ScalingSchedule]
        tags: dict[str, str]
        time_zone: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                exclusion_tag: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                host_pool_references: Optional[List[ScalingHostPoolReference]] = ..., 
                schedules: Optional[List[ScalingSchedule]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                time_zone: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPersonalSchedule(ProxyResource):
        days_of_week: Union[list[str, DayOfWeek]]
        id: str
        name: str
        off_peak_action_on_disconnect: Union[str, SessionHandlingOperation]
        off_peak_action_on_logoff: Union[str, SessionHandlingOperation]
        off_peak_minutes_to_wait_on_disconnect: int
        off_peak_minutes_to_wait_on_logoff: int
        off_peak_start_time: Time
        off_peak_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        peak_action_on_disconnect: Union[str, SessionHandlingOperation]
        peak_action_on_logoff: Union[str, SessionHandlingOperation]
        peak_minutes_to_wait_on_disconnect: int
        peak_minutes_to_wait_on_logoff: int
        peak_start_time: Time
        peak_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        ramp_down_action_on_disconnect: Union[str, SessionHandlingOperation]
        ramp_down_action_on_logoff: Union[str, SessionHandlingOperation]
        ramp_down_minutes_to_wait_on_disconnect: int
        ramp_down_minutes_to_wait_on_logoff: int
        ramp_down_start_time: Time
        ramp_down_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        ramp_up_action_on_disconnect: Union[str, SessionHandlingOperation]
        ramp_up_action_on_logoff: Union[str, SessionHandlingOperation]
        ramp_up_auto_start_hosts: Union[str, StartupBehavior]
        ramp_up_minutes_to_wait_on_disconnect: int
        ramp_up_minutes_to_wait_on_logoff: int
        ramp_up_start_time: Time
        ramp_up_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_of_week: Optional[List[Union[str, DayOfWeek]]] = ..., 
                off_peak_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                off_peak_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                off_peak_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                off_peak_minutes_to_wait_on_logoff: Optional[int] = ..., 
                off_peak_start_time: Optional[Time] = ..., 
                off_peak_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                peak_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                peak_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                peak_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                peak_minutes_to_wait_on_logoff: Optional[int] = ..., 
                peak_start_time: Optional[Time] = ..., 
                peak_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                ramp_down_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_down_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_down_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                ramp_down_minutes_to_wait_on_logoff: Optional[int] = ..., 
                ramp_down_start_time: Optional[Time] = ..., 
                ramp_down_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                ramp_up_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_up_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_up_auto_start_hosts: Optional[Union[str, StartupBehavior]] = ..., 
                ramp_up_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                ramp_up_minutes_to_wait_on_logoff: Optional[int] = ..., 
                ramp_up_start_time: Optional[Time] = ..., 
                ramp_up_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPersonalScheduleList(Model):
        next_link: str
        value: list[ScalingPlanPersonalSchedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ScalingPlanPersonalSchedule]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPersonalSchedulePatch(Model):
        days_of_week: Union[list[str, DayOfWeek]]
        off_peak_action_on_disconnect: Union[str, SessionHandlingOperation]
        off_peak_action_on_logoff: Union[str, SessionHandlingOperation]
        off_peak_minutes_to_wait_on_disconnect: int
        off_peak_minutes_to_wait_on_logoff: int
        off_peak_start_time: Time
        off_peak_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        peak_action_on_disconnect: Union[str, SessionHandlingOperation]
        peak_action_on_logoff: Union[str, SessionHandlingOperation]
        peak_minutes_to_wait_on_disconnect: int
        peak_minutes_to_wait_on_logoff: int
        peak_start_time: Time
        peak_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        ramp_down_action_on_disconnect: Union[str, SessionHandlingOperation]
        ramp_down_action_on_logoff: Union[str, SessionHandlingOperation]
        ramp_down_minutes_to_wait_on_disconnect: int
        ramp_down_minutes_to_wait_on_logoff: int
        ramp_down_start_time: Time
        ramp_down_start_vm_on_connect: Union[str, SetStartVMOnConnect]
        ramp_up_action_on_disconnect: Union[str, SessionHandlingOperation]
        ramp_up_action_on_logoff: Union[str, SessionHandlingOperation]
        ramp_up_auto_start_hosts: Union[str, StartupBehavior]
        ramp_up_minutes_to_wait_on_disconnect: int
        ramp_up_minutes_to_wait_on_logoff: int
        ramp_up_start_time: Time
        ramp_up_start_vm_on_connect: Union[str, SetStartVMOnConnect]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_of_week: Optional[List[Union[str, DayOfWeek]]] = ..., 
                off_peak_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                off_peak_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                off_peak_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                off_peak_minutes_to_wait_on_logoff: Optional[int] = ..., 
                off_peak_start_time: Optional[Time] = ..., 
                off_peak_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                peak_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                peak_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                peak_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                peak_minutes_to_wait_on_logoff: Optional[int] = ..., 
                peak_start_time: Optional[Time] = ..., 
                peak_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                ramp_down_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_down_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_down_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                ramp_down_minutes_to_wait_on_logoff: Optional[int] = ..., 
                ramp_down_start_time: Optional[Time] = ..., 
                ramp_down_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
                ramp_up_action_on_disconnect: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_up_action_on_logoff: Optional[Union[str, SessionHandlingOperation]] = ..., 
                ramp_up_auto_start_hosts: Optional[Union[str, StartupBehavior]] = ..., 
                ramp_up_minutes_to_wait_on_disconnect: Optional[int] = ..., 
                ramp_up_minutes_to_wait_on_logoff: Optional[int] = ..., 
                ramp_up_start_time: Optional[Time] = ..., 
                ramp_up_start_vm_on_connect: Optional[Union[str, SetStartVMOnConnect]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPooledSchedule(Resource):
        days_of_week: Union[list[str, DayOfWeek]]
        id: str
        name: str
        off_peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        off_peak_start_time: Time
        peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        peak_start_time: Time
        ramp_down_capacity_threshold_pct: int
        ramp_down_force_logoff_users: bool
        ramp_down_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_down_minimum_hosts_pct: int
        ramp_down_notification_message: str
        ramp_down_start_time: Time
        ramp_down_stop_hosts_when: Union[str, StopHostsWhen]
        ramp_down_wait_time_minutes: int
        ramp_up_capacity_threshold_pct: int
        ramp_up_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_up_minimum_hosts_pct: int
        ramp_up_start_time: Time
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_of_week: Optional[List[Union[str, DayOfWeek]]] = ..., 
                off_peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                off_peak_start_time: Optional[Time] = ..., 
                peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                peak_start_time: Optional[Time] = ..., 
                ramp_down_capacity_threshold_pct: Optional[int] = ..., 
                ramp_down_force_logoff_users: Optional[bool] = ..., 
                ramp_down_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_down_minimum_hosts_pct: Optional[int] = ..., 
                ramp_down_notification_message: Optional[str] = ..., 
                ramp_down_start_time: Optional[Time] = ..., 
                ramp_down_stop_hosts_when: Optional[Union[str, StopHostsWhen]] = ..., 
                ramp_down_wait_time_minutes: Optional[int] = ..., 
                ramp_up_capacity_threshold_pct: Optional[int] = ..., 
                ramp_up_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_up_minimum_hosts_pct: Optional[int] = ..., 
                ramp_up_start_time: Optional[Time] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPooledScheduleList(Model):
        next_link: str
        value: list[ScalingPlanPooledSchedule]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[ScalingPlanPooledSchedule]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingPlanPooledSchedulePatch(Resource):
        days_of_week: Union[list[str, DayOfWeek]]
        id: str
        name: str
        off_peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        off_peak_start_time: Time
        peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        peak_start_time: Time
        ramp_down_capacity_threshold_pct: int
        ramp_down_force_logoff_users: bool
        ramp_down_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_down_minimum_hosts_pct: int
        ramp_down_notification_message: str
        ramp_down_start_time: Time
        ramp_down_stop_hosts_when: Union[str, StopHostsWhen]
        ramp_down_wait_time_minutes: int
        ramp_up_capacity_threshold_pct: int
        ramp_up_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_up_minimum_hosts_pct: int
        ramp_up_start_time: Time
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_of_week: Optional[List[Union[str, DayOfWeek]]] = ..., 
                off_peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                off_peak_start_time: Optional[Time] = ..., 
                peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                peak_start_time: Optional[Time] = ..., 
                ramp_down_capacity_threshold_pct: Optional[int] = ..., 
                ramp_down_force_logoff_users: Optional[bool] = ..., 
                ramp_down_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_down_minimum_hosts_pct: Optional[int] = ..., 
                ramp_down_notification_message: Optional[str] = ..., 
                ramp_down_start_time: Optional[Time] = ..., 
                ramp_down_stop_hosts_when: Optional[Union[str, StopHostsWhen]] = ..., 
                ramp_down_wait_time_minutes: Optional[int] = ..., 
                ramp_up_capacity_threshold_pct: Optional[int] = ..., 
                ramp_up_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_up_minimum_hosts_pct: Optional[int] = ..., 
                ramp_up_start_time: Optional[Time] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingSchedule(Model):
        days_of_week: Union[list[str, ScalingScheduleDaysOfWeekItem]]
        name: str
        off_peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        off_peak_start_time: Time
        peak_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        peak_start_time: Time
        ramp_down_capacity_threshold_pct: int
        ramp_down_force_logoff_users: bool
        ramp_down_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_down_minimum_hosts_pct: int
        ramp_down_notification_message: str
        ramp_down_start_time: Time
        ramp_down_stop_hosts_when: Union[str, StopHostsWhen]
        ramp_down_wait_time_minutes: int
        ramp_up_capacity_threshold_pct: int
        ramp_up_load_balancing_algorithm: Union[str, SessionHostLoadBalancingAlgorithm]
        ramp_up_minimum_hosts_pct: int
        ramp_up_start_time: Time

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                days_of_week: Optional[List[Union[str, ScalingScheduleDaysOfWeekItem]]] = ..., 
                name: Optional[str] = ..., 
                off_peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                off_peak_start_time: Optional[Time] = ..., 
                peak_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                peak_start_time: Optional[Time] = ..., 
                ramp_down_capacity_threshold_pct: Optional[int] = ..., 
                ramp_down_force_logoff_users: Optional[bool] = ..., 
                ramp_down_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_down_minimum_hosts_pct: Optional[int] = ..., 
                ramp_down_notification_message: Optional[str] = ..., 
                ramp_down_start_time: Optional[Time] = ..., 
                ramp_down_stop_hosts_when: Optional[Union[str, StopHostsWhen]] = ..., 
                ramp_down_wait_time_minutes: Optional[int] = ..., 
                ramp_up_capacity_threshold_pct: Optional[int] = ..., 
                ramp_up_load_balancing_algorithm: Optional[Union[str, SessionHostLoadBalancingAlgorithm]] = ..., 
                ramp_up_minimum_hosts_pct: Optional[int] = ..., 
                ramp_up_start_time: Optional[Time] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ScalingScheduleDaysOfWeekItem(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FRIDAY = "Friday"
        MONDAY = "Monday"
        SATURDAY = "Saturday"
        SUNDAY = "Sunday"
        THURSDAY = "Thursday"
        TUESDAY = "Tuesday"
        WEDNESDAY = "Wednesday"


    class azure.mgmt.desktopvirtualization.models.SendMessage(Model):
        message_body: str
        message_title: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message_body: Optional[str] = ..., 
                message_title: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.ServiceSpecification(Model):
        log_specifications: list[LogSpecification]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                log_specifications: Optional[List[LogSpecification]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SessionHandlingOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEALLOCATE = "Deallocate"
        HIBERNATE = "Hibernate"
        NONE = "None"


    class azure.mgmt.desktopvirtualization.models.SessionHost(Resource):
        agent_version: str
        allow_new_session: bool
        assigned_user: str
        friendly_name: str
        id: str
        last_heart_beat: datetime
        last_update_time: datetime
        name: str
        object_id: str
        os_version: str
        resource_id: str
        session_host_health_check_results: list[SessionHostHealthCheckReport]
        sessions: int
        status: Union[str, Status]
        status_timestamp: datetime
        sx_s_stack_version: str
        system_data: SystemData
        type: str
        update_error_message: str
        update_state: Union[str, UpdateState]
        virtual_machine_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_version: Optional[str] = ..., 
                allow_new_session: Optional[bool] = ..., 
                assigned_user: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                last_heart_beat: Optional[datetime] = ..., 
                os_version: Optional[str] = ..., 
                sessions: Optional[int] = ..., 
                status: Optional[Union[str, Status]] = ..., 
                sx_s_stack_version: Optional[str] = ..., 
                update_error_message: Optional[str] = ..., 
                update_state: Optional[Union[str, UpdateState]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SessionHostComponentUpdateType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        SCHEDULED = "Scheduled"


    class azure.mgmt.desktopvirtualization.models.SessionHostHealthCheckFailureDetails(Model):
        error_code: int
        last_health_check_date_time: datetime
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


    class azure.mgmt.desktopvirtualization.models.SessionHostHealthCheckReport(Model):
        additional_failure_details: SessionHostHealthCheckFailureDetails
        health_check_name: Union[str, HealthCheckName]
        health_check_result: Union[str, HealthCheckResult]

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


    class azure.mgmt.desktopvirtualization.models.SessionHostList(Model):
        next_link: str
        value: list[SessionHost]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[SessionHost]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SessionHostLoadBalancingAlgorithm(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BREADTH_FIRST = "BreadthFirst"
        DEPTH_FIRST = "DepthFirst"


    class azure.mgmt.desktopvirtualization.models.SessionHostPatch(Resource):
        allow_new_session: bool
        assigned_user: str
        friendly_name: str
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                allow_new_session: Optional[bool] = ..., 
                assigned_user: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SessionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        DISCONNECTED = "Disconnected"
        LOG_OFF = "LogOff"
        PENDING = "Pending"
        UNKNOWN = "Unknown"
        USER_PROFILE_DISK_MOUNTED = "UserProfileDiskMounted"


    class azure.mgmt.desktopvirtualization.models.SetStartVMOnConnect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE = "Disable"
        ENABLE = "Enable"


    class azure.mgmt.desktopvirtualization.models.Sku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: Union[str, SkuTier]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: str, 
                size: Optional[str] = ..., 
                tier: Optional[Union[str, SkuTier]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BASIC = "Basic"
        FREE = "Free"
        PREMIUM = "Premium"
        STANDARD = "Standard"


    class azure.mgmt.desktopvirtualization.models.StartMenuItem(Resource):
        app_alias: str
        command_line_arguments: str
        file_path: str
        icon_index: int
        icon_path: str
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_alias: Optional[str] = ..., 
                command_line_arguments: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                icon_index: Optional[int] = ..., 
                icon_path: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.StartMenuItemList(Model):
        next_link: str
        value: list[StartMenuItem]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[StartMenuItem]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.StartupBehavior(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        NONE = "None"
        WITH_ASSIGNED_USER = "WithAssignedUser"


    class azure.mgmt.desktopvirtualization.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DISCONNECTED = "Disconnected"
        DOMAIN_TRUST_RELATIONSHIP_LOST = "DomainTrustRelationshipLost"
        FS_LOGIX_NOT_HEALTHY = "FSLogixNotHealthy"
        NEEDS_ASSISTANCE = "NeedsAssistance"
        NOT_JOINED_TO_DOMAIN = "NotJoinedToDomain"
        NO_HEARTBEAT = "NoHeartbeat"
        SHUTDOWN = "Shutdown"
        SX_S_STACK_LISTENER_NOT_READY = "SxSStackListenerNotReady"
        UNAVAILABLE = "Unavailable"
        UPGRADE_FAILED = "UpgradeFailed"
        UPGRADING = "Upgrading"


    class azure.mgmt.desktopvirtualization.models.StopHostsWhen(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ZERO_ACTIVE_SESSIONS = "ZeroActiveSessions"
        ZERO_SESSIONS = "ZeroSessions"


    class azure.mgmt.desktopvirtualization.models.SystemData(Model):
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


    class azure.mgmt.desktopvirtualization.models.Time(Model):
        hour: int
        minute: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                hour: int, 
                minute: int, 
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


    class azure.mgmt.desktopvirtualization.models.TrackedResource(Resource):
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


    class azure.mgmt.desktopvirtualization.models.UpdateState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        INITIAL = "Initial"
        PENDING = "Pending"
        STARTED = "Started"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.desktopvirtualization.models.UserSession(Resource):
        active_directory_user_name: str
        application_type: Union[str, ApplicationType]
        create_time: datetime
        id: str
        name: str
        object_id: str
        session_state: Union[str, SessionState]
        system_data: SystemData
        type: str
        user_principal_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                active_directory_user_name: Optional[str] = ..., 
                application_type: Optional[Union[str, ApplicationType]] = ..., 
                create_time: Optional[datetime] = ..., 
                session_state: Optional[Union[str, SessionState]] = ..., 
                user_principal_name: Optional[str] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.UserSessionList(Model):
        next_link: str
        value: list[UserSession]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[UserSession]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.Workspace(ResourceModelWithAllowedPropertySet):
        application_group_references: list[str]
        cloud_pc_resource: bool
        description: str
        etag: str
        friendly_name: str
        id: str
        identity: ResourceModelWithAllowedPropertySetIdentity
        kind: str
        location: str
        managed_by: str
        name: str
        object_id: str
        plan: ResourceModelWithAllowedPropertySetPlan
        private_endpoint_connections: list[PrivateEndpointConnection]
        public_network_access: Union[str, PublicNetworkAccess]
        sku: ResourceModelWithAllowedPropertySetSku
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_group_references: Optional[List[str]] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                identity: Optional[ResourceModelWithAllowedPropertySetIdentity] = ..., 
                kind: Optional[str] = ..., 
                location: str, 
                managed_by: Optional[str] = ..., 
                plan: Optional[ResourceModelWithAllowedPropertySetPlan] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Optional[ResourceModelWithAllowedPropertySetSku] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.WorkspaceList(Model):
        next_link: str
        value: list[Workspace]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                value: Optional[List[Workspace]] = ..., 
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


    class azure.mgmt.desktopvirtualization.models.WorkspacePatch(Model):
        application_group_references: list[str]
        description: str
        friendly_name: str
        public_network_access: Union[str, PublicNetworkAccess]
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                application_group_references: Optional[List[str]] = ..., 
                description: Optional[str] = ..., 
                friendly_name: Optional[str] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
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


namespace azure.mgmt.desktopvirtualization.operations

    class azure.mgmt.desktopvirtualization.operations.AppAttachPackageInfoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def import_method(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                import_package_info_request: ImportPackageInfoRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[AppAttachPackage]: ...

        @overload
        def import_method(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                import_package_info_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[AppAttachPackage]: ...


    class azure.mgmt.desktopvirtualization.operations.AppAttachPackageOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package: AppAttachPackage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AppAttachPackage]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[AppAttachPackage]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package_patch: Optional[AppAttachPackagePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                app_attach_package_name: str, 
                app_attach_package_patch: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AppAttachPackage: ...


    class azure.mgmt.desktopvirtualization.operations.ApplicationGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: ApplicationGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ApplicationGroup]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                filter: Optional[str] = None, 
                **kwargs: Any
            ) -> Iterable[ApplicationGroup]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: Optional[ApplicationGroupPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_group: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ApplicationGroup: ...


    class azure.mgmt.desktopvirtualization.operations.ApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Application, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                **kwargs: Any
            ) -> Application: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Application]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Optional[ApplicationPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                application_name: str, 
                application: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Application: ...


    class azure.mgmt.desktopvirtualization.operations.DesktopsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                **kwargs: Any
            ) -> Desktop: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Desktop]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                desktop: Optional[DesktopPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Desktop: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                desktop_name: str, 
                desktop: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Desktop: ...


    class azure.mgmt.desktopvirtualization.operations.HostPoolsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: HostPool, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> HostPool: ...

        @distributed_trace
        def list(
                self, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[HostPool]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[HostPool]: ...

        @distributed_trace
        def list_registration_tokens(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> RegistrationTokenList: ...

        @distributed_trace
        def retrieve_registration_token(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                **kwargs: Any
            ) -> RegistrationInfo: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: Optional[HostPoolPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                host_pool: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HostPool: ...


    class azure.mgmt.desktopvirtualization.operations.MSIXPackagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: MSIXPackage, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[MSIXPackage]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: Optional[MSIXPackagePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_package_full_name: str, 
                msix_package: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> MSIXPackage: ...


    class azure.mgmt.desktopvirtualization.operations.MsixImagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_image_uri: MSIXImageURI, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ExpandMsixImage]: ...

        @overload
        def expand(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                msix_image_uri: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Iterable[ExpandMsixImage]: ...


    class azure.mgmt.desktopvirtualization.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[ResourceProviderOperation]: ...


    class azure.mgmt.desktopvirtualization.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @distributed_trace
        def get_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnectionWithSystemData]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Iterable[PrivateEndpointConnectionWithSystemData]: ...

        @overload
        def update_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        def update_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                private_endpoint_connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        def update_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                connection: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...

        @overload
        def update_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                private_endpoint_connection_name: str, 
                connection: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> PrivateEndpointConnectionWithSystemData: ...


    class azure.mgmt.desktopvirtualization.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...

        @distributed_trace
        def list_by_workspace(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[PrivateLinkResource]: ...


    class azure.mgmt.desktopvirtualization.operations.ScalingPlanPersonalSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: ScalingPlanPersonalSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ScalingPlanPersonalSchedule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[ScalingPlanPersonalSchedulePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPersonalSchedule: ...


    class azure.mgmt.desktopvirtualization.operations.ScalingPlanPooledSchedulesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: ScalingPlanPooledSchedule, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ScalingPlanPooledSchedule]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[ScalingPlanPooledSchedulePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan_schedule_name: str, 
                scaling_plan_schedule: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlanPooledSchedule: ...


    class azure.mgmt.desktopvirtualization.operations.ScalingPlansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: ScalingPlan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @overload
        def create(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ScalingPlan]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ScalingPlan]: ...

        @distributed_trace
        def list_by_subscription(
                self, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[ScalingPlan]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: Optional[ScalingPlanPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                scaling_plan_name: str, 
                scaling_plan: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ScalingPlan: ...


    class azure.mgmt.desktopvirtualization.operations.SessionHostsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                **kwargs: Any
            ) -> SessionHost: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[SessionHost]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                session_host: Optional[SessionHostPatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SessionHost: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                force: Optional[bool] = None, 
                session_host: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SessionHost: ...


    class azure.mgmt.desktopvirtualization.operations.StartMenuItemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                application_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[StartMenuItem]: ...


    class azure.mgmt.desktopvirtualization.operations.UserSessionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def disconnect(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                **kwargs: Any
            ) -> UserSession: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[UserSession]: ...

        @distributed_trace
        def list_by_host_pool(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                filter: Optional[str] = None, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[UserSession]: ...

        @overload
        def send_message(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                send_message: Optional[SendMessage] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def send_message(
                self, 
                resource_group_name: str, 
                host_pool_name: str, 
                session_host_name: str, 
                user_session_id: str, 
                send_message: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.desktopvirtualization.operations.WorkspacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Workspace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                **kwargs: Any
            ) -> Workspace: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                page_size: Optional[int] = None, 
                is_descending: Optional[bool] = None, 
                initial_skip: Optional[int] = None, 
                **kwargs: Any
            ) -> Iterable[Workspace]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[Workspace]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Optional[WorkspacePatch] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                workspace_name: str, 
                workspace: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Workspace: ...


```