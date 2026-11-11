```py
namespace azure.mgmt.appnetwork

    class azure.mgmt.appnetwork.AppNetworkMgmtClient: implements ContextManager 
        app_link_members: AppLinkMembersOperations
        app_links: AppLinksOperations
        available_versions: AvailableVersionsOperations
        operations: Operations
        upgrade_histories: UpgradeHistoriesOperations

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


namespace azure.mgmt.appnetwork.aio

    class azure.mgmt.appnetwork.aio.AppNetworkMgmtClient: implements AsyncContextManager 
        app_link_members: AppLinkMembersOperations
        app_links: AppLinksOperations
        available_versions: AvailableVersionsOperations
        operations: Operations
        upgrade_histories: UpgradeHistoriesOperations

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


namespace azure.mgmt.appnetwork.aio.operations

    class azure.mgmt.appnetwork.aio.operations.AppLinkMembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: AppLinkMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: AppLinkMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: AppLinkMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: AppLinkMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLinkMember]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> AppLinkMember: ...

        @distributed_trace
        def list_by_app_link(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AppLinkMember]: ...


    class azure.mgmt.appnetwork.aio.operations.AppLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: AppLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: AppLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: AppLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: AppLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[AppLink]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> AppLink: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AppLink]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[AppLink]: ...


    class azure.mgmt.appnetwork.aio.operations.AvailableVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                *, 
                kubernetes_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailableVersion]: ...


    class azure.mgmt.appnetwork.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.appnetwork.aio.operations.UpgradeHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_app_link_member(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[UpgradeHistory]: ...


namespace azure.mgmt.appnetwork.models

    class azure.mgmt.appnetwork.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.appnetwork.models.AppLink(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[AppLinkProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[AppLinkProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AppLinkMember(TrackedResource):
        id: str
        location: str
        name: str
        properties: Optional[AppLinkMemberProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                properties: Optional[AppLinkMemberProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AppLinkMemberProperties(_Model):
        cluster_type: Optional[Union[str, ClusterType]]
        connectivity_profile: Optional[ConnectivityProfile]
        metadata: Metadata
        observability_profile: Optional[ObservabilityProfile]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        upgrade_profile: Optional[UpgradeProfile]

        @overload
        def __init__(
                self, 
                *, 
                cluster_type: Optional[Union[str, ClusterType]] = ..., 
                connectivity_profile: Optional[ConnectivityProfile] = ..., 
                metadata: Metadata, 
                observability_profile: Optional[ObservabilityProfile] = ..., 
                upgrade_profile: Optional[UpgradeProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AppLinkMemberUpdate(_Model):
        properties: Optional[AppLinkMemberUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AppLinkMemberUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AppLinkMemberUpdateProperties(_Model):
        connectivity_profile: Optional[ConnectivityProfileUpdate]
        upgrade_profile: Optional[UpgradeProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                connectivity_profile: Optional[ConnectivityProfileUpdate] = ..., 
                upgrade_profile: Optional[UpgradeProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AppLinkProperties(_Model):
        provisioning_state: Optional[Union[str, ProvisioningState]]


    class azure.mgmt.appnetwork.models.AppLinkUpdate(_Model):
        identity: Optional[ManagedServiceIdentityUpdate]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityUpdate] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AvailableVersion(ProxyResource):
        id: str
        name: str
        properties: Optional[AvailableVersionProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AvailableVersionProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.AvailableVersionProperties(_Model):
        fully_managed_versions: FullyManagedVersions
        kubernetes_version: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        self_managed_versions: SelfManagedVersions

        @overload
        def __init__(
                self, 
                *, 
                fully_managed_versions: FullyManagedVersions, 
                kubernetes_version: str, 
                self_managed_versions: SelfManagedVersions
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.ClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AKS = "AKS"


    class azure.mgmt.appnetwork.models.ConnectivityProfile(_Model):
        east_west_gateway: Optional[EastWestGatewayProfile]
        network: Optional[str]
        private_connect: Optional[PrivateConnectProfile]

        @overload
        def __init__(
                self, 
                *, 
                east_west_gateway: Optional[EastWestGatewayProfile] = ..., 
                network: Optional[str] = ..., 
                private_connect: Optional[PrivateConnectProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.ConnectivityProfileUpdate(_Model):
        east_west_gateway: Optional[EastWestGatewayProfileUpdate]
        network: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                east_west_gateway: Optional[EastWestGatewayProfileUpdate] = ..., 
                network: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.appnetwork.models.EastWestGatewayProfile(_Model):
        visibility: Union[str, EastWestGatewayVisibility]

        @overload
        def __init__(
                self, 
                *, 
                visibility: Union[str, EastWestGatewayVisibility]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.EastWestGatewayProfileUpdate(_Model):
        visibility: Optional[Union[str, EastWestGatewayVisibility]]

        @overload
        def __init__(
                self, 
                *, 
                visibility: Optional[Union[str, EastWestGatewayVisibility]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.EastWestGatewayVisibility(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTERNAL = "External"
        INTERNAL = "Internal"


    class azure.mgmt.appnetwork.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.appnetwork.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.appnetwork.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.FullyManagedUpgradeProfile(_Model):
        release_channel: Union[str, UpgradeReleaseChannel]

        @overload
        def __init__(
                self, 
                *, 
                release_channel: Union[str, UpgradeReleaseChannel]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.FullyManagedUpgradeProfileUpdate(_Model):
        release_channel: Optional[Union[str, UpgradeReleaseChannel]]

        @overload
        def __init__(
                self, 
                *, 
                release_channel: Optional[Union[str, UpgradeReleaseChannel]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.FullyManagedVersions(_Model):
        release_channels: list[ReleaseChannelInfo]

        @overload
        def __init__(
                self, 
                *, 
                release_channels: list[ReleaseChannelInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.appnetwork.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.appnetwork.models.ManagedServiceIdentityUpdate(_Model):
        type: Optional[Union[str, ManagedServiceIdentityType]]
        user_assigned_identities: Optional[dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ManagedServiceIdentityType]] = ..., 
                user_assigned_identities: Optional[dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.Metadata(_Model):
        resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.MetricsProfile(_Model):
        metrics_endpoint: Optional[str]


    class azure.mgmt.appnetwork.models.ObservabilityProfile(_Model):
        metrics: Optional[MetricsProfile]

        @overload
        def __init__(
                self, 
                *, 
                metrics: Optional[MetricsProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.Operation(_Model):
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


    class azure.mgmt.appnetwork.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.appnetwork.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.appnetwork.models.PrivateConnectProfile(_Model):
        subnet_resource_id: str

        @overload
        def __init__(
                self, 
                *, 
                subnet_resource_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.appnetwork.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.appnetwork.models.ReleaseChannelInfo(_Model):
        release_channel: str
        version: str

        @overload
        def __init__(
                self, 
                *, 
                release_channel: str, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.appnetwork.models.SelfManagedUpgradeProfile(_Model):
        version: str

        @overload
        def __init__(
                self, 
                *, 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.SelfManagedUpgradeProfileUpdate(_Model):
        version: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                version: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.SelfManagedVersions(_Model):
        versions: list[VersionInfo]

        @overload
        def __init__(
                self, 
                *, 
                versions: list[VersionInfo]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.SystemData(_Model):
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


    class azure.mgmt.appnetwork.models.TrackedResource(Resource):
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


    class azure.mgmt.appnetwork.models.UpgradeHistory(ProxyResource):
        id: str
        name: str
        properties: Optional[UpgradeHistoryProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[UpgradeHistoryProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.UpgradeHistoryProperties(_Model):
        end_timestamp: Optional[datetime]
        from_version: str
        initiated_by: str
        provisioning_state: Optional[Union[str, ProvisioningState]]
        start_timestamp: datetime
        to_version: str

        @overload
        def __init__(
                self, 
                *, 
                end_timestamp: Optional[datetime] = ..., 
                from_version: str, 
                initiated_by: str, 
                start_timestamp: datetime, 
                to_version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.UpgradeMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FULLY_MANAGED = "FullyManaged"
        SELF_MANAGED = "SelfManaged"


    class azure.mgmt.appnetwork.models.UpgradeProfile(_Model):
        fully_managed_upgrade_profile: Optional[FullyManagedUpgradeProfile]
        mode: Union[str, UpgradeMode]
        self_managed_upgrade_profile: Optional[SelfManagedUpgradeProfile]

        @overload
        def __init__(
                self, 
                *, 
                fully_managed_upgrade_profile: Optional[FullyManagedUpgradeProfile] = ..., 
                mode: Union[str, UpgradeMode], 
                self_managed_upgrade_profile: Optional[SelfManagedUpgradeProfile] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.UpgradeProfileUpdate(_Model):
        fully_managed_upgrade_profile: Optional[FullyManagedUpgradeProfileUpdate]
        mode: Optional[Union[str, UpgradeMode]]
        self_managed_upgrade_profile: Optional[SelfManagedUpgradeProfileUpdate]

        @overload
        def __init__(
                self, 
                *, 
                fully_managed_upgrade_profile: Optional[FullyManagedUpgradeProfileUpdate] = ..., 
                mode: Optional[Union[str, UpgradeMode]] = ..., 
                self_managed_upgrade_profile: Optional[SelfManagedUpgradeProfileUpdate] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.appnetwork.models.UpgradeReleaseChannel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        RAPID = "Rapid"
        STABLE = "Stable"


    class azure.mgmt.appnetwork.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.appnetwork.models.VersionInfo(_Model):
        upgrades: list[str]
        version: str

        @overload
        def __init__(
                self, 
                *, 
                upgrades: list[str], 
                version: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.appnetwork.operations

    class azure.mgmt.appnetwork.operations.AppLinkMembersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: AppLinkMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: AppLinkMember, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: AppLinkMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: AppLinkMemberUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLinkMember]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> AppLinkMember: ...

        @distributed_trace
        def list_by_app_link(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AppLinkMember]: ...


    class azure.mgmt.appnetwork.operations.AppLinksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: AppLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: AppLink, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: AppLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: AppLinkUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[AppLink]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                **kwargs: Any
            ) -> AppLink: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AppLink]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[AppLink]: ...


    class azure.mgmt.appnetwork.operations.AvailableVersionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_location(
                self, 
                location: str, 
                *, 
                kubernetes_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[AvailableVersion]: ...


    class azure.mgmt.appnetwork.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.appnetwork.operations.UpgradeHistoriesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_by_app_link_member(
                self, 
                resource_group_name: str, 
                app_link_name: str, 
                app_link_member_name: str, 
                **kwargs: Any
            ) -> ItemPaged[UpgradeHistory]: ...


namespace azure.mgmt.appnetwork.types

    class azure.mgmt.appnetwork.types.AppLink(TrackedResource):
        key "id": str
        key "identity": ForwardRef('ManagedServiceIdentity', module='types')
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AppLinkProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: AppLinkProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appnetwork.types.AppLinkMember(TrackedResource):
        key "id": str
        key "location": Required[str]
        key "name": str
        key "properties": ForwardRef('AppLinkMemberProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        location: str
        name: str
        properties: AppLinkMemberProperties
        systemData: SystemData
        tags: dict[str, str]
        type: str


    class azure.mgmt.appnetwork.types.AppLinkMemberProperties(TypedDict, total=False):
        key "clusterType": Union[str, ClusterType]
        key "connectivityProfile": ForwardRef('ConnectivityProfile', module='types')
        key "metadata": Required[Metadata]
        key "observabilityProfile": ForwardRef('ObservabilityProfile', module='types')
        key "provisioningState": Union[str, ProvisioningState]
        key "upgradeProfile": ForwardRef('UpgradeProfile', module='types')
        clusterType: Union[str, ClusterType]
        connectivityProfile: ConnectivityProfile
        metadata: Metadata
        observabilityProfile: ObservabilityProfile
        provisioningState: Union[str, ProvisioningState]
        upgradeProfile: UpgradeProfile


    class azure.mgmt.appnetwork.types.AppLinkMemberUpdate(TypedDict, total=False):
        key "properties": ForwardRef('AppLinkMemberUpdateProperties', module='types')
        properties: AppLinkMemberUpdateProperties
        tags: dict[str, str]


    class azure.mgmt.appnetwork.types.AppLinkMemberUpdateProperties(TypedDict, total=False):
        key "connectivityProfile": ForwardRef('ConnectivityProfileUpdate', module='types')
        key "upgradeProfile": ForwardRef('UpgradeProfileUpdate', module='types')
        connectivityProfile: ConnectivityProfileUpdate
        upgradeProfile: UpgradeProfileUpdate


    class azure.mgmt.appnetwork.types.AppLinkProperties(TypedDict, total=False):
        key "provisioningState": Union[str, ProvisioningState]
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.appnetwork.types.AppLinkUpdate(TypedDict, total=False):
        key "identity": ForwardRef('ManagedServiceIdentityUpdate', module='types')
        identity: ManagedServiceIdentityUpdate
        tags: dict[str, str]


    class azure.mgmt.appnetwork.types.ConnectivityProfile(TypedDict, total=False):
        key "eastWestGateway": ForwardRef('EastWestGatewayProfile', module='types')
        key "network": str
        key "privateConnect": ForwardRef('PrivateConnectProfile', module='types')
        eastWestGateway: EastWestGatewayProfile
        network: str
        privateConnect: PrivateConnectProfile


    class azure.mgmt.appnetwork.types.ConnectivityProfileUpdate(TypedDict, total=False):
        key "eastWestGateway": ForwardRef('EastWestGatewayProfileUpdate', module='types')
        key "network": str
        eastWestGateway: EastWestGatewayProfileUpdate
        network: str


    class azure.mgmt.appnetwork.types.EastWestGatewayProfile(TypedDict, total=False):
        key "visibility": Required[Union[str, EastWestGatewayVisibility]]
        visibility: Union[str, EastWestGatewayVisibility]


    class azure.mgmt.appnetwork.types.EastWestGatewayProfileUpdate(TypedDict, total=False):
        key "visibility": Union[str, EastWestGatewayVisibility]
        visibility: Union[str, EastWestGatewayVisibility]


    class azure.mgmt.appnetwork.types.FullyManagedUpgradeProfile(TypedDict, total=False):
        key "releaseChannel": Required[Union[str, UpgradeReleaseChannel]]
        releaseChannel: Union[str, UpgradeReleaseChannel]


    class azure.mgmt.appnetwork.types.FullyManagedUpgradeProfileUpdate(TypedDict, total=False):
        key "releaseChannel": Union[str, UpgradeReleaseChannel]
        releaseChannel: Union[str, UpgradeReleaseChannel]


    class azure.mgmt.appnetwork.types.ManagedServiceIdentity(TypedDict, total=False):
        key "principalId": str
        key "tenantId": str
        key "type": Required[Union[str, ManagedServiceIdentityType]]
        principalId: str
        tenantId: str
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.appnetwork.types.ManagedServiceIdentityUpdate(TypedDict, total=False):
        key "type": Union[str, ManagedServiceIdentityType]
        type: Union[str, ManagedServiceIdentityType]
        userAssignedIdentities: dict[str, UserAssignedIdentity]


    class azure.mgmt.appnetwork.types.Metadata(TypedDict, total=False):
        key "resourceId": Required[str]
        resourceId: str


    class azure.mgmt.appnetwork.types.MetricsProfile(TypedDict, total=False):
        key "metricsEndpoint": str
        metricsEndpoint: str


    class azure.mgmt.appnetwork.types.ObservabilityProfile(TypedDict, total=False):
        key "metrics": ForwardRef('MetricsProfile', module='types')
        metrics: MetricsProfile


    class azure.mgmt.appnetwork.types.PrivateConnectProfile(TypedDict, total=False):
        key "subnetResourceId": Required[str]
        subnetResourceId: str


    class azure.mgmt.appnetwork.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.appnetwork.types.SelfManagedUpgradeProfile(TypedDict, total=False):
        key "version": Required[str]
        version: str


    class azure.mgmt.appnetwork.types.SelfManagedUpgradeProfileUpdate(TypedDict, total=False):
        key "version": str
        version: str


    class azure.mgmt.appnetwork.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.appnetwork.types.TrackedResource(Resource):
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


    class azure.mgmt.appnetwork.types.UpgradeProfile(TypedDict, total=False):
        key "fullyManagedUpgradeProfile": ForwardRef('FullyManagedUpgradeProfile', module='types')
        key "mode": Required[Union[str, UpgradeMode]]
        key "selfManagedUpgradeProfile": ForwardRef('SelfManagedUpgradeProfile', module='types')
        fullyManagedUpgradeProfile: FullyManagedUpgradeProfile
        mode: Union[str, UpgradeMode]
        selfManagedUpgradeProfile: SelfManagedUpgradeProfile


    class azure.mgmt.appnetwork.types.UpgradeProfileUpdate(TypedDict, total=False):
        key "fullyManagedUpgradeProfile": ForwardRef('FullyManagedUpgradeProfileUpdate', module='types')
        key "mode": Union[str, UpgradeMode]
        key "selfManagedUpgradeProfile": ForwardRef('SelfManagedUpgradeProfileUpdate', module='types')
        fullyManagedUpgradeProfile: FullyManagedUpgradeProfileUpdate
        mode: Union[str, UpgradeMode]
        selfManagedUpgradeProfile: SelfManagedUpgradeProfileUpdate


    class azure.mgmt.appnetwork.types.UserAssignedIdentity(TypedDict, total=False):
        key "clientId": str
        key "principalId": str
        clientId: str
        principalId: str


```