```py
namespace azure.mgmt.providerhub

    class azure.mgmt.providerhub.ProviderHubMgmtClient(_ProviderHubMgmtClientOperationsMixin): implements ContextManager 
        authorized_applications: AuthorizedApplicationsOperations
        custom_rollouts: CustomRolloutsOperations
        default_rollouts: DefaultRolloutsOperations
        new_region_frontload_release: NewRegionFrontloadReleaseOperations
        notification_registrations: NotificationRegistrationsOperations
        operations: Operations
        provider_monitor_settings: ProviderMonitorSettingsOperations
        provider_registrations: ProviderRegistrationsOperations
        resource_actions: ResourceActionsOperations
        resource_type_registrations: ResourceTypeRegistrationsOperations
        skus: SkusOperations

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
        def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: CheckinManifestParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        @overload
        def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: CheckinManifestParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        @overload
        def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        def close(self) -> None: ...

        @distributed_trace
        def generate_manifest(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...


namespace azure.mgmt.providerhub.aio

    class azure.mgmt.providerhub.aio.ProviderHubMgmtClient(_ProviderHubMgmtClientOperationsMixin): implements AsyncContextManager 
        authorized_applications: AuthorizedApplicationsOperations
        custom_rollouts: CustomRolloutsOperations
        default_rollouts: DefaultRolloutsOperations
        new_region_frontload_release: NewRegionFrontloadReleaseOperations
        notification_registrations: NotificationRegistrationsOperations
        operations: Operations
        provider_monitor_settings: ProviderMonitorSettingsOperations
        provider_registrations: ProviderRegistrationsOperations
        resource_actions: ResourceActionsOperations
        resource_type_registrations: ResourceTypeRegistrationsOperations
        skus: SkusOperations

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
        async def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: CheckinManifestParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        @overload
        async def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: CheckinManifestParams, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        @overload
        async def checkin_manifest(
                self, 
                provider_namespace: str, 
                checkin_manifest_params: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckinManifestInfo: ...

        async def close(self) -> None: ...

        @distributed_trace_async
        async def generate_manifest(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...


namespace azure.mgmt.providerhub.aio.operations

    class azure.mgmt.providerhub.aio.operations.AuthorizedApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: AuthorizedApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthorizedApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: AuthorizedApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthorizedApplication]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AuthorizedApplication]: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                application_id: str, 
                **kwargs: Any
            ) -> AuthorizedApplication: ...

        @distributed_trace
        def list(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AuthorizedApplication]: ...


    class azure.mgmt.providerhub.aio.operations.CustomRolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: CustomRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomRollout]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: CustomRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomRollout]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CustomRollout]: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> CustomRollout: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CustomRollout]: ...

        @distributed_trace_async
        async def stop(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.aio.operations.DefaultRolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: DefaultRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DefaultRollout]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: DefaultRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DefaultRollout]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DefaultRollout]: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DefaultRollout]: ...

        @distributed_trace_async
        async def stop(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.aio.operations.NewRegionFrontloadReleaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        async def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @overload
        async def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @overload
        async def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                release_name: str, 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @distributed_trace_async
        async def stop(
                self, 
                provider_namespace: str, 
                release_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.aio.operations.NotificationRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: NotificationRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: NotificationRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NotificationRegistration]: ...


    class azure.mgmt.providerhub.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: OperationsPutContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: OperationsPutContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationsDefinition]: ...

        @distributed_trace_async
        async def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> List[OperationsDefinition]: ...


    class azure.mgmt.providerhub.aio.operations.ProviderMonitorSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: ProviderMonitorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderMonitorSetting]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: ProviderMonitorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderMonitorSetting]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderMonitorSetting]: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> ProviderMonitorSetting: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProviderMonitorSetting]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ProviderMonitorSetting]: ...

        @distributed_trace_async
        async def update(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> ProviderMonitorSetting: ...


    class azure.mgmt.providerhub.aio.operations.ProviderRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: ProviderRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: ProviderRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ProviderRegistration]: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def generate_operations(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> List[OperationsDefinition]: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ProviderRegistration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[ProviderRegistration]: ...


    class azure.mgmt.providerhub.aio.operations.ResourceActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: ResourceManagementAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: ResourceManagementAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...


    class azure.mgmt.providerhub.aio.operations.ResourceTypeRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: ResourceTypeRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceTypeRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: ResourceTypeRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceTypeRegistration]: ...

        @overload
        async def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ResourceTypeRegistration]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> ResourceTypeRegistration: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ResourceTypeRegistration]: ...


    class azure.mgmt.providerhub.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        async def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace_async
        async def delete(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def delete_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace_async
        async def get_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace_async
        async def get_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace_async
        async def get_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def list_by_resource_type_registrations(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuResource]: ...


namespace azure.mgmt.providerhub.models

    class azure.mgmt.providerhub.models.AdditionalAuthorization(_Model):
        application_id: Optional[str]
        role_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AdditionalOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED_ASYNC_OPERATION_POLLING = "ProtectedAsyncOperationPolling"
        PROTECTED_ASYNC_OPERATION_POLLING_AUDIT_ONLY = "ProtectedAsyncOperationPollingAuditOnly"


    class azure.mgmt.providerhub.models.AdditionalOptionsAsyncOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED_ASYNC_OPERATION_POLLING = "ProtectedAsyncOperationPolling"
        PROTECTED_ASYNC_OPERATION_POLLING_AUDIT_ONLY = "ProtectedAsyncOperationPollingAuditOnly"


    class azure.mgmt.providerhub.models.AdditionalOptionsResourceTypeRegistration(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PROTECTED_ASYNC_OPERATION_POLLING = "ProtectedAsyncOperationPolling"
        PROTECTED_ASYNC_OPERATION_POLLING_AUDIT_ONLY = "ProtectedAsyncOperationPollingAuditOnly"


    class azure.mgmt.providerhub.models.AllowedResourceName(_Model):
        get_action_verb: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                get_action_verb: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AllowedUnauthorizedActionsExtension(_Model):
        action: Optional[str]
        intent: Optional[Union[str, Intent]]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[str] = ..., 
                intent: Optional[Union[str, Intent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ApiProfile(_Model):
        api_version: Optional[str]
        profile_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                profile_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ApplicationDataAuthorization(_Model):
        resource_types: Optional[list[str]]
        role: Union[str, Role]

        @overload
        def __init__(
                self, 
                *, 
                resource_types: Optional[list[str]] = ..., 
                role: Union[str, Role]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ApplicationProviderAuthorization(_Model):
        managed_by_role_definition_id: Optional[str]
        role_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                managed_by_role_definition_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AsyncOperationPollingRules(_Model):
        additional_options: Optional[Union[str, AdditionalOptionsAsyncOperation]]
        authorization_actions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                additional_options: Optional[Union[str, AdditionalOptionsAsyncOperation]] = ..., 
                authorization_actions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AsyncTimeoutRule(_Model):
        action_name: Optional[str]
        timeout: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_name: Optional[str] = ..., 
                timeout: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AuthenticationScheme(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEARER = "Bearer"
        PO_P = "PoP"


    class azure.mgmt.providerhub.models.AuthorizationActionMapping(_Model):
        desired: Optional[str]
        original: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                desired: Optional[str] = ..., 
                original: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AuthorizedApplication(ProxyResource):
        id: str
        name: str
        properties: Optional[AuthorizedApplicationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AuthorizedApplicationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AuthorizedApplicationProperties(_Model):
        data_authorizations: Optional[list[ApplicationDataAuthorization]]
        provider_authorization: Optional[ApplicationProviderAuthorization]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                data_authorizations: Optional[list[ApplicationDataAuthorization]] = ..., 
                provider_authorization: Optional[ApplicationProviderAuthorization] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.AvailabilityZonePolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MULTI_ZONED = "MultiZoned"
        NOT_SPECIFIED = "NotSpecified"
        SINGLE_ZONED = "SingleZoned"


    class azure.mgmt.providerhub.models.AvailableCheckInManifestEnvironment(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        CANARY = "Canary"
        FAIRFAX = "Fairfax"
        MOONCAKE = "Mooncake"
        NOT_SPECIFIED = "NotSpecified"
        PROD = "Prod"


    class azure.mgmt.providerhub.models.BlockActionVerb(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION = "Action"
        DELETE = "Delete"
        NOT_SPECIFIED = "NotSpecified"
        READ = "Read"
        UNRECOGNIZED = "Unrecognized"
        WRITE = "Write"


    class azure.mgmt.providerhub.models.CanaryTrafficRegionRolloutConfiguration(_Model):
        regions: Optional[list[str]]
        skip_regions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                skip_regions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CapacityPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        RESTRICTED = "Restricted"


    class azure.mgmt.providerhub.models.CheckNameAvailabilitySpecifications(_Model):
        enable_default_validation: Optional[bool]
        resource_types_with_custom_validation: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                enable_default_validation: Optional[bool] = ..., 
                resource_types_with_custom_validation: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CheckinManifestInfo(_Model):
        commit_id: Optional[str]
        is_checked_in: bool
        pull_request: Optional[str]
        status_message: str

        @overload
        def __init__(
                self, 
                *, 
                commit_id: Optional[str] = ..., 
                is_checked_in: bool, 
                pull_request: Optional[str] = ..., 
                status_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CheckinManifestParams(_Model):
        baseline_arm_manifest_location: str
        environment: str

        @overload
        def __init__(
                self, 
                *, 
                baseline_arm_manifest_location: str, 
                environment: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CommonApiVersionsMergeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MERGE = "Merge"
        OVERWRITE = "Overwrite"


    class azure.mgmt.providerhub.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.providerhub.models.CrossTenantTokenValidation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENSURE_SECURE_VALIDATION = "EnsureSecureValidation"
        PASSTHROUGH_INSECURE_TOKEN = "PassthroughInsecureToken"


    class azure.mgmt.providerhub.models.CustomRollout(ProxyResource):
        id: str
        name: str
        properties: CustomRolloutProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: CustomRolloutProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        specification: CustomRolloutPropertiesSpecification
        status: Optional[CustomRolloutPropertiesStatus]

        @overload
        def __init__(
                self, 
                *, 
                specification: CustomRolloutPropertiesSpecification, 
                status: Optional[CustomRolloutPropertiesStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutPropertiesSpecification(CustomRolloutSpecification):
        auto_provision_config: CustomRolloutSpecificationAutoProvisionConfig
        canary: CustomRolloutSpecificationCanary
        provider_registration: CustomRolloutSpecificationProviderRegistration
        refresh_subscription_registration: bool
        release_scopes: list[str]
        resource_type_registrations: list[ResourceTypeRegistration]
        skip_release_scope_validation: bool

        @overload
        def __init__(
                self, 
                *, 
                auto_provision_config: Optional[CustomRolloutSpecificationAutoProvisionConfig] = ..., 
                canary: Optional[CustomRolloutSpecificationCanary] = ..., 
                provider_registration: Optional[CustomRolloutSpecificationProviderRegistration] = ..., 
                refresh_subscription_registration: Optional[bool] = ..., 
                release_scopes: Optional[list[str]] = ..., 
                resource_type_registrations: Optional[list[ResourceTypeRegistration]] = ..., 
                skip_release_scope_validation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutPropertiesStatus(CustomRolloutStatus):
        completed_regions: list[str]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: CustomRolloutStatusManifestCheckinStatus

        @overload
        def __init__(
                self, 
                *, 
                completed_regions: Optional[list[str]] = ..., 
                failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]] = ..., 
                manifest_checkin_status: Optional[CustomRolloutStatusManifestCheckinStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutSpecification(_Model):
        auto_provision_config: Optional[CustomRolloutSpecificationAutoProvisionConfig]
        canary: Optional[CustomRolloutSpecificationCanary]
        provider_registration: Optional[CustomRolloutSpecificationProviderRegistration]
        refresh_subscription_registration: Optional[bool]
        release_scopes: Optional[list[str]]
        resource_type_registrations: Optional[list[ResourceTypeRegistration]]
        skip_release_scope_validation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                auto_provision_config: Optional[CustomRolloutSpecificationAutoProvisionConfig] = ..., 
                canary: Optional[CustomRolloutSpecificationCanary] = ..., 
                provider_registration: Optional[CustomRolloutSpecificationProviderRegistration] = ..., 
                refresh_subscription_registration: Optional[bool] = ..., 
                release_scopes: Optional[list[str]] = ..., 
                resource_type_registrations: Optional[list[ResourceTypeRegistration]] = ..., 
                skip_release_scope_validation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutSpecificationAutoProvisionConfig(_Model):
        resource_graph: Optional[bool]
        storage: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                resource_graph: Optional[bool] = ..., 
                storage: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutSpecificationCanary(TrafficRegions):
        regions: list[str]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutSpecificationProviderRegistration(ProviderRegistration):
        id: str
        kind: Union[str, ProviderRegistrationKind]
        name: str
        properties: ProviderRegistrationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ProviderRegistrationKind]] = ..., 
                properties: Optional[ProviderRegistrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutStatus(_Model):
        completed_regions: Optional[list[str]]
        failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]]
        manifest_checkin_status: Optional[CustomRolloutStatusManifestCheckinStatus]

        @overload
        def __init__(
                self, 
                *, 
                completed_regions: Optional[list[str]] = ..., 
                failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]] = ..., 
                manifest_checkin_status: Optional[CustomRolloutStatusManifestCheckinStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.CustomRolloutStatusManifestCheckinStatus(CheckinManifestInfo):
        commit_id: str
        is_checked_in: bool
        pull_request: str
        status_message: str

        @overload
        def __init__(
                self, 
                *, 
                commit_id: Optional[str] = ..., 
                is_checked_in: bool, 
                pull_request: Optional[str] = ..., 
                status_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DataBoundary(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EU = "EU"
        GLOBAL = "Global"
        NOT_DEFINED = "NotDefined"
        US = "US"


    class azure.mgmt.providerhub.models.DefaultRollout(ProxyResource):
        id: str
        name: str
        properties: Optional[DefaultRolloutProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DefaultRolloutProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        specification: Optional[DefaultRolloutPropertiesSpecification]
        status: Optional[DefaultRolloutPropertiesStatus]

        @overload
        def __init__(
                self, 
                *, 
                specification: Optional[DefaultRolloutPropertiesSpecification] = ..., 
                status: Optional[DefaultRolloutPropertiesStatus] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutPropertiesSpecification(DefaultRolloutSpecification):
        auto_provision_config: DefaultRolloutSpecificationAutoProvisionConfig
        canary: DefaultRolloutSpecificationCanary
        expedited_rollout: DefaultRolloutSpecificationExpeditedRollout
        high_traffic: DefaultRolloutSpecificationHighTraffic
        low_traffic: DefaultRolloutSpecificationLowTraffic
        medium_traffic: DefaultRolloutSpecificationMediumTraffic
        provider_registration: DefaultRolloutSpecificationProviderRegistration
        resource_type_registrations: list[ResourceTypeRegistration]
        rest_of_the_world_group_one: DefaultRolloutSpecificationRestOfTheWorldGroupOne
        rest_of_the_world_group_two: DefaultRolloutSpecificationRestOfTheWorldGroupTwo

        @overload
        def __init__(
                self, 
                *, 
                auto_provision_config: Optional[DefaultRolloutSpecificationAutoProvisionConfig] = ..., 
                canary: Optional[DefaultRolloutSpecificationCanary] = ..., 
                expedited_rollout: Optional[DefaultRolloutSpecificationExpeditedRollout] = ..., 
                high_traffic: Optional[DefaultRolloutSpecificationHighTraffic] = ..., 
                low_traffic: Optional[DefaultRolloutSpecificationLowTraffic] = ..., 
                medium_traffic: Optional[DefaultRolloutSpecificationMediumTraffic] = ..., 
                provider_registration: Optional[DefaultRolloutSpecificationProviderRegistration] = ..., 
                resource_type_registrations: Optional[list[ResourceTypeRegistration]] = ..., 
                rest_of_the_world_group_one: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupOne] = ..., 
                rest_of_the_world_group_two: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupTwo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutPropertiesStatus(DefaultRolloutStatus):
        completed_regions: list[str]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: DefaultRolloutStatusManifestCheckinStatus
        next_traffic_region: Union[str, TrafficRegionCategory]
        next_traffic_region_scheduled_time: datetime
        subscription_reregistration_result: Union[str, SubscriptionReregistrationResult]

        @overload
        def __init__(
                self, 
                *, 
                completed_regions: Optional[list[str]] = ..., 
                failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]] = ..., 
                manifest_checkin_status: Optional[DefaultRolloutStatusManifestCheckinStatus] = ..., 
                next_traffic_region: Optional[Union[str, TrafficRegionCategory]] = ..., 
                next_traffic_region_scheduled_time: Optional[datetime] = ..., 
                subscription_reregistration_result: Optional[Union[str, SubscriptionReregistrationResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecification(_Model):
        auto_provision_config: Optional[DefaultRolloutSpecificationAutoProvisionConfig]
        canary: Optional[DefaultRolloutSpecificationCanary]
        expedited_rollout: Optional[DefaultRolloutSpecificationExpeditedRollout]
        high_traffic: Optional[DefaultRolloutSpecificationHighTraffic]
        low_traffic: Optional[DefaultRolloutSpecificationLowTraffic]
        medium_traffic: Optional[DefaultRolloutSpecificationMediumTraffic]
        provider_registration: Optional[DefaultRolloutSpecificationProviderRegistration]
        resource_type_registrations: Optional[list[ResourceTypeRegistration]]
        rest_of_the_world_group_one: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupOne]
        rest_of_the_world_group_two: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupTwo]

        @overload
        def __init__(
                self, 
                *, 
                auto_provision_config: Optional[DefaultRolloutSpecificationAutoProvisionConfig] = ..., 
                canary: Optional[DefaultRolloutSpecificationCanary] = ..., 
                expedited_rollout: Optional[DefaultRolloutSpecificationExpeditedRollout] = ..., 
                high_traffic: Optional[DefaultRolloutSpecificationHighTraffic] = ..., 
                low_traffic: Optional[DefaultRolloutSpecificationLowTraffic] = ..., 
                medium_traffic: Optional[DefaultRolloutSpecificationMediumTraffic] = ..., 
                provider_registration: Optional[DefaultRolloutSpecificationProviderRegistration] = ..., 
                resource_type_registrations: Optional[list[ResourceTypeRegistration]] = ..., 
                rest_of_the_world_group_one: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupOne] = ..., 
                rest_of_the_world_group_two: Optional[DefaultRolloutSpecificationRestOfTheWorldGroupTwo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationAutoProvisionConfig(_Model):
        resource_graph: Optional[bool]
        storage: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                resource_graph: Optional[bool] = ..., 
                storage: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationCanary(CanaryTrafficRegionRolloutConfiguration):
        regions: list[str]
        skip_regions: list[str]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                skip_regions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationExpeditedRollout(ExpeditedRolloutDefinition):
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationHighTraffic(TrafficRegionRolloutConfiguration):
        regions: list[str]
        wait_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationLowTraffic(TrafficRegionRolloutConfiguration):
        regions: list[str]
        wait_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationMediumTraffic(TrafficRegionRolloutConfiguration):
        regions: list[str]
        wait_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationProviderRegistration(ProviderRegistration):
        id: str
        kind: Union[str, ProviderRegistrationKind]
        name: str
        properties: ProviderRegistrationProperties
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ProviderRegistrationKind]] = ..., 
                properties: Optional[ProviderRegistrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationRestOfTheWorldGroupOne(TrafficRegionRolloutConfiguration):
        regions: list[str]
        wait_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutSpecificationRestOfTheWorldGroupTwo(TrafficRegionRolloutConfiguration):
        regions: list[str]
        wait_duration: timedelta

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutStatus(RolloutStatusBase):
        completed_regions: list[str]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: Optional[DefaultRolloutStatusManifestCheckinStatus]
        next_traffic_region: Optional[Union[str, TrafficRegionCategory]]
        next_traffic_region_scheduled_time: Optional[datetime]
        subscription_reregistration_result: Optional[Union[str, SubscriptionReregistrationResult]]

        @overload
        def __init__(
                self, 
                *, 
                completed_regions: Optional[list[str]] = ..., 
                failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]] = ..., 
                manifest_checkin_status: Optional[DefaultRolloutStatusManifestCheckinStatus] = ..., 
                next_traffic_region: Optional[Union[str, TrafficRegionCategory]] = ..., 
                next_traffic_region_scheduled_time: Optional[datetime] = ..., 
                subscription_reregistration_result: Optional[Union[str, SubscriptionReregistrationResult]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DefaultRolloutStatusManifestCheckinStatus(CheckinManifestInfo):
        commit_id: str
        is_checked_in: bool
        pull_request: str
        status_message: str

        @overload
        def __init__(
                self, 
                *, 
                commit_id: Optional[str] = ..., 
                is_checked_in: bool, 
                pull_request: Optional[str] = ..., 
                status_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DeleteDependency(_Model):
        linked_property: Optional[str]
        linked_type: Optional[str]
        required_features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                linked_property: Optional[str] = ..., 
                linked_type: Optional[str] = ..., 
                required_features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.DstsConfiguration(_Model):
        service_dns_name: Optional[str]
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.EndpointInformation(_Model):
        endpoint: Optional[str]
        endpoint_type: Optional[Union[str, NotificationEndpointType]]
        schema_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint: Optional[str] = ..., 
                endpoint_type: Optional[Union[str, NotificationEndpointType]] = ..., 
                schema_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.EndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANARY = "Canary"
        NOT_SPECIFIED = "NotSpecified"
        PRODUCTION = "Production"
        TEST_IN_PRODUCTION = "TestInProduction"


    class azure.mgmt.providerhub.models.EndpointTypeResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANARY = "Canary"
        NOT_SPECIFIED = "NotSpecified"
        PRODUCTION = "Production"
        TEST_IN_PRODUCTION = "TestInProduction"


    class azure.mgmt.providerhub.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.providerhub.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.providerhub.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ExpeditedRolloutDefinition(_Model):
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ExpeditedRolloutIntent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HOTFIX = "Hotfix"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ExtendedErrorInfo(_Model):
        additional_info: Optional[list[TypedErrorInfo]]
        code: Optional[str]
        details: Optional[list[ExtendedErrorInfo]]
        message: Optional[str]
        target: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_info: Optional[list[TypedErrorInfo]] = ..., 
                code: Optional[str] = ..., 
                details: Optional[list[ExtendedErrorInfo]] = ..., 
                message: Optional[str] = ..., 
                target: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ExtendedLocationOptions(_Model):
        supported_policy: Optional[Union[str, ResourceTypeExtendedLocationPolicy]]
        type: Optional[Union[str, ExtendedLocationType]]

        @overload
        def __init__(
                self, 
                *, 
                supported_policy: Optional[Union[str, ResourceTypeExtendedLocationPolicy]] = ..., 
                type: Optional[Union[str, ExtendedLocationType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ExtendedLocationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARC_ZONE = "ArcZone"
        CUSTOM_LOCATION = "CustomLocation"
        EDGE_ZONE = "EdgeZone"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ExtensionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEST_MATCH_OPERATION_BEGIN = "BestMatchOperationBegin"
        NOT_SPECIFIED = "NotSpecified"
        RESOURCE_CREATION_BEGIN = "ResourceCreationBegin"
        RESOURCE_CREATION_COMPLETED = "ResourceCreationCompleted"
        RESOURCE_CREATION_VALIDATE = "ResourceCreationValidate"
        RESOURCE_DELETION_BEGIN = "ResourceDeletionBegin"
        RESOURCE_DELETION_COMPLETED = "ResourceDeletionCompleted"
        RESOURCE_DELETION_VALIDATE = "ResourceDeletionValidate"
        RESOURCE_MOVE_BEGIN = "ResourceMoveBegin"
        RESOURCE_MOVE_COMPLETED = "ResourceMoveCompleted"
        RESOURCE_PATCH_BEGIN = "ResourcePatchBegin"
        RESOURCE_PATCH_COMPLETED = "ResourcePatchCompleted"
        RESOURCE_PATCH_VALIDATE = "ResourcePatchValidate"
        RESOURCE_POST_ACTION = "ResourcePostAction"
        RESOURCE_READ_BEGIN = "ResourceReadBegin"
        RESOURCE_READ_VALIDATE = "ResourceReadValidate"
        SUBSCRIPTION_LIFECYCLE_NOTIFICATION = "SubscriptionLifecycleNotification"
        SUBSCRIPTION_LIFECYCLE_NOTIFICATION_DELETION = "SubscriptionLifecycleNotificationDeletion"


    class azure.mgmt.providerhub.models.ExtensionOptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DO_NOT_MERGE_EXISTING_READ_ONLY_AND_SECRET_PROPERTIES = "DoNotMergeExistingReadOnlyAndSecretProperties"
        INCLUDE_INTERNAL_METADATA = "IncludeInternalMetadata"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ExtensionOptions(_Model):
        request: Optional[list[Union[str, ExtensionOptionType]]]
        response: Optional[list[Union[str, ExtensionOptionType]]]

        @overload
        def __init__(
                self, 
                *, 
                request: Optional[list[Union[str, ExtensionOptionType]]] = ..., 
                response: Optional[list[Union[str, ExtensionOptionType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FanoutLinkedNotificationRule(_Model):
        actions: Optional[list[str]]
        dsts_configuration: Optional[FanoutLinkedNotificationRuleDstsConfiguration]
        endpoints: Optional[list[ResourceProviderEndpoint]]
        token_auth_configuration: Optional[TokenAuthConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                dsts_configuration: Optional[FanoutLinkedNotificationRuleDstsConfiguration] = ..., 
                endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                token_auth_configuration: Optional[TokenAuthConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FanoutLinkedNotificationRuleDstsConfiguration(DstsConfiguration):
        service_dns_name: str
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FeaturesPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        ANY = "Any"


    class azure.mgmt.providerhub.models.FeaturesRule(_Model):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FilterOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENABLE_SUBSCRIPTION_FILTER_ON_TENANT = "EnableSubscriptionFilterOnTenant"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.FilterRule(_Model):
        endpoint_information: Optional[list[EndpointInformation]]
        filter_query: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_information: Optional[list[EndpointInformation]] = ..., 
                filter_query: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FrontdoorRequestMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        USE_MANIFEST = "UseManifest"


    class azure.mgmt.providerhub.models.FrontloadPayload(_Model):
        properties: FrontloadPayloadProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: FrontloadPayloadProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FrontloadPayloadProperties(_Model):
        copy_from_location: str
        environment_type: Union[str, AvailableCheckInManifestEnvironment]
        exclude_resource_types: list[str]
        frontload_location: str
        ignore_fields: list[str]
        include_resource_types: list[str]
        operation_type: str
        override_endpoint_level_fields: FrontloadPayloadPropertiesOverrideEndpointLevelFields
        override_manifest_level_fields: FrontloadPayloadPropertiesOverrideManifestLevelFields
        provider_namespace: str
        service_feature_flag: Union[str, ServiceFeatureFlagAction]

        @overload
        def __init__(
                self, 
                *, 
                copy_from_location: str, 
                environment_type: Union[str, AvailableCheckInManifestEnvironment], 
                exclude_resource_types: list[str], 
                frontload_location: str, 
                ignore_fields: list[str], 
                include_resource_types: list[str], 
                operation_type: str, 
                override_endpoint_level_fields: FrontloadPayloadPropertiesOverrideEndpointLevelFields, 
                override_manifest_level_fields: FrontloadPayloadPropertiesOverrideManifestLevelFields, 
                provider_namespace: str, 
                service_feature_flag: Union[str, ServiceFeatureFlagAction]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FrontloadPayloadPropertiesOverrideEndpointLevelFields(ResourceTypeEndpointBase):
        api_version: str
        api_versions: list[str]
        dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration
        enabled: bool
        endpoint_type: Union[str, EndpointType]
        endpoint_uri: str
        features_rule: ResourceTypeEndpointBaseFeaturesRule
        locations: list[str]
        required_features: list[str]
        sku_link: str
        timeout: timedelta
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                api_version: str, 
                api_versions: list[str], 
                dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration, 
                enabled: bool, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_uri: str, 
                features_rule: ResourceTypeEndpointBaseFeaturesRule, 
                locations: list[str], 
                required_features: list[str], 
                sku_link: str, 
                timeout: timedelta, 
                zones: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.FrontloadPayloadPropertiesOverrideManifestLevelFields(ManifestLevelPropertyBag):
        resource_hydration_accounts: list[ResourceHydrationAccount]

        @overload
        def __init__(
                self, 
                *, 
                resource_hydration_accounts: Optional[list[ResourceHydrationAccount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.IdentityManagement(_Model):
        type: Optional[Union[str, IdentityManagementTypes]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityManagementTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.IdentityManagementProperties(_Model):
        application_id: Optional[str]
        application_ids: Optional[list[str]]
        delegation_app_ids: Optional[list[str]]
        type: Optional[Union[str, IdentityManagementTypes]]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                application_ids: Optional[list[str]] = ..., 
                delegation_app_ids: Optional[list[str]] = ..., 
                type: Optional[Union[str, IdentityManagementTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.IdentityManagementTypes(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTOR = "Actor"
        DELEGATED_RESOURCE_IDENTITY = "DelegatedResourceIdentity"
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.providerhub.models.Intent(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFERRED_ACCESS_CHECK = "DEFERRED_ACCESS_CHECK"
        LOW_PRIVILEGE = "LOW_PRIVILEGE"
        NOT_SPECIFIED = "NOT_SPECIFIED"
        RP_CONTRACT = "RP_CONTRACT"


    class azure.mgmt.providerhub.models.LegacyDisallowedCondition(_Model):
        disallowed_legacy_operations: Optional[list[Union[str, LegacyOperation]]]
        feature: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                disallowed_legacy_operations: Optional[list[Union[str, LegacyOperation]]] = ..., 
                feature: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LegacyOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION = "Action"
        AZURE_ASYNC_OPERATION_WAITING = "AzureAsyncOperationWaiting"
        CREATE = "Create"
        DELETE = "Delete"
        DEPLOYMENT_CLEANUP = "DeploymentCleanup"
        EVALUATE_DEPLOYMENT_OUTPUT = "EvaluateDeploymentOutput"
        NOT_SPECIFIED = "NotSpecified"
        READ = "Read"
        RESOURCE_CACHE_WAITING = "ResourceCacheWaiting"
        WAITING = "Waiting"


    class azure.mgmt.providerhub.models.LightHouseAuthorization(_Model):
        principal_id: str
        role_definition_id: str

        @overload
        def __init__(
                self, 
                *, 
                principal_id: str, 
                role_definition_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LinkedAccessCheck(_Model):
        action_name: Optional[str]
        linked_action: Optional[str]
        linked_action_verb: Optional[str]
        linked_property: Optional[str]
        linked_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_name: Optional[str] = ..., 
                linked_action: Optional[str] = ..., 
                linked_action_verb: Optional[str] = ..., 
                linked_property: Optional[str] = ..., 
                linked_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LinkedAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOCKED = "Blocked"
        ENABLED = "Enabled"
        NOT_SPECIFIED = "NotSpecified"
        VALIDATE = "Validate"


    class azure.mgmt.providerhub.models.LinkedNotificationRule(_Model):
        actions: Optional[list[str]]
        actions_on_failed_operation: Optional[list[str]]
        fast_path_actions: Optional[list[str]]
        fast_path_actions_on_failed_operation: Optional[list[str]]
        linked_notification_timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                actions_on_failed_operation: Optional[list[str]] = ..., 
                fast_path_actions: Optional[list[str]] = ..., 
                fast_path_actions_on_failed_operation: Optional[list[str]] = ..., 
                linked_notification_timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LinkedOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CROSS_RESOURCE_GROUP_RESOURCE_MOVE = "CrossResourceGroupResourceMove"
        CROSS_SUBSCRIPTION_RESOURCE_MOVE = "CrossSubscriptionResourceMove"
        NONE = "None"


    class azure.mgmt.providerhub.models.LinkedOperationRule(_Model):
        depends_on_types: Optional[list[str]]
        linked_action: Union[str, LinkedAction]
        linked_operation: Union[str, LinkedOperation]

        @overload
        def __init__(
                self, 
                *, 
                depends_on_types: Optional[list[str]] = ..., 
                linked_action: Union[str, LinkedAction], 
                linked_operation: Union[str, LinkedOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDefinition(_Model):
        action_type: Optional[Union[str, OperationActionType]]
        display: LocalizedOperationDefinitionDisplay
        is_data_action: Optional[bool]
        name: str
        origin: Optional[Union[str, OperationOrigins]]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, OperationActionType]] = ..., 
                display: LocalizedOperationDefinitionDisplay, 
                is_data_action: Optional[bool] = ..., 
                name: str, 
                origin: Optional[Union[str, OperationOrigins]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDefinitionDisplay(LocalizedOperationDisplayDefinition):
        cs: LocalizedOperationDisplayDefinitionCs
        de: LocalizedOperationDisplayDefinitionDe
        default: LocalizedOperationDisplayDefinitionDefault
        en: LocalizedOperationDisplayDefinitionEn
        es: LocalizedOperationDisplayDefinitionEs
        fr: LocalizedOperationDisplayDefinitionFr
        hu: LocalizedOperationDisplayDefinitionHu
        it: LocalizedOperationDisplayDefinitionIt
        ja: LocalizedOperationDisplayDefinitionJa
        ko: LocalizedOperationDisplayDefinitionKo
        nl: LocalizedOperationDisplayDefinitionNl
        pl: LocalizedOperationDisplayDefinitionPl
        pt_br: LocalizedOperationDisplayDefinitionPtBR
        pt_pt: LocalizedOperationDisplayDefinitionPtPT
        ru: LocalizedOperationDisplayDefinitionRu
        sv: LocalizedOperationDisplayDefinitionSv
        zh_hans: LocalizedOperationDisplayDefinitionZhHans
        zh_hant: LocalizedOperationDisplayDefinitionZhHant

        @overload
        def __init__(
                self, 
                *, 
                cs: Optional[LocalizedOperationDisplayDefinitionCs] = ..., 
                de: Optional[LocalizedOperationDisplayDefinitionDe] = ..., 
                default: LocalizedOperationDisplayDefinitionDefault, 
                en: Optional[LocalizedOperationDisplayDefinitionEn] = ..., 
                es: Optional[LocalizedOperationDisplayDefinitionEs] = ..., 
                fr: Optional[LocalizedOperationDisplayDefinitionFr] = ..., 
                hu: Optional[LocalizedOperationDisplayDefinitionHu] = ..., 
                it: Optional[LocalizedOperationDisplayDefinitionIt] = ..., 
                ja: Optional[LocalizedOperationDisplayDefinitionJa] = ..., 
                ko: Optional[LocalizedOperationDisplayDefinitionKo] = ..., 
                nl: Optional[LocalizedOperationDisplayDefinitionNl] = ..., 
                pl: Optional[LocalizedOperationDisplayDefinitionPl] = ..., 
                pt_br: Optional[LocalizedOperationDisplayDefinitionPtBR] = ..., 
                pt_pt: Optional[LocalizedOperationDisplayDefinitionPtPT] = ..., 
                ru: Optional[LocalizedOperationDisplayDefinitionRu] = ..., 
                sv: Optional[LocalizedOperationDisplayDefinitionSv] = ..., 
                zh_hans: Optional[LocalizedOperationDisplayDefinitionZhHans] = ..., 
                zh_hant: Optional[LocalizedOperationDisplayDefinitionZhHant] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinition(_Model):
        cs: Optional[LocalizedOperationDisplayDefinitionCs]
        de: Optional[LocalizedOperationDisplayDefinitionDe]
        default: LocalizedOperationDisplayDefinitionDefault
        en: Optional[LocalizedOperationDisplayDefinitionEn]
        es: Optional[LocalizedOperationDisplayDefinitionEs]
        fr: Optional[LocalizedOperationDisplayDefinitionFr]
        hu: Optional[LocalizedOperationDisplayDefinitionHu]
        it: Optional[LocalizedOperationDisplayDefinitionIt]
        ja: Optional[LocalizedOperationDisplayDefinitionJa]
        ko: Optional[LocalizedOperationDisplayDefinitionKo]
        nl: Optional[LocalizedOperationDisplayDefinitionNl]
        pl: Optional[LocalizedOperationDisplayDefinitionPl]
        pt_br: Optional[LocalizedOperationDisplayDefinitionPtBR]
        pt_pt: Optional[LocalizedOperationDisplayDefinitionPtPT]
        ru: Optional[LocalizedOperationDisplayDefinitionRu]
        sv: Optional[LocalizedOperationDisplayDefinitionSv]
        zh_hans: Optional[LocalizedOperationDisplayDefinitionZhHans]
        zh_hant: Optional[LocalizedOperationDisplayDefinitionZhHant]

        @overload
        def __init__(
                self, 
                *, 
                cs: Optional[LocalizedOperationDisplayDefinitionCs] = ..., 
                de: Optional[LocalizedOperationDisplayDefinitionDe] = ..., 
                default: LocalizedOperationDisplayDefinitionDefault, 
                en: Optional[LocalizedOperationDisplayDefinitionEn] = ..., 
                es: Optional[LocalizedOperationDisplayDefinitionEs] = ..., 
                fr: Optional[LocalizedOperationDisplayDefinitionFr] = ..., 
                hu: Optional[LocalizedOperationDisplayDefinitionHu] = ..., 
                it: Optional[LocalizedOperationDisplayDefinitionIt] = ..., 
                ja: Optional[LocalizedOperationDisplayDefinitionJa] = ..., 
                ko: Optional[LocalizedOperationDisplayDefinitionKo] = ..., 
                nl: Optional[LocalizedOperationDisplayDefinitionNl] = ..., 
                pl: Optional[LocalizedOperationDisplayDefinitionPl] = ..., 
                pt_br: Optional[LocalizedOperationDisplayDefinitionPtBR] = ..., 
                pt_pt: Optional[LocalizedOperationDisplayDefinitionPtPT] = ..., 
                ru: Optional[LocalizedOperationDisplayDefinitionRu] = ..., 
                sv: Optional[LocalizedOperationDisplayDefinitionSv] = ..., 
                zh_hans: Optional[LocalizedOperationDisplayDefinitionZhHans] = ..., 
                zh_hant: Optional[LocalizedOperationDisplayDefinitionZhHant] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionCs(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionDe(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionDefault(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionEn(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionEs(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionFr(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionHu(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionIt(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionJa(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionKo(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionNl(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionPl(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionPtBR(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionPtPT(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionRu(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionSv(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionZhHans(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocalizedOperationDisplayDefinitionZhHant(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LocationQuotaRule(_Model):
        location: Optional[str]
        policy: Optional[Union[str, QuotaPolicy]]
        quota_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                policy: Optional[Union[str, QuotaPolicy]] = ..., 
                quota_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LoggingDetails(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BODY = "Body"
        NONE = "None"


    class azure.mgmt.providerhub.models.LoggingDirections(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REQUEST = "Request"
        RESPONSE = "Response"


    class azure.mgmt.providerhub.models.LoggingHiddenPropertyPath(_Model):
        hidden_paths_on_request: Optional[list[str]]
        hidden_paths_on_response: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                hidden_paths_on_request: Optional[list[str]] = ..., 
                hidden_paths_on_response: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LoggingRule(_Model):
        action: str
        detail_level: Union[str, LoggingDetails]
        direction: Union[str, LoggingDirections]
        hidden_property_paths: Optional[LoggingRuleHiddenPropertyPaths]

        @overload
        def __init__(
                self, 
                *, 
                action: str, 
                detail_level: Union[str, LoggingDetails], 
                direction: Union[str, LoggingDirections], 
                hidden_property_paths: Optional[LoggingRuleHiddenPropertyPaths] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.LoggingRuleHiddenPropertyPaths(LoggingHiddenPropertyPath):
        hidden_paths_on_request: list[str]
        hidden_paths_on_response: list[str]

        @overload
        def __init__(
                self, 
                *, 
                hidden_paths_on_request: Optional[list[str]] = ..., 
                hidden_paths_on_response: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ManifestLevelPropertyBag(_Model):
        resource_hydration_accounts: Optional[list[ResourceHydrationAccount]]

        @overload
        def __init__(
                self, 
                *, 
                resource_hydration_accounts: Optional[list[ResourceHydrationAccount]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ManifestResourceDeletionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASCADE = "Cascade"
        FORCE = "Force"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.MarketplaceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADD_ON = "AddOn"
        BYPASS = "Bypass"
        NOT_SPECIFIED = "NotSpecified"
        STORE = "Store"


    class azure.mgmt.providerhub.models.MessageScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        REGISTERED_SUBSCRIPTIONS = "RegisteredSubscriptions"


    class azure.mgmt.providerhub.models.Notification(_Model):
        notification_type: Optional[Union[str, NotificationType]]
        skip_notifications: Optional[Union[str, SkipNotifications]]

        @overload
        def __init__(
                self, 
                *, 
                notification_type: Optional[Union[str, NotificationType]] = ..., 
                skip_notifications: Optional[Union[str, SkipNotifications]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.NotificationEndpoint(_Model):
        locations: Optional[list[str]]
        notification_destination: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                locations: Optional[list[str]] = ..., 
                notification_destination: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.NotificationEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENTHUB = "Eventhub"
        WEBHOOK = "Webhook"


    class azure.mgmt.providerhub.models.NotificationMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EVENT_HUB = "EventHub"
        NOT_SPECIFIED = "NotSpecified"
        WEB_HOOK = "WebHook"


    class azure.mgmt.providerhub.models.NotificationOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EMIT_SPENDING_LIMIT = "EmitSpendingLimit"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.NotificationRegistration(ProxyResource):
        id: str
        name: str
        properties: Optional[NotificationRegistrationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NotificationRegistrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.NotificationRegistrationProperties(_Model):
        included_events: Optional[list[str]]
        message_scope: Optional[Union[str, MessageScope]]
        notification_endpoints: Optional[list[NotificationEndpoint]]
        notification_mode: Optional[Union[str, NotificationMode]]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                included_events: Optional[list[str]] = ..., 
                message_scope: Optional[Union[str, MessageScope]] = ..., 
                notification_endpoints: Optional[list[NotificationEndpoint]] = ..., 
                notification_mode: Optional[Union[str, NotificationMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.NotificationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SUBSCRIPTION_NOTIFICATION = "SubscriptionNotification"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.providerhub.models.OpenApiConfiguration(_Model):
        validation: Optional[OpenApiValidation]

        @overload
        def __init__(
                self, 
                *, 
                validation: Optional[OpenApiValidation] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OpenApiValidation(_Model):
        allow_noncompliant_collection_response: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                allow_noncompliant_collection_response: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.OperationOrigins(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM = "System"
        USER = "User"


    class azure.mgmt.providerhub.models.OperationsContentProperties(_Model):
        contents: Optional[list[LocalizedOperationDefinition]]

        @overload
        def __init__(
                self, 
                *, 
                contents: Optional[list[LocalizedOperationDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationsDefinition(_Model):
        action_type: Optional[Union[str, OperationActionType]]
        display: OperationsDefinitionDisplay
        is_data_action: Optional[bool]
        name: str
        origin: Optional[Union[str, OperationOrigins]]
        properties: Optional[Any]

        @overload
        def __init__(
                self, 
                *, 
                action_type: Optional[Union[str, OperationActionType]] = ..., 
                display: OperationsDefinitionDisplay, 
                is_data_action: Optional[bool] = ..., 
                name: str, 
                origin: Optional[Union[str, OperationOrigins]] = ..., 
                properties: Optional[Any] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationsDefinitionDisplay(OperationsDisplayDefinition):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationsDisplayDefinition(_Model):
        description: str
        operation: str
        provider: str
        resource: str

        @overload
        def __init__(
                self, 
                *, 
                description: str, 
                operation: str, 
                provider: str, 
                resource: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationsPutContent(ProxyResource):
        id: str
        name: str
        properties: Optional[OperationsPutContentProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[OperationsPutContentProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OperationsPutContentProperties(OperationsContentProperties):
        contents: list[LocalizedOperationDefinition]

        @overload
        def __init__(
                self, 
                *, 
                contents: Optional[list[LocalizedOperationDefinition]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.OptInHeaderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLIENT_GROUP_MEMBERSHIP = "ClientGroupMembership"
        CLIENT_PRINCIPAL_NAME_ENCODED = "ClientPrincipalNameEncoded"
        MANAGEMENT_GROUP_ANCESTORS_ENCODED = "ManagementGroupAncestorsEncoded"
        MSI_RESOURCE_ID_ENCODED = "MSIResourceIdEncoded"
        NOT_SPECIFIED = "NotSpecified"
        PRIVATE_LINK_ID = "PrivateLinkId"
        PRIVATE_LINK_RESOURCE_ID = "PrivateLinkResourceId"
        PRIVATE_LINK_VNET_TRAFFIC_TAG = "PrivateLinkVnetTrafficTag"
        RESOURCE_GROUP_LOCATION = "ResourceGroupLocation"
        SIGNED_AUXILIARY_TOKENS = "SignedAuxiliaryTokens"
        SIGNED_USER_TOKEN = "SignedUserToken"
        UNBOUNDED_CLIENT_GROUP_MEMBERSHIP = "UnboundedClientGroupMembership"


    class azure.mgmt.providerhub.models.OptOutHeaderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SYSTEM_DATA_CREATED_BY_LAST_MODIFIED_BY = "SystemDataCreatedByLastModifiedBy"


    class azure.mgmt.providerhub.models.Policy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        SYNCHRONIZE_BEGIN_EXTENSION = "SynchronizeBeginExtension"


    class azure.mgmt.providerhub.models.PolicyExecutionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS_POLICIES = "BypassPolicies"
        EXECUTE_POLICIES = "ExecutePolicies"
        EXPECT_PARTIAL_PUT_REQUESTS = "ExpectPartialPutRequests"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.PreflightOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE_DEPLOYMENT_ON_FAILURE = "ContinueDeploymentOnFailure"
        DEFAULT_VALIDATION_ONLY = "DefaultValidationOnly"
        NONE = "None"


    class azure.mgmt.providerhub.models.PrivateResourceProviderConfiguration(_Model):
        allowed_subscriptions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderHubMetadata(_Model):
        direct_rp_role_definition_id: Optional[str]
        global_async_operation_resource_type_name: Optional[str]
        provider_authentication: Optional[ProviderHubMetadataProviderAuthentication]
        provider_authorizations: Optional[list[ResourceProviderAuthorization]]
        regional_async_operation_resource_type_name: Optional[str]
        third_party_provider_authorization: Optional[ProviderHubMetadataThirdPartyProviderAuthorization]

        @overload
        def __init__(
                self, 
                *, 
                direct_rp_role_definition_id: Optional[str] = ..., 
                global_async_operation_resource_type_name: Optional[str] = ..., 
                provider_authentication: Optional[ProviderHubMetadataProviderAuthentication] = ..., 
                provider_authorizations: Optional[list[ResourceProviderAuthorization]] = ..., 
                regional_async_operation_resource_type_name: Optional[str] = ..., 
                third_party_provider_authorization: Optional[ProviderHubMetadataThirdPartyProviderAuthorization] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderHubMetadataProviderAuthentication(ResourceProviderAuthentication):
        allowed_audiences: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderHubMetadataThirdPartyProviderAuthorization(ThirdPartyProviderAuthorization):
        authorizations: list[LightHouseAuthorization]
        managed_by_tenant_id: str

        @overload
        def __init__(
                self, 
                *, 
                authorizations: Optional[list[LightHouseAuthorization]] = ..., 
                managed_by_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderMonitorSetting(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[ProviderMonitorSettingProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[ProviderMonitorSettingProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderMonitorSettingProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.providerhub.models.ProviderRegistration(ProxyResource):
        id: str
        kind: Optional[Union[str, ProviderRegistrationKind]]
        name: str
        properties: Optional[ProviderRegistrationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ProviderRegistrationKind]] = ..., 
                properties: Optional[ProviderRegistrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderRegistrationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        HYBRID = "Hybrid"
        MANAGED = "Managed"


    class azure.mgmt.providerhub.models.ProviderRegistrationProperties(ResourceProviderManifestProperties):
        capabilities: list[ResourceProviderCapabilities]
        cross_tenant_token_validation: Union[str, CrossTenantTokenValidation]
        custom_manifest_version: str
        dsts_configuration: ResourceProviderManifestPropertiesDstsConfiguration
        enable_tenant_linked_notification: bool
        features_rule: ResourceProviderManifestPropertiesFeaturesRule
        global_notification_endpoints: list[ResourceProviderEndpoint]
        legacy_namespace: str
        legacy_registrations: list[str]
        linked_notification_rules: list[FanoutLinkedNotificationRule]
        management: ResourceProviderManifestPropertiesManagement
        management_group_global_notification_endpoints: list[ResourceProviderEndpoint]
        metadata: any
        namespace: str
        notification_options: Union[str, NotificationOptions]
        notification_settings: ResourceProviderManifestPropertiesNotificationSettings
        notifications: list[Notification]
        optional_features: list[str]
        private_resource_provider_configuration: Optional[ProviderRegistrationPropertiesPrivateResourceProviderConfiguration]
        provider_authentication: ResourceProviderManifestPropertiesProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        provider_hub_metadata: Optional[ProviderRegistrationPropertiesProviderHubMetadata]
        provider_type: Union[str, ResourceProviderType]
        provider_version: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        request_header_options: ResourceProviderManifestPropertiesRequestHeaderOptions
        required_features: list[str]
        resource_group_lock_option_during_move: ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove
        resource_hydration_accounts: list[ResourceHydrationAccount]
        resource_provider_authorization_rules: ResourceProviderAuthorizationRules
        response_options: ResourceProviderManifestPropertiesResponseOptions
        service_name: str
        services: list[ResourceProviderService]
        subscription_lifecycle_notification_specifications: Optional[ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications]
        template_deployment_options: ResourceProviderManifestPropertiesTemplateDeploymentOptions
        token_auth_configuration: Optional[TokenAuthConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[ResourceProviderCapabilities]] = ..., 
                cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]] = ..., 
                custom_manifest_version: Optional[str] = ..., 
                dsts_configuration: Optional[ResourceProviderManifestPropertiesDstsConfiguration] = ..., 
                enable_tenant_linked_notification: Optional[bool] = ..., 
                features_rule: Optional[ResourceProviderManifestPropertiesFeaturesRule] = ..., 
                global_notification_endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                legacy_namespace: Optional[str] = ..., 
                legacy_registrations: Optional[list[str]] = ..., 
                linked_notification_rules: Optional[list[FanoutLinkedNotificationRule]] = ..., 
                management: Optional[ResourceProviderManifestPropertiesManagement] = ..., 
                management_group_global_notification_endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                metadata: Optional[Any] = ..., 
                namespace: Optional[str] = ..., 
                notification_options: Optional[Union[str, NotificationOptions]] = ..., 
                notification_settings: Optional[ResourceProviderManifestPropertiesNotificationSettings] = ..., 
                notifications: Optional[list[Notification]] = ..., 
                optional_features: Optional[list[str]] = ..., 
                private_resource_provider_configuration: Optional[ProviderRegistrationPropertiesPrivateResourceProviderConfiguration] = ..., 
                provider_authentication: Optional[ResourceProviderManifestPropertiesProviderAuthentication] = ..., 
                provider_authorizations: Optional[list[ResourceProviderAuthorization]] = ..., 
                provider_hub_metadata: Optional[ProviderRegistrationPropertiesProviderHubMetadata] = ..., 
                provider_type: Optional[Union[str, ResourceProviderType]] = ..., 
                provider_version: Optional[str] = ..., 
                request_header_options: Optional[ResourceProviderManifestPropertiesRequestHeaderOptions] = ..., 
                required_features: Optional[list[str]] = ..., 
                resource_group_lock_option_during_move: Optional[ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove] = ..., 
                resource_hydration_accounts: Optional[list[ResourceHydrationAccount]] = ..., 
                resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules] = ..., 
                response_options: Optional[ResourceProviderManifestPropertiesResponseOptions] = ..., 
                service_name: Optional[str] = ..., 
                services: Optional[list[ResourceProviderService]] = ..., 
                subscription_lifecycle_notification_specifications: Optional[ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications] = ..., 
                template_deployment_options: Optional[ResourceProviderManifestPropertiesTemplateDeploymentOptions] = ..., 
                token_auth_configuration: Optional[TokenAuthConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderRegistrationPropertiesPrivateResourceProviderConfiguration(PrivateResourceProviderConfiguration):
        allowed_subscriptions: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_subscriptions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderRegistrationPropertiesProviderHubMetadata(ProviderHubMetadata):
        direct_rp_role_definition_id: str
        global_async_operation_resource_type_name: str
        provider_authentication: ProviderHubMetadataProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        regional_async_operation_resource_type_name: str
        third_party_provider_authorization: ProviderHubMetadataThirdPartyProviderAuthorization

        @overload
        def __init__(
                self, 
                *, 
                direct_rp_role_definition_id: Optional[str] = ..., 
                global_async_operation_resource_type_name: Optional[str] = ..., 
                provider_authentication: Optional[ProviderHubMetadataProviderAuthentication] = ..., 
                provider_authorizations: Optional[list[ResourceProviderAuthorization]] = ..., 
                regional_async_operation_resource_type_name: Optional[str] = ..., 
                third_party_provider_authorization: Optional[ProviderHubMetadataThirdPartyProviderAuthorization] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications(SubscriptionLifecycleNotificationSpecifications):
        soft_delete_ttl: timedelta
        subscription_state_override_actions: list[SubscriptionStateOverrideAction]

        @overload
        def __init__(
                self, 
                *, 
                soft_delete_ttl: Optional[timedelta] = ..., 
                subscription_state_override_actions: Optional[list[SubscriptionStateOverrideAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        MOVING_RESOURCES = "MovingResources"
        NOT_SPECIFIED = "NotSpecified"
        ROLLOUT_IN_PROGRESS = "RolloutInProgress"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TRANSIENT_FAILURE = "TransientFailure"


    class azure.mgmt.providerhub.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.models.QuotaPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        NONE = "None"
        RESTRICTED = "Restricted"


    class azure.mgmt.providerhub.models.QuotaRule(_Model):
        location_rules: Optional[list[LocationQuotaRule]]
        quota_policy: Optional[Union[str, QuotaPolicy]]
        required_features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                location_rules: Optional[list[LocationQuotaRule]] = ..., 
                quota_policy: Optional[Union[str, QuotaPolicy]] = ..., 
                required_features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ReRegisterSubscriptionMetadata(_Model):
        concurrency_limit: Optional[int]
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                concurrency_limit: Optional[int] = ..., 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.Readiness(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CLOSING_DOWN = "ClosingDown"
        DEPRECATED = "Deprecated"
        GA = "GA"
        INTERNAL_ONLY = "InternalOnly"
        IN_DEVELOPMENT = "InDevelopment"
        PRIVATE_PREVIEW = "PrivatePreview"
        PUBLIC_PREVIEW = "PublicPreview"
        REMOVED_FROM_ARM = "RemovedFromARM"
        RETIRED = "Retired"


    class azure.mgmt.providerhub.models.Regionality(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        GLOBAL = "Global"
        NOT_SPECIFIED = "NotSpecified"
        REGIONAL = "Regional"


    class azure.mgmt.providerhub.models.RequestHeaderOptions(_Model):
        opt_in_headers: Optional[Union[str, OptInHeaderType]]
        opt_out_headers: Optional[Union[str, OptOutHeaderType]]

        @overload
        def __init__(
                self, 
                *, 
                opt_in_headers: Optional[Union[str, OptInHeaderType]] = ..., 
                opt_out_headers: Optional[Union[str, OptOutHeaderType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.providerhub.models.ResourceAccessPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACIS_ACTION_ALLOWED = "AcisActionAllowed"
        ACIS_READ_ALLOWED = "AcisReadAllowed"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ResourceAccessRole(_Model):
        actions: Optional[list[str]]
        allowed_group_claims: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[str]] = ..., 
                allowed_group_claims: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceConcurrencyControlOption(_Model):
        policy: Optional[Union[str, Policy]]

        @overload
        def __init__(
                self, 
                *, 
                policy: Optional[Union[str, Policy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceDeletionPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CASCADE_DELETE_ALL = "CascadeDeleteAll"
        CASCADE_DELETE_PROXY_ONLY_CHILDREN = "CascadeDeleteProxyOnlyChildren"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ResourceGraphConfiguration(_Model):
        api_version: Optional[str]
        enabled: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceHydrationAccount(_Model):
        account_name: Optional[str]
        encrypted_key: Optional[str]
        max_child_resource_consistency_job_limit: Optional[int]
        subscription_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                account_name: Optional[str] = ..., 
                encrypted_key: Optional[str] = ..., 
                max_child_resource_consistency_job_limit: Optional[int] = ..., 
                subscription_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceManagementAction(_Model):
        resources: Optional[list[ResourceManagementEntity]]

        @overload
        def __init__(
                self, 
                *, 
                resources: Optional[list[ResourceManagementEntity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceManagementEntity(_Model):
        home_tenant_id: Optional[str]
        location: Optional[str]
        resource_id: str
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                home_tenant_id: Optional[str] = ..., 
                location: Optional[str] = ..., 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceMovePolicy(_Model):
        cross_resource_group_move_enabled: Optional[bool]
        cross_subscription_move_enabled: Optional[bool]
        validation_required: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                cross_resource_group_move_enabled: Optional[bool] = ..., 
                cross_subscription_move_enabled: Optional[bool] = ..., 
                validation_required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderAuthentication(_Model):
        allowed_audiences: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderAuthorization(_Model):
        allowed_third_party_extensions: Optional[list[ThirdPartyExtension]]
        application_id: Optional[str]
        grouping_tag: Optional[str]
        managed_by_authorization: Optional[ResourceProviderAuthorizationManagedByAuthorization]
        managed_by_role_definition_id: Optional[str]
        role_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_third_party_extensions: Optional[list[ThirdPartyExtension]] = ..., 
                application_id: Optional[str] = ..., 
                grouping_tag: Optional[str] = ..., 
                managed_by_authorization: Optional[ResourceProviderAuthorizationManagedByAuthorization] = ..., 
                managed_by_role_definition_id: Optional[str] = ..., 
                role_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderAuthorizationManagedByAuthorization(_Model):
        additional_authorizations: Optional[list[AdditionalAuthorization]]
        allow_managed_by_inheritance: Optional[bool]
        managed_by_resource_role_definition_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_authorizations: Optional[list[AdditionalAuthorization]] = ..., 
                allow_managed_by_inheritance: Optional[bool] = ..., 
                managed_by_resource_role_definition_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderAuthorizationRules(_Model):
        async_operation_polling_rules: Optional[AsyncOperationPollingRules]

        @overload
        def __init__(
                self, 
                *, 
                async_operation_polling_rules: Optional[AsyncOperationPollingRules] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderCapabilities(_Model):
        effect: Union[str, ResourceProviderCapabilitiesEffect]
        quota_id: str
        required_features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                effect: Union[str, ResourceProviderCapabilitiesEffect], 
                quota_id: str, 
                required_features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderCapabilitiesEffect(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"
        DISALLOW = "Disallow"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ResourceProviderEndpoint(_Model):
        api_versions: Optional[list[str]]
        enabled: Optional[bool]
        endpoint_type: Optional[Union[str, EndpointType]]
        endpoint_uri: Optional[str]
        features_rule: Optional[ResourceProviderEndpointFeaturesRule]
        locations: Optional[list[str]]
        required_features: Optional[list[str]]
        sku_link: Optional[str]
        timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
                enabled: Optional[bool] = ..., 
                endpoint_type: Optional[Union[str, EndpointType]] = ..., 
                endpoint_uri: Optional[str] = ..., 
                features_rule: Optional[ResourceProviderEndpointFeaturesRule] = ..., 
                locations: Optional[list[str]] = ..., 
                required_features: Optional[list[str]] = ..., 
                sku_link: Optional[str] = ..., 
                timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderEndpointFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManagement(_Model):
        authorization_owners: Optional[list[str]]
        canary_manifest_owners: Optional[list[str]]
        error_response_message_options: Optional[ResourceProviderManagementErrorResponseMessageOptions]
        expedited_rollout_metadata: Optional[ResourceProviderManagementExpeditedRolloutMetadata]
        expedited_rollout_submitters: Optional[list[str]]
        incident_contact_email: Optional[str]
        incident_routing_service: Optional[str]
        incident_routing_team: Optional[str]
        manifest_owners: Optional[list[str]]
        pc_code: Optional[str]
        profit_center_program_id: Optional[str]
        resource_access_policy: Optional[Union[str, ResourceAccessPolicy]]
        resource_access_roles: Optional[list[ResourceAccessRole]]
        schema_owners: Optional[list[str]]
        service_tree_infos: Optional[list[ServiceTreeInfo]]

        @overload
        def __init__(
                self, 
                *, 
                authorization_owners: Optional[list[str]] = ..., 
                canary_manifest_owners: Optional[list[str]] = ..., 
                error_response_message_options: Optional[ResourceProviderManagementErrorResponseMessageOptions] = ..., 
                expedited_rollout_metadata: Optional[ResourceProviderManagementExpeditedRolloutMetadata] = ..., 
                expedited_rollout_submitters: Optional[list[str]] = ..., 
                incident_contact_email: Optional[str] = ..., 
                incident_routing_service: Optional[str] = ..., 
                incident_routing_team: Optional[str] = ..., 
                manifest_owners: Optional[list[str]] = ..., 
                pc_code: Optional[str] = ..., 
                profit_center_program_id: Optional[str] = ..., 
                resource_access_policy: Optional[Union[str, ResourceAccessPolicy]] = ..., 
                resource_access_roles: Optional[list[ResourceAccessRole]] = ..., 
                schema_owners: Optional[list[str]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManagementErrorResponseMessageOptions(_Model):
        server_failure_response_message_type: Optional[Union[str, ServerFailureResponseMessageType]]

        @overload
        def __init__(
                self, 
                *, 
                server_failure_response_message_type: Optional[Union[str, ServerFailureResponseMessageType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManagementExpeditedRolloutMetadata(_Model):
        enabled: Optional[bool]
        expedited_rollout_intent: Optional[Union[str, ExpeditedRolloutIntent]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: Optional[bool] = ..., 
                expedited_rollout_intent: Optional[Union[str, ExpeditedRolloutIntent]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifest(_Model):
        capabilities: Optional[list[ResourceProviderCapabilities]]
        cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]]
        enable_tenant_linked_notification: Optional[bool]
        features_rule: Optional[ResourceProviderManifestFeaturesRule]
        global_notification_endpoints: Optional[list[ResourceProviderEndpoint]]
        linked_notification_rules: Optional[list[FanoutLinkedNotificationRule]]
        management: Optional[ResourceProviderManifestManagement]
        metadata: Optional[Any]
        namespace: Optional[str]
        notifications: Optional[list[Notification]]
        provider_authentication: Optional[ResourceProviderManifestProviderAuthentication]
        provider_authorizations: Optional[list[ResourceProviderAuthorization]]
        provider_type: Optional[Union[str, ResourceProviderType]]
        provider_version: Optional[str]
        re_register_subscription_metadata: Optional[ResourceProviderManifestReRegisterSubscriptionMetadata]
        request_header_options: Optional[ResourceProviderManifestRequestHeaderOptions]
        required_features: Optional[list[str]]
        resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules]
        resource_types: Optional[list[ResourceType]]
        service_name: Optional[str]
        services: Optional[list[ResourceProviderService]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[ResourceProviderCapabilities]] = ..., 
                cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]] = ..., 
                enable_tenant_linked_notification: Optional[bool] = ..., 
                features_rule: Optional[ResourceProviderManifestFeaturesRule] = ..., 
                global_notification_endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                linked_notification_rules: Optional[list[FanoutLinkedNotificationRule]] = ..., 
                management: Optional[ResourceProviderManifestManagement] = ..., 
                metadata: Optional[Any] = ..., 
                namespace: Optional[str] = ..., 
                notifications: Optional[list[Notification]] = ..., 
                provider_authentication: Optional[ResourceProviderManifestProviderAuthentication] = ..., 
                provider_authorizations: Optional[list[ResourceProviderAuthorization]] = ..., 
                provider_type: Optional[Union[str, ResourceProviderType]] = ..., 
                provider_version: Optional[str] = ..., 
                re_register_subscription_metadata: Optional[ResourceProviderManifestReRegisterSubscriptionMetadata] = ..., 
                request_header_options: Optional[ResourceProviderManifestRequestHeaderOptions] = ..., 
                required_features: Optional[list[str]] = ..., 
                resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules] = ..., 
                resource_types: Optional[list[ResourceType]] = ..., 
                service_name: Optional[str] = ..., 
                services: Optional[list[ResourceProviderService]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestManagement(ResourceProviderManagement):
        authorization_owners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schema_owners: list[str]
        service_tree_infos: list[ServiceTreeInfo]

        @overload
        def __init__(
                self, 
                *, 
                authorization_owners: Optional[list[str]] = ..., 
                canary_manifest_owners: Optional[list[str]] = ..., 
                error_response_message_options: Optional[ResourceProviderManagementErrorResponseMessageOptions] = ..., 
                expedited_rollout_metadata: Optional[ResourceProviderManagementExpeditedRolloutMetadata] = ..., 
                expedited_rollout_submitters: Optional[list[str]] = ..., 
                incident_contact_email: Optional[str] = ..., 
                incident_routing_service: Optional[str] = ..., 
                incident_routing_team: Optional[str] = ..., 
                manifest_owners: Optional[list[str]] = ..., 
                pc_code: Optional[str] = ..., 
                profit_center_program_id: Optional[str] = ..., 
                resource_access_policy: Optional[Union[str, ResourceAccessPolicy]] = ..., 
                resource_access_roles: Optional[list[ResourceAccessRole]] = ..., 
                schema_owners: Optional[list[str]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestProperties(_Model):
        capabilities: Optional[list[ResourceProviderCapabilities]]
        cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]]
        custom_manifest_version: Optional[str]
        dsts_configuration: Optional[ResourceProviderManifestPropertiesDstsConfiguration]
        enable_tenant_linked_notification: Optional[bool]
        features_rule: Optional[ResourceProviderManifestPropertiesFeaturesRule]
        global_notification_endpoints: Optional[list[ResourceProviderEndpoint]]
        legacy_namespace: Optional[str]
        legacy_registrations: Optional[list[str]]
        linked_notification_rules: Optional[list[FanoutLinkedNotificationRule]]
        management: Optional[ResourceProviderManifestPropertiesManagement]
        management_group_global_notification_endpoints: Optional[list[ResourceProviderEndpoint]]
        metadata: Optional[Any]
        namespace: Optional[str]
        notification_options: Optional[Union[str, NotificationOptions]]
        notification_settings: Optional[ResourceProviderManifestPropertiesNotificationSettings]
        notifications: Optional[list[Notification]]
        optional_features: Optional[list[str]]
        provider_authentication: Optional[ResourceProviderManifestPropertiesProviderAuthentication]
        provider_authorizations: Optional[list[ResourceProviderAuthorization]]
        provider_type: Optional[Union[str, ResourceProviderType]]
        provider_version: Optional[str]
        request_header_options: Optional[ResourceProviderManifestPropertiesRequestHeaderOptions]
        required_features: Optional[list[str]]
        resource_group_lock_option_during_move: Optional[ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove]
        resource_hydration_accounts: Optional[list[ResourceHydrationAccount]]
        resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules]
        response_options: Optional[ResourceProviderManifestPropertiesResponseOptions]
        service_name: Optional[str]
        services: Optional[list[ResourceProviderService]]
        template_deployment_options: Optional[ResourceProviderManifestPropertiesTemplateDeploymentOptions]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[ResourceProviderCapabilities]] = ..., 
                cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]] = ..., 
                custom_manifest_version: Optional[str] = ..., 
                dsts_configuration: Optional[ResourceProviderManifestPropertiesDstsConfiguration] = ..., 
                enable_tenant_linked_notification: Optional[bool] = ..., 
                features_rule: Optional[ResourceProviderManifestPropertiesFeaturesRule] = ..., 
                global_notification_endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                legacy_namespace: Optional[str] = ..., 
                legacy_registrations: Optional[list[str]] = ..., 
                linked_notification_rules: Optional[list[FanoutLinkedNotificationRule]] = ..., 
                management: Optional[ResourceProviderManifestPropertiesManagement] = ..., 
                management_group_global_notification_endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                metadata: Optional[Any] = ..., 
                namespace: Optional[str] = ..., 
                notification_options: Optional[Union[str, NotificationOptions]] = ..., 
                notification_settings: Optional[ResourceProviderManifestPropertiesNotificationSettings] = ..., 
                notifications: Optional[list[Notification]] = ..., 
                optional_features: Optional[list[str]] = ..., 
                provider_authentication: Optional[ResourceProviderManifestPropertiesProviderAuthentication] = ..., 
                provider_authorizations: Optional[list[ResourceProviderAuthorization]] = ..., 
                provider_type: Optional[Union[str, ResourceProviderType]] = ..., 
                provider_version: Optional[str] = ..., 
                request_header_options: Optional[ResourceProviderManifestPropertiesRequestHeaderOptions] = ..., 
                required_features: Optional[list[str]] = ..., 
                resource_group_lock_option_during_move: Optional[ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove] = ..., 
                resource_hydration_accounts: Optional[list[ResourceHydrationAccount]] = ..., 
                resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules] = ..., 
                response_options: Optional[ResourceProviderManifestPropertiesResponseOptions] = ..., 
                service_name: Optional[str] = ..., 
                services: Optional[list[ResourceProviderService]] = ..., 
                template_deployment_options: Optional[ResourceProviderManifestPropertiesTemplateDeploymentOptions] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesDstsConfiguration(DstsConfiguration):
        service_dns_name: str
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesManagement(ResourceProviderManagement):
        authorization_owners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schema_owners: list[str]
        service_tree_infos: list[ServiceTreeInfo]

        @overload
        def __init__(
                self, 
                *, 
                authorization_owners: Optional[list[str]] = ..., 
                canary_manifest_owners: Optional[list[str]] = ..., 
                error_response_message_options: Optional[ResourceProviderManagementErrorResponseMessageOptions] = ..., 
                expedited_rollout_metadata: Optional[ResourceProviderManagementExpeditedRolloutMetadata] = ..., 
                expedited_rollout_submitters: Optional[list[str]] = ..., 
                incident_contact_email: Optional[str] = ..., 
                incident_routing_service: Optional[str] = ..., 
                incident_routing_team: Optional[str] = ..., 
                manifest_owners: Optional[list[str]] = ..., 
                pc_code: Optional[str] = ..., 
                profit_center_program_id: Optional[str] = ..., 
                resource_access_policy: Optional[Union[str, ResourceAccessPolicy]] = ..., 
                resource_access_roles: Optional[list[ResourceAccessRole]] = ..., 
                schema_owners: Optional[list[str]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesNotificationSettings(_Model):
        subscriber_settings: Optional[list[SubscriberSetting]]

        @overload
        def __init__(
                self, 
                *, 
                subscriber_settings: Optional[list[SubscriberSetting]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesProviderAuthentication(ResourceProviderAuthentication):
        allowed_audiences: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesRequestHeaderOptions(RequestHeaderOptions):
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]

        @overload
        def __init__(
                self, 
                *, 
                opt_in_headers: Optional[Union[str, OptInHeaderType]] = ..., 
                opt_out_headers: Optional[Union[str, OptOutHeaderType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove(_Model):
        block_action_verb: Optional[Union[str, BlockActionVerb]]

        @overload
        def __init__(
                self, 
                *, 
                block_action_verb: Optional[Union[str, BlockActionVerb]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesResponseOptions(_Model):
        service_client_options_type: Optional[Union[str, ServiceClientOptionsType]]

        @overload
        def __init__(
                self, 
                *, 
                service_client_options_type: Optional[Union[str, ServiceClientOptionsType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestPropertiesTemplateDeploymentOptions(TemplateDeploymentOptions):
        preflight_options: Union[list[str, PreflightOption]]
        preflight_supported: bool

        @overload
        def __init__(
                self, 
                *, 
                preflight_options: Optional[list[Union[str, PreflightOption]]] = ..., 
                preflight_supported: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestProviderAuthentication(ResourceProviderAuthentication):
        allowed_audiences: list[str]

        @overload
        def __init__(
                self, 
                *, 
                allowed_audiences: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestReRegisterSubscriptionMetadata(ReRegisterSubscriptionMetadata):
        concurrency_limit: int
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                concurrency_limit: Optional[int] = ..., 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderManifestRequestHeaderOptions(RequestHeaderOptions):
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]

        @overload
        def __init__(
                self, 
                *, 
                opt_in_headers: Optional[Union[str, OptInHeaderType]] = ..., 
                opt_out_headers: Optional[Union[str, OptOutHeaderType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderService(_Model):
        service_name: Optional[str]
        status: Optional[Union[str, ServiceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                service_name: Optional[str] = ..., 
                status: Optional[Union[str, ServiceStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceProviderType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTHORIZATION_FREE = "AuthorizationFree"
        EXTERNAL = "External"
        HIDDEN = "Hidden"
        INTERNAL = "Internal"
        LEGACY_REGISTRATION_REQUIRED = "LegacyRegistrationRequired"
        NOT_SPECIFIED = "NotSpecified"
        REGISTRATION_FREE = "RegistrationFree"
        TENANT_ONLY = "TenantOnly"


    class azure.mgmt.providerhub.models.ResourceSubType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYNC_OPERATION = "AsyncOperation"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ResourceType(_Model):
        additional_options: Optional[Union[str, AdditionalOptions]]
        allowed_unauthorized_actions: Optional[list[str]]
        allowed_unauthorized_actions_extensions: Optional[list[AllowedUnauthorizedActionsExtension]]
        authorization_action_mappings: Optional[list[AuthorizationActionMapping]]
        cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]]
        default_api_version: Optional[str]
        disallowed_action_verbs: Optional[list[str]]
        endpoints: Optional[list[ResourceProviderEndpoint]]
        extended_locations: Optional[list[ExtendedLocationOptions]]
        features_rule: Optional[ResourceTypeFeaturesRule]
        identity_management: Optional[ResourceTypeIdentityManagement]
        linked_access_checks: Optional[list[LinkedAccessCheck]]
        linked_notification_rules: Optional[list[LinkedNotificationRule]]
        linked_operation_rules: Optional[list[LinkedOperationRule]]
        logging_rules: Optional[list[LoggingRule]]
        marketplace_type: Optional[Union[str, MarketplaceType]]
        metadata: Optional[Any]
        name: Optional[str]
        notifications: Optional[list[Notification]]
        quota_rule: Optional[QuotaRule]
        request_header_options: Optional[ResourceTypeRequestHeaderOptions]
        required_features: Optional[list[str]]
        resource_deletion_policy: Optional[Union[str, ManifestResourceDeletionPolicy]]
        resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules]
        resource_validation: Optional[Union[str, ResourceValidation]]
        routing_type: Optional[Union[str, RoutingType]]
        service_tree_infos: Optional[list[ServiceTreeInfo]]
        sku_link: Optional[str]
        subscription_state_rules: Optional[list[SubscriptionStateRule]]
        template_deployment_policy: Optional[ResourceTypeTemplateDeploymentPolicy]
        throttling_rules: Optional[list[ThrottlingRule]]

        @overload
        def __init__(
                self, 
                *, 
                additional_options: Optional[Union[str, AdditionalOptions]] = ..., 
                allowed_unauthorized_actions: Optional[list[str]] = ..., 
                allowed_unauthorized_actions_extensions: Optional[list[AllowedUnauthorizedActionsExtension]] = ..., 
                authorization_action_mappings: Optional[list[AuthorizationActionMapping]] = ..., 
                cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]] = ..., 
                default_api_version: Optional[str] = ..., 
                disallowed_action_verbs: Optional[list[str]] = ..., 
                endpoints: Optional[list[ResourceProviderEndpoint]] = ..., 
                extended_locations: Optional[list[ExtendedLocationOptions]] = ..., 
                features_rule: Optional[ResourceTypeFeaturesRule] = ..., 
                identity_management: Optional[ResourceTypeIdentityManagement] = ..., 
                linked_access_checks: Optional[list[LinkedAccessCheck]] = ..., 
                linked_notification_rules: Optional[list[LinkedNotificationRule]] = ..., 
                linked_operation_rules: Optional[list[LinkedOperationRule]] = ..., 
                logging_rules: Optional[list[LoggingRule]] = ..., 
                marketplace_type: Optional[Union[str, MarketplaceType]] = ..., 
                metadata: Optional[Any] = ..., 
                name: Optional[str] = ..., 
                notifications: Optional[list[Notification]] = ..., 
                quota_rule: Optional[QuotaRule] = ..., 
                request_header_options: Optional[ResourceTypeRequestHeaderOptions] = ..., 
                required_features: Optional[list[str]] = ..., 
                resource_deletion_policy: Optional[Union[str, ManifestResourceDeletionPolicy]] = ..., 
                resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules] = ..., 
                resource_validation: Optional[Union[str, ResourceValidation]] = ..., 
                routing_type: Optional[Union[str, RoutingType]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ..., 
                sku_link: Optional[str] = ..., 
                subscription_state_rules: Optional[list[SubscriptionStateRule]] = ..., 
                template_deployment_policy: Optional[ResourceTypeTemplateDeploymentPolicy] = ..., 
                throttling_rules: Optional[list[ThrottlingRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FREE_FORM = "FreeForm"
        INTERNAL = "Internal"
        NONE = "None"
        PURE_PROXY = "PureProxy"


    class azure.mgmt.providerhub.models.ResourceTypeEndpoint(_Model):
        api_version: Optional[str]
        api_versions: Optional[list[str]]
        data_boundary: Optional[Union[str, DataBoundary]]
        dsts_configuration: Optional[ResourceTypeEndpointDstsConfiguration]
        enabled: Optional[bool]
        endpoint_type: Optional[Union[str, EndpointTypeResourceType]]
        endpoint_uri: Optional[str]
        extensions: Optional[list[ResourceTypeExtension]]
        features_rule: Optional[ResourceTypeEndpointFeaturesRule]
        kind: Optional[Union[str, ResourceTypeEndpointKind]]
        locations: Optional[list[str]]
        required_features: Optional[list[str]]
        sku_link: Optional[str]
        timeout: Optional[timedelta]
        token_auth_configuration: Optional[TokenAuthConfiguration]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                api_versions: Optional[list[str]] = ..., 
                data_boundary: Optional[Union[str, DataBoundary]] = ..., 
                dsts_configuration: Optional[ResourceTypeEndpointDstsConfiguration] = ..., 
                enabled: Optional[bool] = ..., 
                endpoint_type: Optional[Union[str, EndpointTypeResourceType]] = ..., 
                endpoint_uri: Optional[str] = ..., 
                extensions: Optional[list[ResourceTypeExtension]] = ..., 
                features_rule: Optional[ResourceTypeEndpointFeaturesRule] = ..., 
                kind: Optional[Union[str, ResourceTypeEndpointKind]] = ..., 
                locations: Optional[list[str]] = ..., 
                required_features: Optional[list[str]] = ..., 
                sku_link: Optional[str] = ..., 
                timeout: Optional[timedelta] = ..., 
                token_auth_configuration: Optional[TokenAuthConfiguration] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointBase(_Model):
        api_version: str
        api_versions: list[str]
        dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration
        enabled: bool
        endpoint_type: Union[str, EndpointType]
        endpoint_uri: str
        features_rule: ResourceTypeEndpointBaseFeaturesRule
        locations: list[str]
        required_features: list[str]
        sku_link: str
        timeout: timedelta
        zones: list[str]

        @overload
        def __init__(
                self, 
                *, 
                api_version: str, 
                api_versions: list[str], 
                dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration, 
                enabled: bool, 
                endpoint_type: Union[str, EndpointType], 
                endpoint_uri: str, 
                features_rule: ResourceTypeEndpointBaseFeaturesRule, 
                locations: list[str], 
                required_features: list[str], 
                sku_link: str, 
                timeout: timedelta, 
                zones: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointBaseDstsConfiguration(DstsConfiguration):
        service_dns_name: str
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointBaseFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointDstsConfiguration(DstsConfiguration):
        service_dns_name: str
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeEndpointKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        MANAGED = "Managed"


    class azure.mgmt.providerhub.models.ResourceTypeExtendedLocationPolicy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL = "All"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ResourceTypeExtension(_Model):
        endpoint_uri: Optional[str]
        extension_categories: Optional[list[Union[str, ExtensionCategory]]]
        timeout: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                endpoint_uri: Optional[str] = ..., 
                extension_categories: Optional[list[Union[str, ExtensionCategory]]] = ..., 
                timeout: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeExtensionOptions(_Model):
        resource_creation_begin: Optional[ResourceTypeExtensionOptionsResourceCreationBegin]

        @overload
        def __init__(
                self, 
                *, 
                resource_creation_begin: Optional[ResourceTypeExtensionOptionsResourceCreationBegin] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeExtensionOptionsResourceCreationBegin(ExtensionOptions):
        request: Union[list[str, ExtensionOptionType]]
        response: Union[list[str, ExtensionOptionType]]

        @overload
        def __init__(
                self, 
                *, 
                request: Optional[list[Union[str, ExtensionOptionType]]] = ..., 
                response: Optional[list[Union[str, ExtensionOptionType]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeIdentityManagement(IdentityManagement):
        type: Union[str, IdentityManagementTypes]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, IdentityManagementTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeOnBehalfOfToken(_Model):
        action_name: Optional[str]
        life_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_name: Optional[str] = ..., 
                life_time: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistration(ProxyResource):
        id: str
        kind: Optional[Union[str, ResourceTypeRegistrationKind]]
        name: str
        properties: Optional[ResourceTypeRegistrationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                kind: Optional[Union[str, ResourceTypeRegistrationKind]] = ..., 
                properties: Optional[ResourceTypeRegistrationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationKind(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DIRECT = "Direct"
        HYBRID = "Hybrid"
        MANAGED = "Managed"


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationProperties(_Model):
        add_resource_list_target_locations: Optional[bool]
        additional_options: Optional[Union[str, AdditionalOptionsResourceTypeRegistration]]
        allow_empty_role_assignments: Optional[bool]
        allowed_resource_names: Optional[list[AllowedResourceName]]
        allowed_template_deployment_reference_actions: Optional[list[str]]
        allowed_unauthorized_actions: Optional[list[str]]
        allowed_unauthorized_actions_extensions: Optional[list[AllowedUnauthorizedActionsExtension]]
        api_profiles: Optional[list[ApiProfile]]
        async_operation_resource_type_name: Optional[str]
        async_timeout_rules: Optional[list[AsyncTimeoutRule]]
        authorization_action_mappings: Optional[list[AuthorizationActionMapping]]
        availability_zone_rule: Optional[ResourceTypeRegistrationPropertiesAvailabilityZoneRule]
        capacity_rule: Optional[ResourceTypeRegistrationPropertiesCapacityRule]
        category: Optional[Union[str, ResourceTypeCategory]]
        check_name_availability_specifications: Optional[ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications]
        common_api_versions: Optional[list[str]]
        cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]]
        default_api_version: Optional[str]
        disallowed_action_verbs: Optional[list[str]]
        disallowed_end_user_operations: Optional[list[str]]
        dsts_configuration: Optional[ResourceTypeRegistrationPropertiesDstsConfiguration]
        enable_async_operation: Optional[bool]
        enable_third_party_s2_s: Optional[bool]
        endpoints: Optional[list[ResourceTypeEndpoint]]
        extended_locations: Optional[list[ExtendedLocationOptions]]
        extension_options: Optional[ResourceTypeRegistrationPropertiesExtensionOptions]
        features_rule: Optional[ResourceTypeRegistrationPropertiesFeaturesRule]
        frontdoor_request_mode: Optional[Union[str, FrontdoorRequestMode]]
        grouping_tag: Optional[str]
        identity_management: Optional[ResourceTypeRegistrationPropertiesIdentityManagement]
        is_pure_proxy: Optional[bool]
        legacy_name: Optional[str]
        legacy_names: Optional[list[str]]
        legacy_policy: Optional[ResourceTypeRegistrationPropertiesLegacyPolicy]
        linked_access_checks: Optional[list[LinkedAccessCheck]]
        linked_notification_rules: Optional[list[LinkedNotificationRule]]
        linked_operation_rules: Optional[list[LinkedOperationRule]]
        logging_rules: Optional[list[LoggingRule]]
        management: Optional[ResourceTypeRegistrationPropertiesManagement]
        manifest_link: Optional[str]
        marketplace_options: Optional[ResourceTypeRegistrationPropertiesMarketplaceOptions]
        marketplace_type: Optional[Union[str, MarketplaceType]]
        metadata: Optional[dict[str, Any]]
        notifications: Optional[list[Notification]]
        on_behalf_of_tokens: Optional[ResourceTypeOnBehalfOfToken]
        open_api_configuration: Optional[OpenApiConfiguration]
        policy_execution_type: Optional[Union[str, PolicyExecutionType]]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        quota_rule: Optional[QuotaRule]
        regionality: Optional[Union[str, Regionality]]
        request_header_options: Optional[ResourceTypeRegistrationPropertiesRequestHeaderOptions]
        required_features: Optional[list[str]]
        resource_cache: Optional[ResourceTypeRegistrationPropertiesResourceCache]
        resource_concurrency_control_options: Optional[dict[str, ResourceConcurrencyControlOption]]
        resource_deletion_policy: Optional[Union[str, ResourceDeletionPolicy]]
        resource_graph_configuration: Optional[ResourceTypeRegistrationPropertiesResourceGraphConfiguration]
        resource_management_options: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptions]
        resource_move_policy: Optional[ResourceTypeRegistrationPropertiesResourceMovePolicy]
        resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules]
        resource_query_management: Optional[ResourceTypeRegistrationPropertiesResourceQueryManagement]
        resource_sub_type: Optional[Union[str, ResourceSubType]]
        resource_type_common_attribute_management: Optional[ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement]
        resource_validation: Optional[Union[str, ResourceValidation]]
        routing_rule: Optional[ResourceTypeRegistrationPropertiesRoutingRule]
        routing_type: Optional[Union[str, RoutingType]]
        service_tree_infos: Optional[list[ServiceTreeInfo]]
        sku_link: Optional[str]
        subscription_lifecycle_notification_specifications: Optional[ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications]
        subscription_state_rules: Optional[list[SubscriptionStateRule]]
        supports_tags: Optional[bool]
        swagger_specifications: Optional[list[SwaggerSpecification]]
        template_deployment_options: Optional[ResourceTypeRegistrationPropertiesTemplateDeploymentOptions]
        template_deployment_policy: Optional[ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy]
        throttling_rules: Optional[list[ThrottlingRule]]
        token_auth_configuration: Optional[TokenAuthConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                add_resource_list_target_locations: Optional[bool] = ..., 
                additional_options: Optional[Union[str, AdditionalOptionsResourceTypeRegistration]] = ..., 
                allow_empty_role_assignments: Optional[bool] = ..., 
                allowed_resource_names: Optional[list[AllowedResourceName]] = ..., 
                allowed_template_deployment_reference_actions: Optional[list[str]] = ..., 
                allowed_unauthorized_actions: Optional[list[str]] = ..., 
                allowed_unauthorized_actions_extensions: Optional[list[AllowedUnauthorizedActionsExtension]] = ..., 
                api_profiles: Optional[list[ApiProfile]] = ..., 
                async_operation_resource_type_name: Optional[str] = ..., 
                async_timeout_rules: Optional[list[AsyncTimeoutRule]] = ..., 
                authorization_action_mappings: Optional[list[AuthorizationActionMapping]] = ..., 
                availability_zone_rule: Optional[ResourceTypeRegistrationPropertiesAvailabilityZoneRule] = ..., 
                capacity_rule: Optional[ResourceTypeRegistrationPropertiesCapacityRule] = ..., 
                category: Optional[Union[str, ResourceTypeCategory]] = ..., 
                check_name_availability_specifications: Optional[ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications] = ..., 
                common_api_versions: Optional[list[str]] = ..., 
                cross_tenant_token_validation: Optional[Union[str, CrossTenantTokenValidation]] = ..., 
                default_api_version: Optional[str] = ..., 
                disallowed_action_verbs: Optional[list[str]] = ..., 
                disallowed_end_user_operations: Optional[list[str]] = ..., 
                dsts_configuration: Optional[ResourceTypeRegistrationPropertiesDstsConfiguration] = ..., 
                enable_async_operation: Optional[bool] = ..., 
                enable_third_party_s2_s: Optional[bool] = ..., 
                endpoints: Optional[list[ResourceTypeEndpoint]] = ..., 
                extended_locations: Optional[list[ExtendedLocationOptions]] = ..., 
                extension_options: Optional[ResourceTypeRegistrationPropertiesExtensionOptions] = ..., 
                features_rule: Optional[ResourceTypeRegistrationPropertiesFeaturesRule] = ..., 
                frontdoor_request_mode: Optional[Union[str, FrontdoorRequestMode]] = ..., 
                grouping_tag: Optional[str] = ..., 
                identity_management: Optional[ResourceTypeRegistrationPropertiesIdentityManagement] = ..., 
                is_pure_proxy: Optional[bool] = ..., 
                legacy_name: Optional[str] = ..., 
                legacy_names: Optional[list[str]] = ..., 
                legacy_policy: Optional[ResourceTypeRegistrationPropertiesLegacyPolicy] = ..., 
                linked_access_checks: Optional[list[LinkedAccessCheck]] = ..., 
                linked_notification_rules: Optional[list[LinkedNotificationRule]] = ..., 
                linked_operation_rules: Optional[list[LinkedOperationRule]] = ..., 
                logging_rules: Optional[list[LoggingRule]] = ..., 
                management: Optional[ResourceTypeRegistrationPropertiesManagement] = ..., 
                manifest_link: Optional[str] = ..., 
                marketplace_options: Optional[ResourceTypeRegistrationPropertiesMarketplaceOptions] = ..., 
                marketplace_type: Optional[Union[str, MarketplaceType]] = ..., 
                metadata: Optional[dict[str, Any]] = ..., 
                notifications: Optional[list[Notification]] = ..., 
                on_behalf_of_tokens: Optional[ResourceTypeOnBehalfOfToken] = ..., 
                open_api_configuration: Optional[OpenApiConfiguration] = ..., 
                policy_execution_type: Optional[Union[str, PolicyExecutionType]] = ..., 
                quota_rule: Optional[QuotaRule] = ..., 
                regionality: Optional[Union[str, Regionality]] = ..., 
                request_header_options: Optional[ResourceTypeRegistrationPropertiesRequestHeaderOptions] = ..., 
                required_features: Optional[list[str]] = ..., 
                resource_cache: Optional[ResourceTypeRegistrationPropertiesResourceCache] = ..., 
                resource_concurrency_control_options: Optional[dict[str, ResourceConcurrencyControlOption]] = ..., 
                resource_deletion_policy: Optional[Union[str, ResourceDeletionPolicy]] = ..., 
                resource_graph_configuration: Optional[ResourceTypeRegistrationPropertiesResourceGraphConfiguration] = ..., 
                resource_management_options: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptions] = ..., 
                resource_move_policy: Optional[ResourceTypeRegistrationPropertiesResourceMovePolicy] = ..., 
                resource_provider_authorization_rules: Optional[ResourceProviderAuthorizationRules] = ..., 
                resource_query_management: Optional[ResourceTypeRegistrationPropertiesResourceQueryManagement] = ..., 
                resource_sub_type: Optional[Union[str, ResourceSubType]] = ..., 
                resource_type_common_attribute_management: Optional[ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement] = ..., 
                resource_validation: Optional[Union[str, ResourceValidation]] = ..., 
                routing_rule: Optional[ResourceTypeRegistrationPropertiesRoutingRule] = ..., 
                routing_type: Optional[Union[str, RoutingType]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ..., 
                sku_link: Optional[str] = ..., 
                subscription_lifecycle_notification_specifications: Optional[ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications] = ..., 
                subscription_state_rules: Optional[list[SubscriptionStateRule]] = ..., 
                supports_tags: Optional[bool] = ..., 
                swagger_specifications: Optional[list[SwaggerSpecification]] = ..., 
                template_deployment_options: Optional[ResourceTypeRegistrationPropertiesTemplateDeploymentOptions] = ..., 
                template_deployment_policy: Optional[ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy] = ..., 
                throttling_rules: Optional[list[ThrottlingRule]] = ..., 
                token_auth_configuration: Optional[TokenAuthConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesAvailabilityZoneRule(_Model):
        availability_zone_policy: Optional[Union[str, AvailabilityZonePolicy]]

        @overload
        def __init__(
                self, 
                *, 
                availability_zone_policy: Optional[Union[str, AvailabilityZonePolicy]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesCapacityRule(_Model):
        capacity_policy: Optional[Union[str, CapacityPolicy]]
        sku_alias: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capacity_policy: Optional[Union[str, CapacityPolicy]] = ..., 
                sku_alias: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications(CheckNameAvailabilitySpecifications):
        enable_default_validation: bool
        resource_types_with_custom_validation: list[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_default_validation: Optional[bool] = ..., 
                resource_types_with_custom_validation: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesDstsConfiguration(DstsConfiguration):
        service_dns_name: str
        service_name: str

        @overload
        def __init__(
                self, 
                *, 
                service_dns_name: Optional[str] = ..., 
                service_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesExtensionOptions(ResourceTypeExtensionOptions):
        resource_creation_begin: ResourceTypeExtensionOptionsResourceCreationBegin

        @overload
        def __init__(
                self, 
                *, 
                resource_creation_begin: Optional[ResourceTypeExtensionOptionsResourceCreationBegin] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesFeaturesRule(FeaturesRule):
        required_features_policy: Union[str, FeaturesPolicy]

        @overload
        def __init__(
                self, 
                *, 
                required_features_policy: Union[str, FeaturesPolicy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesIdentityManagement(IdentityManagementProperties):
        application_id: str
        application_ids: list[str]
        delegation_app_ids: list[str]
        type: Union[str, IdentityManagementTypes]

        @overload
        def __init__(
                self, 
                *, 
                application_id: Optional[str] = ..., 
                application_ids: Optional[list[str]] = ..., 
                delegation_app_ids: Optional[list[str]] = ..., 
                type: Optional[Union[str, IdentityManagementTypes]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesLegacyPolicy(_Model):
        disallowed_conditions: Optional[list[LegacyDisallowedCondition]]
        disallowed_legacy_operations: Optional[list[Union[str, LegacyOperation]]]

        @overload
        def __init__(
                self, 
                *, 
                disallowed_conditions: Optional[list[LegacyDisallowedCondition]] = ..., 
                disallowed_legacy_operations: Optional[list[Union[str, LegacyOperation]]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesManagement(ResourceProviderManagement):
        authorization_owners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schema_owners: list[str]
        service_tree_infos: list[ServiceTreeInfo]

        @overload
        def __init__(
                self, 
                *, 
                authorization_owners: Optional[list[str]] = ..., 
                canary_manifest_owners: Optional[list[str]] = ..., 
                error_response_message_options: Optional[ResourceProviderManagementErrorResponseMessageOptions] = ..., 
                expedited_rollout_metadata: Optional[ResourceProviderManagementExpeditedRolloutMetadata] = ..., 
                expedited_rollout_submitters: Optional[list[str]] = ..., 
                incident_contact_email: Optional[str] = ..., 
                incident_routing_service: Optional[str] = ..., 
                incident_routing_team: Optional[str] = ..., 
                manifest_owners: Optional[list[str]] = ..., 
                pc_code: Optional[str] = ..., 
                profit_center_program_id: Optional[str] = ..., 
                resource_access_policy: Optional[Union[str, ResourceAccessPolicy]] = ..., 
                resource_access_roles: Optional[list[ResourceAccessRole]] = ..., 
                schema_owners: Optional[list[str]] = ..., 
                service_tree_infos: Optional[list[ServiceTreeInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesMarketplaceOptions(_Model):
        add_on_plan_conversion_allowed: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                add_on_plan_conversion_allowed: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesRequestHeaderOptions(RequestHeaderOptions):
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]

        @overload
        def __init__(
                self, 
                *, 
                opt_in_headers: Optional[Union[str, OptInHeaderType]] = ..., 
                opt_out_headers: Optional[Union[str, OptOutHeaderType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceCache(_Model):
        enable_resource_cache: Optional[bool]
        resource_cache_expiration_timespan: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enable_resource_cache: Optional[bool] = ..., 
                resource_cache_expiration_timespan: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceGraphConfiguration(ResourceGraphConfiguration):
        api_version: str
        enabled: bool

        @overload
        def __init__(
                self, 
                *, 
                api_version: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceManagementOptions(_Model):
        batch_provisioning_support: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport]
        delete_dependencies: Optional[list[DeleteDependency]]
        nested_provisioning_support: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport]

        @overload
        def __init__(
                self, 
                *, 
                batch_provisioning_support: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport] = ..., 
                delete_dependencies: Optional[list[DeleteDependency]] = ..., 
                nested_provisioning_support: Optional[ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport(_Model):
        supported_operations: Optional[Union[str, SupportedOperations]]

        @overload
        def __init__(
                self, 
                *, 
                supported_operations: Optional[Union[str, SupportedOperations]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport(_Model):
        minimum_api_version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                minimum_api_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceMovePolicy(ResourceMovePolicy):
        cross_resource_group_move_enabled: bool
        cross_subscription_move_enabled: bool
        validation_required: bool

        @overload
        def __init__(
                self, 
                *, 
                cross_resource_group_move_enabled: Optional[bool] = ..., 
                cross_subscription_move_enabled: Optional[bool] = ..., 
                validation_required: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceQueryManagement(_Model):
        filter_option: Optional[Union[str, FilterOption]]

        @overload
        def __init__(
                self, 
                *, 
                filter_option: Optional[Union[str, FilterOption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement(_Model):
        common_api_versions_merge_mode: Optional[Union[str, CommonApiVersionsMergeMode]]

        @overload
        def __init__(
                self, 
                *, 
                common_api_versions_merge_mode: Optional[Union[str, CommonApiVersionsMergeMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesRoutingRule(_Model):
        host_resource_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                host_resource_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications(SubscriptionLifecycleNotificationSpecifications):
        soft_delete_ttl: timedelta
        subscription_state_override_actions: list[SubscriptionStateOverrideAction]

        @overload
        def __init__(
                self, 
                *, 
                soft_delete_ttl: Optional[timedelta] = ..., 
                subscription_state_override_actions: Optional[list[SubscriptionStateOverrideAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesTemplateDeploymentOptions(TemplateDeploymentOptions):
        preflight_options: Union[list[str, PreflightOption]]
        preflight_supported: bool

        @overload
        def __init__(
                self, 
                *, 
                preflight_options: Optional[list[Union[str, PreflightOption]]] = ..., 
                preflight_supported: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy(TemplateDeploymentPolicy):
        capabilities: Union[str, TemplateDeploymentCapabilities]
        preflight_notifications: Union[str, TemplateDeploymentPreflightNotifications]
        preflight_options: Union[str, TemplateDeploymentPreflightOptions]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Union[str, TemplateDeploymentCapabilities], 
                preflight_notifications: Optional[Union[str, TemplateDeploymentPreflightNotifications]] = ..., 
                preflight_options: Union[str, TemplateDeploymentPreflightOptions]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeRequestHeaderOptions(RequestHeaderOptions):
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]

        @overload
        def __init__(
                self, 
                *, 
                opt_in_headers: Optional[Union[str, OptInHeaderType]] = ..., 
                opt_out_headers: Optional[Union[str, OptOutHeaderType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeSku(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]
        sku_settings: list[SkuSetting]

        @overload
        def __init__(
                self, 
                *, 
                sku_settings: list[SkuSetting]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceTypeTemplateDeploymentPolicy(TemplateDeploymentPolicy):
        capabilities: Union[str, TemplateDeploymentCapabilities]
        preflight_notifications: Union[str, TemplateDeploymentPreflightNotifications]
        preflight_options: Union[str, TemplateDeploymentPreflightOptions]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Union[str, TemplateDeploymentCapabilities], 
                preflight_notifications: Optional[Union[str, TemplateDeploymentPreflightNotifications]] = ..., 
                preflight_options: Union[str, TemplateDeploymentPreflightOptions]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ResourceValidation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        PROFANE_WORDS = "ProfaneWords"
        RESERVED_WORDS = "ReservedWords"


    class azure.mgmt.providerhub.models.Role(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LIMITED_OWNER = "LimitedOwner"
        SERVICE_OWNER = "ServiceOwner"


    class azure.mgmt.providerhub.models.RolloutStatusBase(_Model):
        completed_regions: Optional[list[str]]
        failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]]

        @overload
        def __init__(
                self, 
                *, 
                completed_regions: Optional[list[str]] = ..., 
                failed_or_skipped_regions: Optional[dict[str, ExtendedErrorInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.RoutingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BYPASS_ENDPOINT_SELECTION_OPTIMIZATION = "BypassEndpointSelectionOptimization"
        CASCADE_AUTHORIZED_EXTENSION = "CascadeAuthorizedExtension"
        CASCADE_EXTENSION = "CascadeExtension"
        CHILD_FANOUT = "ChildFanout"
        DEFAULT = "Default"
        EXTENSION = "Extension"
        FAILOVER = "Failover"
        FANOUT = "Fanout"
        HOST_BASED = "HostBased"
        LOCATION_BASED = "LocationBased"
        LOCATION_MAPPING = "LocationMapping"
        PROXY_ONLY = "ProxyOnly"
        SERVICE_FANOUT = "ServiceFanout"
        TENANT = "Tenant"


    class azure.mgmt.providerhub.models.ServerFailureResponseMessageType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        OUTAGE_REPORTING = "OutageReporting"


    class azure.mgmt.providerhub.models.ServiceClientOptionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLE_AUTOMATIC_DECOMPRESSION = "DisableAutomaticDecompression"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.ServiceFeatureFlagAction(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE = "Create"
        DO_NOT_CREATE = "DoNotCreate"


    class azure.mgmt.providerhub.models.ServiceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        INACTIVE = "Inactive"


    class azure.mgmt.providerhub.models.ServiceTreeInfo(_Model):
        component_id: Optional[str]
        readiness: Optional[Union[str, Readiness]]
        service_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                component_id: Optional[str] = ..., 
                readiness: Optional[Union[str, Readiness]] = ..., 
                service_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SignedRequestScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENDPOINT = "Endpoint"
        RESOURCE_URI = "ResourceUri"


    class azure.mgmt.providerhub.models.SkipNotifications(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        UNSPECIFIED = "Unspecified"


    class azure.mgmt.providerhub.models.SkuCapability(_Model):
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


    class azure.mgmt.providerhub.models.SkuCapacity(_Model):
        default: Optional[int]
        maximum: Optional[int]
        minimum: int
        scale_type: Optional[Union[str, SkuScaleType]]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[int] = ..., 
                maximum: Optional[int] = ..., 
                minimum: int, 
                scale_type: Optional[Union[str, SkuScaleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuCost(_Model):
        extended_unit: Optional[str]
        meter_id: str
        quantity: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                extended_unit: Optional[str] = ..., 
                meter_id: str, 
                quantity: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuLocationInfo(_Model):
        extended_locations: Optional[list[str]]
        location: str
        type: Optional[Union[str, ExtendedLocationType]]
        zone_details: Optional[list[SkuZoneDetail]]
        zones: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                extended_locations: Optional[list[str]] = ..., 
                location: str, 
                type: Optional[Union[str, ExtendedLocationType]] = ..., 
                zone_details: Optional[list[SkuZoneDetail]] = ..., 
                zones: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SkuResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SkuResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuResourceProperties(ResourceTypeSku):
        provisioning_state: Union[str, ProvisioningState]
        sku_settings: list[SkuSetting]

        @overload
        def __init__(
                self, 
                *, 
                sku_settings: list[SkuSetting]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.providerhub.models.SkuSetting(_Model):
        capabilities: Optional[list[SkuCapability]]
        capacity: Optional[SkuSettingCapacity]
        costs: Optional[list[SkuCost]]
        family: Optional[str]
        kind: Optional[str]
        location_info: Optional[list[SkuLocationInfo]]
        locations: Optional[list[str]]
        name: str
        required_features: Optional[list[str]]
        required_quota_ids: Optional[list[str]]
        size: Optional[str]
        tier: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[SkuCapability]] = ..., 
                capacity: Optional[SkuSettingCapacity] = ..., 
                costs: Optional[list[SkuCost]] = ..., 
                family: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location_info: Optional[list[SkuLocationInfo]] = ..., 
                locations: Optional[list[str]] = ..., 
                name: str, 
                required_features: Optional[list[str]] = ..., 
                required_quota_ids: Optional[list[str]] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuSettingCapacity(SkuCapacity):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, SkuScaleType]

        @overload
        def __init__(
                self, 
                *, 
                default: Optional[int] = ..., 
                maximum: Optional[int] = ..., 
                minimum: int, 
                scale_type: Optional[Union[str, SkuScaleType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SkuZoneDetail(_Model):
        capabilities: Optional[list[SkuCapability]]
        name: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Optional[list[SkuCapability]] = ..., 
                name: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SubscriberSetting(_Model):
        filter_rules: Optional[list[FilterRule]]

        @overload
        def __init__(
                self, 
                *, 
                filter_rules: Optional[list[FilterRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SubscriptionLifecycleNotificationSpecifications(_Model):
        soft_delete_ttl: Optional[timedelta]
        subscription_state_override_actions: Optional[list[SubscriptionStateOverrideAction]]

        @overload
        def __init__(
                self, 
                *, 
                soft_delete_ttl: Optional[timedelta] = ..., 
                subscription_state_override_actions: Optional[list[SubscriptionStateOverrideAction]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SubscriptionNotificationOperation(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BILLING_CANCELLATION = "BillingCancellation"
        DELETE_ALL_RESOURCES = "DeleteAllResources"
        NOT_DEFINED = "NotDefined"
        NO_OP = "NoOp"
        SOFT_DELETE_ALL_RESOURCES = "SoftDeleteAllResources"
        UNDO_SOFT_DELETE = "UndoSoftDelete"


    class azure.mgmt.providerhub.models.SubscriptionReregistrationResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONDITIONAL_UPDATE = "ConditionalUpdate"
        FAILED = "Failed"
        FORCED_UPDATE = "ForcedUpdate"
        NOT_APPLICABLE = "NotApplicable"


    class azure.mgmt.providerhub.models.SubscriptionState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NOT_DEFINED = "NotDefined"
        PAST_DUE = "PastDue"
        WARNED = "Warned"


    class azure.mgmt.providerhub.models.SubscriptionStateOverrideAction(_Model):
        action: Union[str, SubscriptionNotificationOperation]
        state: Union[str, SubscriptionTransitioningState]

        @overload
        def __init__(
                self, 
                *, 
                action: Union[str, SubscriptionNotificationOperation], 
                state: Union[str, SubscriptionTransitioningState]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SubscriptionStateRule(_Model):
        allowed_actions: Optional[list[str]]
        state: Optional[Union[str, SubscriptionState]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_actions: Optional[list[str]] = ..., 
                state: Optional[Union[str, SubscriptionState]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SubscriptionTransitioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETED = "Deleted"
        REGISTERED = "Registered"
        SUSPENDED = "Suspended"
        SUSPENDED_TO_DELETED = "SuspendedToDeleted"
        SUSPENDED_TO_REGISTERED = "SuspendedToRegistered"
        SUSPENDED_TO_UNREGISTERED = "SuspendedToUnregistered"
        SUSPENDED_TO_WARNED = "SuspendedToWarned"
        UNREGISTERED = "Unregistered"
        WARNED = "Warned"
        WARNED_TO_DELETED = "WarnedToDeleted"
        WARNED_TO_REGISTERED = "WarnedToRegistered"
        WARNED_TO_SUSPENDED = "WarnedToSuspended"
        WARNED_TO_UNREGISTERED = "WarnedToUnregistered"


    class azure.mgmt.providerhub.models.SupportedOperations(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "Delete"
        GET = "Get"
        NOT_SPECIFIED = "NotSpecified"


    class azure.mgmt.providerhub.models.SwaggerSpecification(_Model):
        api_versions: Optional[list[str]]
        swagger_spec_folder_uri: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                api_versions: Optional[list[str]] = ..., 
                swagger_spec_folder_uri: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.SystemData(_Model):
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


    class azure.mgmt.providerhub.models.TemplateDeploymentCapabilities(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        PREFLIGHT = "Preflight"


    class azure.mgmt.providerhub.models.TemplateDeploymentOptions(_Model):
        preflight_options: Optional[list[Union[str, PreflightOption]]]
        preflight_supported: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                preflight_options: Optional[list[Union[str, PreflightOption]]] = ..., 
                preflight_supported: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TemplateDeploymentPolicy(_Model):
        capabilities: Union[str, TemplateDeploymentCapabilities]
        preflight_notifications: Optional[Union[str, TemplateDeploymentPreflightNotifications]]
        preflight_options: Union[str, TemplateDeploymentPreflightOptions]

        @overload
        def __init__(
                self, 
                *, 
                capabilities: Union[str, TemplateDeploymentCapabilities], 
                preflight_notifications: Optional[Union[str, TemplateDeploymentPreflightNotifications]] = ..., 
                preflight_options: Union[str, TemplateDeploymentPreflightOptions]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TemplateDeploymentPreflightNotifications(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        UNREGISTERED_SUBSCRIPTIONS = "UnregisteredSubscriptions"


    class azure.mgmt.providerhub.models.TemplateDeploymentPreflightOptions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEPLOYMENT_REQUESTS = "DeploymentRequests"
        NONE = "None"
        REGISTERED_ONLY = "RegisteredOnly"
        TEST_ONLY = "TestOnly"
        VALIDATION_REQUESTS = "ValidationRequests"


    class azure.mgmt.providerhub.models.ThirdPartyExtension(_Model):
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ThirdPartyProviderAuthorization(_Model):
        authorizations: Optional[list[LightHouseAuthorization]]
        managed_by_tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                authorizations: Optional[list[LightHouseAuthorization]] = ..., 
                managed_by_tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ThrottlingMetric(_Model):
        interval: Optional[timedelta]
        limit: int
        type: Union[str, ThrottlingMetricType]

        @overload
        def __init__(
                self, 
                *, 
                interval: Optional[timedelta] = ..., 
                limit: int, 
                type: Union[str, ThrottlingMetricType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.ThrottlingMetricType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_SPECIFIED = "NotSpecified"
        NUMBER_OF_REQUESTS = "NumberOfRequests"
        NUMBER_OF_RESOURCES = "NumberOfResources"


    class azure.mgmt.providerhub.models.ThrottlingRule(_Model):
        action: str
        application_id: Optional[list[str]]
        metrics: list[ThrottlingMetric]
        required_features: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                action: str, 
                application_id: Optional[list[str]] = ..., 
                metrics: list[ThrottlingMetric], 
                required_features: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TokenAuthConfiguration(_Model):
        authentication_scheme: Optional[Union[str, AuthenticationScheme]]
        disable_certificate_authentication_fallback: Optional[bool]
        signed_request_scope: Optional[Union[str, SignedRequestScope]]

        @overload
        def __init__(
                self, 
                *, 
                authentication_scheme: Optional[Union[str, AuthenticationScheme]] = ..., 
                disable_certificate_authentication_fallback: Optional[bool] = ..., 
                signed_request_scope: Optional[Union[str, SignedRequestScope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TrackedResource(Resource):
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


    class azure.mgmt.providerhub.models.TrafficRegionCategory(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANARY = "Canary"
        HIGH_TRAFFIC = "HighTraffic"
        LOW_TRAFFIC = "LowTraffic"
        MEDIUM_TRAFFIC = "MediumTraffic"
        NONE = "None"
        NOT_SPECIFIED = "NotSpecified"
        REST_OF_THE_WORLD_GROUP_ONE = "RestOfTheWorldGroupOne"
        REST_OF_THE_WORLD_GROUP_TWO = "RestOfTheWorldGroupTwo"


    class azure.mgmt.providerhub.models.TrafficRegionRolloutConfiguration(TrafficRegions):
        regions: list[str]
        wait_duration: Optional[timedelta]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ..., 
                wait_duration: Optional[timedelta] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TrafficRegions(_Model):
        regions: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                regions: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.providerhub.models.TypedErrorInfo(_Model):
        info: Optional[Any]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.providerhub.operations

    class azure.mgmt.providerhub.operations.AuthorizedApplicationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: AuthorizedApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthorizedApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: AuthorizedApplication, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthorizedApplication]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                application_id: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AuthorizedApplication]: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                application_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                application_id: str, 
                **kwargs: Any
            ) -> AuthorizedApplication: ...

        @distributed_trace
        def list(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[AuthorizedApplication]: ...


    class azure.mgmt.providerhub.operations.CustomRolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: CustomRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomRollout]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: CustomRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomRollout]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CustomRollout]: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> CustomRollout: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[CustomRollout]: ...

        @distributed_trace
        def stop(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.operations.DefaultRolloutsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: DefaultRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DefaultRollout]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: DefaultRollout, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DefaultRollout]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DefaultRollout]: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[DefaultRollout]: ...

        @distributed_trace
        def stop(
                self, 
                provider_namespace: str, 
                rollout_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.operations.NewRegionFrontloadReleaseOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                release_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @overload
        def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @overload
        def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: FrontloadPayload, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @overload
        def generate_manifest(
                self, 
                provider_namespace: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ResourceProviderManifest: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                release_name: str, 
                **kwargs: Any
            ) -> DefaultRollout: ...

        @distributed_trace
        def stop(
                self, 
                provider_namespace: str, 
                release_name: str, 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.providerhub.operations.NotificationRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: NotificationRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: NotificationRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                notification_registration_name: str, 
                **kwargs: Any
            ) -> NotificationRegistration: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[NotificationRegistration]: ...


    class azure.mgmt.providerhub.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: OperationsPutContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: OperationsPutContent, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                operations_put_content: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> OperationsPutContent: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationsDefinition]: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> List[OperationsDefinition]: ...


    class azure.mgmt.providerhub.operations.ProviderMonitorSettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: ProviderMonitorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderMonitorSetting]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: ProviderMonitorSetting, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderMonitorSetting]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderMonitorSetting]: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> ProviderMonitorSetting: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProviderMonitorSetting]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ProviderMonitorSetting]: ...

        @distributed_trace
        def update(
                self, 
                resource_group_name: str, 
                provider_monitor_setting_name: str, 
                **kwargs: Any
            ) -> ProviderMonitorSetting: ...


    class azure.mgmt.providerhub.operations.ProviderRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: ProviderRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: ProviderRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ProviderRegistration]: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def generate_operations(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> List[OperationsDefinition]: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ProviderRegistration: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[ProviderRegistration]: ...


    class azure.mgmt.providerhub.operations.ResourceActionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: ResourceManagementAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: ResourceManagementAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_delete_resources(
                self, 
                provider_namespace: str, 
                resource_action_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...


    class azure.mgmt.providerhub.operations.ResourceTypeRegistrationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: ResourceTypeRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceTypeRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: ResourceTypeRegistration, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceTypeRegistration]: ...

        @overload
        def begin_create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ResourceTypeRegistration]: ...

        @distributed_trace
        def begin_delete(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> ResourceTypeRegistration: ...

        @distributed_trace
        def list_by_provider_registration(
                self, 
                provider_namespace: str, 
                **kwargs: Any
            ) -> ItemPaged[ResourceTypeRegistration]: ...


    class azure.mgmt.providerhub.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: SkuResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @overload
        def create_or_update_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def delete(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def delete_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def get_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def get_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def get_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                sku: str, 
                **kwargs: Any
            ) -> SkuResource: ...

        @distributed_trace
        def list_by_resource_type_registrations(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                **kwargs: Any
            ) -> ItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_first(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                **kwargs: Any
            ) -> ItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_second(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                **kwargs: Any
            ) -> ItemPaged[SkuResource]: ...

        @distributed_trace
        def list_by_resource_type_registrations_nested_resource_type_third(
                self, 
                provider_namespace: str, 
                resource_type: str, 
                nested_resource_type_first: str, 
                nested_resource_type_second: str, 
                nested_resource_type_third: str, 
                **kwargs: Any
            ) -> ItemPaged[SkuResource]: ...


namespace azure.mgmt.providerhub.types

    class azure.mgmt.providerhub.types.AdditionalAuthorization(TypedDict, total=False):
        key "applicationId": str
        key "roleDefinitionId": str
        application_id: str
        role_definition_id: str


    class azure.mgmt.providerhub.types.AllowedResourceName(TypedDict, total=False):
        key "getActionVerb": str
        key "name": str
        get_action_verb: str
        name: str


    class azure.mgmt.providerhub.types.AllowedUnauthorizedActionsExtension(TypedDict, total=False):
        key "action": str
        key "intent": Union[str, Intent]
        action: str
        intent: Union[str, Intent]


    class azure.mgmt.providerhub.types.ApiProfile(TypedDict, total=False):
        key "apiVersion": str
        key "profileVersion": str
        api_version: str
        profile_version: str


    class azure.mgmt.providerhub.types.ApplicationDataAuthorization(TypedDict, total=False):
        key "role": Required[Union[str, Role]]
        resourceTypes: list[str]
        resource_types: list[str]
        role: Union[str, Role]


    class azure.mgmt.providerhub.types.ApplicationProviderAuthorization(TypedDict, total=False):
        key "managedByRoleDefinitionId": str
        key "roleDefinitionId": str
        managed_by_role_definition_id: str
        role_definition_id: str


    class azure.mgmt.providerhub.types.AsyncOperationPollingRules(TypedDict, total=False):
        key "additionalOptions": Union[str, AdditionalOptionsAsyncOperation]
        additional_options: Union[str, AdditionalOptionsAsyncOperation]
        authorizationActions: list[str]
        authorization_actions: list[str]


    class azure.mgmt.providerhub.types.AsyncTimeoutRule(TypedDict, total=False):
        key "actionName": str
        key "timeout": str
        action_name: str
        timeout: str


    class azure.mgmt.providerhub.types.AuthorizationActionMapping(TypedDict, total=False):
        key "desired": str
        key "original": str
        desired: str
        original: str


    class azure.mgmt.providerhub.types.AuthorizedApplication(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('AuthorizedApplicationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: AuthorizedApplicationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.AuthorizedApplicationProperties(TypedDict, total=False):
        key "providerAuthorization": ForwardRef('ApplicationProviderAuthorization', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        dataAuthorizations: list[ApplicationDataAuthorization]
        data_authorizations: list[ApplicationDataAuthorization]
        provider_authorization: ApplicationProviderAuthorization
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.providerhub.types.CanaryTrafficRegionRolloutConfiguration(TypedDict, total=False):
        regions: list[str]
        skipRegions: list[str]
        skip_regions: list[str]


    class azure.mgmt.providerhub.types.CheckNameAvailabilitySpecifications(TypedDict, total=False):
        key "enableDefaultValidation": bool
        enable_default_validation: bool
        resourceTypesWithCustomValidation: list[str]
        resource_types_with_custom_validation: list[str]


    class azure.mgmt.providerhub.types.CheckinManifestInfo(TypedDict, total=False):
        key "commitId": str
        key "isCheckedIn": Required[bool]
        key "pullRequest": str
        key "statusMessage": Required[str]
        commit_id: str
        is_checked_in: bool
        pull_request: str
        status_message: str


    class azure.mgmt.providerhub.types.CheckinManifestParams(TypedDict, total=False):
        key "baselineArmManifestLocation": Required[str]
        key "environment": Required[str]
        baseline_arm_manifest_location: str
        environment: str


    class azure.mgmt.providerhub.types.CustomRollout(ProxyResource):
        key "id": str
        key "name": str
        key "properties": Required[CustomRolloutProperties]
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: CustomRolloutProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.CustomRolloutProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "specification": Required[CustomRolloutPropertiesSpecification]
        key "status": ForwardRef('CustomRolloutPropertiesStatus', module='types')
        provisioning_state: Union[str, ProvisioningState]
        specification: CustomRolloutPropertiesSpecification
        status: CustomRolloutPropertiesStatus


    class azure.mgmt.providerhub.types.CustomRolloutPropertiesSpecification(CustomRolloutSpecification):
        key "autoProvisionConfig": ForwardRef('CustomRolloutSpecificationAutoProvisionConfig', module='types')
        key "canary": ForwardRef('CustomRolloutSpecificationCanary', module='types')
        key "providerRegistration": ForwardRef('CustomRolloutSpecificationProviderRegistration', module='types')
        key "refreshSubscriptionRegistration": bool
        key "skipReleaseScopeValidation": bool
        auto_provision_config: CustomRolloutSpecificationAutoProvisionConfig
        canary: CustomRolloutSpecificationCanary
        provider_registration: CustomRolloutSpecificationProviderRegistration
        refresh_subscription_registration: bool
        releaseScopes: list[str]
        release_scopes: list[str]
        resourceTypeRegistrations: list[ResourceTypeRegistration]
        resource_type_registrations: list[ResourceTypeRegistration]
        skip_release_scope_validation: bool


    class azure.mgmt.providerhub.types.CustomRolloutPropertiesStatus(CustomRolloutStatus):
        key "manifestCheckinStatus": ForwardRef('CustomRolloutStatusManifestCheckinStatus', module='types')
        completedRegions: list[str]
        completed_regions: list[str]
        failedOrSkippedRegions: dict[str, ExtendedErrorInfo]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: CustomRolloutStatusManifestCheckinStatus


    class azure.mgmt.providerhub.types.CustomRolloutSpecification(TypedDict, total=False):
        key "autoProvisionConfig": ForwardRef('CustomRolloutSpecificationAutoProvisionConfig', module='types')
        key "canary": ForwardRef('CustomRolloutSpecificationCanary', module='types')
        key "providerRegistration": ForwardRef('CustomRolloutSpecificationProviderRegistration', module='types')
        key "refreshSubscriptionRegistration": bool
        key "skipReleaseScopeValidation": bool
        auto_provision_config: CustomRolloutSpecificationAutoProvisionConfig
        canary: CustomRolloutSpecificationCanary
        provider_registration: CustomRolloutSpecificationProviderRegistration
        refresh_subscription_registration: bool
        releaseScopes: list[str]
        release_scopes: list[str]
        resourceTypeRegistrations: list[ResourceTypeRegistration]
        resource_type_registrations: list[ResourceTypeRegistration]
        skip_release_scope_validation: bool


    class azure.mgmt.providerhub.types.CustomRolloutSpecificationAutoProvisionConfig(TypedDict, total=False):
        key "resourceGraph": bool
        key "storage": bool
        resource_graph: bool
        storage: bool


    class azure.mgmt.providerhub.types.CustomRolloutSpecificationCanary(TrafficRegions):
        regions: list[str]


    class azure.mgmt.providerhub.types.CustomRolloutSpecificationProviderRegistration(ProviderRegistration):
        key "id": str
        key "kind": Union[str, ProviderRegistrationKind]
        key "name": str
        key "properties": ForwardRef('ProviderRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, ProviderRegistrationKind]
        name: str
        properties: ProviderRegistrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.CustomRolloutStatus(TypedDict, total=False):
        key "manifestCheckinStatus": ForwardRef('CustomRolloutStatusManifestCheckinStatus', module='types')
        completedRegions: list[str]
        completed_regions: list[str]
        failedOrSkippedRegions: dict[str, ExtendedErrorInfo]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: CustomRolloutStatusManifestCheckinStatus


    class azure.mgmt.providerhub.types.CustomRolloutStatusManifestCheckinStatus(CheckinManifestInfo):
        key "commitId": str
        key "isCheckedIn": Required[bool]
        key "pullRequest": str
        key "statusMessage": Required[str]
        commit_id: str
        is_checked_in: bool
        pull_request: str
        status_message: str


    class azure.mgmt.providerhub.types.DefaultRollout(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('DefaultRolloutProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: DefaultRolloutProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.DefaultRolloutProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "specification": ForwardRef('DefaultRolloutPropertiesSpecification', module='types')
        key "status": ForwardRef('DefaultRolloutPropertiesStatus', module='types')
        provisioning_state: Union[str, ProvisioningState]
        specification: DefaultRolloutPropertiesSpecification
        status: DefaultRolloutPropertiesStatus


    class azure.mgmt.providerhub.types.DefaultRolloutPropertiesSpecification(DefaultRolloutSpecification):
        key "autoProvisionConfig": ForwardRef('DefaultRolloutSpecificationAutoProvisionConfig', module='types')
        key "canary": ForwardRef('DefaultRolloutSpecificationCanary', module='types')
        key "expeditedRollout": ForwardRef('DefaultRolloutSpecificationExpeditedRollout', module='types')
        key "highTraffic": ForwardRef('DefaultRolloutSpecificationHighTraffic', module='types')
        key "lowTraffic": ForwardRef('DefaultRolloutSpecificationLowTraffic', module='types')
        key "mediumTraffic": ForwardRef('DefaultRolloutSpecificationMediumTraffic', module='types')
        key "providerRegistration": ForwardRef('DefaultRolloutSpecificationProviderRegistration', module='types')
        key "restOfTheWorldGroupOne": ForwardRef('DefaultRolloutSpecificationRestOfTheWorldGroupOne', module='types')
        key "restOfTheWorldGroupTwo": ForwardRef('DefaultRolloutSpecificationRestOfTheWorldGroupTwo', module='types')
        auto_provision_config: DefaultRolloutSpecificationAutoProvisionConfig
        canary: DefaultRolloutSpecificationCanary
        expedited_rollout: DefaultRolloutSpecificationExpeditedRollout
        high_traffic: DefaultRolloutSpecificationHighTraffic
        low_traffic: DefaultRolloutSpecificationLowTraffic
        medium_traffic: DefaultRolloutSpecificationMediumTraffic
        provider_registration: DefaultRolloutSpecificationProviderRegistration
        resourceTypeRegistrations: list[ResourceTypeRegistration]
        resource_type_registrations: list[ResourceTypeRegistration]
        rest_of_the_world_group_one: DefaultRolloutSpecificationRestOfTheWorldGroupOne
        rest_of_the_world_group_two: DefaultRolloutSpecificationRestOfTheWorldGroupTwo


    class azure.mgmt.providerhub.types.DefaultRolloutPropertiesStatus(DefaultRolloutStatus):
        key "manifestCheckinStatus": ForwardRef('DefaultRolloutStatusManifestCheckinStatus', module='types')
        key "nextTrafficRegion": Union[str, TrafficRegionCategory]
        key "nextTrafficRegionScheduledTime": str
        key "subscriptionReregistrationResult": Union[str, SubscriptionReregistrationResult]
        completedRegions: list[str]
        completed_regions: list[str]
        failedOrSkippedRegions: dict[str, ExtendedErrorInfo]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: DefaultRolloutStatusManifestCheckinStatus
        next_traffic_region: Union[str, TrafficRegionCategory]
        next_traffic_region_scheduled_time: str
        subscription_reregistration_result: Union[str, SubscriptionReregistrationResult]


    class azure.mgmt.providerhub.types.DefaultRolloutSpecification(TypedDict, total=False):
        key "autoProvisionConfig": ForwardRef('DefaultRolloutSpecificationAutoProvisionConfig', module='types')
        key "canary": ForwardRef('DefaultRolloutSpecificationCanary', module='types')
        key "expeditedRollout": ForwardRef('DefaultRolloutSpecificationExpeditedRollout', module='types')
        key "highTraffic": ForwardRef('DefaultRolloutSpecificationHighTraffic', module='types')
        key "lowTraffic": ForwardRef('DefaultRolloutSpecificationLowTraffic', module='types')
        key "mediumTraffic": ForwardRef('DefaultRolloutSpecificationMediumTraffic', module='types')
        key "providerRegistration": ForwardRef('DefaultRolloutSpecificationProviderRegistration', module='types')
        key "restOfTheWorldGroupOne": ForwardRef('DefaultRolloutSpecificationRestOfTheWorldGroupOne', module='types')
        key "restOfTheWorldGroupTwo": ForwardRef('DefaultRolloutSpecificationRestOfTheWorldGroupTwo', module='types')
        auto_provision_config: DefaultRolloutSpecificationAutoProvisionConfig
        canary: DefaultRolloutSpecificationCanary
        expedited_rollout: DefaultRolloutSpecificationExpeditedRollout
        high_traffic: DefaultRolloutSpecificationHighTraffic
        low_traffic: DefaultRolloutSpecificationLowTraffic
        medium_traffic: DefaultRolloutSpecificationMediumTraffic
        provider_registration: DefaultRolloutSpecificationProviderRegistration
        resourceTypeRegistrations: list[ResourceTypeRegistration]
        resource_type_registrations: list[ResourceTypeRegistration]
        rest_of_the_world_group_one: DefaultRolloutSpecificationRestOfTheWorldGroupOne
        rest_of_the_world_group_two: DefaultRolloutSpecificationRestOfTheWorldGroupTwo


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationAutoProvisionConfig(TypedDict, total=False):
        key "resourceGraph": bool
        key "storage": bool
        resource_graph: bool
        storage: bool


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationCanary(CanaryTrafficRegionRolloutConfiguration):
        regions: list[str]
        skipRegions: list[str]
        skip_regions: list[str]


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationExpeditedRollout(ExpeditedRolloutDefinition):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationHighTraffic(TrafficRegionRolloutConfiguration):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationLowTraffic(TrafficRegionRolloutConfiguration):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationMediumTraffic(TrafficRegionRolloutConfiguration):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationProviderRegistration(ProviderRegistration):
        key "id": str
        key "kind": Union[str, ProviderRegistrationKind]
        key "name": str
        key "properties": ForwardRef('ProviderRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, ProviderRegistrationKind]
        name: str
        properties: ProviderRegistrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationRestOfTheWorldGroupOne(TrafficRegionRolloutConfiguration):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.DefaultRolloutSpecificationRestOfTheWorldGroupTwo(TrafficRegionRolloutConfiguration):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.DefaultRolloutStatus(RolloutStatusBase):
        key "manifestCheckinStatus": ForwardRef('DefaultRolloutStatusManifestCheckinStatus', module='types')
        key "nextTrafficRegion": Union[str, TrafficRegionCategory]
        key "nextTrafficRegionScheduledTime": str
        key "subscriptionReregistrationResult": Union[str, SubscriptionReregistrationResult]
        completedRegions: list[str]
        completed_regions: list[str]
        failedOrSkippedRegions: dict[str, ExtendedErrorInfo]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]
        manifest_checkin_status: DefaultRolloutStatusManifestCheckinStatus
        next_traffic_region: Union[str, TrafficRegionCategory]
        next_traffic_region_scheduled_time: str
        subscription_reregistration_result: Union[str, SubscriptionReregistrationResult]


    class azure.mgmt.providerhub.types.DefaultRolloutStatusManifestCheckinStatus(CheckinManifestInfo):
        key "commitId": str
        key "isCheckedIn": Required[bool]
        key "pullRequest": str
        key "statusMessage": Required[str]
        commit_id: str
        is_checked_in: bool
        pull_request: str
        status_message: str


    class azure.mgmt.providerhub.types.DeleteDependency(TypedDict, total=False):
        key "linkedProperty": str
        key "linkedType": str
        linked_property: str
        linked_type: str
        requiredFeatures: list[str]
        required_features: list[str]


    class azure.mgmt.providerhub.types.DstsConfiguration(TypedDict, total=False):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.EndpointInformation(TypedDict, total=False):
        key "endpoint": str
        key "endpointType": Union[str, NotificationEndpointType]
        key "schemaVersion": str
        endpoint: str
        endpoint_type: Union[str, NotificationEndpointType]
        schema_version: str


    class azure.mgmt.providerhub.types.ExpeditedRolloutDefinition(TypedDict, total=False):
        key "enabled": bool
        enabled: bool


    class azure.mgmt.providerhub.types.ExtendedErrorInfo(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[TypedErrorInfo]
        additional_info: list[TypedErrorInfo]
        code: str
        details: list[ExtendedErrorInfo]
        message: str
        target: str


    class azure.mgmt.providerhub.types.ExtendedLocationOptions(TypedDict, total=False):
        key "supportedPolicy": Union[str, ResourceTypeExtendedLocationPolicy]
        key "type": Union[str, ExtendedLocationType]
        supported_policy: Union[str, ResourceTypeExtendedLocationPolicy]
        type: Union[str, ExtendedLocationType]


    class azure.mgmt.providerhub.types.ExtensionOptions(TypedDict, total=False):
        request: list[Union[str, ExtensionOptionType]]
        response: list[Union[str, ExtensionOptionType]]


    class azure.mgmt.providerhub.types.FanoutLinkedNotificationRule(TypedDict, total=False):
        key "dstsConfiguration": ForwardRef('FanoutLinkedNotificationRuleDstsConfiguration', module='types')
        key "tokenAuthConfiguration": ForwardRef('TokenAuthConfiguration', module='types')
        actions: list[str]
        dsts_configuration: FanoutLinkedNotificationRuleDstsConfiguration
        endpoints: list[ResourceProviderEndpoint]
        token_auth_configuration: TokenAuthConfiguration


    class azure.mgmt.providerhub.types.FanoutLinkedNotificationRuleDstsConfiguration(DstsConfiguration):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.FeaturesRule(TypedDict, total=False):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.FilterRule(TypedDict, total=False):
        key "filterQuery": str
        endpointInformation: list[EndpointInformation]
        endpoint_information: list[EndpointInformation]
        filter_query: str


    class azure.mgmt.providerhub.types.FrontloadPayload(TypedDict, total=False):
        key "properties": Required[FrontloadPayloadProperties]
        properties: FrontloadPayloadProperties


    class azure.mgmt.providerhub.types.FrontloadPayloadProperties(TypedDict, total=False):
        key "copyFromLocation": Required[str]
        key "environmentType": Required[Union[str, AvailableCheckInManifestEnvironment]]
        key "excludeResourceTypes": Required[list[str]]
        key "frontloadLocation": Required[str]
        key "ignoreFields": Required[list[str]]
        key "includeResourceTypes": Required[list[str]]
        key "operationType": Required[str]
        key "overrideEndpointLevelFields": Required[FrontloadPayloadPropertiesOverrideEndpointLevelFields]
        key "overrideManifestLevelFields": Required[FrontloadPayloadPropertiesOverrideManifestLevelFields]
        key "providerNamespace": Required[str]
        key "serviceFeatureFlag": Required[Union[str, ServiceFeatureFlagAction]]
        copy_from_location: str
        environment_type: Union[str, AvailableCheckInManifestEnvironment]
        exclude_resource_types: list[str]
        frontload_location: str
        ignore_fields: list[str]
        include_resource_types: list[str]
        operation_type: str
        override_endpoint_level_fields: FrontloadPayloadPropertiesOverrideEndpointLevelFields
        override_manifest_level_fields: FrontloadPayloadPropertiesOverrideManifestLevelFields
        provider_namespace: str
        service_feature_flag: Union[str, ServiceFeatureFlagAction]


    class azure.mgmt.providerhub.types.FrontloadPayloadPropertiesOverrideEndpointLevelFields(ResourceTypeEndpointBase):
        key "apiVersion": Required[str]
        key "apiVersions": Required[list[str]]
        key "dstsConfiguration": Required[ResourceTypeEndpointBaseDstsConfiguration]
        key "enabled": Required[bool]
        key "endpointType": Required[Union[str, EndpointType]]
        key "endpointUri": Required[str]
        key "featuresRule": Required[ResourceTypeEndpointBaseFeaturesRule]
        key "locations": Required[list[str]]
        key "requiredFeatures": Required[list[str]]
        key "skuLink": Required[str]
        key "timeout": Required[str]
        key "zones": Required[list[str]]
        api_version: str
        api_versions: list[str]
        dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration
        enabled: bool
        endpoint_type: Union[str, EndpointType]
        endpoint_uri: str
        features_rule: ResourceTypeEndpointBaseFeaturesRule
        locations: list[str]
        required_features: list[str]
        sku_link: str
        timeout: str
        zones: list[str]


    class azure.mgmt.providerhub.types.FrontloadPayloadPropertiesOverrideManifestLevelFields(ManifestLevelPropertyBag):
        resourceHydrationAccounts: list[ResourceHydrationAccount]
        resource_hydration_accounts: list[ResourceHydrationAccount]


    class azure.mgmt.providerhub.types.IdentityManagementProperties(TypedDict, total=False):
        key "applicationId": str
        key "type": Union[str, IdentityManagementTypes]
        applicationIds: list[str]
        application_id: str
        application_ids: list[str]
        delegationAppIds: list[str]
        delegation_app_ids: list[str]
        type: Union[str, IdentityManagementTypes]


    class azure.mgmt.providerhub.types.LegacyDisallowedCondition(TypedDict, total=False):
        key "feature": str
        disallowedLegacyOperations: list[Union[str, LegacyOperation]]
        disallowed_legacy_operations: list[Union[str, LegacyOperation]]
        feature: str


    class azure.mgmt.providerhub.types.LightHouseAuthorization(TypedDict, total=False):
        key "principalId": Required[str]
        key "roleDefinitionId": Required[str]
        principal_id: str
        role_definition_id: str


    class azure.mgmt.providerhub.types.LinkedAccessCheck(TypedDict, total=False):
        key "actionName": str
        key "linkedAction": str
        key "linkedActionVerb": str
        key "linkedProperty": str
        key "linkedType": str
        action_name: str
        linked_action: str
        linked_action_verb: str
        linked_property: str
        linked_type: str


    class azure.mgmt.providerhub.types.LinkedNotificationRule(TypedDict, total=False):
        key "linkedNotificationTimeout": str
        actions: list[str]
        actionsOnFailedOperation: list[str]
        actions_on_failed_operation: list[str]
        fastPathActions: list[str]
        fastPathActionsOnFailedOperation: list[str]
        fast_path_actions: list[str]
        fast_path_actions_on_failed_operation: list[str]
        linked_notification_timeout: str


    class azure.mgmt.providerhub.types.LinkedOperationRule(TypedDict, total=False):
        key "linkedAction": Required[Union[str, LinkedAction]]
        key "linkedOperation": Required[Union[str, LinkedOperation]]
        dependsOnTypes: list[str]
        depends_on_types: list[str]
        linked_action: Union[str, LinkedAction]
        linked_operation: Union[str, LinkedOperation]


    class azure.mgmt.providerhub.types.LocalizedOperationDefinition(TypedDict, total=False):
        key "actionType": Union[str, OperationActionType]
        key "display": Required[LocalizedOperationDefinitionDisplay]
        key "isDataAction": bool
        key "name": Required[str]
        key "origin": Union[str, OperationOrigins]
        action_type: Union[str, OperationActionType]
        display: LocalizedOperationDefinitionDisplay
        is_data_action: bool
        name: str
        origin: Union[str, OperationOrigins]


    class azure.mgmt.providerhub.types.LocalizedOperationDefinitionDisplay(LocalizedOperationDisplayDefinition):
        key "cs": ForwardRef('LocalizedOperationDisplayDefinitionCs', module='types')
        key "de": ForwardRef('LocalizedOperationDisplayDefinitionDe', module='types')
        key "default": Required[LocalizedOperationDisplayDefinitionDefault]
        key "en": ForwardRef('LocalizedOperationDisplayDefinitionEn', module='types')
        key "es": ForwardRef('LocalizedOperationDisplayDefinitionEs', module='types')
        key "fr": ForwardRef('LocalizedOperationDisplayDefinitionFr', module='types')
        key "hu": ForwardRef('LocalizedOperationDisplayDefinitionHu', module='types')
        key "it": ForwardRef('LocalizedOperationDisplayDefinitionIt', module='types')
        key "ja": ForwardRef('LocalizedOperationDisplayDefinitionJa', module='types')
        key "ko": ForwardRef('LocalizedOperationDisplayDefinitionKo', module='types')
        key "nl": ForwardRef('LocalizedOperationDisplayDefinitionNl', module='types')
        key "pl": ForwardRef('LocalizedOperationDisplayDefinitionPl', module='types')
        key "ptBR": ForwardRef('LocalizedOperationDisplayDefinitionPtBR', module='types')
        key "ptPT": ForwardRef('LocalizedOperationDisplayDefinitionPtPT', module='types')
        key "ru": ForwardRef('LocalizedOperationDisplayDefinitionRu', module='types')
        key "sv": ForwardRef('LocalizedOperationDisplayDefinitionSv', module='types')
        key "zhHans": ForwardRef('LocalizedOperationDisplayDefinitionZhHans', module='types')
        key "zhHant": ForwardRef('LocalizedOperationDisplayDefinitionZhHant', module='types')
        cs: LocalizedOperationDisplayDefinitionCs
        de: LocalizedOperationDisplayDefinitionDe
        default: LocalizedOperationDisplayDefinitionDefault
        en: LocalizedOperationDisplayDefinitionEn
        es: LocalizedOperationDisplayDefinitionEs
        fr: LocalizedOperationDisplayDefinitionFr
        hu: LocalizedOperationDisplayDefinitionHu
        it: LocalizedOperationDisplayDefinitionIt
        ja: LocalizedOperationDisplayDefinitionJa
        ko: LocalizedOperationDisplayDefinitionKo
        nl: LocalizedOperationDisplayDefinitionNl
        pl: LocalizedOperationDisplayDefinitionPl
        pt_br: LocalizedOperationDisplayDefinitionPtBR
        pt_pt: LocalizedOperationDisplayDefinitionPtPT
        ru: LocalizedOperationDisplayDefinitionRu
        sv: LocalizedOperationDisplayDefinitionSv
        zh_hans: LocalizedOperationDisplayDefinitionZhHans
        zh_hant: LocalizedOperationDisplayDefinitionZhHant


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinition(TypedDict, total=False):
        key "cs": ForwardRef('LocalizedOperationDisplayDefinitionCs', module='types')
        key "de": ForwardRef('LocalizedOperationDisplayDefinitionDe', module='types')
        key "default": Required[LocalizedOperationDisplayDefinitionDefault]
        key "en": ForwardRef('LocalizedOperationDisplayDefinitionEn', module='types')
        key "es": ForwardRef('LocalizedOperationDisplayDefinitionEs', module='types')
        key "fr": ForwardRef('LocalizedOperationDisplayDefinitionFr', module='types')
        key "hu": ForwardRef('LocalizedOperationDisplayDefinitionHu', module='types')
        key "it": ForwardRef('LocalizedOperationDisplayDefinitionIt', module='types')
        key "ja": ForwardRef('LocalizedOperationDisplayDefinitionJa', module='types')
        key "ko": ForwardRef('LocalizedOperationDisplayDefinitionKo', module='types')
        key "nl": ForwardRef('LocalizedOperationDisplayDefinitionNl', module='types')
        key "pl": ForwardRef('LocalizedOperationDisplayDefinitionPl', module='types')
        key "ptBR": ForwardRef('LocalizedOperationDisplayDefinitionPtBR', module='types')
        key "ptPT": ForwardRef('LocalizedOperationDisplayDefinitionPtPT', module='types')
        key "ru": ForwardRef('LocalizedOperationDisplayDefinitionRu', module='types')
        key "sv": ForwardRef('LocalizedOperationDisplayDefinitionSv', module='types')
        key "zhHans": ForwardRef('LocalizedOperationDisplayDefinitionZhHans', module='types')
        key "zhHant": ForwardRef('LocalizedOperationDisplayDefinitionZhHant', module='types')
        cs: LocalizedOperationDisplayDefinitionCs
        de: LocalizedOperationDisplayDefinitionDe
        default: LocalizedOperationDisplayDefinitionDefault
        en: LocalizedOperationDisplayDefinitionEn
        es: LocalizedOperationDisplayDefinitionEs
        fr: LocalizedOperationDisplayDefinitionFr
        hu: LocalizedOperationDisplayDefinitionHu
        it: LocalizedOperationDisplayDefinitionIt
        ja: LocalizedOperationDisplayDefinitionJa
        ko: LocalizedOperationDisplayDefinitionKo
        nl: LocalizedOperationDisplayDefinitionNl
        pl: LocalizedOperationDisplayDefinitionPl
        pt_br: LocalizedOperationDisplayDefinitionPtBR
        pt_pt: LocalizedOperationDisplayDefinitionPtPT
        ru: LocalizedOperationDisplayDefinitionRu
        sv: LocalizedOperationDisplayDefinitionSv
        zh_hans: LocalizedOperationDisplayDefinitionZhHans
        zh_hant: LocalizedOperationDisplayDefinitionZhHant


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionCs(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionDe(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionDefault(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionEn(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionEs(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionFr(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionHu(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionIt(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionJa(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionKo(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionNl(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionPl(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionPtBR(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionPtPT(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionRu(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionSv(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionZhHans(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocalizedOperationDisplayDefinitionZhHant(OperationsDisplayDefinition):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.LocationQuotaRule(TypedDict, total=False):
        key "location": str
        key "policy": Union[str, QuotaPolicy]
        key "quotaId": str
        location: str
        policy: Union[str, QuotaPolicy]
        quota_id: str


    class azure.mgmt.providerhub.types.LoggingHiddenPropertyPath(TypedDict, total=False):
        hiddenPathsOnRequest: list[str]
        hiddenPathsOnResponse: list[str]
        hidden_paths_on_request: list[str]
        hidden_paths_on_response: list[str]


    class azure.mgmt.providerhub.types.LoggingRule(TypedDict, total=False):
        key "action": Required[str]
        key "detailLevel": Required[Union[str, LoggingDetails]]
        key "direction": Required[Union[str, LoggingDirections]]
        key "hiddenPropertyPaths": ForwardRef('LoggingRuleHiddenPropertyPaths', module='types')
        action: str
        detail_level: Union[str, LoggingDetails]
        direction: Union[str, LoggingDirections]
        hidden_property_paths: LoggingRuleHiddenPropertyPaths


    class azure.mgmt.providerhub.types.LoggingRuleHiddenPropertyPaths(LoggingHiddenPropertyPath):
        hiddenPathsOnRequest: list[str]
        hiddenPathsOnResponse: list[str]
        hidden_paths_on_request: list[str]
        hidden_paths_on_response: list[str]


    class azure.mgmt.providerhub.types.ManifestLevelPropertyBag(TypedDict, total=False):
        resourceHydrationAccounts: list[ResourceHydrationAccount]
        resource_hydration_accounts: list[ResourceHydrationAccount]


    class azure.mgmt.providerhub.types.Notification(TypedDict, total=False):
        key "notificationType": Union[str, NotificationType]
        key "skipNotifications": Union[str, SkipNotifications]
        notification_type: Union[str, NotificationType]
        skip_notifications: Union[str, SkipNotifications]


    class azure.mgmt.providerhub.types.NotificationEndpoint(TypedDict, total=False):
        key "notificationDestination": str
        locations: list[str]
        notification_destination: str


    class azure.mgmt.providerhub.types.NotificationRegistration(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('NotificationRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: NotificationRegistrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.NotificationRegistrationProperties(TypedDict, total=False):
        key "messageScope": Union[str, MessageScope]
        key "notificationMode": Union[str, NotificationMode]
        key "provisioningState": Union[str, ProvisioningState]
        includedEvents: list[str]
        included_events: list[str]
        message_scope: Union[str, MessageScope]
        notificationEndpoints: list[NotificationEndpoint]
        notification_endpoints: list[NotificationEndpoint]
        notification_mode: Union[str, NotificationMode]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.providerhub.types.OpenApiConfiguration(TypedDict, total=False):
        key "validation": ForwardRef('OpenApiValidation', module='types')
        validation: OpenApiValidation


    class azure.mgmt.providerhub.types.OpenApiValidation(TypedDict, total=False):
        key "allowNoncompliantCollectionResponse": bool
        allow_noncompliant_collection_response: bool


    class azure.mgmt.providerhub.types.OperationsContentProperties(TypedDict, total=False):
        contents: list[LocalizedOperationDefinition]


    class azure.mgmt.providerhub.types.OperationsDisplayDefinition(TypedDict, total=False):
        key "description": Required[str]
        key "operation": Required[str]
        key "provider": Required[str]
        key "resource": Required[str]
        description: str
        operation: str
        provider: str
        resource: str


    class azure.mgmt.providerhub.types.OperationsPutContent(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('OperationsPutContentProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: OperationsPutContentProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.OperationsPutContentProperties(OperationsContentProperties):
        contents: list[LocalizedOperationDefinition]


    class azure.mgmt.providerhub.types.PrivateResourceProviderConfiguration(TypedDict, total=False):
        allowedSubscriptions: list[str]
        allowed_subscriptions: list[str]


    class azure.mgmt.providerhub.types.ProviderHubMetadata(TypedDict, total=False):
        key "directRpRoleDefinitionId": str
        key "globalAsyncOperationResourceTypeName": str
        key "providerAuthentication": ForwardRef('ProviderHubMetadataProviderAuthentication', module='types')
        key "regionalAsyncOperationResourceTypeName": str
        key "thirdPartyProviderAuthorization": ForwardRef('ProviderHubMetadataThirdPartyProviderAuthorization', module='types')
        direct_rp_role_definition_id: str
        global_async_operation_resource_type_name: str
        providerAuthorizations: list[ResourceProviderAuthorization]
        provider_authentication: ProviderHubMetadataProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        regional_async_operation_resource_type_name: str
        third_party_provider_authorization: ProviderHubMetadataThirdPartyProviderAuthorization


    class azure.mgmt.providerhub.types.ProviderHubMetadataProviderAuthentication(ResourceProviderAuthentication):
        key "allowedAudiences": Required[list[str]]
        allowed_audiences: list[str]


    class azure.mgmt.providerhub.types.ProviderHubMetadataThirdPartyProviderAuthorization(ThirdPartyProviderAuthorization):
        key "managedByTenantId": str
        authorizations: list[LightHouseAuthorization]
        managed_by_tenant_id: str


    class azure.mgmt.providerhub.types.ProviderMonitorSetting(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('ProviderMonitorSettingProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: ProviderMonitorSettingProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.providerhub.types.ProviderMonitorSettingProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioning_state: Union[str, ProvisioningState]


    class azure.mgmt.providerhub.types.ProviderRegistration(ProxyResource):
        key "id": str
        key "kind": Union[str, ProviderRegistrationKind]
        key "name": str
        key "properties": ForwardRef('ProviderRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, ProviderRegistrationKind]
        name: str
        properties: ProviderRegistrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.ProviderRegistrationProperties(ResourceProviderManifestProperties):
        key "crossTenantTokenValidation": Union[str, CrossTenantTokenValidation]
        key "customManifestVersion": str
        key "dstsConfiguration": ForwardRef('ResourceProviderManifestPropertiesDstsConfiguration', module='types')
        key "enableTenantLinkedNotification": Optional[bool]
        key "featuresRule": ForwardRef('ResourceProviderManifestPropertiesFeaturesRule', module='types')
        key "legacyNamespace": str
        key "management": ForwardRef('ResourceProviderManifestPropertiesManagement', module='types')
        key "metadata": Any
        key "namespace": str
        key "notificationOptions": Union[str, NotificationOptions]
        key "notificationSettings": ForwardRef('ResourceProviderManifestPropertiesNotificationSettings', module='types')
        key "privateResourceProviderConfiguration": ForwardRef('ProviderRegistrationPropertiesPrivateResourceProviderConfiguration', module='types')
        key "providerAuthentication": ForwardRef('ResourceProviderManifestPropertiesProviderAuthentication', module='types')
        key "providerHubMetadata": ForwardRef('ProviderRegistrationPropertiesProviderHubMetadata', module='types')
        key "providerType": Union[str, ResourceProviderType]
        key "providerVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "requestHeaderOptions": ForwardRef('ResourceProviderManifestPropertiesRequestHeaderOptions', module='types')
        key "resourceGroupLockOptionDuringMove": ForwardRef('ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove', module='types')
        key "resourceProviderAuthorizationRules": ForwardRef('ResourceProviderAuthorizationRules', module='types')
        key "responseOptions": ForwardRef('ResourceProviderManifestPropertiesResponseOptions', module='types')
        key "serviceName": str
        key "subscriptionLifecycleNotificationSpecifications": ForwardRef('ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications', module='types')
        key "templateDeploymentOptions": ForwardRef('ResourceProviderManifestPropertiesTemplateDeploymentOptions', module='types')
        key "tokenAuthConfiguration": ForwardRef('TokenAuthConfiguration', module='types')
        capabilities: list[ResourceProviderCapabilities]
        cross_tenant_token_validation: Union[str, CrossTenantTokenValidation]
        custom_manifest_version: str
        dsts_configuration: ResourceProviderManifestPropertiesDstsConfiguration
        enable_tenant_linked_notification: bool
        features_rule: ResourceProviderManifestPropertiesFeaturesRule
        globalNotificationEndpoints: list[ResourceProviderEndpoint]
        global_notification_endpoints: list[ResourceProviderEndpoint]
        legacyRegistrations: list[str]
        legacy_namespace: str
        legacy_registrations: list[str]
        linkedNotificationRules: list[FanoutLinkedNotificationRule]
        linked_notification_rules: list[FanoutLinkedNotificationRule]
        management: ResourceProviderManifestPropertiesManagement
        managementGroupGlobalNotificationEndpoints: list[ResourceProviderEndpoint]
        management_group_global_notification_endpoints: list[ResourceProviderEndpoint]
        metadata: Any
        namespace: str
        notification_options: Union[str, NotificationOptions]
        notification_settings: ResourceProviderManifestPropertiesNotificationSettings
        notifications: list[Notification]
        optionalFeatures: list[str]
        optional_features: list[str]
        private_resource_provider_configuration: ProviderRegistrationPropertiesPrivateResourceProviderConfiguration
        providerAuthorizations: list[ResourceProviderAuthorization]
        provider_authentication: ResourceProviderManifestPropertiesProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        provider_hub_metadata: ProviderRegistrationPropertiesProviderHubMetadata
        provider_type: Union[str, ResourceProviderType]
        provider_version: str
        provisioning_state: Union[str, ProvisioningState]
        request_header_options: ResourceProviderManifestPropertiesRequestHeaderOptions
        requiredFeatures: list[str]
        required_features: list[str]
        resourceHydrationAccounts: list[ResourceHydrationAccount]
        resource_group_lock_option_during_move: ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove
        resource_hydration_accounts: list[ResourceHydrationAccount]
        resource_provider_authorization_rules: ResourceProviderAuthorizationRules
        response_options: ResourceProviderManifestPropertiesResponseOptions
        service_name: str
        services: list[ResourceProviderService]
        subscription_lifecycle_notification_specifications: ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications
        template_deployment_options: ResourceProviderManifestPropertiesTemplateDeploymentOptions
        token_auth_configuration: TokenAuthConfiguration


    class azure.mgmt.providerhub.types.ProviderRegistrationPropertiesPrivateResourceProviderConfiguration(PrivateResourceProviderConfiguration):
        allowedSubscriptions: list[str]
        allowed_subscriptions: list[str]


    class azure.mgmt.providerhub.types.ProviderRegistrationPropertiesProviderHubMetadata(ProviderHubMetadata):
        key "directRpRoleDefinitionId": str
        key "globalAsyncOperationResourceTypeName": str
        key "providerAuthentication": ForwardRef('ProviderHubMetadataProviderAuthentication', module='types')
        key "regionalAsyncOperationResourceTypeName": str
        key "thirdPartyProviderAuthorization": ForwardRef('ProviderHubMetadataThirdPartyProviderAuthorization', module='types')
        direct_rp_role_definition_id: str
        global_async_operation_resource_type_name: str
        providerAuthorizations: list[ResourceProviderAuthorization]
        provider_authentication: ProviderHubMetadataProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        regional_async_operation_resource_type_name: str
        third_party_provider_authorization: ProviderHubMetadataThirdPartyProviderAuthorization


    class azure.mgmt.providerhub.types.ProviderRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications(SubscriptionLifecycleNotificationSpecifications):
        key "softDeleteTTL": str
        soft_delete_ttl: str
        subscriptionStateOverrideActions: list[SubscriptionStateOverrideAction]
        subscription_state_override_actions: list[SubscriptionStateOverrideAction]


    class azure.mgmt.providerhub.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.QuotaRule(TypedDict, total=False):
        key "quotaPolicy": Union[str, QuotaPolicy]
        locationRules: list[LocationQuotaRule]
        location_rules: list[LocationQuotaRule]
        quota_policy: Union[str, QuotaPolicy]
        requiredFeatures: list[str]
        required_features: list[str]


    class azure.mgmt.providerhub.types.RequestHeaderOptions(TypedDict, total=False):
        key "optInHeaders": Union[str, OptInHeaderType]
        key "optOutHeaders": Union[str, OptOutHeaderType]
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]


    class azure.mgmt.providerhub.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.ResourceAccessRole(TypedDict, total=False):
        actions: list[str]
        allowedGroupClaims: list[str]
        allowed_group_claims: list[str]


    class azure.mgmt.providerhub.types.ResourceConcurrencyControlOption(TypedDict, total=False):
        key "policy": Union[str, Policy]
        policy: Union[str, Policy]


    class azure.mgmt.providerhub.types.ResourceGraphConfiguration(TypedDict, total=False):
        key "apiVersion": str
        key "enabled": bool
        api_version: str
        enabled: bool


    class azure.mgmt.providerhub.types.ResourceHydrationAccount(TypedDict, total=False):
        key "accountName": str
        key "encryptedKey": str
        key "maxChildResourceConsistencyJobLimit": int
        key "subscriptionId": str
        account_name: str
        encrypted_key: str
        max_child_resource_consistency_job_limit: int
        subscription_id: str


    class azure.mgmt.providerhub.types.ResourceManagementAction(TypedDict, total=False):
        resources: list[ResourceManagementEntity]


    class azure.mgmt.providerhub.types.ResourceManagementEntity(TypedDict, total=False):
        key "homeTenantId": str
        key "location": str
        key "resourceId": Required[str]
        key "status": str
        home_tenant_id: str
        location: str
        resource_id: str
        status: str


    class azure.mgmt.providerhub.types.ResourceMovePolicy(TypedDict, total=False):
        key "crossResourceGroupMoveEnabled": bool
        key "crossSubscriptionMoveEnabled": bool
        key "validationRequired": bool
        cross_resource_group_move_enabled: bool
        cross_subscription_move_enabled: bool
        validation_required: bool


    class azure.mgmt.providerhub.types.ResourceProviderAuthentication(TypedDict, total=False):
        key "allowedAudiences": Required[list[str]]
        allowed_audiences: list[str]


    class azure.mgmt.providerhub.types.ResourceProviderAuthorization(TypedDict, total=False):
        key "applicationId": str
        key "groupingTag": str
        key "managedByAuthorization": ForwardRef('ResourceProviderAuthorizationManagedByAuthorization', module='types')
        key "managedByRoleDefinitionId": str
        key "roleDefinitionId": str
        allowedThirdPartyExtensions: list[ThirdPartyExtension]
        allowed_third_party_extensions: list[ThirdPartyExtension]
        application_id: str
        grouping_tag: str
        managed_by_authorization: ResourceProviderAuthorizationManagedByAuthorization
        managed_by_role_definition_id: str
        role_definition_id: str


    class azure.mgmt.providerhub.types.ResourceProviderAuthorizationManagedByAuthorization(TypedDict, total=False):
        key "allowManagedByInheritance": bool
        key "managedByResourceRoleDefinitionId": str
        additionalAuthorizations: list[AdditionalAuthorization]
        additional_authorizations: list[AdditionalAuthorization]
        allow_managed_by_inheritance: bool
        managed_by_resource_role_definition_id: str


    class azure.mgmt.providerhub.types.ResourceProviderAuthorizationRules(TypedDict, total=False):
        key "asyncOperationPollingRules": ForwardRef('AsyncOperationPollingRules', module='types')
        async_operation_polling_rules: AsyncOperationPollingRules


    class azure.mgmt.providerhub.types.ResourceProviderCapabilities(TypedDict, total=False):
        key "effect": Required[Union[str, ResourceProviderCapabilitiesEffect]]
        key "quotaId": Required[str]
        effect: Union[str, ResourceProviderCapabilitiesEffect]
        quota_id: str
        requiredFeatures: list[str]
        required_features: list[str]


    class azure.mgmt.providerhub.types.ResourceProviderEndpoint(TypedDict, total=False):
        key "enabled": bool
        key "endpointType": Union[str, EndpointType]
        key "endpointUri": str
        key "featuresRule": ForwardRef('ResourceProviderEndpointFeaturesRule', module='types')
        key "skuLink": str
        key "timeout": str
        apiVersions: list[str]
        api_versions: list[str]
        enabled: bool
        endpoint_type: Union[str, EndpointType]
        endpoint_uri: str
        features_rule: ResourceProviderEndpointFeaturesRule
        locations: list[str]
        requiredFeatures: list[str]
        required_features: list[str]
        sku_link: str
        timeout: str


    class azure.mgmt.providerhub.types.ResourceProviderEndpointFeaturesRule(FeaturesRule):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.ResourceProviderManagement(TypedDict, total=False):
        key "errorResponseMessageOptions": ForwardRef('ResourceProviderManagementErrorResponseMessageOptions', module='types')
        key "expeditedRolloutMetadata": ForwardRef('ResourceProviderManagementExpeditedRolloutMetadata', module='types')
        key "incidentContactEmail": str
        key "incidentRoutingService": str
        key "incidentRoutingTeam": str
        key "pcCode": str
        key "profitCenterProgramId": str
        key "resourceAccessPolicy": Union[str, ResourceAccessPolicy]
        authorizationOwners: list[str]
        authorization_owners: list[str]
        canaryManifestOwners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expeditedRolloutSubmitters: list[str]
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifestOwners: list[str]
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resourceAccessRoles: list[ResourceAccessRole]
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schemaOwners: list[str]
        schema_owners: list[str]
        serviceTreeInfos: list[ServiceTreeInfo]
        service_tree_infos: list[ServiceTreeInfo]


    class azure.mgmt.providerhub.types.ResourceProviderManagementErrorResponseMessageOptions(TypedDict, total=False):
        key "serverFailureResponseMessageType": Union[str, ServerFailureResponseMessageType]
        server_failure_response_message_type: Union[str, ServerFailureResponseMessageType]


    class azure.mgmt.providerhub.types.ResourceProviderManagementExpeditedRolloutMetadata(TypedDict, total=False):
        key "enabled": bool
        key "expeditedRolloutIntent": Union[str, ExpeditedRolloutIntent]
        enabled: bool
        expedited_rollout_intent: Union[str, ExpeditedRolloutIntent]


    class azure.mgmt.providerhub.types.ResourceProviderManifestProperties(TypedDict, total=False):
        key "crossTenantTokenValidation": Union[str, CrossTenantTokenValidation]
        key "customManifestVersion": str
        key "dstsConfiguration": ForwardRef('ResourceProviderManifestPropertiesDstsConfiguration', module='types')
        key "enableTenantLinkedNotification": Optional[bool]
        key "featuresRule": ForwardRef('ResourceProviderManifestPropertiesFeaturesRule', module='types')
        key "legacyNamespace": str
        key "management": ForwardRef('ResourceProviderManifestPropertiesManagement', module='types')
        key "metadata": Any
        key "namespace": str
        key "notificationOptions": Union[str, NotificationOptions]
        key "notificationSettings": ForwardRef('ResourceProviderManifestPropertiesNotificationSettings', module='types')
        key "providerAuthentication": ForwardRef('ResourceProviderManifestPropertiesProviderAuthentication', module='types')
        key "providerType": Union[str, ResourceProviderType]
        key "providerVersion": str
        key "requestHeaderOptions": ForwardRef('ResourceProviderManifestPropertiesRequestHeaderOptions', module='types')
        key "resourceGroupLockOptionDuringMove": ForwardRef('ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove', module='types')
        key "resourceProviderAuthorizationRules": ForwardRef('ResourceProviderAuthorizationRules', module='types')
        key "responseOptions": ForwardRef('ResourceProviderManifestPropertiesResponseOptions', module='types')
        key "serviceName": str
        key "templateDeploymentOptions": ForwardRef('ResourceProviderManifestPropertiesTemplateDeploymentOptions', module='types')
        capabilities: list[ResourceProviderCapabilities]
        cross_tenant_token_validation: Union[str, CrossTenantTokenValidation]
        custom_manifest_version: str
        dsts_configuration: ResourceProviderManifestPropertiesDstsConfiguration
        enable_tenant_linked_notification: bool
        features_rule: ResourceProviderManifestPropertiesFeaturesRule
        globalNotificationEndpoints: list[ResourceProviderEndpoint]
        global_notification_endpoints: list[ResourceProviderEndpoint]
        legacyRegistrations: list[str]
        legacy_namespace: str
        legacy_registrations: list[str]
        linkedNotificationRules: list[FanoutLinkedNotificationRule]
        linked_notification_rules: list[FanoutLinkedNotificationRule]
        management: ResourceProviderManifestPropertiesManagement
        managementGroupGlobalNotificationEndpoints: list[ResourceProviderEndpoint]
        management_group_global_notification_endpoints: list[ResourceProviderEndpoint]
        metadata: Any
        namespace: str
        notification_options: Union[str, NotificationOptions]
        notification_settings: ResourceProviderManifestPropertiesNotificationSettings
        notifications: list[Notification]
        optionalFeatures: list[str]
        optional_features: list[str]
        providerAuthorizations: list[ResourceProviderAuthorization]
        provider_authentication: ResourceProviderManifestPropertiesProviderAuthentication
        provider_authorizations: list[ResourceProviderAuthorization]
        provider_type: Union[str, ResourceProviderType]
        provider_version: str
        request_header_options: ResourceProviderManifestPropertiesRequestHeaderOptions
        requiredFeatures: list[str]
        required_features: list[str]
        resourceHydrationAccounts: list[ResourceHydrationAccount]
        resource_group_lock_option_during_move: ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove
        resource_hydration_accounts: list[ResourceHydrationAccount]
        resource_provider_authorization_rules: ResourceProviderAuthorizationRules
        response_options: ResourceProviderManifestPropertiesResponseOptions
        service_name: str
        services: list[ResourceProviderService]
        template_deployment_options: ResourceProviderManifestPropertiesTemplateDeploymentOptions


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesDstsConfiguration(DstsConfiguration):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesFeaturesRule(FeaturesRule):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesManagement(ResourceProviderManagement):
        key "errorResponseMessageOptions": ForwardRef('ResourceProviderManagementErrorResponseMessageOptions', module='types')
        key "expeditedRolloutMetadata": ForwardRef('ResourceProviderManagementExpeditedRolloutMetadata', module='types')
        key "incidentContactEmail": str
        key "incidentRoutingService": str
        key "incidentRoutingTeam": str
        key "pcCode": str
        key "profitCenterProgramId": str
        key "resourceAccessPolicy": Union[str, ResourceAccessPolicy]
        authorizationOwners: list[str]
        authorization_owners: list[str]
        canaryManifestOwners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expeditedRolloutSubmitters: list[str]
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifestOwners: list[str]
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resourceAccessRoles: list[ResourceAccessRole]
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schemaOwners: list[str]
        schema_owners: list[str]
        serviceTreeInfos: list[ServiceTreeInfo]
        service_tree_infos: list[ServiceTreeInfo]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesNotificationSettings(TypedDict, total=False):
        subscriberSettings: list[SubscriberSetting]
        subscriber_settings: list[SubscriberSetting]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesProviderAuthentication(ResourceProviderAuthentication):
        key "allowedAudiences": Required[list[str]]
        allowed_audiences: list[str]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesRequestHeaderOptions(RequestHeaderOptions):
        key "optInHeaders": Union[str, OptInHeaderType]
        key "optOutHeaders": Union[str, OptOutHeaderType]
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesResourceGroupLockOptionDuringMove(TypedDict, total=False):
        key "blockActionVerb": Union[str, BlockActionVerb]
        block_action_verb: Union[str, BlockActionVerb]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesResponseOptions(TypedDict, total=False):
        key "serviceClientOptionsType": Union[str, ServiceClientOptionsType]
        service_client_options_type: Union[str, ServiceClientOptionsType]


    class azure.mgmt.providerhub.types.ResourceProviderManifestPropertiesTemplateDeploymentOptions(TemplateDeploymentOptions):
        key "preflightSupported": bool
        preflightOptions: list[Union[str, PreflightOption]]
        preflight_options: list[Union[str, PreflightOption]]
        preflight_supported: bool


    class azure.mgmt.providerhub.types.ResourceProviderService(TypedDict, total=False):
        key "serviceName": str
        key "status": Union[str, ServiceStatus]
        service_name: str
        status: Union[str, ServiceStatus]


    class azure.mgmt.providerhub.types.ResourceTypeEndpoint(TypedDict, total=False):
        key "apiVersion": str
        key "dataBoundary": Union[str, DataBoundary]
        key "dstsConfiguration": ForwardRef('ResourceTypeEndpointDstsConfiguration', module='types')
        key "enabled": bool
        key "endpointType": Union[str, EndpointTypeResourceType]
        key "endpointUri": str
        key "featuresRule": ForwardRef('ResourceTypeEndpointFeaturesRule', module='types')
        key "kind": Union[str, ResourceTypeEndpointKind]
        key "skuLink": str
        key "timeout": str
        key "tokenAuthConfiguration": ForwardRef('TokenAuthConfiguration', module='types')
        apiVersions: list[str]
        api_version: str
        api_versions: list[str]
        data_boundary: Union[str, DataBoundary]
        dsts_configuration: ResourceTypeEndpointDstsConfiguration
        enabled: bool
        endpoint_type: Union[str, EndpointTypeResourceType]
        endpoint_uri: str
        extensions: list[ResourceTypeExtension]
        features_rule: ResourceTypeEndpointFeaturesRule
        kind: Union[str, ResourceTypeEndpointKind]
        locations: list[str]
        requiredFeatures: list[str]
        required_features: list[str]
        sku_link: str
        timeout: str
        token_auth_configuration: TokenAuthConfiguration
        zones: list[str]


    class azure.mgmt.providerhub.types.ResourceTypeEndpointBase(TypedDict, total=False):
        key "apiVersion": Required[str]
        key "apiVersions": Required[list[str]]
        key "dstsConfiguration": Required[ResourceTypeEndpointBaseDstsConfiguration]
        key "enabled": Required[bool]
        key "endpointType": Required[Union[str, EndpointType]]
        key "endpointUri": Required[str]
        key "featuresRule": Required[ResourceTypeEndpointBaseFeaturesRule]
        key "locations": Required[list[str]]
        key "requiredFeatures": Required[list[str]]
        key "skuLink": Required[str]
        key "timeout": Required[str]
        key "zones": Required[list[str]]
        api_version: str
        api_versions: list[str]
        dsts_configuration: ResourceTypeEndpointBaseDstsConfiguration
        enabled: bool
        endpoint_type: Union[str, EndpointType]
        endpoint_uri: str
        features_rule: ResourceTypeEndpointBaseFeaturesRule
        locations: list[str]
        required_features: list[str]
        sku_link: str
        timeout: str
        zones: list[str]


    class azure.mgmt.providerhub.types.ResourceTypeEndpointBaseDstsConfiguration(DstsConfiguration):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.ResourceTypeEndpointBaseFeaturesRule(FeaturesRule):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.ResourceTypeEndpointDstsConfiguration(DstsConfiguration):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.ResourceTypeEndpointFeaturesRule(FeaturesRule):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.ResourceTypeExtension(TypedDict, total=False):
        key "endpointUri": str
        key "timeout": str
        endpoint_uri: str
        extensionCategories: list[Union[str, ExtensionCategory]]
        extension_categories: list[Union[str, ExtensionCategory]]
        timeout: str


    class azure.mgmt.providerhub.types.ResourceTypeExtensionOptions(TypedDict, total=False):
        key "resourceCreationBegin": ForwardRef('ResourceTypeExtensionOptionsResourceCreationBegin', module='types')
        resource_creation_begin: ResourceTypeExtensionOptionsResourceCreationBegin


    class azure.mgmt.providerhub.types.ResourceTypeExtensionOptionsResourceCreationBegin(ExtensionOptions):
        request: list[Union[str, ExtensionOptionType]]
        response: list[Union[str, ExtensionOptionType]]


    class azure.mgmt.providerhub.types.ResourceTypeOnBehalfOfToken(TypedDict, total=False):
        key "actionName": str
        key "lifeTime": str
        action_name: str
        life_time: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistration(ProxyResource):
        key "id": str
        key "kind": Union[str, ResourceTypeRegistrationKind]
        key "name": str
        key "properties": ForwardRef('ResourceTypeRegistrationProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        kind: Union[str, ResourceTypeRegistrationKind]
        name: str
        properties: ResourceTypeRegistrationProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationProperties(TypedDict, total=False):
        key "addResourceListTargetLocations": bool
        key "additionalOptions": Union[str, AdditionalOptionsResourceTypeRegistration]
        key "allowEmptyRoleAssignments": bool
        key "asyncOperationResourceTypeName": str
        key "availabilityZoneRule": ForwardRef('ResourceTypeRegistrationPropertiesAvailabilityZoneRule', module='types')
        key "capacityRule": ForwardRef('ResourceTypeRegistrationPropertiesCapacityRule', module='types')
        key "category": Union[str, ResourceTypeCategory]
        key "checkNameAvailabilitySpecifications": ForwardRef('ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications', module='types')
        key "crossTenantTokenValidation": Union[str, CrossTenantTokenValidation]
        key "defaultApiVersion": str
        key "dstsConfiguration": ForwardRef('ResourceTypeRegistrationPropertiesDstsConfiguration', module='types')
        key "enableAsyncOperation": bool
        key "enableThirdPartyS2S": bool
        key "extensionOptions": ForwardRef('ResourceTypeRegistrationPropertiesExtensionOptions', module='types')
        key "featuresRule": ForwardRef('ResourceTypeRegistrationPropertiesFeaturesRule', module='types')
        key "frontdoorRequestMode": Union[str, FrontdoorRequestMode]
        key "groupingTag": str
        key "identityManagement": ForwardRef('ResourceTypeRegistrationPropertiesIdentityManagement', module='types')
        key "isPureProxy": bool
        key "legacyName": str
        key "legacyPolicy": ForwardRef('ResourceTypeRegistrationPropertiesLegacyPolicy', module='types')
        key "management": ForwardRef('ResourceTypeRegistrationPropertiesManagement', module='types')
        key "manifestLink": str
        key "marketplaceOptions": ForwardRef('ResourceTypeRegistrationPropertiesMarketplaceOptions', module='types')
        key "marketplaceType": Union[str, MarketplaceType]
        key "onBehalfOfTokens": ForwardRef('ResourceTypeOnBehalfOfToken', module='types')
        key "openApiConfiguration": ForwardRef('OpenApiConfiguration', module='types')
        key "policyExecutionType": Union[str, PolicyExecutionType]
        key "provisioningState": Union[str, ProvisioningState]
        key "quotaRule": ForwardRef('QuotaRule', module='types')
        key "regionality": Union[str, Regionality]
        key "requestHeaderOptions": ForwardRef('ResourceTypeRegistrationPropertiesRequestHeaderOptions', module='types')
        key "resourceCache": ForwardRef('ResourceTypeRegistrationPropertiesResourceCache', module='types')
        key "resourceDeletionPolicy": Union[str, ResourceDeletionPolicy]
        key "resourceGraphConfiguration": ForwardRef('ResourceTypeRegistrationPropertiesResourceGraphConfiguration', module='types')
        key "resourceManagementOptions": ForwardRef('ResourceTypeRegistrationPropertiesResourceManagementOptions', module='types')
        key "resourceMovePolicy": ForwardRef('ResourceTypeRegistrationPropertiesResourceMovePolicy', module='types')
        key "resourceProviderAuthorizationRules": ForwardRef('ResourceProviderAuthorizationRules', module='types')
        key "resourceQueryManagement": ForwardRef('ResourceTypeRegistrationPropertiesResourceQueryManagement', module='types')
        key "resourceSubType": Union[str, ResourceSubType]
        key "resourceTypeCommonAttributeManagement": ForwardRef('ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement', module='types')
        key "resourceValidation": Union[str, ResourceValidation]
        key "routingRule": ForwardRef('ResourceTypeRegistrationPropertiesRoutingRule', module='types')
        key "routingType": Union[str, RoutingType]
        key "skuLink": str
        key "subscriptionLifecycleNotificationSpecifications": ForwardRef('ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications', module='types')
        key "supportsTags": bool
        key "templateDeploymentOptions": ForwardRef('ResourceTypeRegistrationPropertiesTemplateDeploymentOptions', module='types')
        key "templateDeploymentPolicy": ForwardRef('ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy', module='types')
        key "tokenAuthConfiguration": ForwardRef('TokenAuthConfiguration', module='types')
        add_resource_list_target_locations: bool
        additional_options: Union[str, AdditionalOptionsResourceTypeRegistration]
        allow_empty_role_assignments: bool
        allowedResourceNames: list[AllowedResourceName]
        allowedTemplateDeploymentReferenceActions: list[str]
        allowedUnauthorizedActions: list[str]
        allowedUnauthorizedActionsExtensions: list[AllowedUnauthorizedActionsExtension]
        allowed_resource_names: list[AllowedResourceName]
        allowed_template_deployment_reference_actions: list[str]
        allowed_unauthorized_actions: list[str]
        allowed_unauthorized_actions_extensions: list[AllowedUnauthorizedActionsExtension]
        apiProfiles: list[ApiProfile]
        api_profiles: list[ApiProfile]
        asyncTimeoutRules: list[AsyncTimeoutRule]
        async_operation_resource_type_name: str
        async_timeout_rules: list[AsyncTimeoutRule]
        authorizationActionMappings: list[AuthorizationActionMapping]
        authorization_action_mappings: list[AuthorizationActionMapping]
        availability_zone_rule: ResourceTypeRegistrationPropertiesAvailabilityZoneRule
        capacity_rule: ResourceTypeRegistrationPropertiesCapacityRule
        category: Union[str, ResourceTypeCategory]
        check_name_availability_specifications: ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications
        commonApiVersions: list[str]
        common_api_versions: list[str]
        cross_tenant_token_validation: Union[str, CrossTenantTokenValidation]
        default_api_version: str
        disallowedActionVerbs: list[str]
        disallowedEndUserOperations: list[str]
        disallowed_action_verbs: list[str]
        disallowed_end_user_operations: list[str]
        dsts_configuration: ResourceTypeRegistrationPropertiesDstsConfiguration
        enable_async_operation: bool
        enable_third_party_s2_s: bool
        endpoints: list[ResourceTypeEndpoint]
        extendedLocations: list[ExtendedLocationOptions]
        extended_locations: list[ExtendedLocationOptions]
        extension_options: ResourceTypeRegistrationPropertiesExtensionOptions
        features_rule: ResourceTypeRegistrationPropertiesFeaturesRule
        frontdoor_request_mode: Union[str, FrontdoorRequestMode]
        grouping_tag: str
        identity_management: ResourceTypeRegistrationPropertiesIdentityManagement
        is_pure_proxy: bool
        legacyNames: list[str]
        legacy_name: str
        legacy_names: list[str]
        legacy_policy: ResourceTypeRegistrationPropertiesLegacyPolicy
        linkedAccessChecks: list[LinkedAccessCheck]
        linkedNotificationRules: list[LinkedNotificationRule]
        linkedOperationRules: list[LinkedOperationRule]
        linked_access_checks: list[LinkedAccessCheck]
        linked_notification_rules: list[LinkedNotificationRule]
        linked_operation_rules: list[LinkedOperationRule]
        loggingRules: list[LoggingRule]
        logging_rules: list[LoggingRule]
        management: ResourceTypeRegistrationPropertiesManagement
        manifest_link: str
        marketplace_options: ResourceTypeRegistrationPropertiesMarketplaceOptions
        marketplace_type: Union[str, MarketplaceType]
        metadata: dict[str, Any]
        notifications: list[Notification]
        on_behalf_of_tokens: ResourceTypeOnBehalfOfToken
        open_api_configuration: OpenApiConfiguration
        policy_execution_type: Union[str, PolicyExecutionType]
        provisioning_state: Union[str, ProvisioningState]
        quota_rule: QuotaRule
        regionality: Union[str, Regionality]
        request_header_options: ResourceTypeRegistrationPropertiesRequestHeaderOptions
        requiredFeatures: list[str]
        required_features: list[str]
        resourceConcurrencyControlOptions: dict[str, ResourceConcurrencyControlOption]
        resource_cache: ResourceTypeRegistrationPropertiesResourceCache
        resource_concurrency_control_options: dict[str, ResourceConcurrencyControlOption]
        resource_deletion_policy: Union[str, ResourceDeletionPolicy]
        resource_graph_configuration: ResourceTypeRegistrationPropertiesResourceGraphConfiguration
        resource_management_options: ResourceTypeRegistrationPropertiesResourceManagementOptions
        resource_move_policy: ResourceTypeRegistrationPropertiesResourceMovePolicy
        resource_provider_authorization_rules: ResourceProviderAuthorizationRules
        resource_query_management: ResourceTypeRegistrationPropertiesResourceQueryManagement
        resource_sub_type: Union[str, ResourceSubType]
        resource_type_common_attribute_management: ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement
        resource_validation: Union[str, ResourceValidation]
        routing_rule: ResourceTypeRegistrationPropertiesRoutingRule
        routing_type: Union[str, RoutingType]
        serviceTreeInfos: list[ServiceTreeInfo]
        service_tree_infos: list[ServiceTreeInfo]
        sku_link: str
        subscriptionStateRules: list[SubscriptionStateRule]
        subscription_lifecycle_notification_specifications: ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications
        subscription_state_rules: list[SubscriptionStateRule]
        supports_tags: bool
        swaggerSpecifications: list[SwaggerSpecification]
        swagger_specifications: list[SwaggerSpecification]
        template_deployment_options: ResourceTypeRegistrationPropertiesTemplateDeploymentOptions
        template_deployment_policy: ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy
        throttlingRules: list[ThrottlingRule]
        throttling_rules: list[ThrottlingRule]
        token_auth_configuration: TokenAuthConfiguration


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesAvailabilityZoneRule(TypedDict, total=False):
        key "availabilityZonePolicy": Union[str, AvailabilityZonePolicy]
        availability_zone_policy: Union[str, AvailabilityZonePolicy]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesCapacityRule(TypedDict, total=False):
        key "capacityPolicy": Union[str, CapacityPolicy]
        key "skuAlias": str
        capacity_policy: Union[str, CapacityPolicy]
        sku_alias: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesCheckNameAvailabilitySpecifications(CheckNameAvailabilitySpecifications):
        key "enableDefaultValidation": bool
        enable_default_validation: bool
        resourceTypesWithCustomValidation: list[str]
        resource_types_with_custom_validation: list[str]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesDstsConfiguration(DstsConfiguration):
        key "serviceDnsName": str
        key "serviceName": Required[str]
        service_dns_name: str
        service_name: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesExtensionOptions(ResourceTypeExtensionOptions):
        key "resourceCreationBegin": ForwardRef('ResourceTypeExtensionOptionsResourceCreationBegin', module='types')
        resource_creation_begin: ResourceTypeExtensionOptionsResourceCreationBegin


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesFeaturesRule(FeaturesRule):
        key "requiredFeaturesPolicy": Required[Union[str, FeaturesPolicy]]
        required_features_policy: Union[str, FeaturesPolicy]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesIdentityManagement(IdentityManagementProperties):
        key "applicationId": str
        key "type": Union[str, IdentityManagementTypes]
        applicationIds: list[str]
        application_id: str
        application_ids: list[str]
        delegationAppIds: list[str]
        delegation_app_ids: list[str]
        type: Union[str, IdentityManagementTypes]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesLegacyPolicy(TypedDict, total=False):
        disallowedConditions: list[LegacyDisallowedCondition]
        disallowedLegacyOperations: list[Union[str, LegacyOperation]]
        disallowed_conditions: list[LegacyDisallowedCondition]
        disallowed_legacy_operations: list[Union[str, LegacyOperation]]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesManagement(ResourceProviderManagement):
        key "errorResponseMessageOptions": ForwardRef('ResourceProviderManagementErrorResponseMessageOptions', module='types')
        key "expeditedRolloutMetadata": ForwardRef('ResourceProviderManagementExpeditedRolloutMetadata', module='types')
        key "incidentContactEmail": str
        key "incidentRoutingService": str
        key "incidentRoutingTeam": str
        key "pcCode": str
        key "profitCenterProgramId": str
        key "resourceAccessPolicy": Union[str, ResourceAccessPolicy]
        authorizationOwners: list[str]
        authorization_owners: list[str]
        canaryManifestOwners: list[str]
        canary_manifest_owners: list[str]
        error_response_message_options: ResourceProviderManagementErrorResponseMessageOptions
        expeditedRolloutSubmitters: list[str]
        expedited_rollout_metadata: ResourceProviderManagementExpeditedRolloutMetadata
        expedited_rollout_submitters: list[str]
        incident_contact_email: str
        incident_routing_service: str
        incident_routing_team: str
        manifestOwners: list[str]
        manifest_owners: list[str]
        pc_code: str
        profit_center_program_id: str
        resourceAccessRoles: list[ResourceAccessRole]
        resource_access_policy: Union[str, ResourceAccessPolicy]
        resource_access_roles: list[ResourceAccessRole]
        schemaOwners: list[str]
        schema_owners: list[str]
        serviceTreeInfos: list[ServiceTreeInfo]
        service_tree_infos: list[ServiceTreeInfo]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesMarketplaceOptions(TypedDict, total=False):
        key "addOnPlanConversionAllowed": bool
        add_on_plan_conversion_allowed: bool


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesRequestHeaderOptions(RequestHeaderOptions):
        key "optInHeaders": Union[str, OptInHeaderType]
        key "optOutHeaders": Union[str, OptOutHeaderType]
        opt_in_headers: Union[str, OptInHeaderType]
        opt_out_headers: Union[str, OptOutHeaderType]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceCache(TypedDict, total=False):
        key "enableResourceCache": bool
        key "resourceCacheExpirationTimespan": str
        enable_resource_cache: bool
        resource_cache_expiration_timespan: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceGraphConfiguration(ResourceGraphConfiguration):
        key "apiVersion": str
        key "enabled": bool
        api_version: str
        enabled: bool


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceManagementOptions(TypedDict, total=False):
        key "batchProvisioningSupport": ForwardRef('ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport', module='types')
        key "nestedProvisioningSupport": ForwardRef('ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport', module='types')
        batch_provisioning_support: ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport
        deleteDependencies: list[DeleteDependency]
        delete_dependencies: list[DeleteDependency]
        nested_provisioning_support: ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceManagementOptionsBatchProvisioningSupport(TypedDict, total=False):
        key "supportedOperations": Union[str, SupportedOperations]
        supported_operations: Union[str, SupportedOperations]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceManagementOptionsNestedProvisioningSupport(TypedDict, total=False):
        key "minimumApiVersion": str
        minimum_api_version: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceMovePolicy(ResourceMovePolicy):
        key "crossResourceGroupMoveEnabled": bool
        key "crossSubscriptionMoveEnabled": bool
        key "validationRequired": bool
        cross_resource_group_move_enabled: bool
        cross_subscription_move_enabled: bool
        validation_required: bool


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceQueryManagement(TypedDict, total=False):
        key "filterOption": Union[str, FilterOption]
        filter_option: Union[str, FilterOption]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesResourceTypeCommonAttributeManagement(TypedDict, total=False):
        key "commonApiVersionsMergeMode": Union[str, CommonApiVersionsMergeMode]
        common_api_versions_merge_mode: Union[str, CommonApiVersionsMergeMode]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesRoutingRule(TypedDict, total=False):
        key "hostResourceType": str
        host_resource_type: str


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesSubscriptionLifecycleNotificationSpecifications(SubscriptionLifecycleNotificationSpecifications):
        key "softDeleteTTL": str
        soft_delete_ttl: str
        subscriptionStateOverrideActions: list[SubscriptionStateOverrideAction]
        subscription_state_override_actions: list[SubscriptionStateOverrideAction]


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesTemplateDeploymentOptions(TemplateDeploymentOptions):
        key "preflightSupported": bool
        preflightOptions: list[Union[str, PreflightOption]]
        preflight_options: list[Union[str, PreflightOption]]
        preflight_supported: bool


    class azure.mgmt.providerhub.types.ResourceTypeRegistrationPropertiesTemplateDeploymentPolicy(TemplateDeploymentPolicy):
        key "capabilities": Required[Union[str, TemplateDeploymentCapabilities]]
        key "preflightNotifications": Union[str, TemplateDeploymentPreflightNotifications]
        key "preflightOptions": Required[Union[str, TemplateDeploymentPreflightOptions]]
        capabilities: Union[str, TemplateDeploymentCapabilities]
        preflight_notifications: Union[str, TemplateDeploymentPreflightNotifications]
        preflight_options: Union[str, TemplateDeploymentPreflightOptions]


    class azure.mgmt.providerhub.types.ResourceTypeSku(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        key "skuSettings": Required[list[SkuSetting]]
        provisioning_state: Union[str, ProvisioningState]
        sku_settings: list[SkuSetting]


    class azure.mgmt.providerhub.types.RolloutStatusBase(TypedDict, total=False):
        completedRegions: list[str]
        completed_regions: list[str]
        failedOrSkippedRegions: dict[str, ExtendedErrorInfo]
        failed_or_skipped_regions: dict[str, ExtendedErrorInfo]


    class azure.mgmt.providerhub.types.ServiceTreeInfo(TypedDict, total=False):
        key "componentId": str
        key "readiness": Union[str, Readiness]
        key "serviceId": str
        component_id: str
        readiness: Union[str, Readiness]
        service_id: str


    class azure.mgmt.providerhub.types.SkuCapability(TypedDict, total=False):
        key "name": Required[str]
        key "value": Required[str]
        name: str
        value: str


    class azure.mgmt.providerhub.types.SkuCapacity(TypedDict, total=False):
        key "default": int
        key "maximum": int
        key "minimum": Required[int]
        key "scaleType": Union[str, SkuScaleType]
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, SkuScaleType]


    class azure.mgmt.providerhub.types.SkuCost(TypedDict, total=False):
        key "extendedUnit": str
        key "meterId": Required[str]
        key "quantity": int
        extended_unit: str
        meter_id: str
        quantity: int


    class azure.mgmt.providerhub.types.SkuLocationInfo(TypedDict, total=False):
        key "location": Required[str]
        key "type": Union[str, ExtendedLocationType]
        extendedLocations: list[str]
        extended_locations: list[str]
        location: str
        type: Union[str, ExtendedLocationType]
        zoneDetails: list[SkuZoneDetail]
        zone_details: list[SkuZoneDetail]
        zones: list[str]


    class azure.mgmt.providerhub.types.SkuResource(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SkuResourceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SkuResourceProperties
        system_data: SystemData
        type: str


    class azure.mgmt.providerhub.types.SkuResourceProperties(ResourceTypeSku):
        key "provisioningState": Union[str, ProvisioningState]
        key "skuSettings": Required[list[SkuSetting]]
        provisioning_state: Union[str, ProvisioningState]
        sku_settings: list[SkuSetting]


    class azure.mgmt.providerhub.types.SkuSetting(TypedDict, total=False):
        key "capacity": ForwardRef('SkuSettingCapacity', module='types')
        key "family": str
        key "kind": str
        key "name": Required[str]
        key "size": str
        key "tier": str
        capabilities: list[SkuCapability]
        capacity: SkuSettingCapacity
        costs: list[SkuCost]
        family: str
        kind: str
        locationInfo: list[SkuLocationInfo]
        location_info: list[SkuLocationInfo]
        locations: list[str]
        name: str
        requiredFeatures: list[str]
        requiredQuotaIds: list[str]
        required_features: list[str]
        required_quota_ids: list[str]
        size: str
        tier: str


    class azure.mgmt.providerhub.types.SkuSettingCapacity(SkuCapacity):
        key "default": int
        key "maximum": int
        key "minimum": Required[int]
        key "scaleType": Union[str, SkuScaleType]
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, SkuScaleType]


    class azure.mgmt.providerhub.types.SkuZoneDetail(TypedDict, total=False):
        capabilities: list[SkuCapability]
        name: list[str]


    class azure.mgmt.providerhub.types.SubscriberSetting(TypedDict, total=False):
        filterRules: list[FilterRule]
        filter_rules: list[FilterRule]


    class azure.mgmt.providerhub.types.SubscriptionLifecycleNotificationSpecifications(TypedDict, total=False):
        key "softDeleteTTL": str
        soft_delete_ttl: str
        subscriptionStateOverrideActions: list[SubscriptionStateOverrideAction]
        subscription_state_override_actions: list[SubscriptionStateOverrideAction]


    class azure.mgmt.providerhub.types.SubscriptionStateOverrideAction(TypedDict, total=False):
        key "action": Required[Union[str, SubscriptionNotificationOperation]]
        key "state": Required[Union[str, SubscriptionTransitioningState]]
        action: Union[str, SubscriptionNotificationOperation]
        state: Union[str, SubscriptionTransitioningState]


    class azure.mgmt.providerhub.types.SubscriptionStateRule(TypedDict, total=False):
        key "state": Union[str, SubscriptionState]
        allowedActions: list[str]
        allowed_actions: list[str]
        state: Union[str, SubscriptionState]


    class azure.mgmt.providerhub.types.SwaggerSpecification(TypedDict, total=False):
        key "swaggerSpecFolderUri": str
        apiVersions: list[str]
        api_versions: list[str]
        swagger_spec_folder_uri: str


    class azure.mgmt.providerhub.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.providerhub.types.TemplateDeploymentOptions(TypedDict, total=False):
        key "preflightSupported": bool
        preflightOptions: list[Union[str, PreflightOption]]
        preflight_options: list[Union[str, PreflightOption]]
        preflight_supported: bool


    class azure.mgmt.providerhub.types.TemplateDeploymentPolicy(TypedDict, total=False):
        key "capabilities": Required[Union[str, TemplateDeploymentCapabilities]]
        key "preflightNotifications": Union[str, TemplateDeploymentPreflightNotifications]
        key "preflightOptions": Required[Union[str, TemplateDeploymentPreflightOptions]]
        capabilities: Union[str, TemplateDeploymentCapabilities]
        preflight_notifications: Union[str, TemplateDeploymentPreflightNotifications]
        preflight_options: Union[str, TemplateDeploymentPreflightOptions]


    class azure.mgmt.providerhub.types.ThirdPartyExtension(TypedDict, total=False):
        key "name": str
        name: str


    class azure.mgmt.providerhub.types.ThirdPartyProviderAuthorization(TypedDict, total=False):
        key "managedByTenantId": str
        authorizations: list[LightHouseAuthorization]
        managed_by_tenant_id: str


    class azure.mgmt.providerhub.types.ThrottlingMetric(TypedDict, total=False):
        key "interval": str
        key "limit": Required[int]
        key "type": Required[Union[str, ThrottlingMetricType]]
        interval: str
        limit: int
        type: Union[str, ThrottlingMetricType]


    class azure.mgmt.providerhub.types.ThrottlingRule(TypedDict, total=False):
        key "action": Required[str]
        key "metrics": Required[list[ThrottlingMetric]]
        action: str
        applicationId: list[str]
        application_id: list[str]
        metrics: list[ThrottlingMetric]
        requiredFeatures: list[str]
        required_features: list[str]


    class azure.mgmt.providerhub.types.TokenAuthConfiguration(TypedDict, total=False):
        key "authenticationScheme": Union[str, AuthenticationScheme]
        key "disableCertificateAuthenticationFallback": bool
        key "signedRequestScope": Union[str, SignedRequestScope]
        authentication_scheme: Union[str, AuthenticationScheme]
        disable_certificate_authentication_fallback: bool
        signed_request_scope: Union[str, SignedRequestScope]


    class azure.mgmt.providerhub.types.TrackedResource(Resource):
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


    class azure.mgmt.providerhub.types.TrafficRegionRolloutConfiguration(TrafficRegions):
        key "waitDuration": str
        regions: list[str]
        wait_duration: str


    class azure.mgmt.providerhub.types.TrafficRegions(TypedDict, total=False):
        regions: list[str]


    class azure.mgmt.providerhub.types.TypedErrorInfo(TypedDict, total=False):
        key "info": Any
        key "type": Required[str]
        info: Any
        type: str


```