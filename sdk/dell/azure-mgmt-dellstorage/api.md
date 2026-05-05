```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.dellstorage

    class azure.mgmt.dellstorage.DellStorageMgmtClient: implements ContextManager 
        file_systems: FileSystemsOperations
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


namespace azure.mgmt.dellstorage.aio

    class azure.mgmt.dellstorage.aio.DellStorageMgmtClient: implements AsyncContextManager 
        file_systems: FileSystemsOperations
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


namespace azure.mgmt.dellstorage.aio.operations

    class azure.mgmt.dellstorage.aio.operations.FileSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: FileSystemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileSystemResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileSystemResource]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[FileSystemResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[FileSystemResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[FileSystemResource]: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: FileSystemResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @overload
        async def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...


    class azure.mgmt.dellstorage.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.dellstorage.models

    class azure.mgmt.dellstorage.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.dellstorage.models.Capacity(_Model):
        current: Optional[str]
        incremental: Optional[str]
        max: Optional[str]
        min: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                current: Optional[str] = ..., 
                incremental: Optional[str] = ..., 
                max: Optional[str] = ..., 
                min: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.dellstorage.models.EncryptionIdentityProperties(_Model):
        identity_resource_id: Optional[str]
        identity_type: Optional[Union[str, EncryptionIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, EncryptionIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.EncryptionIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dellstorage.models.EncryptionIdentityUpdateProperties(_Model):
        identity_resource_id: Optional[str]
        identity_type: Optional[Union[str, EncryptionIdentityType]]

        @overload
        def __init__(
                self, 
                *, 
                identity_resource_id: Optional[str] = ..., 
                identity_type: Optional[Union[str, EncryptionIdentityType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.EncryptionProperties(_Model):
        encryption_identity_properties: Optional[EncryptionIdentityProperties]
        encryption_type: Union[str, ResourceEncryptionType]
        key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_identity_properties: Optional[EncryptionIdentityProperties] = ..., 
                encryption_type: Union[str, ResourceEncryptionType], 
                key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.EncryptionUpdateProperties(_Model):
        encryption_identity_properties: Optional[EncryptionIdentityUpdateProperties]
        encryption_type: Optional[Union[str, ResourceEncryptionType]]
        key_url: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                encryption_identity_properties: Optional[EncryptionIdentityUpdateProperties] = ..., 
                encryption_type: Optional[Union[str, ResourceEncryptionType]] = ..., 
                key_url: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.dellstorage.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.dellstorage.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.FileSystemResource(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentity]
        location: str
        name: str
        properties: Optional[FileSystemResourceProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                location: str, 
                properties: Optional[FileSystemResourceProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.FileSystemResourceProperties(_Model):
        capacity: Optional[Capacity]
        delegated_subnet_cidr: str
        delegated_subnet_id: str
        dell_reference_number: str
        encryption: EncryptionProperties
        file_system_id: Optional[str]
        marketplace: MarketplaceDetails
        one_fs_url: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        smart_connect_fqdn: Optional[str]
        user: UserDetails

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[Capacity] = ..., 
                delegated_subnet_cidr: str, 
                delegated_subnet_id: str, 
                dell_reference_number: str, 
                encryption: EncryptionProperties, 
                file_system_id: Optional[str] = ..., 
                marketplace: MarketplaceDetails, 
                one_fs_url: Optional[str] = ..., 
                smart_connect_fqdn: Optional[str] = ..., 
                user: UserDetails
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.FileSystemResourceUpdate(_Model):
        identity: Optional[ManagedServiceIdentityUpdate]
        properties: Optional[FileSystemResourceUpdateProperties]
        tags: Optional[dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityUpdate] = ..., 
                properties: Optional[FileSystemResourceUpdateProperties] = ..., 
                tags: Optional[dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.FileSystemResourceUpdateProperties(_Model):
        capacity: Optional[Capacity]
        delegated_subnet_id: Optional[str]
        encryption: Optional[EncryptionUpdateProperties]

        @overload
        def __init__(
                self, 
                *, 
                capacity: Optional[Capacity] = ..., 
                delegated_subnet_id: Optional[str] = ..., 
                encryption: Optional[EncryptionUpdateProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.ManagedServiceIdentity(_Model):
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


    class azure.mgmt.dellstorage.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.dellstorage.models.ManagedServiceIdentityUpdate(_Model):
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


    class azure.mgmt.dellstorage.models.MarketplaceDetails(_Model):
        end_date: Optional[str]
        marketplace_subscription_id: Optional[str]
        marketplace_subscription_status: Optional[Union[str, MarketplaceSubscriptionStatus]]
        offer_id: str
        plan_id: str
        plan_name: str
        private_offer_id: Optional[str]
        publisher_id: Optional[str]
        term_unit: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                end_date: Optional[str] = ..., 
                marketplace_subscription_id: Optional[str] = ..., 
                offer_id: str, 
                plan_id: str, 
                plan_name: str, 
                private_offer_id: Optional[str] = ..., 
                publisher_id: Optional[str] = ..., 
                term_unit: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.dellstorage.models.MarketplaceSubscriptionStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        PENDING_FULFILLMENT_START = "PendingFulfillmentStart"
        SUBSCRIBED = "Subscribed"
        SUSPENDED = "Suspended"
        UNSUBSCRIBED = "Unsubscribed"


    class azure.mgmt.dellstorage.models.Operation(_Model):
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


    class azure.mgmt.dellstorage.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.dellstorage.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.dellstorage.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETED = "Deleted"
        DELETING = "Deleting"
        FAILED = "Failed"
        NOT_SPECIFIED = "NotSpecified"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.dellstorage.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.dellstorage.models.ResourceEncryptionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CUSTOMER_MANAGED_KEYS_CMK_ = "Customer-managed keys (CMK)"
        MICROSOFT_MANAGED_KEYS_MMK_ = "Microsoft-managed keys (MMK)"


    class azure.mgmt.dellstorage.models.SystemData(_Model):
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


    class azure.mgmt.dellstorage.models.TrackedResource(Resource):
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


    class azure.mgmt.dellstorage.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.dellstorage.models.UserDetails(_Model):
        email: str

        @overload
        def __init__(
                self, 
                *, 
                email: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.dellstorage.operations

    class azure.mgmt.dellstorage.operations.FileSystemsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: FileSystemResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileSystemResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileSystemResource]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[FileSystemResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[FileSystemResource]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[FileSystemResource]: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: FileSystemResourceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...

        @overload
        def update(
                self, 
                resource_group_name: str, 
                filesystem_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FileSystemResource: ...


    class azure.mgmt.dellstorage.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```