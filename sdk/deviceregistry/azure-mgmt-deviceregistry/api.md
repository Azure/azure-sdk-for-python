```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.deviceregistry

    class azure.mgmt.deviceregistry.DeviceRegistryMgmtClient: implements ContextManager 
        asset_endpoint_profiles: AssetEndpointProfilesOperations
        assets: AssetsOperations
        billing_containers: BillingContainersOperations
        credentials: CredentialsOperations
        namespace_assets: NamespaceAssetsOperations
        namespace_devices: NamespaceDevicesOperations
        namespace_discovered_assets: NamespaceDiscoveredAssetsOperations
        namespace_discovered_devices: NamespaceDiscoveredDevicesOperations
        namespaces: NamespacesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        policies: PoliciesOperations
        schema_registries: SchemaRegistriesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations

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


namespace azure.mgmt.deviceregistry.aio

    class azure.mgmt.deviceregistry.aio.DeviceRegistryMgmtClient: implements AsyncContextManager 
        asset_endpoint_profiles: AssetEndpointProfilesOperations
        assets: AssetsOperations
        billing_containers: BillingContainersOperations
        credentials: CredentialsOperations
        namespace_assets: NamespaceAssetsOperations
        namespace_devices: NamespaceDevicesOperations
        namespace_discovered_assets: NamespaceDiscoveredAssetsOperations
        namespace_discovered_devices: NamespaceDiscoveredDevicesOperations
        namespaces: NamespacesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        policies: PoliciesOperations
        schema_registries: SchemaRegistriesOperations
        schema_versions: SchemaVersionsOperations
        schemas: SchemasOperations

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


namespace azure.mgmt.deviceregistry.aio.operations

    class azure.mgmt.deviceregistry.aio.operations.AssetEndpointProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: AssetEndpointProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: AssetEndpointProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AssetEndpointProfile]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                **kwargs: Any
            ) -> AssetEndpointProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AssetEndpointProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AssetEndpointProfile]: ...


    class azure.mgmt.deviceregistry.aio.operations.AssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: Asset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: AssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Asset]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> Asset: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Asset]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Asset]: ...


    class azure.mgmt.deviceregistry.aio.operations.BillingContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'billing_container_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                billing_container_name: str, 
                **kwargs: Any
            ) -> BillingContainer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[BillingContainer]: ...


    class azure.mgmt.deviceregistry.aio.operations.CredentialsOperations:

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
                resource: Credential, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        async def begin_synchronize(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: CredentialUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Credential]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Credential]: ...


    class azure.mgmt.deviceregistry.aio.operations.NamespaceAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: NamespaceAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: NamespaceAssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> NamespaceAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceAsset]: ...


    class azure.mgmt.deviceregistry.aio.operations.NamespaceDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: NamespaceDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: DeviceCredentialsRevokeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: NamespaceDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> NamespaceDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceDevice]: ...


    class azure.mgmt.deviceregistry.aio.operations.NamespaceDiscoveredAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: NamespaceDiscoveredAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: NamespaceDiscoveredAssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceDiscoveredAsset]: ...


    class azure.mgmt.deviceregistry.aio.operations.NamespaceDiscoveredDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: NamespaceDiscoveredDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: NamespaceDiscoveredDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[NamespaceDiscoveredDevice]: ...


    class azure.mgmt.deviceregistry.aio.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: NamespaceMigrateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: NamespaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[Namespace]: ...


    class azure.mgmt.deviceregistry.aio.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.deviceregistry.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.deviceregistry.aio.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: ActivateBringYourOwnRootRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: Policy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name']}, api_versions_list=['2026-03-01-preview'])
        async def begin_revoke_issuer(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: PolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Policy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Policy]: ...


    class azure.mgmt.deviceregistry.aio.operations.SchemaRegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: SchemaRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: SchemaRegistryUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> SchemaRegistry: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SchemaRegistry]: ...


    class azure.mgmt.deviceregistry.aio.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaVersion]: ...


    class azure.mgmt.deviceregistry.aio.operations.SchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        async def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_schema_registry(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Schema]: ...


namespace azure.mgmt.deviceregistry.models

    class azure.mgmt.deviceregistry.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.deviceregistry.models.ActivateBringYourOwnRootRequest(_Model):
        certificate_chain: str

        @overload
        def __init__(
                self, 
                *, 
                certificate_chain: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Asset(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[AssetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[AssetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetEndpointProfile(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[AssetEndpointProfileProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[AssetEndpointProfileProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetEndpointProfileProperties(_Model):
        additional_configuration: Optional[str]
        authentication: Optional[Authentication]
        discovered_asset_endpoint_profile_ref: Optional[str]
        endpoint_profile_type: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[AssetEndpointProfileStatus]
        target_address: str
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[str] = ..., 
                authentication: Optional[Authentication] = ..., 
                discovered_asset_endpoint_profile_ref: Optional[str] = ..., 
                endpoint_profile_type: str, 
                target_address: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetEndpointProfileStatus(_Model):
        errors: Optional[list[AssetEndpointProfileStatusError]]


    class azure.mgmt.deviceregistry.models.AssetEndpointProfileStatusError(_Model):
        code: Optional[int]
        message: Optional[str]


    class azure.mgmt.deviceregistry.models.AssetEndpointProfileUpdate(_Model):
        properties: Optional[AssetEndpointProfileUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssetEndpointProfileUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetEndpointProfileUpdateProperties(_Model):
        additional_configuration: Optional[str]
        authentication: Optional[Authentication]
        endpoint_profile_type: Optional[str]
        target_address: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[str] = ..., 
                authentication: Optional[Authentication] = ..., 
                endpoint_profile_type: Optional[str] = ..., 
                target_address: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetProperties(_Model):
        asset_endpoint_profile_ref: str
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[Dataset]]
        default_datasets_configuration: Optional[str]
        default_events_configuration: Optional[str]
        default_topic: Optional[Topic]
        description: Optional[str]
        discovered_asset_refs: Optional[list[str]]
        display_name: Optional[str]
        documentation_uri: Optional[str]
        enabled: Optional[bool]
        events: Optional[list[Event]]
        external_asset_id: Optional[str]
        hardware_revision: Optional[str]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]
        software_revision: Optional[str]
        status: Optional[AssetStatus]
        uuid: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asset_endpoint_profile_ref: str, 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[Dataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_topic: Optional[Topic] = ..., 
                description: Optional[str] = ..., 
                discovered_asset_refs: Optional[list[str]] = ..., 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                events: Optional[list[Event]] = ..., 
                external_asset_id: Optional[str] = ..., 
                hardware_revision: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetStatus(_Model):
        datasets: Optional[list[AssetStatusDataset]]
        errors: Optional[list[AssetStatusError]]
        events: Optional[list[AssetStatusEvent]]
        version: Optional[int]


    class azure.mgmt.deviceregistry.models.AssetStatusDataset(_Model):
        message_schema_reference: Optional[MessageSchemaReference]
        name: str


    class azure.mgmt.deviceregistry.models.AssetStatusError(_Model):
        code: Optional[int]
        message: Optional[str]


    class azure.mgmt.deviceregistry.models.AssetStatusEvent(_Model):
        message_schema_reference: Optional[MessageSchemaReference]
        name: str


    class azure.mgmt.deviceregistry.models.AssetUpdate(_Model):
        properties: Optional[AssetUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AssetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AssetUpdateProperties(_Model):
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[Dataset]]
        default_datasets_configuration: Optional[str]
        default_events_configuration: Optional[str]
        default_topic: Optional[Topic]
        description: Optional[str]
        display_name: Optional[str]
        documentation_uri: Optional[str]
        enabled: Optional[bool]
        events: Optional[list[Event]]
        hardware_revision: Optional[str]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        serial_number: Optional[str]
        software_revision: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[Dataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_topic: Optional[Topic] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                events: Optional[list[Event]] = ..., 
                hardware_revision: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Authentication(_Model):
        method: Union[str, AuthenticationMethod]
        username_password_credentials: Optional[UsernamePasswordCredentials]
        x509_credentials: Optional[X509Credentials]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, AuthenticationMethod], 
                username_password_credentials: Optional[UsernamePasswordCredentials] = ..., 
                x509_credentials: Optional[X509Credentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.AuthenticationMethod(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANONYMOUS = "Anonymous"
        CERTIFICATE = "Certificate"
        USERNAME_PASSWORD = "UsernamePassword"


    class azure.mgmt.deviceregistry.models.BillingContainer(ProxyResource):
        etag: Optional[str]
        id: str
        name: str
        properties: Optional[BillingContainerProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[BillingContainerProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.BillingContainerProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.deviceregistry.models.BringYourOwnRoot(_Model):
        certificate_signing_request: Optional[str]
        enabled: bool
        issuing_certificate_thumbprint: Optional[str]
        status: Optional[Union[str, BringYourOwnRootStatus]]

        @overload
        def __init__(
                self, 
                *, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.BringYourOwnRootStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ACTIVE_BUT_PENDING_RENEWAL = "ActiveButPendingRenewal"
        PENDING_ACTIVATION = "PendingActivation"


    class azure.mgmt.deviceregistry.models.BrokerStateStoreDestinationConfiguration(_Model):
        key: str

        @overload
        def __init__(
                self, 
                *, 
                key: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificateAuthorityConfiguration(_Model):
        bring_your_own_root: Optional[BringYourOwnRoot]
        key_type: Union[str, SupportedKeyType]
        subject: Optional[str]
        validity_not_after: Optional[datetime]
        validity_not_before: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                bring_your_own_root: Optional[BringYourOwnRoot] = ..., 
                key_type: Union[str, SupportedKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificateConfiguration(_Model):
        certificate_authority_configuration: CertificateAuthorityConfiguration
        leaf_certificate_configuration: LeafCertificateConfiguration

        @overload
        def __init__(
                self, 
                *, 
                certificate_authority_configuration: CertificateAuthorityConfiguration, 
                leaf_certificate_configuration: LeafCertificateConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.deviceregistry.models.Credential(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CredentialProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CredentialProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CredentialProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.deviceregistry.models.CredentialUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DataPoint(DataPointBase):
        data_point_configuration: str
        data_source: str
        name: str
        observability_mode: Optional[Union[str, DataPointObservabilityMode]]

        @overload
        def __init__(
                self, 
                *, 
                data_point_configuration: Optional[str] = ..., 
                data_source: str, 
                name: str, 
                observability_mode: Optional[Union[str, DataPointObservabilityMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DataPointBase(_Model):
        data_point_configuration: Optional[str]
        data_source: str
        name: str

        @overload
        def __init__(
                self, 
                *, 
                data_point_configuration: Optional[str] = ..., 
                data_source: str, 
                name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DataPointObservabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COUNTER = "Counter"
        GAUGE = "Gauge"
        HISTOGRAM = "Histogram"
        LOG = "Log"
        NONE = "None"


    class azure.mgmt.deviceregistry.models.Dataset(_Model):
        data_points: Optional[list[DataPoint]]
        dataset_configuration: Optional[str]
        name: str
        topic: Optional[Topic]

        @overload
        def __init__(
                self, 
                *, 
                data_points: Optional[list[DataPoint]] = ..., 
                dataset_configuration: Optional[str] = ..., 
                name: str, 
                topic: Optional[Topic] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DatasetBrokerStateStoreDestination(DatasetDestination, discriminator='BrokerStateStore'):
        configuration: BrokerStateStoreDestinationConfiguration
        target: Literal[DatasetDestinationTarget.BROKER_STATE_STORE]

        @overload
        def __init__(
                self, 
                *, 
                configuration: BrokerStateStoreDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DatasetDestination(_Model):
        target: str

        @overload
        def __init__(
                self, 
                *, 
                target: str = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DatasetDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROKER_STATE_STORE = "BrokerStateStore"
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.models.DatasetMqttDestination(DatasetDestination, discriminator='Mqtt'):
        configuration: MqttDestinationConfiguration
        target: Literal[DatasetDestinationTarget.MQTT]

        @overload
        def __init__(
                self, 
                *, 
                configuration: MqttDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DatasetStorageDestination(DatasetDestination, discriminator='Storage'):
        configuration: StorageDestinationConfiguration
        target: Literal[DatasetDestinationTarget.STORAGE]

        @overload
        def __init__(
                self, 
                *, 
                configuration: StorageDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DeviceCredentialPolicy(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DeviceCredentialsRevokeRequest(_Model):
        disable: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                disable: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DeviceMessagingEndpoint(_Model):
        address: str
        endpoint_type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: str, 
                endpoint_type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DeviceRef(_Model):
        device_name: str
        endpoint_name: str

        @overload
        def __init__(
                self, 
                *, 
                device_name: str, 
                endpoint_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DeviceStatus(_Model):
        config: Optional[StatusConfig]
        endpoints: Optional[DeviceStatusEndpoints]


    class azure.mgmt.deviceregistry.models.DeviceStatusEndpoint(_Model):
        error: Optional[StatusError]


    class azure.mgmt.deviceregistry.models.DeviceStatusEndpoints(_Model):
        inbound: Optional[dict[str, DeviceStatusEndpoint]]


    class azure.mgmt.deviceregistry.models.DiscoveredInboundEndpoints(_Model):
        additional_configuration: Optional[str]
        address: str
        endpoint_type: str
        last_updated_on: Optional[datetime]
        supported_authentication_methods: Optional[list[Union[str, AuthenticationMethod]]]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[str] = ..., 
                address: str, 
                endpoint_type: str, 
                last_updated_on: Optional[datetime] = ..., 
                supported_authentication_methods: Optional[list[Union[str, AuthenticationMethod]]] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DiscoveredMessagingEndpoints(_Model):
        inbound: Optional[dict[str, DiscoveredInboundEndpoints]]
        outbound: Optional[DiscoveredOutboundEndpoints]

        @overload
        def __init__(
                self, 
                *, 
                inbound: Optional[dict[str, DiscoveredInboundEndpoints]] = ..., 
                outbound: Optional[DiscoveredOutboundEndpoints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.DiscoveredOutboundEndpoints(_Model):
        assigned: dict[str, DeviceMessagingEndpoint]

        @overload
        def __init__(
                self, 
                *, 
                assigned: dict[str, DeviceMessagingEndpoint]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.deviceregistry.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.deviceregistry.models.ErrorDetails(_Model):
        code: Optional[str]
        correlation_id: Optional[str]
        info: Optional[str]
        message: Optional[str]


    class azure.mgmt.deviceregistry.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Event(EventBase):
        event_configuration: str
        event_notifier: str
        name: str
        observability_mode: Optional[Union[str, EventObservabilityMode]]
        topic: Topic

        @overload
        def __init__(
                self, 
                *, 
                event_configuration: Optional[str] = ..., 
                event_notifier: str, 
                name: str, 
                observability_mode: Optional[Union[str, EventObservabilityMode]] = ..., 
                topic: Optional[Topic] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.EventBase(_Model):
        event_configuration: Optional[str]
        event_notifier: str
        name: str
        topic: Optional[Topic]

        @overload
        def __init__(
                self, 
                *, 
                event_configuration: Optional[str] = ..., 
                event_notifier: str, 
                name: str, 
                topic: Optional[Topic] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.EventDestination(_Model):
        target: str

        @overload
        def __init__(
                self, 
                *, 
                target: str = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.EventDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.models.EventMqttDestination(EventDestination, discriminator='Mqtt'):
        configuration: MqttDestinationConfiguration
        target: Literal[EventDestinationTarget.MQTT]

        @overload
        def __init__(
                self, 
                *, 
                configuration: MqttDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.EventObservabilityMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOG = "Log"
        NONE = "None"


    class azure.mgmt.deviceregistry.models.EventStorageDestination(EventDestination, discriminator='Storage'):
        configuration: StorageDestinationConfiguration
        target: Literal[EventDestinationTarget.STORAGE]

        @overload
        def __init__(
                self, 
                *, 
                configuration: StorageDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ExtendedLocation(_Model):
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


    class azure.mgmt.deviceregistry.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELTA1_0 = "Delta/1.0"
        JSON_SCHEMA_DRAFT7 = "JsonSchema/draft-07"


    class azure.mgmt.deviceregistry.models.HostAuthentication(_Model):
        method: Union[str, AuthenticationMethod]
        username_password_credentials: Optional[UsernamePasswordCredentials]
        x509_credentials: Optional[X509CertificateCredentials]

        @overload
        def __init__(
                self, 
                *, 
                method: Union[str, AuthenticationMethod], 
                username_password_credentials: Optional[UsernamePasswordCredentials] = ..., 
                x509_credentials: Optional[X509CertificateCredentials] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.InboundEndpoints(_Model):
        additional_configuration: Optional[str]
        address: str
        authentication: Optional[HostAuthentication]
        endpoint_type: str
        trust_settings: Optional[TrustSettings]
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                additional_configuration: Optional[str] = ..., 
                address: str, 
                authentication: Optional[HostAuthentication] = ..., 
                endpoint_type: str, 
                trust_settings: Optional[TrustSettings] = ..., 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.LeafCertificateConfiguration(_Model):
        validity_period_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                validity_period_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ManagementAction(_Model):
        action_configuration: Optional[str]
        action_type: Optional[Union[str, ManagementActionType]]
        name: str
        target_uri: str
        timeout_in_seconds: Optional[int]
        topic: Optional[str]
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[str] = ..., 
                action_type: Optional[Union[str, ManagementActionType]] = ..., 
                name: str, 
                target_uri: str, 
                timeout_in_seconds: Optional[int] = ..., 
                topic: Optional[str] = ..., 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ManagementActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALL = "Call"
        READ = "Read"
        WRITE = "Write"


    class azure.mgmt.deviceregistry.models.ManagementGroup(_Model):
        actions: Optional[list[ManagementAction]]
        data_source: Optional[str]
        default_timeout_in_seconds: Optional[int]
        default_topic: Optional[str]
        management_group_configuration: Optional[str]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[ManagementAction]] = ..., 
                data_source: Optional[str] = ..., 
                default_timeout_in_seconds: Optional[int] = ..., 
                default_topic: Optional[str] = ..., 
                management_group_configuration: Optional[str] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MessageSchemaReference(_Model):
        schema_name: str
        schema_registry_namespace: str
        schema_version: str


    class azure.mgmt.deviceregistry.models.Messaging(_Model):
        endpoints: Optional[dict[str, MessagingEndpoint]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[dict[str, MessagingEndpoint]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MessagingEndpoint(_Model):
        address: str
        endpoint_type: Optional[str]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: str, 
                endpoint_type: Optional[str] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MessagingEndpoints(_Model):
        inbound: Optional[dict[str, InboundEndpoints]]
        outbound: Optional[OutboundEndpoints]

        @overload
        def __init__(
                self, 
                *, 
                inbound: Optional[dict[str, InboundEndpoints]] = ..., 
                outbound: Optional[OutboundEndpoints] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MqttDestinationConfiguration(_Model):
        qos: Optional[Union[str, MqttDestinationQos]]
        retain: Optional[Union[str, TopicRetainType]]
        topic: str
        ttl: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                qos: Optional[Union[str, MqttDestinationQos]] = ..., 
                retain: Optional[Union[str, TopicRetainType]] = ..., 
                topic: str, 
                ttl: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MqttDestinationQos(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        QOS0 = "Qos0"
        QOS1 = "Qos1"


    class azure.mgmt.deviceregistry.models.Namespace(TrackedResource):
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: str
        name: str
        properties: Optional[NamespaceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[NamespaceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceAsset(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[NamespaceAssetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[NamespaceAssetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceAssetProperties(_Model):
        asset_type_refs: Optional[list[str]]
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[NamespaceDataset]]
        default_datasets_configuration: Optional[str]
        default_datasets_destinations: Optional[list[DatasetDestination]]
        default_events_configuration: Optional[str]
        default_events_destinations: Optional[list[EventDestination]]
        default_management_groups_configuration: Optional[str]
        default_streams_configuration: Optional[str]
        default_streams_destinations: Optional[list[StreamDestination]]
        description: Optional[str]
        device_ref: DeviceRef
        discovered_asset_refs: Optional[list[str]]
        display_name: Optional[str]
        documentation_uri: Optional[str]
        enabled: Optional[bool]
        event_groups: Optional[list[NamespaceEventGroup]]
        external_asset_id: Optional[str]
        hardware_revision: Optional[str]
        last_transition_time: Optional[datetime]
        management_groups: Optional[list[ManagementGroup]]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]
        software_revision: Optional[str]
        status: Optional[NamespaceAssetStatus]
        streams: Optional[list[NamespaceStream]]
        uuid: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asset_type_refs: Optional[list[str]] = ..., 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[NamespaceDataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_datasets_destinations: Optional[list[DatasetDestination]] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_events_destinations: Optional[list[EventDestination]] = ..., 
                default_management_groups_configuration: Optional[str] = ..., 
                default_streams_configuration: Optional[str] = ..., 
                default_streams_destinations: Optional[list[StreamDestination]] = ..., 
                description: Optional[str] = ..., 
                device_ref: DeviceRef, 
                discovered_asset_refs: Optional[list[str]] = ..., 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                event_groups: Optional[list[NamespaceEventGroup]] = ..., 
                external_asset_id: Optional[str] = ..., 
                hardware_revision: Optional[str] = ..., 
                management_groups: Optional[list[ManagementGroup]] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ..., 
                streams: Optional[list[NamespaceStream]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatus(_Model):
        config: Optional[StatusConfig]
        datasets: Optional[list[NamespaceAssetStatusDataset]]
        event_groups: Optional[list[NamespaceAssetStatusEventGroup]]
        management_groups: Optional[list[NamespaceAssetStatusManagementGroup]]
        streams: Optional[list[NamespaceAssetStatusStream]]


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusDataset(_Model):
        error: Optional[StatusError]
        message_schema_reference: Optional[NamespaceMessageSchemaReference]
        name: str


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusEvent(_Model):
        error: Optional[StatusError]
        message_schema_reference: Optional[NamespaceMessageSchemaReference]
        name: str


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusEventGroup(_Model):
        events: Optional[list[NamespaceAssetStatusEvent]]
        name: str


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusManagementAction(_Model):
        error: Optional[StatusError]
        name: str
        request_message_schema_reference: Optional[NamespaceMessageSchemaReference]
        response_message_schema_reference: Optional[NamespaceMessageSchemaReference]


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusManagementGroup(_Model):
        actions: Optional[list[NamespaceAssetStatusManagementAction]]
        name: str


    class azure.mgmt.deviceregistry.models.NamespaceAssetStatusStream(_Model):
        error: Optional[StatusError]
        message_schema_reference: Optional[NamespaceMessageSchemaReference]
        name: str


    class azure.mgmt.deviceregistry.models.NamespaceAssetUpdate(_Model):
        properties: Optional[NamespaceAssetUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceAssetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceAssetUpdateProperties(_Model):
        asset_type_refs: Optional[list[str]]
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[NamespaceDataset]]
        default_datasets_configuration: Optional[str]
        default_datasets_destinations: Optional[list[DatasetDestination]]
        default_events_configuration: Optional[str]
        default_events_destinations: Optional[list[EventDestination]]
        default_management_groups_configuration: Optional[str]
        default_streams_configuration: Optional[str]
        default_streams_destinations: Optional[list[StreamDestination]]
        description: Optional[str]
        display_name: Optional[str]
        documentation_uri: Optional[str]
        enabled: Optional[bool]
        event_groups: Optional[list[NamespaceEventGroup]]
        hardware_revision: Optional[str]
        management_groups: Optional[list[ManagementGroup]]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        serial_number: Optional[str]
        software_revision: Optional[str]
        streams: Optional[list[NamespaceStream]]

        @overload
        def __init__(
                self, 
                *, 
                asset_type_refs: Optional[list[str]] = ..., 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[NamespaceDataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_datasets_destinations: Optional[list[DatasetDestination]] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_events_destinations: Optional[list[EventDestination]] = ..., 
                default_management_groups_configuration: Optional[str] = ..., 
                default_streams_configuration: Optional[str] = ..., 
                default_streams_destinations: Optional[list[StreamDestination]] = ..., 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                event_groups: Optional[list[NamespaceEventGroup]] = ..., 
                hardware_revision: Optional[str] = ..., 
                management_groups: Optional[list[ManagementGroup]] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ..., 
                streams: Optional[list[NamespaceStream]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDataset(_Model):
        data_points: Optional[list[NamespaceDatasetDataPoint]]
        data_source: Optional[str]
        dataset_configuration: Optional[str]
        destinations: Optional[list[DatasetDestination]]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_points: Optional[list[NamespaceDatasetDataPoint]] = ..., 
                data_source: Optional[str] = ..., 
                dataset_configuration: Optional[str] = ..., 
                destinations: Optional[list[DatasetDestination]] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDatasetDataPoint(_Model):
        data_point_configuration: Optional[str]
        data_source: str
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_point_configuration: Optional[str] = ..., 
                data_source: str, 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDevice(TrackedResource):
        etag: Optional[str]
        extended_location: Optional[ExtendedLocation]
        id: str
        location: str
        name: str
        properties: Optional[NamespaceDeviceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: Optional[ExtendedLocation] = ..., 
                location: str, 
                properties: Optional[NamespaceDeviceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDeviceProperties(_Model):
        attributes: Optional[dict[str, Any]]
        discovered_device_ref: Optional[str]
        enabled: Optional[bool]
        endpoints: Optional[MessagingEndpoints]
        external_device_id: Optional[str]
        last_transition_time: Optional[datetime]
        manufacturer: Optional[str]
        model: Optional[str]
        operating_system: Optional[str]
        operating_system_version: Optional[str]
        policy: Optional[DeviceCredentialPolicy]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        status: Optional[DeviceStatus]
        uuid: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                discovered_device_ref: Optional[str] = ..., 
                enabled: Optional[bool] = ..., 
                endpoints: Optional[MessagingEndpoints] = ..., 
                external_device_id: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                model: Optional[str] = ..., 
                operating_system: Optional[str] = ..., 
                operating_system_version: Optional[str] = ..., 
                policy: Optional[DeviceCredentialPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDeviceUpdate(_Model):
        properties: Optional[NamespaceDeviceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceDeviceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDeviceUpdateProperties(_Model):
        attributes: Optional[dict[str, Any]]
        enabled: Optional[bool]
        endpoints: Optional[MessagingEndpoints]
        operating_system_version: Optional[str]
        policy: Optional[DeviceCredentialPolicy]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                enabled: Optional[bool] = ..., 
                endpoints: Optional[MessagingEndpoints] = ..., 
                operating_system_version: Optional[str] = ..., 
                policy: Optional[DeviceCredentialPolicy] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredAsset(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[NamespaceDiscoveredAssetProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[NamespaceDiscoveredAssetProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredAssetProperties(_Model):
        asset_type_refs: Optional[list[str]]
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[NamespaceDiscoveredDataset]]
        default_datasets_configuration: Optional[str]
        default_datasets_destinations: Optional[list[DatasetDestination]]
        default_events_configuration: Optional[str]
        default_events_destinations: Optional[list[EventDestination]]
        default_management_groups_configuration: Optional[str]
        default_streams_configuration: Optional[str]
        default_streams_destinations: Optional[list[StreamDestination]]
        description: Optional[str]
        device_ref: DeviceRef
        discovery_id: str
        display_name: Optional[str]
        documentation_uri: Optional[str]
        event_groups: Optional[list[NamespaceDiscoveredEventGroup]]
        external_asset_id: Optional[str]
        hardware_revision: Optional[str]
        management_groups: Optional[list[NamespaceDiscoveredManagementGroup]]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        serial_number: Optional[str]
        software_revision: Optional[str]
        streams: Optional[list[NamespaceDiscoveredStream]]
        version: int

        @overload
        def __init__(
                self, 
                *, 
                asset_type_refs: Optional[list[str]] = ..., 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[NamespaceDiscoveredDataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_datasets_destinations: Optional[list[DatasetDestination]] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_events_destinations: Optional[list[EventDestination]] = ..., 
                default_management_groups_configuration: Optional[str] = ..., 
                default_streams_configuration: Optional[str] = ..., 
                default_streams_destinations: Optional[list[StreamDestination]] = ..., 
                description: Optional[str] = ..., 
                device_ref: DeviceRef, 
                discovery_id: str, 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                event_groups: Optional[list[NamespaceDiscoveredEventGroup]] = ..., 
                external_asset_id: Optional[str] = ..., 
                hardware_revision: Optional[str] = ..., 
                management_groups: Optional[list[NamespaceDiscoveredManagementGroup]] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ..., 
                streams: Optional[list[NamespaceDiscoveredStream]] = ..., 
                version: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredAssetUpdate(_Model):
        properties: Optional[NamespaceDiscoveredAssetUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceDiscoveredAssetUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredAssetUpdateProperties(_Model):
        asset_type_refs: Optional[list[str]]
        attributes: Optional[dict[str, Any]]
        datasets: Optional[list[NamespaceDiscoveredDataset]]
        default_datasets_configuration: Optional[str]
        default_datasets_destinations: Optional[list[DatasetDestination]]
        default_events_configuration: Optional[str]
        default_events_destinations: Optional[list[EventDestination]]
        default_management_groups_configuration: Optional[str]
        default_streams_configuration: Optional[str]
        default_streams_destinations: Optional[list[StreamDestination]]
        description: Optional[str]
        device_ref: Optional[DeviceRef]
        discovery_id: Optional[str]
        display_name: Optional[str]
        documentation_uri: Optional[str]
        event_groups: Optional[list[NamespaceDiscoveredEventGroup]]
        hardware_revision: Optional[str]
        management_groups: Optional[list[NamespaceDiscoveredManagementGroup]]
        manufacturer: Optional[str]
        manufacturer_uri: Optional[str]
        model: Optional[str]
        product_code: Optional[str]
        serial_number: Optional[str]
        software_revision: Optional[str]
        streams: Optional[list[NamespaceDiscoveredStream]]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                asset_type_refs: Optional[list[str]] = ..., 
                attributes: Optional[dict[str, Any]] = ..., 
                datasets: Optional[list[NamespaceDiscoveredDataset]] = ..., 
                default_datasets_configuration: Optional[str] = ..., 
                default_datasets_destinations: Optional[list[DatasetDestination]] = ..., 
                default_events_configuration: Optional[str] = ..., 
                default_events_destinations: Optional[list[EventDestination]] = ..., 
                default_management_groups_configuration: Optional[str] = ..., 
                default_streams_configuration: Optional[str] = ..., 
                default_streams_destinations: Optional[list[StreamDestination]] = ..., 
                description: Optional[str] = ..., 
                device_ref: Optional[DeviceRef] = ..., 
                discovery_id: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                documentation_uri: Optional[str] = ..., 
                event_groups: Optional[list[NamespaceDiscoveredEventGroup]] = ..., 
                hardware_revision: Optional[str] = ..., 
                management_groups: Optional[list[NamespaceDiscoveredManagementGroup]] = ..., 
                manufacturer: Optional[str] = ..., 
                manufacturer_uri: Optional[str] = ..., 
                model: Optional[str] = ..., 
                product_code: Optional[str] = ..., 
                serial_number: Optional[str] = ..., 
                software_revision: Optional[str] = ..., 
                streams: Optional[list[NamespaceDiscoveredStream]] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDataset(_Model):
        data_points: Optional[list[NamespaceDiscoveredDatasetDataPoint]]
        data_source: Optional[str]
        dataset_configuration: Optional[str]
        destinations: Optional[list[DatasetDestination]]
        last_updated_on: Optional[datetime]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_points: Optional[list[NamespaceDiscoveredDatasetDataPoint]] = ..., 
                data_source: Optional[str] = ..., 
                dataset_configuration: Optional[str] = ..., 
                destinations: Optional[list[DatasetDestination]] = ..., 
                last_updated_on: Optional[datetime] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDatasetDataPoint(_Model):
        data_point_configuration: Optional[str]
        data_source: str
        last_updated_on: Optional[datetime]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_point_configuration: Optional[str] = ..., 
                data_source: str, 
                last_updated_on: Optional[datetime] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDevice(TrackedResource):
        extended_location: ExtendedLocation
        id: str
        location: str
        name: str
        properties: Optional[NamespaceDiscoveredDeviceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                extended_location: ExtendedLocation, 
                location: str, 
                properties: Optional[NamespaceDiscoveredDeviceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDeviceProperties(_Model):
        attributes: Optional[dict[str, Any]]
        discovery_id: str
        endpoints: Optional[DiscoveredMessagingEndpoints]
        external_device_id: Optional[str]
        manufacturer: Optional[str]
        model: Optional[str]
        operating_system: Optional[str]
        operating_system_version: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        version: int

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                discovery_id: str, 
                endpoints: Optional[DiscoveredMessagingEndpoints] = ..., 
                external_device_id: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                model: Optional[str] = ..., 
                operating_system: Optional[str] = ..., 
                operating_system_version: Optional[str] = ..., 
                version: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDeviceUpdate(_Model):
        properties: Optional[NamespaceDiscoveredDeviceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[NamespaceDiscoveredDeviceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredDeviceUpdateProperties(_Model):
        attributes: Optional[dict[str, Any]]
        discovery_id: Optional[str]
        endpoints: Optional[DiscoveredMessagingEndpoints]
        external_device_id: Optional[str]
        operating_system_version: Optional[str]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                discovery_id: Optional[str] = ..., 
                endpoints: Optional[DiscoveredMessagingEndpoints] = ..., 
                external_device_id: Optional[str] = ..., 
                operating_system_version: Optional[str] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredEvent(_Model):
        data_source: Optional[str]
        destinations: Optional[list[EventDestination]]
        event_configuration: Optional[str]
        last_updated_on: Optional[datetime]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[str] = ..., 
                destinations: Optional[list[EventDestination]] = ..., 
                event_configuration: Optional[str] = ..., 
                last_updated_on: Optional[datetime] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredEventGroup(_Model):
        data_source: Optional[str]
        default_destinations: Optional[list[EventDestination]]
        event_group_configuration: Optional[str]
        events: Optional[list[NamespaceDiscoveredEvent]]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[str] = ..., 
                default_destinations: Optional[list[EventDestination]] = ..., 
                event_group_configuration: Optional[str] = ..., 
                events: Optional[list[NamespaceDiscoveredEvent]] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredManagementAction(_Model):
        action_configuration: Optional[str]
        action_type: Optional[Union[str, NamespaceDiscoveredManagementActionType]]
        last_updated_on: Optional[datetime]
        name: str
        target_uri: str
        timeout_in_seconds: Optional[int]
        topic: Optional[str]
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                action_configuration: Optional[str] = ..., 
                action_type: Optional[Union[str, NamespaceDiscoveredManagementActionType]] = ..., 
                last_updated_on: Optional[datetime] = ..., 
                name: str, 
                target_uri: str, 
                timeout_in_seconds: Optional[int] = ..., 
                topic: Optional[str] = ..., 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredManagementActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CALL = "Call"
        READ = "Read"
        WRITE = "Write"


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredManagementGroup(_Model):
        actions: Optional[list[NamespaceDiscoveredManagementAction]]
        data_source: Optional[str]
        default_timeout_in_seconds: Optional[int]
        default_topic: Optional[str]
        last_updated_on: Optional[datetime]
        management_group_configuration: Optional[str]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                actions: Optional[list[NamespaceDiscoveredManagementAction]] = ..., 
                data_source: Optional[str] = ..., 
                default_timeout_in_seconds: Optional[int] = ..., 
                default_topic: Optional[str] = ..., 
                last_updated_on: Optional[datetime] = ..., 
                management_group_configuration: Optional[str] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceDiscoveredStream(_Model):
        destinations: Optional[list[StreamDestination]]
        last_updated_on: Optional[datetime]
        name: str
        stream_configuration: Optional[str]
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destinations: Optional[list[StreamDestination]] = ..., 
                last_updated_on: Optional[datetime] = ..., 
                name: str, 
                stream_configuration: Optional[str] = ..., 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceEvent(_Model):
        data_source: Optional[str]
        destinations: Optional[list[EventDestination]]
        event_configuration: Optional[str]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[str] = ..., 
                destinations: Optional[list[EventDestination]] = ..., 
                event_configuration: Optional[str] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceEventGroup(_Model):
        data_source: Optional[str]
        default_destinations: Optional[list[EventDestination]]
        event_group_configuration: Optional[str]
        events: Optional[list[NamespaceEvent]]
        name: str
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                data_source: Optional[str] = ..., 
                default_destinations: Optional[list[EventDestination]] = ..., 
                event_group_configuration: Optional[str] = ..., 
                events: Optional[list[NamespaceEvent]] = ..., 
                name: str, 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceMessageSchemaReference(_Model):
        schema_name: str
        schema_registry_namespace: str
        schema_version: str


    class azure.mgmt.deviceregistry.models.NamespaceMigrateRequest(_Model):
        resource_ids: Optional[list[str]]
        scope: Optional[Union[str, Scope]]

        @overload
        def __init__(
                self, 
                *, 
                resource_ids: Optional[list[str]] = ..., 
                scope: Optional[Union[str, Scope]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceProperties(_Model):
        messaging: Optional[Messaging]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                messaging: Optional[Messaging] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceStream(_Model):
        destinations: Optional[list[StreamDestination]]
        name: str
        stream_configuration: Optional[str]
        type_ref: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                destinations: Optional[list[StreamDestination]] = ..., 
                name: str, 
                stream_configuration: Optional[str] = ..., 
                type_ref: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceUpdate(_Model):
        identity: Optional[SystemAssignedServiceIdentity]
        properties: Optional[NamespaceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                properties: Optional[NamespaceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceUpdateProperties(_Model):
        messaging: Optional[Messaging]

        @overload
        def __init__(
                self, 
                *, 
                messaging: Optional[Messaging] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Operation(_Model):
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


    class azure.mgmt.deviceregistry.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.deviceregistry.models.OperationStatusResult(_Model):
        end_time: Optional[datetime]
        error: Optional[ErrorDetail]
        id: Optional[str]
        name: Optional[str]
        operations: Optional[list[OperationStatusResult]]
        percent_complete: Optional[float]
        resource_id: Optional[str]
        start_time: Optional[datetime]
        status: str

        @overload
        def __init__(
                self, 
                *, 
                end_time: Optional[datetime] = ..., 
                error: Optional[ErrorDetail] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                operations: Optional[list[OperationStatusResult]] = ..., 
                percent_complete: Optional[float] = ..., 
                start_time: Optional[datetime] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.deviceregistry.models.OutboundEndpoints(_Model):
        assigned: dict[str, DeviceMessagingEndpoint]
        unassigned: Optional[dict[str, DeviceMessagingEndpoint]]

        @overload
        def __init__(
                self, 
                *, 
                assigned: dict[str, DeviceMessagingEndpoint], 
                unassigned: Optional[dict[str, DeviceMessagingEndpoint]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Policy(ProxyResource):
        id: str
        name: str
        properties: Optional[PolicyProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.PolicyProperties(_Model):
        certificate: Optional[CertificateConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[CertificateConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.PolicyUpdate(_Model):
        properties: Optional[PolicyUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PolicyUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.PolicyUpdateProperties(_Model):
        certificate: Optional[CertificateConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[CertificateConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.deviceregistry.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.deviceregistry.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.deviceregistry.models.Schema(ProxyResource):
        id: str
        name: str
        properties: Optional[SchemaProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        format: Union[str, Format]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema_type: Union[str, SchemaType]
        tags: Optional[dict[str, str]]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                format: Union[str, Format], 
                schema_type: Union[str, SchemaType], 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistry(TrackedResource):
        id: str
        identity: Optional[SystemAssignedServiceIdentity]
        location: str
        name: str
        properties: Optional[SchemaRegistryProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[SchemaRegistryProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistryProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        namespace: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        storage_account_container_url: str
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                namespace: str, 
                storage_account_container_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistryUpdate(_Model):
        identity: Optional[SystemAssignedServiceIdentity]
        properties: Optional[SchemaRegistryUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[SystemAssignedServiceIdentity] = ..., 
                properties: Optional[SchemaRegistryUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistryUpdateProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MESSAGE_SCHEMA = "MessageSchema"


    class azure.mgmt.deviceregistry.models.SchemaVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[SchemaVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SchemaVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaVersionProperties(_Model):
        description: Optional[str]
        hash: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        schema_content: str
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                schema_content: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Scope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RESOURCES = "Resources"


    class azure.mgmt.deviceregistry.models.StatusConfig(_Model):
        error: Optional[StatusError]
        last_transition_time: Optional[datetime]
        version: Optional[int]


    class azure.mgmt.deviceregistry.models.StatusError(_Model):
        code: Optional[str]
        details: Optional[list[ErrorDetails]]
        message: Optional[str]


    class azure.mgmt.deviceregistry.models.StorageDestinationConfiguration(_Model):
        path: str

        @overload
        def __init__(
                self, 
                *, 
                path: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.StreamDestination(_Model):
        target: str

        @overload
        def __init__(
                self, 
                *, 
                target: str = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.StreamDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.models.StreamMqttDestination(StreamDestination, discriminator='Mqtt'):
        configuration: MqttDestinationConfiguration
        target: Literal[StreamDestinationTarget.MQTT]

        @overload
        def __init__(
                self, 
                *, 
                configuration: MqttDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.StreamStorageDestination(StreamDestination, discriminator='Storage'):
        configuration: StorageDestinationConfiguration
        target: Literal[StreamDestinationTarget.STORAGE]

        @overload
        def __init__(
                self, 
                *, 
                configuration: StorageDestinationConfiguration
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SupportedKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECC = "ECC"


    class azure.mgmt.deviceregistry.models.SystemAssignedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, SystemAssignedServiceIdentityType]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, SystemAssignedServiceIdentityType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SystemAssignedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"


    class azure.mgmt.deviceregistry.models.SystemData(_Model):
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


    class azure.mgmt.deviceregistry.models.Topic(_Model):
        path: str
        retain: Optional[Union[str, TopicRetainType]]

        @overload
        def __init__(
                self, 
                *, 
                path: str, 
                retain: Optional[Union[str, TopicRetainType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.TopicRetainType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        KEEP = "Keep"
        NEVER = "Never"


    class azure.mgmt.deviceregistry.models.TrackedResource(Resource):
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


    class azure.mgmt.deviceregistry.models.TrustSettings(_Model):
        trust_list: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                trust_list: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.UsernamePasswordCredentials(_Model):
        password_secret_name: str
        username_secret_name: str

        @overload
        def __init__(
                self, 
                *, 
                password_secret_name: str, 
                username_secret_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.X509CertificateCredentials(_Model):
        certificate_secret_name: str
        intermediate_certificates_secret_name: Optional[str]
        key_secret_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate_secret_name: str, 
                intermediate_certificates_secret_name: Optional[str] = ..., 
                key_secret_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.X509Credentials(_Model):
        certificate_secret_name: str

        @overload
        def __init__(
                self, 
                *, 
                certificate_secret_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.deviceregistry.operations

    class azure.mgmt.deviceregistry.operations.AssetEndpointProfilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: AssetEndpointProfile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: AssetEndpointProfileUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AssetEndpointProfile]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asset_endpoint_profile_name: str, 
                **kwargs: Any
            ) -> AssetEndpointProfile: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AssetEndpointProfile]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AssetEndpointProfile]: ...


    class azure.mgmt.deviceregistry.operations.AssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: Asset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: AssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Asset]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> Asset: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Asset]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Asset]: ...


    class azure.mgmt.deviceregistry.operations.BillingContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'billing_container_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                billing_container_name: str, 
                **kwargs: Any
            ) -> BillingContainer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[BillingContainer]: ...


    class azure.mgmt.deviceregistry.operations.CredentialsOperations:

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
                resource: Credential, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def begin_synchronize(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: CredentialUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Credential]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Credential: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-11-01-preview', params_added_on={'2025-11-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Credential]: ...


    class azure.mgmt.deviceregistry.operations.NamespaceAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: NamespaceAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: NamespaceAssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> NamespaceAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NamespaceAsset]: ...


    class azure.mgmt.deviceregistry.operations.NamespaceDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: NamespaceDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: DeviceCredentialsRevokeRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_revoke(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: NamespaceDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> NamespaceDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NamespaceDevice]: ...


    class azure.mgmt.deviceregistry.operations.NamespaceDiscoveredAssetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: NamespaceDiscoveredAsset, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: NamespaceDiscoveredAssetUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NamespaceDiscoveredAsset]: ...


    class azure.mgmt.deviceregistry.operations.NamespaceDiscoveredDevicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: NamespaceDiscoveredDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: NamespaceDiscoveredDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[NamespaceDiscoveredDevice]: ...


    class azure.mgmt.deviceregistry.operations.NamespacesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: Namespace, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: NamespaceMigrateRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_migrate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: NamespaceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[Namespace]: ...


    class azure.mgmt.deviceregistry.operations.OperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.deviceregistry.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.deviceregistry.operations.PoliciesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: ActivateBringYourOwnRootRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_activate_bring_your_own_root(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: Policy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name']}, api_versions_list=['2026-03-01-preview'])
        def begin_revoke_issuer(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: PolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Policy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'policy_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                policy_name: str, 
                **kwargs: Any
            ) -> Policy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-03-01-preview', params_added_on={'2026-03-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Policy]: ...


    class azure.mgmt.deviceregistry.operations.SchemaRegistriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: SchemaRegistry, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: SchemaRegistryUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> SchemaRegistry: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SchemaRegistry]: ...


    class azure.mgmt.deviceregistry.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: SchemaVersion, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_schema(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchemaVersion]: ...


    class azure.mgmt.deviceregistry.operations.SchemasOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: Schema, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @overload
        def create_or_replace(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview'])
        def list_by_schema_registry(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Schema]: ...


```