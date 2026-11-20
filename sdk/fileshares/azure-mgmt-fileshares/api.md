```py
namespace azure.mgmt.fileshares

    class azure.mgmt.fileshares.FileSharesMgmtClient: implements ContextManager 
        file_share_snapshots: FileShareSnapshotsOperations
        file_shares: FileSharesOperations
        informational_operations: InformationalOperationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.fileshares.aio

    class azure.mgmt.fileshares.aio.FileSharesMgmtClient: implements AsyncContextManager 
        file_share_snapshots: FileShareSnapshotsOperations
        file_shares: FileSharesOperations
        informational_operations: InformationalOperationsOperations
        operations: Operations
        private_endpoint_connections: PrivateEndpointConnectionsOperations
        private_link_resources: PrivateLinkResourcesOperations

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


namespace azure.mgmt.fileshares.aio.operations

    class azure.mgmt.fileshares.aio.operations.FileShareSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: FileShareSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @overload
        async def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: FileShareSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @overload
        async def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @distributed_trace_async
        async def begin_delete_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: FileShareSnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @overload
        async def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: FileShareSnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @overload
        async def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShareSnapshot]: ...

        @distributed_trace_async
        async def get_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FileShareSnapshot: ...

        @distributed_trace
        def list_by_file_share(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FileShareSnapshot]: ...


    class azure.mgmt.fileshares.aio.operations.FileSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: FileShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: FileShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileShare]: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2026-09-01', params_added_on={'2026-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-09-01'])
        async def get_redundancy_conversion_status(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> RedundancyConversionStatusResponse: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FileShare]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FileShare]: ...

        @overload
        async def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: StartRedundancyConversionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: StartRedundancyConversionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        async def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.fileshares.aio.operations.InformationalOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def get_limits(
                self, 
                location: str, 
                body: Optional[FileShareLimitsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        async def get_limits(
                self, 
                location: str, 
                body: Optional[FileShareLimitsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        async def get_limits(
                self, 
                location: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        async def get_provisioning_recommendation(
                self, 
                location: str, 
                body: FileShareProvisioningRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @overload
        async def get_provisioning_recommendation(
                self, 
                location: str, 
                body: FileShareProvisioningRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @overload
        async def get_provisioning_recommendation(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @distributed_trace_async
        async def get_usage_data(
                self, 
                location: str, 
                **kwargs: Any
            ) -> FileShareUsageDataResponse: ...


    class azure.mgmt.fileshares.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.fileshares.aio.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[PrivateEndpointConnection]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_endpoint_connection_name']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        async def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def list_by_file_share(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.fileshares.aio.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        async def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.fileshares.models

    class azure.mgmt.fileshares.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.fileshares.models.CheckNameAvailabilityReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.fileshares.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.CheckNameAvailabilityResponse(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, CheckNameAvailabilityReason]]

        @overload
        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, CheckNameAvailabilityReason]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.fileshares.models.CustomerManagedKeyEncryption(_Model):
        key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity]
        key_encryption_key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key_encryption_key_identity: Optional[KeyEncryptionKeyIdentity] = ..., 
                key_encryption_key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.EncryptionInTransitRequired(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.fileshares.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.fileshares.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.fileshares.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShare(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[FileShareProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[FileShareProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareEncryption(_Model):
        auto_key_rotation_error: Optional[ErrorDetail]
        current_key_encryption_key_url: Optional[str]
        customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption]
        infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]]
        last_key_rotation_timestamp: Optional[datetime]

        @overload
        def __init__(
                self, 
                *, 
                customer_managed_key_encryption: Optional[CustomerManagedKeyEncryption] = ..., 
                infrastructure_encryption: Optional[Union[str, InfrastructureEncryption]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareLimits(_Model):
        max_file_share_private_endpoint_connections: int
        max_file_share_snapshots: int
        max_file_share_subnets: int
        max_file_shares: int
        max_provisioned_io_per_sec: int
        max_provisioned_storage_gi_b: int
        max_provisioned_throughput_mi_b_per_sec: int
        min_provisioned_io_per_sec: int
        min_provisioned_storage_gi_b: int
        min_provisioned_throughput_mi_b_per_sec: int

        @overload
        def __init__(
                self, 
                *, 
                max_file_share_private_endpoint_connections: int, 
                max_file_share_snapshots: int, 
                max_file_share_subnets: int, 
                max_file_shares: int, 
                max_provisioned_io_per_sec: int, 
                max_provisioned_storage_gi_b: int, 
                max_provisioned_throughput_mi_b_per_sec: int, 
                min_provisioned_io_per_sec: int, 
                min_provisioned_storage_gi_b: int, 
                min_provisioned_throughput_mi_b_per_sec: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareLimitsOutput(_Model):
        limits: FileShareLimits
        provisioning_constants: FileShareProvisioningConstants

        @overload
        def __init__(
                self, 
                *, 
                limits: FileShareLimits, 
                provisioning_constants: FileShareProvisioningConstants
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareLimitsRequest(_Model):
        properties: FileShareOfferInput

        @overload
        def __init__(
                self, 
                *, 
                properties: FileShareOfferInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareLimitsResponse(_Model):
        properties: FileShareLimitsOutput

        @overload
        def __init__(
                self, 
                *, 
                properties: FileShareLimitsOutput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareOfferInput(_Model):
        media_tier: Optional[Union[str, MediaTier]]
        protocol: Optional[Union[str, Protocol]]
        scale_mode: Optional[Union[str, ScaleMode]]

        @overload
        def __init__(
                self, 
                *, 
                media_tier: Optional[Union[str, MediaTier]] = ..., 
                protocol: Optional[Union[str, Protocol]] = ..., 
                scale_mode: Optional[Union[str, ScaleMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProperties(_Model):
        encryption: Optional[FileShareEncryption]
        host_name: Optional[str]
        included_burst_io_per_sec: Optional[int]
        max_burst_io_per_sec_credits: Optional[int]
        media_tier: Optional[Union[str, MediaTier]]
        migration_state: Optional[MigrationState]
        mount_name: Optional[str]
        nfs_protocol_properties: Optional[NfsProtocolProperties]
        private_endpoint_connections: Optional[list[PrivateEndpointConnection]]
        protocol: Optional[Union[str, Protocol]]
        provisioned_io_per_sec: Optional[int]
        provisioned_io_per_sec_next_allowed_downgrade: Optional[datetime]
        provisioned_storage_gi_b: Optional[int]
        provisioned_storage_next_allowed_downgrade: Optional[datetime]
        provisioned_throughput_mi_b_per_sec: Optional[int]
        provisioned_throughput_next_allowed_downgrade: Optional[datetime]
        provisioning_state: Optional[Union[str, FileShareProvisioningState]]
        public_access_properties: Optional[PublicAccessProperties]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]
        redundancy: Optional[Union[str, Redundancy]]
        scale_mode: Optional[Union[str, ScaleMode]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[FileShareEncryption] = ..., 
                media_tier: Optional[Union[str, MediaTier]] = ..., 
                mount_name: Optional[str] = ..., 
                nfs_protocol_properties: Optional[NfsProtocolProperties] = ..., 
                protocol: Optional[Union[str, Protocol]] = ..., 
                provisioned_io_per_sec: Optional[int] = ..., 
                provisioned_storage_gi_b: Optional[int] = ..., 
                provisioned_throughput_mi_b_per_sec: Optional[int] = ..., 
                public_access_properties: Optional[PublicAccessProperties] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ..., 
                redundancy: Optional[Union[str, Redundancy]] = ..., 
                scale_mode: Optional[Union[str, ScaleMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningConstants(_Model):
        base_io_per_sec: int
        base_throughput_mi_b_per_sec: int
        guardrail_io_per_sec_scalar: float
        guardrail_throughput_scalar: float
        scalar_io_per_sec: float
        scalar_throughput_mi_b_per_sec: float

        @overload
        def __init__(
                self, 
                *, 
                base_io_per_sec: int, 
                base_throughput_mi_b_per_sec: int, 
                guardrail_io_per_sec_scalar: float, 
                guardrail_throughput_scalar: float, 
                scalar_io_per_sec: float, 
                scalar_throughput_mi_b_per_sec: float
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningRecommendationInput(_Model):
        media_tier: Optional[Union[str, MediaTier]]
        protocol: Optional[Union[str, Protocol]]
        provisioned_storage_gi_b: int
        scale_mode: Optional[Union[str, ScaleMode]]

        @overload
        def __init__(
                self, 
                *, 
                media_tier: Optional[Union[str, MediaTier]] = ..., 
                protocol: Optional[Union[str, Protocol]] = ..., 
                provisioned_storage_gi_b: int, 
                scale_mode: Optional[Union[str, ScaleMode]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningRecommendationOutput(_Model):
        available_redundancy_options: list[Union[str, Redundancy]]
        provisioned_io_per_sec: int
        provisioned_throughput_mi_b_per_sec: int

        @overload
        def __init__(
                self, 
                *, 
                available_redundancy_options: list[Union[str, Redundancy]], 
                provisioned_io_per_sec: int, 
                provisioned_throughput_mi_b_per_sec: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningRecommendationRequest(_Model):
        properties: FileShareProvisioningRecommendationInput

        @overload
        def __init__(
                self, 
                *, 
                properties: FileShareProvisioningRecommendationInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningRecommendationResponse(_Model):
        properties: FileShareProvisioningRecommendationOutput

        @overload
        def __init__(
                self, 
                *, 
                properties: FileShareProvisioningRecommendationOutput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATED = "Created"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        PATCHING = "Patching"
        POSTING = "Posting"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        TRANSIENT_FAILURE = "TransientFailure"
        UPDATING = "Updating"


    class azure.mgmt.fileshares.models.FileShareSnapshot(ProxyResource):
        id: str
        name: str
        properties: Optional[FileShareSnapshotProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileShareSnapshotProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareSnapshotProperties(_Model):
        initiator_id: Optional[str]
        metadata: Optional[dict[str, str]]
        snapshot_time: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                initiator_id: Optional[str] = ..., 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareSnapshotUpdate(_Model):
        properties: Optional[FileShareSnapshotUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[FileShareSnapshotUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareSnapshotUpdateProperties(_Model):
        metadata: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareUpdate(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[FileShareUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[FileShareUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareUpdateProperties(_Model):
        encryption: Optional[FileShareEncryption]
        nfs_protocol_properties: Optional[NfsProtocolProperties]
        provisioned_io_per_sec: Optional[int]
        provisioned_storage_gi_b: Optional[int]
        provisioned_throughput_mi_b_per_sec: Optional[int]
        public_access_properties: Optional[PublicAccessProperties]
        public_network_access: Optional[Union[str, PublicNetworkAccess]]

        @overload
        def __init__(
                self, 
                *, 
                encryption: Optional[FileShareEncryption] = ..., 
                nfs_protocol_properties: Optional[NfsProtocolProperties] = ..., 
                provisioned_io_per_sec: Optional[int] = ..., 
                provisioned_storage_gi_b: Optional[int] = ..., 
                provisioned_throughput_mi_b_per_sec: Optional[int] = ..., 
                public_access_properties: Optional[PublicAccessProperties] = ..., 
                public_network_access: Optional[Union[str, PublicNetworkAccess]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareUsageDataOutput(_Model):
        live_shares: LiveSharesUsageData

        @overload
        def __init__(
                self, 
                *, 
                live_shares: LiveSharesUsageData
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.FileShareUsageDataResponse(_Model):
        properties: FileShareUsageDataOutput

        @overload
        def __init__(
                self, 
                *, 
                properties: FileShareUsageDataOutput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.InfrastructureEncryption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "disabled"
        ENABLED = "enabled"


    class azure.mgmt.fileshares.models.KeyEncryptionKeyIdentity(_Model):
        delegated_identity_client_id: Optional[str]
        federated_client_id: Optional[str]
        identity_type: Optional[Union[str, KeyEncryptionKeyIdentityType]]
        user_assigned_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                delegated_identity_client_id: Optional[str] = ..., 
                federated_client_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, KeyEncryptionKeyIdentityType]] = ..., 
                user_assigned_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.KeyEncryptionKeyIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELEGATED_RESOURCE_IDENTITY = "delegatedResourceIdentity"
        SYSTEM_ASSIGNED_IDENTITY = "systemAssignedIdentity"
        USER_ASSIGNED_IDENTITY = "userAssignedIdentity"


    class azure.mgmt.fileshares.models.LiveSharesUsageData(_Model):
        file_share_count: int

        @overload
        def __init__(
                self, 
                *, 
                file_share_count: int
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.fileshares.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.fileshares.models.MediaTier(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        HDD = "HDD"
        SSD = "SSD"


    class azure.mgmt.fileshares.models.MigrationState(_Model):
        redundancy_conversion_in_progress: bool


    class azure.mgmt.fileshares.models.NfsProtocolProperties(_Model):
        encryption_in_transit_required: Optional[Union[str, EncryptionInTransitRequired]]
        root_squash: Optional[Union[str, ShareRootSquash]]

        @overload
        def __init__(
                self, 
                *, 
                encryption_in_transit_required: Optional[Union[str, EncryptionInTransitRequired]] = ..., 
                root_squash: Optional[Union[str, ShareRootSquash]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.Operation(_Model):
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


    class azure.mgmt.fileshares.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.fileshares.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.fileshares.models.PrivateEndpoint(_Model):
        id: Optional[str]


    class azure.mgmt.fileshares.models.PrivateEndpointConnection(Resource):
        id: str
        name: str
        properties: Optional[PrivateEndpointConnectionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateEndpointConnectionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.PrivateEndpointConnectionProperties(_Model):
        group_ids: Optional[list[str]]
        private_endpoint: Optional[PrivateEndpoint]
        private_link_service_connection_state: PrivateLinkServiceConnectionState
        provisioning_state: Optional[Union[str, PrivateEndpointConnectionProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                private_endpoint: Optional[PrivateEndpoint] = ..., 
                private_link_service_connection_state: PrivateLinkServiceConnectionState
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.PrivateEndpointConnectionProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.fileshares.models.PrivateEndpointServiceConnectionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.fileshares.models.PrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[PrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[PrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.PrivateLinkResourceProperties(_Model):
        group_id: Optional[str]
        required_members: Optional[list[str]]
        required_zone_names: Optional[list[str]]


    class azure.mgmt.fileshares.models.PrivateLinkServiceConnectionState(_Model):
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


    class azure.mgmt.fileshares.models.Protocol(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NFS = "NFS"


    class azure.mgmt.fileshares.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.fileshares.models.PublicAccessProperties(_Model):
        allowed_subnets: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                allowed_subnets: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.PublicNetworkAccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DISABLED = "Disabled"
        ENABLED = "Enabled"


    class azure.mgmt.fileshares.models.Redundancy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCAL = "Local"
        ZONE = "Zone"


    class azure.mgmt.fileshares.models.RedundancyConversionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETE = "Complete"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        SUBMITTED_FOR_CONVERSION = "SubmittedForConversion"


    class azure.mgmt.fileshares.models.RedundancyConversionStatusOutput(_Model):
        conversion_failed_detailed_reason: Optional[str]
        conversion_failed_reason: Optional[str]
        conversion_status: Union[str, RedundancyConversionStatus]
        target_redundancy: Union[str, Redundancy]


    class azure.mgmt.fileshares.models.RedundancyConversionStatusResponse(_Model):
        properties: RedundancyConversionStatusOutput

        @overload
        def __init__(
                self, 
                *, 
                properties: RedundancyConversionStatusOutput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.fileshares.models.ScaleMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPATIBILITY = "Compatibility"
        SCALE = "Scale"


    class azure.mgmt.fileshares.models.ShareRootSquash(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALL_SQUASH = "AllSquash"
        NO_ROOT_SQUASH = "NoRootSquash"
        ROOT_SQUASH = "RootSquash"


    class azure.mgmt.fileshares.models.StartRedundancyConversionInput(_Model):
        target_redundancy: Union[str, Redundancy]

        @overload
        def __init__(
                self, 
                *, 
                target_redundancy: Union[str, Redundancy]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.StartRedundancyConversionRequest(_Model):
        properties: StartRedundancyConversionInput

        @overload
        def __init__(
                self, 
                *, 
                properties: StartRedundancyConversionInput
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.fileshares.models.SystemData(_Model):
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


    class azure.mgmt.fileshares.models.TrackedResource(Resource):
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


    class azure.mgmt.fileshares.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.fileshares.operations

    class azure.mgmt.fileshares.operations.FileShareSnapshotsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: FileShareSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @overload
        def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: FileShareSnapshot, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @overload
        def begin_create_or_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @distributed_trace
        def begin_delete_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: FileShareSnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @overload
        def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: FileShareSnapshotUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @overload
        def begin_update_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShareSnapshot]: ...

        @distributed_trace
        def get_file_share_snapshot(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                name: str, 
                **kwargs: Any
            ) -> FileShareSnapshot: ...

        @distributed_trace
        def list_by_file_share(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FileShareSnapshot]: ...


    class azure.mgmt.fileshares.operations.FileSharesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: FileShare, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: FileShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: FileShareUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileShare]: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResponse: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> FileShare: ...

        @distributed_trace
        @api_version_validation(method_added_on='2026-09-01', params_added_on={'2026-09-01': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2026-09-01'])
        def get_redundancy_conversion_status(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> RedundancyConversionStatusResponse: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FileShare]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FileShare]: ...

        @overload
        def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: StartRedundancyConversionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: StartRedundancyConversionRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...

        @overload
        def start_redundancy_conversion(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> None: ...


    class azure.mgmt.fileshares.operations.InformationalOperationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def get_limits(
                self, 
                location: str, 
                body: Optional[FileShareLimitsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        def get_limits(
                self, 
                location: str, 
                body: Optional[FileShareLimitsRequest] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        def get_limits(
                self, 
                location: str, 
                body: Optional[IO[bytes]] = None, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareLimitsResponse: ...

        @overload
        def get_provisioning_recommendation(
                self, 
                location: str, 
                body: FileShareProvisioningRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @overload
        def get_provisioning_recommendation(
                self, 
                location: str, 
                body: FileShareProvisioningRecommendationRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @overload
        def get_provisioning_recommendation(
                self, 
                location: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileShareProvisioningRecommendationResponse: ...

        @distributed_trace
        def get_usage_data(
                self, 
                location: str, 
                **kwargs: Any
            ) -> FileShareUsageDataResponse: ...


    class azure.mgmt.fileshares.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.fileshares.operations.PrivateEndpointConnectionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: PrivateEndpointConnection, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[PrivateEndpointConnection]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_endpoint_connection_name']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def begin_delete(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_endpoint_connection_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_endpoint_connection_name: str, 
                **kwargs: Any
            ) -> PrivateEndpointConnection: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def list_by_file_share(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateEndpointConnection]: ...


    class azure.mgmt.fileshares.operations.PrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'private_link_resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def get(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                private_link_resource_name: str, 
                **kwargs: Any
            ) -> PrivateLinkResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2025-09-01-preview', params_added_on={'2025-09-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'resource_name', 'accept']}, api_versions_list=['2025-09-01-preview', '2026-06-01', '2026-09-01'])
        def list(
                self, 
                resource_group_name: str, 
                resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[PrivateLinkResource]: ...


namespace azure.mgmt.fileshares.types

    class azure.mgmt.fileshares.types.CheckNameAvailabilityRequest(TypedDict, total=False):
        key "name": str
        key "type": str
        name: str
        type: str


    class azure.mgmt.fileshares.types.CustomerManagedKeyEncryption(TypedDict, total=False):
        key "keyEncryptionKeyIdentity": ForwardRef('KeyEncryptionKeyIdentity', module='types')
        key "keyEncryptionKeyUrl": str
        keyEncryptionKeyIdentity: KeyEncryptionKeyIdentity
        keyEncryptionKeyUrl: str


    class azure.mgmt.fileshares.types.ErrorAdditionalInfo(TypedDict, total=False):
        key "info": Any
        key "type": str
        info: Any
        type: str


    class azure.mgmt.fileshares.types.ErrorDetail(TypedDict, total=False):
        key "code": str
        key "message": str
        key "target": str
        additionalInfo: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str


    class azure.mgmt.fileshares.types.FileShare(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('FileShareProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: FileShareProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.fileshares.types.FileShareEncryption(TypedDict, total=False):
        key "autoKeyRotationError": ForwardRef('ErrorDetail', module='types')
        key "currentKeyEncryptionKeyUrl": str
        key "customerManagedKeyEncryption": ForwardRef('CustomerManagedKeyEncryption', module='types')
        key "infrastructureEncryption": Union[str, InfrastructureEncryption]
        key "lastKeyRotationTimestamp": str
        autoKeyRotationError: ErrorDetail
        currentKeyEncryptionKeyUrl: str
        customerManagedKeyEncryption: CustomerManagedKeyEncryption
        infrastructureEncryption: Union[str, InfrastructureEncryption]
        lastKeyRotationTimestamp: str


    class azure.mgmt.fileshares.types.FileShareLimitsRequest(TypedDict, total=False):
        key "properties": Required[FileShareOfferInput]
        properties: FileShareOfferInput


    class azure.mgmt.fileshares.types.FileShareOfferInput(TypedDict, total=False):
        key "mediaTier": Union[str, MediaTier]
        key "protocol": Union[str, Protocol]
        key "scaleMode": Union[str, ScaleMode]
        mediaTier: Union[str, MediaTier]
        protocol: Union[str, Protocol]
        scaleMode: Union[str, ScaleMode]


    class azure.mgmt.fileshares.types.FileShareProperties(TypedDict, total=False):
        key "encryption": ForwardRef('FileShareEncryption', module='types')
        key "hostName": str
        key "includedBurstIOPerSec": int
        key "maxBurstIOPerSecCredits": int
        key "mediaTier": Union[str, MediaTier]
        key "migrationState": ForwardRef('MigrationState', module='types')
        key "mountName": str
        key "nfsProtocolProperties": ForwardRef('NfsProtocolProperties', module='types')
        key "protocol": Union[str, Protocol]
        key "provisionedIOPerSec": int
        key "provisionedIOPerSecNextAllowedDowngrade": str
        key "provisionedStorageGiB": int
        key "provisionedStorageNextAllowedDowngrade": str
        key "provisionedThroughputMiBPerSec": int
        key "provisionedThroughputNextAllowedDowngrade": str
        key "provisioningState": Union[str, FileShareProvisioningState]
        key "publicAccessProperties": ForwardRef('PublicAccessProperties', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        key "redundancy": Union[str, Redundancy]
        key "scaleMode": Union[str, ScaleMode]
        encryption: FileShareEncryption
        hostName: str
        includedBurstIOPerSec: int
        maxBurstIOPerSecCredits: int
        mediaTier: Union[str, MediaTier]
        migrationState: MigrationState
        mountName: str
        nfsProtocolProperties: NfsProtocolProperties
        privateEndpointConnections: list[PrivateEndpointConnection]
        protocol: Union[str, Protocol]
        provisionedIOPerSec: int
        provisionedIOPerSecNextAllowedDowngrade: str
        provisionedStorageGiB: int
        provisionedStorageNextAllowedDowngrade: str
        provisionedThroughputMiBPerSec: int
        provisionedThroughputNextAllowedDowngrade: str
        provisioningState: Union[str, FileShareProvisioningState]
        publicAccessProperties: PublicAccessProperties
        publicNetworkAccess: Union[str, PublicNetworkAccess]
        redundancy: Union[str, Redundancy]
        scaleMode: Union[str, ScaleMode]


    class azure.mgmt.fileshares.types.FileShareProvisioningRecommendationInput(TypedDict, total=False):
        key "mediaTier": Union[str, MediaTier]
        key "protocol": Union[str, Protocol]
        key "provisionedStorageGiB": Required[int]
        key "scaleMode": Union[str, ScaleMode]
        mediaTier: Union[str, MediaTier]
        protocol: Union[str, Protocol]
        provisionedStorageGiB: int
        scaleMode: Union[str, ScaleMode]


    class azure.mgmt.fileshares.types.FileShareProvisioningRecommendationRequest(TypedDict, total=False):
        key "properties": Required[FileShareProvisioningRecommendationInput]
        properties: FileShareProvisioningRecommendationInput


    class azure.mgmt.fileshares.types.FileShareSnapshot(ProxyResource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('FileShareSnapshotProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: FileShareSnapshotProperties
        systemData: SystemData
        type: str


    class azure.mgmt.fileshares.types.FileShareSnapshotProperties(TypedDict, total=False):
        key "initiatorId": str
        key "snapshotTime": str
        initiatorId: str
        metadata: dict[str, str]
        snapshotTime: str


    class azure.mgmt.fileshares.types.FileShareSnapshotUpdate(TypedDict, total=False):
        key "properties": ForwardRef('FileShareSnapshotUpdateProperties', module='types')
        properties: FileShareSnapshotUpdateProperties


    class azure.mgmt.fileshares.types.FileShareSnapshotUpdateProperties(TypedDict, total=False):
        metadata: dict[str, str]


    class azure.mgmt.fileshares.types.FileShareUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "properties": ForwardRef('FileShareUpdateProperties', module='types')
        identity: ManagedServiceIdentity
        properties: FileShareUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.fileshares.types.FileShareUpdateProperties(TypedDict, total=False):
        key "encryption": ForwardRef('FileShareEncryption', module='types')
        key "nfsProtocolProperties": ForwardRef('NfsProtocolProperties', module='types')
        key "provisionedIOPerSec": int
        key "provisionedStorageGiB": int
        key "provisionedThroughputMiBPerSec": int
        key "publicAccessProperties": ForwardRef('PublicAccessProperties', module='types')
        key "publicNetworkAccess": Union[str, PublicNetworkAccess]
        encryption: FileShareEncryption
        nfsProtocolProperties: NfsProtocolProperties
        provisionedIOPerSec: int
        provisionedStorageGiB: int
        provisionedThroughputMiBPerSec: int
        publicAccessProperties: PublicAccessProperties
        publicNetworkAccess: Union[str, PublicNetworkAccess]


    class azure.mgmt.fileshares.types.KeyEncryptionKeyIdentity(TypedDict, total=False):
        key "delegatedIdentityClientId": str
        key "federatedClientId": str
        key "identityType": Union[str, KeyEncryptionKeyIdentityType]
        key "userAssignedIdentityResourceId": str
        delegatedIdentityClientId: str
        federatedClientId: str
        identityType: Union[str, KeyEncryptionKeyIdentityType]
        userAssignedIdentityResourceId: str


    class azure.mgmt.fileshares.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.fileshares.types.MigrationState(TypedDict, total=False):
        key "redundancyConversionInProgress": Required[bool]
        redundancyConversionInProgress: bool


    class azure.mgmt.fileshares.types.NfsProtocolProperties(TypedDict, total=False):
        key "encryptionInTransitRequired": Union[str, EncryptionInTransitRequired]
        key "rootSquash": Union[str, ShareRootSquash]
        encryptionInTransitRequired: Union[str, EncryptionInTransitRequired]
        rootSquash: Union[str, ShareRootSquash]


    class azure.mgmt.fileshares.types.PrivateEndpoint(TypedDict, total=False):
        key "id": str
        id: str


    class azure.mgmt.fileshares.types.PrivateEndpointConnection(Resource):
        key "id": str
        key "name": str
        key "properties": ForwardRef('PrivateEndpointConnectionProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        properties: PrivateEndpointConnectionProperties
        systemData: SystemData
        type: str


    class azure.mgmt.fileshares.types.PrivateEndpointConnectionProperties(TypedDict, total=False):
        key "privateEndpoint": ForwardRef('PrivateEndpoint', module='types')
        key "privateLinkServiceConnectionState": Required[PrivateLinkServiceConnectionState]
        key "provisioningState": Union[str, PrivateEndpointConnectionProvisioningState]
        groupIds: list[str]
        privateEndpoint: PrivateEndpoint
        privateLinkServiceConnectionState: PrivateLinkServiceConnectionState
        provisioningState: Union[str, PrivateEndpointConnectionProvisioningState]


    class azure.mgmt.fileshares.types.PrivateLinkServiceConnectionState(TypedDict, total=False):
        key "actionsRequired": str
        key "description": str
        key "status": Union[str, PrivateEndpointServiceConnectionStatus]
        actionsRequired: str
        description: str
        status: Union[str, PrivateEndpointServiceConnectionStatus]


    class azure.mgmt.fileshares.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.fileshares.types.PublicAccessProperties(TypedDict, total=False):
        allowedSubnets: list[str]


    class azure.mgmt.fileshares.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.fileshares.types.StartRedundancyConversionInput(TypedDict, total=False):
        key "targetRedundancy": Required[Union[str, Redundancy]]
        targetRedundancy: Union[str, Redundancy]


    class azure.mgmt.fileshares.types.StartRedundancyConversionRequest(TypedDict, total=False):
        key "properties": Required[StartRedundancyConversionInput]
        properties: StartRedundancyConversionInput


    class azure.mgmt.fileshares.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.fileshares.types.TrackedResource(Resource):
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


    class azure.mgmt.fileshares.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```