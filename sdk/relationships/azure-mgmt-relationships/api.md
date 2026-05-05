```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.relationships

    class azure.mgmt.relationships.RelationshipsMgmtClient: implements ContextManager 
        dependency_of_relationships: DependencyOfRelationshipsOperations
        operations: Operations
        service_group_member_relationships: ServiceGroupMemberRelationshipsOperations

        def __init__(
                self, 
                credential: TokenCredential, 
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


namespace azure.mgmt.relationships.aio

    class azure.mgmt.relationships.aio.RelationshipsMgmtClient: implements AsyncContextManager 
        dependency_of_relationships: DependencyOfRelationshipsOperations
        operations: Operations
        service_group_member_relationships: ServiceGroupMemberRelationshipsOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
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


namespace azure.mgmt.relationships.aio.operations

    class azure.mgmt.relationships.aio.operations.DependencyOfRelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: DependencyOfRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DependencyOfRelationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DependencyOfRelationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DependencyOfRelationship]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DependencyOfRelationship: ...


    class azure.mgmt.relationships.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.relationships.aio.operations.ServiceGroupMemberRelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: ServiceGroupMemberRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroupMemberRelationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroupMemberRelationship]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ServiceGroupMemberRelationship]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> ServiceGroupMemberRelationship: ...


namespace azure.mgmt.relationships.models

    class azure.mgmt.relationships.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.relationships.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.relationships.models.DependencyOfRelationship(ExtensionResource):
        id: str
        name: str
        properties: Optional[DependencyOfRelationshipProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DependencyOfRelationshipProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.relationships.models.DependencyOfRelationshipProperties(_Model):
        metadata: RelationshipMetadata
        origin_information: RelationshipOriginInformation
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_id: str
        target_id: str
        target_tenant: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_id: str, 
                target_tenant: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.relationships.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.relationships.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.relationships.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.relationships.models.ExtensionResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.relationships.models.Operation(_Model):
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


    class azure.mgmt.relationships.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.relationships.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.relationships.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.relationships.models.RelationshipMetadata(_Model):
        source_type: str
        target_type: str


    class azure.mgmt.relationships.models.RelationshipOriginInformation(_Model):
        discovery_engine: Optional[str]
        relationship_origin_type: Union[str, RelationshipOrigins]


    class azure.mgmt.relationships.models.RelationshipOrigins(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVICE_EXPLICITLY_CREATED = "ServiceExplicitlyCreated"
        SYSTEM_DISCOVERED_BY_RULE = "SystemDiscoveredByRule"
        USER_DISCOVERED_BY_RULE = "UserDiscoveredByRule"
        USER_EXPLICITLY_CREATED = "UserExplicitlyCreated"


    class azure.mgmt.relationships.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.relationships.models.ServiceGroupMemberRelationship(ExtensionResource):
        id: str
        name: str
        properties: Optional[ServiceGroupMemberRelationshipProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ServiceGroupMemberRelationshipProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.relationships.models.ServiceGroupMemberRelationshipProperties(_Model):
        metadata: RelationshipMetadata
        origin_information: RelationshipOriginInformation
        provisioning_state: Optional[Union[str, ProvisioningState]]
        source_id: str
        target_id: str
        target_tenant: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                target_id: str, 
                target_tenant: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.relationships.models.SystemData(_Model):
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


namespace azure.mgmt.relationships.operations

    class azure.mgmt.relationships.operations.DependencyOfRelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: DependencyOfRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DependencyOfRelationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DependencyOfRelationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DependencyOfRelationship]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> DependencyOfRelationship: ...


    class azure.mgmt.relationships.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.relationships.operations.ServiceGroupMemberRelationshipsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: ServiceGroupMemberRelationship, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroupMemberRelationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroupMemberRelationship]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_uri: str, 
                name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ServiceGroupMemberRelationship]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_uri: str, 
                name: str, 
                **kwargs: Any
            ) -> ServiceGroupMemberRelationship: ...


```