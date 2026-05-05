```py
# Package is parsed using apiview-stub-generator(version:0.3.28), Python version: 3.11.15


namespace azure.mgmt.datamigration

    class azure.mgmt.datamigration.DataMigrationManagementClient: implements ContextManager 
        database_migrations_mongo_to_cosmos_db_ru_mongo: DatabaseMigrationsMongoToCosmosDbRUMongoOperations
        database_migrations_mongo_to_cosmos_dbv_core_mongo: DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations
        database_migrations_sql_db: DatabaseMigrationsSqlDbOperations
        database_migrations_sql_mi: DatabaseMigrationsSqlMiOperations
        database_migrations_sql_vm: DatabaseMigrationsSqlVmOperations
        files: FilesOperations
        migration_services: MigrationServicesOperations
        operations: Operations
        projects: ProjectsOperations
        resource_skus: ResourceSkusOperations
        service_tasks: ServiceTasksOperations
        services: ServicesOperations
        sql_migration_services: SqlMigrationServicesOperations
        tasks: TasksOperations
        usages: UsagesOperations

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


namespace azure.mgmt.datamigration.aio

    class azure.mgmt.datamigration.aio.DataMigrationManagementClient: implements AsyncContextManager 
        database_migrations_mongo_to_cosmos_db_ru_mongo: DatabaseMigrationsMongoToCosmosDbRUMongoOperations
        database_migrations_mongo_to_cosmos_dbv_core_mongo: DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations
        database_migrations_sql_db: DatabaseMigrationsSqlDbOperations
        database_migrations_sql_mi: DatabaseMigrationsSqlMiOperations
        database_migrations_sql_vm: DatabaseMigrationsSqlVmOperations
        files: FilesOperations
        migration_services: MigrationServicesOperations
        operations: Operations
        projects: ProjectsOperations
        resource_skus: ResourceSkusOperations
        service_tasks: ServiceTasksOperations
        services: ServicesOperations
        sql_migration_services: SqlMigrationServicesOperations
        tasks: TasksOperations
        usages: UsagesOperations

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


namespace azure.mgmt.datamigration.aio.operations

    class azure.mgmt.datamigration.aio.operations.DatabaseMigrationsMongoToCosmosDbRUMongoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: DatabaseMigrationCosmosDbMongo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> DatabaseMigrationCosmosDbMongo: ...

        @distributed_trace
        def get_for_scope(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabaseMigrationCosmosDbMongo]: ...


    class azure.mgmt.datamigration.aio.operations.DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: DatabaseMigrationCosmosDbMongo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @overload
        async def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> DatabaseMigrationCosmosDbMongo: ...

        @distributed_trace
        def get_for_scope(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabaseMigrationCosmosDbMongo]: ...


    class azure.mgmt.datamigration.aio.operations.DatabaseMigrationsSqlDbOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlDb, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlDb]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlDb]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_retry(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_input: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlDb]: ...

        @overload
        async def begin_retry(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlDb]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlDb: ...


    class azure.mgmt.datamigration.aio.operations.DatabaseMigrationsSqlMiOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlMi, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlMi]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlMi]: ...

        @overload
        async def begin_cutover(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cutover(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlMi]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlMi: ...


    class azure.mgmt.datamigration.aio.operations.DatabaseMigrationsSqlVmOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlVm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlVm]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlVm]: ...

        @overload
        async def begin_cutover(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_cutover(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[DatabaseMigrationSqlVm]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlVm: ...


    class azure.mgmt.datamigration.aio.operations.FilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: ProjectFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> ProjectFile: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectFile]: ...

        @distributed_trace_async
        async def read(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileStorageInfo: ...

        @distributed_trace_async
        async def read_write(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileStorageInfo: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: ProjectFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...


    class azure.mgmt.datamigration.aio.operations.MigrationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: MigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: MigrationServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[MigrationService]: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> MigrationService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[MigrationService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[MigrationService]: ...

        @distributed_trace
        def list_migrations(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabaseMigrationBase]: ...


    class azure.mgmt.datamigration.aio.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[OperationsDefinition]: ...


    class azure.mgmt.datamigration.aio.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Project]: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...


    class azure.mgmt.datamigration.aio.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> AsyncItemPaged[ResourceSku]: ...


    class azure.mgmt.datamigration.aio.operations.ServiceTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                task_type: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectTask]: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...


    class azure.mgmt.datamigration.aio.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: DataMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataMigrationService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataMigrationService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                group_name: str, 
                service_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_start(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @distributed_trace_async
        async def begin_stop(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: DataMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataMigrationService]: ...

        @overload
        async def begin_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[DataMigrationService]: ...

        @overload
        async def check_children_name_availability(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        async def check_children_name_availability(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        async def check_name_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @distributed_trace_async
        async def check_status(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> DataMigrationServiceStatusResponse: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> DataMigrationService: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> AsyncItemPaged[DataMigrationService]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DataMigrationService]: ...

        @distributed_trace
        def list_skus(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[AvailableServiceSku]: ...


    class azure.mgmt.datamigration.aio.operations.SqlMigrationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: SqlMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlMigrationService]: ...

        @overload
        async def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlMigrationService]: ...

        @distributed_trace_async
        async def begin_delete(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> AsyncLROPoller[None]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: SqlMigrationServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlMigrationService]: ...

        @overload
        async def begin_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> AsyncLROPoller[SqlMigrationService]: ...

        @overload
        async def delete_node(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: DeleteNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteNode: ...

        @overload
        async def delete_node(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteNode: ...

        @distributed_trace_async
        async def get(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> SqlMigrationService: ...

        @distributed_trace_async
        async def list_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> AuthenticationKeys: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[SqlMigrationService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> AsyncItemPaged[SqlMigrationService]: ...

        @distributed_trace
        def list_migrations(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[DatabaseMigration]: ...

        @distributed_trace_async
        async def list_monitoring_data(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> IntegrationRuntimeMonitoringData: ...

        @overload
        async def regenerate_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: RegenAuthKeys, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegenAuthKeys: ...

        @overload
        async def regenerate_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegenAuthKeys: ...


    class azure.mgmt.datamigration.aio.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace_async
        async def cancel(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def command(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: CommandProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommandProperties: ...

        @overload
        async def command(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommandProperties: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace_async
        async def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace_async
        async def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_type: Optional[str] = None, 
                **kwargs: Any
            ) -> AsyncItemPaged[ProjectTask]: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        async def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...


    class azure.mgmt.datamigration.aio.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> AsyncItemPaged[Quota]: ...


namespace azure.mgmt.datamigration.models

    class azure.mgmt.datamigration.models.ApiError(Model):
        error: ODataError
        system_data: SystemDataAutoGenerated

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ODataError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AuthType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCOUNT_KEY = "AccountKey"
        MANAGED_IDENTITY = "ManagedIdentity"


    class azure.mgmt.datamigration.models.AuthenticationKeys(Model):
        auth_key1: str
        auth_key2: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_key1: Optional[str] = ..., 
                auth_key2: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AuthenticationType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTIVE_DIRECTORY_INTEGRATED = "ActiveDirectoryIntegrated"
        ACTIVE_DIRECTORY_PASSWORD = "ActiveDirectoryPassword"
        NONE = "None"
        SQL_AUTHENTICATION = "SqlAuthentication"
        WINDOWS_AUTHENTICATION = "WindowsAuthentication"


    class azure.mgmt.datamigration.models.AvailableServiceSku(Model):
        capacity: AvailableServiceSkuCapacity
        resource_type: str
        sku: AvailableServiceSkuSku

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[AvailableServiceSkuCapacity] = ..., 
                resource_type: Optional[str] = ..., 
                sku: Optional[AvailableServiceSkuSku] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AvailableServiceSkuCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, ServiceScalability]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                default: Optional[int] = ..., 
                maximum: Optional[int] = ..., 
                minimum: Optional[int] = ..., 
                scale_type: Optional[Union[str, ServiceScalability]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AvailableServiceSkuSku(Model):
        family: str
        name: str
        size: str
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                family: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AzureActiveDirectoryApp(Model):
        app_key: str
        application_id: str
        ignore_azure_permissions: bool
        tenant_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                app_key: Optional[str] = ..., 
                application_id: Optional[str] = ..., 
                ignore_azure_permissions: Optional[bool] = ..., 
                tenant_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.AzureBlob(Model):
        account_key: str
        auth_type: Union[str, AuthType]
        blob_container_name: str
        identity: ManagedServiceIdentity
        storage_account_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                auth_type: Optional[Union[str, AuthType]] = ..., 
                blob_container_name: Optional[str] = ..., 
                identity: Optional[ManagedServiceIdentity] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.BackupConfiguration(Model):
        source_location: SourceLocation
        target_location: TargetLocation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_location: Optional[SourceLocation] = ..., 
                target_location: Optional[TargetLocation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.BackupFileInfo(Model):
        family_sequence_number: int
        file_location: str
        status: Union[str, BackupFileStatus]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                family_sequence_number: Optional[int] = ..., 
                file_location: Optional[str] = ..., 
                status: Optional[Union[str, BackupFileStatus]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.BackupFileStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ARRIVED = "Arrived"
        CANCELLED = "Cancelled"
        QUEUED = "Queued"
        RESTORED = "Restored"
        RESTORING = "Restoring"
        UPLOADED = "Uploaded"
        UPLOADING = "Uploading"


    class azure.mgmt.datamigration.models.BackupMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CREATE_BACKUP = "CreateBackup"
        EXISTING_BACKUP = "ExistingBackup"


    class azure.mgmt.datamigration.models.BackupSetInfo(Model):
        backup_finished_date: datetime
        backup_set_id: str
        backup_start_date: datetime
        backup_type: Union[str, BackupType]
        database_name: str
        first_lsn: str
        is_backup_restored: bool
        last_lsn: str
        last_modified_time: datetime
        list_of_backup_files: list[BackupFileInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_finished_date: Optional[datetime] = ..., 
                backup_set_id: Optional[str] = ..., 
                backup_start_date: Optional[datetime] = ..., 
                backup_type: Optional[Union[str, BackupType]] = ..., 
                database_name: Optional[str] = ..., 
                first_lsn: Optional[str] = ..., 
                is_backup_restored: Optional[bool] = ..., 
                last_lsn: Optional[str] = ..., 
                last_modified_time: Optional[datetime] = ..., 
                list_of_backup_files: Optional[List[BackupFileInfo]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.BackupType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DATABASE = "Database"
        DIFFERENTIAL_DATABASE = "DifferentialDatabase"
        DIFFERENTIAL_FILE = "DifferentialFile"
        DIFFERENTIAL_PARTIAL = "DifferentialPartial"
        FILE = "File"
        PARTIAL = "Partial"
        TRANSACTION_LOG = "TransactionLog"


    class azure.mgmt.datamigration.models.BlobShare(Model):
        sas_uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                sas_uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CheckOCIDriverTaskInput(Model):
        server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                server_version: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CheckOCIDriverTaskOutput(Model):
        installed_driver: OracleOCIDriverInfo
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                installed_driver: Optional[OracleOCIDriverInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CheckOCIDriverTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: CheckOCIDriverTaskInput
        output: list[CheckOCIDriverTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[CheckOCIDriverTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CommandProperties(Model):
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CommandState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        FAILED = "Failed"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.datamigration.models.CommandType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCEL = "cancel"
        FINISH = "finish"
        MIGRATE_SQL_SERVER_AZURE_DB_SQL_MI_COMPLETE = "Migrate.SqlServer.AzureDbSqlMi.Complete"
        MIGRATE_SYNC_COMPLETE_DATABASE = "Migrate.Sync.Complete.Database"
        RESTART = "restart"


    class azure.mgmt.datamigration.models.ConnectToMongoDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MongoDbConnectionInfo
        output: list[MongoDbClusterInfo]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MongoDbConnectionInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceMySqlTaskInput(Model):
        check_permissions_group: Union[str, ServerLevelPermissionsGroup]
        is_offline_migration: bool
        source_connection_info: MySqlConnectionInfo
        target_platform: Union[str, MySqlTargetPlatformType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                check_permissions_group: Optional[Union[str, ServerLevelPermissionsGroup]] = ..., 
                is_offline_migration: bool = False, 
                source_connection_info: MySqlConnectionInfo, 
                target_platform: Optional[Union[str, MySqlTargetPlatformType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceMySqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToSourceMySqlTaskInput
        output: list[ConnectToSourceNonSqlTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToSourceMySqlTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceNonSqlTaskOutput(Model):
        databases: list[str]
        id: str
        server_properties: ServerProperties
        source_server_brand_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceOracleSyncTaskInput(Model):
        source_connection_info: OracleConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: OracleConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceOracleSyncTaskOutput(Model):
        databases: list[str]
        source_server_brand_version: str
        source_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceOracleSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToSourceOracleSyncTaskInput
        output: list[ConnectToSourceOracleSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToSourceOracleSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourcePostgreSqlSyncTaskInput(Model):
        source_connection_info: PostgreSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: PostgreSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourcePostgreSqlSyncTaskOutput(Model):
        databases: list[str]
        id: str
        source_server_brand_version: str
        source_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourcePostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToSourcePostgreSqlSyncTaskInput
        output: list[ConnectToSourcePostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToSourcePostgreSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToSourceSqlServerTaskInput
        output: list[ConnectToSourceSqlServerTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToSourceSqlServerTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskInput(Model):
        check_permissions_group: Union[str, ServerLevelPermissionsGroup]
        collect_agent_jobs: bool
        collect_databases: bool
        collect_logins: bool
        collect_tde_certificate_info: bool
        encrypted_key_for_secure_fields: str
        source_connection_info: SqlConnectionInfo
        validate_ssis_catalog_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                check_permissions_group: Optional[Union[str, ServerLevelPermissionsGroup]] = ..., 
                collect_agent_jobs: bool = False, 
                collect_databases: bool = True, 
                collect_logins: bool = False, 
                collect_tde_certificate_info: bool = False, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                source_connection_info: SqlConnectionInfo, 
                validate_ssis_catalog_only: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskOutputAgentJobLevel(ConnectToSourceSqlServerTaskOutput):
        id: str
        is_enabled: bool
        job_category: str
        job_owner: str
        last_executed_on: datetime
        migration_eligibility: MigrationEligibilityInfo
        name: str
        result_type: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskOutputDatabaseLevel(ConnectToSourceSqlServerTaskOutput):
        compatibility_level: Union[str, DatabaseCompatLevel]
        database_files: list[DatabaseFileInfo]
        database_state: Union[str, DatabaseState]
        id: str
        name: str
        result_type: str
        size_mb: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskOutputLoginLevel(ConnectToSourceSqlServerTaskOutput):
        default_database: str
        id: str
        is_enabled: bool
        login_type: Union[str, LoginType]
        migration_eligibility: MigrationEligibilityInfo
        name: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskOutputTaskLevel(ConnectToSourceSqlServerTaskOutput):
        agent_jobs: str
        database_tde_certificate_mapping: str
        databases: str
        id: str
        logins: str
        result_type: str
        source_server_brand_version: str
        source_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToSourceSqlServerTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToSourceSqlServerTaskInput
        output: list[ConnectToSourceSqlServerTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToSourceSqlServerTaskInput] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForMySqlTaskInput(Model):
        is_offline_migration: bool
        source_connection_info: MySqlConnectionInfo
        target_connection_info: MySqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_offline_migration: bool = False, 
                source_connection_info: MySqlConnectionInfo, 
                target_connection_info: MySqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForMySqlTaskOutput(Model):
        databases: list[str]
        id: str
        server_version: str
        target_server_brand_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForMySqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetAzureDbForMySqlTaskInput
        output: list[ConnectToTargetAzureDbForMySqlTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetAzureDbForMySqlTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForPostgreSqlSyncTaskInput(Model):
        source_connection_info: PostgreSqlConnectionInfo
        target_connection_info: PostgreSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: PostgreSqlConnectionInfo, 
                target_connection_info: PostgreSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForPostgreSqlSyncTaskOutput(Model):
        databases: list[str]
        id: str
        target_server_brand_version: str
        target_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetAzureDbForPostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetAzureDbForPostgreSqlSyncTaskInput
        output: list[ConnectToTargetAzureDbForPostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetAzureDbForPostgreSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskInput(Model):
        target_connection_info: PostgreSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                target_connection_info: PostgreSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskOutput(Model):
        database_schema_map: list[ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskOutputDatabaseSchemaMapItem]
        databases: list[str]
        target_server_brand_version: str
        target_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_schema_map: Optional[List[ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskOutputDatabaseSchemaMapItem]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskOutputDatabaseSchemaMapItem(Model):
        database: str
        schemas: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database: Optional[str] = ..., 
                schemas: Optional[List[str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskInput
        output: list[ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetOracleAzureDbForPostgreSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlDbSyncTaskInput(Model):
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlDbSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetSqlDbSyncTaskInput
        output: list[ConnectToTargetSqlDbTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetSqlDbSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlDbTaskInput(Model):
        query_object_counts: bool
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query_object_counts: Optional[bool] = ..., 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlDbTaskOutput(Model):
        databases: str
        id: str
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: ConnectToTargetSqlDbTaskInput
        output: list[ConnectToTargetSqlDbTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[ConnectToTargetSqlDbTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMISyncTaskInput(Model):
        azure_app: AzureActiveDirectoryApp
        target_connection_info: MiSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_app: AzureActiveDirectoryApp, 
                target_connection_info: MiSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMISyncTaskOutput(Model):
        target_server_brand_version: str
        target_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMISyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetSqlMISyncTaskInput
        output: list[ConnectToTargetSqlMISyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetSqlMISyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMITaskInput(Model):
        collect_agent_jobs: bool
        collect_logins: bool
        target_connection_info: SqlConnectionInfo
        validate_ssis_catalog_only: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collect_agent_jobs: bool = True, 
                collect_logins: bool = True, 
                target_connection_info: SqlConnectionInfo, 
                validate_ssis_catalog_only: bool = False, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMITaskOutput(Model):
        agent_jobs: list[str]
        id: str
        logins: list[str]
        target_server_brand_version: str
        target_server_version: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectToTargetSqlMITaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ConnectToTargetSqlMITaskInput
        output: list[ConnectToTargetSqlMITaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ConnectToTargetSqlMITaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ConnectionInfo(Model):
        password: str
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CopyProgressDetails(Model):
        copy_duration: int
        copy_start: datetime
        copy_throughput: float
        data_read: int
        data_written: int
        parallel_copy_type: str
        rows_copied: int
        rows_read: int
        status: str
        table_name: str
        used_parallel_copies: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.CreatedByType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        APPLICATION = "Application"
        KEY = "Key"
        MANAGED_IDENTITY = "ManagedIdentity"
        USER = "User"


    class azure.mgmt.datamigration.models.DataIntegrityValidationResult(Model):
        failed_objects: dict[str, str]
        validation_errors: ValidationError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                failed_objects: Optional[Dict[str, str]] = ..., 
                validation_errors: Optional[ValidationError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataItemMigrationSummaryResult(Model):
        ended_on: datetime
        error_prefix: str
        items_completed_count: int
        items_count: int
        name: str
        result_prefix: str
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataMigrationError(Model):
        message: str
        type: Union[str, ErrorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Optional[Union[str, ErrorType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataMigrationProjectMetadata(Model):
        selected_migration_tables: list[MigrationTableMetadata]
        source_server_name: str
        source_server_port: str
        source_username: str
        target_db_name: str
        target_server_name: str
        target_username: str
        target_using_win_auth: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataMigrationResultCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FATAL_ERROR = "FatalError"
        INITIAL = "Initial"
        OBJECT_NOT_EXISTS_IN_SOURCE = "ObjectNotExistsInSource"
        OBJECT_NOT_EXISTS_IN_TARGET = "ObjectNotExistsInTarget"
        TARGET_OBJECT_IS_INACCESSIBLE = "TargetObjectIsInaccessible"


    class azure.mgmt.datamigration.models.DataMigrationService(TrackedResourceAutoGenerated):
        auto_stop_delay: str
        delete_resources_on_stop: bool
        etag: str
        id: str
        kind: str
        location: str
        name: str
        provisioning_state: Union[str, ServiceProvisioningState]
        public_key: str
        sku: ServiceSku
        system_data: SystemDataAutoGenerated
        tags: dict[str, str]
        type: str
        virtual_nic_id: str
        virtual_subnet_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auto_stop_delay: Optional[str] = ..., 
                delete_resources_on_stop: Optional[bool] = ..., 
                etag: Optional[str] = ..., 
                kind: Optional[str] = ..., 
                location: Optional[str] = ..., 
                public_key: Optional[str] = ..., 
                sku: Optional[ServiceSku] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                virtual_nic_id: Optional[str] = ..., 
                virtual_subnet_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataMigrationServiceList(Model):
        next_link: str
        value: list[DataMigrationService]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[DataMigrationService]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DataMigrationServiceStatusResponse(Model):
        agent_configuration: JSON
        agent_version: str
        status: str
        supported_task_types: list[str]
        vm_size: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                agent_configuration: Optional[JSON] = ..., 
                agent_version: Optional[str] = ..., 
                status: Optional[str] = ..., 
                supported_task_types: Optional[List[str]] = ..., 
                vm_size: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.Database(Model):
        collation: str
        compatibility_level: Union[str, DatabaseCompatLevel]
        database_state: Union[str, DatabaseState]
        fqdn: str
        id: str
        install_id: str
        name: str
        server_core_count: int
        server_default_backup_path: str
        server_default_data_path: str
        server_default_log_path: str
        server_edition: str
        server_id: str
        server_level: str
        server_name: str
        server_version: str
        server_visible_online_core_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collation: Optional[str] = ..., 
                compatibility_level: Optional[Union[str, DatabaseCompatLevel]] = ..., 
                database_state: Optional[Union[str, DatabaseState]] = ..., 
                fqdn: Optional[str] = ..., 
                id: Optional[str] = ..., 
                install_id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                server_core_count: Optional[int] = ..., 
                server_default_backup_path: Optional[str] = ..., 
                server_default_data_path: Optional[str] = ..., 
                server_default_log_path: Optional[str] = ..., 
                server_edition: Optional[str] = ..., 
                server_id: Optional[str] = ..., 
                server_level: Optional[str] = ..., 
                server_name: Optional[str] = ..., 
                server_version: Optional[str] = ..., 
                server_visible_online_core_count: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseBackupInfo(Model):
        backup_files: list[str]
        backup_finish_date: datetime
        backup_type: Union[str, BackupType]
        database_name: str
        family_count: int
        is_compressed: bool
        is_damaged: bool
        position: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseCompatLevel(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPAT_LEVEL100 = "CompatLevel100"
        COMPAT_LEVEL110 = "CompatLevel110"
        COMPAT_LEVEL120 = "CompatLevel120"
        COMPAT_LEVEL130 = "CompatLevel130"
        COMPAT_LEVEL140 = "CompatLevel140"
        COMPAT_LEVEL80 = "CompatLevel80"
        COMPAT_LEVEL90 = "CompatLevel90"


    class azure.mgmt.datamigration.models.DatabaseFileInfo(Model):
        database_name: str
        file_type: Union[str, DatabaseFileType]
        id: str
        logical_name: str
        physical_full_name: str
        restore_full_name: str
        size_mb: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                file_type: Optional[Union[str, DatabaseFileType]] = ..., 
                id: Optional[str] = ..., 
                logical_name: Optional[str] = ..., 
                physical_full_name: Optional[str] = ..., 
                restore_full_name: Optional[str] = ..., 
                size_mb: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseFileInput(Model):
        file_type: Union[str, DatabaseFileType]
        id: str
        logical_name: str
        physical_full_name: str
        restore_full_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_type: Optional[Union[str, DatabaseFileType]] = ..., 
                id: Optional[str] = ..., 
                logical_name: Optional[str] = ..., 
                physical_full_name: Optional[str] = ..., 
                restore_full_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseFileType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FILESTREAM = "Filestream"
        FULLTEXT = "Fulltext"
        LOG = "Log"
        NOT_SUPPORTED = "NotSupported"
        ROWS = "Rows"


    class azure.mgmt.datamigration.models.DatabaseInfo(Model):
        source_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_database_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigration(ProxyResource):
        id: str
        name: str
        properties: DatabaseMigrationProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseMigrationProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationBase(ProxyResource):
        id: str
        name: str
        properties: DatabaseMigrationBaseProperties
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseMigrationBaseProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationBaseListResult(Model):
        next_link: str
        value: list[DatabaseMigrationBase]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationBaseProperties(Model):
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationCosmosDbMongo(ProxyResource):
        collection_list: list[MongoMigrationCollection]
        ended_on: datetime
        id: str
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        name: str
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_mongo_connection: MongoConnectionInformation
        started_on: datetime
        system_data: SystemData
        target_mongo_connection: MongoConnectionInformation
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection_list: Optional[List[MongoMigrationCollection]] = ..., 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_mongo_connection: Optional[MongoConnectionInformation] = ..., 
                target_mongo_connection: Optional[MongoConnectionInformation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationCosmosDbMongoListResult(Model):
        next_link: str
        value: list[DatabaseMigrationCosmosDbMongo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationListResult(Model):
        next_link: str
        value: list[DatabaseMigration]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationProperties(DatabaseMigrationBaseProperties):
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_database_name: str
        source_server_name: str
        source_sql_connection: SqlConnectionInformation
        started_on: datetime
        target_database_collation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_database_name: Optional[str] = ..., 
                source_sql_connection: Optional[SqlConnectionInformation] = ..., 
                target_database_collation: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationPropertiesCosmosDbMongo(DatabaseMigrationBaseProperties):
        collection_list: list[MongoMigrationCollection]
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_mongo_connection: MongoConnectionInformation
        started_on: datetime
        target_mongo_connection: MongoConnectionInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collection_list: Optional[List[MongoMigrationCollection]] = ..., 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_mongo_connection: Optional[MongoConnectionInformation] = ..., 
                target_mongo_connection: Optional[MongoConnectionInformation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationPropertiesSqlDb(DatabaseMigrationProperties):
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        migration_status_details: SqlDbMigrationStatusDetails
        offline_configuration: SqlDbOfflineConfiguration
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_database_name: str
        source_server_name: str
        source_sql_connection: SqlConnectionInformation
        started_on: datetime
        table_list: list[str]
        target_database_collation: str
        target_sql_connection: SqlConnectionInformation

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_database_name: Optional[str] = ..., 
                source_sql_connection: Optional[SqlConnectionInformation] = ..., 
                table_list: Optional[List[str]] = ..., 
                target_database_collation: Optional[str] = ..., 
                target_sql_connection: Optional[SqlConnectionInformation] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationPropertiesSqlMi(DatabaseMigrationProperties):
        backup_configuration: BackupConfiguration
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        migration_status_details: MigrationStatusDetails
        offline_configuration: OfflineConfiguration
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_database_name: str
        source_server_name: str
        source_sql_connection: SqlConnectionInformation
        started_on: datetime
        target_database_collation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_configuration: Optional[BackupConfiguration] = ..., 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                offline_configuration: Optional[OfflineConfiguration] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_database_name: Optional[str] = ..., 
                source_sql_connection: Optional[SqlConnectionInformation] = ..., 
                target_database_collation: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationPropertiesSqlVm(DatabaseMigrationProperties):
        backup_configuration: BackupConfiguration
        ended_on: datetime
        kind: Union[str, ResourceType]
        migration_failure_error: ErrorInfo
        migration_operation_id: str
        migration_service: str
        migration_status: str
        migration_status_details: MigrationStatusDetails
        offline_configuration: OfflineConfiguration
        provisioning_error: str
        provisioning_state: Union[str, ProvisioningState]
        scope: str
        source_database_name: str
        source_server_name: str
        source_sql_connection: SqlConnectionInformation
        started_on: datetime
        target_database_collation: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_configuration: Optional[BackupConfiguration] = ..., 
                migration_operation_id: Optional[str] = ..., 
                migration_service: Optional[str] = ..., 
                offline_configuration: Optional[OfflineConfiguration] = ..., 
                provisioning_error: Optional[str] = ..., 
                scope: Optional[str] = ..., 
                source_database_name: Optional[str] = ..., 
                source_sql_connection: Optional[SqlConnectionInformation] = ..., 
                target_database_collation: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationSqlDb(ProxyResourceAutoGenerated):
        id: str
        name: str
        properties: DatabaseMigrationPropertiesSqlDb
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseMigrationPropertiesSqlDb] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationSqlMi(ProxyResourceAutoGenerated):
        id: str
        name: str
        properties: DatabaseMigrationPropertiesSqlMi
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseMigrationPropertiesSqlMi] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationSqlVm(ProxyResourceAutoGenerated):
        id: str
        name: str
        properties: DatabaseMigrationPropertiesSqlVm
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                properties: Optional[DatabaseMigrationPropertiesSqlVm] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseMigrationStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP = "Backup"
        COMPLETED = "Completed"
        FILE_COPY = "FileCopy"
        INITIALIZE = "Initialize"
        NONE = "None"
        RESTORE = "Restore"


    class azure.mgmt.datamigration.models.DatabaseMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELLED = "CANCELLED"
        COMPLETED = "COMPLETED"
        CUTOVER_START = "CUTOVER_START"
        FAILED = "FAILED"
        FULL_BACKUP_UPLOAD_START = "FULL_BACKUP_UPLOAD_START"
        INITIAL = "INITIAL"
        LOG_SHIPPING_START = "LOG_SHIPPING_START"
        POST_CUTOVER_COMPLETE = "POST_CUTOVER_COMPLETE"
        UNDEFINED = "UNDEFINED"
        UPLOAD_LOG_FILES_START = "UPLOAD_LOG_FILES_START"


    class azure.mgmt.datamigration.models.DatabaseObjectName(Model):
        database_name: str
        object_name: str
        object_type: Union[str, ObjectType]
        schema_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_type: Optional[Union[str, ObjectType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COPYING = "Copying"
        EMERGENCY = "Emergency"
        OFFLINE = "Offline"
        OFFLINE_SECONDARY = "OfflineSecondary"
        ONLINE = "Online"
        RECOVERING = "Recovering"
        RECOVERY_PENDING = "RecoveryPending"
        RESTORING = "Restoring"
        SUSPECT = "Suspect"


    class azure.mgmt.datamigration.models.DatabaseSummaryResult(DataItemMigrationSummaryResult):
        ended_on: datetime
        error_prefix: str
        items_completed_count: int
        items_count: int
        name: str
        result_prefix: str
        size_mb: float
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DatabaseTable(Model):
        has_rows: bool
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.DeleteNode(Model):
        integration_runtime_name: str
        node_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                integration_runtime_name: Optional[str] = ..., 
                node_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ErrorAdditionalInfo(Model):
        info: JSON
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ErrorDetail(Model):
        additional_info: list[ErrorAdditionalInfo]
        code: str
        details: list[ErrorDetail]
        message: str
        target: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ErrorInfo(Model):
        code: str
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ErrorResponse(Model):
        error: ErrorDetail

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error: Optional[ErrorDetail] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        ERROR = "Error"
        WARNING = "Warning"


    class azure.mgmt.datamigration.models.ExecutionStatistics(Model):
        cpu_time_ms: float
        elapsed_time_ms: float
        execution_count: int
        has_errors: bool
        sql_errors: list[str]
        wait_stats: dict[str, WaitStatistics]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                cpu_time_ms: Optional[float] = ..., 
                elapsed_time_ms: Optional[float] = ..., 
                execution_count: Optional[int] = ..., 
                has_errors: Optional[bool] = ..., 
                sql_errors: Optional[List[str]] = ..., 
                wait_stats: Optional[Dict[str, WaitStatistics]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.FileList(Model):
        next_link: str
        value: list[ProjectFile]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ProjectFile]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.FileShare(Model):
        password: str
        path: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                path: str, 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.FileStorageInfo(Model):
        headers: dict[str, str]
        uri: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                headers: Optional[Dict[str, str]] = ..., 
                uri: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetProjectDetailsNonSqlTaskInput(Model):
        project_location: str
        project_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                project_location: str, 
                project_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetTdeCertificatesSqlTaskInput(Model):
        backup_file_share: FileShare
        connection_info: SqlConnectionInfo
        selected_certificates: list[SelectedCertificateInput]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_file_share: FileShare, 
                connection_info: SqlConnectionInfo, 
                selected_certificates: List[SelectedCertificateInput], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetTdeCertificatesSqlTaskOutput(Model):
        base64_encoded_certificates: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetTdeCertificatesSqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetTdeCertificatesSqlTaskInput
        output: list[GetTdeCertificatesSqlTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetTdeCertificatesSqlTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesMySqlTaskInput(Model):
        connection_info: MySqlConnectionInfo
        selected_databases: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_info: MySqlConnectionInfo, 
                selected_databases: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesMySqlTaskOutput(Model):
        databases_to_tables: str
        id: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesMySqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetUserTablesMySqlTaskInput
        output: list[GetUserTablesMySqlTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetUserTablesMySqlTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesOracleTaskInput(Model):
        connection_info: OracleConnectionInfo
        selected_schemas: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_info: OracleConnectionInfo, 
                selected_schemas: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesOracleTaskOutput(Model):
        schema_name: str
        tables: list[DatabaseTable]
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesOracleTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetUserTablesOracleTaskInput
        output: list[GetUserTablesOracleTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetUserTablesOracleTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesPostgreSqlTaskInput(Model):
        connection_info: PostgreSqlConnectionInfo
        selected_databases: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_info: PostgreSqlConnectionInfo, 
                selected_databases: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesPostgreSqlTaskOutput(Model):
        database_name: str
        tables: list[DatabaseTable]
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesPostgreSqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetUserTablesPostgreSqlTaskInput
        output: list[GetUserTablesPostgreSqlTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetUserTablesPostgreSqlTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlSyncTaskInput(Model):
        selected_source_databases: list[str]
        selected_target_databases: list[str]
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_source_databases: List[str], 
                selected_target_databases: List[str], 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlSyncTaskOutput(Model):
        databases_to_source_tables: str
        databases_to_target_tables: str
        table_validation_errors: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetUserTablesSqlSyncTaskInput
        output: list[GetUserTablesSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetUserTablesSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlTaskInput(Model):
        connection_info: SqlConnectionInfo
        encrypted_key_for_secure_fields: str
        selected_databases: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_info: SqlConnectionInfo, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                selected_databases: List[str], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlTaskOutput(Model):
        databases_to_tables: str
        id: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.GetUserTablesSqlTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: GetUserTablesSqlTaskInput
        output: list[GetUserTablesSqlTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[GetUserTablesSqlTaskInput] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.InstallOCIDriverTaskInput(Model):
        driver_package_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                driver_package_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.InstallOCIDriverTaskOutput(Model):
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.InstallOCIDriverTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: InstallOCIDriverTaskInput
        output: list[InstallOCIDriverTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[InstallOCIDriverTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.IntegrationRuntimeMonitoringData(Model):
        name: str
        nodes: list[NodeMonitoringData]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.LoginMigrationStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASSIGN_ROLE_MEMBERSHIP = "AssignRoleMembership"
        ASSIGN_ROLE_OWNERSHIP = "AssignRoleOwnership"
        COMPLETED = "Completed"
        ESTABLISH_OBJECT_PERMISSIONS = "EstablishObjectPermissions"
        ESTABLISH_SERVER_PERMISSIONS = "EstablishServerPermissions"
        ESTABLISH_USER_MAPPING = "EstablishUserMapping"
        INITIALIZE = "Initialize"
        LOGIN_MIGRATION = "LoginMigration"
        NONE = "None"


    class azure.mgmt.datamigration.models.LoginType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ASYMMETRIC_KEY = "AsymmetricKey"
        CERTIFICATE = "Certificate"
        EXTERNAL_GROUP = "ExternalGroup"
        EXTERNAL_USER = "ExternalUser"
        SQL_LOGIN = "SqlLogin"
        WINDOWS_GROUP = "WindowsGroup"
        WINDOWS_USER = "WindowsUser"


    class azure.mgmt.datamigration.models.ManagedServiceIdentity(Model):
        principal_id: str
        tenant_id: str
        type: Union[str, ManagedServiceIdentityType]
        user_assigned_identities: dict[str, UserAssignedIdentity]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                type: Union[str, ManagedServiceIdentityType], 
                user_assigned_identities: Optional[Dict[str, UserAssignedIdentity]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ManagedServiceIdentityType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NONE = "None"
        SYSTEM_ASSIGNED = "SystemAssigned"
        SYSTEM_ASSIGNED_USER_ASSIGNED = "SystemAssigned,UserAssigned"
        USER_ASSIGNED = "UserAssigned"


    class azure.mgmt.datamigration.models.MiSqlConnectionInfo(ConnectionInfo):
        managed_instance_resource_id: str
        password: str
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                managed_instance_resource_id: str, 
                password: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMISyncCompleteCommandInput(Model):
        source_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_database_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMISyncCompleteCommandOutput(Model):
        errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                errors: Optional[List[ReportableException]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMISyncCompleteCommandProperties(CommandProperties):
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        input: MigrateMISyncCompleteCommandInput
        output: MigrateMISyncCompleteCommandOutput
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                input: Optional[MigrateMISyncCompleteCommandInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMongoDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MongoDbMigrationSettings
        output: list[MongoDbProgress]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MongoDbMigrationSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineDatabaseInput(Model):
        name: str
        table_map: dict[str, str]
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                table_map: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskInput(Model):
        encrypted_key_for_secure_fields: str
        make_source_server_read_only: bool
        optional_agent_settings: dict[str, str]
        selected_databases: list[MigrateMySqlAzureDbForMySqlOfflineDatabaseInput]
        source_connection_info: MySqlConnectionInfo
        started_on: datetime
        target_connection_info: MySqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                make_source_server_read_only: bool = False, 
                optional_agent_settings: Optional[Dict[str, str]] = ..., 
                selected_databases: List[MigrateMySqlAzureDbForMySqlOfflineDatabaseInput], 
                source_connection_info: MySqlConnectionInfo, 
                started_on: Optional[datetime] = ..., 
                target_connection_info: MySqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskOutputDatabaseLevel(MigrateMySqlAzureDbForMySqlOfflineTaskOutput):
        database_name: str
        ended_on: datetime
        error_count: int
        error_prefix: str
        exceptions_and_warnings: list[ReportableException]
        id: str
        last_storage_update: datetime
        message: str
        number_of_objects: int
        number_of_objects_completed: int
        object_summary: str
        result_prefix: str
        result_type: str
        stage: Union[str, DatabaseMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskOutputError(MigrateMySqlAzureDbForMySqlOfflineTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskOutputMigrationLevel(MigrateMySqlAzureDbForMySqlOfflineTaskOutput):
        database_summary: str
        databases: str
        duration_in_seconds: int
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        last_storage_update: datetime
        message: str
        migration_report_result: MigrationReportResult
        result_type: str
        source_server_brand_version: str
        source_server_version: str
        started_on: datetime
        status: Union[str, MigrationStatus]
        status_message: str
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                databases: Optional[str] = ..., 
                migration_report_result: Optional[MigrationReportResult] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskOutputTableLevel(MigrateMySqlAzureDbForMySqlOfflineTaskOutput):
        ended_on: datetime
        error_prefix: str
        id: str
        items_completed_count: int
        items_count: int
        last_storage_update: datetime
        object_name: str
        result_prefix: str
        result_type: str
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlOfflineTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateMySqlAzureDbForMySqlOfflineTaskInput
        is_cloneable: bool
        output: list[MigrateMySqlAzureDbForMySqlOfflineTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateMySqlAzureDbForMySqlOfflineTaskInput] = ..., 
                is_cloneable: Optional[bool] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncDatabaseInput(Model):
        migration_setting: dict[str, str]
        name: str
        source_setting: dict[str, str]
        table_map: dict[str, str]
        target_database_name: str
        target_setting: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_setting: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                source_setting: Optional[Dict[str, str]] = ..., 
                table_map: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                target_setting: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskInput(Model):
        selected_databases: list[MigrateMySqlAzureDbForMySqlSyncDatabaseInput]
        source_connection_info: MySqlConnectionInfo
        target_connection_info: MySqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_databases: List[MigrateMySqlAzureDbForMySqlSyncDatabaseInput], 
                source_connection_info: MySqlConnectionInfo, 
                target_connection_info: MySqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutputDatabaseError(MigrateMySqlAzureDbForMySqlSyncTaskOutput):
        error_message: str
        events: list[SyncMigrationDatabaseErrorEvent]
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                events: Optional[List[SyncMigrationDatabaseErrorEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutputDatabaseLevel(MigrateMySqlAzureDbForMySqlSyncTaskOutput):
        applied_changes: int
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        database_name: str
        ended_on: datetime
        full_load_completed_tables: int
        full_load_errored_tables: int
        full_load_loading_tables: int
        full_load_queued_tables: int
        id: str
        incoming_changes: int
        initialization_completed: bool
        latency: int
        migration_state: Union[str, SyncDatabaseMigrationReportingState]
        result_type: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutputError(MigrateMySqlAzureDbForMySqlSyncTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutputMigrationLevel(MigrateMySqlAzureDbForMySqlSyncTaskOutput):
        ended_on: datetime
        id: str
        result_type: str
        source_server: str
        source_server_version: str
        started_on: datetime
        target_server: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskOutputTableLevel(MigrateMySqlAzureDbForMySqlSyncTaskOutput):
        cdc_delete_counter: str
        cdc_insert_counter: str
        cdc_update_counter: str
        data_errors_counter: int
        database_name: str
        full_load_ended_on: datetime
        full_load_est_finish_time: datetime
        full_load_started_on: datetime
        full_load_total_rows: int
        id: str
        last_modified_time: datetime
        result_type: str
        state: Union[str, SyncTableMigrationState]
        table_name: str
        total_changes_applied: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateMySqlAzureDbForMySqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateMySqlAzureDbForMySqlSyncTaskInput
        output: list[MigrateMySqlAzureDbForMySqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateMySqlAzureDbForMySqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbForPostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateOracleAzureDbPostgreSqlSyncTaskInput
        output: list[MigrateOracleAzureDbPostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateOracleAzureDbPostgreSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncDatabaseInput(Model):
        case_manipulation: str
        migration_setting: dict[str, str]
        name: str
        schema_name: str
        source_setting: dict[str, str]
        table_map: dict[str, str]
        target_database_name: str
        target_setting: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                case_manipulation: Optional[str] = ..., 
                migration_setting: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                schema_name: Optional[str] = ..., 
                source_setting: Optional[Dict[str, str]] = ..., 
                table_map: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                target_setting: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskInput(Model):
        selected_databases: list[MigrateOracleAzureDbPostgreSqlSyncDatabaseInput]
        source_connection_info: OracleConnectionInfo
        target_connection_info: PostgreSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_databases: List[MigrateOracleAzureDbPostgreSqlSyncDatabaseInput], 
                source_connection_info: OracleConnectionInfo, 
                target_connection_info: PostgreSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutputDatabaseError(MigrateOracleAzureDbPostgreSqlSyncTaskOutput):
        error_message: str
        events: list[SyncMigrationDatabaseErrorEvent]
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                events: Optional[List[SyncMigrationDatabaseErrorEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutputDatabaseLevel(MigrateOracleAzureDbPostgreSqlSyncTaskOutput):
        applied_changes: int
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        database_name: str
        ended_on: datetime
        full_load_completed_tables: int
        full_load_errored_tables: int
        full_load_loading_tables: int
        full_load_queued_tables: int
        id: str
        incoming_changes: int
        initialization_completed: bool
        latency: int
        migration_state: Union[str, SyncDatabaseMigrationReportingState]
        result_type: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutputError(MigrateOracleAzureDbPostgreSqlSyncTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutputMigrationLevel(MigrateOracleAzureDbPostgreSqlSyncTaskOutput):
        ended_on: datetime
        id: str
        result_type: str
        source_server: str
        source_server_version: str
        started_on: datetime
        target_server: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateOracleAzureDbPostgreSqlSyncTaskOutputTableLevel(MigrateOracleAzureDbPostgreSqlSyncTaskOutput):
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        data_errors_counter: int
        database_name: str
        full_load_ended_on: datetime
        full_load_est_finish_time: datetime
        full_load_started_on: datetime
        full_load_total_rows: int
        id: str
        last_modified_time: datetime
        result_type: str
        state: Union[str, SyncTableMigrationState]
        table_name: str
        total_changes_applied: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput(Model):
        id: str
        migration_setting: dict[str, any]
        name: str
        selected_tables: list[MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseTableInput]
        source_setting: dict[str, str]
        target_database_name: str
        target_setting: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_setting: Optional[Dict[str, Any]] = ..., 
                name: Optional[str] = ..., 
                selected_tables: Optional[List[MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseTableInput]] = ..., 
                source_setting: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                target_setting: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseTableInput(Model):
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput(Model):
        encrypted_key_for_secure_fields: str
        selected_databases: list[MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput]
        source_connection_info: PostgreSqlConnectionInfo
        started_on: datetime
        target_connection_info: PostgreSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                selected_databases: List[MigratePostgreSqlAzureDbForPostgreSqlSyncDatabaseInput], 
                source_connection_info: PostgreSqlConnectionInfo, 
                target_connection_info: PostgreSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputDatabaseError(MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput):
        error_message: str
        events: list[SyncMigrationDatabaseErrorEvent]
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                events: Optional[List[SyncMigrationDatabaseErrorEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputDatabaseLevel(MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput):
        applied_changes: int
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        database_name: str
        ended_on: datetime
        full_load_completed_tables: int
        full_load_errored_tables: int
        full_load_loading_tables: int
        full_load_queued_tables: int
        id: str
        incoming_changes: int
        initialization_completed: bool
        latency: int
        migration_state: Union[str, SyncDatabaseMigrationReportingState]
        result_type: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputError(MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput):
        error: ReportableException
        events: list[SyncMigrationDatabaseErrorEvent]
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                events: Optional[List[SyncMigrationDatabaseErrorEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputMigrationLevel(MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput):
        database_count: float
        ended_on: datetime
        id: str
        result_type: str
        source_server: str
        source_server_type: Union[str, ScenarioSource]
        source_server_version: str
        started_on: datetime
        state: Union[str, ReplicateMigrationState]
        target_server: str
        target_server_type: Union[str, ScenarioTarget]
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_count: Optional[float] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutputTableLevel(MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput):
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        data_errors_counter: int
        database_name: str
        full_load_ended_on: datetime
        full_load_est_finish_time: datetime
        full_load_started_on: datetime
        full_load_total_rows: int
        id: str
        last_modified_time: datetime
        result_type: str
        state: Union[str, SyncTableMigrationState]
        table_name: str
        total_changes_applied: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigratePostgreSqlAzureDbForPostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput
        is_cloneable: bool
        output: list[MigratePostgreSqlAzureDbForPostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[MigratePostgreSqlAzureDbForPostgreSqlSyncTaskInput] = ..., 
                is_cloneable: Optional[bool] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbDatabaseInput(Model):
        id: str
        name: str
        schema_setting: SchemaMigrationSetting
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                name: Optional[str] = ..., 
                schema_setting: Optional[SchemaMigrationSetting] = ..., 
                target_database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskInput(SqlMigrationTaskInput):
        encrypted_key_for_secure_fields: str
        selected_databases: list[MigrateSchemaSqlServerSqlDbDatabaseInput]
        source_connection_info: SqlConnectionInfo
        started_on: str
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                selected_databases: List[MigrateSchemaSqlServerSqlDbDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                started_on: Optional[str] = ..., 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskOutputDatabaseLevel(MigrateSchemaSqlServerSqlDbTaskOutput):
        database_error_result_prefix: str
        database_name: str
        ended_on: datetime
        file_id: str
        id: str
        number_of_failed_operations: int
        number_of_successful_operations: int
        result_type: str
        schema_error_result_prefix: str
        stage: Union[str, SchemaMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskOutputError(MigrateSchemaSqlServerSqlDbTaskOutput):
        command_text: str
        error_text: str
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskOutputMigrationLevel(MigrateSchemaSqlServerSqlDbTaskOutput):
        ended_on: datetime
        id: str
        result_type: str
        source_server_brand_version: str
        source_server_version: str
        started_on: datetime
        state: Union[str, MigrationState]
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlServerSqlDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: MigrateSchemaSqlServerSqlDbTaskInput
        is_cloneable: bool
        output: list[MigrateSchemaSqlServerSqlDbTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[MigrateSchemaSqlServerSqlDbTaskInput] = ..., 
                is_cloneable: Optional[bool] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSchemaSqlTaskOutputError(MigrateSchemaSqlServerSqlDbTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerDatabaseInput(Model):
        backup_and_restore_folder: str
        database_files: list[DatabaseFileInput]
        name: str
        restore_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_and_restore_folder: Optional[str] = ..., 
                database_files: Optional[List[DatabaseFileInput]] = ..., 
                name: Optional[str] = ..., 
                restore_database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbDatabaseInput(Model):
        id: str
        make_source_db_read_only: bool
        name: str
        schema_setting: JSON
        table_map: dict[str, str]
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                make_source_db_read_only: Optional[bool] = ..., 
                name: Optional[str] = ..., 
                schema_setting: Optional[JSON] = ..., 
                table_map: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncDatabaseInput(Model):
        id: str
        migration_setting: dict[str, str]
        name: str
        schema_name: str
        source_setting: dict[str, str]
        table_map: dict[str, str]
        target_database_name: str
        target_setting: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                migration_setting: Optional[Dict[str, str]] = ..., 
                name: Optional[str] = ..., 
                schema_name: Optional[str] = ..., 
                source_setting: Optional[Dict[str, str]] = ..., 
                table_map: Optional[Dict[str, str]] = ..., 
                target_database_name: Optional[str] = ..., 
                target_setting: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskInput(SqlMigrationTaskInput):
        selected_databases: list[MigrateSqlServerSqlDbSyncDatabaseInput]
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo
        validation_options: MigrationValidationOptions

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_databases: List[MigrateSqlServerSqlDbSyncDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                validation_options: Optional[MigrationValidationOptions] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutputDatabaseError(MigrateSqlServerSqlDbSyncTaskOutput):
        error_message: str
        events: list[SyncMigrationDatabaseErrorEvent]
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                error_message: Optional[str] = ..., 
                events: Optional[List[SyncMigrationDatabaseErrorEvent]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutputDatabaseLevel(MigrateSqlServerSqlDbSyncTaskOutput):
        applied_changes: int
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        database_name: str
        ended_on: datetime
        full_load_completed_tables: int
        full_load_errored_tables: int
        full_load_loading_tables: int
        full_load_queued_tables: int
        id: str
        incoming_changes: int
        initialization_completed: bool
        latency: int
        migration_state: Union[str, SyncDatabaseMigrationReportingState]
        result_type: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutputError(MigrateSqlServerSqlDbSyncTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutputMigrationLevel(MigrateSqlServerSqlDbSyncTaskOutput):
        database_count: int
        ended_on: datetime
        id: str
        result_type: str
        source_server: str
        source_server_version: str
        started_on: datetime
        target_server: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskOutputTableLevel(MigrateSqlServerSqlDbSyncTaskOutput):
        cdc_delete_counter: int
        cdc_insert_counter: int
        cdc_update_counter: int
        data_errors_counter: int
        database_name: str
        full_load_ended_on: datetime
        full_load_est_finish_time: datetime
        full_load_started_on: datetime
        full_load_total_rows: int
        id: str
        last_modified_time: datetime
        result_type: str
        state: Union[str, SyncTableMigrationState]
        table_name: str
        total_changes_applied: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateSqlServerSqlDbSyncTaskInput
        output: list[MigrateSqlServerSqlDbSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateSqlServerSqlDbSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskInput(SqlMigrationTaskInput):
        encrypted_key_for_secure_fields: str
        selected_databases: list[MigrateSqlServerSqlDbDatabaseInput]
        source_connection_info: SqlConnectionInfo
        started_on: str
        target_connection_info: SqlConnectionInfo
        validation_options: MigrationValidationOptions

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                selected_databases: List[MigrateSqlServerSqlDbDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                started_on: Optional[str] = ..., 
                target_connection_info: SqlConnectionInfo, 
                validation_options: Optional[MigrationValidationOptions] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputDatabaseLevel(MigrateSqlServerSqlDbTaskOutput):
        database_name: str
        ended_on: datetime
        error_count: int
        error_prefix: str
        exceptions_and_warnings: list[ReportableException]
        id: str
        message: str
        number_of_objects: int
        number_of_objects_completed: int
        object_summary: str
        result_prefix: str
        result_type: str
        stage: Union[str, DatabaseMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputDatabaseLevelValidationResult(MigrateSqlServerSqlDbTaskOutput, MigrationValidationDatabaseLevelResult):
        data_integrity_validation_result: DataIntegrityValidationResult
        ended_on: datetime
        id: str
        migration_id: str
        query_analysis_validation_result: QueryAnalysisValidationResult
        result_type: str
        schema_validation_result: SchemaComparisonValidationResult
        source_database_name: str
        started_on: datetime
        status: Union[str, ValidationStatus]
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputError(MigrateSqlServerSqlDbTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputMigrationLevel(MigrateSqlServerSqlDbTaskOutput):
        database_summary: str
        databases: str
        duration_in_seconds: int
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        message: str
        migration_report_result: MigrationReportResult
        migration_validation_result: MigrationValidationResult
        result_type: str
        source_server_brand_version: str
        source_server_version: str
        started_on: datetime
        status: Union[str, MigrationStatus]
        status_message: str
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_report_result: Optional[MigrationReportResult] = ..., 
                migration_validation_result: Optional[MigrationValidationResult] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputTableLevel(MigrateSqlServerSqlDbTaskOutput):
        ended_on: datetime
        error_prefix: str
        id: str
        items_completed_count: int
        items_count: int
        object_name: str
        result_prefix: str
        result_type: str
        started_on: datetime
        state: Union[str, MigrationState]
        status_message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskOutputValidationResult(MigrateSqlServerSqlDbTaskOutput, MigrationValidationResult):
        id: str
        migration_id: str
        result_type: str
        status: Union[str, ValidationStatus]
        summary_results: dict[str, MigrationValidationDatabaseSummaryResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                summary_results: Optional[Dict[str, MigrationValidationDatabaseSummaryResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: MigrateSqlServerSqlDbTaskInput
        is_cloneable: bool
        output: list[MigrateSqlServerSqlDbTaskOutput]
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[MigrateSqlServerSqlDbTaskInput] = ..., 
                is_cloneable: Optional[bool] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMIDatabaseInput(Model):
        backup_file_paths: list[str]
        backup_file_share: FileShare
        id: str
        name: str
        restore_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_file_paths: Optional[List[str]] = ..., 
                backup_file_share: Optional[FileShare] = ..., 
                id: Optional[str] = ..., 
                name: str, 
                restore_database_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskInput(SqlServerSqlMISyncTaskInput):
        azure_app: AzureActiveDirectoryApp
        backup_file_share: FileShare
        number_of_parallel_database_migrations: float
        selected_databases: list[MigrateSqlServerSqlMIDatabaseInput]
        source_connection_info: SqlConnectionInfo
        storage_resource_id: str
        target_connection_info: MiSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_app: AzureActiveDirectoryApp, 
                backup_file_share: Optional[FileShare] = ..., 
                number_of_parallel_database_migrations: Optional[float] = ..., 
                selected_databases: List[MigrateSqlServerSqlMIDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                storage_resource_id: str, 
                target_connection_info: MiSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskOutputDatabaseLevel(MigrateSqlServerSqlMISyncTaskOutput):
        active_backup_sets: list[BackupSetInfo]
        container_name: str
        ended_on: datetime
        error_prefix: str
        exceptions_and_warnings: list[ReportableException]
        full_backup_set_info: BackupSetInfo
        id: str
        is_full_backup_restored: bool
        last_restored_backup_set_info: BackupSetInfo
        migration_state: Union[str, DatabaseMigrationState]
        result_type: str
        source_database_name: str
        started_on: datetime

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskOutputError(MigrateSqlServerSqlMISyncTaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskOutputMigrationLevel(MigrateSqlServerSqlMISyncTaskOutput):
        database_count: int
        database_error_count: int
        ended_on: datetime
        id: str
        result_type: str
        source_server_brand_version: str
        source_server_name: str
        source_server_version: str
        started_on: datetime
        state: Union[str, MigrationState]
        target_server_brand_version: str
        target_server_name: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMISyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: MigrateSqlServerSqlMISyncTaskInput
        output: list[MigrateSqlServerSqlMISyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[MigrateSqlServerSqlMISyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskInput(SqlMigrationTaskInput):
        aad_domain_name: str
        backup_blob_share: BlobShare
        backup_file_share: FileShare
        backup_mode: Union[str, BackupMode]
        encrypted_key_for_secure_fields: str
        selected_agent_jobs: list[str]
        selected_databases: list[MigrateSqlServerSqlMIDatabaseInput]
        selected_logins: list[str]
        source_connection_info: SqlConnectionInfo
        started_on: str
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                aad_domain_name: Optional[str] = ..., 
                backup_blob_share: BlobShare, 
                backup_file_share: Optional[FileShare] = ..., 
                backup_mode: Optional[Union[str, BackupMode]] = ..., 
                encrypted_key_for_secure_fields: Optional[str] = ..., 
                selected_agent_jobs: Optional[List[str]] = ..., 
                selected_databases: List[MigrateSqlServerSqlMIDatabaseInput], 
                selected_logins: Optional[List[str]] = ..., 
                source_connection_info: SqlConnectionInfo, 
                started_on: Optional[str] = ..., 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutputAgentJobLevel(MigrateSqlServerSqlMITaskOutput):
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        is_enabled: bool
        message: str
        name: str
        result_type: str
        started_on: datetime
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutputDatabaseLevel(MigrateSqlServerSqlMITaskOutput):
        database_name: str
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        message: str
        result_type: str
        size_mb: float
        stage: Union[str, DatabaseMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutputError(MigrateSqlServerSqlMITaskOutput):
        error: ReportableException
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutputLoginLevel(MigrateSqlServerSqlMITaskOutput):
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        login_name: str
        message: str
        result_type: str
        stage: Union[str, LoginMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskOutputMigrationLevel(MigrateSqlServerSqlMITaskOutput):
        agent_jobs: str
        databases: str
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        logins: str
        message: str
        orphaned_users_info: list[OrphanedUserInfo]
        result_type: str
        server_role_results: str
        source_server_brand_version: str
        source_server_version: str
        started_on: datetime
        state: Union[str, MigrationState]
        status: Union[str, MigrationStatus]
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSqlServerSqlMITaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        created_on: str
        errors: list[ODataError]
        input: MigrateSqlServerSqlMITaskInput
        is_cloneable: bool
        output: list[MigrateSqlServerSqlMITaskOutput]
        parent_task_id: str
        state: Union[str, TaskState]
        task_id: str
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                created_on: Optional[str] = ..., 
                input: Optional[MigrateSqlServerSqlMITaskInput] = ..., 
                is_cloneable: Optional[bool] = ..., 
                parent_task_id: Optional[str] = ..., 
                task_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSsisTaskInput(SqlMigrationTaskInput):
        source_connection_info: SqlConnectionInfo
        ssis_migration_info: SsisMigrationInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: SqlConnectionInfo, 
                ssis_migration_info: SsisMigrationInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSsisTaskOutput(Model):
        id: str
        result_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSsisTaskOutputMigrationLevel(MigrateSsisTaskOutput):
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        id: str
        message: str
        result_type: str
        source_server_brand_version: str
        source_server_version: str
        stage: Union[str, SsisMigrationStage]
        started_on: datetime
        status: Union[str, MigrationStatus]
        target_server_brand_version: str
        target_server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSsisTaskOutputProjectLevel(MigrateSsisTaskOutput):
        ended_on: datetime
        exceptions_and_warnings: list[ReportableException]
        folder_name: str
        id: str
        message: str
        project_name: str
        result_type: str
        stage: Union[str, SsisMigrationStage]
        started_on: datetime
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSsisTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateSsisTaskInput
        output: list[MigrateSsisTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateSsisTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSyncCompleteCommandInput(Model):
        commit_time_stamp: datetime
        database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                commit_time_stamp: Optional[datetime] = ..., 
                database_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSyncCompleteCommandOutput(Model):
        errors: list[ReportableException]
        id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrateSyncCompleteCommandProperties(CommandProperties):
        command_id: str
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        input: MigrateSyncCompleteCommandInput
        output: MigrateSyncCompleteCommandOutput
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                command_id: Optional[str] = ..., 
                input: Optional[MigrateSyncCompleteCommandInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationEligibilityInfo(Model):
        is_eligible_for_migration: bool
        validation_messages: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationOperationInput(Model):
        migration_operation_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                migration_operation_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationReportResult(Model):
        id: str
        report_url: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                id: Optional[str] = ..., 
                report_url: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationService(TrackedResource):
        id: str
        integration_runtime_state: str
        location: str
        name: str
        provisioning_state: Union[str, ProvisioningState]
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationServiceListResult(Model):
        next_link: str
        value: list[MigrationService]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationServiceUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NONE = "None"
        SKIPPED = "Skipped"
        STOPPED = "Stopped"
        WARNING = "Warning"


    class azure.mgmt.datamigration.models.MigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        CONFIGURED = "Configured"
        CONNECTING = "Connecting"
        DEFAULT = "Default"
        ERROR = "Error"
        RUNNING = "Running"
        SELECT_LOGINS = "SelectLogins"
        SOURCE_AND_TARGET_SELECTED = "SourceAndTargetSelected"
        STOPPED = "Stopped"


    class azure.mgmt.datamigration.models.MigrationStatusDetails(Model):
        active_backup_sets: list[SqlBackupSetInfo]
        blob_container_name: str
        complete_restore_error_message: str
        current_restoring_filename: str
        file_upload_blocking_errors: list[str]
        full_backup_set_info: SqlBackupSetInfo
        invalid_files: list[str]
        is_full_backup_restored: bool
        last_restored_backup_set_info: SqlBackupSetInfo
        last_restored_filename: str
        migration_state: str
        pending_log_backups_count: int
        restore_blocking_reason: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationTableMetadata(Model):
        source_table_name: str
        target_table_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationValidationDatabaseLevelResult(Model):
        data_integrity_validation_result: DataIntegrityValidationResult
        ended_on: datetime
        id: str
        migration_id: str
        query_analysis_validation_result: QueryAnalysisValidationResult
        schema_validation_result: SchemaComparisonValidationResult
        source_database_name: str
        started_on: datetime
        status: Union[str, ValidationStatus]
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationValidationDatabaseSummaryResult(Model):
        ended_on: datetime
        id: str
        migration_id: str
        source_database_name: str
        started_on: datetime
        status: Union[str, ValidationStatus]
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationValidationOptions(Model):
        enable_data_integrity_validation: bool
        enable_query_analysis_validation: bool
        enable_schema_validation: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                enable_data_integrity_validation: Optional[bool] = ..., 
                enable_query_analysis_validation: Optional[bool] = ..., 
                enable_schema_validation: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MigrationValidationResult(Model):
        id: str
        migration_id: str
        status: Union[str, ValidationStatus]
        summary_results: dict[str, MigrationValidationDatabaseSummaryResult]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                summary_results: Optional[Dict[str, MigrationValidationDatabaseSummaryResult]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoConnectionInformation(Model):
        connection_string: str
        host: str
        password: str
        port: int
        use_ssl: bool
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                connection_string: Optional[str] = ..., 
                host: Optional[str] = ..., 
                password: Optional[str] = ..., 
                port: Optional[int] = ..., 
                use_ssl: Optional[bool] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbCancelCommand(CommandProperties):
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        input: MongoDbCommandInput
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                input: Optional[MongoDbCommandInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbClusterInfo(Model):
        databases: list[MongoDbDatabaseInfo]
        supports_sharding: bool
        type: Union[str, MongoDbClusterType]
        version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                databases: List[MongoDbDatabaseInfo], 
                supports_sharding: bool, 
                type: Union[str, MongoDbClusterType], 
                version: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbClusterType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BLOB_CONTAINER = "BlobContainer"
        COSMOS_DB = "CosmosDb"
        MONGO_DB = "MongoDb"


    class azure.mgmt.datamigration.models.MongoDbCollectionInfo(MongoDbObjectInfo):
        average_document_size: int
        data_size: int
        database_name: str
        document_count: int
        is_capped: bool
        is_system_collection: bool
        is_view: bool
        name: str
        qualified_name: str
        shard_key: MongoDbShardKeyInfo
        supports_sharding: bool
        view_of: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                average_document_size: int, 
                data_size: int, 
                database_name: str, 
                document_count: int, 
                is_capped: bool, 
                is_system_collection: bool, 
                is_view: bool, 
                name: str, 
                qualified_name: str, 
                shard_key: Optional[MongoDbShardKeyInfo] = ..., 
                supports_sharding: bool, 
                view_of: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbCollectionProgress(MongoDbProgress):
        bytes_copied: int
        documents_copied: int
        elapsed_time: str
        errors: dict[str, MongoDbError]
        events_pending: int
        events_replayed: int
        last_event_time: datetime
        last_replay_time: datetime
        name: str
        qualified_name: str
        result_type: Union[str, MongoDbProgressResultType]
        state: Union[str, MongoDbMigrationState]
        total_bytes: int
        total_documents: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bytes_copied: int, 
                documents_copied: int, 
                elapsed_time: str, 
                errors: Dict[str, MongoDbError], 
                events_pending: int, 
                events_replayed: int, 
                last_event_time: Optional[datetime] = ..., 
                last_replay_time: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                state: Union[str, MongoDbMigrationState], 
                total_bytes: int, 
                total_documents: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbCollectionSettings(Model):
        can_delete: bool
        shard_key: MongoDbShardKeySetting
        target_r_us: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                can_delete: Optional[bool] = ..., 
                shard_key: Optional[MongoDbShardKeySetting] = ..., 
                target_r_us: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbCommandInput(Model):
        object_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbConnectionInfo(ConnectionInfo):
        additional_settings: str
        authentication: Union[str, AuthenticationType]
        connection_string: str
        data_source: str
        encrypt_connection: bool
        enforce_ssl: bool
        password: str
        port: int
        server_brand_version: str
        server_name: str
        server_version: str
        trust_server_certificate: bool
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_settings: Optional[str] = ..., 
                authentication: Optional[Union[str, AuthenticationType]] = ..., 
                connection_string: str, 
                data_source: Optional[str] = ..., 
                encrypt_connection: Optional[bool] = ..., 
                enforce_ssl: Optional[bool] = ..., 
                password: Optional[str] = ..., 
                port: Optional[int] = ..., 
                server_brand_version: Optional[str] = ..., 
                server_name: Optional[str] = ..., 
                server_version: Optional[str] = ..., 
                trust_server_certificate: bool = False, 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbDatabaseInfo(MongoDbObjectInfo):
        average_document_size: int
        collections: list[MongoDbCollectionInfo]
        data_size: int
        document_count: int
        name: str
        qualified_name: str
        supports_sharding: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                average_document_size: int, 
                collections: List[MongoDbCollectionInfo], 
                data_size: int, 
                document_count: int, 
                name: str, 
                qualified_name: str, 
                supports_sharding: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbDatabaseProgress(MongoDbProgress):
        bytes_copied: int
        collections: dict[str, MongoDbCollectionProgress]
        documents_copied: int
        elapsed_time: str
        errors: dict[str, MongoDbError]
        events_pending: int
        events_replayed: int
        last_event_time: datetime
        last_replay_time: datetime
        name: str
        qualified_name: str
        result_type: Union[str, MongoDbProgressResultType]
        state: Union[str, MongoDbMigrationState]
        total_bytes: int
        total_documents: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bytes_copied: int, 
                collections: Optional[Dict[str, MongoDbCollectionProgress]] = ..., 
                documents_copied: int, 
                elapsed_time: str, 
                errors: Dict[str, MongoDbError], 
                events_pending: int, 
                events_replayed: int, 
                last_event_time: Optional[datetime] = ..., 
                last_replay_time: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                state: Union[str, MongoDbMigrationState], 
                total_bytes: int, 
                total_documents: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbDatabaseSettings(Model):
        collections: dict[str, MongoDbCollectionSettings]
        target_r_us: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                collections: Dict[str, MongoDbCollectionSettings], 
                target_r_us: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbError(Model):
        code: str
        count: int
        message: str
        type: Union[str, MongoDbErrorType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                count: Optional[int] = ..., 
                message: Optional[str] = ..., 
                type: Optional[Union[str, MongoDbErrorType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbErrorType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        VALIDATION_ERROR = "ValidationError"
        WARNING = "Warning"


    class azure.mgmt.datamigration.models.MongoDbFinishCommand(CommandProperties):
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        input: MongoDbFinishCommandInput
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                input: Optional[MongoDbFinishCommandInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbFinishCommandInput(MongoDbCommandInput):
        immediate: bool
        object_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                immediate: bool, 
                object_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbMigrationProgress(MongoDbProgress):
        bytes_copied: int
        databases: dict[str, MongoDbDatabaseProgress]
        documents_copied: int
        elapsed_time: str
        errors: dict[str, MongoDbError]
        events_pending: int
        events_replayed: int
        last_event_time: datetime
        last_replay_time: datetime
        name: str
        qualified_name: str
        result_type: Union[str, MongoDbProgressResultType]
        state: Union[str, MongoDbMigrationState]
        total_bytes: int
        total_documents: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bytes_copied: int, 
                databases: Optional[Dict[str, MongoDbDatabaseProgress]] = ..., 
                documents_copied: int, 
                elapsed_time: str, 
                errors: Dict[str, MongoDbError], 
                events_pending: int, 
                events_replayed: int, 
                last_event_time: Optional[datetime] = ..., 
                last_replay_time: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                state: Union[str, MongoDbMigrationState], 
                total_bytes: int, 
                total_documents: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbMigrationSettings(Model):
        boost_r_us: int
        databases: dict[str, MongoDbDatabaseSettings]
        replication: Union[str, MongoDbReplication]
        source: MongoDbConnectionInfo
        target: MongoDbConnectionInfo
        throttling: MongoDbThrottlingSettings

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                boost_r_us: Optional[int] = ..., 
                databases: Dict[str, MongoDbDatabaseSettings], 
                replication: Optional[Union[str, MongoDbReplication]] = ..., 
                source: MongoDbConnectionInfo, 
                target: MongoDbConnectionInfo, 
                throttling: Optional[MongoDbThrottlingSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETE = "Complete"
        COPYING = "Copying"
        FAILED = "Failed"
        FINALIZING = "Finalizing"
        INITIALIZING = "Initializing"
        INITIAL_REPLAY = "InitialReplay"
        NOT_STARTED = "NotStarted"
        REPLAYING = "Replaying"
        RESTARTING = "Restarting"
        VALIDATING_INPUT = "ValidatingInput"


    class azure.mgmt.datamigration.models.MongoDbObjectInfo(Model):
        average_document_size: int
        data_size: int
        document_count: int
        name: str
        qualified_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                average_document_size: int, 
                data_size: int, 
                document_count: int, 
                name: str, 
                qualified_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbProgress(Model):
        bytes_copied: int
        documents_copied: int
        elapsed_time: str
        errors: dict[str, MongoDbError]
        events_pending: int
        events_replayed: int
        last_event_time: datetime
        last_replay_time: datetime
        name: str
        qualified_name: str
        result_type: Union[str, MongoDbProgressResultType]
        state: Union[str, MongoDbMigrationState]
        total_bytes: int
        total_documents: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                bytes_copied: int, 
                documents_copied: int, 
                elapsed_time: str, 
                errors: Dict[str, MongoDbError], 
                events_pending: int, 
                events_replayed: int, 
                last_event_time: Optional[datetime] = ..., 
                last_replay_time: Optional[datetime] = ..., 
                name: Optional[str] = ..., 
                qualified_name: Optional[str] = ..., 
                state: Union[str, MongoDbMigrationState], 
                total_bytes: int, 
                total_documents: int, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbProgressResultType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTION = "Collection"
        DATABASE = "Database"
        MIGRATION = "Migration"


    class azure.mgmt.datamigration.models.MongoDbReplication(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONTINUOUS = "Continuous"
        DISABLED = "Disabled"
        ONE_TIME = "OneTime"


    class azure.mgmt.datamigration.models.MongoDbRestartCommand(CommandProperties):
        command_type: Union[str, CommandType]
        errors: list[ODataError]
        input: MongoDbCommandInput
        state: Union[str, CommandState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                input: Optional[MongoDbCommandInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbShardKeyField(Model):
        name: str
        order: Union[str, MongoDbShardKeyOrder]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: str, 
                order: Union[str, MongoDbShardKeyOrder], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbShardKeyInfo(Model):
        fields: list[MongoDbShardKeyField]
        is_unique: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fields: List[MongoDbShardKeyField], 
                is_unique: bool, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbShardKeyOrder(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FORWARD = "Forward"
        HASHED = "Hashed"
        REVERSE = "Reverse"


    class azure.mgmt.datamigration.models.MongoDbShardKeySetting(Model):
        fields: list[MongoDbShardKeyField]
        is_unique: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                fields: List[MongoDbShardKeyField], 
                is_unique: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoDbThrottlingSettings(Model):
        max_parallelism: int
        min_free_cpu: int
        min_free_memory_mb: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                max_parallelism: Optional[int] = ..., 
                min_free_cpu: Optional[int] = ..., 
                min_free_memory_mb: Optional[int] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoMigrationCollection(Model):
        migration_progress_details: MongoMigrationProgressDetails
        source_collection: str
        source_database: str
        target_collection: str
        target_database: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_collection: Optional[str] = ..., 
                source_database: Optional[str] = ..., 
                target_collection: Optional[str] = ..., 
                target_database: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoMigrationProgressDetails(Model):
        duration_in_seconds: int
        migration_error: str
        migration_status: Union[str, MongoMigrationStatus]
        processed_document_count: int
        source_document_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MongoMigrationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        COMPLETED = "Completed"
        FAILED = "Failed"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"


    class azure.mgmt.datamigration.models.MySqlConnectionInfo(ConnectionInfo):
        additional_settings: str
        authentication: Union[str, AuthenticationType]
        data_source: str
        encrypt_connection: bool
        password: str
        port: int
        server_name: str
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_settings: Optional[str] = ..., 
                authentication: Optional[Union[str, AuthenticationType]] = ..., 
                data_source: Optional[str] = ..., 
                encrypt_connection: bool = True, 
                password: Optional[str] = ..., 
                port: int, 
                server_name: str, 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.MySqlTargetPlatformType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DB_FOR_MY_SQL = "AzureDbForMySQL"
        SQL_SERVER = "SqlServer"


    class azure.mgmt.datamigration.models.NameAvailabilityRequest(Model):
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                name: Optional[str] = ..., 
                type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NameAvailabilityResponse(Model):
        message: str
        name_available: bool
        reason: Union[str, NameCheckFailureReason]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                message: Optional[str] = ..., 
                name_available: Optional[bool] = ..., 
                reason: Optional[Union[str, NameCheckFailureReason]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NameCheckFailureReason(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ALREADY_EXISTS = "AlreadyExists"
        INVALID = "Invalid"


    class azure.mgmt.datamigration.models.NodeMonitoringData(Model):
        additional_properties: dict[str, JSON]
        available_memory_in_mb: int
        concurrent_jobs_limit: int
        concurrent_jobs_running: int
        cpu_utilization: int
        max_concurrent_jobs: int
        node_name: str
        received_bytes: float
        sent_bytes: float

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NonSqlDataMigrationTable(Model):
        source_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NonSqlDataMigrationTableResult(Model):
        elapsed_time_in_miliseconds: float
        errors: list[DataMigrationError]
        result_code: Union[str, DataMigrationResultCode]
        source_name: str
        source_row_count: int
        target_name: str
        target_row_count: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NonSqlMigrationTaskInput(Model):
        project_location: str
        project_name: str
        selected_tables: list[NonSqlDataMigrationTable]
        target_connection_info: SqlConnectionInfo
        target_database_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                project_location: str, 
                project_name: str, 
                selected_tables: List[NonSqlDataMigrationTable], 
                target_connection_info: SqlConnectionInfo, 
                target_database_name: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.NonSqlMigrationTaskOutput(Model):
        data_migration_table_results: str
        ended_on: datetime
        id: str
        progress_message: str
        source_server_name: str
        started_on: datetime
        status: Union[str, MigrationStatus]
        target_server_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ODataError(Model):
        code: str
        details: list[ODataError]
        message: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                code: Optional[str] = ..., 
                details: Optional[List[ODataError]] = ..., 
                message: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ObjectType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        FUNCTION = "Function"
        STORED_PROCEDURES = "StoredProcedures"
        TABLE = "Table"
        USER = "User"
        VIEW = "View"


    class azure.mgmt.datamigration.models.OfflineConfiguration(Model):
        last_backup_name: str
        offline: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                last_backup_name: Optional[str] = ..., 
                offline: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OperationListResult(Model):
        next_link: str
        value: list[OperationsDefinition]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OperationOrigin(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SYSTEM = "system"
        USER = "user"


    class azure.mgmt.datamigration.models.OperationsDefinition(Model):
        display: OperationsDisplayDefinition
        is_data_action: bool
        name: str
        origin: Union[str, OperationOrigin]
        properties: dict[str, JSON]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                is_data_action: Optional[bool] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OperationsDisplayDefinition(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OracleConnectionInfo(ConnectionInfo):
        authentication: Union[str, AuthenticationType]
        data_source: str
        password: str
        port: int
        server_name: str
        server_version: str
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication: Optional[Union[str, AuthenticationType]] = ..., 
                data_source: str, 
                password: Optional[str] = ..., 
                port: Optional[int] = ..., 
                server_name: Optional[str] = ..., 
                server_version: Optional[str] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OracleOCIDriverInfo(Model):
        archive_checksum: str
        assembly_version: str
        driver_name: str
        driver_size: str
        oracle_checksum: str
        supported_oracle_versions: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.OrphanedUserInfo(Model):
        database_name: str
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_name: Optional[str] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.PostgreSqlConnectionInfo(ConnectionInfo):
        additional_settings: str
        authentication: Union[str, AuthenticationType]
        data_source: str
        database_name: str
        encrypt_connection: bool
        password: str
        port: int
        server_brand_version: str
        server_name: str
        server_version: str
        trust_server_certificate: bool
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_settings: Optional[str] = ..., 
                authentication: Optional[Union[str, AuthenticationType]] = ..., 
                data_source: Optional[str] = ..., 
                database_name: Optional[str] = ..., 
                encrypt_connection: bool = True, 
                password: Optional[str] = ..., 
                port: int, 
                server_brand_version: Optional[str] = ..., 
                server_name: str, 
                server_version: Optional[str] = ..., 
                trust_server_certificate: bool = False, 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.Project(TrackedResourceAutoGenerated):
        azure_authentication_info: AzureActiveDirectoryApp
        creation_time: datetime
        databases_info: list[DatabaseInfo]
        etag: str
        id: str
        location: str
        name: str
        provisioning_state: Union[str, ProjectProvisioningState]
        source_connection_info: ConnectionInfo
        source_platform: Union[str, ProjectSourcePlatform]
        system_data: SystemDataAutoGenerated
        tags: dict[str, str]
        target_connection_info: ConnectionInfo
        target_platform: Union[str, ProjectTargetPlatform]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_authentication_info: Optional[AzureActiveDirectoryApp] = ..., 
                databases_info: Optional[List[DatabaseInfo]] = ..., 
                etag: Optional[str] = ..., 
                location: Optional[str] = ..., 
                source_connection_info: Optional[ConnectionInfo] = ..., 
                source_platform: Optional[Union[str, ProjectSourcePlatform]] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                target_connection_info: Optional[ConnectionInfo] = ..., 
                target_platform: Optional[Union[str, ProjectTargetPlatform]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProjectFile(ResourceAutoGenerated):
        etag: str
        id: str
        name: str
        properties: ProjectFileProperties
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ProjectFileProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProjectFileProperties(Model):
        extension: str
        file_path: str
        last_modified: datetime
        media_type: str
        size: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                extension: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                media_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProjectList(Model):
        next_link: str
        value: list[Project]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Project]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProjectProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DELETING = "Deleting"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datamigration.models.ProjectSourcePlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONGO_DB = "MongoDb"
        MY_SQL = "MySQL"
        POSTGRE_SQL = "PostgreSql"
        SQL = "SQL"
        UNKNOWN = "Unknown"


    class azure.mgmt.datamigration.models.ProjectTargetPlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DB_FOR_MY_SQL = "AzureDbForMySql"
        AZURE_DB_FOR_POSTGRE_SQL = "AzureDbForPostgreSql"
        MONGO_DB = "MongoDb"
        SQLDB = "SQLDB"
        SQLMI = "SQLMI"
        UNKNOWN = "Unknown"


    class azure.mgmt.datamigration.models.ProjectTask(ResourceAutoGenerated):
        etag: str
        id: str
        name: str
        properties: ProjectTaskProperties
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                etag: Optional[str] = ..., 
                properties: Optional[ProjectTaskProperties] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProjectTaskProperties(Model):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        PROVISIONING = "Provisioning"
        SUCCEEDED = "Succeeded"
        UPDATING = "Updating"


    class azure.mgmt.datamigration.models.ProxyResource(Resource):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ProxyResourceAutoGenerated(Model):
        id: str
        name: str
        system_data: SystemDataAutoGenerated
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.QueryAnalysisValidationResult(Model):
        query_results: QueryExecutionResult
        validation_errors: ValidationError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query_results: Optional[QueryExecutionResult] = ..., 
                validation_errors: Optional[ValidationError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.QueryExecutionResult(Model):
        query_text: str
        source_result: ExecutionStatistics
        statements_in_batch: int
        target_result: ExecutionStatistics

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                query_text: Optional[str] = ..., 
                source_result: Optional[ExecutionStatistics] = ..., 
                statements_in_batch: Optional[int] = ..., 
                target_result: Optional[ExecutionStatistics] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.Quota(Model):
        current_value: float
        id: str
        limit: float
        name: QuotaName
        unit: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                current_value: Optional[float] = ..., 
                id: Optional[str] = ..., 
                limit: Optional[float] = ..., 
                name: Optional[QuotaName] = ..., 
                unit: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.QuotaList(Model):
        next_link: str
        value: list[Quota]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[Quota]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.QuotaName(Model):
        localized_value: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                localized_value: Optional[str] = ..., 
                value: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.RegenAuthKeys(Model):
        auth_key1: str
        auth_key2: str
        key_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                auth_key1: Optional[str] = ..., 
                auth_key2: Optional[str] = ..., 
                key_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ReplicateMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACTION_REQUIRED = "ACTION_REQUIRED"
        COMPLETE = "COMPLETE"
        FAILED = "FAILED"
        PENDING = "PENDING"
        UNDEFINED = "UNDEFINED"
        VALIDATING = "VALIDATING"


    class azure.mgmt.datamigration.models.ReportableException(Model):
        actionable_message: str
        file_path: str
        h_result: int
        line_number: str
        message: str
        stack_trace: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                actionable_message: Optional[str] = ..., 
                file_path: Optional[str] = ..., 
                h_result: Optional[int] = ..., 
                line_number: Optional[str] = ..., 
                message: Optional[str] = ..., 
                stack_trace: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.Resource(Model):
        id: str
        name: str
        system_data: SystemData
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceAutoGenerated(Model):
        id: str
        name: str
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSku(Model):
        api_versions: list[str]
        capabilities: list[ResourceSkuCapabilities]
        capacity: ResourceSkuCapacity
        costs: list[ResourceSkuCosts]
        family: str
        kind: str
        locations: list[str]
        name: str
        resource_type: str
        restrictions: list[ResourceSkuRestrictions]
        size: str
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSkuCapabilities(Model):
        name: str
        value: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSkuCapacity(Model):
        default: int
        maximum: int
        minimum: int
        scale_type: Union[str, ResourceSkuCapacityScaleType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSkuCapacityScaleType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "Automatic"
        MANUAL = "Manual"
        NONE = "None"


    class azure.mgmt.datamigration.models.ResourceSkuCosts(Model):
        extended_unit: str
        meter_id: str
        quantity: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSkuRestrictions(Model):
        reason_code: Union[str, ResourceSkuRestrictionsReasonCode]
        type: Union[str, ResourceSkuRestrictionsType]
        values: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceSkuRestrictionsReasonCode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        NOT_AVAILABLE_FOR_SUBSCRIPTION = "NotAvailableForSubscription"
        QUOTA_ID = "QuotaId"


    class azure.mgmt.datamigration.models.ResourceSkuRestrictionsType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        LOCATION = "location"


    class azure.mgmt.datamigration.models.ResourceSkusResult(Model):
        next_link: str
        value: list[ResourceSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: List[ResourceSku], 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ResourceType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        MONGO_TO_COSMOS_DB_MONGO = "MongoToCosmosDbMongo"
        SQL_DB = "SqlDb"
        SQL_MI = "SqlMi"
        SQL_VM = "SqlVm"


    class azure.mgmt.datamigration.models.ScenarioSource(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCESS = "Access"
        DB2 = "DB2"
        MONGO_DB = "MongoDB"
        MY_SQL = "MySQL"
        MY_SQLRDS = "MySQLRDS"
        ORACLE = "Oracle"
        POSTGRE_SQL = "PostgreSQL"
        POSTGRE_SQLRDS = "PostgreSQLRDS"
        SQL = "SQL"
        SQLRDS = "SQLRDS"
        SYBASE = "Sybase"


    class azure.mgmt.datamigration.models.ScenarioTarget(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AZURE_DB_FOR_MY_SQL = "AzureDBForMySql"
        AZURE_DB_FOR_POSTGRES_SQL = "AzureDBForPostgresSQL"
        MONGO_DB = "MongoDB"
        SQLDB = "SQLDB"
        SQLDW = "SQLDW"
        SQLMI = "SQLMI"
        SQL_SERVER = "SQLServer"


    class azure.mgmt.datamigration.models.SchemaComparisonValidationResult(Model):
        schema_differences: SchemaComparisonValidationResultType
        source_database_object_count: dict[str, int]
        target_database_object_count: dict[str, int]
        validation_errors: ValidationError

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                schema_differences: Optional[SchemaComparisonValidationResultType] = ..., 
                source_database_object_count: Optional[Dict[str, int]] = ..., 
                target_database_object_count: Optional[Dict[str, int]] = ..., 
                validation_errors: Optional[ValidationError] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SchemaComparisonValidationResultType(Model):
        object_name: str
        object_type: Union[str, ObjectType]
        update_action: Union[str, UpdateActionType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                object_name: Optional[str] = ..., 
                object_type: Optional[Union[str, ObjectType]] = ..., 
                update_action: Optional[Union[str, UpdateActionType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SchemaMigrationOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        EXTRACT_FROM_SOURCE = "ExtractFromSource"
        NONE = "None"
        USE_STORAGE_FILE = "UseStorageFile"


    class azure.mgmt.datamigration.models.SchemaMigrationSetting(Model):
        file_id: str
        file_name: str
        schema_option: Union[str, SchemaMigrationOption]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                file_id: Optional[str] = ..., 
                file_name: Optional[str] = ..., 
                schema_option: Optional[Union[str, SchemaMigrationOption]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SchemaMigrationStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COLLECTING_OBJECTS = "CollectingObjects"
        COMPLETED = "Completed"
        COMPLETED_WITH_WARNINGS = "CompletedWithWarnings"
        DEPLOYING_SCHEMA = "DeployingSchema"
        DOWNLOADING_SCRIPT = "DownloadingScript"
        FAILED = "Failed"
        GENERATING_SCRIPT = "GeneratingScript"
        NOT_STARTED = "NotStarted"
        UPLOADING_SCRIPT = "UploadingScript"
        VALIDATING_INPUTS = "ValidatingInputs"


    class azure.mgmt.datamigration.models.SelectedCertificateInput(Model):
        certificate_name: str
        password: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                certificate_name: str, 
                password: str, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServerLevelPermissionsGroup(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        DEFAULT = "Default"
        MIGRATION_FROM_MY_SQL_TO_AZURE_DB_FOR_MY_SQL = "MigrationFromMySQLToAzureDBForMySQL"
        MIGRATION_FROM_SQL_SERVER_TO_AZURE_DB = "MigrationFromSqlServerToAzureDB"
        MIGRATION_FROM_SQL_SERVER_TO_AZURE_MI = "MigrationFromSqlServerToAzureMI"
        MIGRATION_FROM_SQL_SERVER_TO_AZURE_VM = "MigrationFromSqlServerToAzureVM"


    class azure.mgmt.datamigration.models.ServerProperties(Model):
        server_database_count: int
        server_edition: str
        server_name: str
        server_operating_system_version: str
        server_platform: str
        server_version: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServiceOperation(Model):
        display: ServiceOperationDisplay
        name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                display: Optional[ServiceOperationDisplay] = ..., 
                name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServiceOperationDisplay(Model):
        description: str
        operation: str
        provider: str
        resource: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                description: Optional[str] = ..., 
                operation: Optional[str] = ..., 
                provider: Optional[str] = ..., 
                resource: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServiceOperationList(Model):
        next_link: str
        value: list[ServiceOperation]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ServiceOperation]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServiceProvisioningState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ACCEPTED = "Accepted"
        DELETING = "Deleting"
        DEPLOYING = "Deploying"
        FAILED = "Failed"
        FAILED_TO_START = "FailedToStart"
        FAILED_TO_STOP = "FailedToStop"
        STARTING = "Starting"
        STOPPED = "Stopped"
        STOPPING = "Stopping"
        SUCCEEDED = "Succeeded"


    class azure.mgmt.datamigration.models.ServiceScalability(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        AUTOMATIC = "automatic"
        MANUAL = "manual"
        NONE = "none"


    class azure.mgmt.datamigration.models.ServiceSku(Model):
        capacity: int
        family: str
        name: str
        size: str
        tier: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                capacity: Optional[int] = ..., 
                family: Optional[str] = ..., 
                name: Optional[str] = ..., 
                size: Optional[str] = ..., 
                tier: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ServiceSkuList(Model):
        next_link: str
        value: list[AvailableServiceSku]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[AvailableServiceSku]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.Severity(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ERROR = "Error"
        MESSAGE = "Message"
        WARNING = "Warning"


    class azure.mgmt.datamigration.models.SourceLocation(Model):
        azure_blob: AzureBlob
        file_share: SqlFileShare
        file_storage_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_blob: Optional[AzureBlob] = ..., 
                file_share: Optional[SqlFileShare] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlBackupFileInfo(Model):
        copy_duration: int
        copy_throughput: float
        data_read: int
        data_written: int
        family_sequence_number: int
        file_name: str
        status: str
        total_size: int

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlBackupSetInfo(Model):
        backup_finish_date: datetime
        backup_set_id: str
        backup_start_date: datetime
        backup_type: str
        family_count: int
        first_lsn: str
        has_backup_checksums: bool
        ignore_reasons: list[str]
        is_backup_restored: bool
        last_lsn: str
        list_of_backup_files: list[SqlBackupFileInfo]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlConnectionInfo(ConnectionInfo):
        additional_settings: str
        authentication: Union[str, AuthenticationType]
        data_source: str
        encrypt_connection: bool
        password: str
        platform: Union[str, SqlSourcePlatform]
        port: int
        resource_id: str
        server_brand_version: str
        server_name: str
        server_version: str
        trust_server_certificate: bool
        type: str
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                additional_settings: Optional[str] = ..., 
                authentication: Optional[Union[str, AuthenticationType]] = ..., 
                data_source: str, 
                encrypt_connection: bool = True, 
                password: Optional[str] = ..., 
                platform: Optional[Union[str, SqlSourcePlatform]] = ..., 
                port: Optional[int] = ..., 
                resource_id: Optional[str] = ..., 
                server_brand_version: Optional[str] = ..., 
                server_name: Optional[str] = ..., 
                server_version: Optional[str] = ..., 
                trust_server_certificate: bool = False, 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlConnectionInformation(Model):
        authentication: str
        data_source: str
        encrypt_connection: bool
        password: str
        trust_server_certificate: bool
        user_name: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                authentication: Optional[str] = ..., 
                data_source: Optional[str] = ..., 
                encrypt_connection: Optional[bool] = ..., 
                password: Optional[str] = ..., 
                trust_server_certificate: Optional[bool] = ..., 
                user_name: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlDbMigrationStatusDetails(Model):
        list_of_copy_progress_details: list[CopyProgressDetails]
        migration_state: str
        sql_data_copy_errors: list[str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlDbOfflineConfiguration(Model):
        offline: bool

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlFileShare(Model):
        password: str
        path: str
        username: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                password: Optional[str] = ..., 
                path: Optional[str] = ..., 
                username: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlMigrationListResult(Model):
        next_link: str
        value: list[SqlMigrationService]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlMigrationService(TrackedResourceAutoGenerated):
        id: str
        integration_runtime_state: str
        location: str
        name: str
        provisioning_state: str
        system_data: SystemDataAutoGenerated
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlMigrationServiceUpdate(Model):
        tags: dict[str, str]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlMigrationTaskInput(Model):
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlServerSqlMISyncTaskInput(Model):
        azure_app: AzureActiveDirectoryApp
        backup_file_share: FileShare
        selected_databases: list[MigrateSqlServerSqlMIDatabaseInput]
        source_connection_info: SqlConnectionInfo
        storage_resource_id: str
        target_connection_info: MiSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_app: AzureActiveDirectoryApp, 
                backup_file_share: Optional[FileShare] = ..., 
                selected_databases: List[MigrateSqlServerSqlMIDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                storage_resource_id: str, 
                target_connection_info: MiSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SqlSourcePlatform(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SQL_ON_PREM = "SqlOnPrem"


    class azure.mgmt.datamigration.models.SsisMigrationInfo(Model):
        environment_overwrite_option: Union[str, SsisMigrationOverwriteOption]
        project_overwrite_option: Union[str, SsisMigrationOverwriteOption]
        ssis_store_type: Union[str, SsisStoreType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                environment_overwrite_option: Optional[Union[str, SsisMigrationOverwriteOption]] = ..., 
                project_overwrite_option: Optional[Union[str, SsisMigrationOverwriteOption]] = ..., 
                ssis_store_type: Optional[Union[str, SsisStoreType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SsisMigrationOverwriteOption(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        IGNORE = "Ignore"
        OVERWRITE = "Overwrite"


    class azure.mgmt.datamigration.models.SsisMigrationStage(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        INITIALIZE = "Initialize"
        IN_PROGRESS = "InProgress"
        NONE = "None"


    class azure.mgmt.datamigration.models.SsisStoreType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        SSIS_CATALOG = "SsisCatalog"


    class azure.mgmt.datamigration.models.StartMigrationScenarioServerRoleResult(Model):
        exceptions_and_warnings: list[ReportableException]
        name: str
        state: Union[str, MigrationState]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SyncDatabaseMigrationReportingState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BACKUP_COMPLETED = "BACKUP_COMPLETED"
        BACKUP_IN_PROGRESS = "BACKUP_IN_PROGRESS"
        CANCELLED = "CANCELLED"
        CANCELLING = "CANCELLING"
        COMPLETE = "COMPLETE"
        COMPLETING = "COMPLETING"
        CONFIGURING = "CONFIGURING"
        FAILED = "FAILED"
        INITIALIAZING = "INITIALIAZING"
        READY_TO_COMPLETE = "READY_TO_COMPLETE"
        RESTORE_COMPLETED = "RESTORE_COMPLETED"
        RESTORE_IN_PROGRESS = "RESTORE_IN_PROGRESS"
        RUNNING = "RUNNING"
        STARTING = "STARTING"
        UNDEFINED = "UNDEFINED"
        VALIDATING = "VALIDATING"
        VALIDATION_COMPLETE = "VALIDATION_COMPLETE"
        VALIDATION_FAILED = "VALIDATION_FAILED"


    class azure.mgmt.datamigration.models.SyncMigrationDatabaseErrorEvent(Model):
        event_text: str
        event_type_string: str
        timestamp_string: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SyncTableMigrationState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        BEFORE_LOAD = "BEFORE_LOAD"
        CANCELED = "CANCELED"
        COMPLETED = "COMPLETED"
        ERROR = "ERROR"
        FAILED = "FAILED"
        FULL_LOAD = "FULL_LOAD"


    class azure.mgmt.datamigration.models.SystemData(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.SystemDataAutoGenerated(Model):
        created_at: datetime
        created_by: str
        created_by_type: Union[str, CreatedByType]
        last_modified_at: datetime
        last_modified_by: str
        last_modified_by_type: Union[str, CreatedByType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                created_at: Optional[datetime] = ..., 
                created_by: Optional[str] = ..., 
                created_by_type: Optional[Union[str, CreatedByType]] = ..., 
                last_modified_at: Optional[datetime] = ..., 
                last_modified_by: Optional[str] = ..., 
                last_modified_by_type: Optional[Union[str, CreatedByType]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.TargetLocation(Model):
        account_key: str
        storage_account_resource_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                account_key: Optional[str] = ..., 
                storage_account_resource_id: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.TaskList(Model):
        next_link: str
        value: list[ProjectTask]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                next_link: Optional[str] = ..., 
                value: Optional[List[ProjectTask]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.TaskState(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CANCELED = "Canceled"
        FAILED = "Failed"
        FAILED_INPUT_VALIDATION = "FailedInputValidation"
        FAULTED = "Faulted"
        QUEUED = "Queued"
        RUNNING = "Running"
        SUCCEEDED = "Succeeded"
        UNKNOWN = "Unknown"


    class azure.mgmt.datamigration.models.TaskType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        CONNECT_MONGO_DB = "Connect.MongoDb"
        CONNECT_TO_SOURCE_MY_SQL = "ConnectToSource.MySql"
        CONNECT_TO_SOURCE_ORACLE_SYNC = "ConnectToSource.Oracle.Sync"
        CONNECT_TO_SOURCE_POSTGRE_SQL_SYNC = "ConnectToSource.PostgreSql.Sync"
        CONNECT_TO_SOURCE_SQL_SERVER = "ConnectToSource.SqlServer"
        CONNECT_TO_SOURCE_SQL_SERVER_SYNC = "ConnectToSource.SqlServer.Sync"
        CONNECT_TO_TARGET_AZURE_DB_FOR_MY_SQL = "ConnectToTarget.AzureDbForMySql"
        CONNECT_TO_TARGET_AZURE_DB_FOR_POSTGRE_SQL_SYNC = "ConnectToTarget.AzureDbForPostgreSql.Sync"
        CONNECT_TO_TARGET_AZURE_SQL_DB_MI = "ConnectToTarget.AzureSqlDbMI"
        CONNECT_TO_TARGET_AZURE_SQL_DB_MI_SYNC_LRS = "ConnectToTarget.AzureSqlDbMI.Sync.LRS"
        CONNECT_TO_TARGET_ORACLE_AZURE_DB_FOR_POSTGRE_SQL_SYNC = "ConnectToTarget.Oracle.AzureDbForPostgreSql.Sync"
        CONNECT_TO_TARGET_SQL_DB = "ConnectToTarget.SqlDb"
        CONNECT_TO_TARGET_SQL_DB_SYNC = "ConnectToTarget.SqlDb.Sync"
        GET_TDE_CERTIFICATES_SQL = "GetTDECertificates.Sql"
        GET_USER_TABLES_AZURE_SQL_DB_SYNC = "GetUserTables.AzureSqlDb.Sync"
        GET_USER_TABLES_MY_SQL = "GetUserTablesMySql"
        GET_USER_TABLES_ORACLE = "GetUserTablesOracle"
        GET_USER_TABLES_POSTGRE_SQL = "GetUserTablesPostgreSql"
        GET_USER_TABLES_SQL = "GetUserTables.Sql"
        MIGRATE_MONGO_DB = "Migrate.MongoDb"
        MIGRATE_MY_SQL_AZURE_DB_FOR_MY_SQL = "Migrate.MySql.AzureDbForMySql"
        MIGRATE_MY_SQL_AZURE_DB_FOR_MY_SQL_SYNC = "Migrate.MySql.AzureDbForMySql.Sync"
        MIGRATE_ORACLE_AZURE_DB_FOR_POSTGRE_SQL_SYNC = "Migrate.Oracle.AzureDbForPostgreSql.Sync"
        MIGRATE_POSTGRE_SQL_AZURE_DB_FOR_POSTGRE_SQL_SYNC_V2 = "Migrate.PostgreSql.AzureDbForPostgreSql.SyncV2"
        MIGRATE_SCHEMA_SQL_SERVER_SQL_DB = "MigrateSchemaSqlServerSqlDb"
        MIGRATE_SQL_SERVER_AZURE_SQL_DB_MI = "Migrate.SqlServer.AzureSqlDbMI"
        MIGRATE_SQL_SERVER_AZURE_SQL_DB_MI_SYNC_LRS = "Migrate.SqlServer.AzureSqlDbMI.Sync.LRS"
        MIGRATE_SQL_SERVER_AZURE_SQL_DB_SYNC = "Migrate.SqlServer.AzureSqlDb.Sync"
        MIGRATE_SQL_SERVER_SQL_DB = "Migrate.SqlServer.SqlDb"
        MIGRATE_SSIS = "Migrate.Ssis"
        SERVICE_CHECK_OCI = "Service.Check.OCI"
        SERVICE_INSTALL_OCI = "Service.Install.OCI"
        SERVICE_UPLOAD_OCI = "Service.Upload.OCI"
        VALIDATE_MIGRATION_INPUT_SQL_SERVER_AZURE_SQL_DB_MI = "ValidateMigrationInput.SqlServer.AzureSqlDbMI"
        VALIDATE_MIGRATION_INPUT_SQL_SERVER_AZURE_SQL_DB_MI_SYNC_LRS = "ValidateMigrationInput.SqlServer.AzureSqlDbMI.Sync.LRS"
        VALIDATE_MIGRATION_INPUT_SQL_SERVER_SQL_DB_SYNC = "ValidateMigrationInput.SqlServer.SqlDb.Sync"
        VALIDATE_MONGO_DB = "Validate.MongoDb"
        VALIDATE_ORACLE_AZURE_DB_POSTGRE_SQL_SYNC = "Validate.Oracle.AzureDbPostgreSql.Sync"


    class azure.mgmt.datamigration.models.TrackedResource(Resource):
        id: str
        location: str
        name: str
        system_data: SystemData
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: str, 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.TrackedResourceAutoGenerated(Model):
        id: str
        location: str
        name: str
        system_data: SystemDataAutoGenerated
        tags: dict[str, str]
        type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                location: Optional[str] = ..., 
                tags: Optional[Dict[str, str]] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.UpdateActionType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        ADDED_ON_TARGET = "AddedOnTarget"
        CHANGED_ON_TARGET = "ChangedOnTarget"
        DELETED_ON_TARGET = "DeletedOnTarget"


    class azure.mgmt.datamigration.models.UploadOCIDriverTaskInput(Model):
        driver_share: FileShare

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                driver_share: Optional[FileShare] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.UploadOCIDriverTaskOutput(Model):
        driver_package_name: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.UploadOCIDriverTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: UploadOCIDriverTaskInput
        output: list[UploadOCIDriverTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[UploadOCIDriverTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.UserAssignedIdentity(Model):
        client_id: str
        principal_id: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlDbSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ValidateSyncMigrationInputSqlServerTaskInput
        output: list[ValidateSyncMigrationInputSqlServerTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ValidateSyncMigrationInputSqlServerTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMISyncTaskInput(SqlServerSqlMISyncTaskInput):
        azure_app: AzureActiveDirectoryApp
        backup_file_share: FileShare
        selected_databases: list[MigrateSqlServerSqlMIDatabaseInput]
        source_connection_info: SqlConnectionInfo
        storage_resource_id: str
        target_connection_info: MiSqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                azure_app: AzureActiveDirectoryApp, 
                backup_file_share: Optional[FileShare] = ..., 
                selected_databases: List[MigrateSqlServerSqlMIDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                storage_resource_id: str, 
                target_connection_info: MiSqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMISyncTaskOutput(Model):
        id: str
        name: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMISyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ValidateMigrationInputSqlServerSqlMISyncTaskInput
        output: list[ValidateMigrationInputSqlServerSqlMISyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ValidateMigrationInputSqlServerSqlMISyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMITaskInput(Model):
        backup_blob_share: BlobShare
        backup_file_share: FileShare
        backup_mode: Union[str, BackupMode]
        selected_databases: list[MigrateSqlServerSqlMIDatabaseInput]
        selected_logins: list[str]
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                backup_blob_share: BlobShare, 
                backup_file_share: Optional[FileShare] = ..., 
                backup_mode: Optional[Union[str, BackupMode]] = ..., 
                selected_databases: List[MigrateSqlServerSqlMIDatabaseInput], 
                selected_logins: Optional[List[str]] = ..., 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMITaskOutput(Model):
        backup_folder_errors: list[ReportableException]
        backup_share_credentials_errors: list[ReportableException]
        backup_storage_account_errors: list[ReportableException]
        database_backup_info: DatabaseBackupInfo
        existing_backup_errors: list[ReportableException]
        id: str
        name: str
        restore_database_name_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                database_backup_info: Optional[DatabaseBackupInfo] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMigrationInputSqlServerSqlMITaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: ValidateMigrationInputSqlServerSqlMITaskInput
        output: list[ValidateMigrationInputSqlServerSqlMITaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[ValidateMigrationInputSqlServerSqlMITaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateMongoDbTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MongoDbMigrationSettings
        output: list[MongoDbMigrationProgress]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MongoDbMigrationSettings] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateOracleAzureDbForPostgreSqlSyncTaskProperties(ProjectTaskProperties):
        client_data: dict[str, str]
        commands: list[CommandProperties]
        errors: list[ODataError]
        input: MigrateOracleAzureDbPostgreSqlSyncTaskInput
        output: list[ValidateOracleAzureDbPostgreSqlSyncTaskOutput]
        state: Union[str, TaskState]
        task_type: Union[str, TaskType]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                client_data: Optional[Dict[str, str]] = ..., 
                input: Optional[MigrateOracleAzureDbPostgreSqlSyncTaskInput] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateOracleAzureDbPostgreSqlSyncTaskOutput(Model):
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateSyncMigrationInputSqlServerTaskInput(Model):
        selected_databases: list[MigrateSqlServerSqlDbSyncDatabaseInput]
        source_connection_info: SqlConnectionInfo
        target_connection_info: SqlConnectionInfo

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                selected_databases: List[MigrateSqlServerSqlDbSyncDatabaseInput], 
                source_connection_info: SqlConnectionInfo, 
                target_connection_info: SqlConnectionInfo, 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidateSyncMigrationInputSqlServerTaskOutput(Model):
        id: str
        name: str
        validation_errors: list[ReportableException]

        def __eq__(self, other: Any) -> bool: ...

        def __init__(self, **kwargs: Any) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidationError(Model):
        severity: Union[str, Severity]
        text: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                severity: Optional[Union[str, Severity]] = ..., 
                text: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


    class azure.mgmt.datamigration.models.ValidationStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
        COMPLETED = "Completed"
        COMPLETED_WITH_ISSUES = "CompletedWithIssues"
        DEFAULT = "Default"
        FAILED = "Failed"
        INITIALIZED = "Initialized"
        IN_PROGRESS = "InProgress"
        NOT_STARTED = "NotStarted"
        STOPPED = "Stopped"


    class azure.mgmt.datamigration.models.WaitStatistics(Model):
        wait_count: int
        wait_time_ms: float
        wait_type: str

        def __eq__(self, other: Any) -> bool: ...

        def __init__(
                self, 
                *, 
                wait_count: Optional[int] = ..., 
                wait_time_ms: float = 0, 
                wait_type: Optional[str] = ..., 
                **kwargs: Any
            ) -> None: ...

        def __ne__(self, other: Any) -> bool: ...

        def __str__(self) -> str: ...

        @classmethod
        def deserialize(
                cls, 
                data: Any, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def enable_additional_properties_sending(cls) -> None: ...

        @classmethod
        def from_dict(
                cls, 
                data: Any, 
                key_extractors: Optional[Callable[[str, Dict[str, Any], Any], Any]] = None, 
                content_type: Optional[str] = None
            ) -> Self: ...

        @classmethod
        def is_xml_model(cls) -> bool: ...

        def as_dict(
                self, 
                keep_readonly: bool = True, 
                key_transformer: Callable[[str, Dict[str, Any], Any], Any] = attribute_transformer, 
                **kwargs: Any
            ) -> JSON: ...

        def serialize(
                self, 
                keep_readonly: bool = False, 
                **kwargs: Any
            ) -> JSON: ...


namespace azure.mgmt.datamigration.operations

    class azure.mgmt.datamigration.operations.DatabaseMigrationsMongoToCosmosDbRUMongoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: DatabaseMigrationCosmosDbMongo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> DatabaseMigrationCosmosDbMongo: ...

        @distributed_trace
        def get_for_scope(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabaseMigrationCosmosDbMongo]: ...


    class azure.mgmt.datamigration.operations.DatabaseMigrationsMongoToCosmosDbvCoreMongoOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: DatabaseMigrationCosmosDbMongo, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @overload
        def begin_create(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationCosmosDbMongo]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                migration_name: str, 
                **kwargs: Any
            ) -> DatabaseMigrationCosmosDbMongo: ...

        @distributed_trace
        def get_for_scope(
                self, 
                resource_group_name: str, 
                target_resource_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabaseMigrationCosmosDbMongo]: ...


    class azure.mgmt.datamigration.operations.DatabaseMigrationsSqlDbOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlDb, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlDb]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlDb]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_retry(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_input: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlDb]: ...

        @overload
        def begin_retry(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_input: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlDb]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_db_instance_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlDb: ...


    class azure.mgmt.datamigration.operations.DatabaseMigrationsSqlMiOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlMi, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlMi]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlMi]: ...

        @overload
        def begin_cutover(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cutover(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlMi]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                managed_instance_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlMi: ...


    class azure.mgmt.datamigration.operations.DatabaseMigrationsSqlVmOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cancel(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: DatabaseMigrationSqlVm, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlVm]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlVm]: ...

        @overload
        def begin_cutover(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: MigrationOperationInput, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_cutover(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                force: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[DatabaseMigrationSqlVm]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_virtual_machine_name: str, 
                target_db_name: str, 
                migration_operation_id: Optional[str] = None, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> DatabaseMigrationSqlVm: ...


    class azure.mgmt.datamigration.operations.FilesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: ProjectFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @distributed_trace
        def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> ProjectFile: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> ItemPaged[ProjectFile]: ...

        @distributed_trace
        def read(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileStorageInfo: ...

        @distributed_trace
        def read_write(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                **kwargs: Any
            ) -> FileStorageInfo: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: ProjectFile, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                file_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectFile: ...


    class azure.mgmt.datamigration.operations.MigrationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: MigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: MigrationServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[MigrationService]: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> MigrationService: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[MigrationService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[MigrationService]: ...

        @distributed_trace
        def list_migrations(
                self, 
                resource_group_name: str, 
                migration_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabaseMigrationBase]: ...


    class azure.mgmt.datamigration.operations.Operations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[OperationsDefinition]: ...


    class azure.mgmt.datamigration.operations.ProjectsOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                **kwargs: Any
            ) -> Project: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[Project]: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: Project, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> Project: ...


    class azure.mgmt.datamigration.operations.ResourceSkusOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list_skus(self, **kwargs: Any) -> ItemPaged[ResourceSku]: ...


    class azure.mgmt.datamigration.operations.ServiceTasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def delete(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                task_type: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ProjectTask]: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...


    class azure.mgmt.datamigration.operations.ServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: DataMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataMigrationService]: ...

        @overload
        def begin_create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataMigrationService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                group_name: str, 
                service_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_start(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @distributed_trace
        def begin_stop(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: DataMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataMigrationService]: ...

        @overload
        def begin_update(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[DataMigrationService]: ...

        @overload
        def check_children_name_availability(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        def check_children_name_availability(
                self, 
                group_name: str, 
                service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: NameAvailabilityRequest, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @overload
        def check_name_availability(
                self, 
                location: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> NameAvailabilityResponse: ...

        @distributed_trace
        def check_status(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> DataMigrationServiceStatusResponse: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> DataMigrationService: ...

        @distributed_trace
        def list(self, **kwargs: Any) -> ItemPaged[DataMigrationService]: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DataMigrationService]: ...

        @distributed_trace
        def list_skus(
                self, 
                group_name: str, 
                service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[AvailableServiceSku]: ...


    class azure.mgmt.datamigration.operations.SqlMigrationServicesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: SqlMigrationService, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlMigrationService]: ...

        @overload
        def begin_create_or_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlMigrationService]: ...

        @distributed_trace
        def begin_delete(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> LROPoller[None]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: SqlMigrationServiceUpdate, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlMigrationService]: ...

        @overload
        def begin_update(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> LROPoller[SqlMigrationService]: ...

        @overload
        def delete_node(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: DeleteNode, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteNode: ...

        @overload
        def delete_node(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> DeleteNode: ...

        @distributed_trace
        def get(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> SqlMigrationService: ...

        @distributed_trace
        def list_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> AuthenticationKeys: ...

        @distributed_trace
        def list_by_resource_group(
                self, 
                resource_group_name: str, 
                **kwargs: Any
            ) -> ItemPaged[SqlMigrationService]: ...

        @distributed_trace
        def list_by_subscription(self, **kwargs: Any) -> ItemPaged[SqlMigrationService]: ...

        @distributed_trace
        def list_migrations(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> ItemPaged[DatabaseMigration]: ...

        @distributed_trace
        def list_monitoring_data(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                **kwargs: Any
            ) -> IntegrationRuntimeMonitoringData: ...

        @overload
        def regenerate_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: RegenAuthKeys, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegenAuthKeys: ...

        @overload
        def regenerate_auth_keys(
                self, 
                resource_group_name: str, 
                sql_migration_service_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> RegenAuthKeys: ...


    class azure.mgmt.datamigration.operations.TasksOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def cancel(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def command(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: CommandProperties, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommandProperties: ...

        @overload
        def command(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> CommandProperties: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def create_or_update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def delete(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                delete_running_tasks: Optional[bool] = None, 
                **kwargs: Any
            ) -> None: ...

        @distributed_trace
        def get(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                expand: Optional[str] = None, 
                **kwargs: Any
            ) -> ProjectTask: ...

        @distributed_trace
        def list(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_type: Optional[str] = None, 
                **kwargs: Any
            ) -> ItemPaged[ProjectTask]: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: ProjectTask, 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...

        @overload
        def update(
                self, 
                group_name: str, 
                service_name: str, 
                project_name: str, 
                task_name: str, 
                parameters: IO[bytes], 
                *, 
                content_type: str = "application/json", 
                **kwargs: Any
            ) -> ProjectTask: ...


    class azure.mgmt.datamigration.operations.UsagesOperations:

        def __init__(
                self, 
                *args, 
                **kwargs
            ) -> None: ...

        @distributed_trace
        def list(
                self, 
                location: str, 
                **kwargs: Any
            ) -> ItemPaged[Quota]: ...


```