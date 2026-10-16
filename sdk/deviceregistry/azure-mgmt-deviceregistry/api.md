```py
namespace azure.mgmt.deviceregistry

    class azure.mgmt.deviceregistry.DeviceRegistryMgmtClient: implements ContextManager 
        asset_endpoint_profiles: AssetEndpointProfilesOperations
        assets: AssetsOperations
        async_operation_status: AsyncOperationStatusOperations
        billing_containers: BillingContainersOperations
        certificate_authorities: CertificateAuthoritiesOperations
        certificate_policies: CertificatePoliciesOperations
        namespace_assets: NamespaceAssetsOperations
        namespace_devices: NamespaceDevicesOperations
        namespace_discovered_assets: NamespaceDiscoveredAssetsOperations
        namespace_discovered_devices: NamespaceDiscoveredDevicesOperations
        namespaces: NamespacesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        registry_devices: RegistryDevicesOperations
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
        async_operation_status: AsyncOperationStatusOperations
        billing_containers: BillingContainersOperations
        certificate_authorities: CertificateAuthoritiesOperations
        certificate_policies: CertificatePoliciesOperations
        namespace_assets: NamespaceAssetsOperations
        namespace_devices: NamespaceDevicesOperations
        namespace_discovered_assets: NamespaceDiscoveredAssetsOperations
        namespace_discovered_devices: NamespaceDiscoveredDevicesOperations
        namespaces: NamespacesOperations
        operation_status: OperationStatusOperations
        operations: Operations
        registry_devices: RegistryDevicesOperations
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


    class azure.mgmt.deviceregistry.aio.operations.AsyncOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.deviceregistry.aio.operations.BillingContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'billing_container_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                billing_container_name: str, 
                **kwargs: Any
            ) -> BillingContainer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[BillingContainer]: ...


    class azure.mgmt.deviceregistry.aio.operations.CertificateAuthoritiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: ActivateCertificateAuthorityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: ActivateCertificateAuthorityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: CertificateAuthority, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: CertificateAuthority, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name']}, api_versions_list=['2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name']}, api_versions_list=['2026-11-01'])
        async def begin_revoke_and_rotate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: CertificateAuthorityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: CertificateAuthorityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificateAuthority]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> CertificateAuthority: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificateAuthority]: ...


    class azure.mgmt.deviceregistry.aio.operations.CertificatePoliciesOperations:

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
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: CertificatePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: CertificatePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'certificate_policy_name']}, api_versions_list=['2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: CertificatePolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: CertificatePolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CertificatePolicy]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'certificate_policy_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_certificate_authority(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[CertificatePolicy]: ...


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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                body: NamespaceAssetExecuteActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                body: NamespaceAssetExecuteActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> NamespaceAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> NamespaceDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Namespace]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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


    class azure.mgmt.deviceregistry.aio.operations.RegistryDevicesOperations:

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
                registry_device_name: str, 
                resource: RegistryDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                resource: RegistryDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @overload
        async def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'registry_device_name']}, api_versions_list=['2026-11-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: RegistryDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: RegistryDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RegistryDevice]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'registry_device_name', 'accept']}, api_versions_list=['2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                **kwargs: Any
            ) -> RegistryDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[RegistryDevice]: ...


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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SchemaRegistry]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> SchemaRegistry: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SchemaRegistry]: ...


    class azure.mgmt.deviceregistry.aio.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        async def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_schema_registry(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Schema]: ...


namespace azure.mgmt.deviceregistry.models

    class azure.mgmt.deviceregistry.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.deviceregistry.models.ActivateCertificateAuthorityRequest(_Model):
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


    class azure.mgmt.deviceregistry.models.CertificateAuthority(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CertificateAuthorityProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CertificateAuthorityProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificateAuthorityIssuer(_Model):
        issuer_type: str

        @overload
        def __init__(
                self, 
                *, 
                issuer_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificateAuthorityIssuerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        MICROSOFT = "Microsoft"


    class azure.mgmt.deviceregistry.models.CertificateAuthorityKeyType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ECC = "ECC"


    class azure.mgmt.deviceregistry.models.CertificateAuthorityProperties(_Model):
        certificate_authority_type: str
        key_type: Union[str, CertificateAuthorityKeyType]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        subject: Optional[str]
        uuid: Optional[str]
        validity_not_after: Optional[datetime]
        validity_not_before: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                certificate_authority_type: str, 
                key_type: Union[str, CertificateAuthorityKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificateAuthorityStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE = "Active"
        ACTIVE_BUT_PENDING_RENEWAL = "ActiveButPendingRenewal"
        PENDING_ACTIVATION = "PendingActivation"


    class azure.mgmt.deviceregistry.models.CertificateAuthorityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ICA = "ICA"
        ROOT = "Root"


    class azure.mgmt.deviceregistry.models.CertificateAuthorityUpdate(_Model):
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificatePolicy(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[CertificatePolicyProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[CertificatePolicyProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificatePolicyConfiguration(_Model):
        validity_period_in_days: int

        @overload
        def __init__(
                self, 
                *, 
                validity_period_in_days: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificatePolicyProperties(_Model):
        certificate: Optional[CertificatePolicyConfiguration]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[CertificatePolicyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificatePolicyUpdate(_Model):
        properties: Optional[CertificatePolicyUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CertificatePolicyUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CertificatePolicyUpdateProperties(_Model):
        certificate: Optional[OptionalPropertiesCertificatePolicyConfiguration]

        @overload
        def __init__(
                self, 
                *, 
                certificate: Optional[OptionalPropertiesCertificatePolicyConfiguration] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


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
        health_state: Optional[HealthState]


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


    class azure.mgmt.deviceregistry.models.ExternalCertificateAuthorityIssuer(CertificateAuthorityIssuer, discriminator='External'):
        certificate_signing_request: Optional[str]
        issuer_type: Literal[CertificateAuthorityIssuerType.EXTERNAL]
        status: Optional[Union[str, CertificateAuthorityStatus]]
        thumbprint: Optional[str]

        @overload
        def __init__(self) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Format(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELTA1_0 = "Delta/1.0"
        JSON_LD1_1 = "JsonLD/1.1"
        JSON_SCHEMA_DRAFT7 = "JsonSchema/draft-07"


    class azure.mgmt.deviceregistry.models.HealthState(_Model):
        last_transition_time: Optional[str]
        last_update_time: Optional[str]
        message: Optional[str]
        reason_code: Optional[str]
        status: Optional[Union[str, HealthStatus]]


    class azure.mgmt.deviceregistry.models.HealthStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DEGRADED = "Degraded"
        UNAVAILABLE = "Unavailable"
        UNKNOWN = "Unknown"


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


    class azure.mgmt.deviceregistry.models.InboundCallerIdentity(_Model):
        type: Union[str, InboundCallerIdentityType]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, InboundCallerIdentityType], 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.InboundCallerIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


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


    class azure.mgmt.deviceregistry.models.IntermediateCertificateAuthorityProperties(CertificateAuthorityProperties, discriminator='ICA'):
        certificate_authority_type: Literal[CertificateAuthorityType.ICA]
        issuer: CertificateAuthorityIssuer
        key_type: Union[str, CertificateAuthorityKeyType]
        provisioning_state: Union[str, ProvisioningState]
        subject: str
        uuid: str
        validity_not_after: datetime
        validity_not_before: datetime

        @overload
        def __init__(
                self, 
                *, 
                issuer: CertificateAuthorityIssuer, 
                key_type: Union[str, CertificateAuthorityKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.deviceregistry.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.deviceregistry.models.Management(_Model):
        endpoints: Optional[dict[str, ManagementEndpoint]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[dict[str, ManagementEndpoint]] = ...
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


    class azure.mgmt.deviceregistry.models.ManagementEndpoint(_Model):
        address: str
        endpoint_type: str
        resource_id: str
        scope_id: str

        @overload
        def __init__(
                self, 
                *, 
                address: str, 
                endpoint_type: str, 
                resource_id: str, 
                scope_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        address: Optional[str]
        device_address: Optional[str]
        endpoint_type: Optional[str]
        inbound_caller_identity: Optional[InboundCallerIdentity]
        linking_error: Optional[NamespaceLinkingError]
        linking_state: Optional[Union[str, NamespaceLinkingStateValue]]
        provisioning: Optional[MessagingEndpointProvisioning]
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                address: Optional[str] = ..., 
                endpoint_type: Optional[str] = ..., 
                inbound_caller_identity: Optional[InboundCallerIdentity] = ..., 
                provisioning: Optional[MessagingEndpointProvisioning] = ..., 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.MessagingEndpointAvailability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AVAILABLE = "Available"
        DISABLED = "Disabled"


    class azure.mgmt.deviceregistry.models.MessagingEndpointProvisioning(_Model):
        allocation_weight: Optional[int]
        availability: Optional[Union[str, MessagingEndpointAvailability]]

        @overload
        def __init__(
                self, 
                *, 
                allocation_weight: Optional[int] = ..., 
                availability: Optional[Union[str, MessagingEndpointAvailability]] = ...
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


    class azure.mgmt.deviceregistry.models.MicrosoftCertificateAuthorityIssuer(CertificateAuthorityIssuer, discriminator='Microsoft'):
        certificate_authority_resource_id: str
        issuer_type: Literal[CertificateAuthorityIssuerType.MICROSOFT]

        @overload
        def __init__(
                self, 
                *, 
                certificate_authority_resource_id: str
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
        identity: Optional[ManagedServiceIdentity]
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
                identity: Optional[ManagedServiceIdentity] = ..., 
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


    class azure.mgmt.deviceregistry.models.NamespaceAssetExecuteActionRequest(_Model):
        management_action_name: str
        management_group_name: str
        payload: Optional[dict[str, Any]]

        @overload
        def __init__(
                self, 
                *, 
                management_action_name: str, 
                management_group_name: str, 
                payload: Optional[dict[str, Any]] = ...
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
        health_state: Optional[HealthState]
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
                operating_system_version: Optional[str] = ...
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

        @overload
        def __init__(
                self, 
                *, 
                attributes: Optional[dict[str, Any]] = ..., 
                enabled: Optional[bool] = ..., 
                endpoints: Optional[MessagingEndpoints] = ..., 
                operating_system_version: Optional[str] = ...
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


    class azure.mgmt.deviceregistry.models.NamespaceLinkingError(_Model):
        code: Optional[str]
        message: Optional[str]


    class azure.mgmt.deviceregistry.models.NamespaceLinkingStateValue(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUCCEEDED = "Succeeded"


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
        management: Optional[Management]
        messaging: Optional[Messaging]
        outbound_identity: Optional[OutboundIdentity]
        provisioning: Optional[NamespaceProvisioning]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                management: Optional[Management] = ..., 
                messaging: Optional[Messaging] = ..., 
                outbound_identity: Optional[OutboundIdentity] = ..., 
                provisioning: Optional[NamespaceProvisioning] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceProvisioning(_Model):
        endpoints: Optional[dict[str, ProvisioningEndpoint]]

        @overload
        def __init__(
                self, 
                *, 
                endpoints: Optional[dict[str, ProvisioningEndpoint]] = ...
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
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[NamespaceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[NamespaceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.NamespaceUpdateProperties(_Model):
        management: Optional[Management]
        messaging: Optional[Messaging]
        outbound_identity: Optional[OutboundIdentity]
        provisioning: Optional[NamespaceProvisioning]

        @overload
        def __init__(
                self, 
                *, 
                management: Optional[Management] = ..., 
                messaging: Optional[Messaging] = ..., 
                outbound_identity: Optional[OutboundIdentity] = ..., 
                provisioning: Optional[NamespaceProvisioning] = ...
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


    class azure.mgmt.deviceregistry.models.OptionalPropertiesCertificatePolicyConfiguration(_Model):
        validity_period_in_days: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                validity_period_in_days: Optional[int] = ...
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


    class azure.mgmt.deviceregistry.models.OutboundIdentity(_Model):
        type: Union[str, OutboundIdentityType]
        user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, OutboundIdentityType], 
                user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.OutboundIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.deviceregistry.models.ProvisioningEndpoint(_Model):
        endpoint_type: Union[str, ProvisioningEndpointType]
        inbound_caller_identity: InboundCallerIdentity
        linking_error: Optional[NamespaceLinkingError]
        linking_state: Optional[Union[str, NamespaceLinkingStateValue]]
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                endpoint_type: Union[str, ProvisioningEndpointType], 
                inbound_caller_identity: InboundCallerIdentity, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.ProvisioningEndpointType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DPS = "Microsoft.Devices/provisioningServices"


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


    class azure.mgmt.deviceregistry.models.RegistryDevice(TrackedResource):
        etag: Optional[str]
        id: str
        location: str
        name: str
        properties: Optional[RegistryDeviceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[RegistryDeviceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.RegistryDeviceEnablementState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.deviceregistry.models.RegistryDeviceProperties(_Model):
        enablement_state: Union[str, RegistryDeviceEnablementState]
        external_device_id: Optional[str]
        hardware_revision: Optional[str]
        manufacturer: Optional[str]
        model: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        software_revision: Optional[str]
        uuid: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enablement_state: Union[str, RegistryDeviceEnablementState], 
                external_device_id: Optional[str] = ..., 
                hardware_revision: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                model: Optional[str] = ..., 
                software_revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.RegistryDeviceUpdate(_Model):
        properties: Optional[RegistryDeviceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[RegistryDeviceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.RegistryDeviceUpdateProperties(_Model):
        enablement_state: Optional[Union[str, RegistryDeviceEnablementState]]
        hardware_revision: Optional[str]
        manufacturer: Optional[str]
        model: Optional[str]
        software_revision: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                enablement_state: Optional[Union[str, RegistryDeviceEnablementState]] = ..., 
                hardware_revision: Optional[str] = ..., 
                manufacturer: Optional[str] = ..., 
                model: Optional[str] = ..., 
                software_revision: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.deviceregistry.models.RootCertificateAuthorityProperties(CertificateAuthorityProperties, discriminator='Root'):
        certificate_authority_type: Literal[CertificateAuthorityType.ROOT]
        key_type: Union[str, CertificateAuthorityKeyType]
        provisioning_state: Union[str, ProvisioningState]
        subject: str
        uuid: str
        validity_not_after: datetime
        validity_not_before: datetime

        @overload
        def __init__(
                self, 
                *, 
                key_type: Union[str, CertificateAuthorityKeyType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


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
        identity: Optional[ManagedServiceIdentity]
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
                identity: Optional[ManagedServiceIdentity] = ..., 
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
        outbound_identity: Optional[OutboundIdentity]
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
                outbound_identity: Optional[OutboundIdentity] = ..., 
                storage_account_container_url: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistryUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[SchemaRegistryUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[SchemaRegistryUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaRegistryUpdateProperties(_Model):
        description: Optional[str]
        display_name: Optional[str]
        outbound_identity: Optional[OutboundIdentity]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: Optional[str] = ..., 
                outbound_identity: Optional[OutboundIdentity] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.deviceregistry.models.SchemaType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MESSAGE_SCHEMA = "MessageSchema"
        THING_DESCRIPTION = "ThingDescription"
        THING_MODEL = "ThingModel"


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


    class azure.mgmt.deviceregistry.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


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


    class azure.mgmt.deviceregistry.operations.AsyncOperationStatusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'location', 'operation_id', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                location: str, 
                operation_id: str, 
                **kwargs: Any
            ) -> OperationStatusResult: ...


    class azure.mgmt.deviceregistry.operations.BillingContainersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'billing_container_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                billing_container_name: str, 
                **kwargs: Any
            ) -> BillingContainer: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2024-11-01', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[BillingContainer]: ...


    class azure.mgmt.deviceregistry.operations.CertificateAuthoritiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: ActivateCertificateAuthorityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: ActivateCertificateAuthorityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_activate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: CertificateAuthority, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: CertificateAuthority, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name']}, api_versions_list=['2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name']}, api_versions_list=['2026-11-01'])
        def begin_revoke_and_rotate(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: CertificateAuthorityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: CertificateAuthorityUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificateAuthority]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> CertificateAuthority: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificateAuthority]: ...


    class azure.mgmt.deviceregistry.operations.CertificatePoliciesOperations:

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
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: CertificatePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: CertificatePolicy, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'certificate_policy_name']}, api_versions_list=['2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: CertificatePolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: CertificatePolicyUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CertificatePolicy]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'certificate_policy_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                certificate_policy_name: str, 
                **kwargs: Any
            ) -> CertificatePolicy: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'certificate_authority_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_certificate_authority(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                certificate_authority_name: str, 
                **kwargs: Any
            ) -> ItemPaged[CertificatePolicy]: ...


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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                body: NamespaceAssetExecuteActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                body: NamespaceAssetExecuteActionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_execute_action(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                asset_name: str, 
                **kwargs: Any
            ) -> NamespaceAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                device_name: str, 
                **kwargs: Any
            ) -> NamespaceDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredAsset]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_asset_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_asset_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredAsset: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[NamespaceDiscoveredDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'discovered_device_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                discovered_device_name: str, 
                **kwargs: Any
            ) -> NamespaceDiscoveredDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_namespace(
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> Namespace: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Namespace]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-07-01-preview', params_added_on={'2025-07-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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


    class azure.mgmt.deviceregistry.operations.RegistryDevicesOperations:

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
                registry_device_name: str, 
                resource: RegistryDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                resource: RegistryDevice, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @overload
        def begin_create_or_replace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'registry_device_name']}, api_versions_list=['2026-11-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: RegistryDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: RegistryDeviceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RegistryDevice]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'registry_device_name', 'accept']}, api_versions_list=['2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                registry_device_name: str, 
                **kwargs: Any
            ) -> RegistryDevice: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-11-01', params_added_on={'2026-11-01': ['api_version', 'subscription_id', 'resource_group_name', 'namespace_name', 'accept']}, api_versions_list=['2026-11-01'])
        def list_by_namespace(
                self, 
                resource_group_name: str, 
                namespace_name: str, 
                **kwargs: Any
            ) -> ItemPaged[RegistryDevice]: ...


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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> SchemaRegistry: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SchemaRegistry]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SchemaRegistry]: ...


    class azure.mgmt.deviceregistry.operations.SchemaVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'schema_version_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                schema_version_name: str, 
                **kwargs: Any
            ) -> SchemaVersion: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
        @api_version_validation(method_added_on='2025-10-01', params_added_on={'2025-10-01': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name']}, api_versions_list=['2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
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
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'schema_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def get(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                schema_name: str, 
                **kwargs: Any
            ) -> Schema: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-09-01-preview', params_added_on={'2024-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'schema_registry_name', 'accept']}, api_versions_list=['2024-09-01-preview', '2025-07-01-preview', '2025-10-01', '2025-11-01-preview', '2026-03-01-preview', '2026-04-01', '2026-11-01'])
        def list_by_schema_registry(
                self, 
                resource_group_name: str, 
                schema_registry_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Schema]: ...


namespace azure.mgmt.deviceregistry.types

    class azure.mgmt.deviceregistry.types.ActivateCertificateAuthorityRequest(TypedDict, total=False):
        key "certificateChain": Required[str]
        certificateChain: str


    class azure.mgmt.deviceregistry.types.Asset(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AssetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: AssetProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.AssetEndpointProfile(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AssetEndpointProfileProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: AssetEndpointProfileProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.AssetEndpointProfileProperties(TypedDict, total=False):
        key "additionalConfiguration": str
        key "authentication": ForwardRef('Authentication', module='types')
        key "discoveredAssetEndpointProfileRef": str
        key "endpointProfileType": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('AssetEndpointProfileStatus', module='types')
        key "targetAddress": Required[str]
        key "uuid": str
        additionalConfiguration: str
        authentication: Authentication
        discoveredAssetEndpointProfileRef: str
        endpointProfileType: str
        provisioningState: Union[str, ProvisioningState]
        status: AssetEndpointProfileStatus
        targetAddress: str
        uuid: str


    class azure.mgmt.deviceregistry.types.AssetEndpointProfileStatus(TypedDict, total=False):
        errors: list[AssetEndpointProfileStatusError]


    class azure.mgmt.deviceregistry.types.AssetEndpointProfileStatusError(TypedDict, total=False):
        key "code": int
        key "message": str
        code: int
        message: str


    class azure.mgmt.deviceregistry.types.AssetEndpointProfileUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AssetEndpointProfileUpdateProperties', module='types')
        properties: AssetEndpointProfileUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.AssetEndpointProfileUpdateProperties(TypedDict, total=False):
        key "additionalConfiguration": str
        key "authentication": ForwardRef('Authentication', module='types')
        key "endpointProfileType": str
        key "targetAddress": str
        additionalConfiguration: str
        authentication: Authentication
        endpointProfileType: str
        targetAddress: str


    class azure.mgmt.deviceregistry.types.AssetProperties(TypedDict, total=False):
        key "assetEndpointProfileRef": Required[str]
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultTopic": ForwardRef('Topic', module='types')
        key "description": str
        key "displayName": str
        key "documentationUri": str
        key "enabled": bool
        key "externalAssetId": str
        key "hardwareRevision": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "provisioningState": Union[str, ProvisioningState]
        key "serialNumber": str
        key "softwareRevision": str
        key "status": ForwardRef('AssetStatus', module='types')
        key "uuid": str
        key "version": int
        assetEndpointProfileRef: str
        attributes: dict[str, Any]
        datasets: list[Dataset]
        defaultDatasetsConfiguration: str
        defaultEventsConfiguration: str
        defaultTopic: Topic
        description: str
        discoveredAssetRefs: list[str]
        displayName: str
        documentationUri: str
        enabled: bool
        events: list[Event]
        externalAssetId: str
        hardwareRevision: str
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        provisioningState: Union[str, ProvisioningState]
        serialNumber: str
        softwareRevision: str
        status: AssetStatus
        uuid: str
        version: int


    class azure.mgmt.deviceregistry.types.AssetStatus(TypedDict, total=False):
        key "version": int
        datasets: list[AssetStatusDataset]
        errors: list[AssetStatusError]
        events: list[AssetStatusEvent]
        version: int


    class azure.mgmt.deviceregistry.types.AssetStatusDataset(TypedDict, total=False):
        key "messageSchemaReference": ForwardRef('MessageSchemaReference', module='types')
        key "name": Required[str]
        messageSchemaReference: MessageSchemaReference
        name: str


    class azure.mgmt.deviceregistry.types.AssetStatusError(TypedDict, total=False):
        key "code": int
        key "message": str
        code: int
        message: str


    class azure.mgmt.deviceregistry.types.AssetStatusEvent(TypedDict, total=False):
        key "messageSchemaReference": ForwardRef('MessageSchemaReference', module='types')
        key "name": Required[str]
        messageSchemaReference: MessageSchemaReference
        name: str


    class azure.mgmt.deviceregistry.types.AssetUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AssetUpdateProperties', module='types')
        properties: AssetUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.AssetUpdateProperties(TypedDict, total=False):
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultTopic": ForwardRef('Topic', module='types')
        key "description": str
        key "displayName": str
        key "documentationUri": str
        key "enabled": bool
        key "hardwareRevision": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "serialNumber": str
        key "softwareRevision": str
        attributes: dict[str, Any]
        datasets: list[Dataset]
        defaultDatasetsConfiguration: str
        defaultEventsConfiguration: str
        defaultTopic: Topic
        description: str
        displayName: str
        documentationUri: str
        enabled: bool
        events: list[Event]
        hardwareRevision: str
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        serialNumber: str
        softwareRevision: str


    class azure.mgmt.deviceregistry.types.Authentication(TypedDict, total=False):
        key "method": Required[Union[str, AuthenticationMethod]]
        key "usernamePasswordCredentials": ForwardRef('UsernamePasswordCredentials', module='types')
        key "x509Credentials": ForwardRef('X509Credentials', module='types')
        method: Union[str, AuthenticationMethod]
        usernamePasswordCredentials: UsernamePasswordCredentials
        x509Credentials: X509Credentials


    class azure.mgmt.deviceregistry.types.BrokerStateStoreDestinationConfiguration(TypedDict, total=False):
        key "key": Required[str]
        key: str


    class azure.mgmt.deviceregistry.types.CertificateAuthority(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CertificateAuthorityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CertificateAuthorityProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.CertificateAuthorityIssuerType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        MICROSOFT = "Microsoft"


    class azure.mgmt.deviceregistry.types.CertificateAuthorityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ICA = "ICA"
        ROOT = "Root"


    class azure.mgmt.deviceregistry.types.CertificateAuthorityUpdate(TypedDict, total=False):
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.CertificatePolicy(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('CertificatePolicyProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: CertificatePolicyProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.CertificatePolicyConfiguration(TypedDict, total=False):
        key "validityPeriodInDays": Required[int]
        validityPeriodInDays: int


    class azure.mgmt.deviceregistry.types.CertificatePolicyProperties(TypedDict, total=False):
        key "certificate": ForwardRef('CertificatePolicyConfiguration', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        certificate: CertificatePolicyConfiguration
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.deviceregistry.types.CertificatePolicyUpdate(TypedDict, total=False):
        key "properties": ForwardRef('CertificatePolicyUpdateProperties', module='types')
        properties: CertificatePolicyUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.CertificatePolicyUpdateProperties(TypedDict, total=False):
        key "certificate": ForwardRef('OptionalPropertiesCertificatePolicyConfiguration', module='types')
        certificate: OptionalPropertiesCertificatePolicyConfiguration


    class azure.mgmt.deviceregistry.types.DataPoint(DataPointBase):
        key "dataPointConfiguration": str
        key "dataSource": Required[str]
        key "name": Required[str]
        key "observabilityMode": Union[str, DataPointObservabilityMode]
        dataPointConfiguration: str
        dataSource: str
        name: str
        observabilityMode: Union[str, DataPointObservabilityMode]


    class azure.mgmt.deviceregistry.types.DataPointBase(TypedDict, total=False):
        key "dataPointConfiguration": str
        key "dataSource": Required[str]
        key "name": Required[str]
        dataPointConfiguration: str
        dataSource: str
        name: str


    class azure.mgmt.deviceregistry.types.Dataset(TypedDict, total=False):
        key "datasetConfiguration": str
        key "name": Required[str]
        key "topic": ForwardRef('Topic', module='types')
        dataPoints: list[DataPoint]
        datasetConfiguration: str
        name: str
        topic: Topic


    class azure.mgmt.deviceregistry.types.DatasetBrokerStateStoreDestination(TypedDict, total=False):
        key "configuration": Required[BrokerStateStoreDestinationConfiguration]
        key "target": Required[Literal[DatasetDestinationTarget.BROKER_STATE_STORE]]
        configuration: BrokerStateStoreDestinationConfiguration
        target: Literal[DatasetDestinationTarget.BROKER_STATE_STORE]


    class azure.mgmt.deviceregistry.types.DatasetDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BROKER_STATE_STORE = "BrokerStateStore"
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.types.DatasetMqttDestination(TypedDict, total=False):
        key "configuration": Required[MqttDestinationConfiguration]
        key "target": Required[Literal[DatasetDestinationTarget.MQTT]]
        configuration: MqttDestinationConfiguration
        target: Literal[DatasetDestinationTarget.MQTT]


    class azure.mgmt.deviceregistry.types.DatasetStorageDestination(TypedDict, total=False):
        key "configuration": Required[StorageDestinationConfiguration]
        key "target": Required[Literal[DatasetDestinationTarget.STORAGE]]
        configuration: StorageDestinationConfiguration
        target: Literal[DatasetDestinationTarget.STORAGE]


    class azure.mgmt.deviceregistry.types.DeviceMessagingEndpoint(TypedDict, total=False):
        key "address": Required[str]
        key "endpointType": str
        address: str
        endpointType: str


    class azure.mgmt.deviceregistry.types.DeviceRef(TypedDict, total=False):
        key "deviceName": Required[str]
        key "endpointName": Required[str]
        deviceName: str
        endpointName: str


    class azure.mgmt.deviceregistry.types.DeviceStatus(TypedDict, total=False):
        key "config": ForwardRef('StatusConfig', module='types')
        key "endpoints": ForwardRef('DeviceStatusEndpoints', module='types')
        config: StatusConfig
        endpoints: DeviceStatusEndpoints


    class azure.mgmt.deviceregistry.types.DeviceStatusEndpoint(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "healthState": ForwardRef('HealthState', module='types')
        error: StatusError
        healthState: HealthState


    class azure.mgmt.deviceregistry.types.DeviceStatusEndpoints(TypedDict, total=False):
        inbound: dict[str, DeviceStatusEndpoint]


    class azure.mgmt.deviceregistry.types.DiscoveredInboundEndpoints(TypedDict, total=False):
        key "additionalConfiguration": str
        key "address": Required[str]
        key "endpointType": Required[str]
        key "lastUpdatedOn": str
        key "version": str
        additionalConfiguration: str
        address: str
        endpointType: str
        lastUpdatedOn: str
        supportedAuthenticationMethods: list[Union[str, AuthenticationMethod]]
        version: str


    class azure.mgmt.deviceregistry.types.DiscoveredMessagingEndpoints(TypedDict, total=False):
        key "outbound": ForwardRef('DiscoveredOutboundEndpoints', module='types')
        inbound: dict[str, DiscoveredInboundEndpoints]
        outbound: DiscoveredOutboundEndpoints


    class azure.mgmt.deviceregistry.types.DiscoveredOutboundEndpoints(TypedDict, total=False):
        key "assigned": Required[dict[str, DeviceMessagingEndpoint]]
        assigned: dict[str, DeviceMessagingEndpoint]


    class azure.mgmt.deviceregistry.types.ErrorDetails(TypedDict, total=False):
        key "code": str
        key "correlationId": str
        key "info": str
        key "message": str
        code: str
        correlationId: str
        info: str
        message: str


    class azure.mgmt.deviceregistry.types.Event(EventBase):
        key "eventConfiguration": str
        key "eventNotifier": Required[str]
        key "name": Required[str]
        key "observabilityMode": Union[str, EventObservabilityMode]
        key "topic": ForwardRef('Topic', module='types')
        eventConfiguration: str
        eventNotifier: str
        name: str
        observabilityMode: Union[str, EventObservabilityMode]
        topic: Topic


    class azure.mgmt.deviceregistry.types.EventBase(TypedDict, total=False):
        key "eventConfiguration": str
        key "eventNotifier": Required[str]
        key "name": Required[str]
        key "topic": ForwardRef('Topic', module='types')
        eventConfiguration: str
        eventNotifier: str
        name: str
        topic: Topic


    class azure.mgmt.deviceregistry.types.EventDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.types.EventMqttDestination(TypedDict, total=False):
        key "configuration": Required[MqttDestinationConfiguration]
        key "target": Required[Literal[EventDestinationTarget.MQTT]]
        configuration: MqttDestinationConfiguration
        target: Literal[EventDestinationTarget.MQTT]


    class azure.mgmt.deviceregistry.types.EventStorageDestination(TypedDict, total=False):
        key "configuration": Required[StorageDestinationConfiguration]
        key "target": Required[Literal[EventDestinationTarget.STORAGE]]
        configuration: StorageDestinationConfiguration
        target: Literal[EventDestinationTarget.STORAGE]


    class azure.mgmt.deviceregistry.types.ExtendedLocation(TypedDict, total=False):
        key "name": Required[str]
        key "type": Required[str]
        name: str
        type: str


    class azure.mgmt.deviceregistry.types.ExternalCertificateAuthorityIssuer(TypedDict, total=False):
        key "certificateSigningRequest": str
        key "issuerType": Required[Literal[CertificateAuthorityIssuerType.EXTERNAL]]
        key "status": Union[str, CertificateAuthorityStatus]
        key "thumbprint": str
        certificateSigningRequest: str
        issuerType: Literal[CertificateAuthorityIssuerType.EXTERNAL]
        status: Union[str, CertificateAuthorityStatus]
        thumbprint: str


    class azure.mgmt.deviceregistry.types.HealthState(TypedDict, total=False):
        key "lastTransitionTime": str
        key "lastUpdateTime": str
        key "message": str
        key "reasonCode": str
        key "status": Union[str, HealthStatus]
        lastTransitionTime: str
        lastUpdateTime: str
        message: str
        reasonCode: str
        status: Union[str, HealthStatus]


    class azure.mgmt.deviceregistry.types.HostAuthentication(TypedDict, total=False):
        key "method": Required[Union[str, AuthenticationMethod]]
        key "usernamePasswordCredentials": ForwardRef('UsernamePasswordCredentials', module='types')
        key "x509Credentials": ForwardRef('X509CertificateCredentials', module='types')
        method: Union[str, AuthenticationMethod]
        usernamePasswordCredentials: UsernamePasswordCredentials
        x509Credentials: X509CertificateCredentials


    class azure.mgmt.deviceregistry.types.InboundCallerIdentity(TypedDict, total=False):
        key "type": Required[Union[str, InboundCallerIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, InboundCallerIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.deviceregistry.types.InboundEndpoints(TypedDict, total=False):
        key "additionalConfiguration": str
        key "address": Required[str]
        key "authentication": ForwardRef('HostAuthentication', module='types')
        key "endpointType": Required[str]
        key "trustSettings": ForwardRef('TrustSettings', module='types')
        key "version": str
        additionalConfiguration: str
        address: str
        authentication: HostAuthentication
        endpointType: str
        trustSettings: TrustSettings
        version: str


    class azure.mgmt.deviceregistry.types.IntermediateCertificateAuthorityProperties(TypedDict, total=False):
        key "certificateAuthorityType": Required[Literal[CertificateAuthorityType.ICA]]
        key "issuer": Required[CertificateAuthorityIssuer]
        key "keyType": Required[Union[str, CertificateAuthorityKeyType]]
        key "provisioningState": Union[str, ProvisioningState]
        key "subject": str
        key "uuid": str
        key "validityNotAfter": str
        key "validityNotBefore": str
        certificateAuthorityType: Literal[CertificateAuthorityType.ICA]
        issuer: CertificateAuthorityIssuer
        keyType: Union[str, CertificateAuthorityKeyType]
        provisioningState: Union[str, ProvisioningState]
        subject: str
        uuid: str
        validityNotAfter: str
        validityNotBefore: str


    class azure.mgmt.deviceregistry.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.deviceregistry.types.Management(TypedDict, total=False):
        endpoints: dict[str, ManagementEndpoint]


    class azure.mgmt.deviceregistry.types.ManagementAction(TypedDict, total=False):
        key "actionConfiguration": str
        key "actionType": Union[str, ManagementActionType]
        key "name": Required[str]
        key "targetUri": Required[str]
        key "timeoutInSeconds": int
        key "topic": str
        key "typeRef": str
        actionConfiguration: str
        actionType: Union[str, ManagementActionType]
        name: str
        targetUri: str
        timeoutInSeconds: int
        topic: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.ManagementEndpoint(TypedDict, total=False):
        key "address": Required[str]
        key "endpointType": Required[str]
        key "resourceId": Required[str]
        key "scopeId": Required[str]
        address: str
        endpointType: str
        resourceId: str
        scopeId: str


    class azure.mgmt.deviceregistry.types.ManagementGroup(TypedDict, total=False):
        key "dataSource": str
        key "defaultTimeoutInSeconds": int
        key "defaultTopic": str
        key "managementGroupConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        actions: list[ManagementAction]
        dataSource: str
        defaultTimeoutInSeconds: int
        defaultTopic: str
        managementGroupConfiguration: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.MessageSchemaReference(TypedDict, total=False):
        key "schemaName": Required[str]
        key "schemaRegistryNamespace": Required[str]
        key "schemaVersion": Required[str]
        schemaName: str
        schemaRegistryNamespace: str
        schemaVersion: str


    class azure.mgmt.deviceregistry.types.Messaging(TypedDict, total=False):
        endpoints: dict[str, MessagingEndpoint]


    class azure.mgmt.deviceregistry.types.MessagingEndpoint(TypedDict, total=False):
        key "address": str
        key "deviceAddress": str
        key "endpointType": str
        key "inboundCallerIdentity": ForwardRef('InboundCallerIdentity', module='types')
        key "linkingError": ForwardRef('NamespaceLinkingError', module='types')
        key "linkingState": Union[str, NamespaceLinkingStateValue]
        key "provisioning": ForwardRef('MessagingEndpointProvisioning', module='types')
        key "resourceId": str
        address: str
        deviceAddress: str
        endpointType: str
        inboundCallerIdentity: InboundCallerIdentity
        linkingError: NamespaceLinkingError
        linkingState: Union[str, NamespaceLinkingStateValue]
        provisioning: MessagingEndpointProvisioning
        resourceId: str


    class azure.mgmt.deviceregistry.types.MessagingEndpointProvisioning(TypedDict, total=False):
        key "allocationWeight": int
        key "availability": Union[str, MessagingEndpointAvailability]
        allocationWeight: int
        availability: Union[str, MessagingEndpointAvailability]


    class azure.mgmt.deviceregistry.types.MessagingEndpoints(TypedDict, total=False):
        key "outbound": ForwardRef('OutboundEndpoints', module='types')
        inbound: dict[str, InboundEndpoints]
        outbound: OutboundEndpoints


    class azure.mgmt.deviceregistry.types.MicrosoftCertificateAuthorityIssuer(TypedDict, total=False):
        key "certificateAuthorityResourceId": Required[str]
        key "issuerType": Required[Literal[CertificateAuthorityIssuerType.MICROSOFT]]
        certificateAuthorityResourceId: str
        issuerType: Literal[CertificateAuthorityIssuerType.MICROSOFT]


    class azure.mgmt.deviceregistry.types.MqttDestinationConfiguration(TypedDict, total=False):
        key "qos": Union[str, MqttDestinationQos]
        key "retain": Union[str, TopicRetainType]
        key "topic": Required[str]
        key "ttl": int
        qos: Union[str, MqttDestinationQos]
        retain: Union[str, TopicRetainType]
        topic: str
        ttl: int


    class azure.mgmt.deviceregistry.types.Namespace(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: NamespaceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.NamespaceAsset(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceAssetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NamespaceAssetProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetExecuteActionRequest(TypedDict, total=False):
        key "managementActionName": Required[str]
        key "managementGroupName": Required[str]
        managementActionName: str
        managementGroupName: str
        payload: dict[str, Any]


    class azure.mgmt.deviceregistry.types.NamespaceAssetProperties(TypedDict, total=False):
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultManagementGroupsConfiguration": str
        key "defaultStreamsConfiguration": str
        key "description": str
        key "deviceRef": Required[DeviceRef]
        key "displayName": str
        key "documentationUri": str
        key "enabled": bool
        key "externalAssetId": str
        key "hardwareRevision": str
        key "lastTransitionTime": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "provisioningState": Union[str, ProvisioningState]
        key "serialNumber": str
        key "softwareRevision": str
        key "status": ForwardRef('NamespaceAssetStatus', module='types')
        key "uuid": str
        key "version": int
        assetTypeRefs: list[str]
        attributes: dict[str, Any]
        datasets: list[NamespaceDataset]
        defaultDatasetsConfiguration: str
        defaultDatasetsDestinations: list[DatasetDestination]
        defaultEventsConfiguration: str
        defaultEventsDestinations: list[EventDestination]
        defaultManagementGroupsConfiguration: str
        defaultStreamsConfiguration: str
        defaultStreamsDestinations: list[StreamDestination]
        description: str
        deviceRef: DeviceRef
        discoveredAssetRefs: list[str]
        displayName: str
        documentationUri: str
        enabled: bool
        eventGroups: list[NamespaceEventGroup]
        externalAssetId: str
        hardwareRevision: str
        lastTransitionTime: str
        managementGroups: list[ManagementGroup]
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        provisioningState: Union[str, ProvisioningState]
        serialNumber: str
        softwareRevision: str
        status: NamespaceAssetStatus
        streams: list[NamespaceStream]
        uuid: str
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatus(TypedDict, total=False):
        key "config": ForwardRef('StatusConfig', module='types')
        key "healthState": ForwardRef('HealthState', module='types')
        config: StatusConfig
        datasets: list[NamespaceAssetStatusDataset]
        eventGroups: list[NamespaceAssetStatusEventGroup]
        healthState: HealthState
        managementGroups: list[NamespaceAssetStatusManagementGroup]
        streams: list[NamespaceAssetStatusStream]


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusDataset(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "messageSchemaReference": ForwardRef('NamespaceMessageSchemaReference', module='types')
        key "name": Required[str]
        error: StatusError
        messageSchemaReference: NamespaceMessageSchemaReference
        name: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusEvent(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "messageSchemaReference": ForwardRef('NamespaceMessageSchemaReference', module='types')
        key "name": Required[str]
        error: StatusError
        messageSchemaReference: NamespaceMessageSchemaReference
        name: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusEventGroup(TypedDict, total=False):
        key "name": Required[str]
        events: list[NamespaceAssetStatusEvent]
        name: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusManagementAction(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "name": Required[str]
        key "requestMessageSchemaReference": ForwardRef('NamespaceMessageSchemaReference', module='types')
        key "responseMessageSchemaReference": ForwardRef('NamespaceMessageSchemaReference', module='types')
        error: StatusError
        name: str
        requestMessageSchemaReference: NamespaceMessageSchemaReference
        responseMessageSchemaReference: NamespaceMessageSchemaReference


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusManagementGroup(TypedDict, total=False):
        key "name": Required[str]
        actions: list[NamespaceAssetStatusManagementAction]
        name: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetStatusStream(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "messageSchemaReference": ForwardRef('NamespaceMessageSchemaReference', module='types')
        key "name": Required[str]
        error: StatusError
        messageSchemaReference: NamespaceMessageSchemaReference
        name: str


    class azure.mgmt.deviceregistry.types.NamespaceAssetUpdate(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceAssetUpdateProperties', module='types')
        properties: NamespaceAssetUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.NamespaceAssetUpdateProperties(TypedDict, total=False):
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultManagementGroupsConfiguration": str
        key "defaultStreamsConfiguration": str
        key "description": str
        key "displayName": str
        key "documentationUri": str
        key "enabled": bool
        key "hardwareRevision": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "serialNumber": str
        key "softwareRevision": str
        assetTypeRefs: list[str]
        attributes: dict[str, Any]
        datasets: list[NamespaceDataset]
        defaultDatasetsConfiguration: str
        defaultDatasetsDestinations: list[DatasetDestination]
        defaultEventsConfiguration: str
        defaultEventsDestinations: list[EventDestination]
        defaultManagementGroupsConfiguration: str
        defaultStreamsConfiguration: str
        defaultStreamsDestinations: list[StreamDestination]
        description: str
        displayName: str
        documentationUri: str
        enabled: bool
        eventGroups: list[NamespaceEventGroup]
        hardwareRevision: str
        managementGroups: list[ManagementGroup]
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        serialNumber: str
        softwareRevision: str
        streams: list[NamespaceStream]


    class azure.mgmt.deviceregistry.types.NamespaceDataset(TypedDict, total=False):
        key "dataSource": str
        key "datasetConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        dataPoints: list[NamespaceDatasetDataPoint]
        dataSource: str
        datasetConfiguration: str
        destinations: list[DatasetDestination]
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDatasetDataPoint(TypedDict, total=False):
        key "dataPointConfiguration": str
        key "dataSource": Required[str]
        key "name": Required[str]
        key "typeRef": str
        dataPointConfiguration: str
        dataSource: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDevice(TrackedResource):
        key "etag": str
        key "extendedLocation": ForwardRef('ExtendedLocation', module='types')
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceDeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NamespaceDeviceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.NamespaceDeviceProperties(TypedDict, total=False):
        key "discoveredDeviceRef": str
        key "enabled": bool
        key "endpoints": ForwardRef('MessagingEndpoints', module='types')
        key "externalDeviceId": str
        key "lastTransitionTime": str
        key "manufacturer": str
        key "model": str
        key "operatingSystem": str
        key "operatingSystemVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "status": ForwardRef('DeviceStatus', module='types')
        key "uuid": str
        key "version": int
        attributes: dict[str, Any]
        discoveredDeviceRef: str
        enabled: bool
        endpoints: MessagingEndpoints
        externalDeviceId: str
        lastTransitionTime: str
        manufacturer: str
        model: str
        operatingSystem: str
        operatingSystemVersion: str
        provisioningState: Union[str, ProvisioningState]
        status: DeviceStatus
        uuid: str
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceDeviceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceDeviceUpdateProperties', module='types')
        properties: NamespaceDeviceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.NamespaceDeviceUpdateProperties(TypedDict, total=False):
        key "enabled": bool
        key "endpoints": ForwardRef('MessagingEndpoints', module='types')
        key "operatingSystemVersion": str
        attributes: dict[str, Any]
        enabled: bool
        endpoints: MessagingEndpoints
        operatingSystemVersion: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredAsset(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceDiscoveredAssetProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NamespaceDiscoveredAssetProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredAssetProperties(TypedDict, total=False):
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultManagementGroupsConfiguration": str
        key "defaultStreamsConfiguration": str
        key "description": str
        key "deviceRef": Required[DeviceRef]
        key "discoveryId": Required[str]
        key "displayName": str
        key "documentationUri": str
        key "externalAssetId": str
        key "hardwareRevision": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "provisioningState": Union[str, ProvisioningState]
        key "serialNumber": str
        key "softwareRevision": str
        key "version": Required[int]
        assetTypeRefs: list[str]
        attributes: dict[str, Any]
        datasets: list[NamespaceDiscoveredDataset]
        defaultDatasetsConfiguration: str
        defaultDatasetsDestinations: list[DatasetDestination]
        defaultEventsConfiguration: str
        defaultEventsDestinations: list[EventDestination]
        defaultManagementGroupsConfiguration: str
        defaultStreamsConfiguration: str
        defaultStreamsDestinations: list[StreamDestination]
        description: str
        deviceRef: DeviceRef
        discoveryId: str
        displayName: str
        documentationUri: str
        eventGroups: list[NamespaceDiscoveredEventGroup]
        externalAssetId: str
        hardwareRevision: str
        managementGroups: list[NamespaceDiscoveredManagementGroup]
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        provisioningState: Union[str, ProvisioningState]
        serialNumber: str
        softwareRevision: str
        streams: list[NamespaceDiscoveredStream]
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredAssetUpdate(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceDiscoveredAssetUpdateProperties', module='types')
        properties: NamespaceDiscoveredAssetUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredAssetUpdateProperties(TypedDict, total=False):
        key "defaultDatasetsConfiguration": str
        key "defaultEventsConfiguration": str
        key "defaultManagementGroupsConfiguration": str
        key "defaultStreamsConfiguration": str
        key "description": str
        key "deviceRef": ForwardRef('DeviceRef', module='types')
        key "discoveryId": str
        key "displayName": str
        key "documentationUri": str
        key "hardwareRevision": str
        key "manufacturer": str
        key "manufacturerUri": str
        key "model": str
        key "productCode": str
        key "serialNumber": str
        key "softwareRevision": str
        key "version": int
        assetTypeRefs: list[str]
        attributes: dict[str, Any]
        datasets: list[NamespaceDiscoveredDataset]
        defaultDatasetsConfiguration: str
        defaultDatasetsDestinations: list[DatasetDestination]
        defaultEventsConfiguration: str
        defaultEventsDestinations: list[EventDestination]
        defaultManagementGroupsConfiguration: str
        defaultStreamsConfiguration: str
        defaultStreamsDestinations: list[StreamDestination]
        description: str
        deviceRef: DeviceRef
        discoveryId: str
        displayName: str
        documentationUri: str
        eventGroups: list[NamespaceDiscoveredEventGroup]
        hardwareRevision: str
        managementGroups: list[NamespaceDiscoveredManagementGroup]
        manufacturer: str
        manufacturerUri: str
        model: str
        productCode: str
        serialNumber: str
        softwareRevision: str
        streams: list[NamespaceDiscoveredStream]
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDataset(TypedDict, total=False):
        key "dataSource": str
        key "datasetConfiguration": str
        key "lastUpdatedOn": str
        key "name": Required[str]
        key "typeRef": str
        dataPoints: list[NamespaceDiscoveredDatasetDataPoint]
        dataSource: str
        datasetConfiguration: str
        destinations: list[DatasetDestination]
        lastUpdatedOn: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDatasetDataPoint(TypedDict, total=False):
        key "dataPointConfiguration": str
        key "dataSource": Required[str]
        key "lastUpdatedOn": str
        key "name": Required[str]
        key "typeRef": str
        dataPointConfiguration: str
        dataSource: str
        lastUpdatedOn: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDevice(TrackedResource):
        key "extendedLocation": Required[ExtendedLocation]
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('NamespaceDiscoveredDeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        extendedLocation: ExtendedLocation
        id: str
        location: str
        name: str
        properties: NamespaceDiscoveredDeviceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDeviceProperties(TypedDict, total=False):
        key "discoveryId": Required[str]
        key "endpoints": ForwardRef('DiscoveredMessagingEndpoints', module='types')
        key "externalDeviceId": str
        key "manufacturer": str
        key "model": str
        key "operatingSystem": str
        key "operatingSystemVersion": str
        key "provisioningState": Union[str, ProvisioningState]
        key "version": Required[int]
        attributes: dict[str, Any]
        discoveryId: str
        endpoints: DiscoveredMessagingEndpoints
        externalDeviceId: str
        manufacturer: str
        model: str
        operatingSystem: str
        operatingSystemVersion: str
        provisioningState: Union[str, ProvisioningState]
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDeviceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('NamespaceDiscoveredDeviceUpdateProperties', module='types')
        properties: NamespaceDiscoveredDeviceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredDeviceUpdateProperties(TypedDict, total=False):
        key "discoveryId": str
        key "endpoints": ForwardRef('DiscoveredMessagingEndpoints', module='types')
        key "externalDeviceId": str
        key "operatingSystemVersion": str
        key "version": int
        attributes: dict[str, Any]
        discoveryId: str
        endpoints: DiscoveredMessagingEndpoints
        externalDeviceId: str
        operatingSystemVersion: str
        version: int


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredEvent(TypedDict, total=False):
        key "dataSource": str
        key "eventConfiguration": str
        key "lastUpdatedOn": str
        key "name": Required[str]
        key "typeRef": str
        dataSource: str
        destinations: list[EventDestination]
        eventConfiguration: str
        lastUpdatedOn: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredEventGroup(TypedDict, total=False):
        key "dataSource": str
        key "eventGroupConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        dataSource: str
        defaultDestinations: list[EventDestination]
        eventGroupConfiguration: str
        events: list[NamespaceDiscoveredEvent]
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredManagementAction(TypedDict, total=False):
        key "actionConfiguration": str
        key "actionType": Union[str, NamespaceDiscoveredManagementActionType]
        key "lastUpdatedOn": str
        key "name": Required[str]
        key "targetUri": Required[str]
        key "timeoutInSeconds": int
        key "topic": str
        key "typeRef": str
        actionConfiguration: str
        actionType: Union[str, NamespaceDiscoveredManagementActionType]
        lastUpdatedOn: str
        name: str
        targetUri: str
        timeoutInSeconds: int
        topic: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredManagementGroup(TypedDict, total=False):
        key "dataSource": str
        key "defaultTimeoutInSeconds": int
        key "defaultTopic": str
        key "lastUpdatedOn": str
        key "managementGroupConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        actions: list[NamespaceDiscoveredManagementAction]
        dataSource: str
        defaultTimeoutInSeconds: int
        defaultTopic: str
        lastUpdatedOn: str
        managementGroupConfiguration: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceDiscoveredStream(TypedDict, total=False):
        key "lastUpdatedOn": str
        key "name": Required[str]
        key "streamConfiguration": str
        key "typeRef": str
        destinations: list[StreamDestination]
        lastUpdatedOn: str
        name: str
        streamConfiguration: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceEvent(TypedDict, total=False):
        key "dataSource": str
        key "eventConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        dataSource: str
        destinations: list[EventDestination]
        eventConfiguration: str
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceEventGroup(TypedDict, total=False):
        key "dataSource": str
        key "eventGroupConfiguration": str
        key "name": Required[str]
        key "typeRef": str
        dataSource: str
        defaultDestinations: list[EventDestination]
        eventGroupConfiguration: str
        events: list[NamespaceEvent]
        name: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceLinkingError(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        message: str


    class azure.mgmt.deviceregistry.types.NamespaceMessageSchemaReference(TypedDict, total=False):
        key "schemaName": Required[str]
        key "schemaRegistryNamespace": Required[str]
        key "schemaVersion": Required[str]
        schemaName: str
        schemaRegistryNamespace: str
        schemaVersion: str


    class azure.mgmt.deviceregistry.types.NamespaceMigrateRequest(TypedDict, total=False):
        key "scope": Union[str, Scope]
        resourceIds: list[str]
        scope: Union[str, Scope]


    class azure.mgmt.deviceregistry.types.NamespaceProperties(TypedDict, total=False):
        key "management": ForwardRef('Management', module='types')
        key "messaging": ForwardRef('Messaging', module='types')
        key "outboundIdentity": ForwardRef('OutboundIdentity', module='types')
        key "provisioning": ForwardRef('NamespaceProvisioning', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "uuid": str
        management: Management
        messaging: Messaging
        outboundIdentity: OutboundIdentity
        provisioning: NamespaceProvisioning
        provisioningState: Union[str, ProvisioningState]
        uuid: str


    class azure.mgmt.deviceregistry.types.NamespaceProvisioning(TypedDict, total=False):
        endpoints: dict[str, ProvisioningEndpoint]


    class azure.mgmt.deviceregistry.types.NamespaceStream(TypedDict, total=False):
        key "name": Required[str]
        key "streamConfiguration": str
        key "typeRef": str
        destinations: list[StreamDestination]
        name: str
        streamConfiguration: str
        typeRef: str


    class azure.mgmt.deviceregistry.types.NamespaceUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('NamespaceUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: NamespaceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.NamespaceUpdateProperties(TypedDict, total=False):
        key "management": ForwardRef('Management', module='types')
        key "messaging": ForwardRef('Messaging', module='types')
        key "outboundIdentity": ForwardRef('OutboundIdentity', module='types')
        key "provisioning": ForwardRef('NamespaceProvisioning', module='types')
        management: Management
        messaging: Messaging
        outboundIdentity: OutboundIdentity
        provisioning: NamespaceProvisioning


    class azure.mgmt.deviceregistry.types.OptionalPropertiesCertificatePolicyConfiguration(TypedDict, total=False):
        key "validityPeriodInDays": int
        validityPeriodInDays: int


    class azure.mgmt.deviceregistry.types.OutboundEndpoints(TypedDict, total=False):
        key "assigned": Required[dict[str, DeviceMessagingEndpoint]]
        assigned: dict[str, DeviceMessagingEndpoint]
        unassigned: dict[str, DeviceMessagingEndpoint]


    class azure.mgmt.deviceregistry.types.OutboundIdentity(TypedDict, total=False):
        key "type": Required[Union[str, OutboundIdentityType]]
        key "userAssignedIdentity": str
        type: Union[str, OutboundIdentityType]
        userAssignedIdentity: str


    class azure.mgmt.deviceregistry.types.ProvisioningEndpoint(TypedDict, total=False):
        key "endpointType": Required[Union[str, ProvisioningEndpointType]]
        key "inboundCallerIdentity": Required[InboundCallerIdentity]
        key "linkingError": ForwardRef('NamespaceLinkingError', module='types')
        key "linkingState": Union[str, NamespaceLinkingStateValue]
        key "resourceId": Required[str]
        endpointType: Union[str, ProvisioningEndpointType]
        inboundCallerIdentity: InboundCallerIdentity
        linkingError: NamespaceLinkingError
        linkingState: Union[str, NamespaceLinkingStateValue]
        resourceId: str


    class azure.mgmt.deviceregistry.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.deviceregistry.types.RegistryDevice(TrackedResource):
        key "etag": str
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('RegistryDeviceProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        etag: str
        id: str
        location: str
        name: str
        properties: RegistryDeviceProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.RegistryDeviceProperties(TypedDict, total=False):
        key "enablementState": Required[Union[str, RegistryDeviceEnablementState]]
        key "externalDeviceId": str
        key "hardwareRevision": str
        key "manufacturer": str
        key "model": str
        key "provisioningState": Union[str, ProvisioningState]
        key "softwareRevision": str
        key "uuid": str
        enablementState: Union[str, RegistryDeviceEnablementState]
        externalDeviceId: str
        hardwareRevision: str
        manufacturer: str
        model: str
        provisioningState: Union[str, ProvisioningState]
        softwareRevision: str
        uuid: str


    class azure.mgmt.deviceregistry.types.RegistryDeviceUpdate(TypedDict, total=False):
        key "properties": ForwardRef('RegistryDeviceUpdateProperties', module='types')
        properties: RegistryDeviceUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.RegistryDeviceUpdateProperties(TypedDict, total=False):
        key "enablementState": Union[str, RegistryDeviceEnablementState]
        key "hardwareRevision": str
        key "manufacturer": str
        key "model": str
        key "softwareRevision": str
        enablementState: Union[str, RegistryDeviceEnablementState]
        hardwareRevision: str
        manufacturer: str
        model: str
        softwareRevision: str


    class azure.mgmt.deviceregistry.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.deviceregistry.types.RootCertificateAuthorityProperties(TypedDict, total=False):
        key "certificateAuthorityType": Required[Literal[CertificateAuthorityType.ROOT]]
        key "keyType": Required[Union[str, CertificateAuthorityKeyType]]
        key "provisioningState": Union[str, ProvisioningState]
        key "subject": str
        key "uuid": str
        key "validityNotAfter": str
        key "validityNotBefore": str
        certificateAuthorityType: Literal[CertificateAuthorityType.ROOT]
        keyType: Union[str, CertificateAuthorityKeyType]
        provisioningState: Union[str, ProvisioningState]
        subject: str
        uuid: str
        validityNotAfter: str
        validityNotBefore: str


    class azure.mgmt.deviceregistry.types.Schema(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SchemaProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SchemaProperties
        systemData: SystemData
        type: str


    class azure.mgmt.deviceregistry.types.SchemaProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "format": Required[Union[str, Format]]
        key "provisioningState": Union[str, ProvisioningState]
        key "schemaType": Required[Union[str, SchemaType]]
        key "uuid": str
        description: str
        displayName: str
        format: Union[str, Format]
        provisioningState: Union[str, ProvisioningState]
        schemaType: Union[str, SchemaType]
        tags: dict[str, str]
        uuid: str


    class azure.mgmt.deviceregistry.types.SchemaRegistry(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('SchemaRegistryProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: SchemaRegistryProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.deviceregistry.types.SchemaRegistryProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "namespace": Required[str]
        key "outboundIdentity": ForwardRef('OutboundIdentity', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "storageAccountContainerUrl": Required[str]
        key "uuid": str
        description: str
        displayName: str
        namespace: str
        outboundIdentity: OutboundIdentity
        provisioningState: Union[str, ProvisioningState]
        storageAccountContainerUrl: str
        uuid: str


    class azure.mgmt.deviceregistry.types.SchemaRegistryUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('SchemaRegistryUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: SchemaRegistryUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.deviceregistry.types.SchemaRegistryUpdateProperties(TypedDict, total=False):
        key "description": str
        key "displayName": str
        key "outboundIdentity": ForwardRef('OutboundIdentity', module='types')
        description: str
        displayName: str
        outboundIdentity: OutboundIdentity


    class azure.mgmt.deviceregistry.types.SchemaVersion(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('SchemaVersionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: SchemaVersionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.deviceregistry.types.SchemaVersionProperties(TypedDict, total=False):
        key "description": str
        key "hash": str
        key "provisioningState": Union[str, ProvisioningState]
        key "schemaContent": Required[str]
        key "uuid": str
        description: str
        hash: str
        provisioningState: Union[str, ProvisioningState]
        schemaContent: str
        uuid: str


    class azure.mgmt.deviceregistry.types.StatusConfig(TypedDict, total=False):
        key "error": ForwardRef('StatusError', module='types')
        key "lastTransitionTime": str
        key "version": int
        error: StatusError
        lastTransitionTime: str
        version: int


    class azure.mgmt.deviceregistry.types.StatusError(TypedDict, total=False):
        key "code": str
        key "message": str
        code: str
        details: list[ErrorDetails]
        message: str


    class azure.mgmt.deviceregistry.types.StorageDestinationConfiguration(TypedDict, total=False):
        key "path": Required[str]
        path: str


    class azure.mgmt.deviceregistry.types.StreamDestinationTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MQTT = "Mqtt"
        STORAGE = "Storage"


    class azure.mgmt.deviceregistry.types.StreamMqttDestination(TypedDict, total=False):
        key "configuration": Required[MqttDestinationConfiguration]
        key "target": Required[Literal[StreamDestinationTarget.MQTT]]
        configuration: MqttDestinationConfiguration
        target: Literal[StreamDestinationTarget.MQTT]


    class azure.mgmt.deviceregistry.types.StreamStorageDestination(TypedDict, total=False):
        key "configuration": Required[StorageDestinationConfiguration]
        key "target": Required[Literal[StreamDestinationTarget.STORAGE]]
        configuration: StorageDestinationConfiguration
        target: Literal[StreamDestinationTarget.STORAGE]


    class azure.mgmt.deviceregistry.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.deviceregistry.types.Topic(TypedDict, total=False):
        key "path": Required[str]
        key "retain": Union[str, TopicRetainType]
        path: str
        retain: Union[str, TopicRetainType]


    class azure.mgmt.deviceregistry.types.TrackedResource(Resource):
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


    class azure.mgmt.deviceregistry.types.TrustSettings(TypedDict, total=False):
        key "trustList": str
        trustList: str


    class azure.mgmt.deviceregistry.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


    class azure.mgmt.deviceregistry.types.UsernamePasswordCredentials(TypedDict, total=False):
        key "passwordSecretName": Required[str]
        key "usernameSecretName": Required[str]
        passwordSecretName: str
        usernameSecretName: str


    class azure.mgmt.deviceregistry.types.X509CertificateCredentials(TypedDict, total=False):
        key "certificateSecretName": Required[str]
        key "intermediateCertificatesSecretName": str
        key "keySecretName": str
        certificateSecretName: str
        intermediateCertificatesSecretName: str
        keySecretName: str


    class azure.mgmt.deviceregistry.types.X509Credentials(TypedDict, total=False):
        key "certificateSecretName": Required[str]
        certificateSecretName: str


```