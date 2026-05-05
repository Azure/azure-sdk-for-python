```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.elasticsan

    class azure.mgmt.elasticsan.ElasticSanMgmtClient: implements ContextManager 
        elastic_sans: ElasticSansOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        skus: SkusOperations
        volume_groups: VolumeGroupsOperations
        volume_snapshots: VolumeSnapshotsOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.elasticsan.aio

    class azure.mgmt.elasticsan.aio.ElasticSanMgmtClient: implements AsyncContextManager 
        elastic_sans: ElasticSansOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations
        skus: SkusOperations
        volume_groups: VolumeGroupsOperations
        volume_snapshots: VolumeSnapshotsOperations
        volumes: VolumesOperations

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


namespace azure.mgmt.elasticsan.aio.operations

    class azure.mgmt.elasticsan.aio.operations.ElasticSansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: ElasticSan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: ElasticSanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ElasticSan]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> ElasticSan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ElasticSan]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[ElasticSan]: ...


    class azure.mgmt.elasticsan.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.elasticsan.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.elasticsan.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def list_by_elastic_san(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.elasticsan.aio.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SkuInformation]: ...


    class azure.mgmt.elasticsan.aio.operations.VolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[VolumeGroup]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroup: ...

        @distributed_trace
        def list_by_elastic_san(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[VolumeGroup]: ...


    class azure.mgmt.elasticsan.aio.operations.VolumeSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Snapshot]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[Snapshot]: ...


    class azure.mgmt.elasticsan.aio.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                *, 
                x_ms_delete_snapshots: Optional[Union[str, XMsDeleteSnapshots]] = ..., 
                x_ms_force_delete: Optional[Union[str, XMsForceDelete]] = ..., 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeNameList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: DiskSnapshotList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PreValidationResponse]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Volume]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Volume]: ...


namespace azure.mgmt.elasticsan.models

    class azure.mgmt.elasticsan.models.Action(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOW = "Allow"


    class azure.mgmt.elasticsan.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.elasticsan.models.AutoScalePolicyEnforcement(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"
        NONE = "None"


    class azure.mgmt.elasticsan.models.AutoScaleProperties(_Model):
        scale_up_properties: Optional[ScaleUpProperties]

        @overload
        def __init__(
                self, 
                *, 
                scale_up_properties: Optional[ScaleUpProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.elasticsan.models.DiskSnapshotList(_Model):
        disk_snapshot_ids: list[str]

        @overload
        def __init__(
                self, 
                *, 
                disk_snapshot_ids: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.ElasticSan(TrackedResource):
        id: str
        location: str
        name: str
        properties: ElasticSanProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: ElasticSanProperties, 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.ElasticSanProperties(_Model):
        auto_scale_properties: Optional[AutoScaleProperties]
        availability_zones: Optional[list[str]]
        base_size_ti_b: int
        extended_capacity_size_ti_b: int
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        provisioning_state: Optional[Union[str, ProvisioningStates]]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        sku: Sku
        total_iops: Optional[int]
        total_m_bps: Optional[int]
        total_size_ti_b: Optional[int]
        total_volume_size_gi_b: Optional[int]
        volume_group_count: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_properties: Optional[AutoScaleProperties] = ..., 
                availability_zones: Optional[list[str]] = ..., 
                base_size_ti_b: int, 
                extended_capacity_size_ti_b: int, 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                sku: Sku
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.ElasticSanUpdate(_Model):
        properties: Optional[ElasticSanUpdateProperties]
        tags: Optional[dict[str, str]]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ElasticSanUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.ElasticSanUpdateProperties(_Model):
        auto_scale_properties: Optional[AutoScaleProperties]
        base_size_ti_b: Optional[int]
        extended_capacity_size_ti_b: Optional[int]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_properties: Optional[AutoScaleProperties] = ..., 
                base_size_ti_b: Optional[int] = ..., 
                extended_capacity_size_ti_b: Optional[int] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.EncryptionIdentity(_Model):
        encryption_user_assigned_identity: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_user_assigned_identity: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.EncryptionProperties(_Model):
        encryption_identity: Optional[EncryptionIdentity]
        key_vault_properties: Optional[KeyVaultProperties]

        @overload
        def __init__(
                self, 
                *, 
                encryption_identity: Optional[EncryptionIdentity] = ..., 
                key_vault_properties: Optional[KeyVaultProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.EncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ENCRYPTION_AT_REST_WITH_CUSTOMER_MANAGED_KEY = "EncryptionAtRestWithCustomerManagedKey"
        ENCRYPTION_AT_REST_WITH_PLATFORM_KEY = "EncryptionAtRestWithPlatformKey"


    class azure.mgmt.elasticsan.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.elasticsan.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.elasticsan.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.Identity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, IdentityType]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, IdentityType], 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.IdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.elasticsan.models.IscsiTargetInfo(_Model):
        provisioning_state: Optional[Union[str, ProvisioningStates]]
        status: Optional[Union[str, OperationalStatus]]
        target_iqn: Optional[str]
        target_portal_hostname: Optional[str]
        target_portal_port: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                status: Optional[Union[str, OperationalStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.KeyVaultProperties(_Model):
        current_versioned_key_expiration_timestamp: Optional[datetime]
        current_versioned_key_identifier: Optional[str]
        key_name: Optional[str]
        key_vault_uri: Optional[str]
        key_version: Optional[str]
        last_key_rotation_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                key_name: Optional[str] = ..., 
                key_vault_uri: Optional[str] = ..., 
                key_version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.ManagedByInfo(_Model):
        resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.NetworkRuleSet(_Model):
        virtual_network_rules: Optional[list[VirtualNetworkRule]]

        @overload
        def __init__(
                self, 
                *, 
                virtual_network_rules: Optional[list[VirtualNetworkRule]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.Operation(_Model):
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


    class azure.mgmt.elasticsan.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.elasticsan.models.OperationalStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HEALTHY = "Healthy"
        INVALID = "Invalid"
        RUNNING = "Running"
        STOPPED = "Stopped"
        STOPPED_DEALLOCATED_ = "Stopped (deallocated)"
        UNHEALTHY = "Unhealthy"
        UNKNOWN = "Unknown"
        UPDATING = "Updating"


    class azure.mgmt.elasticsan.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.elasticsan.models.PreValidationResponse(_Model):
        validation_status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                validation_status: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.elasticsan.models.PrivateEndpointConnection(ProxyResource):
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: PrivateEndpointConnectionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, ProvisioningStates]]

        @overload
        def __init__(
                self, 
                *, 
                group_ids: Optional[list[str]] = ..., 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        FAILED = "Failed"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.elasticsan.models.PrivateLinkResource(Resource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateLinkResourceListResult(_Model):
        next_link: Optional[str]
        value: list[PrivateLinkResource]

        @overload
        def __init__(
                self, 
                *, 
                value: list[PrivateLinkResource]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                required_zone_names: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.PrivateLinkServiceConnectionState(_Model):
        actions_required: Optional[str]
        description: Optional[str]
        status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]]

        @overload
        def __init__(
                self, 
                *, 
                actions_required: Optional[str] = ..., 
                description: Optional[str] = ..., 
                status: Optional[Union[str, PrivateEndpointServiceConnectionStatus]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.ProvisioningStates(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        INVALID = "Invalid"
        PENDING = "Pending"
        RESTORING = "Restoring"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.elasticsan.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.elasticsan.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.elasticsan.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.elasticsan.models.SKUCapability(_Model):
        name: Optional[str]
        value: Optional[str]


    class azure.mgmt.elasticsan.models.ScaleUpProperties(_Model):
        auto_scale_policy_enforcement: Optional[Union[str, AutoScalePolicyEnforcement]]
        capacity_unit_scale_up_limit_ti_b: Optional[int]
        increase_capacity_unit_by_ti_b: Optional[int]
        unused_size_ti_b: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                auto_scale_policy_enforcement: Optional[Union[str, AutoScalePolicyEnforcement]] = ..., 
                capacity_unit_scale_up_limit_ti_b: Optional[int] = ..., 
                increase_capacity_unit_by_ti_b: Optional[int] = ..., 
                unused_size_ti_b: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.Sku(_Model):
        name: Union[str, SkuName]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.SkuInformation(_Model):
        capabilities: Optional[list[SKUCapability]]
        location_info: Optional[list[SkuLocationInfo]]
        locations: Optional[list[str]]
        name: Union[str, SkuName]
        resource_type: Optional[str]
        tier: Optional[Union[str, SkuTier]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, SkuName], 
                tier: Optional[Union[str, SkuTier]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.SkuLocationInfo(_Model):
        location: Optional[str]
        zones: Optional[list[str]]


    class azure.mgmt.elasticsan.models.SkuName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM_LRS = "Premium_LRS"
        PREMIUM_ZRS = "Premium_ZRS"


    class azure.mgmt.elasticsan.models.SkuTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PREMIUM = "Premium"


    class azure.mgmt.elasticsan.models.Snapshot(ProxyResource):
        id: str
        name: str
        properties: SnapshotProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: SnapshotProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.SnapshotCreationData(_Model):
        source_id: str

        @overload
        def __init__(
                self, 
                *, 
                source_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.SnapshotProperties(_Model):
        creation_data: SnapshotCreationData
        provisioning_state: Optional[Union[str, ProvisioningStates]]
        source_volume_size_gi_b: Optional[int]
        volume_name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_data: SnapshotCreationData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.SourceCreationData(_Model):
        create_source: Optional[Union[str, VolumeCreateOption]]
        source_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                create_source: Optional[Union[str, VolumeCreateOption]] = ..., 
                source_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.StorageTargetType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ISCSI = "Iscsi"
        NONE = "None"


    class azure.mgmt.elasticsan.models.SystemData(_Model):
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


    class azure.mgmt.elasticsan.models.TrackedResource(Resource):
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


    class azure.mgmt.elasticsan.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.elasticsan.models.VirtualNetworkRule(_Model):
        action: Optional[Union[str, Action]]
        virtual_network_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[Union[str, Action]] = ..., 
                virtual_network_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.Volume(ProxyResource):
        id: str
        name: str
        properties: VolumeProperties
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: VolumeProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeCreateOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISK = "Disk"
        DISK_RESTORE_POINT = "DiskRestorePoint"
        DISK_SNAPSHOT = "DiskSnapshot"
        NONE = "None"
        VOLUME_SNAPSHOT = "VolumeSnapshot"


    class azure.mgmt.elasticsan.models.VolumeGroup(ProxyResource):
        id: str
        identity: Optional[Identity]
        name: str
        properties: Optional[VolumeGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[VolumeGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeGroupProperties(_Model):
        encryption: Optional[Union[str, EncryptionType]]
        encryption_properties: Optional[EncryptionProperties]
        enforce_data_integrity_check_for_iscsi: Optional[bool]
        network_acls: Optional[NetworkRuleSet]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        protocol_type: Optional[Union[str, StorageTargetType]]
        provisioning_state: Optional[Union[str, ProvisioningStates]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[Union[str, EncryptionType]] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                enforce_data_integrity_check_for_iscsi: Optional[bool] = ..., 
                network_acls: Optional[NetworkRuleSet] = ..., 
                protocol_type: Optional[Union[str, StorageTargetType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeGroupUpdate(_Model):
        identity: Optional[Identity]
        properties: Optional[VolumeGroupUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[Identity] = ..., 
                properties: Optional[VolumeGroupUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeGroupUpdateProperties(_Model):
        encryption: Optional[Union[str, EncryptionType]]
        encryption_properties: Optional[EncryptionProperties]
        enforce_data_integrity_check_for_iscsi: Optional[bool]
        network_acls: Optional[NetworkRuleSet]
        protocol_type: Optional[Union[str, StorageTargetType]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[Union[str, EncryptionType]] = ..., 
                encryption_properties: Optional[EncryptionProperties] = ..., 
                enforce_data_integrity_check_for_iscsi: Optional[bool] = ..., 
                network_acls: Optional[NetworkRuleSet] = ..., 
                protocol_type: Optional[Union[str, StorageTargetType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeNameList(_Model):
        volume_names: list[str]

        @overload
        def __init__(
                self, 
                *, 
                volume_names: list[str]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeProperties(_Model):
        creation_data: Optional[SourceCreationData]
        managed_by: Optional[ManagedByInfo]
        provisioning_state: Optional[Union[str, ProvisioningStates]]
        size_gi_b: int
        storage_target: Optional[IscsiTargetInfo]
        volume_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                creation_data: Optional[SourceCreationData] = ..., 
                managed_by: Optional[ManagedByInfo] = ..., 
                size_gi_b: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeUpdate(_Model):
        properties: Optional[VolumeUpdateProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[VolumeUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.elasticsan.models.VolumeUpdateProperties(_Model):
        managed_by: Optional[ManagedByInfo]
        size_gi_b: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                managed_by: Optional[ManagedByInfo] = ..., 
                size_gi_b: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.elasticsan.models.XMsDeleteSnapshots(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


    class azure.mgmt.elasticsan.models.XMsForceDelete(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FALSE = "false"
        TRUE = "true"


namespace azure.mgmt.elasticsan.operations

    class azure.mgmt.elasticsan.operations.ElasticSansOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: ElasticSan, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: ElasticSanUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ElasticSan]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> ElasticSan: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ElasticSan]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[ElasticSan]: ...


    class azure.mgmt.elasticsan.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.elasticsan.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.elasticsan.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_elastic_san(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResourceListResult: ...


    class azure.mgmt.elasticsan.operations.SkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SkuInformation]: ...


    class azure.mgmt.elasticsan.operations.VolumeGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeGroupUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[VolumeGroup]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> VolumeGroup: ...

        @distributed_trace
        def list_by_elastic_san(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                **kwargs: Any
            ) -> ItemPaged[VolumeGroup]: ...


    class azure.mgmt.elasticsan.operations.VolumeSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: Snapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Snapshot]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                snapshot_name: str, 
                **kwargs: Any
            ) -> Snapshot: ...

        @distributed_trace
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[Snapshot]: ...


    class azure.mgmt.elasticsan.operations.VolumesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: Volume, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                *, 
                x_ms_delete_snapshots: Optional[Union[str, XMsDeleteSnapshots]] = ..., 
                x_ms_force_delete: Optional[Union[str, XMsForceDelete]] = ..., 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: VolumeNameList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_pre_backup(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: DiskSnapshotList, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_pre_restore(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PreValidationResponse]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: VolumeUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Volume]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                volume_name: str, 
                **kwargs: Any
            ) -> Volume: ...

        @distributed_trace
        def list_by_volume_group(
                self, 
                resource_group_name: str, 
                elastic_san_name: str, 
                volume_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Volume]: ...


```