```py
namespace azure.mgmt.migrate

    class azure.mgmt.migrate.MigrateClient: implements ContextManager 
        migrate_projects: MigrateProjectsOperations
        migration_entities: MigrationEntitiesOperations
        migration_entity_groups: MigrationEntityGroupsOperations
        operations: Operations
        tasks: TasksOperations
        waves: WavesOperations

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


namespace azure.mgmt.migrate.aio

    class azure.mgmt.migrate.aio.MigrateClient: implements AsyncContextManager 
        migrate_projects: MigrateProjectsOperations
        migration_entities: MigrationEntitiesOperations
        migration_entity_groups: MigrationEntityGroupsOperations
        operations: Operations
        tasks: TasksOperations
        waves: WavesOperations

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


namespace azure.mgmt.migrate.aio.operations

    class azure.mgmt.migrate.aio.operations.MigrateProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: CreateWavesFromPlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        async def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: CreateWavesFromPlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        async def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        async def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GenerateWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateWavePlanResponse]: ...

        @overload
        async def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GenerateWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateWavePlanResponse]: ...

        @overload
        async def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[GenerateWavePlanResponse]: ...

        @overload
        async def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ImportWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportWavePlanResponse]: ...

        @overload
        async def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ImportWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportWavePlanResponse]: ...

        @overload
        async def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[ImportWavePlanResponse]: ...

        @overload
        async def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: RefreshEntitiesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RefreshEntitiesResponse]: ...

        @overload
        async def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: RefreshEntitiesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RefreshEntitiesResponse]: ...

        @overload
        async def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[RefreshEntitiesResponse]: ...

        @overload
        async def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: FetchSasUriRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        async def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: FetchSasUriRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        async def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        async def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GetWavePlansRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...

        @overload
        async def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GetWavePlansRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...

        @overload
        async def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...


    class azure.mgmt.migrate.aio.operations.MigrationEntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: MigrationEntity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: MigrationEntity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntity]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntity]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                **kwargs: Any
            ) -> MigrationEntity: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationEntity]: ...


    class azure.mgmt.migrate.aio.operations.MigrationEntityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: MigrationEntityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntityGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: MigrationEntityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntityGroup]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationEntityGroup]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                **kwargs: Any
            ) -> MigrationEntityGroup: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationEntityGroup]: ...


    class azure.mgmt.migrate.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[Operation]: ...


    class azure.mgmt.migrate.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Task]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Task]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Task]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @overload
        async def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: TaskSummaryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @overload
        async def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: TaskSummaryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @overload
        async def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Task]: ...


    class azure.mgmt.migrate.aio.operations.WavesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: Wave, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Wave]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: Wave, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Wave]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[Wave]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> Wave: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Wave]: ...

        @distributed_trace_async
        async def refresh(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> WaveProperties: ...


namespace azure.mgmt.migrate.models

    class azure.mgmt.migrate.models.ActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        INTERNAL = "Internal"


    class azure.mgmt.migrate.models.Arg(_Model):
        query: str

        @overload
        def __init__(
                self, 
                *, 
                query: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.ArtifactProperties(_Model):
        artifact_id: str
        version_id: str


    class azure.mgmt.migrate.models.CreateWavesFromPlanRequest(_Model):
        assessment_arm_id: str
        migration_path: str
        wave_selection: Optional[list[WaveSelectionItem]]

        @overload
        def __init__(
                self, 
                *, 
                assessment_arm_id: str, 
                migration_path: str, 
                wave_selection: Optional[list[WaveSelectionItem]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.CreateWavesFromPlanResponse(_Model):
        expiration_time: Optional[datetime]
        failed_waves: int
        sas_uri: Optional[str]
        skipped_waves: int
        succeeded_waves: int
        total_waves: int


    class azure.mgmt.migrate.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.migrate.models.ErrorAdditionalInfo(_Model):
        info: Optional[Any]
        type: Optional[str]


    class azure.mgmt.migrate.models.ErrorDetail(_Model):
        additional_info: Optional[list[ErrorAdditionalInfo]]
        code: Optional[str]
        details: Optional[list[ErrorDetail]]
        message: Optional[str]
        target: Optional[str]


    class azure.mgmt.migrate.models.ErrorResponse(_Model):
        error: Optional[ErrorDetail]

        @overload
        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.FetchSasUriRequest(_Model):
        assessment_arm_id: str
        migration_path: str
        sas_version_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_arm_id: str, 
                migration_path: str, 
                sas_version_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.FetchSasUriResponse(_Model):
        expiration_time: datetime
        sas_uri: str


    class azure.mgmt.migrate.models.GenerateWavePlanRequest(_Model):
        assessment_arm_id: Optional[str]
        migration_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_arm_id: Optional[str] = ..., 
                migration_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.GenerateWavePlanResponse(_Model):
        artifact_properties: ArtifactProperties
        assessment_arm_id: str
        migration_path: str
        plan_source: Union[str, PlanSource]
        provisioning_state: Union[str, ProvisioningState]
        summary: Optional[WavePlanSummary]
        wave_plan_name: str


    class azure.mgmt.migrate.models.GetWavePlansRequest(_Model):
        assessment_arm_id: str
        migration_path: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_arm_id: str, 
                migration_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.GetWavePlansResponse(_Model):
        value: list[WavePlanListItem]

        @overload
        def __init__(
                self, 
                *, 
                value: list[WavePlanListItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.ImportWavePlanRequest(_Model):
        assessment_arm_id: str
        migration_path: str
        sas_version_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessment_arm_id: str, 
                migration_path: str, 
                sas_version_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.ImportWavePlanResponse(_Model):
        artifact_properties: ArtifactProperties
        assessment_arm_id: str
        migration_path: str
        plan_source: Union[str, PlanSource]
        provisioning_state: Union[str, ProvisioningState]
        wave_plan_name: str


    class azure.mgmt.migrate.models.MigrationEntity(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[MigrationEntityProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrationEntityProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.MigrationEntityGroup(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[MigrationEntityGroupProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[MigrationEntityGroupProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.MigrationEntityGroupProperties(_Model):
        application_display_name: str
        application_id: str
        associated_assessment_id: Optional[str]
        associated_wave_ids: Optional[list[str]]
        execution_start_date: Optional[datetime]
        execution_status: Optional[str]
        migration_path: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]

        @overload
        def __init__(
                self, 
                *, 
                application_display_name: str, 
                application_id: str, 
                associated_assessment_id: Optional[str] = ..., 
                associated_wave_ids: Optional[list[str]] = ..., 
                migration_path: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.MigrationEntityProperties(_Model):
        assessed_entity_arm_id: Optional[str]
        associated_assessment_id: Optional[str]
        associated_inventory_resource_id: str
        associated_migration_entity_group_ids: Optional[list[str]]
        associated_wave_id: Optional[str]
        execution_readiness: Optional[str]
        execution_stage: Optional[str]
        execution_start_date: Optional[datetime]
        execution_status: Optional[str]
        inventory_display_name: str
        migration_path: Optional[str]
        migration_specific_properties: Optional[MigrationSpecificPropertiesBase]
        migration_strategy: Optional[Union[str, Strategy]]
        migration_tool: Optional[str]
        partner_resource_arm_id: Optional[str]
        provisioning_state: Optional[Union[str, ProvisioningState]]
        target: Optional[str]
        target_azure_resource_arm_id: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                assessed_entity_arm_id: Optional[str] = ..., 
                associated_assessment_id: Optional[str] = ..., 
                associated_inventory_resource_id: str, 
                associated_migration_entity_group_ids: Optional[list[str]] = ..., 
                associated_wave_id: Optional[str] = ..., 
                inventory_display_name: str, 
                migration_path: Optional[str] = ..., 
                migration_specific_properties: Optional[MigrationSpecificPropertiesBase] = ..., 
                migration_tool: Optional[str] = ..., 
                partner_resource_arm_id: Optional[str] = ..., 
                target: Optional[str] = ..., 
                target_azure_resource_arm_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.MigrationSpecificPropertiesBase(_Model):
        instance_type: str

        @overload
        def __init__(
                self, 
                *, 
                instance_type: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.MigrationSpecificPropertiesInstanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVER_MIGRATION = "ServerMigration"


    class azure.mgmt.migrate.models.Operation(_Model):
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


    class azure.mgmt.migrate.models.OperationDisplay(_Model):
        description: Optional[str]
        operation: Optional[str]
        provider: Optional[str]
        resource: Optional[str]


    class azure.mgmt.migrate.models.Origin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"
        USER_SYSTEM = "user,system"


    class azure.mgmt.migrate.models.PlanSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IMPORTED = "Imported"
        SYSTEM_GENERATED = "SystemGenerated"


    class azure.mgmt.migrate.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        CANCELED = "Canceled"
        DELETING = "Deleting"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.migrate.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str


    class azure.mgmt.migrate.models.RefreshEntitiesRequest(_Model):
        migration_entity_group_ids: Optional[list[str]]
        migration_entity_ids: Optional[list[str]]

        @overload
        def __init__(
                self, 
                *, 
                migration_entity_group_ids: Optional[list[str]] = ..., 
                migration_entity_ids: Optional[list[str]] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.RefreshEntitiesResponse(_Model):
        migration_entity_group_ids: Optional[list[str]]
        migration_entity_ids: Optional[list[str]]


    class azure.mgmt.migrate.models.Resource(_Model):
        id: Optional[str]
        name: Optional[str]
        system_data: Optional[SystemData]
        type: Optional[str]


    class azure.mgmt.migrate.models.ServerMigrationSpecificProperties(MigrationSpecificPropertiesBase, discriminator='ServerMigration'):
        current_job_id: Optional[str]
        dr_appliance_inventory_id: Optional[str]
        instance_type: Literal[MigrationSpecificPropertiesInstanceType.SERVER_MIGRATION]

        @overload
        def __init__(
                self, 
                *, 
                current_job_id: Optional[str] = ..., 
                dr_appliance_inventory_id: Optional[str] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.Strategy(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        REARCHITECT = "Rearchitect"
        REBUILD = "Rebuild"
        REFACTOR = "Refactor"
        REHOST = "Rehost"
        REPLACE = "Replace"
        REPLATFORM = "Replatform"
        RETAIN = "Retain"
        RETIRE = "Retire"


    class azure.mgmt.migrate.models.SystemData(_Model):
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


    class azure.mgmt.migrate.models.Task(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[TaskProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[TaskProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskProperties(_Model):
        completion_date: Optional[datetime]
        description: Optional[str]
        display_name: str
        is_editable: bool
        provisioning_state: Optional[Union[str, ProvisioningState]]
        scope: Union[str, TaskScope]
        scope_id: str
        stage: Optional[str]
        status: str
        task_type: Union[str, TaskType]

        @overload
        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                display_name: str, 
                scope: Union[str, TaskScope], 
                scope_id: str, 
                stage: Optional[str] = ..., 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskScope(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MIGRATION_ENTITY = "MigrationEntity"
        MIGRATION_ENTITY_GROUP = "MigrationEntityGroup"
        WAVE = "Wave"


    class azure.mgmt.migrate.models.TaskStatusCountMap(_Model):
        count: int
        status: str

        @overload
        def __init__(
                self, 
                *, 
                count: int, 
                status: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskStatusCounts(_Model):
        status_counts: list[TaskStatusCountMap]

        @overload
        def __init__(
                self, 
                *, 
                status_counts: list[TaskStatusCountMap]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskSummaryItem(_Model):
        aggregated_status: str
        stage: str
        status_counts: TaskStatusCounts
        tasks: list[Task]

        @overload
        def __init__(
                self, 
                *, 
                aggregated_status: str, 
                stage: str, 
                status_counts: TaskStatusCounts, 
                tasks: list[Task]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskSummaryRequest(_Model):
        scope_id: str

        @overload
        def __init__(
                self, 
                *, 
                scope_id: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskSummaryResponse(_Model):
        items_property: list[TaskSummaryItem]

        @overload
        def __init__(
                self, 
                *, 
                items_property: list[TaskSummaryItem]
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.TaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM_DEFINED = "SystemDefined"
        USER_DEFINED = "UserDefined"


    class azure.mgmt.migrate.models.Wave(ProxyResource):
        e_tag: Optional[str]
        id: str
        name: str
        properties: Optional[WaveProperties]
        system_data: SystemData
        type: str

        @overload
        def __init__(
                self, 
                *, 
                properties: Optional[WaveProperties] = ...
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.WavePlanListItem(_Model):
        artifact_properties: ArtifactProperties
        assessment_arm_id: str
        migration_path: str
        plan_source: Union[str, PlanSource]
        provisioning_state: Union[str, ProvisioningState]
        summary: Optional[WavePlanSummary]
        wave_plan_name: str


    class azure.mgmt.migrate.models.WavePlanSummary(_Model):
        confidence: str
        number_of_waves: int
        risk: str


    class azure.mgmt.migrate.models.WaveProperties(_Model):
        actual_start_date: Optional[datetime]
        arg: Arg
        description: Optional[str]
        display_name: str
        planned_completion_date: Optional[datetime]
        planned_start_date: datetime
        provisioning_state: Optional[Union[str, ProvisioningState]]
        stage: Optional[str]
        status: Optional[str]

        @overload
        def __init__(
                self, 
                *, 
                arg: Arg, 
                description: Optional[str] = ..., 
                display_name: str, 
                planned_completion_date: Optional[datetime] = ..., 
                planned_start_date: datetime
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


    class azure.mgmt.migrate.models.WaveSelectionItem(_Model):
        wave_display_name: Optional[str]
        wave_name: str

        @overload
        def __init__(
                self, 
                *, 
                wave_display_name: Optional[str] = ..., 
                wave_name: str
            ) -> None: ...

        @overload
        def __init__(self, mapping: Mapping[str, Any]) -> None: ...


namespace azure.mgmt.migrate.operations

    class azure.mgmt.migrate.operations.MigrateProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: CreateWavesFromPlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: CreateWavesFromPlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        def begin_create_waves_from_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[CreateWavesFromPlanResponse]: ...

        @overload
        def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GenerateWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateWavePlanResponse]: ...

        @overload
        def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GenerateWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateWavePlanResponse]: ...

        @overload
        def begin_generate_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[GenerateWavePlanResponse]: ...

        @overload
        def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ImportWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportWavePlanResponse]: ...

        @overload
        def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: ImportWavePlanRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportWavePlanResponse]: ...

        @overload
        def begin_import_wave_plan(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[ImportWavePlanResponse]: ...

        @overload
        def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: RefreshEntitiesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RefreshEntitiesResponse]: ...

        @overload
        def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: RefreshEntitiesRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RefreshEntitiesResponse]: ...

        @overload
        def begin_refresh_entities(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[RefreshEntitiesResponse]: ...

        @overload
        def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: FetchSasUriRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: FetchSasUriRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        def fetch_sas_uri(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> FetchSasUriResponse: ...

        @overload
        def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GetWavePlansRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...

        @overload
        def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: GetWavePlansRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...

        @overload
        def get_wave_plans(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> GetWavePlansResponse: ...


    class azure.mgmt.migrate.operations.MigrationEntitiesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: MigrationEntity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: MigrationEntity, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntity]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntity]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_name: str, 
                **kwargs: Any
            ) -> MigrationEntity: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MigrationEntity]: ...


    class azure.mgmt.migrate.operations.MigrationEntityGroupsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: MigrationEntityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntityGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: MigrationEntityGroup, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntityGroup]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationEntityGroup]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                migration_entity_group_name: str, 
                **kwargs: Any
            ) -> MigrationEntityGroup: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MigrationEntityGroup]: ...


    class azure.mgmt.migrate.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[Operation]: ...


    class azure.mgmt.migrate.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Task]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: Task, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Task]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Task]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> Task: ...

        @overload
        def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: TaskSummaryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @overload
        def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: TaskSummaryRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @overload
        def get_summary(
                self, 
                resource_group_name: str, 
                project_name: str, 
                body: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> TaskSummaryResponse: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Task]: ...


    class azure.mgmt.migrate.operations.WavesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: Wave, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Wave]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: Wave, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Wave]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                resource: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[Wave]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> Wave: ...

        @distributed_trace
        def list_by_parent(
                self, 
                resource_group_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Wave]: ...

        @distributed_trace
        def refresh(
                self, 
                resource_group_name: str, 
                project_name: str, 
                wave_name: str, 
                **kwargs: Any
            ) -> WaveProperties: ...


namespace azure.mgmt.migrate.types

    class azure.mgmt.migrate.types.Arg(TypedDict, total=False):
        key "query": Required[str]
        query: str


    class azure.mgmt.migrate.types.CreateWavesFromPlanRequest(TypedDict, total=False):
        key "assessmentArmId": Required[str]
        key "migrationPath": Required[str]
        assessmentArmId: str
        migrationPath: str
        waveSelection: list[WaveSelectionItem]


    class azure.mgmt.migrate.types.FetchSasUriRequest(TypedDict, total=False):
        key "assessmentArmId": Required[str]
        key "migrationPath": Required[str]
        key "sasVersionId": str
        assessmentArmId: str
        migrationPath: str
        sasVersionId: str


    class azure.mgmt.migrate.types.GenerateWavePlanRequest(TypedDict, total=False):
        key "assessmentArmId": str
        key "migrationPath": str
        assessmentArmId: str
        migrationPath: str


    class azure.mgmt.migrate.types.GetWavePlansRequest(TypedDict, total=False):
        key "assessmentArmId": Required[str]
        key "migrationPath": str
        assessmentArmId: str
        migrationPath: str


    class azure.mgmt.migrate.types.ImportWavePlanRequest(TypedDict, total=False):
        key "assessmentArmId": Required[str]
        key "migrationPath": Required[str]
        key "sasVersionId": str
        assessmentArmId: str
        migrationPath: str
        sasVersionId: str


    class azure.mgmt.migrate.types.MigrationEntity(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('MigrationEntityProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: MigrationEntityProperties
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.MigrationEntityGroup(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('MigrationEntityGroupProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: MigrationEntityGroupProperties
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.MigrationEntityGroupProperties(TypedDict, total=False):
        key "applicationDisplayName": Required[str]
        key "applicationId": Required[str]
        key "associatedAssessmentId": str
        key "executionStartDate": str
        key "executionStatus": str
        key "migrationPath": str
        key "provisioningState": Union[str, ProvisioningState]
        applicationDisplayName: str
        applicationId: str
        associatedAssessmentId: str
        associatedWaveIds: list[str]
        executionStartDate: str
        executionStatus: str
        migrationPath: str
        provisioningState: Union[str, ProvisioningState]


    class azure.mgmt.migrate.types.MigrationEntityProperties(TypedDict, total=False):
        key "assessedEntityArmId": str
        key "associatedAssessmentId": str
        key "associatedInventoryResourceId": Required[str]
        key "associatedWaveId": str
        key "executionReadiness": str
        key "executionStage": str
        key "executionStartDate": str
        key "executionStatus": str
        key "inventoryDisplayName": Required[str]
        key "migrationPath": str
        key "migrationSpecificProperties": ForwardRef('MigrationSpecificPropertiesBase', module='types')
        key "migrationStrategy": Union[str, Strategy]
        key "migrationTool": str
        key "partnerResourceArmId": str
        key "provisioningState": Union[str, ProvisioningState]
        key "target": str
        key "targetAzureResourceArmId": str
        assessedEntityArmId: str
        associatedAssessmentId: str
        associatedInventoryResourceId: str
        associatedMigrationEntityGroupIds: list[str]
        associatedWaveId: str
        executionReadiness: str
        executionStage: str
        executionStartDate: str
        executionStatus: str
        inventoryDisplayName: str
        migrationPath: str
        migrationSpecificProperties: MigrationSpecificPropertiesBase
        migrationStrategy: Union[str, Strategy]
        migrationTool: str
        partnerResourceArmId: str
        provisioningState: Union[str, ProvisioningState]
        target: str
        targetAzureResourceArmId: str


    class azure.mgmt.migrate.types.MigrationSpecificPropertiesBase(TypedDict, total=False):
        key "currentJobId": str
        key "drApplianceInventoryId": str
        key "instanceType": Required[Literal[MigrationSpecificPropertiesInstanceType.SERVER_MIGRATION]]
        currentJobId: str
        drApplianceInventoryId: str
        instanceType: Literal[MigrationSpecificPropertiesInstanceType.SERVER_MIGRATION]


    class azure.mgmt.migrate.types.MigrationSpecificPropertiesInstanceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SERVER_MIGRATION = "ServerMigration"


    class azure.mgmt.migrate.types.ProxyResource(Resource):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.RefreshEntitiesRequest(TypedDict, total=False):
        migrationEntityGroupIds: list[str]
        migrationEntityIds: list[str]


    class azure.mgmt.migrate.types.Resource(TypedDict, total=False):
        key "id": str
        key "name": str
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        id: str
        name: str
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.ServerMigrationSpecificProperties(TypedDict, total=False):
        key "currentJobId": str
        key "drApplianceInventoryId": str
        key "instanceType": Required[Literal[MigrationSpecificPropertiesInstanceType.SERVER_MIGRATION]]
        currentJobId: str
        drApplianceInventoryId: str
        instanceType: Literal[MigrationSpecificPropertiesInstanceType.SERVER_MIGRATION]


    class azure.mgmt.migrate.types.SystemData(TypedDict, total=False):
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


    class azure.mgmt.migrate.types.Task(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('TaskProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: TaskProperties
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.TaskProperties(TypedDict, total=False):
        key "completionDate": str
        key "description": str
        key "displayName": Required[str]
        key "isEditable": Required[bool]
        key "provisioningState": Union[str, ProvisioningState]
        key "scope": Required[Union[str, TaskScope]]
        key "scopeId": Required[str]
        key "stage": str
        key "status": Required[str]
        key "taskType": Required[Union[str, TaskType]]
        completionDate: str
        description: str
        displayName: str
        isEditable: bool
        provisioningState: Union[str, ProvisioningState]
        scope: Union[str, TaskScope]
        scopeId: str
        stage: str
        status: str
        taskType: Union[str, TaskType]


    class azure.mgmt.migrate.types.TaskSummaryRequest(TypedDict, total=False):
        key "scopeId": Required[str]
        scopeId: str


    class azure.mgmt.migrate.types.Wave(ProxyResource):
        key "eTag": str
        key "id": str
        key "name": str
        key "properties": ForwardRef('WaveProperties', module='types')
        key "systemData": ForwardRef('SystemData', module='types')
        key "type": str
        eTag: str
        id: str
        name: str
        properties: WaveProperties
        systemData: SystemData
        type: str


    class azure.mgmt.migrate.types.WaveProperties(TypedDict, total=False):
        key "actualStartDate": str
        key "arg": Required[Arg]
        key "description": str
        key "displayName": Required[str]
        key "plannedCompletionDate": str
        key "plannedStartDate": Required[str]
        key "provisioningState": Union[str, ProvisioningState]
        key "stage": str
        key "status": str
        actualStartDate: str
        arg: Arg
        description: str
        displayName: str
        plannedCompletionDate: str
        plannedStartDate: str
        provisioningState: Union[str, ProvisioningState]
        stage: str
        status: str


    class azure.mgmt.migrate.types.WaveSelectionItem(TypedDict, total=False):
        key "waveDisplayName": str
        key "waveName": Required[str]
        waveDisplayName: str
        waveName: str


```