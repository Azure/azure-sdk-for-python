```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.databasewatcher

    class azure.mgmt.databasewatcher.DatabaseWatcherMgmtClient: implements ContextManager 
        alert_rule_resources: AlertRuleResourcesOperations
        health_validations: HealthValidationsOperations
        operations: Operations
        shared_private_link_resources: SharedPrivateLinkResourcesOperations
        targets: TargetsOperations
        watchers: WatchersOperations

        def __init__(
                self, 
                credential: TokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.databasewatcher.aio

    class azure.mgmt.databasewatcher.aio.DatabaseWatcherMgmtClient: implements AsyncContextManager 
        alert_rule_resources: AlertRuleResourcesOperations
        health_validations: HealthValidationsOperations
        operations: Operations
        shared_private_link_resources: SharedPrivateLinkResourcesOperations
        targets: TargetsOperations
        watchers: WatchersOperations

        def __init__(
                self, 
                credential: AsyncTokenCredential, 
                subscription_id: str, 
                base_url: str = "https://management.azure.com", 
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


namespace azure.mgmt.databasewatcher.aio.operations

    class azure.mgmt.databasewatcher.aio.operations.AlertRuleResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: AlertRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'alert_rule_resource_name', 'accept']})
        async def delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'alert_rule_resource_name', 'accept']})
        async def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'accept']})
        def list_by_parent(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[AlertRuleResource]: ...


    class azure.mgmt.databasewatcher.aio.operations.HealthValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'health_validation_name', 'accept']})
        async def begin_start_validation(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                health_validation_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[HealthValidation]: ...

        @distributed_trace_async
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'health_validation_name', 'accept']})
        async def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                health_validation_name: str, 
                **kwargs: Any
            ) -> HealthValidation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'accept']})
        def list_by_parent(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[HealthValidation]: ...


    class azure.mgmt.databasewatcher.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncIterable[Operation]: ...


    class azure.mgmt.databasewatcher.aio.operations.SharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list_by_watcher(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[SharedPrivateLinkResource]: ...


    class azure.mgmt.databasewatcher.aio.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        async def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace_async
        async def delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list_by_watcher(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Target]: ...


    class azure.mgmt.databasewatcher.aio.operations.WatchersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: Watcher, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: WatcherUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Watcher]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncIterable[Watcher]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncIterable[Watcher]: ...


namespace azure.mgmt.databasewatcher.models

    class azure.mgmt.databasewatcher.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.databasewatcher.models.AlertRuleCreationProperties(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATED_WITH_ACTION_GROUP = "CreatedWithActionGroup"
        NONE = "None"


    class azure.mgmt.databasewatcher.models.AlertRuleResource(ProxyResource):
        id: str
        name: str
        properties: Optional[AlertRuleResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[AlertRuleResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.AlertRuleResourceProperties(Model):
        alert_rule_resource_id: str
        alert_rule_template_id: str
        alert_rule_template_version: str
        created_with_properties: Union[str, AlertRuleCreationProperties]
        creation_time: datetime
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                alert_rule_resource_id: str, 
                alert_rule_template_id: str, 
                alert_rule_template_version: str, 
                created_with_properties: Union[str, AlertRuleCreationProperties], 
                creation_time: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.databasewatcher.models.DatabaseWatcherProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.databasewatcher.models.Datastore(Model):
        adx_cluster_resource_id: Optional[str]
        kusto_cluster_display_name: Optional[str]
        kusto_cluster_uri: str
        kusto_data_ingestion_uri: str
        kusto_database_name: str
        kusto_management_url: str
        kusto_offering_type: Union[str, KustoOfferingType]

        @overload
        def __init__(
                self, 
                *, 
                adx_cluster_resource_id: Optional[str] = ..., 
                kusto_cluster_display_name: Optional[str] = ..., 
                kusto_cluster_uri: str, 
                kusto_data_ingestion_uri: str, 
                kusto_database_name: str, 
                kusto_management_url: str, 
                kusto_offering_type: Union[str, KustoOfferingType]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.ErrorAdditionalInfo(Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.databasewatcher.models.ErrorDetail(Model):
        additional_info: Optional[List[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[List[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.databasewatcher.models.ErrorResponse(Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.HealthValidation(ProxyResource):
        id: str
        name: str
        properties: Optional[HealthValidationProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[HealthValidationProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.HealthValidationProperties(Model):
        end_time: datetime
        issues: List[ValidationIssue]
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        start_time: datetime
        status: Union[str, ValidationStatus]


    class azure.mgmt.databasewatcher.models.KustoOfferingType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADX = "adx"
        FABRIC = "fabric"
        FREE = "free"


    class azure.mgmt.databasewatcher.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_AND_USER_ASSIGNED = "SystemAssigned, UserAssigned"
        SYSTEM_ASSIGNED = "SystemAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.databasewatcher.models.ManagedServiceIdentityV4(Model):
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


    class azure.mgmt.databasewatcher.models.Operation(Model):
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


    class azure.mgmt.databasewatcher.models.OperationDisplay(Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.databasewatcher.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.databasewatcher.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.databasewatcher.models.Resource(Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.databasewatcher.models.ResourceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.databasewatcher.models.SharedPrivateLinkResource(ProxyResource):
        id: str
        name: str
        properties: Optional[SharedPrivateLinkResourceProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[SharedPrivateLinkResourceProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.SharedPrivateLinkResourceProperties(Model):
        dns_zone: Optional[str]
        group_id: str
        private_link_resource_id: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        request_message: str
        status: Optional[Union[str, SharedPrivateLinkResourceStatus]]

        @overload
        def __init__(
                self, 
                *, 
                dns_zone: Optional[str] = ..., 
                group_id: str, 
                private_link_resource_id: str, 
                request_message: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.SharedPrivateLinkResourceStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPROVED = "Approved"
        DISCONNECTED = "Disconnected"
        PENDING = "Pending"
        REJECTED = "Rejected"


    class azure.mgmt.databasewatcher.models.SqlDbElasticPoolTargetProperties(TargetProperties, discriminator='SqlEp'):
        anchor_database_resource_id: str
        connection_server_name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        read_intent: Optional[bool]
        sql_ep_resource_id: str
        target_authentication_type: Union[str, TargetAuthenticationType]
        target_type: Literal["SqlEp"]
        target_vault: VaultSecret

        @overload
        def __init__(
                self, 
                *, 
                anchor_database_resource_id: str, 
                connection_server_name: str, 
                read_intent: Optional[bool] = ..., 
                sql_ep_resource_id: str, 
                target_authentication_type: Union[str, TargetAuthenticationType], 
                target_vault: Optional[VaultSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.SqlDbSingleDatabaseTargetProperties(TargetProperties, discriminator='SqlDb'):
        connection_server_name: str
        provisioning_state: Union[str, ResourceProvisioningState]
        read_intent: Optional[bool]
        sql_db_resource_id: str
        target_authentication_type: Union[str, TargetAuthenticationType]
        target_type: Literal["SqlDb"]
        target_vault: VaultSecret

        @overload
        def __init__(
                self, 
                *, 
                connection_server_name: str, 
                read_intent: Optional[bool] = ..., 
                sql_db_resource_id: str, 
                target_authentication_type: Union[str, TargetAuthenticationType], 
                target_vault: Optional[VaultSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.SqlMiTargetProperties(TargetProperties, discriminator='SqlMi'):
        connection_server_name: str
        connection_tcp_port: Optional[int]
        provisioning_state: Union[str, ResourceProvisioningState]
        read_intent: Optional[bool]
        sql_mi_resource_id: str
        target_authentication_type: Union[str, TargetAuthenticationType]
        target_type: Literal["SqlMi"]
        target_vault: VaultSecret

        @overload
        def __init__(
                self, 
                *, 
                connection_server_name: str, 
                connection_tcp_port: Optional[int] = ..., 
                read_intent: Optional[bool] = ..., 
                sql_mi_resource_id: str, 
                target_authentication_type: Union[str, TargetAuthenticationType], 
                target_vault: Optional[VaultSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.SystemData(Model):
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


    class azure.mgmt.databasewatcher.models.Target(ProxyResource):
        id: str
        name: str
        properties: Optional[TargetProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TargetProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.TargetAuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AAD = "Aad"
        SQL = "Sql"


    class azure.mgmt.databasewatcher.models.TargetProperties(Model):
        connection_server_name: str
        provisioning_state: Optional[Union[str, ResourceProvisioningState]]
        target_authentication_type: Union[str, TargetAuthenticationType]
        target_type: str
        target_vault: Optional[VaultSecret]

        @overload
        def __init__(
                self, 
                *, 
                connection_server_name: str, 
                target_authentication_type: Union[str, TargetAuthenticationType], 
                target_type: str, 
                target_vault: Optional[VaultSecret] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.TrackedResource(Resource):
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


    class azure.mgmt.databasewatcher.models.UserAssignedIdentity(Model):
        client_id: Optional[str]
        principal_id: Optional[str]


    class azure.mgmt.databasewatcher.models.ValidationIssue(Model):
        additional_details: Optional[str]
        error_code: str
        error_message: str
        recommendation_message: str
        recommendation_url: Optional[str]
        related_resource_id: Optional[str]
        related_resource_type: Optional[str]


    class azure.mgmt.databasewatcher.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        NOT_STARTED = "NotStarted"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        TIMED_OUT = "TimedOut"


    class azure.mgmt.databasewatcher.models.VaultSecret(Model):
        akv_resource_id: Optional[str]
        akv_target_password: Optional[str]
        akv_target_user: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                akv_resource_id: Optional[str] = ..., 
                akv_target_password: Optional[str] = ..., 
                akv_target_user: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.Watcher(TrackedResource):
        id: str
        identity: Optional[ManagedServiceIdentityV4]
        location: str
        name: str
        properties: Optional[WatcherProperties]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityV4] = ..., 
                location: str, 
                properties: Optional[WatcherProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.WatcherProperties(Model):
        datastore: Optional[Datastore]
        default_alert_rule_identity_resource_id: Optional[str]
        provisioning_state: Optional[Union[str, DatabaseWatcherProvisioningState]]
        status: Optional[Union[str, WatcherStatus]]

        @overload
        def __init__(
                self, 
                *, 
                datastore: Optional[Datastore] = ..., 
                default_alert_rule_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.WatcherStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        RUNNING = "Running"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"


    class azure.mgmt.databasewatcher.models.WatcherUpdate(Model):
        identity: Optional[ManagedServiceIdentityV4]
        properties: Optional[WatcherUpdateProperties]
        tags: Optional[Dict[str, str]]

        @overload
        def __init__(
                self, 
                *, 
                identity: Optional[ManagedServiceIdentityV4] = ..., 
                properties: Optional[WatcherUpdateProperties] = ..., 
                tags: Optional[Dict[str, str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.databasewatcher.models.WatcherUpdateProperties(Model):
        datastore: Optional[Datastore]
        default_alert_rule_identity_resource_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                datastore: Optional[Datastore] = ..., 
                default_alert_rule_identity_resource_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.databasewatcher.operations

    class azure.mgmt.databasewatcher.operations.AlertRuleResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: AlertRuleResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'alert_rule_resource_name', 'accept']})
        def delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'alert_rule_resource_name', 'accept']})
        def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                alert_rule_resource_name: str, 
                **kwargs: Any
            ) -> AlertRuleResource: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-07-19-preview', params_added_on={'2024-07-19-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'accept']})
        def list_by_parent(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Iterable[AlertRuleResource]: ...


    class azure.mgmt.databasewatcher.operations.HealthValidationsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'health_validation_name', 'accept']})
        def begin_start_validation(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                health_validation_name: str, 
                **kwargs: Any
            ) -> LROPoller[HealthValidation]: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'health_validation_name', 'accept']})
        def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                health_validation_name: str, 
                **kwargs: Any
            ) -> HealthValidation: ...

        @distributed_trace
        @api_version_validation(method_added_on='2024-10-01-preview', params_added_on={'2024-10-01-preview': ['api_version', 'subscription_id', 'resource_group_name', 'watcher_name', 'accept']})
        def list_by_parent(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Iterable[HealthValidation]: ...


    class azure.mgmt.databasewatcher.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @distributed_trace
        def list(self, **kwargs: Any) -> Iterable[Operation]: ...


    class azure.mgmt.databasewatcher.operations.SharedPrivateLinkResourcesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: SharedPrivateLinkResource, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SharedPrivateLinkResource]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                shared_private_link_resource_name: str, 
                **kwargs: Any
            ) -> SharedPrivateLinkResource: ...

        @distributed_trace
        def list_by_watcher(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Iterable[SharedPrivateLinkResource]: ...


    class azure.mgmt.databasewatcher.operations.TargetsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: Target, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @overload
        def create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                target_name: str, 
                **kwargs: Any
            ) -> Target: ...

        @distributed_trace
        def list_by_watcher(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Iterable[Target]: ...


    class azure.mgmt.databasewatcher.operations.WatchersOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ): ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: Watcher, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: WatcherUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: JSON, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                properties: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Watcher]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                watcher_name: str, 
                **kwargs: Any
            ) -> Watcher: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> Iterable[Watcher]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> Iterable[Watcher]: ...


```