```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.storageactions

    class azure.mgmt.storageactions.StorageActionsMgmtClient: implements ContextManager 
        operations: Operations
        storage_task_assignment: StorageTaskAssignmentOperations
        storage_tasks: StorageTasksOperations
        storage_tasks_report: StorageTasksReportOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.storageactions.aio

    class azure.mgmt.storageactions.aio.StorageActionsMgmtClient: implements AsyncContextManager 
        operations: Operations
        storage_task_assignment: StorageTaskAssignmentOperations
        storage_tasks: StorageTasksOperations
        storage_tasks_report: StorageTasksReportOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: Optional[str] = None, 
                *, 
                api_version: str = ..., 
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


namespace azure.mgmt.storageactions.aio.operations

    class azure.mgmt.storageactions.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.storageactions.aio.operations.StorageTaskAssignmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTaskAssignment]: ...


    class azure.mgmt.storageactions.aio.operations.StorageTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: StorageTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: StorageTaskUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[StorageTask]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> StorageTask: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTask]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[StorageTask]: ...

        @overload
        async def preview_actions(
                self, 
                location: str, 
                parameters: StorageTaskPreviewAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...

        @overload
        async def preview_actions(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...

        @overload
        async def preview_actions(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...


    class azure.mgmt.storageactions.aio.operations.StorageTasksReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> AsyncItemPaged[StorageTaskReportInstance]: ...


namespace azure.mgmt.storageactions.models

    class azure.mgmt.storageactions.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.storageactions.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.storageactions.models.ElseCondition(_Model):
        operations: List[StorageTaskOperation]

        @overload
        def __init__(
                self, 
                *, 
                operations: List[StorageTaskOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.storageactions.models.ErrorDetail(_Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.storageactions.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.IfCondition(_Model):
        condition: str
        operations: List[StorageTaskOperation]

        @overload
        def __init__(
                self, 
                *, 
                condition: str, 
                operations: List[StorageTaskOperation]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.ManagedServiceIdentity(_Model):
        principal_id: Optional[str]
        tenant_id: Optional[str]
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]]

        @overload
        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.storageactions.models.MatchedBlockName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ELSE = "Else"
        IF = "If"
        NONE = "None"


    class azure.mgmt.storageactions.models.OnFailure(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BREAK = "break"


    class azure.mgmt.storageactions.models.OnSuccess(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUE = "continue"


    class azure.mgmt.storageactions.models.Operation(_Model):
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


    class azure.mgmt.storageactions.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.storageactions.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.storageactions.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        CREATING = "Creating"
        DELETING = "Deleting"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"
        VALIDATE_SUBSCRIPTION_QUOTA_BEGIN = "ValidateSubscriptionQuotaBegin"
        VALIDATE_SUBSCRIPTION_QUOTA_END = "ValidateSubscriptionQuotaEnd"


    class azure.mgmt.storageactions.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.storageactions.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.storageactions.models.RunResult(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.storageactions.models.RunStatusEnum(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FINISHED = "Finished"
        IN_PROGRESS = "InProgress"


    class azure.mgmt.storageactions.models.StorageTask(TrackedResource):
        id: str
        identity: ManagedServiceIdentity
        location: str
        name: str
        properties: StorageTaskProperties
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: ManagedServiceIdentity, 
                location: str, 
                properties: StorageTaskProperties, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskAction(_Model):
        else_property: Optional[ElseCondition]
        if_property: IfCondition

        @overload
        def __init__(
                self, 
                *, 
                else_property: Optional[ElseCondition] = ..., 
                if_property: IfCondition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskAssignment(_Model):
        id: Optional[str]


    class azure.mgmt.storageactions.models.StorageTaskOperation(_Model):
        name: Union[str, StorageTaskOperationName]
        on_failure: Optional[Union[str, OnFailure]]
        on_success: Optional[Union[str, OnSuccess]]
        parameters: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                name: Union[str, StorageTaskOperationName], 
                on_failure: Optional[Union[str, OnFailure]] = ..., 
                on_success: Optional[Union[str, OnSuccess]] = ..., 
                parameters: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskOperationName(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETE_BLOB = "DeleteBlob"
        SET_BLOB_EXPIRY = "SetBlobExpiry"
        SET_BLOB_IMMUTABILITY_POLICY = "SetBlobImmutabilityPolicy"
        SET_BLOB_LEGAL_HOLD = "SetBlobLegalHold"
        SET_BLOB_TAGS = "SetBlobTags"
        SET_BLOB_TIER = "SetBlobTier"
        UNDELETE_BLOB = "UndeleteBlob"


    class azure.mgmt.storageactions.models.StorageTaskPreviewAction(_Model):
        properties: StorageTaskPreviewActionProperties

        @overload
        def __init__(
                self, 
                *, 
                properties: StorageTaskPreviewActionProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewActionCondition(_Model):
        else_block_exists: bool
        if_property: StorageTaskPreviewActionIfCondition

        @overload
        def __init__(
                self, 
                *, 
                else_block_exists: bool, 
                if_property: StorageTaskPreviewActionIfCondition
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewActionIfCondition(_Model):
        condition: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                condition: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewActionProperties(_Model):
        action: StorageTaskPreviewActionCondition
        blobs: List[StorageTaskPreviewBlobProperties]
        container: StorageTaskPreviewContainerProperties

        @overload
        def __init__(
                self, 
                *, 
                action: StorageTaskPreviewActionCondition, 
                blobs: List[StorageTaskPreviewBlobProperties], 
                container: StorageTaskPreviewContainerProperties
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewBlobProperties(_Model):
        matched_block: Optional[Union[str, MatchedBlockName]]
        metadata: Optional[List[StorageTaskPreviewKeyValueProperties]]
        name: Optional[str]
        properties: Optional[List[StorageTaskPreviewKeyValueProperties]]
        tags: Optional[List[StorageTaskPreviewKeyValueProperties]]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[List[StorageTaskPreviewKeyValueProperties]] = ..., 
                name: Optional[str] = ..., 
                properties: Optional[List[StorageTaskPreviewKeyValueProperties]] = ..., 
                tags: Optional[List[StorageTaskPreviewKeyValueProperties]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewContainerProperties(_Model):
        metadata: Optional[List[StorageTaskPreviewKeyValueProperties]]
        name: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                metadata: Optional[List[StorageTaskPreviewKeyValueProperties]] = ..., 
                name: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskPreviewKeyValueProperties(_Model):
        key: Optional[str]
        value: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                key: Optional[str] = ..., 
                value: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskProperties(_Model):
        action: StorageTaskAction
        creation_time_in_utc: Optional[datetime]
        description: str
        enabled: bool
        provisioning_state: Optional[Union[str, ProvisioningState]]
        task_version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action: StorageTaskAction, 
                description: str, 
                enabled: bool
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskReportInstance(ProxyResource):
        id: str
        name: str
        properties: Optional[StorageTaskReportProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[StorageTaskReportProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskReportProperties(_Model):
        finish_time: Optional[str]
        object_failed_count: Optional[str]
        objects_operated_on_count: Optional[str]
        objects_succeeded_count: Optional[str]
        objects_targeted_count: Optional[str]
        run_result: Optional[Union[str, RunResult]]
        run_status_enum: Optional[Union[str, RunStatusEnum]]
        run_status_error: Optional[str]
        start_time: Optional[str]
        storage_account_id: Optional[str]
        summary_report_path: Optional[str]
        task_assignment_id: Optional[str]
        task_id: Optional[str]
        task_version: Optional[str]


    class azure.mgmt.storageactions.models.StorageTaskUpdateParameters(_Model):
        identity: Optional[ManagedServiceIdentity]
        properties: Optional[StorageTaskUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentity] = ..., 
                properties: Optional[StorageTaskUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.StorageTaskUpdateProperties(_Model):
        action: Optional[StorageTaskAction]
        creation_time_in_utc: Optional[datetime]
        description: Optional[str]
        enabled: Optional[bool]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        task_version: Optional[int]

        @overload
        def __init__(
                self, 
                *, 
                action: Optional[StorageTaskAction] = ..., 
                description: Optional[str] = ..., 
                enabled: Optional[bool] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.SystemData(_Model):
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


    class azure.mgmt.storageactions.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: Optional[Dict[str, str]]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.storageactions.models.UserAssignedIdentity(_Model):
        client_id: Optional[str]
        principal_id: Optional[str]


namespace azure.mgmt.storageactions.operations

    class azure.mgmt.storageactions.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.storageactions.operations.StorageTaskAssignmentOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageTaskAssignment]: ...


    class azure.mgmt.storageactions.operations.StorageTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: StorageTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: StorageTaskUpdateParameters, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[StorageTask]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                **kwargs: Any
            ) -> StorageTask: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[StorageTask]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[StorageTask]: ...

        @overload
        def preview_actions(
                self, 
                location: str, 
                parameters: StorageTaskPreviewAction, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...

        @overload
        def preview_actions(
                self, 
                location: str, 
                parameters: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...

        @overload
        def preview_actions(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> StorageTaskPreviewAction: ...


    class azure.mgmt.storageactions.operations.StorageTasksReportOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                resource_group_name: str, 
                storage_task_name: str, 
                *, 
                filter: Optional[str] = ..., 
                **kwargs: Any
            ) -> ItemPaged[StorageTaskReportInstance]: ...


```