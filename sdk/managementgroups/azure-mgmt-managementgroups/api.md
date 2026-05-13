```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.managementgroups

    class azure.mgmt.managementgroups.ManagementGroupsMgmtClient(_ManagementGroupsMgmtClientOperationsMixin): implements ContextManager 
        entities: EntitiesOperations
        hierarchy_settings: HierarchySettingsOperations
        management_group_subscriptions: ManagementGroupSubscriptionsOperations
        management_groups: ManagementGroupsOperations
        operations: Operations

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

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> HttpResponse: ...

        @distributed_trace
        def start_tenant_backfill(self, **kwargs: Any) -> TenantBackfillStatusResult: ...

        @distributed_trace
        def tenant_backfill_status(self, **kwargs: Any) -> TenantBackfillStatusResult: ...


namespace azure.mgmt.managementgroups.aio

    class azure.mgmt.managementgroups.aio.ManagementGroupsMgmtClient(_ManagementGroupsMgmtClientOperationsMixin): implements AsyncContextManager 
        entities: EntitiesOperations
        hierarchy_settings: HierarchySettingsOperations
        management_group_subscriptions: ManagementGroupSubscriptionsOperations
        management_groups: ManagementGroupsOperations
        operations: Operations

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

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: CheckNameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        @overload
        async def check_name_availability(
                self, 
                check_name_availability_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CheckNameAvailabilityResult: ...

        async def close(self) -> None: ...

        def send_request(
                self, 
                request: HttpRequest, 
                *, 
                stream: bool = False, 
                **kwargs: Any
            ) -> Awaitable[AsyncHttpResponse]: ...

        @distributed_trace_async
        async def start_tenant_backfill(self, **kwargs: Any) -> TenantBackfillStatusResult: ...

        @distributed_trace_async
        async def tenant_backfill_status(self, **kwargs: Any) -> TenantBackfillStatusResult: ...


namespace azure.mgmt.managementgroups.aio.operations

    class azure.mgmt.managementgroups.aio.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cache_control: str = "no-cache", 
                filter: Optional[str] = ..., 
                group_name: Optional[str] = ..., 
                search: Optional[Union[str, EntitySearchType]] = ..., 
                select: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                view: Optional[Union[str, EntityViewParameterType]] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[EntityInfo]: ...


    class azure.mgmt.managementgroups.aio.operations.HierarchySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: CreateOrUpdateSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        async def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        async def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @distributed_trace_async
        async def list(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> HierarchySettingsList: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: CreateOrUpdateSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...


    class azure.mgmt.managementgroups.aio.operations.ManagementGroupSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def create(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> SubscriptionUnderManagementGroup: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get_subscription(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> SubscriptionUnderManagementGroup: ...

        @distributed_trace
        def get_subscriptions_under_management_group(
                self, 
                group_id: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[SubscriptionUnderManagementGroup]: ...


    class azure.mgmt.managementgroups.aio.operations.ManagementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: CreateManagementGroupRequest, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagementGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: JSON, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagementGroup]: ...

        @overload
        async def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: IO[bytes], 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ManagementGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                group_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                group_id: str, 
                *, 
                cache_control: str = "no-cache", 
                expand: Optional[Union[str, ManagementGroupExpandType]] = ..., 
                filter: Optional[str] = ..., 
                recurse: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @distributed_trace
        def get_descendants(
                self, 
                group_id: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[DescendantInfo]: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cache_control: str = "no-cache", 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[ManagementGroupInfo]: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                patch_group_request: PatchManagementGroupRequest, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                patch_group_request: JSON, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @overload
        async def update(
                self, 
                group_id: str, 
                patch_group_request: IO[bytes], 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...


    class azure.mgmt.managementgroups.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


namespace azure.mgmt.managementgroups.models

    class azure.mgmt.managementgroups.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.managementgroups.models.CheckNameAvailabilityRequest(_Model):
        name: Optional[str]
        type: Optional[Literal["Management/managementGroups"]]

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[Literal[Management/managementGroups]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.CheckNameAvailabilityResult(_Model):
        message: Optional[str]
        name_available: Optional[bool]
        reason: Optional[Union[str, Reason]]


    class azure.mgmt.managementgroups.models.CreateManagementGroupChildInfo(_Model):
        children: Optional[list[CreateManagementGroupChildInfo]]
        display_name: Optional[str]
        id: Optional[str]
        name: Optional[str]
        type: Optional[Union[str, ManagementGroupChildType]]


    class azure.mgmt.managementgroups.models.CreateManagementGroupDetails(_Model):
        parent: Optional[CreateParentGroupInfo]
        updated_by: Optional[str]
        updated_time: Optional[datetime]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                parent: Optional[CreateParentGroupInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.CreateManagementGroupProperties(_Model):
        children: Optional[list[CreateManagementGroupChildInfo]]
        details: Optional[CreateManagementGroupDetails]
        display_name: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                details: Optional[CreateManagementGroupDetails] = ..., 
                display_name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.CreateManagementGroupRequest(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[CreateManagementGroupProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                properties: Optional[CreateManagementGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.CreateOrUpdateSettingsProperties(_Model):
        default_management_group: Optional[str]
        require_authorization_for_group_creation: Optional[bool]

        @overload
        def __init__(
                self, 
                *, 
                default_management_group: Optional[str] = ..., 
                require_authorization_for_group_creation: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.CreateOrUpdateSettingsRequest(_Model):
        properties: Optional[CreateOrUpdateSettingsProperties]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[CreateOrUpdateSettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.CreateParentGroupInfo(_Model):
        display_name: Optional[str]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.managementgroups.models.DescendantInfo(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[DescendantInfoProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[DescendantInfoProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.DescendantInfoProperties(_Model):
        display_name: Optional[str]
        parent: Optional[DescendantParentGroupInfo]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                parent: Optional[DescendantParentGroupInfo] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.DescendantParentGroupInfo(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.EntityInfo(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[EntityInfoProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[EntityInfoProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.EntityInfoProperties(_Model):
        display_name: Optional[str]
        inherited_permissions: Optional[Union[str, Permissions]]
        number_of_child_groups: Optional[int]
        number_of_children: Optional[int]
        number_of_descendants: Optional[int]
        parent: Optional[EntityParentGroupInfo]
        parent_display_name_chain: Optional[list[str]]
        parent_name_chain: Optional[list[str]]
        permissions: Optional[Union[str, Permissions]]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                inherited_permissions: Optional[Union[str, Permissions]] = ..., 
                number_of_child_groups: Optional[int] = ..., 
                number_of_children: Optional[int] = ..., 
                number_of_descendants: Optional[int] = ..., 
                parent: Optional[EntityParentGroupInfo] = ..., 
                parent_display_name_chain: Optional[list[str]] = ..., 
                parent_name_chain: Optional[list[str]] = ..., 
                permissions: Optional[Union[str, Permissions]] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.EntityParentGroupInfo(_Model):
        id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.EntitySearchType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALLOWED_CHILDREN = "AllowedChildren"
        ALLOWED_PARENTS = "AllowedParents"
        CHILDREN_ONLY = "ChildrenOnly"
        PARENT_AND_FIRST_LEVEL_CHILDREN = "ParentAndFirstLevelChildren"
        PARENT_ONLY = "ParentOnly"


    class azure.mgmt.managementgroups.models.EntityViewParameterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUDIT = "Audit"
        FULL_HIERARCHY = "FullHierarchy"
        GROUPS_ONLY = "GroupsOnly"
        SUBSCRIPTIONS_ONLY = "SubscriptionsOnly"


    class azure.mgmt.managementgroups.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.managementgroups.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.managementgroups.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.HierarchySettings(ProxyResource):
        id: str
        name: str
        properties: Optional[HierarchySettingsProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HierarchySettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.HierarchySettingsInfo(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[HierarchySettingsProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HierarchySettingsProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.HierarchySettingsList(_Model):
        next_link: Optional[str]
        value: Optional[list[HierarchySettingsInfo]]

        @overload
        def __init__(
                self, 
                *, 
                value: Optional[list[HierarchySettingsInfo]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.HierarchySettingsProperties(_Model):
        default_management_group: Optional[str]
        require_authorization_for_group_creation: Optional[bool]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                default_management_group: Optional[str] = ..., 
                require_authorization_for_group_creation: Optional[bool] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[ManagementGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagementGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupChildInfo(_Model):
        children: Optional[list[ManagementGroupChildInfo]]
        display_name: Optional[str]
        id: Optional[str]
        name: Optional[str]
        type: Optional[Union[str, ManagementGroupChildType]]

        @overload
        def __init__(
                self, 
                *, 
                children: Optional[list[ManagementGroupChildInfo]] = ..., 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                type: Optional[Union[str, ManagementGroupChildType]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupChildType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MICROSOFT_MANAGEMENT_MANAGEMENT_GROUPS = "Microsoft.Management/managementGroups"
        SUBSCRIPTIONS = "/subscriptions"


    class azure.mgmt.managementgroups.models.ManagementGroupDetails(_Model):
        management_group_ancestors: Optional[list[str]]
        management_group_ancestors_chain: Optional[list[ManagementGroupPathElement]]
        parent: Optional[ParentGroupInfo]
        path: Optional[list[ManagementGroupPathElement]]
        updated_by: Optional[str]
        updated_time: Optional[datetime]
        version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                management_group_ancestors: Optional[list[str]] = ..., 
                management_group_ancestors_chain: Optional[list[ManagementGroupPathElement]] = ..., 
                parent: Optional[ParentGroupInfo] = ..., 
                path: Optional[list[ManagementGroupPathElement]] = ..., 
                updated_by: Optional[str] = ..., 
                updated_time: Optional[datetime] = ..., 
                version: Optional[int] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupExpandType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ANCESTORS = "ancestors"
        CHILDREN = "children"
        PATH = "path"


    class azure.mgmt.managementgroups.models.ManagementGroupInfo(_Model):
        id: Optional[str]
        name: Optional[str]
        properties: Optional[ManagementGroupInfoProperties]
        type: Optional[str]

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[ManagementGroupInfoProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupInfoProperties(_Model):
        display_name: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupPathElement(_Model):
        display_name: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.ManagementGroupProperties(_Model):
        children: Optional[list[ManagementGroupChildInfo]]
        details: Optional[ManagementGroupDetails]
        display_name: Optional[str]
        tenant_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                children: Optional[list[ManagementGroupChildInfo]] = ..., 
                details: Optional[ManagementGroupDetails] = ..., 
                display_name: Optional[str] = ..., 
                tenant_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.Operation(_Model):
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


    class azure.mgmt.managementgroups.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.managementgroups.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.managementgroups.models.ParentGroupInfo(_Model):
        display_name: Optional[str]
        id: Optional[str]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                id: Optional[str] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.PatchManagementGroupRequest(_Model):
        display_name: Optional[str]
        parent_group_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                parent_group_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.Permissions(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE = "delete"
        EDIT = "edit"
        NOACCESS = "noaccess"
        VIEW = "view"


    class azure.mgmt.managementgroups.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.managementgroups.models.Reason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.managementgroups.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.managementgroups.models.Status(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "Cancelled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        NOT_STARTED_BUT_GROUPS_EXIST = "NotStartedButGroupsExist"
        STARTED = "Started"


    class azure.mgmt.managementgroups.models.SubscriptionUnderManagementGroup(ProxyResource):
        id: str
        name: str
        properties: Optional[SubscriptionUnderManagementGroupProperties]
        system_data: SystemData
        type: str

        def __getattr__(self, name: str) -> Any: ...

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SubscriptionUnderManagementGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...

        def __setattr__(
                self, 
                key: str, 
                value: Any
            ) -> None: ...


    class azure.mgmt.managementgroups.models.SubscriptionUnderManagementGroupProperties(_Model):
        display_name: Optional[str]
        parent: Optional[DescendantParentGroupInfo]
        state: Optional[str]
        tenant: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                display_name: Optional[str] = ..., 
                parent: Optional[DescendantParentGroupInfo] = ..., 
                state: Optional[str] = ..., 
                tenant: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.managementgroups.models.SystemData(_Model):
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


    class azure.mgmt.managementgroups.models.TenantBackfillStatusResult(_Model):
        status: Optional[Union[str, Status]]
        tenant_id: Optional[str]


namespace azure.mgmt.managementgroups.operations

    class azure.mgmt.managementgroups.operations.EntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cache_control: str = "no-cache", 
                filter: Optional[str] = ..., 
                group_name: Optional[str] = ..., 
                search: Optional[Union[str, EntitySearchType]] = ..., 
                select: Optional[str] = ..., 
                skip: Optional[int] = ..., 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                view: Optional[Union[str, EntityViewParameterType]] = ..., 
                **kwargs: Any
            ) -> ItemPaged[EntityInfo]: ...


    class azure.mgmt.managementgroups.operations.HierarchySettingsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: CreateOrUpdateSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        def create_or_update(
                self, 
                group_id: str, 
                create_tenant_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @distributed_trace
        def delete(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @distributed_trace
        def list(
                self, 
                group_id: str, 
                **kwargs: Any
            ) -> HierarchySettingsList: ...

        @overload
        def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: CreateOrUpdateSettingsRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...

        @overload
        def update(
                self, 
                group_id: str, 
                create_tenant_settings_request: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> HierarchySettings: ...


    class azure.mgmt.managementgroups.operations.ManagementGroupSubscriptionsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def create(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> SubscriptionUnderManagementGroup: ...

        @distributed_trace
        def delete(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get_subscription(
                self, 
                group_id: str, 
                subscription_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> SubscriptionUnderManagementGroup: ...

        @distributed_trace
        def get_subscriptions_under_management_group(
                self, 
                group_id: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[SubscriptionUnderManagementGroup]: ...


    class azure.mgmt.managementgroups.operations.ManagementGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: CreateManagementGroupRequest, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagementGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: JSON, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagementGroup]: ...

        @overload
        def begin_create_or_update(
                self, 
                group_id: str, 
                create_management_group_request: IO[bytes], 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ManagementGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                group_id: str, 
                *, 
                cache_control: str = "no-cache", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                group_id: str, 
                *, 
                cache_control: str = "no-cache", 
                expand: Optional[Union[str, ManagementGroupExpandType]] = ..., 
                filter: Optional[str] = ..., 
                recurse: Optional[bool] = ..., 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @distributed_trace
        def get_descendants(
                self, 
                group_id: str, 
                *, 
                skiptoken: Optional[str] = ..., 
                top: Optional[int] = ..., 
                **kwargs: Any
            ) -> ItemPaged[DescendantInfo]: ...

        @distributed_trace
        def list(
                self, 
                *, 
                cache_control: str = "no-cache", 
                skiptoken: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[ManagementGroupInfo]: ...

        @overload
        def update(
                self, 
                group_id: str, 
                patch_group_request: PatchManagementGroupRequest, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @overload
        def update(
                self, 
                group_id: str, 
                patch_group_request: JSON, 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...

        @overload
        def update(
                self, 
                group_id: str, 
                patch_group_request: IO[bytes], 
                *, 
                cache_control: str = "no-cache", 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ManagementGroup: ...


    class azure.mgmt.managementgroups.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


```